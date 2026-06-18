# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.h

## Purpose
This header defines PF transmit-side software and hardware formats: scatter/gather descriptors, Tx buffer metadata, interface and queue stats, Input Queue state, instruction header, Tx offload flags, optional metadata, and the 64-byte hardware Tx descriptor.

## Important APIs, Types, And Functions
- SGL format: `struct octep_tx_sglist_desc` stores four 16-bit lengths and four DMA pointers; `OCTEP_SGLIST_ENTRIES_PER_PKT` and `OCTEP_SGLIST_SIZE_PER_PKT` size per-packet SGL storage.
- Buffer bookkeeping: `struct octep_tx_buffer` tracks skb, DMA address, SGL pointers, and gather flag.
- Stats: `struct octep_iface_tx_stats` mirrors hardware interface counters; `struct octep_iq_stats` tracks posted/completed/dropped instructions, bytes, SGL packets, busy events, and restarts.
- Queue state: `struct octep_iq` stores ring indices, descriptor/SGL memory, MMIO registers, netdev queue pointer, fill counts, and stats.
- Hardware descriptor: `struct octep_instr_hdr`, `struct tx_mdata`, and `struct octep_tx_desc_hw`; static asserts enforce descriptor ABI sizes.
- Offload helpers: `OCTEP_TX_OFFLOAD_*`, `OCTEP_TX_IP_CSUM()`, and `OCTEP_TX_TSO()`.

## Control Flow
`octep_main.c` fills `octep_tx_desc_hw` in the transmit path, `octep_tx.c` allocates and frees the rings and consumes completion state, and chip-specific register code binds each `octep_iq` to doorbell, instruction count, and interrupt-level registers. Offload flags are derived from firmware-advertised capabilities and netdev feature settings before descriptors are posted.

## State And Persistence
The structs define runtime-only state. Hardware reads descriptors and SGLs from DMA memory, while software tracks ownership with `host_write_index`, `octep_read_index`, and `flush_index`. Interface stats are copied from hardware elsewhere; per-IQ stats are accumulated in memory.

## Dependencies And Integration Points
The header is included by `octep_main.h`, `octep_tx.c`, PF main transmit logic, and ethtool/stat code. It depends on Linux skb, DMA, netdev queue, and bit macro types through source context. Its descriptor layout is an ABI with OCTEON firmware/hardware.

## Risks And Edge Cases
- Static layout constraints must remain unchanged for hardware compatibility.
- The SGL length order uses reversed length slots relative to pointer index; mapping and unmapping code must agree.
- Offload metadata is byte-swapped before hardware because of ESR behavior; missing or duplicate swapping breaks Tx offloads.
- `u16` ring indices constrain practical descriptor counts and assume mask-based wrap.

## Test Signals
Compile-time static asserts, Tx packet transmission with and without fragments, maximum-fragment skb transmission, TSO and checksum offload validation, completion and BQL stat consistency, and hardware descriptor dump inspection are the main signals.
