<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.c

Purpose: Provides low-level KB3310B embedded-controller access for YeeLoong/related Lemote 2F machines.

Important APIs/types/functions: `ec_read()`, `ec_write()`, `ec_query_seq()`, `ec_query_event_num()`, and `ec_get_event_num()` are exported. Two spinlocks serialize indexed register access and command/status port access.

Control flow: Indexed reads/writes output high and low address bytes then read/write data port. Command queries write to `EC_CMD_PORT`, poll status bit 1 until the EC accepts the command, then event retrieval waits for status bit 0 and reads `EC_DAT_PORT`.

State and persistence: EC state is external hardware state. Kernel state is limited to spinlocks.

Dependencies and integration: Used by Lemote PM/reset/laptop code and constants from `ec_kb3310b.h`.

Risks: Polling timeouts return `-EINVAL`; excessive printk on command success can be noisy. Port access assumes x86-style IO ports exist and are reserved.

Test signals: EC register reads should return battery/lid/fan values; SCI event queries should time out cleanly when EC is unresponsive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.c -->
