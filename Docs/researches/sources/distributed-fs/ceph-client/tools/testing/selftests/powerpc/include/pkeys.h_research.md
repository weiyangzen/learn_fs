# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/pkeys.h

## Purpose
PowerPC protection-key helper header for selftests that need pkey syscalls and AMR rights manipulation.

## Important APIs, Types, and Functions
Defines pkey rights constants, syscall numbers, bit masks, `pkey_set_rights()`, `sys_pkey_mprotect()`, `sys_pkey_alloc()`, `sys_pkey_free()`, `pkeys_unsupported()`, `siginfo_pkey()`, and `pkey_rights()`.

## Control Flow
Helpers wrap syscalls, modify AMR rights for a key, detect unsupported platforms, and decode pkey from siginfo layout.

## State and Persistence
Mutates per-thread AMR/pkey rights and memory protection state in callers; no files are persisted.

## Dependencies and Integration Points
Depends on `reg.h` AMR helpers, `utils.h`, mmap/pkey syscall ABI, and signal ABI.

## Risks and Test Signals
Risks include hard-coded syscall numbers/layout offsets and platform support variance. Pkey tests signal unsupported or mismatched fault metadata.
