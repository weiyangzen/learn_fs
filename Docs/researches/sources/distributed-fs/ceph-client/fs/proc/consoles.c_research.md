# sources/distributed-fs/ceph-client/fs/proc/consoles.c

Purpose: Implements `/proc/consoles`, listing registered kernel consoles, capabilities, flags, and device numbers.

Important APIs and types: Uses `struct console`, console flag bits (`CON_ENABLED`, `CON_CONSDEV`, `CON_BOOT`, `CON_NBCON`, `CON_PRINTBUFFER`, `CON_BRL`, `CON_ANYTIME`), `struct tty_driver`, `console_list_lock()`, `console_lock()`, and seq operations registered with `proc_create_seq()`.

Control flow: The seq iterator locks the console list in `c_start()`, walks consoles with `for_each_console()` and hlist next pointers, and unlocks in `c_stop()`. `show_console_dev()` optionally calls a console's `device()` callback under `console_lock()`, computes the device number, formats read/write/unblank capability letters, flag letters, and major:minor output.

State and persistence: It stores no private persistent state; each read traverses the current console list. Locking snapshots enough state to avoid unsafe list traversal and serialize device callback state.

Dependencies and integration points: Integrates with printk console registration, TTY drivers, procfs seq files, and device number formatting.

Risks: Console list traversal must hold the list lock for seq iteration lifetime. Device callback serialization is needed because console state such as foreground VT can change under `console_lock()`. Formatting is userspace-visible and should remain stable.

Test signals: Systems with early boot consoles, real tty consoles, net/nbcon consoles, braille consoles, console unregister/register races, and reads while switching virtual terminals.
