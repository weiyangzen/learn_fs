# sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.c

## Purpose
`drv_fcoe_fw_funcs.c` initializes QEDF FCoE firmware task contexts and SQEs for read/write initiator I/O, midpath/unsolicited exchanges, aborts, cleanup, and sequence recovery. It is a formatting layer between QEDF driver logic and QED firmware HSI structures.

## Important APIs, types, and functions
The local helper `init_common_sqe()` clears the SQE, sets `FCOE_WQE_REQ_TYPE`, and assigns `task_id`. Exported helpers are `init_initiator_rw_fcoe_task()`, `init_initiator_midpath_unsolicited_fcoe_task()`, `init_initiator_abort_fcoe_task()`, `init_initiator_cleanup_fcoe_task()`, and `init_initiator_sequence_recovery_fcoe_task()`. They use `struct fcoe_task_params`, `struct scsi_sgl_task_params`, `struct regpair`, FCoE task contexts, and helper functions from `drv_scsi_fw_funcs.c`.

## Control flow
For read/write I/O, the function preserves the ystorm aggregate validation byte, clears the context, determines fast versus slow SGL mode with `scsi_is_slow_sgl()`, computes transfer size from task type, and fills ystorm, tstorm, ustorm, and mstorm context regions. Write tasks configure TX SGLs and expect first transfer. Read tasks configure RX SGLs and data remaining. Both paths set response/sense buffer addresses and initialize a `SEND_FCOE_CMD` SQE.

Midpath initialization clears context, sets TX and RX SGL context, copies FC header parameters, configures whether firmware places the FC header, initializes connection/CQ/task-type fields, and emits a `SEND_FCOE_MIDPATH` SQE with burst length, SGE count, and fast SGL mode. Abort, cleanup, and sequence recovery only initialize common SQE fields, with sequence recovery also writing the desired offset.

## State and persistence behavior
All state is written into caller-provided firmware context and SQE memory. There is no allocation, global state, persistence, locking, or I/O. The functions assume input structures and DMA addresses have already been prepared by the caller.

## Dependencies and integration points
The file depends on `drv_fcoe_fw_funcs.h`, `drv_scsi_fw_funcs.h`, QEDF HSI definitions, endian conversion helpers, and firmware bitfield macros such as `SET_FIELD`. It is integrated into `qedf.o` and likely called by QEDF I/O submission and ELS/FIP paths before ringing hardware queues.

## Risks and test signals
Risks include HSI layout drift, wrong endian conversion, invalid task type/size pairing, unvalidated pointers, mismatched slow-SGL mode constants between TX/RX fields, and preserving only one aggregate context byte across clear. Tests should check generated context bytes against firmware specifications for read, write, tape, slow SGL, fast SGL, midpath with/without FC header placement, abort, cleanup, and sequence recovery. Static analysis should focus on null pointer assumptions and struct size changes.
