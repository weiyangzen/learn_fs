# sources/distributed-fs/openafs/src/afs/AIX/osi_timeout.c

Purpose: AIX compatibility implementation of BSD-style `timeout`, `untimeout`, and callout-table sizing using AIX timer request blocks.

Important APIs and functions: `timeout` schedules or replaces a callback; `untimeout` cancels a pending callback; `timeout_end` is the TRB callback trampoline; `timeoutcf` grows or shrinks the callout table.

Control flow: `timeout` converts ticks to seconds/nanoseconds, locks `afs_callout_lock` at interrupt priority, finds an existing matching callback or a free slot, stops any active TRB, initializes it, and starts it. `timeout_end` clears the slot under lock and then invokes the original function. `timeoutcf` allocates/frees `struct tos` plus `trb` entries, removing only inactive slots when shrinking.

State and persistence: in-memory `afs_callo` linked list tracks callout entries; each `tos` owns one `trb`, callback identity, and temporary type/p1 fields.

Dependencies and integration: initialized by `osi_config.c` via `timeoutcf(AFS_CALLOUT_TBL_SIZE)` and protected by `afs_callout_lock`.

Risks and test signals: table exhaustion asserts instead of recovering; cancellation loops retry when `tstop` races with active timers. Signals include successful callback execution/cancellation and clean table shrink during module unload.
