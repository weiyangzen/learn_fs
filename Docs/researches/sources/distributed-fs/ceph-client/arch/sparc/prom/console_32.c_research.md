# sources/distributed-fs/ceph-client/arch/sparc/prom/console_32.c

Purpose: writes early console output through SPARC32 PROM services.

Important APIs/functions: exports `prom_console_write_buf()`. Internal helper `prom_nbputchar()` serializes a single-character write through PROM V0 or V2/V3 ROM vector operations.

Control flow: `prom_console_write_buf()` loops until all characters are accepted. `prom_nbputchar()` takes `prom_lock`, dispatches to the correct PROM write method, calls `restore_current()`, releases the lock, and reports success/failure.

State and persistence: no data persistence; output is sent to PROM stdout. Uses global PROM lock state.

Dependencies and integration points: called by `prom_write()`/`prom_printf()` for early printk. Depends on `romvec`, `prom_vers`, `prom_lock`, and `restore_current()`.

Risks: unsupported PROM versions can make the caller spin forever. PROM calls require locking and current-task restoration to avoid corrupting kernel state.

Test signals: early boot console on PROM V0/V2/V3, concurrent early printk paths, and failure behavior when PROM write returns no progress.
