# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/lam.c

## Purpose

`lam.c` tests x86 Linear Address Masking userspace behavior. It validates tagged pointers with malloc, mmap, syscalls, get_user paths, io_uring, fork/thread/exec inheritance, reported max tag bits, and optional PASID/SVA interactions with Intel DSA.

## Important APIs, Types, and Functions

It defines LAM arch prctls `ARCH_GET_UNTAG_MASK`, `ARCH_ENABLE_TAGGED_ADDR`, `ARCH_GET_MAX_TAG_BITS`, and `ARCH_FORCE_TAGGED_SVA`. Important helpers include `lam_is_available()`, `la57_enabled()`, `set_lam()`, `get_default_tag_bits()`, `get_lam()`, `set_metadata()`, `handle_lam_test()`, `handle_max_bits()`, `handle_malloc()`, `handle_mmap()`, `handle_syscall()`, `get_user_syscall()`, io_uring helpers `setup_io_uring()`, `mmap_io_uring()`, `handle_uring_sq()`, `handle_uring_cq()`, `do_uring()`, inheritance helpers `handle_execve()`, `handle_inheritance()`, `handle_thread()`, `handle_thread_enable()`, and PASID helpers `Dsa_Init_Sysfs()`, `allocate_dsa_pasid()`, `set_force_svm()`, and `handle_pasid()`.

## Control Flow

`main()` skips if CPUID or kernel prctl support says LAM is unavailable, parses `-t` to select a bitmask of test families, and returns current LAM mode when invoked with `-t 0x0` by the exec test. Each testcase is run in a forked child via `run_test()` so process LAM mode changes are isolated. The malloc, mmap, syscall, and io_uring cases enable LAM before or after allocation depending on `later`, tag pointers with bits 62:57, and expect success or SIGSEGV/error. `get_user_syscall()` uses `FIOASYNC` on a memfd to test properly tagged user pointers and malformed kernel/noncanonical pointers. Inheritance cases verify fork/thread inheritance, disallow child-thread enablement, and confirm exec disables LAM. PASID cases configure DSA sysfs and run LAM/PASID/SVA operations in several orderings.

## State and Persistence Behavior

State includes process LAM mode, mapped test pages, malloc buffers, io_uring rings, temporary memfd, cloned thread state, DSA sysfs configuration, and optional `/dev/dsa/wq0.1` mappings. No ordinary files are persisted by the test itself, but PASID setup writes to sysfs and binds devices.

## Dependencies and Integration Points

It requires x86_64, CPU LAM support, kernel `CONFIG_ADDRESS_MASKING`, arch prctl support, io_uring for that family, and optional idxd/DSA/SVA support with `intel_iommu=on,sm_on` for PASID. It integrates with kselftest plan/result APIs.

## Risks and Edge Cases

`run_test()` prints results before `ksft_set_plan()`, which is unusual for TAP consumers. Several negative tests treat any nonzero errno path as expected. `get_user_syscall()` calls `munmap(ptr, PAGE_SIZE)` after `ptr` may have been modified with tag or kernel bits, which is risky if the pointer is no longer the original mapped address. PASID tests perform real sysfs device configuration and may disturb an existing DSA setup.

## Test Signals

Pass signals are kselftest results for each selected case: tagged malloc/mmap/syscall/io_uring success under LAM, expected failures without LAM or for kernel-like pointers, correct max tag bits, fork/thread inheritance behavior, exec reset to `LAM_NONE`, and expected PASID/SVA ordering outcomes or skips when DSA/SVA is unavailable.
