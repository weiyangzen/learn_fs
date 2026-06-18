# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount.h

## Purpose

`statmount.h` provides local syscall wrappers and allocation helpers for `statmount` and `listmount` tests.

## Important APIs, Types, and Functions

It defines fallback syscall numbers for `statmount` and `listmount` on alpha, MIPS ABIs, and generic architectures. `statmount` builds `struct mnt_id_req` using mount id, mount namespace id, or fd when `STATMOUNT_BY_FD` is set. `listmount` builds a similar request with `last_mnt_id` in `param`. `statmount_alloc` and `statmount_alloc_by_fd` retry with doubling buffers on `EOVERFLOW`.

## Control Flow, State, and Persistence

Wrappers are synchronous syscall shims. Allocation helpers start at `STATMOUNT_BUFSIZE` (32 KiB), call the syscall, return the filled buffer on success, free and fail on non-overflow errors, or double the buffer on overflow. No state persists outside caller-owned allocated buffers.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on `<linux/mount.h>`, syscall ABI compatibility, and `struct mnt_id_req` version sizes. It integrates all statmount/listmount selftests and other namespace tests in this subset. Risks are stale fallback syscall numbers, ABI version mismatch, unbounded doubling on repeated overflow, and callers needing to free returned buffers. Passing signals are successful wrapper calls, correct fd-vs-id request selection, and overflow handling for string-heavy masks.
