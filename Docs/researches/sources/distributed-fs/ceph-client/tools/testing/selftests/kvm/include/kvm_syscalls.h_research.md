# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_syscalls.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_syscalls.h

Purpose: syscall wrapper macros for KVM selftests. It standardizes direct syscall invocation, assertion behavior, and mmap/dup helpers without repeating boilerplate.

Important APIs/types/functions: `MAP_ARGS*`, `DECLARE_ARGS`, `UNPACK_ARGS`, `__KVM_SYSCALL_ERROR`, `__KVM_SYSCALL_DEFINE`, `KVM_SYSCALL_DEFINE`, `__kvm_mmap`, `kvm_mmap`, and `kvm_dup`.

Control flow and state: generated wrappers call the raw syscall, either returning the result for negative testing or asserting that failure did not occur. `kvm_mmap` maps anonymous/file memory and asserts the result is not `MAP_FAILED`; `kvm_dup` asserts `dup` succeeded.

Dependencies and integration: depends on `<sys/syscall.h>` and `test_util.h` assertion macros through inclusion chains. It is used by `kvm_util.h` and lower-level helpers that need consistent error text.

Risks: variadic macro machinery is limited to the supported argument count and can be hard to debug when misused. Assertion wrappers are inappropriate for tests that intentionally provoke syscall failures; those need the underscore/raw variants.

Test signals: broad selftest compilation validates macro expansion. Runtime failures are surfaced as standardized `TEST_ASSERT` messages with syscall name and errno.
