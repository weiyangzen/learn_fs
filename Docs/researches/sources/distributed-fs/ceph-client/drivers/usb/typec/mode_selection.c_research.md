<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mode_selection.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mode_selection.c

## Purpose

`mode_selection.c` implements priority-based automatic Type-C alternate-mode activation for a partner. It builds a prioritized list of partner altmodes with activation callbacks, attempts entry in order, handles timeout/error callbacks, exits an already-active lower-priority mode, and cleans up when a mode succeeds or all candidates fail.

## Important APIs, Types, and Functions

Private state includes `struct mode_state`, `struct mode_selection`, and `struct mode_order`. Exported APIs are `typec_mode_selection_start()`, `typec_altmode_state_update()`, and `typec_mode_selection_delete()`. Core helpers are `activate_altmode()`, `mode_selection_activate()`, `mode_selection_work_fn()`, `altmode_add_to_list()`, `compare_priorities()`, and `mode_list_clean()`.

## Control Flow

Start refuses USB4 partners and duplicate selection sessions, collects partner altmode children that have a paired port altmode and an `activate` op, sorts them by port priority, stores delay/timeout, and schedules delayed work. Work examines the first candidate: if already active it cleans the list; if another SVID is active it exits that mode first; if the current candidate has an error it deactivates/removes it; otherwise it calls activate-enter and marks the candidate as timed out until a callback arrives. `typec_altmode_state_update()` updates the head candidate result, cancels/reschedules work immediately, and records the active SVID.

## State and Persistence Behavior

State is a per-partner heap allocation referenced by `partner->sel`. It contains a mutex-protected list, active SVID, delayed work, timeout and delay. No state persists after delete, success cleanup, or partner teardown.

## Dependencies and Integration Points

The code depends on the private Type-C partner structure, child alternate-mode devices, `typec_altmode_get_partner()`, altmode `activate` ops, Linux delayed work, list sorting, and mutexes. Port alternate-mode priority from `class.c` controls ordering.

## Risks and Test Signals

Risks include deadlock avoidance relying on the mode list remaining stable while the mutex is dropped, timeout/error races with delayed work cancellation, USB4 exclusion policy, memory cleanup on partial list construction, and a duplicated `struct mode_state *ms;` declaration in `typec_altmode_state_update()` in this source snapshot. Test signals include sorted activation order, failed first mode falling through to the next, timeout behavior, successful callback cleanup, active-mode exit before entering another mode, delete while work is pending, and no activation for partners without suitable altmode ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mode_selection.c -->
