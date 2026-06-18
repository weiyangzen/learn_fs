# sources/distributed-fs/ceph-client/tools/include/nolibc/stdarg.h

## Purpose
Provides varargs primitives for nolibc.

## APIs, Types, and Functions
Typedefs `va_list` to `__builtin_va_list` and maps `va_start`, `va_end`, `va_arg`, and `va_copy` to compiler builtins.

## Control Flow, State, and Persistence
There is no runtime state beyond caller-owned varargs traversal objects. Control flow follows compiler ABI lowering for variadic functions.

## Dependencies and Integration
Depends on compiler builtins. It integrates with `stdio` formatting/scanning, `err` diagnostics, and `open`/`openat` mode varargs.

## Risks and Test Signals
Risks are compiler ABI assumptions and misuse after `va_end` or without `va_copy`. Test signals are printf/asprintf/open varargs tests across architectures.
