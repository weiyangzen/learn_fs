# sources/distributed-fs/orangefs/src/common/events/debug.h

Purpose: Tiny debug-print macro layer for the TAU event tracing code.

Important APIs/macros: Defines `PFX` as `TAU_NAME`. With `TAU_DEBUG`, `dbg()` and `info()` print prefixed messages; otherwise they compile to empty `do {} while (0)` blocks. `err()` and `warn()` always print prefixed error/warning messages.

Control flow/state: No state; compile-time macro selection controls emission.

Dependencies/integration: Requires including code to define `TAU_NAME` and include/declare `printf()`. Used by `pvfs_tau_api.c`.

Risks: Macro uses GNU variadic syntax `arg...`, which is not strict ISO C/C++. Always-on `err()`/`warn()` write to stdout via `printf()`, not stderr or OrangeFS gossip logging.

Test signals: Compile TAU event code with and without `TAU_DEBUG`, and verify format strings compile in C++ mode.
