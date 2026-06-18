# sources/distributed-fs/ceph-client/fs/btrfs/Kconfig

## Purpose
Defines Kconfig options controlling Btrfs filesystem availability and feature gates. It exposes the main `BTRFS_FS` tristate, optional POSIX ACLs, module-load sanity tests, debug instrumentation, runtime assertions, and experimental features.

## Important APIs, Types, And Functions
This is declarative Kconfig rather than C code. The main symbols are `BTRFS_FS`, `BTRFS_FS_POSIX_ACL`, `BTRFS_FS_RUN_SANITY_TESTS`, `BTRFS_DEBUG`, `BTRFS_ASSERT`, and `BTRFS_EXPERIMENTAL`. `BTRFS_FS` selects required libraries and subsystems including cgroup bio punt support, CRC32, BLAKE2b, SHA256, zlib, LZO, Zstd, iomap, RAID6 parity, XOR blocks, and xxhash. It depends on `PAGE_SIZE_LESS_THAN_256KB`.

## Control Flow
The kernel configuration system evaluates dependencies and selects. Enabling `BTRFS_FS` allows building the filesystem built-in or as module. Enabling ACL support selects `FS_POSIX_ACL`; enabling sanity tests compiles test objects that run on module load; enabling debug or assert symbols compiles additional checking paths in other Btrfs files. `BTRFS_EXPERIMENTAL` gates unstable features listed in the help text rather than implementing them locally.

## State And Persistence
The file produces build-time configuration state. It does not run at runtime, but selected symbols determine which object files are built and which runtime features or checks are available. User-visible persistence is indirect through the generated kernel `.config` and built module/kernel image.

## Dependencies And Integration Points
The options feed `fs/btrfs/Makefile` object selection and many `#ifdef CONFIG_BTRFS_*` blocks across Btrfs. The selected compression, checksum, RAID, and iomap dependencies correspond to core filesystem capabilities. `BTRFS_FS_POSIX_ACL` directly controls whether `acl.o` is compiled and whether `acl.h` exports real ACL methods or stubs.

## Risks
Incorrect dependencies can allow invalid builds or silently omit required libraries. Debug, assertion, sanity-test, and experimental options trade coverage for runtime cost and stability. The page-size dependency is critical for supported metadata block constraints; relaxing it without matching code changes could mount unsupported configurations.

## Test Signals
Build tests should cover built-in, module, and disabled Btrfs; ACL enabled/disabled; debug/assert builds; sanity-test module-load execution; and experimental-feature build combinations. Kconfig dependency checks should verify that all selected libraries and page-size constraints appear in generated configs.
