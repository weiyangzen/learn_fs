# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_cbdr.c

## Purpose
Provides control buffer descriptor ring support for ENETC command operations. Rev 1 hardware uses `struct enetc_cbdr` and `struct enetc_cbd`; ENETC4 delegates command-ring setup and RSS table access to the NTMP library.

## Important APIs, Types, and Functions
Exports `enetc_setup_cbdr`, `enetc_teardown_cbdr`, `enetc_send_cmd`, `enetc_clear_mac_flt_entry`, `enetc_set_mac_flt_entry`, `enetc_set_fs_entry`, `enetc_get_rss_table`, `enetc_set_rss_table`, `enetc4_setup_cbdr`, `enetc4_teardown_cbdr`, `enetc4_get_rss_table`, and `enetc4_set_rss_table`. Internal helpers include `enetc_clean_cbdr`, `enetc_cbd_unused`, and `enetc_cmd_rss_table`.

## Control Flow
Legacy setup allocates coherent descriptors, enforces 128-byte DMA alignment, writes CBDR base/length/cache attributes, initializes producer/consumer indices, and enables the ring. `enetc_send_cmd` copies a command descriptor to the next slot, updates PIR, busy-waits for CIR under contexts that may hold RTNL, copies writeback data, and cleans completed descriptors. RFS and RSS commands allocate aligned command data buffers, populate descriptor class/cmd fields, send, and free DMA data.

## State and Persistence
Software ring state tracks `next_to_clean`, `next_to_use`, DMA base, ring size, register pointers, and owning DMA device. Hardware state persists in CBDR mode/base/length/PIR/CIR registers and in command-programmed tables such as MAC filters, RFS entries, and RSS indirection. ENETC4 stores equivalent command-ring state in `si->ntmp_user`.

## Dependencies and Integration Points
Used by PF, VF, ethtool RX classification, RSS, and QoS/PSFP command paths. It depends on ENETC register accessors, `enetc_cbd_alloc_data_mem` and `enetc_cbd_free_data_mem` from common driver code, and NTMP functions for rev 4 table management.

## Risks
Risks include missing synchronization around callers using the legacy ring, fixed busy-wait timeouts, unaligned DMA rejection, descriptor status masking that only logs command status during cleaning, and RSS count assumptions requiring a full hardware table. ENETC4 wrappers require NTMP user initialization before ethtool RSS operations.

## Test Signals
Probe should fail cleanly on allocation or alignment failure. Exercise MAC exact filters, ethtool RXNFC RFS rules, RSS get/set, CBDR timeout injection, and teardown after failed mid-probe command setup. Command errors should produce warnings without leaving stale descriptors.
