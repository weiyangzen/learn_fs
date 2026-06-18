# File Research: sources/cow-pools/nilfs-utils/lib/cnormap.c

Implements checkpoint-number reverse mapping for time-based protection periods. It builds a history of checkpoint spans containing start/end checkpoint numbers, timestamps, and approximate checkpoint counts.

The mapper detects available clocks (`CLOCK_BOOTTIME`, coarse realtime, coarse monotonic) and falls back when unsupported. It enumerates checkpoint info forward or backward with callback-driven scanners, tracks elapsed time across spans, handles clock rewinds as a one-second gap, and caches history between calls.

`nilfs_cnormap_track_back()` returns the earliest checkpoint still inside a requested period, or `NILFS_CNO_MAX` when none is found. `lssu` uses this for latest-usage protection calculations.
