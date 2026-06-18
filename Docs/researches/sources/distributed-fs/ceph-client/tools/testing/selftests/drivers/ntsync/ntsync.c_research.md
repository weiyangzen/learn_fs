# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/ntsync.c

## Purpose
Comprehensive unit/integration test for the ntsync synchronization primitive driver UAPI. It validates semaphore, mutex, event, wait-any, wait-all, alertable wait, wakeup, owner-death, duplicate-object, limit, timeout, close-while-waiting, and stress behavior through `/dev/ntsync`.

## Important APIs, Types, And Functions
Uses ioctls `NTSYNC_IOC_CREATE_SEM`, `NTSYNC_IOC_SEM_READ/RELEASE`, `NTSYNC_IOC_CREATE_MUTEX`, `NTSYNC_IOC_MUTEX_READ/UNLOCK/KILL`, `NTSYNC_IOC_CREATE_EVENT`, `NTSYNC_IOC_EVENT_READ/SET/RESET/PULSE`, `NTSYNC_IOC_WAIT_ANY`, and `NTSYNC_IOC_WAIT_ALL`. Helpers include `read_sem_state()`, `release_sem()`, `read_mutex_state()`, `unlock_mutex()`, `read_event_state()`, `wait_objs()`, wait wrappers, `wait_thread()`, `get_abs_timeout()`, and `wait_for_thread()`.

## Control Flow
Each `TEST()` opens `/dev/ntsync`, creates objects, performs state transitions, and asserts return codes, errno, indexes, counts, owners, and signal states. Threaded tests start a blocking ioctl in a pthread, verify it remains blocked with timed join, release/set/unlock an object, then verify the waiter wakes with correct index and consumed state. Stress creates four threads repeatedly acquiring an ntsync mutex after a start event and checks the shared counter reaches `STRESS_LOOPS * STRESS_THREADS`.

## State And Persistence
State lives in kernel ntsync file descriptors and object descriptors. Static globals are used only for the stress test (`stress_counter`, `stress_device`, `stress_start_event`, `stress_mutex`). No persistent state is written.

## Dependencies And Integration Points
Requires `/dev/ntsync`, the ntsync UAPI header, pthreads, and kselftest harness. It tests behavior intended to match Windows-style synchronization semantics.

## Risks
Timed joins use short 100-200 ms windows and can be sensitive on very slow systems. Some tests intentionally pass duplicate descriptors, zero counts, max counts, invalid owners, and closed descriptors; incorrect cleanup can cascade if a prior ASSERT aborts a test body.

## Test Signals
Primary signals are exact errno values (`EINVAL`, `EOVERFLOW`, `ETIMEDOUT`, `EPERM`, `EOWNERDEAD`), state reads after every transition, wake indexes for alert/object waits, no premature wakeups, and stress counter equality.
