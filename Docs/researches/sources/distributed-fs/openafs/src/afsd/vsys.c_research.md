# sources/distributed-fs/openafs/src/afsd/vsys.c

## Purpose

`vsys.c` is a diagnostic command for invoking an AFS syscall directly with user-supplied parameters.

## Important APIs and Functions

`main()` parses numeric arguments with `atoi()`, treats an argument after `-s` as a string pointer cast through `intptr_t`, stores up to six parameters in `parms`, calls `syscall(AFS_SYSCALL, ...)` when available, and prints the returned code.

## Control Flow

The program requires at least one argument, rejects unknown switches, fills the syscall parameter array, calls the syscall or returns `-1` when `AFS_SYSCALL` is not defined, prints `code <value>`, and exits.

## State and Persistence Behavior

There is no local persistence. Any durable state change depends entirely on the syscall number and parameters passed by the caller.

## Dependencies and Integration Points

It depends on OpenAFS syscall headers, libc `syscall()`, and the generated component version file. It integrates directly with the kernel AFS syscall ABI.

## Risks and Test Signals

The six-element parameter array is not bounds-checked, invalid numeric input silently becomes zero, string-pointer syscalls are unsafe without ABI knowledge, and the process returns success even for syscall errors. Test usage, switch handling, numeric/string placement, builds without `AFS_SYSCALL`, and too-many-argument hardening.
