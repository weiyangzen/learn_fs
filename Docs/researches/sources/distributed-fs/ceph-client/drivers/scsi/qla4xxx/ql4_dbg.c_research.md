# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.c

Purpose: debug dump helpers for qla4xxx buffers, legacy registers, mailbox registers, page-selected registers, and 8xxx PEG halt state.

Important APIs/functions: `qla4xxx_dump_buffer()`, `qla4xxx_dump_registers()`, and `qla4_8xxx_dump_peg_reg()`.

Control flow: buffer dump prints hex bytes in 16-byte rows. Register dump branches by adapter family: 8022 mailbox registers, 4010 register pages, or 4022/4032 register pages with page selection via `ctrl_status`. PEG dump reads halt-status registers and, for 8022, PEG network program counters.

State and persistence: no persistent state, but register dump briefly writes page-select values for 4022/4032 debug output. Output goes to kernel log.

Dependencies and integration: depends on `ql4_def.h`, chip predicates, register structures, `readw/readl/writel`, qla8xxx direct register reads, and debug macros.

Risks: register dumping during unstable hardware/reset can fault or produce stale values; page selection side effects should not race with normal access; high-volume printk output can flood logs. Test signals include dump output on each supported family, reset-time PEG dump, and ensuring debug paths are gated by logging settings.
