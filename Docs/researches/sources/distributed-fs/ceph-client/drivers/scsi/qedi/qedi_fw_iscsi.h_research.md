# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_iscsi.h

Purpose: this header declares the qedi firmware iSCSI task-builder API used by the command submission path.

Important types and APIs: `struct iscsi_task_params` carries the firmware task context, SQE, TX/RX sizes, connection ICID, initiator task ID, and CQ RSS number. `struct iscsi_conn_params` carries session/connection transfer policy: first burst length, max send PDU length, max burst length, initial R2T, and immediate data. The header declares builders for read/write SCSI tasks, login, NOP-Out, logout, TMF, text, and cleanup tasks.

Control flow and state: the header has no runtime control flow. It defines the call contract between `qedi_fw.c` and `qedi_fw_api.c`: callers prepare libiscsi-derived headers and SGL parameters, then builders fill firmware contexts/SQEs.

Dependencies and integration points: it includes `qedi_fw_scsi.h`, which supplies SGL, DIF, and initiator command parameter structs. It references HSI PDU header types such as `iscsi_cmd_hdr`, `iscsi_login_req_hdr`, and `iscsi_tmf_request_hdr` from the included firmware/common headers.

Risks: this is a narrow but critical ABI within the driver. If prototypes drift from implementation or if callers pass inconsistent TX/RX sizes and SGL pointers, firmware context initialization can be wrong. Connection parameters must mirror negotiated libiscsi settings.

Test signals: compile-time prototype matching, submission tests for every declared task type, and negative testing for unsupported read/write flag combinations in `init_initiator_rw_iscsi_task`.
