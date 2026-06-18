<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_ethtool.c

## Purpose

`enic_ethtool.c` implements ENIC ethtool operations: driver/link information, hardware and software statistics, ring sizing, interrupt coalescing including adaptive RX coalescing, RX classifier rule introspection, RSS key get/set, RSS hash fields, timestamp capability, and channel counts.

## Important APIs, Types, and Functions

Statistic descriptors are represented by `struct enic_stat` and macros mapping field names to `u64` offsets in firmware and per-queue stats. Public setup is `enic_set_ethtool_ops`. Key functions include `enic_get_ksettings`, `enic_get_drvinfo`, `enic_get_strings`, `enic_get_ringparam`, `enic_set_ringparam`, `enic_get_sset_count`, `enic_get_ethtool_stats`, message-level get/set, `enic_get_coalesce`, `enic_set_coalesce`, RXNFC helpers, `enic_get_rxfh`, `enic_set_rxfh`, `enic_get_rx_flow_hash`, `enic_get_ts_info`, and `enic_get_channels`.

## Control Flow

Link settings combine PCI subsystem IDs with carrier state to report supported media and current speed/duplex. Stats dumping fetches firmware counters with `enic_dev_stats_dump`, then appends driver generic, per-RQ, and per-WQ stats. Ring parameter changes validate ranges, close the interface if running, align counts down to 32, free/reallocate/reinitialize vNIC resources, and reopen if needed; on error it restores saved counts.

Coalescing validation clamps values to firmware max, rejects TX coalescing outside MSI-X mode, and validates adaptive RX low/high ranges. Setting coalescing programs TX interrupt timers for WQs, optionally programs fixed RX timers, and updates adaptive RX range state. RXNFC reads the in-memory RFS classifier table; it does not install arbitrary user rules. RSS key set rejects indirection table changes and unsupported hash functions, copies the key, and calls `__enic_set_rsskey`.

## State and Persistence Behavior

Ettool operations mutate in-memory and firmware-backed settings: ring descriptor counts, RSS key, interrupt coalescing timers, adaptive RX coalescing ranges, and message level. These settings persist for the lifetime of the device instance but are not stored across driver reload.

## Dependencies and Integration Points

The file depends on ENIC devcmd wrappers, classifier table state, vNIC RSS/stat structures, and PCI subsystem IDs from `enic.h`. It is attached to each netdev by `enic_set_ethtool_ops` during probe.

## Risks and Edge Cases

Ring resize has a notable failure mode: if reallocation fails after counts were changed, it restores counts but does not reallocate old resources before returning, leaving recovery to higher-level handling. Stats and driver-info functions silently return old/partial data on non-ENOMEM devcmd failures. RXNFC operates on RFS filters only, so user expectations for programmable ntuple rules may not match behavior. Coalescing values are clamped after warning, not rejected except for invalid relationships.

## Test Signals

Use `ethtool -i`, `-S`, `-g/-G`, `-c/-C`, `-n`, `-x/-X`, `-k`, and channel queries across interrupt modes. Validate running ring resize, resize failure injection, adaptive coalescing ranges, RSS key programming, RFS filter reporting, and media reporting for multiple VIC subsystem IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_ethtool.c -->
