# File Research: sources/block-storage/parted/libparted/debug.c

This file implements debug/assertion support when libparted is compiled with `DEBUG`.

Behavior under `DEBUG`:
- Defines a default debug handler that prints level, source file, line, function, and formatted message to `stderr`.
- `ped_debug()` formats a message into an 8192-byte heap buffer and sends it to the current debug handler.
- `ped_debug_set_handler()` installs a custom handler or restores the default handler for `NULL`.
- `ped_assert()` optionally prints a backtrace when `HAVE_BACKTRACE` is available, throws a `PED_EXCEPTION_BUG`, then aborts.

Behavior without `DEBUG`:
- The entire implementation is excluded by `#ifdef DEBUG`.

Research notes:
- The public-facing macros in headers are expected to call these functions only in debug builds.
- Assertion failure intentionally both reports through libparted’s exception system and terminates with `abort()`.
