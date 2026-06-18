# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.h

## Purpose

`cn10k_ipsec.h` defines the CN10K IPsec offload ABI used by the NIC driver: CPT instruction queue sizes, CPT LF register offsets, hardware state structures, outbound SA layout, CPT instruction/result/scatter-gather formats, register bit masks, and build-time stubs when XFRM offload is disabled.

## Important APIs, Types, And Functions

- Queue sizing macros define CPT instruction count, bytes, group queue bytes, extra required entries, and flow-control size.
- CPT LF register macros encode RVU function block address plus CPT LF offsets.
- Opcode macros identify write-SA and outbound IPsec operations.
- `enum cn10k_cpt_comp_e` lists CPT completion codes and mask.
- `struct cn10k_cpt_inst_queue` tracks real/aligned CPU and DMA pointers.
- `enum cn10k_cpt_hw_state_e` backs the atomic CPT availability state.
- `struct cn10k_ipsec` is embedded in `struct otx2_nic`.
- `struct cn10k_tx_sa_s` is the hardware outbound SA context, including cipher key, salt, and hardware context words.
- `struct cpt_inst_s`, `struct cpt_res_s`, and `struct cpt_sg_s` define CPT work queue ABI.
- Conditional prototypes/stubs expose `cn10k_ipsec_init()`, cleanup, ethtool toggle, SG setup, and transmit.

## Control Flow

This header has no runtime control flow except inline stubs. With `CONFIG_XFRM_OFFLOAD`, callers bind to real implementations. Without it, initialization and cleanup are no-ops, ethtool init returns success, and transmit/SG helpers return true, allowing the rest of the NIC code to compile without feature logic.

## State And Persistence

The header defines in-memory and DMA-visible state. `struct cn10k_ipsec` persists for the NIC lifetime. SA contexts and CPT instructions persist in coherent memory while offload is active. Hardware consumes the bitfield layouts exactly as written.

## Dependencies And Integration Points

It depends on Linux types and, through users, RVU block address shifts and CPT register semantics. It is included by `otx2_common.h` and transmit code. Its stubs are the integration boundary for kernels built without XFRM offload.

## Risks

- Bitfield layout must match CPT hardware exactly; compiler/endianness assumptions are critical.
- Stub `cn10k_ipsec_ethtool_init()` returning 0 when XFRM offload is absent can make callers treat unavailable offload as a successful no-op unless feature bits are also absent.
- Queue size constants must maintain hardware-required alignment and extra-entry constraints.
- SA key/salt fields are sensitive material and must be zeroed or freed carefully by implementations.

## Test Signals

Build with `CONFIG_XFRM_OFFLOAD=y` and disabled, verify object linkage/stubs, validate struct sizes/offsets against hardware specs, and run XFRM outbound offload tests that exercise CPT instruction/result/SG layout.
