# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fplustm.h

## Purpose
`fplustm.h` defines FORMAC+ tag-mode descriptor, queue, FIFO, error, multicast, and receive-mode structures used by `fplustm.c` and OS-specific descriptor management.

## Important APIs, Types, And Functions
Important types are `struct err_st`, `struct s_smt_fp_txd`, `struct s_smt_fp_rxd`, `union s_fp_descr`, `struct s_smt_tx_queue`, `struct s_smt_rx_queue`, `struct s_smt_fifo_conf`, and `struct s_smt_fp`. Constants define special frame offsets, RBC memory size, FIFO split sizes, queue indices, multicast table limits, receive-mode commands, and endian conversion macros (`AIX_REVERSE`, `MDR_REVERSE`).

## Control Flow
The header provides data layout only. `fplustm.c` fills queue pointers, FIFO starts/sizes, CAM tables, error stats, and FORMAC status shadows from these definitions. OS-specific TX/RX paths use descriptor fields and queue state to hand buffers to BMUs.

## State And Persistence
`struct s_smt_fp` is embedded in hardware state and persists for the adapter lifetime. Descriptor rings and FIFO configuration are runtime state mirrored into hardware registers; multicast table entries are reprogrammed after reset.

## Dependencies And Integration Points
It requires OS-specific `struct s_txd_os` and `struct s_rxd_os` from `osdef1st.h`/target headers, FDDI address types, FORMAC bit definitions, and descriptor access macros in `hwmtm.h`.

## Risks And Edge Cases
Descriptor layout is ABI-sensitive for DMA and 64-bit address support. FIFO constants assume the adapter memory map used by FORMAC+. `AIX_REVERSE` is overloaded by Linux to perform little-endian conversion, so direct descriptor reads without the macros can break endian behavior.

## Test Signals
Compile-time structure size checks, TX/RX descriptor ring initialization, 64-bit descriptor builds, FIFO splits for sync and async traffic, multicast table saturation, receive mode toggles, and endian-correct descriptor ownership/length/address reads.
