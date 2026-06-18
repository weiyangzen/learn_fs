<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/usercopy_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/usercopy_kunit.c

## Purpose
KUnit tests for user access helpers: valid and invalid `copy_to_user()`/`copy_from_user()`, scalar `get_user()`/`put_user()`, `check_zeroed_user()`, and `copy_struct_from_user()` ABI-extension semantics.

## APIs, Types, and Functions
Uses `copy_to_user()`, `copy_from_user()`, `get_user()`, `put_user()`, `clear_user()`, `check_zeroed_user()`, `copy_struct_from_user()`, `kunit_vm_mmap()`, and `memchr_inv()`. `struct usercopy_test_priv` holds kernel memory, user memory, and buffer size. `TEST_U64` conditionally enables 64-bit scalar access tests on capable 32-bit architectures and all 64-bit architectures.

## Control Flow, State, and Persistence
`usercopy_test_init()` skips non-MMU systems, allocates two pages of kernel memory, maps two pages of user memory below `TASK_SIZE`, and stores both in `test->priv`. Valid tests copy a page both ways and exercise scalar get/put. Invalid tests skip alternate address-space or non-MMU systems, then confirm kernel addresses cast to `__user` are rejected and destination zeroing/preservation occurs. `check_zeroed_user()` is compared to `memchr_inv()` over every subrange of a 1024-byte page-boundary-spanning pattern. `copy_struct_from_user()` checks equal-size, old-userspace shorter input with zero-fill, too-large nonzero tail rejection, and too-large zero tail success.

## Dependencies and Integration
Depends on KUnit, MMU support, `uaccess`, mmap helpers, scheduler/task address limits, and architecture user access enforcement. It registers as `usercopy`.

## Risks and Test Signals
Risks include architecture-specific user address models, disabled explosive reversed-copy coverage, runtime cost of O(n^2) subrange zero checks, and user memory permissions using `PROT_EXEC` though execute is not central. Test signals include page-boundary scanning, valid scalar sizes, invalid kernel/user confusion rejection, copy-tail zeroing, and struct ABI compatibility behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/usercopy_kunit.c -->
