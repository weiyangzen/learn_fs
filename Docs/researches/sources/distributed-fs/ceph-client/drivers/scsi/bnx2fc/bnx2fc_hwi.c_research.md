# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_hwi.c

## Purpose

`bnx2fc_hwi.c` implements the firmware and hardware interface for bnx2fc. It builds FCoE KWQEs, processes KCQE and per-session CQ completions, handles unsolicited frames and firmware error reports, rings doorbells, maps doorbell BAR space, initializes firmware task contexts, and allocates/frees firmware-visible DMA resources.

## Important APIs, Types, and Functions

Firmware request functions include `bnx2fc_send_stat_req()`, `bnx2fc_send_fw_fcoe_init_msg()`, `bnx2fc_send_fw_fcoe_destroy_msg()`, `bnx2fc_send_session_ofld_req()`, `bnx2fc_send_session_enable_req()`, `bnx2fc_send_session_disable_req()`, and `bnx2fc_send_session_destroy_req()`. Completion and event functions include `bnx2fc_indicate_kcqe()`, `bnx2fc_process_new_cqes()`, `bnx2fc_process_cq_compl()`, and `bnx2fc_process_l2_frame_compl()`. Queue/task helpers include `bnx2fc_add_2_sq()`, `bnx2fc_ring_doorbell()`, `bnx2fc_arm_cq()`, `bnx2fc_map_doorbell()`, `bnx2fc_get_next_rqe()`, `bnx2fc_return_rqe()`, `bnx2fc_init_task()`, `bnx2fc_init_mp_task()`, `bnx2fc_init_cleanup_task()`, and `bnx2fc_init_seq_cleanup_task()`.

## Control Flow

Firmware init sends three KWQEs with queue sizes, task-context PBL, hash tables, HSI version, and error bitmap. Session offload sends four KWQEs describing queues, DMA memory, MACs, VLANs, FC IDs, payload sizes, sequence settings, recovery flags, and timers. KCQE handling dispatches CQ notifications, session state completions, init/destroy completions, and stat completions.

Per-session CQ processing consumes entries by toggle bit, routes unsolicited CQEs to frame/error/warning handling, and queues pending-work completions to per-CPU workers or processes inline. `bnx2fc_process_cq_compl()` dispatches by command type and firmware RX state to SCSI, ELS, TM, ABTS, cleanup, or sequence-cleanup completion handlers. Task initialization writes FCP command, SGL/cached SGE state, data length, task/device/class type, context ID, RX state, sequence count, FC headers, and cleanup metadata into firmware task contexts.

## State and Persistence Behavior

The file manages firmware-visible DMA state: task-context pages/BDT, hash tables/PBLs, T2 hash tables, dummy buffer, stats buffer, per-rport queues, connection DB, SQ/CQ/RQ indices and toggle bits, and MMIO doorbell mappings. It mutates rport flags, HBA adapter flags, command task pointers, and per-command recovery state.

## Dependencies and Integration Points

It depends on HSI structures, bnx2fc constants, CNIC `submit_kwqes`, PCI DMA/ioremap APIs, per-CPU worker state from `bnx2fc_fcoe.c`, libfc frame helpers, SCSI command structures, and completion handlers in I/O, target, and ELS code.

## Risks and Edge Cases

DMA and endian correctness are critical. Many 64-bit DMA addresses are manually split into low/high fields. Queue wrap/toggle logic must be exact. `bnx2fc_get_next_rqe()` cannot span ring end in one call, so unsolicited-frame copying must handle wrap carefully. Completion work can race teardown. Error reports trigger REC/SRR for selected tape cases and ABTS otherwise, so misclassification can hang or lose commands.

## Test Signals

Validate init/destroy KWQEs, session offload/enable/disable/destroy, doorbell mapping/writes, SQ/CQ/RQ wrap stress, FCP read/write with cached and multi-SGE contexts, ELS/TMF/ABTS/cleanup/sequence-cleanup completions, unsolicited ELS, firmware error/warning reports, REC/SRR tape recovery, stats requests, DMA API debug, CPU hotplug completion processing, and teardown during pending CQEs.
