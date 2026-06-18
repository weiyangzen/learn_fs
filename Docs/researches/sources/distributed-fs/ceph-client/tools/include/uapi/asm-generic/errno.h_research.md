# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno.h

## Purpose
Extends base errno definitions with Linux-specific generic error numbers through `EHWPOISON`.

## Important APIs, Types, and Functions
Includes `asm-generic/errno-base.h` and defines errors such as `ENOSYS`, `EWOULDBLOCK`, socket/network errors, filesystem errors, key errors, robust mutex errors, `ERFKILL`, and aliases including `EDEADLOCK`, `EFSBADCRC`, and `EFSCORRUPTED`.

## Control Flow, State, and Persistence
No runtime logic. The comments around `ENOSYS` document syscall ABI behavior: nonexistent syscalls return `-ENOSYS`, so real syscall implementations should avoid using it for ordinary failures.

## Dependencies and Integration
Depends on the base errno header. It integrates with syscall wrappers, tools, and architecture wrappers that need Linux error-number constants independent of host libc drift.

## Risks and Test Signals
Risks include arch-specific errno values being different for some targets, alias expectations changing, and duplicate definitions with system headers. Test signals are compile tests through `uapi/asm/errno.h` on arch-specific include paths and numeric checks for common errors.
