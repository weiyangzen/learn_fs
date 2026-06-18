# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/t4fw_api_stor.h

## Purpose

This header defines Chelsio T4/T5 storage firmware ABI structures and constants for FCoE and SCSI offload. It is a packed protocol contract between driver code and adapter firmware, covering remote-device events, FCoE ELS/CT, SCSI read/write/command/abort-close WRs, FCoE resource/link/VNP/service-parameter/stat/FCF commands, and field extraction helpers.

## Important APIs, Types, And Functions

Key enums are `fw_fcoe_link_sub_op`, `fw_fcoe_link_status`, `fw_ofld_prot`, `rport_type_fcoe`, `event_cause_fcoe`, `fcoe_cmn_type`, `fw_wr_stor_opcodes`, and `fw_cmd_stor_opcodes`. Important structures include `fw_rdev_wr`, `fw_fcoe_els_ct_wr`, `fw_scsi_write_wr`, `fw_scsi_read_wr`, `fw_scsi_cmd_wr`, `fw_scsi_abrt_cls_wr`, `fw_fcoe_res_info_cmd`, `fw_fcoe_link_cmd`, `fw_fcoe_vnp_cmd`, `fw_fcoe_sparams_cmd`, `fw_fcoe_stats_cmd`, and `fw_fcoe_fcf_cmd`.

Macros such as `FW_RDEV_WR_FLOWID_GET()`, `FW_SCSI_*_WR_IMMDLEN()`, `FW_SCSI_ABRT_CLS_WR_SUB_OPCODE()`, and `FW_FCOE_*_GET()` encode or decode packed firmware fields. `SCSI_ABORT` and `SCSI_CLOSE` define abort-close suboperation values.

## Control Flow

This file has no executable control flow. Driver code fills these structures, converts fields to big-endian as needed, appends immediate FCP payloads or DSGLs, posts the resulting WRs to Chelsio queues, and later decodes firmware responses or asynchronous events using the same opcode and field definitions.

## State And Persistence

There is no mutable state in this header. Its structures describe DMA/mailbox payloads that become transient hardware/firmware state when submitted. Firmware-created resources such as rdev flowids, FCFs, VNPs, sessions, and exchanges persist on the adapter until explicitly closed, reset, or invalidated by link/session events.

## Dependencies And Integration Points

The header depends on fixed-width Linux endian types and the generic firmware command header conventions from included Chelsio headers. It is consumed by csiostor SCSI, lnode/rnode, FCoE control, mailbox, and WR paths. Correct integration requires exact field sizes, endian conversion, opcode values, and firmware-version compatibility.

## Risks

Any layout drift breaks hardware communication. Several fields are densely packed and exposed only through partial macros, so callers must know which endian conversion and bit shifts apply. `u64 cookie` fields carry host pointers in csiostor; that assumes pointer-width compatibility and that firmware returns the value opaquely. This ABI mixes FCoE and iSCSI remote-device layouts in unions, increasing risk if protocol selectors are wrong.

## Test Signals

Signals include successful compile against firmware headers, adapter login and rdev events, FCoE link up/down handling, VNP allocation/free, FCF discovery, SCSI read/write/cmd completions, abort/close completions, stats retrieval, and verification that firmware statuses map correctly into SCSI/FC upper-layer behavior.
