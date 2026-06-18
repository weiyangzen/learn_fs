# File Research: sources/block-storage/lvm2/lib/misc/lvm-signal.c

This file manages SIGINT/SIGTERM handling and full signal blocking around critical sections.

Main APIs:
- `sigint_allow()`: installs temporary handlers for SIGINT/SIGTERM, clears `SA_RESTART`, and unmasks those signals.
- `sigint_restore()`: restores saved masks/handlers.
- `sigint_caught()`, `sigint_clear()`.
- `sigint_usleep()`: interruptible sleep with temporary signal handling.
- `block_signals()`, `unblock_signals()`.

Implementation details:
- Supports up to three nested allow/restore levels.
- `_catch_sigint()` only sets a `volatile sig_atomic_t` flag.
- Signal changes are skipped when `memlock_count_daemon()` is active.

Dependencies:
- `memlock.h`, POSIX signal APIs.

Correctness notes:
- Interrupt flags are not cleared automatically; command runner is expected to call `sigint_clear()`.
- Blocking uses `sigfillset()` and saves old mask.

Risks:
- Nesting beyond `MAX_SIGINTS` silently stops saving new handler state.
- `sigint_caught()` logs “Interrupted...” every time the flag is observed.
