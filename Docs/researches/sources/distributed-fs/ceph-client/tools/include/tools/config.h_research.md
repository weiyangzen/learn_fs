# sources/distributed-fs/ceph-client/tools/include/tools/config.h

## Purpose
Supplies a small tools-side subset of kernel Kconfig expression helpers so C and preprocessor code can test boolean/tristate-style `CONFIG_*` defines safely.

## Important APIs, Types, and Functions
Exports `IS_BUILTIN(option)` via the internal placeholder chain `__is_defined()`, `___is_defined()`, `____is_defined()`, `__ARG_PLACEHOLDER_1`, and `__take_second_arg()`.

## Control Flow, State, and Persistence
There is no runtime behavior. Macro expansion turns a symbol defined as `1` into `1` and an undefined or nonmatching token into `0`, enabling use in `#if` and C expressions.

## Dependencies and Integration
No external includes. It integrates with perf and other Linux tools that compile outside the kernel build but still consume generated or manually supplied `CONFIG_*` symbols.

## Risks and Test Signals
Risks include assuming support for module `m` values beyond the limited helper, passing expressions rather than simple config tokens, or redefining placeholder macros. Test signals are preprocessor tests for defined `CONFIG_FOO 1`, undefined symbols, and use in both `#if` and ordinary C expressions.
