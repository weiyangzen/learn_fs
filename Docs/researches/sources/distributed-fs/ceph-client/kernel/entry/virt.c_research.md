# sources/distributed-fs/ceph-client/kernel/entry/virt.c

## Purpose

`virt.c` handles generic pending work before transferring execution into a virtual guest, such as KVM guest mode. It lets the outer guest loop service signals, rescheduling, notify-resume work, and architecture-specific guest-transfer work before entering the guest.

## Important APIs, Types, And Functions

- `xfer_to_guest_mode_work()` loops over `XFER_TO_GUEST_MODE_WORK` thread flags.
- `xfer_to_guest_mode_handle_work()` is the exported public entry point for virtualization code.
- It calls `schedule()`, `resume_user_mode_work(NULL)`, and `arch_xfer_to_guest_mode_handle_work(ti_work)`.

## Control Flow

`xfer_to_guest_mode_handle_work()` reads thread flags with interrupts and preemption already enabled. If no guest-transfer work is pending it returns zero. Otherwise it calls the internal loop. The loop returns `-EINTR` immediately for pending signals or notify-signal work, schedules for resched flags, handles notify-resume work, delegates architecture-specific work, and rereads flags until no guest-transfer work remains. Any nonzero architecture return is propagated.

## State And Persistence Behavior

No persistent state is owned here. The function services per-task thread flags, scheduler state, resume-user-mode callbacks, and architecture-specific guest-entry state.

## Dependencies And Integration Points

It integrates with `entry-virt.h`, KVM or other virtualization outer loops, scheduler rescheduling, signal/notify flags, resume-user-mode work, and architecture-specific guest transfer hooks. It is exported GPL for virtualization users.

## Risks And Edge Cases

- Callers must enter with interrupts and preemption enabled as documented; the inner KVM loop checks pending work with interrupts disabled but this handler services it outside that context.
- Signals are prioritized with `-EINTR` so guest entry can be aborted cleanly.
- Architecture hooks can impose additional failure modes that must be propagated to the virtualization caller.

## Test Signals

Use KVM guest-entry tests with pending signals, lazy and normal reschedule flags, notify-resume work, architecture hook failures, and repeated flag changes while the loop runs.
