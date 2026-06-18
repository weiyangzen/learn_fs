# sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_hsi.h

Purpose: defines the QEDF-facing FCoE hardware/software interface layouts shared with QED firmware: command queue elements, completion queue elements, response information, unsolicited/warning/error payloads, error code enums, slow-path error codes, and task transmit states.

Important APIs/types/functions: `struct fcoe_cmdqe_control` and `struct fcoe_cmdqe` describe control and payload command queue entries. `struct fcoe_cqe` is the central completion entry with `cqe_data` fields for task ID and CQE type plus a `union fcoe_cqe_info`. Completion payloads include `fcoe_cqe_rsp_info` for FCP response status/residual/sense metadata, `fcoe_err_report_entry` for error detection, `fcoe_warning_report_entry` for REC/RR timer warnings, `fcoe_abts_info` for ABTS responses, `fcoe_cqe_midpath_info` for ELS/TMF response placement, and `fcoe_unsolic_info` for BDQ-backed unsolicited packets. Enums `fcoe_cqe_type`, `fcoe_fp_error_warning_code`, `fcoe_sp_error_code`, and `fcoe_task_tx_state` define firmware event and state values consumed by completion dispatch and recovery code.

Control flow: no executable code. Runtime code in `qedf_io.c` and `qedf_els.c` decodes CQEs using these structures, tests bit fields with the provided masks/shifts, extracts XIDs and CQE types from `cqe_data`, and maps error/warning bits to ABTS, REC/SRR, cleanup, or unsolicited frame handoff.

State and persistence: structures represent DMA/shared-memory protocol state produced or consumed by firmware. They are transient queue entries and task states, not persisted. Endianness annotations (`__le16`, `__le32`) define how drivers must convert firmware values.

Dependencies and integration: includes QED common/storage/FCoE HSI headers and must be included before other QED headers from `qedf.h`. The layouts are tightly coupled to firmware task initialization helpers and QED FCoE ops.

Risks and test signals: layout drift between driver and firmware is catastrophic, causing bad task IDs, wrong residuals, missed errors, or invalid DMA addresses. Several fields are bit-packed and endian-sensitive; consumers must convert before comparing or logging. Build/API compatibility with QED headers, firmware CQE decoding tests, unsolicited BDQ index validation, ABTS response handling, residual/sense parsing, and warning/error bitmap coverage are critical signals.
