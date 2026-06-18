# subset-b-005281 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_init.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_init.c

## Purpose
`sas_init.c` is the libsas transport initialization and host-adapter control glue. It allocates the core task and event caches, registers and unregisters SAS HAs, binds libsas callbacks into the SCSI SAS transport template, exposes transport operations for phy reset/enable/link-rate/error counters, and coordinates HA suspend/resume with libsas workqueues and SCSI request blocking.

## Important APIs, types, and functions
- `sas_alloc_task`, `sas_alloc_slow_task`, and `sas_free_task` allocate libsas `struct sas_task` objects from `sas_task_cache`; slow tasks additionally allocate `struct sas_task_slow`, initialize a timer and completion, and are used by internal TMF paths in `sas_scsi_host.c`.
- `sas_hash_addr` computes the 24-bit SAS address hash with polynomial `0x00DB2777` and stores it in `sas_ha->hashed_sas_addr`.
- `sas_register_ha` initializes `sas_ha_struct` locks, queues, lists, state flags, event threshold, phys, ports, and ordered event/discovery workqueues.
- `sas_unregister_ha` disables event ingress, unregisters ports, drains pending work, and destroys discovery/event workqueues.
- `transport_sas_phy_reset`, `sas_phy_enable`, `sas_phy_reset`, and `sas_set_phy_speed` implement SAS transport callbacks by dispatching either to LLDD `lldd_control_phy` for local phys or SMP helper paths for expander phys.
- `sas_try_ata_reset` routes non-hard-reset SATA links through libata EH when a probed SATA `domain_device` is attached.
- `sas_prep_resume_ha`, `sas_resume_ha`, `sas_resume_ha_no_sync`, and `sas_suspend_ha` coordinate host power-state transitions, stale event cleanup, request blocking/unblocking, suspended-phy timeout handling, deferred work replay, and expander broadcast revalidation.
- `queue_phy_reset` and `queue_phy_enable` run user-requested transport operations in libsas workqueue context under runtime PM and `sas_phy_data.event_lock`.
- `sas_domain_attach_transport` creates the SAS transport template, stores the LLDD `sas_domain_function_template`, enables a transport workqueue, and installs `sas_scsi_recover_host` as the EH strategy.
- `sas_alloc_event` and `sas_free_event` manage event cache entries and per-phy event throttling. Bursty event production can schedule `PHYE_SHUTDOWN` or refuse allocation when LLDD phy control is unavailable.

## Control flow and state
HA registration follows an unwind-safe sequence: initialize locks/lists and set `SAS_HA_REGISTERED`, register phys, register ports, allocate `event_q`, allocate `disco_q`, then initialize EH queues. Failure destroys only the resources already acquired. Unregistration clears `SAS_HA_REGISTERED` under `sas_ha->lock`, drains work under `drain_mutex`, unregisters ports, drains again, and finally destroys workqueues.

Transport phy operations split on `scsi_is_sas_phy_local()`. Local phys retrieve `asd_sas_phy` from `sas_ha->sas_phy[phy->number]` and call LLDD control hooks. Remote expander phys resolve `sas_rphy` to `domain_device` and use SMP helpers. Link reset paths prefer libata-managed reset for SATA devices when the operation is not a hard reset.

Suspend clears event acceptance, blocks SCSI requests, emits `DISCE_SUSPEND` on every port, and drains suspend work while unregistered. Resume marks the HA registered and resuming, clears stale `attached_sas_addr` and frame data, waits up to 25 seconds for suspended phys, emits `PHYE_RESUME_TIMEOUT` for late phys, unblocks SCSI, optionally drains work, clears `SAS_HA_RESUMING`, queues deferred work, and broadcasts revalidation to expander ports.

## State and persistence behavior
State is in kernel memory only: kmem caches, `sas_ha_struct` flags/lists/workqueues, `asd_sas_phy` frame/event counters, and sysfs-visible `event_thres`. There is no disk persistence. `phy_event_threshold_store` updates `sas_ha->event_thres` from sysfs and clamps values below 32. Runtime PM references are taken around queued user phy operations.

## Dependencies and integration points
This file depends on the SCSI transport SAS layer (`sas_attach_transport`, `sas_phy_*`, `sas_port_*`), libata integration (`sas_ata_schedule_reset`, `sas_ata_wait_eh`), SMP helpers in libsas discovery code, LLDD callbacks in `sas_domain_function_template`, and shared declarations in `sas_internal.h`. It exports symbols used by low-level SAS drivers and other libsas modules.

## Risks and edge cases
- Event throttling depends on balanced `sas_alloc_event`/`sas_free_event`; leaks keep `event_nr` elevated and can trigger unnecessary phy shutdown.
- `queue_phy_reset` and `queue_phy_enable` assume `phy->hostdata` was initialized by `sas_phy_setup`; missing setup returns `-ENOMEM`.
- SATA reset routing requires a successfully probed `domain_device`; otherwise reset falls back to SAS/SMP control.
- Resume timeout handling intentionally races with late LLDD resume events and rechecks `phy->suspended` in the event worker.
- `sas_set_phy_speed` mutates the caller-provided link-rate structure to hardware min/max bounds before dispatching.

## Test signals
- Module load/unload should create and destroy `sas_task` and `asd_sas_event` caches without leaks.
- HA register failure injection should unwind phys, ports, and workqueues cleanly.
- Sysfs phy reset/enable paths should run in libsas workqueue context and return LLDD/SMP errors.
- SATA link reset should exercise libata EH rather than direct LLDD reset for non-hard resets.
- Suspend/resume tests should show request blocking, deferred work replay, timeout event emission, and expander broadcast revalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_internal.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_internal.h

## Purpose
`sas_internal.h` is the private coordination header for libsas implementation files. It centralizes shared prototypes, task-to-SCSI-command helpers, per-phy transport callback state, device/rphy helper inlines, event dispatch declarations, and conditional SATA stubs.

## Important APIs, types, and functions
- `TO_SAS_TASK` and `ASSIGN_SAS_TASK` store and retrieve `struct sas_task *` through `scsi_cmnd.host_scribble`, tying SCSI command lifetime to libsas task lifetime.
- `struct sas_phy_data` is per-transport-phy hostdata used by `sas_init.c` to queue reset and enable operations onto libsas workqueues, carrying the target `struct sas_phy`, an `event_lock`, requested operation parameters, result slots, and `sas_work` items.
- Discovery, domain, and device prototypes include `sas_discover_root_expander`, `sas_ex_revalidate_domain`, `sas_unregister_domain_devices`, `sas_init_disc`, `sas_discover_event`, `sas_init_dev`, and `sas_unregister_dev`.
- Registration prototypes expose `sas_register_phys`, `sas_unregister_phys`, `sas_register_ports`, and `sas_unregister_ports`.
- Event plumbing includes `sas_alloc_event`, `sas_free_event`, `sas_phy_event_fns`, `sas_port_event_fns`, `sas_queue_work`, `__sas_drain_work`, and individual port-event worker prototypes.
- SMP and expander helpers include `sas_smp_handler`, `sas_smp_phy_control`, `sas_smp_get_phy_events`, `sas_ex_to_ata`, `sas_ex_phy_discover`, and attached-device lookup helpers.
- `sas_fill_in_rphy` copies libsas `domain_device` identity into transport `sas_rphy` identity, mapping SATA-like end devices to `SAS_END_DEVICE`.
- `sas_phy_set_target` updates a local transport phy identity to reflect the attached target or clears it to unused.
- `sas_alloc_device` initializes a zeroed `domain_device` with sibling/discovery list heads, a kref, and `done_lock`; `sas_put_device` releases via `sas_free_device`.
- The `CONFIG_SCSI_SAS_ATA` section declares real SATA integration or provides no-op/failing stubs with a once-only notice when SATA support is disabled.

## Control flow and state
The header defines the internal contracts that allow libsas files to call across module boundaries without exposing these helpers as public UAPI. Most control-flow coupling is asynchronous: discovery and port/phy events are queued as `sas_work`; SCSI EH paths call into recovery and task-management helpers; transport sysfs operations use `struct sas_phy_data` to serialize workqueue execution.

## State and persistence behavior
No persistent storage is declared. State is held in kernel structures, lists, krefs, spinlocks, mutexes, and SCSI transport objects. `host_scribble` is a transient pointer slot and must be cleared when tasks complete or are transferred to EH ownership.

## Dependencies and integration points
The header depends on SCSI core headers, `scsi_transport_sas`, public `<scsi/libsas.h>`, libata SAS headers, and runtime PM. It is included by libsas implementation files and indirectly binds them to LLDD-provided `sas_domain_function_template` callbacks.

## Risks and edge cases
- `TO_SAS_TASK`/`ASSIGN_SAS_TASK` require exclusive ownership of `host_scribble`; other SCSI host code must not reuse it.
- Inline address matching casts SAS address bytes through `SAS_ADDR`; all callers rely on correctly populated 8-byte addresses.
- `sas_fail_probe` unregisters devices directly after logging, so callers must not continue using the `domain_device` without holding references.
- SATA-disabled stubs return success for some lifecycle hooks but fail discovery/add-device operations, so test matrices must include `CONFIG_SCSI_SAS_ATA=n`.

## Test signals
- Build coverage with and without `CONFIG_SCSI_SAS_ATA` and `CONFIG_SCSI_SAS_HOST_SMP`.
- Static analysis should verify every `ASSIGN_SAS_TASK(cmd, task)` has a clear/free path.
- Discovery tests should confirm rphy identity fields and phy target fields match domain-device type/protocol transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_phy.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_phy.c

## Purpose
`sas_phy.c` implements libsas phy event workers and registration of local phys with the SCSI SAS transport class. It translates hardware/link events into port deformation, hard reset, spinup-hold release, resume-timeout cleanup, or phy shutdown.

## Important APIs, types, and functions
- `sas_phye_loss_of_signal` clears the phy error counter and deforms the port as gone.
- `sas_phye_oob_done` clears OOB error state after successful out-of-band negotiation.
- `sas_phye_oob_error` deforms the current port, then for enabled standalone phys attempts two hard resets and disables the phy on the third error if LLDD phy control is available.
- `sas_phye_spinup_hold` releases spinup hold via `PHY_FUNC_RELEASE_SPINUP_HOLD`.
- `sas_phye_resume_timeout` cancels itself if the LLDD already cleared suspension; otherwise it clears `suspended` and deforms the port.
- `sas_phye_shutdown` disables an enabled phy through `PHY_FUNC_DISABLE`, logs LLDD failures, and clears `in_shutdown`.
- `sas_register_phys` initializes every `asd_sas_phy`, allocates a transport `sas_phy`, populates identify and link-rate fields, and adds it to the transport class.
- `sas_unregister_phys` deletes and frees each transport phy.
- `sas_phy_event_fns` maps `PHYE_*` enum values to the corresponding work functions.

## Control flow and state
Phy event workers receive `struct asd_sas_event` through `to_asd_sas_event(work)` and operate on `event->phy`. Port membership changes are delegated to `sas_deform_port`. Error escalation is local to `asd_sas_phy.error`: OOB errors increment the counter only when no port is formed, the phy is enabled, and LLDD control exists; the third error disables the phy and resets the counter.

Registration loops over `sas_ha->num_phys`. Each `asd_sas_phy` is linked to its HA, event counter, frame locks, primitive lock, port list node, and transport object. If allocation or `sas_phy_add` fails, the function rolls back previously added phys by deleting and freeing their transport objects.

## State and persistence behavior
Phy state is transient kernel state: `error`, `event_nr`, `in_shutdown`, `enabled`, `suspended`, frame data, `port`, and `phy->phy` transport pointer. Link-rate fields are initialized to `SAS_LINK_RATE_UNKNOWN` and later updated by LLDD/discovery paths. No durable persistence is performed.

## Dependencies and integration points
This file integrates with `sas_port.c` through `sas_deform_port`, with `sas_init.c` event allocation and thresholding, with the SCSI SAS transport through `sas_phy_alloc/add/delete/free`, and with LLDD callbacks through `lldd_control_phy`.

## Risks and edge cases
- `sas_phye_oob_error` assumes repeated OOB errors on a standalone enabled phy indicate a bad link and can disable it; overly aggressive LLDD event reporting can take a phy offline.
- Resume timeout has an intentional race with late resume completion; it rechecks `phy->suspended` before deformation.
- Registration rollback must stay in sync with initialization order to avoid transport object leaks.
- `sas_unregister_phys` assumes all phys were registered; partial-registration error paths must not call it on uninitialized entries.

## Test signals
- Inject `PHYE_OOB_ERROR` repeatedly and verify hard reset, hard reset, disable ordering.
- Exercise `PHYE_RESUME_TIMEOUT` both before and after LLDD clears `suspended`.
- Fail `sas_phy_alloc` or `sas_phy_add` mid-registration and check rollback.
- Confirm transport class shows expected local phy identity and unknown initial link rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_port.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_port.c

## Purpose
`sas_port.c` manages libsas port formation, wide-port membership, port deformation, resume handling, port event workers, and per-HA port initialization. It is the topology bridge between per-phy link events and domain discovery.

## Important APIs, types, and functions
- `phy_is_wideport_member` checks whether a phy belongs in an existing port by matching attached SAS address and, when `strict_wide_ports` is set, the local SAS address.
- `sas_resume_port` notifies the LLDD that the port is formed, marks a suspended port active once, re-notifies all known devices as found, resets expander change counters to force full revalidation, and emits `DISCE_RESUME`.
- `sas_form_port_add_phy` links a phy to a port, updates target identity, `port->num_phys`, `phy_mask`, SAS addresses, protocols, OOB mode, and maximum link rate.
- `sas_form_port` either validates an existing port, resumes a suspended phy, attaches the phy to a matching wide port, or allocates a free port slot and creates the transport `sas_port`. It notifies the LLDD, starts domain discovery, and schedules expander revalidation when a port device already exists.
- `sas_deform_port` removes a phy from a port, unregisters/destructs devices if the last phy is gone, updates transport port membership, notifies LLDD deformation, clears port state when empty, and schedules expander revalidation for remaining wide ports.
- Event workers map port events to formation, revalidation, or deformation: `sas_porte_bytes_dmaed`, `sas_porte_broadcast_rcvd`, `sas_porte_link_reset_err`, `sas_porte_timer_event`, and `sas_porte_hard_reset`.
- `sas_register_ports` initializes all HA ports and discovery state; `sas_unregister_ports` deforms any still-attached phys.

## Control flow and state
On `PORTE_BYTES_DMAED`, libsas calls `sas_form_port`. Existing phy membership is checked first: nonmatching membership triggers deformation, suspended matching membership resumes the port and wakes the HA EH wait queue, and duplicate active membership is ignored. New membership is serialized by `sas_ha->phy_port_lock` plus each port's `phy_list_lock`. Wide-port lookup scans existing nonempty ports before claiming an empty port slot.

On deformation, device topology is torn down before removing the phy from port lists. If the port loses its last phy, all domain devices are unregistered/destructed and the transport port is deleted. If other phys remain, only the phy is removed and device-to-phy association is refreshed. Discovery queue flushes make event effects visible before returning.

## State and persistence behavior
Port state is held in `asd_sas_port`: `sas_addr`, `attached_sas_addr`, protocol fields, `oob_mode`, `linkrate`, `num_phys`, `phy_mask`, `phy_list`, `dev_list`, discovery lists, and transport `sas_port *`. Device `pathways` tracks wide-port path count. There is no persistence beyond in-memory kernel topology and SCSI transport objects.

## Dependencies and integration points
This file depends on SCSI SAS transport port APIs, LLDD callbacks `lldd_port_formed` and `lldd_port_deformed`, discovery helpers in libsas, device unregister/destruct helpers, expander revalidation state, and phy identity helpers from `sas_internal.h`.

## Risks and edge cases
- Port/phy locking order is critical: HA `phy_port_lock` wraps per-port `phy_list_lock` during formation and deformation.
- `sas_form_port` uses `BUG_ON(!port->port)` after `sas_port_alloc`, so allocation failure is fatal.
- Wide-port matching behavior changes when `strict_wide_ports` is enabled; mismatched local addresses prevent aggregation.
- `sas_porte_broadcast_rcvd` calls `sas_discover_event(phy->port, ...)` before checking `phy->port`; callers should ensure broadcast events have a live port.
- Deformation decrements `dev->pathways` when a port device exists; inconsistent wide-port accounting can affect path management.

## Test signals
- Single-phy link-up should allocate a transport port, add the phy, and emit domain discovery.
- Multiple phys with the same attached SAS address should form a wide port and update `pathways`/`phy_mask`.
- Loss of one wide-port phy should remove only that phy and schedule expander revalidation.
- Loss of the last phy should unregister/destruct devices and delete the transport port.
- Resume tests should re-notify LLDD devices and force expander change-count revalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_scsi_host.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_scsi_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_task.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_task.c

## Purpose
`sas_task.c` provides the SSP response parser for libsas tasks. It converts an SSP response IU into libsas `task_status_struct` fields consumed by `sas_scsi_host.c` completion and EH paths.

## Important APIs, types, and functions
- `sas_ssp_task_response(struct device *dev, struct sas_task *task, struct ssp_response_iu *iu)` sets `task->task_status.resp` to `SAS_TASK_COMPLETE` and interprets `iu->datapres`.
- `SAS_DATAPRES_NO_DATA` copies the IU status directly.
- `SAS_DATAPRES_RESPONSE_DATA` takes the task status from `iu->resp_data[3]`.
- `SAS_DATAPRES_SENSE_DATA` marks `SAS_SAM_STAT_CHECK_CONDITION`, bounds `buf_valid_size` by `SAS_STATUS_BUF_SIZE` and big-endian `sense_data_len`, copies sense bytes, and warns if IU status was not `SAM_STAT_CHECK_CONDITION`.
- Unknown/corrupt `datapres` is treated as check condition.

## Control flow and state
The parser is synchronous and mutates only the provided task's `task_status`. It does not complete the task itself. LLDD completion code calls it after receiving an SSP response IU, and later completion logic maps the filled task status to SCSI result and sense data.

## State and persistence behavior
No persistent state. The only state transition is filling `task->task_status.resp`, `stat`, `buf_valid_size`, and `buf`.

## Dependencies and integration points
The function depends on SAS protocol structures from `<scsi/sas.h>` and `<scsi/libsas.h>`, endian conversion for `sense_data_len`, and caller-provided device/task context for warnings and SAS address logging. It is exported for LLDD users.

## Risks and edge cases
- Response-data status is read from `resp_data[3]`, so callers must provide a valid IU with adequate response data.
- Sense copy is bounded by libsas buffer size but assumes the IU sense-data area is valid for the reported length as provided by the LLDD.
- Treating unknown `datapres` as check condition is conservative but may hide malformed-frame diagnosis unless paired with LLDD logging.

## Test signals
- Feed no-data, response-data, sense-data, and invalid `datapres` IUs and verify task status fields.
- Sense-data length greater than `SAS_STATUS_BUF_SIZE` should truncate safely.
- Non-check-condition IU status with sense data should emit a warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/Makefile

## Purpose
This Makefile builds the Broadcom/Emulex `lpfc` Fibre Channel HBA driver as a kernel object when `CONFIG_SCSI_LPFC` is enabled. It also supports optional GCOV instrumentation and treating warnings as errors.

## Important APIs, types, and functions
- `ccflags-$(GCOV)` adds `-fprofile-arcs -ftest-coverage` and disables optimization with `-O0` for coverage builds.
- `ifdef WARNINGS_BECOME_ERRORS` adds `-Werror` to `ccflags-y`.
- `obj-$(CONFIG_SCSI_LPFC) := lpfc.o` ties the driver object to kernel configuration.
- `lpfc-objs` composes the module from `lpfc_mem.o`, `lpfc_sli.o`, `lpfc_ct.o`, `lpfc_els.o`, `lpfc_hbadisc.o`, `lpfc_init.o`, `lpfc_mbox.o`, `lpfc_nportdisc.o`, `lpfc_scsi.o`, `lpfc_attr.o`, `lpfc_vport.o`, `lpfc_debugfs.o`, `lpfc_bsg.o`, `lpfc_nvme.o`, `lpfc_nvmet.o`, and `lpfc_vmid.o`.

## Control flow and state
There is no runtime control flow. Build-time configuration decides whether the module is compiled, whether GCOV flags are applied, and whether warnings fail the build.

## State and persistence behavior
No runtime state or persistence. Build artifacts are produced by the kernel build system.

## Dependencies and integration points
The Makefile depends on Kbuild variables (`obj-*`, `<module>-objs`, `ccflags-*`) and the `CONFIG_SCSI_LPFC` kernel config option. The object list corresponds to lpfc subsystems: memory, SLI, CT/ELS discovery, mailbox, SCSI, sysfs attributes, vports, debugfs, BSG, NVMe initiator/target, and VMID.

## Risks and edge cases
- Adding source files without updating `lpfc-objs` leaves code unbuilt.
- `WARNINGS_BECOME_ERRORS` can expose compiler-version-dependent warnings.
- GCOV builds use `-O0`, which can change timing and code generation compared with production builds.

## Test signals
- `CONFIG_SCSI_LPFC=m` should produce `lpfc.ko` with all listed objects linked.
- GCOV-enabled builds should include coverage flags.
- Warning-as-error CI should be run across supported compiler versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc.h

## Purpose
`lpfc.h` is the central private header for the Broadcom/Emulex lpfc Fibre Channel driver. It defines driver-wide limits, feature flags, Fibre Channel and HBA state enums, DMA and queue buffer types, vport and HBA state containers, congestion-management structures, VMID metadata, RAS/debug support, and SLI revision abstraction helpers.

## Important APIs, types, and functions
- Global limits cover targets, discovery concurrency, queue depth, S/G segment counts, NVMe segment counts, IOCB pool size, link speeds, MSI-X vectors, mailbox wait modes, heartbeat/error polling intervals, and vport naming.
- DMA/buffer types include `struct lpfc_dmabuf`, `struct lpfc_nvmet_ctxbuf`, `struct lpfc_dma_pool`, `struct hbq_dmabuf`, and `struct rqb_dmabuf`.
- `lpfc_vpd_t` stores vital product data, firmware revisions, names, and SLI3 feature bits with endian-specific bitfields.
- `struct lpfc_stats` tracks ELS, frame, link, FCP, and error counters.
- VMID structures include `struct lpfc_vmid`, `union lpfc_vmid_io_tag`, `struct lpfc_vmid_context`, and priority range/info structures.
- State enums include `enum discovery_state`, `enum hba_state`, `enum lpfc_hba_flag`, `enum lpfc_fc_flag`, `enum lpfc_load_flag`, interrupt modes, RAS states, mailbox buffer states, and HBA bit flags.
- Congestion management types include `struct lpfc_cgn_param`, `struct lpfc_cgn_ts`, `struct lpfc_cgn_info`, `struct lpfc_cgn_stat`, `struct lpfc_cgn_acqe_stat`, `struct rx_info_entry`, and `struct lpfc_rx_info_monitor`.
- `struct lpfc_vport` represents a physical or NPIV/Fabric vport with FC identity, discovery lists/counters, RSCN state, timers, tunables, VMID table, debugfs entries, receive buffers, FDMI masks, and NVMe local port state.
- `struct lpfc_hba` is the main adapter object. It contains function pointers for SCSI buffer handling, IOCB/WQE issue/prep, mailbox issue, slow-ring processing, board/link operations, block-guard prep, SLI4 and SLI state, workqueues/timers, PCI/MMIO mappings, mailbox/HBQ resources, VPD strings, SCSI/IOCB pools, RRQ state, DMA/mempools, port/vport allocation, fabric scheduler state, debugfs/error-injection state, heartbeat/RAS/CMF/congestion/FPIN state, CPU hotplug/polling hooks, and debug log storage.
- Inline helpers include `lpfc_shost_from_vport`, `lpfc_set_loopback_flag`, `lpfc_is_link_up`, `lpfc_worker_wake_up`, `lpfc_readl`, `lpfc_sli_read_hs`, `lpfc_phba_elsring`, CPU selection helpers, `lpfc_sli4_mod_hba_eq_delay`, `DECLARE_ENUM2STR_LOOKUP`, `lpfc_is_vmid_enabled`, and SLI2/3 vs SLI4 job accessors such as `get_job_ulpstatus`, `get_job_word4`, `get_job_cmnd`, `get_job_ulpcontext`, `get_job_rcvoxid`, `get_job_data_placed`, `get_job_abtsiotag`, and `get_job_els_rsp64_did`.

## Control flow and state
The header itself has little control flow, but its data model drives the driver. `struct lpfc_hba` owns adapter-level queues, memory pools, MMIO mappings, worker state, timers, SLI revision dispatch, PCI identity, feature configuration, congestion state, and port list. `struct lpfc_vport` owns per-NPort discovery and protocol state and points back to its HBA. Function pointers inside `lpfc_hba` abstract SLI generation differences and allow common code to call revision-specific implementations.

Inline helpers encode common control decisions: link-up state is true for `LPFC_LINK_UP`, `LPFC_CLEAR_LA`, or `LPFC_HBA_READY`; worker wake-up sets `LPFC_DATA_READY` and wakes `work_waitq`; MMIO reads returning `0xffffffff` are treated as `-EIO`; `lpfc_sli_read_hs` snapshots host status/work status and clears error attention; `lpfc_phba_elsring` returns the correct ELS ring for SLI2/3 or SLI4; job accessors select IOCB fields for SLI2/3 or WQE/WCQE fields for SLI4.

## State and persistence behavior
Most state is volatile driver runtime state in `lpfc_hba` and `lpfc_vport`: discovery state, FC IDs, flags, lists, timers, queues, DMA pools, mempools, config parameters, congestion counters, VMID tables, debug traces, and MMIO pointers. Some fields mirror persistent or firmware-provided information, including VPD, firmware names/revisions, flash congestion parameters (`LPFC_CFG_PARAM_MAGIC_NUM`, `LPFC_PORT_CFG_NAME`), serial/model strings, WWNN/WWPN, and RAS/congestion buffers registered with firmware. The header defines structures for these persisted/firmware interfaces but does not itself perform I/O.

## Dependencies and integration points
`lpfc.h` integrates with the SCSI host model, PCI/MMIO, DMA pools, mempools, timers, workqueues, debugfs, Fibre Channel transport, NVMe-FC/NVMET, CPU hotplug, firmware mailbox/SLI definitions from other lpfc headers, and kernel congestion/FPIN concepts. The Makefile builds many C files that include this header and fill in the function-pointer implementations.

## Risks and edge cases
- `struct lpfc_hba` is very broad; changes can affect SCSI, NVMe, discovery, interrupt handling, mailbox, firmware logging, congestion management, and vports at once.
- Endian-specific VPD bitfields must match firmware layout on both big- and little-endian builds.
- MMIO helper `lpfc_readl` treats all-ones as device error; callers must propagate `-EIO` to avoid using invalid register snapshots.
- SLI revision helpers must be kept aligned with IOCB/WQE layout changes; wrong field selection can corrupt completions or aborts.
- Many counters and lists are protected by different locks (`hbalock`, `port_list_lock`, VMID lock, debug/RAS locks, SCSI buffer locks). Locking rules must be preserved outside this header.
- Conditional debugfs and NVMe feature macros change struct contents and defaults, so ABI assumptions inside the driver must be configuration-aware.

## Test signals
- Build with SLI3/SLI4, debugfs on/off, NVMe-FC enabled/disabled, and big-endian bitfield coverage where available.
- Link-state and worker wake-up paths should update flags and wake waiters as expected.
- Simulated MMIO all-ones reads should force `-EIO` and error-attention handling should snapshot/clear registers.
- SLI4 and SLI3 completion accessor unit tests or trace validation should return equivalent semantic fields.
- VMID, CMF/congestion, RAS logging, and vport discovery tests should verify counters, timers, and config bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc.h -->
