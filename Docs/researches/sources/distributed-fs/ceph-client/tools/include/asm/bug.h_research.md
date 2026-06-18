# sources/distributed-fs/ceph-client/tools/include/asm/bug.h

## Purpose

This header provides tools-friendly warning macros modeled after kernel `WARN*` helpers.

## APIs, State, and Dependencies

It defines `__WARN_printf` to print to `stderr`, plus `WARN`, `WARN_ON`, `WARN_ON_ONCE`, and `WARN_ONCE`. The once variants use a function-local static `__warned` flag for persistence. It depends on compiler `unlikely` and `<stdio.h>`.

## Risks and Test Signals

Warnings are side effects to standard error, not kernel logs, and once-state is per macro expansion. Tests should compile warning users and verify return values reflect whether the condition was true, including once behavior.
