# sources/distributed-fs/openafs/src/afsd/afsd.h

## Purpose

`afsd.h` defines the shared contract between common afsd startup logic and platform/runtime backends.

## Important APIs and Types

It exposes `afsd_init()`, `afsd_parse()`, `afsd_run()`, debug globals, `afsd_cacheMountDir`, `afsd_callback_func`, portable `afsd_syscall_param_t`, `CAST_SYSCALL_PARAM()`, and `struct afsd_syscall_args`. Backend-required functions are `afsd_mount_afs()`, `afsd_check_mount()`, `afsd_set_rx_rtpri()`, `afsd_set_afsd_rtpri()`, `afsd_call_syscall()`, `afsd_fork()`, and `afsd_daemon()`.

## Control Flow

`afsd.c` builds command/cache/kernel initialization state, packages syscalls into `struct afsd_syscall_args`, and calls backend functions declared here. Native builds satisfy the contract in `afsd_kernel.c`; FUSE/libuafs code includes the same header for common parsing semantics.

## State and Persistence Behavior

The header owns no runtime persistence. Its ABI definitions determine how pointer and integer syscall parameters are represented before backend code hands them to the kernel or runtime.

## Dependencies and Integration Points

The file is coupled to platform pointer widths, Darwin user address rules, and all AFSOP call sites in `afsd.c`. Any alternative backend must implement the full function set with matching semantics.

## Risks and Test Signals

ABI drift is the key risk: wrong `afsd_syscall_param_t` width or casts can truncate pointers. Compile matrix tests and mocked syscall-population tests should cover pointer-heavy and integer-heavy opcodes.
