# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_target.h

Purpose: shared qla2xxx Fibre Channel target-mode contract. It defines firmware IOCB layouts, target command/session state, task-management constants, and the callback table used by `qla_target.c` to call into `tcm_qla2xxx.c`.

Important APIs/types: `struct qla_tgt_func_tmpl`, `struct qla_tgt`, `struct qla_tgt_cmd`, `struct qla_tgt_mgmt_cmd`, `struct qla_tgt_srr`, ATIO/CTIO/NACK/ABTS layouts, and exported `qlt_*` prototypes. Inline helpers validate/correct ATIO7 FCP command size, extract data length, test initiator/target/dual mode, convert S_ID to a btree key, and free offset-adjusted scatterlists.

Control flow: firmware response entries arrive as ATIO, CTIO completion, immediate notify, SRR, or ABTS packets and are decoded with these packed structs. `qla_target.c` owns low-level queue processing, while the TCM module fills `qla_tgt_func_tmpl` callbacks for command allocation, submission, session lookup, DIF policy, task management, and teardown.

State and persistence: state is in memory only: target stop flags, session counts, wait queues, SRR lists, reset generation counts, command flags, DIF metadata, trace flags, and hardware exchange identifiers. Persistent behavior is indirect through hardware queues and target-core sessions.

Dependencies and integration: depends on `qla_def.h`, `qla_dsd.h`, target-core types, qla2xxx hardware structures, DMA scatterlists, and Fibre Channel wire formats. Build-time `BUILD_BUG_ON` checks in the TCM module rely on these packet sizes.

Risks: packed hardware ABI drift, endian mistakes, handle-bit collisions, stale session lookup during teardown, SRR retry loops, and DIF metadata mismatch. Test signals include target-mode login/logout, ATIO corruption handling, ABTS/TMR responses, SRR accept/reject, DIF error injection, queue full/retry, and structure-size assertions.
