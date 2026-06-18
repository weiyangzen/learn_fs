# sources/distributed-fs/ceph-client/include/uapi/linux/memfd.h

## Purpose
Defines `memfd_create(2)` flags for anonymous file creation, sealing, executable policy, hugetlb backing, and hugepage size encodings.

## Important APIs, Types, And Functions
Exports `MFD_CLOEXEC`, `MFD_ALLOW_SEALING`, `MFD_HUGETLB`, `MFD_NOEXEC_SEAL`, `MFD_EXEC`, `MFD_HUGE_SHIFT`, `MFD_HUGE_MASK`, and all known `MFD_HUGE_*` size constants from `asm-generic/hugetlb_encode.h`.

## Control Flow
Userspace passes flags to `memfd_create`; the kernel creates a file descriptor with close-on-exec, sealing permission, executable restrictions, or hugetlb allocation as requested. Hugepage size bits are meaningful only with `MFD_HUGETLB`.

## State, Persistence, And Dependencies
Resulting state lives in the returned anonymous file descriptor and its seals/mapping behavior. Dependencies are hugetlb encoding macros.

## Integration Points
Used by sandboxing, shared-memory IPC, JITs, loaders, and tests that need anonymous sealed files or explicit executable policy.

## Risks
Executable flags are policy-sensitive, sealing must be requested up front, and hugepage sizes are platform dependent. Passing unsupported hugepage encodings or conflicting exec flags should be validated by syscall tests.

## Test Signals
Test close-on-exec, adding seals only after `MFD_ALLOW_SEALING`, `MFD_NOEXEC_SEAL` behavior, `MFD_EXEC` behavior, hugetlb creation, and failure on unsupported hugepage sizes.
