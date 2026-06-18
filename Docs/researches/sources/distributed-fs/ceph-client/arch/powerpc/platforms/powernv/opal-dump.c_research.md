
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-dump.c

Purpose: exposes OPAL platform dumps through `/sys/firmware/opal/dump`, including dump initiation, retrieval, and acknowledgement.

Important APIs/types/functions: `struct dump_obj` backs each dump kobject and binary `dump` file. `dump_read_info()` queries dump ID/size/type, preferring `opal_dump_info2()`. `dump_read_data()` allocates a vmalloc buffer, builds an OPAL scatter-gather list, and calls `opal_dump_read()`. `process_dump()` is the threaded IRQ handler. `opal_platform_dump_init()` creates sysfs and requests the OPAL dump event IRQ.

Control flow: init checks firmware token `OPAL_DUMP_READ`, creates the `dump` kset, adds an `initiate_dump` attribute, requests `OPAL_EVENT_DUMP_AVAIL`, and asks firmware to resend pending notifications when supported. On event, the handler reads dump metadata, deduplicates by name, and creates a kobject named by type and ID. Userspace reads the binary dump file; data is fetched lazily on first read and retained until acknowledge. Writing acknowledge removes the attribute, sends `opal_dump_ack()`, and drops the kobject.

State and persistence: each dump object holds ID/type/size and an in-memory buffer until acknowledged. The firmware dump remains pending until ack. Kernel state is sysfs/kobject based.

Dependencies and integration points: depends on OPAL dump calls, OPAL event IRQ mapping, ksets/sysfs binary attributes, vmalloc SG helpers, and userspace dump daemons.

Risks: sysfs object lifetime is explicitly guarded by extra kobject references to avoid read/acknowledge vs uevent races. Partial dump reads return `-EIO` and rely on userspace retry. Large dumps allocate vmalloc memory and retain it.

Test signals: firmware dump notification, duplicate event deduplication, binary read, partial-read retry, acknowledge removal and firmware ack, initiate FSP dump, and uevent ordering under fast userspace consumers.
