<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/panic.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/panic.h

## Purpose
`panic.h` provides a user-space implementation of kernel `panic()` semantics for fatal tools errors.

## APIs And Flow
It defines inline `panic(const char *fmt, ...)`, which formats the message to `stderr` with `vfprintf()` and exits the process with status `-1`.

## State, Dependencies, Risks, Tests
State is limited to process termination and stderr output. Dependencies are `<stdarg.h>`, `<stdio.h>`, and `<stdlib.h>`. Integration points are imported kernel code that expects `panic()` to be noreturn-like. Risks are cleanup bypass, exit status truncation by shells, and no automatic newline or stack dump. Tests should execute a small child process that calls `panic()` and assert output and nonzero termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/panic.h -->
