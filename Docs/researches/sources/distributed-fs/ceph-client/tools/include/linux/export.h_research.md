# sources/distributed-fs/ceph-client/tools/include/linux/export.h

## Purpose

This header stubs Linux symbol export annotations for tools code.

## APIs, State, and Dependencies

It defines `EXPORT_SYMBOL(sym)` and `EXPORT_SYMBOL_GPL(sym)` as empty macros. There is no state or dependency.

## Risks and Test Signals

The macros do not emit module export metadata. They only allow copied kernel code to compile in userspace tools. Tests are compile-only.
