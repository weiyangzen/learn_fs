# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_avb.c

Purpose: provides AVB/PTP/TAI register-window access operations through Global2 AVB command/data registers for several mv88e6xxx generations.

Important APIs/types/functions: private helpers `mv88e6xxx_g2_avb_read()` and `mv88e6xxx_g2_avb_write()` implement the busy-bit transaction. Exported ops tables are `mv88e6352_avb_ops`, `mv88e6165_avb_ops`, and `mv88e6390_avb_ops`, each supplying port PTP, global PTP, and TAI read/write callbacks.

Control flow: reads wait for idle, reject snapshots longer than four words, issue either single-read or incrementing-read command, wait again, then read data repeatedly. Writes wait for idle, write one data word, issue write command, and wait for completion. Family wrappers construct command words with generation-specific opcodes and special global port numbers.

State and persistence: accessed registers configure PTP/AVB/TAI hardware and may contain latched timestamp data. The file itself stores no runtime state.

Dependencies/integration: consumed by `hwtstamp.c` and PTP code through `chip->info->ops->avb_ops`; relies on Global2 register definitions and outer register-locking by callers.

Risks: hardware supports only four-word snapshots; callers must split larger reads. Similar-looking 6352 and 6390 command encodings use different op fields and global port numbers. No local locking is done.

Test signals: PTP setup should read/write global and per-port registers, RX/TX timestamp reads should fetch four-word blocks, 6165 TAI special port selection should work, and oversized reads should return `-E2BIG`.
