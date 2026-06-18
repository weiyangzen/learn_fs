# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.h

Purpose: private state definition for the CSI RX resource manager.

Important type: `isys_csi_rx_rsrc_t` stores `active_table`, total `num_active`, and separate `num_long_packets`/`num_short_packets` counters.

Control flow/state: no functions; `csi_rx_rmgr.c` owns a per-backend array of this struct. `active_table` is a bitset used to allocate LUT entries.

Dependencies/integration: depends on integer types made available by included compile context; consumed only by the CSI RX manager implementation.

Risks: the `u32` bitmap limits directly encode maximum LUT entries. If hardware exposes more than 32 entries or long/short tables should have disjoint spaces, the struct needs redesign.

Test signals: build-time compatibility with `N_LONG_PACKET_LUT_ENTRIES`/`N_SHORT_PACKET_LUT_ENTRIES`, counter consistency after allocate/release, and zeroed init state.
