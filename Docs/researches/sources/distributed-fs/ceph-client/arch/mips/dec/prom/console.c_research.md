# sources/distributed-fs/ceph-client/arch/mips/dec/prom/console.c

Purpose: provides an early boot console backed by DEC PROM `prom_printf`.

Important APIs: `register_prom_console()` registers a boot console named `"prom"`. `prom_console_write()` chunks output into an 80-character buffer, null terminates it, and prints with `prom_printf("%s", buf)`.

State and integration: console registration persists until normal consoles take over. It depends on PROM vector initialization having set `__prom_printf`.

Risks and test signals: PROM output routines may be slow or unavailable after firmware teardown, so this is init-only. Early boot messages should appear before the normal console is registered.
