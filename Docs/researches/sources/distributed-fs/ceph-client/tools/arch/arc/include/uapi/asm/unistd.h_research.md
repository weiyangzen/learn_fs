# sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/unistd.h

## Purpose
Defines ARC syscall UAPI wiring for tools, including generic syscall inclusion and ARC-specific syscall numbers.

## Important APIs, Types, And Functions
- Guard permits inclusion twice when `__SYSCALL` is defined.
- Defines `__ARCH_WANT_*` feature macros for selected legacy/generic syscall wrappers.
- Aliases `sys_mmap2` to `sys_mmap_pgoff`.
- Includes `asm-generic/unistd.h`, defines `NR_syscalls`, `__NR_sysfs`, and ARC-specific syscalls: `cacheflush`, `arc_settls`, `arc_gettls`, and `arc_usr_cmpxchg`.
- Emits `__SYSCALL()` entries for ARC-specific and `sysfs` calls.

## Control Flow
No runtime flow; preprocessor controls syscall table generation and tools ABI constants.

## State And Persistence
No state. Constants and macros persist in compiled tools.

## Dependencies And Integration Points
Integrates with generic unistd headers and tools syscall decoding/generation for ARC.

## Risks
Incorrect syscall numbering or feature macros would break syscall tracing/decoding and tools that issue ARC-specific syscalls.

## Test Signals
Cross-compile syscall-aware tools for ARC and compare syscall numbers with kernel UAPI.
