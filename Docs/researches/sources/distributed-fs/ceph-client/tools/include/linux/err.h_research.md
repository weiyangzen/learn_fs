# sources/distributed-fs/ceph-client/tools/include/linux/err.h

## Purpose

This header implements kernel-style encoded error-pointer helpers for userspace tools.

## APIs, State, and Dependencies

It defines `MAX_ERRNO`, `IS_ERR_VALUE`, `ERR_PTR`, `PTR_ERR`, `IS_ERR`, `IS_ERR_OR_NULL`, `PTR_ERR_OR_ZERO`, and `ERR_CAST`. It depends on compiler and type annotations plus asm errno values. It stores no state; it interprets pointer values in the high unused address range as negative errno values.

## Risks and Test Signals

The scheme assumes architectures have an unused pointer range analogous to the kernel/user address hole. Misusing real pointers near the error range would be misclassified. Tests should cover all helper conversions for common negative errno values and null/non-null pointers.
