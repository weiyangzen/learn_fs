# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_api.c

Purpose: this file translates qedi/libiscsi task descriptions into firmware task contexts and SQEs for the QED iSCSI hardware interface.

Important APIs and functions: exported builders are `init_initiator_rw_iscsi_task`, `init_initiator_login_request_task`, `init_initiator_nop_out_task`, `init_initiator_logout_request_task`, `init_initiator_tmf_request_task`, `init_initiator_text_request_task`, and `init_cleanup_task`. Internal helpers initialize cached SGL context, DIF flags/context, default iSCSI task context, extended CDB context, USTORM state, expected data accounting, local completion markers, and common SQE fields.

Control flow: each exported builder receives an `iscsi_task_params` containing a firmware context pointer, SQE pointer, transfer sizes, connection ID, task ID, and CQ RSS number. It zeros/initializes context state from the PDU header, fills storm-specific context fields, populates SGL metadata when TX/RX buffers exist, computes expected transfer and acknowledged data lengths from connection/session settings, sets DIF context when provided, initializes SQE type/flags/SGE count/content length, and returns 0 or an error for unsupported read/write direction combinations.

State and persistence: this file mutates only caller-owned firmware task contexts and SQEs. It preserves `mstorm_ag_context.cdu_validation` across context zeroing. It performs endian conversions into the little-endian HSI layout and uses firmware field macros. No global state is stored.

Dependencies and integration points: it depends on `qedi_hsi.h`, QED common iSCSI HSI definitions, `qedi_fw_iscsi.h`, and `qedi_fw_scsi.h`. `qedi_fw.c` is the primary caller and supplies PDU headers/SGLs built from libiscsi tasks and SCSI commands.

Risks: field programming must exactly match firmware expectations. Incorrect endian conversion, SGE counts, AHS/CDB length, expected transfer length, `exp_data_acked`, or DIF flags can cause data corruption or stuck tasks. Several paths pass nullable SGL pointers when sizes are zero; helpers assume non-null only when corresponding transfer sizes are nonzero. The slow-SGL decision depends on `small_mid_sge` and threshold constants, so SGL classification in `qedi_fw.c` must match this API's interpretation.

Test signals: firmware bring-up tests for read, write, zero-length/TUR, login, logout, text, NOP-Out, TMF, and cleanup WQEs; SGL tests for cached, fast, and slow I/O; AHS/extended CDB coverage; immediate data and initial-R2T combinations; DIF on/off combinations; and HSI structure dumps compared against firmware documentation or known-good traces.
