# sources/distributed-fs/ceph-client/tools/include/asm/export.h

## Purpose

This header stubs kernel export macros for tools builds.

## APIs, State, and Dependencies

It defines `EXPORT_SYMBOL(x)` and `EXPORT_SYMBOL_GPL(x)` as empty macros. There is no state, dependency, or control flow.

## Risks and Test Signals

The header is intentionally a build-compatibility shim; it does not create symbol metadata. Tests are compile-only coverage of copied kernel code that contains export annotations.
