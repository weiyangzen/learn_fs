# File Research: sources/cow-pools/bcachefs-tools/fs/data/copygc.h

Declares copygc control, diagnostics, and wakeup APIs.

Key responsibilities:
- Declares wait amount helpers, diagnostic text output, progress predicate, start/stop, and fs init/exit functions.
- Defines `bch2_copygc_wakeup()` to increment `kick_count` and wake the copygc thread under RCU.

Important interactions:
- Used by allocator paths and EC creation/allocation paths to avoid waiting forever when copygc can free fragmented space.
