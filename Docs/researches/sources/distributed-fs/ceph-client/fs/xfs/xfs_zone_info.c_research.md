# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_info.c

## Purpose
`xfs_zone_info.c` renders zoned XFS runtime allocator and GC state into a seq_file statistics view.

## Important APIs, types, and functions
The exported function is `xfs_zoned_show_stats`. Helpers include `xfs_write_hint_to_str`, `xfs_show_open_zone`, and `xfs_show_full_zone_used_distribution`.

## Control flow
The stats function prints user and reserved realtime free counters, whether reservations or GC are required, total/free/open zone counts, each open zone with write pointer, written blocks, used blocks, write hint, and GC marker, then prints the distribution of fully written reclaimable zones by used-block bucket plus inferred completely full zones.

## State and persistence
It reads live in-memory state from `m_zone_info`, free counters, open-zone lists, atomic free-zone count, and used-bucket bitmaps. It does not mutate persistent state.

## Dependencies and integration points
It depends on `seq_file`, zoned allocator private structures, realtime group helpers, and `xfs_zoned_need_gc`. It is used by XFS stats/debug reporting paths that include zoned-specific output.

## Risks and test signals
Risks include reporting inconsistent snapshots while zones change, arithmetic underflow when deriving full zones, and lock coverage around open-zone and bucket lists. Test signals include reading stats during concurrent writeback, GC, reset, mount with no open zones, and varied write-life hints.
