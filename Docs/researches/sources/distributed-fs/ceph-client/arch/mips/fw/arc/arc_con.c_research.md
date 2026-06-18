<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/arc_con.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/arc_con.c

**Purpose:** Registers an early ARC firmware-backed Linux console named `arc`. It lets boot messages reach firmware console output before normal tty/serial drivers are available.

**Important APIs/types/functions:** `prom_console_write()` emits characters through `prom_putchar()`, translating `\n` into CRLF. `prom_console_setup()` gates activation on `PROM_FLAG_USE_AS_CONSOLE`. `arc_cons` is the `struct console`, and `arc_console_init()` registers it with `console_initcall`.

**Control flow:** Console init always calls `register_console()`. The console core invokes setup, which returns `-ENODEV` unless platform identification set the relevant PROM flag. Writes are synchronous character loops into ARC firmware.

**State, dependencies, integration:** Reads global `prom_flags` from ARC identification and calls `prom_putchar()` from promlib. It integrates with Linux console registration and ARC firmware I/O.

**Risks and test signals:** Firmware calls are slow and unsafe after PROM memory is freed, so this is early-console only. Test by booting an ARC machine with and without `PROM_FLAG_USE_AS_CONSOLE`, checking CRLF output and no duplicate console when normal drivers register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/arc_con.c -->
