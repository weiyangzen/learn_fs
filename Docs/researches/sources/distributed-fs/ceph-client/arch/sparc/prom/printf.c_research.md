# sources/distributed-fs/ceph-client/arch/sparc/prom/printf.c

Purpose: implements PROM-backed early formatted output for SPARC.

Important APIs/functions: exposes `prom_write()` and `prom_printf()`. Uses static buffers `ppbuf` and `console_write_buf`, protected by `console_write_lock`.

Control flow: `prom_printf()` formats into `ppbuf` with `vscnprintf()` and calls `prom_write()`. `prom_write()` serializes output, inserts carriage returns before newlines, batches up to 1024 bytes, and writes chunks through `prom_console_write_buf()`.

State and persistence: only static formatting/output buffers and a raw spinlock. Output is transient console I/O.

Dependencies and integration points: used by early boot, fatal PROM halt paths, and low-level diagnostics before normal console availability. Depends on bitness-specific PROM console writers.

Risks: fixed global buffers require serialization. Calling in tracing-sensitive contexts uses `notrace`. PROM output can be slow or blocking, so it should remain early/debug-only.

Test signals: early printk with `\n` conversion, long messages over buffer boundary, concurrent early messages, and use before normal console registration.
