# sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.h

## Purpose
`drv_fcoe_fw_funcs.h` declares the QEDF FCoE firmware-context initialization API and defines `struct fcoe_task_params`, the common input/output bundle used by those helpers.

## Important APIs, types, and functions
`struct fcoe_task_params` carries output pointers to a `fcoe_task_context` and `fcoe_wqe`, plus task type, TX/RX byte counts, connection CID, initiator task id, CQ RSS number, and disk/tape device classification. Declared functions initialize read/write tasks, midpath unsolicited tasks, abort tasks, cleanup tasks, and sequence recovery tasks.

## Control flow relevance
Callers fill `fcoe_task_params` and SGL-related inputs, call one of the init functions, then submit the resulting SQE/context to firmware through QEDF queueing code elsewhere. The header documents which buffers and payloads are caller-provided.

## State and persistence behavior
The header defines no storage. It describes write targets in caller-owned memory and has no persistence behavior.

## Dependencies and integration points
It includes `drv_scsi_fw_funcs.h`, `qedf_hsi.h`, and QED interface headers. That makes it tightly coupled to firmware HSI structures and common QED storage types.

## Risks and test signals
Risks include stale comments, misspelled parameter names, and ABI drift if HSI structs change without updating helper signatures. Test signals include successful compilation of all QEDF objects, call-site type checking, and context-layout tests in the C implementation.
