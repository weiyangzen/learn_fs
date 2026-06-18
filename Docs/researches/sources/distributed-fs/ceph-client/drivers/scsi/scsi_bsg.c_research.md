# sources/distributed-fs/ceph-client/drivers/scsi/scsi_bsg.c

## Purpose
`scsi_bsg.c` registers SCSI block SG (BSG) command handling for SCSI devices. It supports traditional `sg_io_v4` request submission and newer `io_uring` passthrough commands, mapping user CDB/data buffers into block requests and returning SCSI status, host status, residuals, and sense data.

## Important APIs, Types, And Functions
The public registration function is `scsi_bsg_register_queue()`. The synchronous sg_io path is `scsi_bsg_sg_io_fn()`. The io_uring path is `scsi_bsg_uring_cmd()`, `scsi_bsg_map_user_buffer()`, `scsi_bsg_uring_cmd_done()`, and `scsi_bsg_uring_task_cb()`. `struct scsi_bsg_uring_cmd_pdu` stores per-command temporary state inside `io_uring_cmd.pdu`: mapped bio, request pointer, and response buffer address.

## Control Flow
For sg_io, the handler validates BSG protocol/subprotocol, rejects bidirectional transfers, allocates a SCSI driver request for input or output, copies the user CDB, checks command permissions with `scsi_cmd_allowed()`, maps one user data buffer if present, executes the request synchronously, fills `sg_io_v4` status fields and residuals, copies sense data to the response buffer when present, unmaps the bio, and frees the request.

For io_uring, submission validates protocol, CDB pointer/length, no bidi, and no iovec mode, chooses NOWAIT/GFP_NOWAIT when requested, allocates a request, copies and authorizes the CDB, records response state, maps fixed or normal user buffers, sets timeout/end_io data, and starts `blk_execute_rq_nowait()`. Completion schedules task work; task work unmaps the bio, copies sense data if needed, builds the packed BSG `res2` status value, frees the request, and completes the io_uring command.

## State And Persistence
No long-lived state is stored in this file. Per-command state lives in the request, SCSI command PDU, mapped bio, user header, and io_uring PDU until completion. There is no persistent storage behavior.

## Dependencies And Integration Points
The file depends on block request allocation/execution, BSG queue registration, SCSI command permission filtering, uaccess, SG/BSG UAPI structures, and io_uring command/task-work APIs. It integrates with each `scsi_device` request queue through `bsg_register_queue()`.

## Risks And Edge Cases
Bidirectional BSG support is explicitly removed and returns `-EOPNOTSUPP`. The io_uring path does not support iovec counts, only a single fixed or normal buffer. User pointers and CDB lengths are security-sensitive; permission checks depend on `open_for_write`. Sense copying can fail after the device command has completed, producing `-EFAULT` while still reporting packed status. Nonblocking allocation/map paths can fail under memory pressure. Correct lifetime depends on request freeing only after task-work completion in the io_uring path.

## Test Signals
Signals include BSG queue registration per SCSI device, valid INQUIRY/TEST UNIT READY passthrough through sg_io and io_uring, rejection of invalid protocol/subprotocol, missing CDB, overlong CDB, bidi transfers, iovec mode, and disallowed commands for read-only opens, user data mapping for input and output, fixed-buffer io_uring mapping, timeout propagation, sense data copy on check condition, residual reporting, and request/bio cleanup on all error paths.
