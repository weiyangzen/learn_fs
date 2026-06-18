# sources/distributed-fs/ceph-client/arch/sparc/prom/console_64.c

Purpose: writes SPARC64 early console output through IEEE-1275 `write`.

Important APIs/functions: exports `prom_console_write_buf()`. Internal `__prom_console_write_buf()` builds a P1275 argument array for service `"write"` with `prom_stdout`, buffer, and length.

Control flow: the public writer repeatedly calls the direct PROM write until the requested length is consumed. The helper invokes `p1275_cmd_direct()` and treats negative firmware return as no progress.

State and persistence: no owned state; sends bytes to PROM stdout.

Dependencies and integration points: used by PROM printf/early console; depends on `prom_stdout` initialized by `prom_init()` and P1275 CIF support.

Risks: the loop must handle partial writes. The current code advances `buf` by the remaining length after subtracting `n`, which is a subtle area to test for multi-chunk writes. Firmware errors can spin.

Test signals: early boot output with short and long buffers, partial-write PROM behavior, and newline conversion through `prom_write()`.
