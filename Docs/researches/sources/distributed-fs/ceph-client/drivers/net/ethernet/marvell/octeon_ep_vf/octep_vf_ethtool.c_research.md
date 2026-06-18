# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_ethtool.c

## Purpose
This file implements VF ethtool operations for driver info, link state, statistics strings/counts/values, link mode reporting, and channel counts.

## Important APIs, Types, And Functions
- Stats metadata: `octep_vf_gstrings_global_stats`, `octep_vf_gstrings_tx_q_stats`, and `octep_vf_gstrings_rx_q_stats`.
- Etthool callbacks: `octep_vf_get_drvinfo()`, `octep_vf_get_strings()`, `octep_vf_get_sset_count()`, `octep_vf_get_ethtool_stats()`, `octep_vf_get_link_ksettings()`, and `octep_vf_get_channels()`.
- Link mode mapping: `OCTEP_VF_SET_ETHTOOL_LINK_MODES_BITMAP()` converts OCTEON VF link-mode bits to ethtool link mode bits.
- Registration: `octep_vf_set_ethtool_ops()` assigns `octep_vf_ethtool_ops`.

## Control Flow
VF probe calls `octep_vf_set_ethtool_ops()`. User ethtool stats requests first fetch interface stats from PF via `octep_vf_get_if_stats()`, then combine global hardware stats with per-queue software stats. Link settings requests fetch link info from PF via `octep_vf_get_link_info()`, translate supported/advertised link bitmaps, report autoneg and fibre port mode, and use carrier state to decide whether speed/duplex are known.

## State And Persistence
The file stores no persistent state. It reads and updates `oct->iface_rx_stats`, `oct->iface_tx_stats`, and `oct->link_info` through mailbox calls, then reports in-memory queue stats. Etthool output is a point-in-time snapshot.

## Dependencies And Integration Points
It depends on Linux ethtool APIs, `octep_vf_main.h` for state and exported mailbox-backed helpers, and `octep_vf_config.h` for queue counts. It integrates with PF mailbox bulk reads for stats/link information.

## Risks And Edge Cases
- `octep_vf_get_sset_count()` uses active ring count, but `octep_vf_get_ethtool_stats()` iterates `OCTEP_VF_MAX_QUEUES` for Tx queue stats while strings are emitted only for active queues; this can misalign stats data if active queues are fewer than max.
- Mailbox failures in stats/link fetch are not surfaced strongly to ethtool users; stale cached values may be reported.
- Link mode bitmaps are assigned to `u32` even `link_info` stores `u64`, so upper link mode bits would be truncated if added later.
- The macro body is large and duplicated for supported/advertising; adding new link modes requires careful update.

## Test Signals
Run `ethtool -i`, `ethtool -S`, `ethtool -k`, `ethtool <dev>`, and channel queries on active VFs; compare stats string count to values returned; test link up/down notifications and link-ksettings output; simulate mailbox errors; and validate all supported speeds advertised by firmware are represented.
