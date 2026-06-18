# sources/distributed-fs/ceph-client/drivers/tty/serial/kgdboc.c

## Purpose

`kgdboc.c` implements KGDB/KDB over an existing console-capable TTY polling driver. It multiplexes debugger I/O onto a configured serial console or keyboard path and supports built-in early console debugging when `CONFIG_KGDB_SERIAL_CONSOLE` allows it.

## Important APIs, Types, and Functions

The key KGDB object is `kgdboc_io_ops`, a `struct kgdb_io` with `read_char`, `write_char`, `pre_exception`, and `post_exception`. Configuration flows through `param_set_kgdboc_var()`, `configure_kgdboc()`, `cleanup_kgdboc()`, `kgdboc_probe()`, `init_kgdboc()`, and `exit_kgdboc()`. Keyboard support uses `kgdboc_register_kbd()`, `kgdboc_unregister_kbd()`, and an input-handler reset path guarded by `CONFIG_KDB_KEYBOARD`. Built-in early console support adds `kgdboc_earlycon_io_ops`, `kgdboc_earlycon_init()`, `kgdboc_earlycon_late_init()`, and deferred boot-console exit handling.

## Control Flow

Module init registers a platform driver and creates a single platform device so probe deferral can retry until the target TTY polling driver exists. `configure_kgdboc()` parses optional `kms,`, optional `kbd`/`kdb`, then asks `tty_find_polling_driver()` for the serial driver/line. It scans registered consoles under console locking to connect KGDB to the matching console, then registers the KGDB I/O module. Runtime debugger I/O calls the TTY driver's `poll_get_char` and `poll_put_char`. Exception entry can switch consoles into debug graphics mode and pins the module; exception exit restores graphics, releases the module, and queues keyboard reset work if needed.

## State and Persistence Behavior

State is global because KGDB has a single active I/O backend: `configured`, `config`, `kgdboc_use_kms`, `kgdb_tty_driver`, `kgdb_tty_line`, and `kgdboc_pdev`. `config_mutex` serializes setup/teardown and sysfs reconfiguration. Early console state stores the selected boot console and original `exit()` callback so cleanup can undo deferred exit.

## Dependencies and Integration Points

This file integrates with KGDB/KDB core, TTY polling operations, console registration, VT/KMS debug enter/leave, input core keyboard polling, irq_work, workqueues, module parameters, early params, and platform-device probe deferral. It requires the underlying console driver to implement polling hooks for normal kgdboc serial use.

## Risks and Edge Cases

Reconfiguration is blocked while KGDB is connected. Invalid sysfs configuration clears `config`, while invalid command-line configuration can remain so probe deferral keeps retrying. Early console support deliberately keeps a boot console usable after normal console takeover, which can be unsafe for some serial drivers and therefore warns once. Keyboard reset is carefully deferred from NMI-like context; failures there can leave keyboard state odd after KDB.

## Test Signals

Test with boot parameter and module-parameter configuration, missing TTY driver probe deferral, sysfs reconfiguration after driver load, KGDB attach/detach module refcount behavior, `kms,` graphics enter/leave, keyboard polling registration/removal, and earlycon registration/deinit across boot-console handoff.
