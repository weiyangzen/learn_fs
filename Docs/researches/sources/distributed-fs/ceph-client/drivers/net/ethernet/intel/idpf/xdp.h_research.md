# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.h

## Purpose
Declares IDPF XDP entry points and provides inline descriptor helpers for XDP transmit finalization and advanced RX descriptor metadata extraction. It bridges IDPF descriptor formats from `idpf_txrx.h` and `virtchnl2_lan_desc.h` with generic libeth XDP helpers.

## Important APIs, Types, And Functions
The header declares RXQ registration/deinit helpers, BPF program propagation, XDP SQ allocation/free, XDP SQ completion polling, bulk Tx flush, `idpf_xdp_set_features()`, netdev BPF setup `idpf_xdp()`, and `idpf_xdp_xmit()`. `idpf_xdp_tx_xmit()` writes one hardware flex Tx descriptor from a libeth XDP descriptor, setting descriptor type, EOP, optional checksum offload, DMA address, and length.

`idpf_xdpsq_set_rs()`, `idpf_xdpsq_update_tail()`, and `idpf_xdp_tx_finalize()` set the report-status bit, perform a DMA write barrier, update the hardware tail register, and queue cleanup timer when a batch needs flushing. `struct idpf_xdp_rx_desc` normalizes selected fields from `virtchnl2_rx_flex_desc_adv_nic_3`. Accessor macros expose buffer queue ID, generation bit, length, ptype, buffer ID, EOP, RSS hash, and timestamp low/high fields. `idpf_xdp_get_qw0()` through `idpf_xdp_get_qw3()` load descriptor qwords either by direct word access or by endian-safe field assembly.

## Control Flow
The inline Tx path is called from generated libeth bulk-flush helpers in `xdp.c`: prepare a queue, fill descriptors for frames, then finalize by setting RS and ringing the tail if requested or when the queue is near full. The RX metadata path in `xdp.c` calls the qword extraction helpers lazily, only reading the descriptor qwords needed for hash or timestamp operations.

## State And Persistence
The header manipulates hardware-visible Tx descriptors, queue `next_to_use`, pending count, tail MMIO register, and cleanup timer scheduling. RX descriptor helpers are read-only normalizers over DMA writeback descriptors. It does not own persistent state beyond inline updates to queue rings and locks supplied by callers.

## Dependencies And Integration Points
It includes `net/libeth/xdp.h` and `idpf_txrx.h`, and uses descriptor constants and structures from the IDPF Tx/Rx stack. It integrates with `xdp.c`, libeth XDP bulk APIs, IDPF queue flags and tail registers, virtchnl2 advanced RX descriptor layout, XSK metadata paths, and PTP/RSS metadata consumers.

## Risks
Descriptor packing must match hardware layout for both `__LIBETH_WORD_ACCESS` and portable endian-safe paths. Missing the DMA write barrier before tail update can expose incomplete descriptors to hardware. `idpf_xdp_tx_finalize()` has subtle flush conditions: it avoids unnecessary tail writes unless a flush is requested, frames were sent, or the queue is effectively full. RX descriptor field masks must stay synchronized with `virtchnl2_lan_desc.h`; otherwise hash, ptype, timestamp, or length metadata will be wrong.

## Test Signals
Signals include XDP transmit descriptor inspection under checksum and multi-frame flags, queue tail updates after flush, completion timer scheduling, descriptor qword extraction on little-endian and non-word-access builds, RX hash and timestamp metadata tests, static assertions for RX descriptor size, and ring boundary tests where `next_to_use` wraps to zero.
