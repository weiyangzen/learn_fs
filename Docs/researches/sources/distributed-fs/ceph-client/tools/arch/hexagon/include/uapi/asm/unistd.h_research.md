# sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/unistd.h

## Purpose
Hexagon syscall UAPI selector for tools, including aliases and architecture-specific generic syscall wants.

## Important APIs, Types, and Functions
Defines `sys_mmap2` as `sys_mmap_pgoff`, requests renameat, stat64, set/getrlimit, execve, clone, vfork, fork, and time32 syscall support, then includes `asm-generic/unistd.h`.

## Control Flow, State, and Persistence
The file participates only in preprocessing; generic unistd expands syscall numbers or prototypes depending on `__SYSCALL` usage.

## Dependencies and Integration Points
Integrated by syscall table generation and tracing tools for Hexagon.

## Risks and Test Signals
Risk is wrong `__ARCH_WANT_*` selection changing syscall availability or table layout. Test signals include generated syscall tables, trace syscall decoding, and build coverage with `__SYSCALL` declaration/table modes.
