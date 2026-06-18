# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.c

Purpose: LIO/target-core fabric module for qla2xxx Fibre Channel target mode, including NPIV support. It translates qla2xxx target callbacks into target-core command, session, TPG, and configfs operations.

Important APIs/functions: WWN parsers/formatters; command lifecycle helpers `tcm_qla2xxx_get_cmd()`, `handle_cmd()`, `write_pending()`, `queue_data_in()`, `queue_status()`, `handle_data()`, and release/free callbacks; task management translation in `handle_tmr()`; session maps by FC S_ID and loop ID; TPG/lport creation, enabling, and dropping; fabric ops `tcm_qla2xxx_ops` and `tcm_qla2xxx_npiv_ops`.

Control flow: qla2xxx receives ATIO/TMR events and calls the registered `qla_tgt_func_tmpl`. Normal SCSI commands allocate a pre-tagged `qla_tgt_cmd`, attach it to the session command list, initialize a target-core `se_cmd`, submit it, and later call qla low-level transmit functions for XFER_RDY, DATA_IN, or status. WRITE completions are queued to a workqueue before target execution. Configfs lport/TPG creation registers the qla target lport; NPIV creation creates an FC vport before binding the target lport.

State and persistence: keeps per-session command lists, krefs, dynamic NodeACL/session maps in a 24-bit S_ID btree and 16-bit loop-id array, configfs attributes, TPG enable flags, and a reclaim workqueue. User-created configfs objects are persistent only while configured in target-core/configfs.

Dependencies and integration: depends on target-core fabric APIs, qla target APIs, SCSI/FC transport, btree, workqueues, `utsname`, and packed IOCB ABI from `qla_target.h`.

Risks: session map races during logout/update, command freeing while firmware owns CTIO, queue-full retry interactions with aborted commands, NPIV host reference balancing, and DIF option mismatches. Test signals include configfs create/drop for qla2xxx and qla2xxx_npiv, demo-mode ACL sessions, login/logout storms, TMR/ABTS translation, WRITE with DIF errors, aborted command paths, and module init `BUILD_BUG_ON` layout checks.
