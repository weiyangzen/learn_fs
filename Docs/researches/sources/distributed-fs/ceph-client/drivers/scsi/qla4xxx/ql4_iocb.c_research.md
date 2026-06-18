<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_iocb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_iocb.c

Purpose: builds and posts firmware IOCBs for SCSI commands, marker commands, iSCSI passthrough PDUs, and mailbox-over-IOCB ping requests. It also provides adapter-family queue doorbell and completion-consumer updates.

Important APIs/types/functions: public functions are `qla4xxx_send_marker_iocb()`, `qla4_83xx_queue_iocb()`, `qla4_83xx_complete_iocb()`, `qla4_82xx_queue_iocb()`, `qla4_82xx_complete_iocb()`, `qla4xxx_queue_iocb()`, `qla4xxx_complete_iocb()`, `qla4xxx_send_command_to_isp()`, `qla4xxx_send_passthru0()`, and `qla4xxx_ping_iocb()`. Internal helpers include `qla4xxx_space_in_req_ring()`, `qla4xxx_advance_req_ring_ptr()`, `qla4xxx_get_req_pkt()`, `qla4xxx_alloc_cont_entry()`, `qla4xxx_calc_request_entries()`, `qla4xxx_build_scsi_iocbs()`, `qla4xxx_get_new_mrb()`, and `qla4xxx_send_mbox_iocb()`.

Control flow: SCSI submission takes `hardware_lock`, rejects offline adapters, DMA maps the SCSI command, calculates needed request entries from SG segment count, enforces firmware IOCB high-water limits, fills a `command_t3_entry`, appends continuation entries for extra DSDs, stores the request tag in `host_scribble`, marks the SRB active/DMA-valid, updates counters, and rings the adapter doorbell. Passthrough builds a `passthru0` IOCB with request/response DMA buffers and queues task completion work from ISR later. Ping allocates an MRB, posts an `ET_MBOX_CMD` IOCB, and is completed through `ET_MBOX_STATUS`.

State and persistence: mutates request ring producer state, request free count, `iocb_cnt`, per-SRB `iocb_cnt`/state/flags, active MRB array, and task IOCB request counts. Persistent state is not directly modified, but passthrough and mailbox IOCBs can trigger firmware/network effects.

Dependencies and integration: integrates with Linux SCSI DMA mapping/tagging, libiscsi task data, qla4xxx DDB sessions, firmware IOCB ABI from `ql4_fw.h`, and `isp_ops` MMIO callbacks for 40xx/82xx/83xx doorbells.

Risks and test signals: queue accounting is delicate: ring free space, continuation allocation, `iocb_cnt`, and DMA unmap on queue failure must stay balanced. `qla4_82xx_queue_iocb()` computes `dbval` but writes only `request_in`, so adapter-specific expectations should be verified. Test signals include high-SG I/O requiring continuation entries, full request rings, offline/reset races, passthrough PDU response handling, ping IOCB completion, and DMA-map failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_iocb.c -->
