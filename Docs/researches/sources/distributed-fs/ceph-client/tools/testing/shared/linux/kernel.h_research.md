<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/kernel.h

## Purpose

`linux/kernel.h` supplies a userspace-compatible wrapper around core kernel helper macros for shared data-structure tests.

## Important APIs, Types, and Functions

It includes the tools kernel header, libc string/stdio/limits headers, compiler, error, bitops, log2, and kconfig headers. It maps `printk`, `pr_err`, `pr_info`, `pr_debug`, and `pr_cont` to `printf`, defines `schedule()` as a no-op, sets `PAGE_SHIFT` to 12, and stubs `EXPORT_PER_CPU_SYMBOL_GPL`.

## Control Flow and State

No runtime state exists beyond print macro expansion. Scheduling and export behavior are intentionally inert in userspace.

## Dependencies and Integration Points

It is a central dependency for imported kernel libraries compiled by `shared.mk`. It bridges kernel logging and helper expectations to libc.

## Risks and Test Signals

Risks include hiding scheduling assumptions, mismatched page size assumptions, or print macro side effects. Sanitized test builds and data-structure tests validate practical compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kernel.h -->
