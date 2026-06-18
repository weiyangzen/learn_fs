# sources/distributed-fs/ceph-client/kernel/regset.c

## Purpose
`regset.c` provides small common helpers for fetching architecture-defined `user_regset` data from a target task into kernel memory or userspace. It is used by ptrace/core-dump-style code paths that consume `struct user_regset_view` without duplicating allocation, size clamping, and copy logic.

## Important APIs, Types, and Functions
- `__regset_get()` is the internal helper. It validates the `regset_get` callback, clamps requested size to `regset->n * regset->size`, allocates a zeroed buffer when the caller does not provide one, invokes the regset callback with a `struct membuf`, and returns bytes produced.
- `regset_get()` fetches data into caller-provided storage.
- `regset_get_alloc()` allocates storage and returns it through `void **data`.
- `copy_regset_to_user()` resolves a regset by index from a `user_regset_view`, obtains an allocated buffer, copies produced bytes to a user pointer, and frees the buffer.

## Control Flow
The common path enters `__regset_get()`. If the architecture regset has no getter, it returns `-EOPNOTSUPP`. The requested size is capped to the architectural maximum. If no buffer was supplied, it allocates with `kvzalloc()`. The regset callback writes through `struct membuf`, whose remaining length is returned as `res`; negative values abort and free any internal allocation. Success stores the buffer pointer and returns `size - res`.

`copy_regset_to_user()` uses `regset_get_alloc()`, treats positive returns as byte counts, copies exactly those bytes to userspace, maps copy failures to `-EFAULT`, frees with `kvfree()`, and returns either zero or the error.

## State and Persistence
The file has no global mutable state. Allocation is transient per call. The target task and regset callback own the actual register state; this helper only stages a snapshot in kernel memory.

## Dependencies and Integration Points
It depends on `linux/regset.h`, task structures, `struct user_regset`, `struct user_regset_view`, `struct membuf`, `kvzalloc()`, `kvfree()`, and `copy_to_user()`. Architecture code supplies regset definitions and callbacks.

## Risks
The main risks are incorrect size calculations in regset definitions, callbacks returning malformed remaining lengths, usercopy failures, and callers misunderstanding positive byte counts versus zero success in `copy_regset_to_user()`. The helper clamps oversize requests and frees only internally allocated buffers, which avoids freeing caller-owned storage.

## Test Signals
Signals include ptrace/regset tests across architectures, requests with zero/oversized sizes, missing getter callbacks returning `-EOPNOTSUPP`, allocation failure paths returning `-ENOMEM`, usercopy fault injection producing `-EFAULT`, and validation that returned byte counts match callback-filled data.
