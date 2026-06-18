# sources/distributed-fs/ceph-client/arch/sparc/prom/misc_32.c

Purpose: provides SPARC32 miscellaneous PROM operations: reboot, Forth evaluation, entering PROM command line, halt, sync hook, IDPROM, and version queries.

Important APIs/functions: defines `prom_lock` and functions `prom_reboot()`, `prom_feval()`, `prom_cmdline()`, `prom_halt()`, `prom_setsync()`, `prom_get_idprom()`, `prom_version()`, `prom_getrev()`, and `prom_getprev()`.

Control flow: PROM entry points serialize with `prom_lock`, invoke the appropriate ROM vector operation, call `restore_current()`, and release the lock. Halt loops forever because firmware might return. IDPROM reads the root `idprom` property after checking length.

State and persistence: maintains only the global PROM spinlock. Reboot/halt/power state is delegated to firmware.

Dependencies and integration points: used by architecture restart/poweroff paths, early debug code, IDPROM consumers, and exported `prom_feval()`. Depends on ROM vector layout and PROM tree property helpers.

Risks: PROM calls can return unexpectedly or alter kernel register/current state. Locking with interrupts disabled is necessary, but misuse can deadlock if called from unsafe contexts.

Test signals: PROM command entry and resume, reboot/halt paths, Forth command execution, IDPROM reads with varying buffer sizes, and version query consistency.
