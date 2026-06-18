# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_constants.h

## Purpose

`57xx_iscsi_constants.h` defines firmware HSI constants for NetXtreme II iSCSI offload. It supplies opcode, status, task-type, queue-doorbell, page-size, digest, and connection-type values consumed by `bnx2i_hwi.c` and the firmware ABI structures in `57xx_iscsi_hsi.h`.

## Important APIs, Types, and Functions

The file has no functions or types. Important definitions include cleanup request/response opcodes, iSCSI task type encodings for read/write/middle-path commands, initial CQ sequence numbers, KWQE layer/opcodes for firmware init, connection offload/update/destroy, KCQE opcodes for offload/update/init/cleanup/TCP/iSCSI errors, completion status codes, SQ/RQ/CQ doorbell structure sizes, page-size encodings, iSCSI header/digest sizes, and the 577xx iSCSI connection type.

## Control Flow

There is no executable control flow. Runtime code uses these constants when building KWQEs, SQ WQEs, KCQE dispatch switches, error classification, queue page-table offsets, and doorbell headers.

## State and Persistence Behavior

No state is stored. The constants are firmware ABI and must remain stable for driver and firmware compatibility.

## Dependencies and Integration Points

Included by `bnx2i.h`, which in turn feeds all bnx2i implementation files. `bnx2i_send_fw_iscsi_init_msg()` uses init opcodes, page-size encodings, and error masks. `bnx2i_indicate_kcqe()` and error handlers dispatch on KCQE opcodes/status values. 577xx queue setup uses the SQ/RQ/CQ DB size constants.

## Risks and Edge Cases

Wrong numeric values would route KWQEs to the wrong firmware operation, misclassify fatal protocol errors as warnings, corrupt 577xx page-table offsets, or break doorbell programming. Because these values are not type checked, regressions usually appear only at runtime on specific hardware/firmware combinations.

## Test Signals

Build coverage is necessary but insufficient. Useful signals include firmware init success, offload/update/destroy KCQE dispatch, command cleanup response handling, license-error reporting, protocol warning versus recovery behavior under `error_mask1/2`, and 577xx doorbell/page-table operation.
