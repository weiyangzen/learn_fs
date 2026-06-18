# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.c

## Purpose
`efc_sm.c` implements the minimal generic state-machine dispatcher used by libefc domain, nport, node, fabric, and device state handlers.

## Important APIs, Types, And Functions
`efc_sm_post_event` calls the current state handler with an event and optional data, returning `-EIO` when no handler is installed. `efc_sm_transition` posts EXIT to the old state, updates `current_state`, then posts ENTER to the new state, or posts REENTER if the target state is already current. `efc_sm_event_name` maps event enum values to strings via `EFC_SM_EVENT_NAME`.

## Control Flow And State
The dispatcher is synchronous and does not queue events. State handlers may recursively post additional events or transition again. State ownership and locking are entirely the caller's responsibility; most libefc callback entry points take `efc->lock` before posting.

## Dependencies And Integration Points
It includes `efc.h` and `efc_sm.h` and is used by every stateful object embedding `struct efc_sm_ctx`. Node-specific code wraps transition/post to add event-depth tracking and deferred freeing.

## Risks And Test Signals
Risks include recursion depth, handlers freeing their context during nested events, and `efc_sm_event_name` only checking `evt > EFC_EVT_LAST` rather than negative values. Test signals include transition enter/exit ordering, reenter behavior, disabled/null state handling, and event-name coverage for all enum values.
