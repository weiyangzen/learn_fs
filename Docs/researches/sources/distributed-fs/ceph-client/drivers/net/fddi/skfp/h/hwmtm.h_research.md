# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/hwmtm.h

## Purpose
`hwmtm.h` defines the hardware-module abstraction for SMT mbuf pools, receive/transmit queues, OS-visible descriptor accessor macros, DMA sync placeholders, receive pass modes, frame status bits, debug hooks, and HWM error IDs.

## Important APIs, Types, And Functions
Key types are `struct s_mbuf_pool`, `struct hwm_r`, and `struct hw_modul`. Important macros include `HWM_GET_TX_PHYS()`, `HWM_GET_TX_LEN()`, `HWM_GET_TX_USED()`, `HWM_GET_CURR_TXD()`, `HWM_GET_RX_FRAG_LEN()`, `HWM_GET_RX_PHYS()`, `HWM_GET_RX_USED()`, `HWM_GET_RX_FREE()`, `HWM_GET_CURR_RXD()`, and `HWM_RX_CHECK()`.

## Control Flow
No code runs here, but OS-specific driver paths use these macros to inspect current descriptor positions, refill RX rings at low-water thresholds, track queued LLC/SMT mbufs, and decide whether frames are local, LAN-bound, first/last fragments, or failed due to ring/descriptor shortage.

## State And Persistence
`struct hw_modul` is runtime state under `smc->hw`: mbuf pool, descriptor base pointer, receive pass flags, RX/TX queues, ISR flags, current TX frame cursor, and error counters. It is rebuilt on driver init and reset.

## Dependencies And Integration Points
It includes `mbuf.h` and relies on descriptor types from `fplustm.h`, endian macros, OS-specific DMA synchronization, and `mac_drv_fill_rxd()` provided outside this header.

## Risks And Edge Cases
`DRV_BUF_FLUSH()` defaults to a no-op unless the OS layer overrides it; DMA coherency depends on the target integration. `HWM_GET_RX_FREE()` subtracts one descriptor for an ASIC workaround, so callers must not “fix” the apparent off-by-one. `HWM_RX_CHECK()` expands to code and depends on a valid `smc` expression.

## Test Signals
Descriptor accessor unit tests, RX low-water refill behavior, DMA sync override compilation, local/SMT/LAN frame status handling, no-buffer and out-of-TxD paths, ISR entry/exit state, and build checks for HWM error paths.
