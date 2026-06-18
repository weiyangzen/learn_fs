# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.c

## Purpose

`pm8001_sas.c` implements the libsas low-level driver behavior for PM8001/PM80xx adapters after the PCI/module layer has created an HBA. It handles SAS task submission, CCB/tag allocation and freeing, DMA mapping for commands, local PHY control, SCSI scan startup, device registration and deregistration with firmware, open-reject retry completion, and SCSI/SAS error recovery callbacks such as abort task, query task, LUN reset, and I_T nexus reset.

The file is the bridge between libsas domain objects (`domain_device`, `sas_task`, `asd_sas_phy`, `asd_sas_port`) and firmware-facing driver objects (`pm8001_hba_info`, `pm8001_device`, `pm8001_ccb_info`, `pm8001_phy`). Like the init file, it avoids chip-specific IOMB construction by delegating command preparation and management operations through `PM8001_CHIP_DISP`.

## Important APIs, Types, and Functions

Tag and CCB support consists of `pm8001_find_tag`, `pm8001_tag_alloc`, `pm8001_tag_free`, `pm8001_ccb_task_free`, and the inline `pm8001_ccb_alloc`/`pm8001_ccb_free` helpers from `pm8001_sas.h`. Reserved tags are tracked in `pm8001_ha->rsvd_tags`; normal request-backed I/O uses `sas_task_find_rq(task)->tag + PM8001_RESERVE_SLOT`.

Command submission is centered on `pm8001_queue_command`. It validates device/port availability, handles controller fatal-error short-circuiting, allocates a CCB, maps SG lists for non-ATA tasks, stores `task->lldd_task`, increments `pm8001_dev->running_req`, and dispatches to `pm8001_deliver_command`. `pm8001_deliver_command` selects one of `smp_req`, `ssp_io_req`, `ssp_tm_req`, `sata_req`, or `task_abort` based on `task_proto` and `task->tmf`.

PHY and scan functions are `pm8001_phy_control`, `pm8001_scan_start`, and `pm8001_scan_finished`. PHY control implements link-rate changes, hard/link reset, spinup-hold release, disable, and event counter reads. Scan start optionally issues SAS reinitialization for SPC and starts every PHY; scan finish waits at least one second and drains libsas work.

Device lifecycle functions are `pm8001_dev_found`, `pm8001_dev_found_notify`, `pm8001_dev_gone`, `pm8001_dev_gone_notify`, `pm8001_alloc_dev`, `pm8001_init_dev`, `pm8001_find_dev`, and `pm8001_free_dev`. Discovery allocates a `pm8001_device`, attaches it to `domain_device->lldd_dev`, resolves attached PHY IDs for expander and direct SATA paths, sends firmware registration, and waits for completion. Removal aborts outstanding work if needed, deregisters firmware device ID, clears local PHY attachment for direct-attached devices, frees the slot, and clears `dev->lldd_dev`.

Error recovery functions are `pm8001_abort_task`, `pm8001_query_task`, `pm8001_lu_reset`, `pm8001_clear_task_set`, `pm8001_I_T_nexus_reset`, `pm8001_I_T_nexus_event_handler`, `pm8001_setds_completion`, and `pm8001_tmf_aborted`. They integrate libsas helpers such as `sas_abort_task`, `sas_query_task`, `sas_lu_reset`, `sas_clear_task_set`, `sas_phy_reset`, `sas_execute_internal_abort_single`, and `sas_execute_internal_abort_dev`.

Diagnostics and retry helpers include `pm80xx_get_tag_opcodes`, `pm80xx_show_pending_commands`, `pm80xx_get_local_phy_id`, `pm8001_open_reject_retry`, and tracepoint use in ATA completion cleanup. `pm8001_mem_alloc` is also defined here for coherent DMA allocation with alignment adjustment, even though init code is its heaviest user.

## Control Flow

The normal I/O path begins when libsas calls `pm8001_queue_command`. If the task is not an internal abort and lacks a port, the driver completes it as `SAS_TASK_UNDELIVERED`/`SAS_PHY_DOWN`. If the controller is in fatal error, it completes the task as undelivered. Otherwise the function takes the HBA lock, verifies the target `pm8001_device` and `pm8001_port` are still valid and attached, allocates a CCB, maps non-ATA scatter/gather entries, links the CCB to `task->lldd_task`, records `n_elem`, increments `running_req`, and calls `pm8001_deliver_command`.

`pm8001_deliver_command` is a protocol switch. SMP tasks call the chip `smp_req`; SSP tasks call either `ssp_tm_req` for TMFs or `ssp_io_req` for normal I/O; SATA/STP tasks call `sata_req`; internal abort tasks call `task_abort`. If dispatch returns an error, `pm8001_queue_command` decrements `running_req`, unmaps any mapped SG list, frees the CCB, and returns the error to libsas.

Completion control flow is split across this file and MPI response handlers in other files. When firmware completes a command, those handlers call `pm8001_ccb_task_free` or `pm8001_ccb_task_free_done`. `pm8001_ccb_task_free` unmaps non-ATA SG lists, unmaps SMP request/response SGs, emits ATA completion trace data, clears `task->lldd_task`, and frees the CCB/tag. The `_done` helper then uses a memory barrier and calls `task->task_done`.

Discovery flow starts with `pm8001_dev_found_notify`. Under the HBA lock it allocates a device slot, links it to libsas, determines the local or expander-attached PHY, initializes a completion pointer, and sends `reg_dev_req`. It drops the lock before waiting for the registration completion. On device removal, `pm8001_dev_gone_notify` waits for outstanding `running_req` to drain by issuing `sas_execute_internal_abort_dev`, sends `dereg_dev_req`, clears direct local PHY attachment, frees the slot, and clears the libsas private pointer.

PHY control first rejects operations when firmware is in fatal-error state. Link-rate set, hard reset, and link reset start a disabled PHY before issuing the control operation. Disable synthesizes a libsas disconnect/loss-of-signal event when the PHY was linked, then sends `phy_stop_req`. Event reads lock the HBA, perform BAR4 window shifting for SPC, read counter registers from logical BAR2, restore BAR4 for SPC, and return.

Error recovery branches by protocol and chip. `pm8001_abort_task` marks the task aborted under the task state lock and installs a stack `sas_task_slow` completion if none exists. SSP uses `sas_abort_task` plus an internal abort. SATA/STP on `chip_8006` performs a multi-step recovery: set device state to recovery, hard reset the PHY, wait for PHY and port reset completions, abort all device tasks, wait for the target task's slow completion, and set device state back to operational. Other SATA/STP and SMP cases issue firmware/libsas internal aborts, with `ccb->task = NULL` for non-8006 SATA/STP to avoid racing a later completion against libsas task lifetime.

Open-reject retry handling walks all active CCBs while holding the HBA lock, optionally filters by task or device, forces task status to `SAS_OPEN_REJECT` with `SAS_OREJ_RSVD_RETRY`, decrements `running_req`, marks the task done, frees the CCB, and calls `task_done` outside the HBA lock unless the task is already aborted.

## State and Persistence Behavior

This file manages volatile runtime state only. The key state objects are:

- `task->lldd_task`, which points to a live `pm8001_ccb_info` while firmware owns the task.
- `pm8001_ccb_info`, which records task, device, tag, SG element count, PRD buffer, firmware-control context, and open-retry flag.
- `pm8001_device`, which records libsas domain device, firmware `device_id`, local/expander attached PHY, discovery and set-device-state completions, and `running_req`.
- `pm8001_phy`, which stores link state, completion pointers, reset completion/status, and local SAS PHY linkage.
- `pm8001_ha->rsvd_tags`, `devices[]`, `ccb_info[]`, and host-wide lock/bitmap lock.

Device slots are reused by zeroing and resetting `dev_type` to `SAS_PHY_UNUSED` and `device_id` to `PM8001_MAX_DEVICES`. CCB slots are considered active when `ccb_tag != PM8001_INVALID_TAG`; this convention is explicitly used by `pm8001_open_reject_retry` and pending-command diagnostics.

The only persistence-like interaction is firmware registration state. `pm8001_dev_found_notify` creates firmware-visible device registration and receives a firmware device ID asynchronously. `pm8001_dev_gone_notify` deregisters that ID. Device state transitions such as `DS_IN_RECOVERY` and `DS_OPERATIONAL` are firmware state changes, but they are not stored persistently by this file.

Concurrency is managed with the HBA spinlock for CCB/device/port operations, `bitmap_lock` for reserved tag allocation, task state locks for libsas task flags, atomics for per-device running request counts, and completions for firmware responses. Several waits occur after dropping the HBA lock, but some completion pointers are stack variables stored in shared structures, so missed or late completions are lifetime-sensitive.

## Dependencies and Integration Points

The file depends on libsas for task/domain/PHY abstractions and error recovery helpers, libata for STP/SATA queued command metadata and NCQ tags, DMA mapping APIs for SG lists, and PM8001 hardware dispatch functions for actual firmware IOMB construction and control commands.

Major dispatch dependencies are `smp_req`, `sata_req`, `ssp_io_req`, `ssp_tm_req`, `task_abort`, `phy_start_req`, `phy_stop_req`, `phy_ctl_req`, `reg_dev_req`, `dereg_dev_req`, `set_dev_state_req`, `hw_event_ack_req`, `fatal_errors`, and the BAR4 shift helpers for PHY counters. MPI response handlers elsewhere must complete `dcompletion`, `setds_completion`, `enable_completion`, `reset_completion`, and task slow completions for these paths to make progress.

This file is registered with libsas through `pm8001_transport_ops` in `pm8001_init.c`. Its prototypes and shared structures live in `pm8001_sas.h`. It also emits `pm80xx_tracepoints.h` trace events for ATA request completion. Hardware-specific files consume CCB state and PRD buffers prepared here when building inbound IOMBs.

## Risks and Edge Cases

Task lifetime races are the main risk. The code deliberately clears `ccb->task` for some abort paths to avoid completions touching a task after libsas may free it. Any new completion path must honor NULL `ccb->task` and the `SAS_TASK_STATE_ABORTED`/`DONE` flags, or it can double-complete or dereference freed tasks.

The use of stack completions stored in `pm8001_device` and `pm8001_phy` fields is safe only if firmware response handlers complete before the function returns or if timeout paths clear the pointer. Some paths wait without timeout (`pm8001_dev_found_notify`, `pm8001_lu_reset` set-device-state wait, `pm8001_setds_completion`, PHY starts in scan) and can hang if firmware does not respond.

`pm8001_dev_gone_notify` waits in a loop until `running_req` becomes zero after an internal abort. If completions are lost or `running_req` accounting becomes unbalanced, removal can stall. `pm8001_open_reject_retry` decrements `running_req` while walking CCBs, so it must stay consistent with every CCB free and completion path.

The device allocator scans for `SAS_PHY_UNUSED` without its own lock; callers currently hold the HBA lock in discovery. Future callers must preserve that locking rule. `pm8001_find_dev` scans by firmware `device_id` and logs failure, so duplicate or stale device IDs would return the first match.

`pm8001_phy_control(PHY_FUNC_GET_EVENTS)` reads fixed register offsets with BAR4 window manipulation for SPC. Incorrect chip detection or concurrent BAR4 users could corrupt register access if not protected by `pm8001_ha->lock`.

For direct-attached SATA device-not-present paths, `pm8001_queue_command` temporarily drops the HBA lock before calling `task_done` and then reacquires it. That avoids callback-under-lock behavior for ATA, but makes this branch sensitive to task and device state changes while unlocked.

## Test Signals

Data-path validation should cover SSP, SMP, SATA, STP, NCQ, and internal abort submission. Useful checks are correct CCB tag assignment for request-backed and reserved-tag commands, SG DMA map/unmap balance, `task->lldd_task` cleanup, `running_req` increments/decrements, and command completion tracepoints.

Discovery tests should exercise direct SAS, direct SATA, and expander-attached devices, including failure of `sas_find_attached_phy_id`, registration completion, deregistration, and removal with outstanding I/O. Hotplug and expander topology changes are especially relevant because they stress device slot reuse and local-vs-expander PHY handling.

Error recovery tests should cover SSP abort/query/LU reset, SATA/STP abort on `chip_8006` and non-8006 chips, I_T nexus reset/event handling for SATA and SSP, open-reject retry by task and by device, and controller fatal-error short-circuiting. Timeout/failure injection for PHY reset, port reset, internal abort, and set-device-state completions would expose hang and stale-pointer risks.

PHY-control tests should cover link-rate changes from disabled and enabled states, hard/link reset, disable notifications, spinup-hold release, and event counter reads on SPC and non-SPC chips. Lockdep, KASAN, DMA API debug, and tracing are appropriate because this file combines spinlocks, atomics, completions, task callbacks, and DMA mappings.
