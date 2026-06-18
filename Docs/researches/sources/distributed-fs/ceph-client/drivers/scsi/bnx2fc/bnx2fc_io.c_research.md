# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_io.c

## Purpose

`bnx2fc_io.c` is the FCoE offload driver's SCSI I/O manager. It owns the per-XID `struct bnx2fc_cmd` pool, maps SCSI scatterlists into firmware buffer descriptors, posts FCP commands to target send queues, handles completions, and drives SCSI error handling through ABTS, cleanup requests, and FCP task management functions.

## Important APIs, Types, and Functions

Externally used entry points include `bnx2fc_cmd_mgr_alloc()`, `bnx2fc_cmd_mgr_free()`, `bnx2fc_cmd_alloc()`, `bnx2fc_elstm_alloc()`, `bnx2fc_cmd_release()`, `bnx2fc_queuecommand()`, `bnx2fc_post_io_req()`, `bnx2fc_eh_abort()`, `bnx2fc_eh_device_reset()`, `bnx2fc_eh_target_reset()`, `bnx2fc_initiate_abts()`, `bnx2fc_initiate_cleanup()`, `bnx2fc_initiate_seq_cleanup()`, `bnx2fc_process_scsi_cmd_compl()`, `bnx2fc_process_abts_compl()`, `bnx2fc_process_cleanup_compl()`, `bnx2fc_process_tm_compl()`, and `bnx2fc_build_fcp_cmnd()`.

The file revolves around `struct bnx2fc_cmd`, `struct bnx2fc_cmd_mgr`, `struct io_bdt`, `struct bnx2fc_mp_req`, `struct fcoe_task_ctx_entry`, `struct fcoe_bd_ctx`, and SCSI/libfc objects such as `struct scsi_cmnd`, `struct fc_lport`, `struct fc_rport`, and `struct fc_rport_priv`.

## Control Flow

Normal I/O enters through `bnx2fc_queuecommand()`. It verifies remote-port readiness, local-port link state, session readiness, and target retry delay, then allocates a command under `tgt_lock` and calls `bnx2fc_post_io_req()`. Posting sets direction flags and counters, maps the SCSI SG list into BD entries, initializes the firmware task context, starts an I/O timeout when enabled, adds the XID to the SQ, links the command on `active_cmd_queue`, and rings the target doorbell.

Completions arrive from the hardware path into `bnx2fc_process_scsi_cmd_compl()`. The completion path suppresses duplicate timeout races with `BNX2FC_FLAG_IO_COMPL`, cancels timeout work, parses the FCP response and sense/RQ data, moves the command to `io_retire_queue`, unmaps DMA, sets SCSI result and residual, applies retry-delay throttling for BUSY/TASK_SET_FULL, calls `scsi_done()`, and drops the command reference.

Error handling is multi-stage. `bnx2fc_cmd_timeout()` issues ABTS for timed-out SCSI commands, invokes cleanup when ABTS itself times out, and handles ELS timeout callbacks. `bnx2fc_eh_abort()` removes a command from the active queue, initiates ABTS, waits for `abts_done`, and falls back to cleanup before returning control to the SCSI mid-layer. Device and target resets call `bnx2fc_initiate_tmf()`, which sends a TMF FCP command and then aborts matching active commands on successful LUN or target reset completion.

## State and Persistence Behavior

No durable state is written. Runtime state is held in per-adapter command pools, per-target active/TMF/ELS/retire queues, per-command refcounts and flags, delayed timeout work, DMA-coherent BD tables, and `bnx2fc_priv(sc_cmd)->io_req` back-pointers. Firmware-visible task context is indexed by XID. Timer holds are explicit `kref` references released by timeout cancellation or execution.

## Dependencies and Integration Points

The file integrates with the Linux SCSI mid-layer, libfc remote-port state, FCoE task-context helpers from `bnx2fc_hwi.c`, CNIC DMA resources through the PCI device, and target/session state from `bnx2fc_tgt.c`. It depends on hardware constants and command structures from `bnx2fc.h`, FCP status layouts, FC frame headers, workqueues, completions, krefs, and DMA mapping APIs.

## Risks and Edge Cases

Race handling is delicate because timeout work, SCSI error handlers, firmware completions, and session flush can all see the same command. Incorrect flag ordering can double-complete a SCSI command or leak a command reference. BD splitting must stay under `BNX2FC_FW_MAX_BDS_PER_CMD`; otherwise the mid-layer sees host busy. `bnx2fc_parse_fcp_rsp()` assumes a single RQ buffer is normally enough for response and sense data and truncates invalid lengths. Cleanup/ABTS interactions rely on firmware behavior that one completion may suppress the other. Queue accounting uses atomics plus per-list locks, so missed `kref_put()` or queue removal can stall session upload.

## Test Signals

Useful validation includes SCSI read/write I/O with direct and split SG entries, zero-length/control commands, induced BD overflow, FCP sense data and residual handling, BUSY/TASK_SET_FULL retry delay, command timeout with ABTS success and failure, cleanup timeout, LUN and target reset while I/O is active, ELS timeout callbacks, session flush with active commands, and reference/DMAMAP leak checks during link flap and module unload.
