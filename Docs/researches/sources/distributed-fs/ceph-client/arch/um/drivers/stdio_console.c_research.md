<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.c

Purpose: implements UML virtual consoles (`tty0`-`tty15`) using common channel/line infrastructure. It provides the main guest console and configurable additional consoles.

Important APIs/types/functions: `MAX_TTYS` is 16. Static objects include `opts`, `driver`, `vt_conf[]`, `def_conf`, `vts[]`, `console_ops`, and `stdiocons`. Functions include `stdio_announce()`, `con_config()`, `con_get_config()`, `con_remove()`, `con_install()`, `uml_console_write()`, `uml_console_device()`, `uml_console_setup()`, `stdio_init()`, `console_exit()`, and `console_chan_setup()`.

Control flow: boot-time `con...` setup records default or per-console channel strings, ignoring `console=` substrings intended for generic console selection. Late init registers the TTY driver, applies UMID to xterm titles, configures each console from explicit/default/compiled defaults (`CON_ZERO_CHAN` for tty0, `CON_CHAN` for others), then registers the console driver. Writes lock the line and dispatch directly to the output channel.

State and persistence: per-console runtime state is in `vts[]`; command-line config pointers persist for boot. No host data is persisted.

Dependencies and integration points: depends on TTY major/minor conventions, Linux console subsystem, channel/line framework, mconsole dynamic config, and config defaults from `drivers/Kconfig`.

Risks: main console default uses host stdin/stdout FDs, so terminal raw-mode handling and close ordering are visible to the UML process environment. Invalid compiled channel defaults can leave consoles unavailable. Console writes occur under spinlock and must remain bounded.

Test signals: boot default console, `con0=fd:0,fd:1`, `con1=xterm/pty/null/port`, mconsole config/remove/query, `/dev/tty*` open/write, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.c -->
