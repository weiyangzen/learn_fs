# sources/compression/xz/src/xz/signals.h

Purpose: public internal header for the `xz` command signal-abort subsystem.

Important APIs and types: declares the volatile `sig_atomic_t user_abort` flag, `signals_init()`, optional `signals_block()`/`signals_unblock()`, and optional `signals_exit()`. On native Windows and VMS, block/unblock are compiled as no-op macros. On native Windows, `signals_exit()` is also a no-op macro because `signals.c` cannot preserve and re-raise a POSIX-style signal number.

Control flow and integration: consumers initialize handlers early with `signals_init()`, poll `user_abort` from long-running compression/decompression loops, use block/unblock around critical regions that should not be interrupted by handled signals, and call `signals_exit()` after cleanup to preserve signal termination semantics on POSIX.

State and persistence: no state is defined here besides the external `user_abort` declaration. The header controls platform-specific API availability through preprocessor macros.

Dependencies: requires signal-related types to be visible through the command's shared private headers before inclusion. It is part of the internal `src/xz` API, not liblzma's public API.

Risks: platform no-op macros mean callers must not rely on block/unblock for correctness on Windows or VMS. Callers must treat `user_abort` as a poll-only signal flag and avoid using it as a substitute for immediate cleanup in unsafe contexts.

Test signals: validation is mostly compile- and integration-level. Useful checks are platform builds that verify declarations/macros match `signals.c`, plus command tests that abort during reads, writes, and output-file cleanup.
