# sources/distributed-fs/ceph-client/ipc/msgutil.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/msgutil.c` provides shared message payload allocation, user copy, duplication, and free helpers for System V message queues and POSIX mqueues. It also defines `init_ipc_ns` and `mq_lock` for build configurations where only one IPC family is enabled. The source was read as a complete 192-line file.

## Important APIs, Types, and Functions

`DEFINE_SPINLOCK(mq_lock)` protects mqueue namespace/mount teardown races. `struct ipc_namespace init_ipc_ns` seeds the initial IPC namespace. Message storage uses a head `struct msg_msg` followed by optional `struct msg_msgseg` continuation pages. `init_msg_buckets()` creates bucketed allocations for message heads. `load_msg()` allocates and copies user payload into segmented kernel memory, `store_msg()` copies it back to userspace, `copy_msg()` supports checkpoint/restore message copying, and `free_msg()` releases LSM state plus all segments.

## Control Flow

`alloc_msg()` allocates enough head storage for `DATALEN_MSG` and chains additional `msg_msgseg` allocations for larger payloads. `load_msg()` copies each segment from userspace and then calls `security_msg_msg_alloc()`. `store_msg()` walks the same segmentation layout in the opposite direction. `free_msg()` calls `security_msg_msg_free()` and frees the head and all segments with reschedule points for long chains.

## State and Persistence Behavior

Message payloads persist only while held by a queue, a blocked sender/receiver handoff, or a temporary copy operation. The global bucket allocator persists after `subsys_initcall`. `init_ipc_ns` persists for the kernel lifetime.

## Dependencies and Integration Points

This file integrates slab bucket allocation, LSM message hooks, user-copy APIs, IPC namespace initialization, namespace tree/proc namespace headers, and both `msg.c` and `mqueue.c`.

## Risks and Edge Cases

Segment accounting must match the payload length exactly across allocation, copy-in, copy-out, and free. Failure after partial allocation or partial user copy must release all segments. `copy_msg()` is gated by checkpoint/restore; callers must handle `-ENOSYS` when unsupported. The shared `init_ipc_ns` definition must be available for config combinations selected by the Makefile.

## Test Signals

Tests should cover zero-length, small, page-sized, and multi-page messages; copy_from_user/copy_to_user faults at different segment boundaries; LSM allocation failure; checkpoint/restore `MSG_COPY`; and kmemleak or fault-injection runs for partial allocation cleanup.
