# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/beauty.h

## Purpose
This is the central header for perf trace syscall argument beautifiers. It defines string-table containers, syscall argument context, augmented-argument metadata, and the function/macro names used by syscall format tables.

## Important APIs, Types, And Functions
Core types are `struct strarray`, `struct strarrays`, `struct augmented_arg`, `struct syscall_arg`, and lightweight `struct file`. Key macros are `DEFINE_STRARRAY`, `DEFINE_STRARRAY_OFFSET`, `DEFINE_STRARRAYS`, and many `SCA_*` / `STUL_*` aliases. Declared formatters cover file descriptors, integers, pointers, clone flags, fcntl, flock, mount/open/rename/socket/futex-related flags, x86 MSRs/IRQ vectors/arch_prctl, prctl args, timespecs, and more.

## Control Flow
No runtime control flow is implemented here, but the header defines the dispatch contract: each syscall argument formatter receives a buffer, size, and `struct syscall_arg`; it may inspect `arg->val`, other syscall arguments via `syscall_arg__val()`, augmented payloads, thread/trace context, and may set masks or return-value formatters.

## State, Dependencies, And Integration
The state model is explicit in `struct syscall_arg`: raw argument value, complete argument blob, formatting metadata, optional augmented eBPF payload, thread/trace context, private formatter parameter, dynamic-array length, argument index, mask, and prefix display policy. This header is included by individual beauty C files and by `builtin-trace.c` syscall tables.

## Risks And Test Signals
Because this is a shared ABI inside perf, field changes can break many formatters. Risks include inconsistent prefix handling, incorrect argument masks, and augmented payload size misuse. Tests should exercise representative syscall formatters and parsing helpers through `perf trace` output.
