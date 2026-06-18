# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcp.h

Purpose: Defines Fibre Channel Protocol for SCSI command, transfer-ready, response, task-management, and SRR payloads.

Important APIs/types/functions: `struct fcp_cmnd` and `fcp_cmnd32` encode LUN, task attributes, task-management flags, CDB, and data length. `struct fcp_txrdy` carries relative offset and burst length. `struct fcp_resp`, `fcp_resp_ext`, and response-info structs describe status, residuals, sense length, response length, and optional bidirectional residuals. `struct fcp_srr` defines Sequence Retransmission Request. Macros define command flags, task attributes, TM flags, response flags, response codes, and FC-4 feature bits.

Control flow and state: These wire records drive SCSI-over-FC command submission and completion. Consumers inspect read/write bits, residual flags, sense/response lengths, and task-management responses to complete `scsi_cmnd`s or trigger recovery.

Dependencies and integration: Depends on SCSI LUN definitions and is used by libfc FCP packet logic, FC target/initiator paths, and discovery feature reporting.

Risks and test signals: Risks include accepting non-standard short responses incorrectly, CDB additional-length mistakes, residual over/underflow handling, and malformed sense/response length parsing. Tests should cover 16/32-byte CDBs, task management commands, residual flags, sense data extraction, SRR recovery, and feature registration.
