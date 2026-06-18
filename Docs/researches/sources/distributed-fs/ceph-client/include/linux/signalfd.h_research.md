# sources/distributed-fs/ceph-client/include/linux/signalfd.h

## Purpose

`signalfd.h` connects signal delivery with signalfd waiters. It provides a notification hook that wakes signalfd readers when a task receives a signal and a cleanup hook for sighand teardown, with no-op stubs when signalfd is disabled.

## Important APIs, Types, And Functions

The APIs are `signalfd_notify()` and `signalfd_cleanup()`. When `CONFIG_SIGNALFD` is enabled, `signalfd_notify()` checks `tsk->sighand->signalfd_wqh` with `waitqueue_active()` and wakes it if needed. `signalfd_cleanup()` is declared for implementation code. When disabled, both helpers compile to empty inline functions.

## Control Flow

Signal delivery paths call `signalfd_notify()` after signal state changes. If a signalfd reader is sleeping on the sighand waitqueue, the helper wakes the queue so userspace can read signal records. Sighand teardown calls `signalfd_cleanup()` to release signalfd-related state.

## State And Persistence

The waitqueue is stored in `sighand_struct`, not this header. The helper does not modify signal state; it only wakes waiters. Disabled builds preserve call-site behavior without state.

## Dependencies And Integration Points

Dependencies are UAPI signalfd structures and `linux/sched/signal.h` for task and sighand fields. Integration points are signal delivery, signalfd file operations, poll/select wakeups, and sighand lifetime management.

## Risks And Test Signals

Risks are missed wakeups if signal state changes without calling the helper, dereferencing sighand after teardown, and build differences when `CONFIG_SIGNALFD` is disabled. Test signals include signalfd read/poll selftests, signal mask changes with signalfd, multithreaded delivery, sighand cleanup on exit, and disabled-config builds.
