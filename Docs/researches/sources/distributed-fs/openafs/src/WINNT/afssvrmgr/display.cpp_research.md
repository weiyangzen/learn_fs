# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/display.cpp

## Purpose
`display.cpp` is the asynchronous display scheduler for the Server Manager UI. It accepts display refresh requests, coalesces redundant work, runs up to four update threads, dispatches to the `dispguts.cpp` internals, and completes FastList/combobox transactions once all pending refreshes for a window finish.

## Important APIs, Types, And Functions
Public routines include `GetItemText`, `UpdateDisplay`, `UpdateDisplay_Cell`, `UpdateDisplay_Servers`, `UpdateDisplay_Services`, `UpdateDisplay_Aggregates`, `UpdateDisplay_Filesets`, `UpdateDisplay_Replicas`, `UpdateDisplay_ServerWindow`, `UpdateDisplay_SetIconView`, `Display_GetServerIconView`, and `HandleColumnNotify`. Important private state includes `aDisplayQueue`, `cDisplayQueueActive`, `cUpdateThreadsActive`, critical sections, active request snapshots per target, and `aWindowActOnDone` for deferred end-change actions.

## Control Flow
`UpdateDisplay()` validates and copies a `DISPLAYREQUEST`, initializes queue state lazily, applies `DisplayQueueFilter()` against queued and active work, increments a per-window outstanding count, and either runs synchronously for `fWait` or starts `DisplayQueue_ThreadProc`. The thread pulls queued requests, records the active request, enters AFSClass, dispatches to the appropriate internal display routine, decrements the per-window count, and either performs final UI actions or records them for a later request on the same control. Wrapper functions construct standard request packets for common targets.

## State And Persistence
Display state is process-local. Queue storage grows in chunks of 128 entries and never shrinks. Per-window counters are maintained through `InterlockedIncrementByWindow` and `InterlockedDecrementByWindow`. Completion actions and desired selection are stored in `aWindowActOnDone` until the last outstanding operation for a list finishes. Column sort/width changes are persisted indirectly by `FL_StoreView` into the supplied `VIEWINFO`, which is later saved with global settings.

## Dependencies And Integration Points
The module depends on Win32 threads and critical sections, FastList callbacks, AFSClass locking, `Main_StartWorking`/`Main_StopWorking`, server-window helpers, property cache lookup, global view state `gr`, and the internal display functions declared by `dispguts.h`. `GetItemText` integrates every list view with server/service/aggregate/fileset/replica column formatters.

## Risks And Edge Cases
The queue is global and lazily initialized without an outer initialization lock, so first-use concurrency is sensitive. `DisplayQueueFilter()` deliberately drops requests when broader refreshes cover them; bugs here cause stale UI. `UpdateDisplay(..., TRUE)` executes immediately on the caller and the header warns not to block the main thread. `aWindowActOnDone` entries are reused but not compacted. UI updates from worker threads are legacy Win32-style and rely on controls tolerating these calls.

## Test Signals
Test signals include duplicate request coalescing, broad-refresh versus narrow-refresh ordering, active-request filtering, synchronous refresh behavior, maximum update-thread fan-out, correct `FL_EndChange`/`CB_EndChange` after multiple outstanding requests, selection preservation, preview-pane update, column resize/click persistence, and icon-view switching.
