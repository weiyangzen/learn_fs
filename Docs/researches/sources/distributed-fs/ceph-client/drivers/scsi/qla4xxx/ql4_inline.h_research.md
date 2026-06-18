<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_inline.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_inline.h

Purpose: provides small hot-path helpers for DDB lookup, legacy interrupt enable/disable, and CHAP type classification. These functions are header-inline because they are used across queueing, initialization, interrupt, and session paths.

Important APIs/types/functions: `qla4xxx_lookup_ddb_by_fw_index()` maps a firmware DDB index to the driver's `struct ddb_entry`. `__qla4xxx_enable_intrs()` and `__qla4xxx_disable_intrs()` perform unlocked MMIO updates for legacy 40xx/4022/4032 interrupt bits and update `AF_INTERRUPTS_ON`. `qla4xxx_enable_intrs()` and `qla4xxx_disable_intrs()` wrap those operations with `hardware_lock`. `qla4xxx_get_chap_type()` maps CHAP table flags to `LOCAL_CHAP` or `BIDI_CHAP`.

Control flow: DDB lookup validates the index against `MAX_DDB_ENTRIES` and rejects entries marked `INVALID_ENTRY`. Interrupt helpers choose the correct register path: 4022/4032 use the interrupt-mask register and 4010-style adapters use `ctrl_status`. The public enable/disable helpers serialize the MMIO update with IRQ-safe spin locking.

State and persistence: DDB lookup reads `ha->fw_ddb_index_map`, which is maintained by login, free, rebuild, and DDB-change paths. Interrupt helpers mutate adapter flags and hardware interrupt enable bits. CHAP type reads persistent flash-derived CHAP table flags but does not modify them.

Dependencies and integration: depends on `ql4_def.h` structures/macros, `ql4_fw.h` register masks, and qla4xxx family predicates. Used by `ql4_isr.c`, `ql4_init.c`, `ql4_iocb.c`, and mailbox/session code whenever firmware indexes or interrupt masks need fast handling.

Risks and test signals: lookup assumes invalid entries are explicitly poisoned with `INVALID_ENTRY`; stale pointers would route completions or AENs to the wrong session. The unlocked `__qla4xxx_*` variants require callers to already hold `hardware_lock`; misuse can race with ISR/register updates. Test signals include DDB removal while AENs arrive, interrupt enable/disable around reset/removal, and CHAP cache entries with local vs bidirectional flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_inline.h -->
