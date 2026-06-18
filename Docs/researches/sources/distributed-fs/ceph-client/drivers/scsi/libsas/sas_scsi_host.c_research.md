# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_scsi_host.c

## Purpose
`sas_scsi_host.c` is libsas' SCSI mid-layer integration. It converts SCSI commands to SAS tasks, completes SAS task status back to SCSI results, coordinates normal command submission, implements layered error handling and task-management functions, manages SCSI target/device attachment, delegates SATA paths to libata, and provides firmware SAS-address loading.

## Important APIs, types, and functions
- `sas_end_task` maps `task_status_struct` response/status into SCSI host status and SAM status, copies sense data, clears `host_scribble`, and frees the SAS task.
- `sas_scsi_task_done` is the normal SAS task completion callback. It synchronizes with EH via `dev->done_lock` and `SAS_HA_FROZEN`, then calls `sas_end_task` and `scsi_done`.
- `sas_create_task` allocates a task, binds it to the SCSI command, fills SSP LUN/task attributes, scatterlist, transfer length, data direction, and completion callback.
- `sas_queuecommand` rejects gone devices, delegates SATA commands to `ata_sas_queuecmd`, or submits SSP/SAS tasks through LLDD `lldd_execute_task`.
- EH helpers `sas_scsi_find_task`, `sas_recover_lu`, `sas_recover_I_T`, `sas_eh_handle_sas_errors`, and `sas_scsi_recover_host` implement escalation from abort, query, LU recovery, I_T nexus reset, command-device reset, port nexus clear, HA nexus clear, and finally queue clearing.
- `sas_queue_reset`, `sas_eh_device_reset_handler`, and `sas_eh_target_reset_handler` support directed resets from outside the EH thread by queueing reset work on `ha->eh_dev_q`.
- `sas_get_local_phy`, `sas_find_dev_by_rphy`, `sas_target_alloc`, and `sas_target_destroy` manage transport-to-domain-device association and krefs.
- `sas_sdev_configure`, `sas_change_queue_depth`, `sas_sdev_init`, `sas_ioctl`, and `sas_bios_param` implement SCSI device policy, queue depth, SATA LUN restriction, SATA ioctl passthrough, and disk geometry defaults.
- `sas_execute_internal_abort`, `sas_execute_internal_abort_single`, `sas_execute_internal_abort_dev`, `sas_execute_tmf`, and the wrappers `sas_abort_task_set`, `sas_clear_task_set`, `sas_lu_reset`, `sas_query_task`, and `sas_abort_task` implement blocking internal TMF/abort commands with retries and 20-second timers.
- `sas_task_abort` lets LLDD request upper-layer abort handling, with special handling for internal slow tasks and SATA tasks.
- `sas_request_addr` loads a textual SAS address from firmware file `sas_addr` and converts it with `hex2bin`.

## Control flow and state
Normal I/O starts in `sas_queuecommand`. SATA devices stay under libata locking and queueing. SSP devices get a `sas_task` stored in `cmd->host_scribble`, then LLDD owns execution. Completion comes through `sas_scsi_task_done`; if EH froze the HA, completion is ignored and EH finishes the command later.

EH begins by moving `shost->eh_cmd_q` into a local queue, setting `SAS_HA_FROZEN`, and handling SAS-task-backed failures. Commands that completed before EH ownership are moved aside. Remaining tasks are aborted or queried. Tasks still at the LU trigger LU recovery; tasks not at the LU or failed aborts trigger I_T recovery. If that fails, EH escalates to reset handlers, port nexus clear, HA nexus clear, or forced completion. After SAS handling, SATA EH and generic SCSI sense/ready processing run, directed reset queue entries are serviced, libata strategy handling runs, and the done queue is flushed. The loop repeats while `ha->eh_active` indicates newly queued reset work.

Internal TMF execution allocates a slow task, arms a timer, submits it through LLDD `lldd_execute_task`, waits for completion, runs LLDD completion hooks, interprets SAS task status, retries up to three times, and frees the slow task. Timeout paths mark `SAS_TASK_STATE_ABORTED` and can call LLDD timeout/aborted hooks.

## State and persistence behavior
Per-command state lives in `scsi_cmnd.host_scribble`, `struct sas_task`, `task_state_flags`, task status, and SCSI result fields. EH state lives in `sas_ha_struct` queues (`eh_dev_q`, `eh_done_q`, `eh_ata_q`), `eh_active`, and state bits such as `SAS_HA_FROZEN`. Device references are maintained through `domain_device.kref` stored in `scsi_target.hostdata`. `sas_request_addr` reads firmware once per request and does not persist changes.

## Dependencies and integration points
This file sits between SCSI core, block abort handling, libata SAS support, SCSI transport SAS, firmware loading, and LLDD libsas callbacks (`lldd_execute_task`, abort/query/reset/clear-nexus hooks, TMF hooks, abort timeout hooks). It also depends on discovery-maintained `domain_device` and port lists.

## Risks and edge cases
- `host_scribble` ownership is central. Double completion or failure to clear it can cause use-after-free or EH leaks.
- EH uses `SAS_HA_FROZEN` plus `dev->done_lock` to arbitrate completion races; changes here are high risk.
- `sas_queue_reset` spins up to 100 tries without sleeping; it expects rapid state change under `ha->lock`.
- `sas_eh_handle_sas_errors` contains a suspicious log expression using `SAS_ADDR(task->dev)` in one message rather than `task->dev->sas_addr`; logging correctness should be checked before relying on that line.
- Internal TMF timeout paths depend on LLDD honoring task state and optional hooks; inconsistent LLDD behavior can leak in-flight firmware commands.
- SATA devices are deliberately routed to libata for queueing, EH, ioctl, queue-depth changes, and LUN restrictions; mixed SAS/SATA changes must preserve those splits.

## Test signals
- SSP command success, underrun, overrun, open reject, queue full, check condition, and transport errors should map to expected SCSI results.
- Completion-vs-EH races should show no double frees with `SAS_HA_FROZEN` set.
- Abort/query/LU-reset/I_T-reset/clear-nexus escalation should be covered with LLDD fault injection.
- Directed reset from outside EH should enqueue work and cause EH retry until `eh_active` reaches zero.
- SATA command, EH, ioctl, queue-depth, and nonzero-LUN rejection paths should delegate to libata.
- Firmware `sas_addr` loading should reject short content and malformed hex.
