# sources/distributed-fs/ceph-client/arch/powerpc/kernel/udbg.c

## Purpose
Implements the generic early polling debug console abstraction used before the normal console subsystem is available and by low-level debugger paths.

## Important APIs, Types, And Functions
Global function pointers `udbg_putc`, `udbg_flush`, `udbg_getc`, and `udbg_getc_poll` define the active backend. `udbg_early_init` selects one configured backend such as LPAR, HVSI, G5, RTAS panel, BootX, 44x, CPM, USB Gecko, memory console, OPAL, or 16550. Output helpers are `udbg_puts`, `udbg_write`, `udbg_printf`, and `udbg_progress`. `register_early_udbg_console` installs the `udbg` boot console.

## Control Flow
Early boot calls `udbg_early_init`, which initializes exactly one backend selected by Kconfig, raises the console loglevel for early debug, and registers a boot console if `udbg_putc` is available. Output helpers check the function pointers, emit characters, and flush if supported. The console write callback delegates to `udbg_write`.

## State And Persistence
State is the backend function-pointer set and the registered early console pointer. Output is transient console/kmsg data. The `udbg-immortal` boot option clears `CON_BOOT` so the early console survives beyond normal boot-console teardown.

## Dependencies And Integration Points
Integrates PowerPC platform early-debug backends with Linux console registration, xmon/debugger printing, and early machine-check diagnostics. Backend implementations live in platform-specific files such as `udbg_16550.c`.

## Risks And Edge Cases
Kconfig selects a backend that may make the kernel unbootable on other hardware. `udbg_write` stops on NUL bytes even if `n` is larger, so it is a text console path rather than a binary write path. Registering too early without `udbg_putc` silently does nothing.

## Test Signals
Boot with each early-debug Kconfig on matching hardware or emulation, confirm early panic/machine-check output, verify `udbg-immortal`, and build-test all backend combinations.
