# sources/distributed-fs/ceph-client/drivers/misc/ntsync.c

## Purpose
This misc driver implements Windows NT-style synchronization primitives in the kernel for userspace compatibility layers. It provides file-backed semaphore, mutex, and event objects plus wait-any and wait-all ioctls through `/dev/ntsync`.

## Important APIs, types, and functions
Core structures are `ntsync_device`, `ntsync_obj`, `ntsync_q`, and `ntsync_q_entry`. Object operations include semaphore release/read, mutex unlock/kill/read, event set/reset/pulse/read, object allocation, object file creation, and object release. Wait operations include `setup_wait()`, `ntsync_wait_any()`, `ntsync_wait_all()`, `ntsync_schedule()`, and wake helpers `try_wake_any_sem()`, `try_wake_any_mutex()`, `try_wake_any_event()`, `try_wake_all()`, and `try_wake_all_obj()`. Entry points are `ntsync_char_open()`, `ntsync_char_release()`, `ntsync_char_ioctl()`, and `ntsync_obj_ioctl()`.

## Control flow and state
Opening `/dev/ntsync` creates an isolated namespace with a device-wide `wait_all_lock`. Create ioctls return anonymous-inode fds for objects tied to that namespace. Object ioctls mutate object state and wake waiters. Wait-any queues entries on each object's `any_waiters`, checks in API order, sleeps with absolute monotonic or realtime timeout, unqueues, and returns the signaled index. Wait-all queues on each object's `all_waiters` under `wait_all_lock`, atomically locks all objects by setting `dev_locked`, consumes all signaled states together, optionally checks an alert object, then sleeps/unqueues.

## State and persistence behavior
All state is file-lifetime kernel memory. Objects hold references to the namespace file; waits hold object file references. Semaphores track count/max, mutexes track recursive count/owner/ownerdead, and events track manual-reset/signaled. No state persists after file descriptors close.

## Dependencies and integration points
It depends on anonymous inodes, miscdevice, hrtimer scheduling, signal handling, spinlocks, mutexes, user-copy, and UAPI `linux/ntsync.h`. Userspace interacts only via fds and ioctls; mode `0666` lets unprivileged processes create isolated namespaces.

## Risks and test signals
Risks include subtle lock ordering between object spinlocks and `wait_all_lock`, lost wakeups around CAS on `q->signaled`, all-wait duplicate-object rejection, ownerdead propagation, recursive mutex overflow, semaphore overflow, alert-event ordering, timeout clock semantics, and cleanup with blocked waiters. Test signals include Wine/NT primitive conformance, wait-any order, wait-all atomic consumption, manual vs auto event behavior, pulse semantics, signal interruption, timeout behavior on both clocks, object fd namespace isolation, lockdep, and stress with concurrent close/ioctl/wait.
