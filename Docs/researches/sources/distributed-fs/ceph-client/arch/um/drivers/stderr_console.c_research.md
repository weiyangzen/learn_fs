<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stderr_console.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/stderr_console.c

Purpose: provides an early, optional console that writes printk output directly to host stderr.

Important APIs/types/functions: static `use_stderr_console` is set by `stderr=`. `stderr_console_write()` writes to FD 2 through `generic_write()`. `stderr_console_init()` registers the console during console init, and `unregister_stderr()` unregisters it later.

Control flow: if boot option `stderr=<nonzero>` is present, console init registers a `stderr` console with `CON_PRINTBUFFER`. A later initcall always unregisters it so the real UML console can become `/dev/console`.

State and persistence: only a boot-time boolean is stored. Output goes to host stderr and is not persisted by the driver.

Dependencies and integration points: depends on Linux console initcalls, UML channel generic write helper, and `__setup`.

Risks: registering too early can make stderr the default console; the late unregister is intentional to avoid `/dev/console` open failures. Unregister is called even when not registered and should remain harmless.

Test signals: boot with and without `stderr=1`, inspect early printk destination, ensure `/dev/console` opens after normal console registration, and verify unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stderr_console.c -->
