# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_tmf.c

Purpose: this file implements aic94xx task-management and nexus cleanup operations used by libsas error handling: abort task, abort/clear task set, LU reset, I_T nexus reset, query task, adapter/port clear nexus, and lower-level sequencer clear-nexus commands.

Important APIs/types/functions: exported functions are `asd_clear_nexus_ha()`, `asd_clear_nexus_port()`, `asd_I_T_nexus_reset()`, `asd_abort_task()`, `asd_abort_task_set()`, `asd_clear_task_set()`, `asd_lu_reset()`, and `asd_query_task()`. Internal helpers enqueue internal SCBs with timers, build/complete clear-nexus SCBs, parse TMF responses from EDBs, clear nexus by tag or transaction index, and initiate generic SSP TMFs.

Control flow and state: internal TMF SCBs are posted with a timer and stack completion. Clear-nexus helpers build `CLEAR_NEXUS` SCBs for adapter, port, I_T, I_T_L, tag, or transaction context and translate `TC_NO_ERROR` to libsas TMF completion. `asd_I_T_nexus_reset()` suspends transmit, issues a libsas phy reset, clears outstanding commands, and retries resume. `asd_abort_task()` sends `SCB_ABORT_TASK`, copies returned tag information back to the target ASCB, then either clears nexus, waits for late completion, or maps sequencer TMF errors to SAS TMF responses. Generic SSP TMFs build task-management IUs and optionally clear I_T_L after success.

Persistence behavior: mutates task ASCB completion pointers, task tags/tag_valid, task `lldd_task`, timers, and ASCB lifecycle. It also changes sequencer queue/nexus state through clear-nexus SCBs and may reset phys through libsas.

Dependencies and integration points: depends on `aic94xx_task.c`-created ASCB/task state, `aic94xx_sas.h` TMF/clear-nexus layouts, ASCB posting/freeing, EDB invalidation, and libsas TMF/phy reset contracts. Error handlers above this file must set aborted state before abort calls as documented.

Risks: many stack completion/status objects are referenced by ASCB callbacks, so timer deletion and completion ordering are critical. If clear-nexus resume fails, the sequencer can remain suspended for a device. Return values mix done-list opcodes and SAS TMF responses in some paths, requiring careful caller interpretation. Races with normal task completion are expected and handled but fragile.

Test signals: abort of pending, already-done, tag-known, tag-unknown, and device-lost tasks; QUERY TASK for present/missing task; abort/clear task set and LU reset on SSP devices; I_T reset for SATA versus SSP reset type; TMF timeout; EDB response parsing; and clear-nexus resume retry failure.
