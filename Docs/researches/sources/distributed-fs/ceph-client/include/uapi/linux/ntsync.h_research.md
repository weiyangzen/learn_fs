# sources/distributed-fs/ceph-client/include/uapi/linux/ntsync.h

Purpose: Defines the ioctl ABI for Linux kernel emulation of Windows NT synchronization primitives used by Wine/Proton-style runtimes.

Important APIs/types/functions: Exports `struct ntsync_sem_args`, `struct ntsync_mutex_args`, `struct ntsync_event_args`, `struct ntsync_wait_args`, `NTSYNC_WAIT_REALTIME`, `NTSYNC_MAX_WAIT_COUNT`, creation ioctls for semaphores, mutexes, and events, wait-any/wait-all ioctls, and object operations such as semaphore release, mutex unlock/kill/read, and event set/reset/pulse/read.

Control flow: Userspace creates synchronization objects through an ntsync device fd, receives object fds, then waits on arrays of object fds through `NTSYNC_IOC_WAIT_ANY` or `NTSYNC_IOC_WAIT_ALL`. Wait arguments carry a userspace pointer to object references, a count capped by `NTSYNC_MAX_WAIT_COUNT`, timeout mode, owner ID, alert object, and return index.

State and persistence behavior: The header defines userspace-visible object state: semaphore count/max, mutex owner/recursion count, event manual-reset and signaled bits, and wait result fields. Object lifetime and wait queues persist only while kernel object fds are open.

Dependencies and integration points: Depends on `<linux/types.h>` and ioctl encoding macros. Integrates with `/dev/ntsync`, Wine synchronization layers, pollable file descriptors, and Linux wait queue implementation behind the driver.

Risks: Windows-compatible semantics are subtle: abandoned/killed mutexes, pulse events, alertable waits, timeout clock selection, and wait-all atomicity must match expectations. The ABI uses userspace pointers and owner IDs, so validation and 32/64-bit compatibility matter.

Test signals: Run Wine synchronization conformance tests, verify wait-any indexes, wait-all atomic acquisition, realtime versus monotonic timeouts, max wait count rejection, event pulse behavior, mutex kill/read semantics, and concurrent close during waits.
