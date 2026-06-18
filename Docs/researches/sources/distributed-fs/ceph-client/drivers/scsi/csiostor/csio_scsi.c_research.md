# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.c

## Purpose

This file implements the Chelsio FCoE SCSI mid-layer bridge for csiostor. It accepts Linux SCSI commands, maps them into firmware SCSI work requests, tracks those requests through a small state machine, handles completions/errors/task management, exposes FCoE host sysfs controls, and owns allocation of SCSI request/response/DDP buffers.

## Important APIs, Types, And Functions

The file exports module tunables such as `csio_scsi_eqsize`, `csio_scsi_iqlen`, `csio_scsi_ioreqs`, `csio_lun_qdepth`, and scan-timeout values. Core entry points are `csio_queuecommand()`, `csio_scsi_cmpl_handler()`, `csio_scsim_cleanup_io()`, `csio_scsim_cleanup_io_lnode()`, `csio_scsim_init()`, and `csio_scsim_exit()`. It also defines `csio_fcoe_shost_template` and `csio_fcoe_shost_vport_template` for SCSI host registration.

Important helpers build firmware requests: `csio_scsi_fcp_cmnd()`, `csio_scsi_init_cmd_wr()`, `csio_scsi_init_read_wr()`, `csio_scsi_init_write_wr()`, `csio_scsi_init_ultptx_dsgl()`, and `csio_scsi_init_abrt_cls_wr()`. Error handling flows through `csio_scsi_err_handler()`, `csio_scsi_cbfn()`, `csio_eh_abort_handler()`, `csio_tm_cbfn()`, and `csio_eh_lun_reset_handler()`. State functions are `csio_scsis_uninit()`, `csio_scsis_io_active()`, `csio_scsis_tm_active()`, `csio_scsis_aborting()`, `csio_scsis_closing()`, and `csio_scsis_shost_cmpl_await()`.

## Control Flow

Normal I/O starts in `csio_queuecommand()`. The function checks FC rport and hardware readiness, DMA-maps the SCSI scatterlist, rejects requests above `CSIO_SCSI_MAX_SGE`, obtains a preallocated `csio_ioreq`, fills lnode/rnode/queue/data-direction fields, stores the command in `scratch1`, and posts `CSIO_SCSIE_START_IO`. The uninitialized state chooses a command, read, or write WR, optionally routes reads through DDP setup, adds the request to `active_q`, and rings the selected egress queue.

Completions enter through `csio_scsi_cmpl_handler()`, which validates `CPL_FW6_MSG`, decodes WR opcode/status, recovers the `csio_ioreq` from the firmware cookie, and returns it to the caller. State completion usually moves the request out of `active_q`; special I-T nexus-loss statuses can move it to the rnode host completion wait queue until remote-node loss is reported. Callback processing maps firmware/FCP status to Linux `cmnd->result`, copies autosense, unmaps DMA, copies DDP bounce data when needed, calls `scsi_done()`, clears the command pointer, and wakes error-handler waiters.

SCSI EH abort posts an ABORT or CLOSE WR depending on lnode readiness, waits for `cmplobj`, and treats `DID_REQUEUE` as a successful abort. LUN reset issues an FCP task-management command, waits by polling `csio_scsi_cmnd(ioreq)`, then gathers active I/O matching the LUN and aborts them.

## State And Persistence

Runtime state is in `struct csio_scsim`: `active_q`, `ioreq_freelist`, `ddp_freelist`, `freelist_lock`, protocol lengths, `max_sge`, and statistics. Each `csio_ioreq` persists through firmware completion and carries state-machine state, queue indices, DMA response buffer, WR status, callback, lnode/rnode, command pointer, optional DDP buffer list, and completion object. No on-disk state exists. Hardware-visible state consists of DMA mappings, firmware exchanges, and FCoE/SCSI sessions.

## Dependencies And Integration Points

This code integrates with Linux SCSI, libfc/fc transport, csiostor hardware/lnode/rnode modules, the Chelsio WR layer, firmware ABI structures from `t4fw_api_stor.h`, DMA pools, PCI device DMA allocation, sysfs host attributes, and FC error-recovery helpers such as `fc_block_scsi_eh()` and `fc_remote_port_chkready()`.

## Risks

Request lifetime is race-prone: abort, close, firmware completion, and driver cleanup all mutate the same `csio_ioreq` and command pointer. DDP bounce buffering depends on page-boundary alignment and finite `csio_ddp_descs`; underprovisioning returns `-EBUSY`. Several cleanup paths sleep while dropping and reacquiring `hw->lock`, so queue membership must remain consistent. `csio_store_dbg_level()` appears to return `-EINVAL` when `sscanf()` succeeds, which makes the sysfs debug-level store path suspect. LUN reset failure paths increment rnode stats only when `rn` is valid; earlier `fail_ret` avoids that, but later paths assume a live rnode.

## Test Signals

Useful signals include successful kernel build with csiostor, SCSI discovery through `csio_scan_finished()`, normal read/write/control I/O, SGE-limit rejection, DMA-map failure injection, unaligned-read DDP bounce coverage, FCP autosense and residual handling, abort/close races, LUN reset with pending I/O, link-down/rdev-lost serialization, sysfs `hw_state`, `device_reset`, `disable_port`, and `dbg_level` behavior, plus leak checks for ioreq/DDP freelists after unload.
