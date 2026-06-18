<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/usercopy.c -->
# sources/distributed-fs/ceph-client/lib/usercopy.c

## Purpose
Out-of-line usercopy wrappers and a userspace zero-check helper for generic uaccess infrastructure.

## APIs, Types, and Functions
Conditionally exports `_copy_from_user()` and `_copy_to_user()` when inline variants are not used, forwarding to `_inline_copy_from_user()` and `_inline_copy_to_user()`. Exports `check_zeroed_user(const void __user *from, size_t size)`.

## Control Flow, State, and Persistence
`check_zeroed_user()` treats zero size as zeroed, aligns the starting user pointer down to an `unsigned long` boundary, expands size by the alignment offset, and starts a user read access window. It reads word-sized chunks with `unsafe_get_user()`, masks leading bytes before the original pointer and trailing bytes after the requested size, exits early if a nonzero word appears, and closes user access before returning 1 for all zero, 0 for nonzero, or `-EFAULT` on access failure. No state is retained.

## Dependencies and Integration
Depends on uaccess primitives, nospec/instrumentation headers, wordpart byte masks, fault-injection usercopy headers, and symbol exports. It is used by syscall helpers such as `copy_struct_from_user()` and validated by `usercopy_kunit.c`.

## Risks and Test Signals
Risks include subtle alignment and tail-mask mistakes, user fault cleanup paths, architecture-specific user access window semantics, and pointer arithmetic on `__user` addresses. Test signals include zero-size return, unaligned starts, sizes shorter than a word, page-boundary reads, injected faults, and comparison against `memchr_inv()` on copied user data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/usercopy.c -->
