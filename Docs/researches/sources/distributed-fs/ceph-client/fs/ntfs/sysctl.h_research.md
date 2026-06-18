# sources/distributed-fs/ceph-client/fs/ntfs/sysctl.h

## Purpose
Declares the NTFS debug sysctl entry point while hiding compile-time feature differences from the rest of the driver.

## Important APIs, Types, And Functions
When both `DEBUG` and `CONFIG_SYSCTL` are enabled, it declares `int ntfs_sysctl(int add);`. Otherwise it defines an inline `ntfs_sysctl()` stub that always returns success.

## Control Flow
Callers in module init/exit can invoke `ntfs_sysctl(1)` and `ntfs_sysctl(0)` unconditionally. The preprocessor selects either the real registration path in `sysctl.c` or a no-op path.

## State And Persistence
This header has no persistent state. Its only state impact is compile-time: debug sysctl availability is either active or erased.

## Dependencies And Integration Points
Integrated by `super.c` for lifecycle management and by `sysctl.c` for the real implementation. It depends on the same `DEBUG && CONFIG_SYSCTL` contract as the source file.

## Risks And Edge Cases
The stub makes non-debug builds ignore sysctl setup failures by design. Any code expecting a visible proc entry in non-debug builds would be incorrect.

## Test Signals
Compile matrix tests should verify both branches: real declaration resolves with `sysctl.c`, while non-debug builds link without sysctl/procfs dependencies.
