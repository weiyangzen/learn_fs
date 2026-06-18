# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.h

Public interface for copygc state reporting, wakeup, lifecycle, and progress heuristics.

Key contents:
- Declares wait/progress calculations and wait-state text formatter.
- `bch2_copygc_wakeup()` increments `kick_count` and wakes the copygc thread under RCU.
- Declares start/stop and fs init/exit hooks.

Dependencies and interactions:
- Used by allocator paths to wake copygc when allocation is blocked or fragmentation requires progress.
