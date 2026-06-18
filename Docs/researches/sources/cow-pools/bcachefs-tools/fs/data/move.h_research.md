# File Research: sources/cow-pools/bcachefs-tools/fs/data/move.h

## Purpose
Public movement API plus `struct moving_context`, wait macros, predicate signature, and movement/scrub declarations.

## Main Interfaces and Behavior
- `struct moving_context` tracks a transaction, list linkage, caller IP, rate limiter, stats, write point, copygc wait preference, closure, IO lists, sequence counter, atomic read/write sector and IO counters, mutex, and waitqueue.
- `move_ctxt_wait_event_timeout()` and `move_ctxt_wait_event()` drain pending writes before waiting and unlock the transaction during long waits.
- `move_pred_fn` lets callers inspect a btree key and fill `data_update_opts` for selected movement.
- Declares context lifecycle, pending write handling, rate limiting, extent movement, logical and physical scan helpers, evacuation helpers, journal scrub/repair, ioctl data job dispatch, stats rendering, and filesystem move init/exit.

## Dependencies
Includes ioctl data definitions, bucket helpers, bbpos, btree iterator, data update, and movement types.

## Risks and Invariants
- Wait macros assume the context’s transaction can be dropped during long waits.
- The comments document the in-flight IO accounting contract used by both extent moves and stripe repairs.
