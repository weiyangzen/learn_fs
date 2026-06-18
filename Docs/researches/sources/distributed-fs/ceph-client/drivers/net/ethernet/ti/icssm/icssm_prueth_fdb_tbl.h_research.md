# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_fdb_tbl.h

## Purpose
This header defines the firmware-shared forwarding database layout for ICSSM switch mode. The host driver and PRU firmware both view the same shared-RAM table, so the structures describe the exact index table, MAC table, STP state, flood-enable flags, and arbitration bytes.

## Important APIs, types, and functions
- `struct fdb_index_tbl_entry` maps an 8-bit hash bucket to a first MAC-table index and bucket entry count.
- `struct fdb_index_array` contains 256 bucket entries.
- `struct fdb_mac_tbl_entry` stores a MAC address, age, zero-based port, and packed `is_static`/`active` flags.
- `struct fdb_mac_tbl_array` contains 256 MAC entries.
- `struct fdb_stp_config` and `struct fdb_flood_config` provide per-port STP and flooding policy bytes.
- `struct fdb_arbitration` contains host and PRU lock bytes for shared table arbitration.
- `struct fdb_tbl` is the host-side collection of `__iomem` pointers to each firmware table section plus the host-maintained total entry count.

## Control flow
The header has no executable code. `icssm_prueth_switch.c` maps these structures onto offsets from `icssm_switch.h`, initializes flood flags and lock bytes, then uses the index and MAC arrays to add/delete/learn/purge FDB entries while coordinating with PRU locks.

## State and persistence behavior
FDB contents persist only while switch firmware and driver state are active. Actual entries live in PRUSS shared RAM; `struct fdb_tbl` holds host pointers and a software `total_entries` counter allocated during switch open and freed after switch shutdown when no EMAC remains configured.

## Dependencies and integration points
The file depends on Linux kernel/debugfs includes and local ICSSM definitions. Its struct sizes feed the shared-memory offsets in `icssm_switch.h`, so it is part of the firmware ABI. It is consumed by `icssm_prueth_switch.c` and `icssm_switchdev.c`.

## Risks and edge cases
- Bitfields and structure packing must stay ABI-compatible with firmware expectations.
- `total_entries` is host-side only; firmware aging behavior can diverge unless constrained.
- The 8-bit XOR hash and fixed 256-entry MAC table bound scale and collision behavior.
- The host/PRU lock is a byte-level protocol; timeout or stale locks directly affect switchdev updates.

## Test signals
Exercise FDB insert/delete/learn/purge under traffic, full-table conditions, duplicate MAC updates, STP state changes, and concurrent firmware learning. Confirm structure sizes and offsets against firmware documentation or integration tests.
