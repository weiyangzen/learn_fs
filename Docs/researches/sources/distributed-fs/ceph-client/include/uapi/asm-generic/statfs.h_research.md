# sources/distributed-fs/ceph-client/include/uapi/asm-generic/statfs.h

## Purpose
Defines generic filesystem statistics structures returned by `statfs` and `fstatfs`.

## Important APIs, Types, And Functions
Exports `__statfs_word`, `struct statfs`, `struct statfs64`, `struct compat_statfs64`, and optional packing macros `ARCH_PACK_STATFS64` and `ARCH_PACK_COMPAT_STATFS64`.

## Control Flow
Compile-time selection chooses `__kernel_long_t` on 64-bit and `__u32` on 32-bit unless an architecture overrides `__statfs_word`. Packing attributes may be supplied by architectures.

## State, Persistence, And Dependencies
No internal state. The structs are snapshots of filesystem capacity, free blocks, free inodes, filesystem id, name length, fragment size, and mount flags. It depends on `<linux/types.h>`.

## Integration Points
Used by `statfs`, `fstatfs`, compat syscall handlers, libc filesystem APIs, and filesystem clients such as Ceph that report cluster-backed capacity through VFS.

## Risks
Signedness and size vary by word type. Padding differs on ARM, IA64, x86_64 compat, S390x, and MIPS cases. Overflows are possible when 32-bit `statfs` reports large distributed filesystems.

## Test Signals
Size/offset ABI tests per architecture, `statfs64` large-capacity tests, compat syscall tests, mount flag reporting tests, and filesystem-specific capacity/inode accounting comparisons.
