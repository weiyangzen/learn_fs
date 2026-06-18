# sources/distributed-fs/ceph-client/mm/rodata_test.c

## Purpose
`rodata_test.c` is a small functional test for kernel read-only data protection. It verifies that a `static const` variable in `.rodata` can be read, cannot be modified through a nofault kernel write helper, remains unchanged after the attempted write, and that the `.rodata` section boundaries are page-aligned.

## Important APIs, Types, and Functions
The file defines `TEST_VALUE`, a `static const int rodata_test_data`, and one function, `rodata_test()`. It uses `READ_ONCE()` to verify the value, `copy_to_kernel_nofault()` to attempt a write that should fault/fail cleanly, `PAGE_ALIGNED()` to check `__start_rodata` and `__end_rodata`, and `pr_err()`/`pr_info()` for result reporting.

## Control Flow
`rodata_test()` runs four checks in sequence. First it verifies the initial constant value. Second it attempts to write zero into the const object and treats a successful copy as failure because `.rodata` should be read-only. Third it reads the object again to ensure it was not changed. Fourth it checks start and end rodata section alignment. The function returns early on any failure and logs success only after all checks pass.

## State and Persistence Behavior
The intended behavior is no state mutation. The attempted write is expected to fail without changing `rodata_test_data`. The only persistent effect is kernel log output. A failed protection setup could corrupt the test variable, and the first and third checks are designed to catch that corruption.

## Dependencies and Integration Points
The file depends on rodata test declarations, uaccess nofault copying, MM page alignment macros, and architecture section symbols from `asm/sections.h`. It integrates with architecture or core init code that calls `rodata_test()` after read-only permissions are applied to kernel text/rodata mappings.

## Risks and Edge Cases
The test is meaningful only after page permissions for rodata have been finalized. If called too early, it can falsely report writable rodata. `copy_to_kernel_nofault()` must fail safely without panicking on a protected kernel address. Section boundary checks assume the architecture exposes accurate `__start_rodata` and `__end_rodata` symbols and requires page-aligned rodata protection.

## Test Signals
The expected signal is one `all tests were successful` log line during boot/test execution. Failure logs identify initial data corruption, writable rodata, post-write corruption, or unaligned rodata boundaries. Architecture bring-up and debug kernels should run this alongside W+X and strict kernel RWX tests.
