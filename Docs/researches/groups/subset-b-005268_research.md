# Research: subset-b-005268

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvfc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvfc.c

## Purpose
`ibmvfc.c` implements the IBM Power Virtual Fibre Channel client driver for Linux SCSI. It binds to VIO devices with type/name `fcp` / `IBM,vfc-client`, registers an FC transport and SCSI host, negotiates NPIV login with the VIOS partner, discovers FC targets, exposes them as FC remote ports, queues SCSI FCP I/O over CRQ or sub-CRQ channels, and handles link/migration/error-recovery paths.

The file is the active implementation companion to `ibmvfc.h`: it owns module parameters, host and target state machines, CRQ/SCRQ allocation and interrupt handling, SCSI queuecommand and EH callbacks, BSG passthrough, sysfs attributes, memory allocation, VIO probe/remove, and module init/exit.

## Important APIs, Types, and Entry Points
The module-level knobs are `mq`, `scsi_host_queues`, `scsi_hw_channels`, `mig_channels_only`, `mig_no_less_channels`, `init_timeout`, `default_timeout`, `max_requests`, `max_sectors`, `scsi_qdepth`, `max_lun`, `max_targets`, `disc_threads`, `debug`, `log_level`, and `cls3_error`. They feed queue sizing, discovery fanout, recovery timeouts, multiqueue channel negotiation, and FC class 3 retry behavior.

The SCSI host template `driver_template` wires the driver into the midlayer through `ibmvfc_queuecommand`, `ibmvfc_eh_abort_handler`, `ibmvfc_eh_device_reset_handler`, `ibmvfc_eh_target_reset_handler`, `ibmvfc_eh_host_reset_handler`, `ibmvfc_sdev_init`, `ibmvfc_sdev_configure`, `ibmvfc_target_alloc`, `ibmvfc_scan_finished`, and `ibmvfc_change_queue_depth`.

The FC transport template `ibmvfc_transport_functions` publishes host and remote-port attributes and callbacks: `ibmvfc_get_host_port_state`, `ibmvfc_get_host_speed`, `ibmvfc_issue_fc_host_lip`, `ibmvfc_terminate_rport_io`, `ibmvfc_set_rport_dev_loss_tmo`, `ibmvfc_get_starget_node_name`, `ibmvfc_get_starget_port_name`, `ibmvfc_get_starget_port_id`, `ibmvfc_bsg_request`, and `ibmvfc_bsg_timeout`.

VIO integration is through `ibmvfc_driver`, with `ibmvfc_probe`, `ibmvfc_remove`, `ibmvfc_get_desired_dma`, and PM resume `ibmvfc_resume`. Module init checks `FW_FEATURE_VIO`, attaches the FC transport, and registers the VIO driver; module exit unregisters and releases the transport.

The main local data objects are `struct ibmvfc_host`, `struct ibmvfc_target`, `struct ibmvfc_queue`, `struct ibmvfc_event`, and the protocol IUs declared in `ibmvfc.h`. This file manipulates them primarily under `shost->host_lock`, per-queue `q_lock`, and per-queue event-list `l_lock`.

## Control Flow
Probe starts in `ibmvfc_probe`. It allocates a `Scsi_Host`, initializes `ibmvfc_host`, sizes hardware queues from module parameters and CPU count, allocates memory (`ibmvfc_alloc_mem`), starts the worker thread (`ibmvfc_work`), registers the CRQ (`ibmvfc_init_crq`), adds the SCSI host, creates the optional trace sysfs file, initializes sub-CRQs if multiqueue is enabled, adds the host to `ibmvfc_head`, sends CRQ init, and starts `scsi_scan_host`.

CRQ initialization is a handshake. `ibmvfc_send_crq_init` sends an init message; `ibmvfc_handle_crq` reacts to `IBMVFC_CRQ_INIT` and `IBMVFC_CRQ_INIT_COMPLETE` by sending init-complete and calling `ibmvfc_init_host`. Host initialization blocks SCSI requests, clears async queue state, schedules target cleanup or relogin after migration, sets `IBMVFC_INITIALIZING`, and dispatches `ibmvfc_npiv_login` through the worker state machine.

NPIV login is built by `ibmvfc_gather_partition_info` and `ibmvfc_set_login_info`, then sent as `IBMVFC_NPIV_LOGIN`. `ibmvfc_npiv_login_done` validates native FC support and usable command depth, updates FC host identity, supported classes, max sectors, and queue depth, then optionally performs channel enquiry/setup if VIOS advertises channel support. After login, the worker sends `IBMVFC_DISC_TARGETS`, allocates target objects from the discovery buffer, and progresses each target through implicit logout, PLOGI, PRLI, ADISC/query, and FC rport creation.

SCSI I/O enters at `ibmvfc_queuecommand`. It first checks the FC rport and host state, chooses a sub-CRQ by blk-mq hardware queue when channel mode is active or the base CRQ otherwise, allocates an event, initializes the FCP command IU with target WWPN/port ID/LUN/CDB/tag/correlation, maps DMA scatterlists, and sends the event. Completion comes back through CRQ/SCRQ interrupts, moves events to a done list, deletes timers, traces completion, decodes FCP status/sense/residuals, optionally schedules relogin for `PLOGI_REQUIRED`, unmaps DMA, calls `scsi_done`, and returns the event to its free list.

Interrupt flow is split by queue type. The base VIO IRQ calls `ibmvfc_interrupt`, disables interrupts, and schedules `ibmvfc_tasklet`, which drains async CRQ entries and base CRQ entries under host and queue locks. Multiqueue SCRQs use `ibmvfc_interrupt_mq`, which disables that SCRQ IRQ and drains it with `ibmvfc_drain_sub_crq`. Both CRQ handlers validate returned correlation tokens against the event pool and reject duplicate completions using the event `active` atomic.

The worker thread `ibmvfc_work` sleeps on `work_wait_q` until `ibmvfc_work_to_do` finds a host or target action. `ibmvfc_do_work` is the central host state machine. It handles reset/reenable, NPIV logout/login, query, target discovery/init/delete, rport deletion, reinit loops, and transition to `IBMVFC_ACTIVE` with `scsi_unblock_requests` and queued rport-add work.

## State and Persistence Behavior
The driver has no durable on-disk state. Persistence is in kernel memory for the lifetime of a VIO device: host state/action, target list, DMA buffers, queue pages, event pools, trace ring, login response, channel setup data, and per-target service parameters. Host state is represented by `IBMVFC_NO_CRQ`, `IBMVFC_INITIALIZING`, `IBMVFC_ACTIVE`, `IBMVFC_HALTED`, `IBMVFC_LINK_DOWN`, `IBMVFC_LINK_DEAD`, and `IBMVFC_HOST_OFFLINE`; host actions encode the pending worker step.

Target state is represented by `IBMVFC_TGT_ACTION_*`, with transitions guarded by `ibmvfc_set_tgt_action`. Targets carry WWPN, SCSI ID/port ID, FC service parameters, remote-port pointer, retry counters, move-login flags, cancel key, and a timer for ADISC cancellation. Krefs protect targets across async commands and rport-add work.

Event state is managed by event pools per queue. An event is free when on the queue free list with `free == 1` and `active == -1`; send moves it to the sent list and marks `active = 1`; response handling atomically transitions active toward completion and moves it to a done list; `ibmvfc_free_event` returns it to the free list and replenishes ordinary or reserved depth. Internal MADs use reserved events to preserve recovery/initialization capacity.

Trace state is a fixed-size ring of `IBMVFC_NUM_TRACE_ENTRIES` entries when `CONFIG_SCSI_IBMVFC_TRACE` is enabled, exposed as a binary sysfs file. Sysfs attributes expose live login response fields and mutable `log_level`/`nr_scsi_channels`; changing channel count resets the host.

## Dependencies and Integration Points
The file depends on Linux SCSI core, blk-mq tag helpers, FC transport, FC BSG, DMA mapping and DMA pools, VIO and pseries hypervisor calls, Open Firmware properties, interrupts, tasklets, kthreads, workqueues, timers, completions, mempools, and kernel logging/sysfs.

Hypervisor integration uses `H_REG_CRQ`, `H_FREE_CRQ`, `H_ENABLE_CRQ`, `H_SEND_CRQ`, `H_REG_SUB_CRQ`, `H_FREE_SUB_CRQ`, `H_SEND_SUB_CRQ`, and `H_VIOCTL` through `plpar_hcall*` helpers. VIO interrupt control is through `vio_enable_interrupts` and `vio_disable_interrupts`; sub-CRQ interrupts are mapped from hardware IRQ numbers with `irq_create_mapping`.

FC transport integration is substantial: login response fields populate `fc_host_*`, discovery creates `fc_rport` objects, target attribute callbacks read `ibmvfc_target`, async events post FC host events, and EH uses `fc_block_scsi_eh`, `fc_block_rport`, remote-port readiness checks, and `fc_remote_port_delete`/`rolechg`.

BSG passthrough maps user request/reply SG lists, serializes via `passthru_mutex`, can issue a temporary PLOGI for host CT requests, sends `IBMVFC_PASSTHRU`, and has a timeout path that sends `IBMVFC_TMF_MAD` using the passthrough cancel key.

## Error Handling and Recovery
Command status mapping is table-driven through `cmd_status`, `ibmvfc_get_err_index`, `ibmvfc_get_err_result`, and `ibmvfc_retry_cmd`. Completion code maps VIOS/fabric/FC/SCSI errors to SCSI result codes, logs according to per-entry and module log levels, copies sense data, handles residual underflow/overflow, and detects PLOGI-required relogin.

Host recovery includes graceful NPIV logout when possible (`__ibmvfc_reset_host`), hard CRQ reset when needed (`ibmvfc_hard_reset_host`), request purging (`ibmvfc_purge_requests`), CRQ reenable after partition migration (`ibmvfc_reenable_crq_queue`), and link-down/offline transitions. Transport events from `ibmvfc_handle_crq` detect partition migration, partner failure, and partner deregistration.

SCSI EH has separate paths for abort, LUN reset, target reset, and host reset. It first blocks against FC transport state, sends VIOS cancel/TMF commands when useful, waits for matching in-flight events to complete, and escalates to host reset or hard reset on timeout. Multiqueue cancellation sends per-SCRQ cancels only where matching events exist.

Async events drive discovery/recovery. Link up/resume and RSCN events schedule reset or reinit, link down/dead/halt blocks requests and deletes targets, ELS target events selectively delete or relogin matching targets, and adapter failure drives link-down recovery.

## Risks and Edge Cases
Concurrency risk is high. The driver mixes host lock, queue locks, event-list locks, tasklets, IRQ handlers, worker thread, workqueue, timers, completions, and SCSI EH callbacks. Regressions can produce double completion, leaked reserved events, stale target pointers, deadlocks, or I/O that never completes. The atomic `active`/`free` checks and event-pool validation are important safety barriers.

Channelized I/O adds migration and fallback complexity. The `do_enquiry`, `using_channels`, `desired_queues`, `active_queues`, and `vios_cookie` state must remain synchronized with CRQ reset/reenable and VIOS channel setup responses. Module options that forbid migration to fewer/no channels can change host availability after LPM.

The target discovery state machine has subtle rport lifetime cases. A target can be removed while rport add is in progress, an old SCSI ID can require move-login, fast-fail settings change whether outstanding I/O is expected to drain, and failed implicit logout can leave `LOGOUT_DELETED_RPORT` work for `terminate_rport_io`.

DMA and queue sizing are sensitive to module parameters and VIOS responses. `max_cmds` must exceed internal reserved requests; scatterlist extension buffers come from a DMA pool sized for `SG_ALL`; BSG rejects multi-segment request/reply payloads; and `max_sectors` is clamped only at module init for a minimum page-size-derived value.

Timeout behavior is intentionally escalatory. Internal command timers reset the host; ADISC has both an ADISC timer and a longer event timer to cover cancel failure; BSG timeout can reset the host when already aborting or inactive. Tests should account for these forced-reset side effects.

Several paths use `BUG_ON` for invariant violations in event state and worker wakeup interruption, so malformed queue state or unexpected sleeping/wakeup behavior is fatal in debug scenarios.

## Test Signals
Build-level signals include successful compilation for pseries/VIO configurations with and without `CONFIG_SCSI_IBMVFC_TRACE`, no sparse/endian warnings in protocol structure use, and no missing prototypes after SCSI/FC API changes.

Probe/init tests should cover CRQ register success, `H_CLOSED` partner-not-ready behavior, `H_RESOURCE` reset retry, IRQ registration failure unwind, memory allocation failure unwind, trace file create failure, multiqueue sub-CRQ registration failure fallback, and successful NPIV login to active state.

I/O tests should cover single-queue and multiqueue queuecommand, no-SG and multi-SG commands, tagged commands, residual underflow/overflow, sense data copy, PLOGI-required relogin, command timeout host reset, and queue full/host busy event exhaustion.

Discovery tests should exercise discover-targets success/failure, max target truncation, new target allocation, target already known by SCSI ID, WWPN moved to new SCSI ID, implicit logout failure, PLOGI/PRLI retry decisions, ADISC mismatch deletion, and FC rport add/delete races.

Recovery tests should cover abort, LUN reset, target reset, host reset, cancel failure statuses, waiting for matching ops across all SCRQs, FC fast-fail behavior, partition migration, partner deregister/failure, link up/down/dead/halt, RSCN, and BSG passthrough timeout cancellation.

Sysfs/transport tests should validate host attributes after login, mutable log level, channel-count write causing reset, host speed mapping, port state mapping, dev-loss timeout normalization, BSG ELS/CT passthrough, and trace binary read bounds when tracing is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvfc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvfc.h

## Purpose
`ibmvfc.h` defines the protocol constants, packed wire-format structures, state enums, and in-memory driver objects used by the IBM Power Virtual Fibre Channel client driver. It is the contract between `ibmvfc.c`, the Linux SCSI/FC subsystems, and the VIOS/hypervisor-facing message protocol.

The header covers driver defaults, module-parameter defaults, MAD opcodes/status values, NPIV login data, target discovery, PLOGI/PRLI/query/move-login/logout commands, task management, FCP command/response layouts, FC passthrough, channel enquiry/setup, CRQ/SCRQ formats, async events, event pools, queues, channel collections, host/target state machines, trace records, and logging/sysfs trace helper macros.

## Important APIs, Types, and Constants
Driver identity and defaults include `IBMVFC_NAME`, `IBMVFC_DRIVER_VERSION`, timeout constants, queue depth defaults, maximum targets/LUN/sectors, discovery thread limits, target mempool size, max commands per LUN, init retry limits, dev-loss timeout, class-3 retry default, and multiqueue defaults.

`IBMVFC_NUM_INTERNAL_REQ` reserves base-queue events for ERP, initialization, NPIV logout, BSG passthrough, and discovery; `IBMVFC_NUM_INTERNAL_SUBQ_REQ` reserves subqueue events for channelized cancel commands. These macros depend on the C file's `disc_threads` module variable, so queue sizing is a header/C coupling point.

Protocol status and opcode enums include CRQ valid/init/transport event values, command status flags, fabric-mapped errors, VIOS errors, MAD opcodes, FC reason/type/explain values, FCP response info/flags, command flags, task attributes, TMF flags, CRQ formats, async events, link/FPIN states, target actions, protocols, host actions, and host states.

Important wire structs are `ibmvfc_mad_common`, `ibmvfc_npiv_login_mad`, `ibmvfc_npiv_logout_mad`, `ibmvfc_npiv_login`, `ibmvfc_npiv_login_resp`, `ibmvfc_discover_targets`, `ibmvfc_port_login`, `ibmvfc_move_login`, `ibmvfc_process_login`, `ibmvfc_query_tgt`, `ibmvfc_implicit_logout`, `ibmvfc_tmf`, `ibmvfc_fcp_cmd_iu`, `ibmvfc_fcp_rsp`, `ibmvfc_cmd`, `ibmvfc_passthru_mad`, `ibmvfc_channel_enquiry`, `ibmvfc_channel_setup`, `ibmvfc_connection_info`, `ibmvfc_crq`, `ibmvfc_sub_crq`, and `ibmvfc_async_crq`. Most are packed and explicitly aligned for hypervisor/VIOS DMA layout.

Important in-memory structs are `ibmvfc_target`, `ibmvfc_event`, `ibmvfc_event_pool`, `ibmvfc_queue`, `ibmvfc_channels`, and `ibmvfc_host`. They are not just declarations; their field layout expresses the driver's ownership model, queue model, target/rport lifecycle, and host state machine.

## Control Flow Expressed by the Header
The header encodes the CRQ transport framing: messages are either command responses, async events, or MAD/FCP payload descriptors. `union ibmvfc_iu` lets a single DMA-backed event storage slot carry any supported management command or FCP command, while `ibmvfc_crq.ioba` returns the event correlation token.

NPIV login flow is represented by `ibmvfc_npiv_login`, `ibmvfc_npiv_login_resp`, and capability flags. The client advertises migration, channel, FPIN, MAD-version, and VF-WWPN abilities; VIOS responds with native-FC support, flush/suppress-ABTS/MAD/channel/VF-WWPN capabilities, max commands, scsi ID, WWPNs, link speed, names, and service parameters. `ibmvfc.c` uses these fields to decide command IU version, multiqueue setup, host FC identity, and max queue depth.

Target discovery and login flow is encoded by `ibmvfc_discover_targets_entry`, `ibmvfc_discover_targets`, `ibmvfc_port_login`, `ibmvfc_process_login`, `ibmvfc_query_tgt`, `ibmvfc_implicit_logout`, and `ibmvfc_move_login`. The driver discovers SCSI port IDs and WWPNs, logs into ports, runs PRLI with SCSI-FCP service parameters, validates or updates existing targets, logs out old IDs, and optionally moves login state for NPIV failover cases.

I/O flow is represented by `ibmvfc_cmd`, `ibmvfc_fcp_cmd_iu`, `ibmvfc_fcp_rsp`, and scatterlist-related `srp_direct_buf` fields. The command struct includes status/error, adapter residual, flags, cancel key, exchange ID, external function descriptor, data descriptor, response descriptor, correlation, target identity, and both v1 and v2 IU layouts. The v2 layout inserts an extra reserved word and target WWPN support when `IBMVFC_HANDLE_VF_WWPN` is negotiated.

Recovery flow is represented by `ibmvfc_tmf`, cancel keys, TMF flags, event completions, host/target actions, and async event enums. These definitions let `ibmvfc.c` issue cancels, abort task sets, LUN/target resets, passthrough cancels, and host reset/relogin sequences in response to SCSI EH, timeouts, CRQ transport events, and async FC events.

## State and Persistence Behavior
`struct ibmvfc_host` is the root runtime object stored as SCSI host private data. It persists while the VIO device is bound and contains host state/action, target list, purge list, device pointers, DMA pools and buffers, CRQ/async/sub-CRQ queues, login buffers, channel setup buffer, log level, passthrough mutex, channel limits, task-set counter, state flags, scan status, pending async event flags, partition identity, worker callback, worker thread, tasklet, rport-add work, and wait queues.

`struct ibmvfc_target` persists per discovered FC target and contains list linkage, owning host, protocol, SCSI ID/WWPN/new SCSI ID, FC rport pointer, target ID, action, login/add flags, retry and move-login state, cancel key, service parameters, FC rport identifiers, job callback, ADISC timer, and kref.

`struct ibmvfc_event` is the unit of queued work. It holds list nodes, host/queue/target/SCSI command pointers, `free` and `active` atomics, DMA transfer IU pointer, callbacks, CRQ descriptor, local IU staging storage, optional synchronous response pointer, external scatterlist DMA buffer/token, completion objects, timer, hardware queue index, and reserved-event flag.

`struct ibmvfc_queue` tracks one CRQ-like queue page plus its event pool and sub-CRQ metadata. It stores the DMA-mapped message page, current ring index, lock pointers, sent/free event lists, depth accounting, cancel response IU, hypervisor cookies, IRQs, hardware queue ID, name, and IRQ handler. `struct ibmvfc_channels` groups SCRQs by protocol and tracks active/desired/max queue counts plus a DMA discovery buffer.

All protocol fields use big-endian integer types where VIOS expects big-endian wire data. There is no disk persistence; the header's state structs describe volatile kernel state rebuilt on probe and destroyed on remove.

## Dependencies and Integration Points
The header includes `linux/list.h`, `linux/types.h`, and `scsi/viosrp.h`; additional types are supplied by the C file's broader includes. `srp_direct_buf`, `struct scsi_lun`, `SCSI_SENSE_BUFFERSIZE`, `struct fc_rport`, `struct fc_rport_identifiers`, `struct Scsi_Host`, `struct scsi_cmnd`, DMA address types, timers, completions, mempools, work structs, tasklets, and wait queues are all part of the integration surface.

Packed/aligned protocol definitions integrate with VIOS DMA and pseries CRQ/SCRQ hypervisor calls. The CRQ, sub-CRQ, async CRQ, MAD common header, and all MAD payload structs must remain ABI-compatible with the firmware/VIOS contract.

The logging macros integrate with kernel device logging and the C file's `ibmvfc_debug`/`log_level` globals. Trace helper macros integrate with sysfs only when `CONFIG_SCSI_IBMVFC_TRACE` is enabled.

## Risks and Edge Cases
The protocol structs are ABI-sensitive. Changing packing, alignment, field order, endian annotations, or union layout can break VIOS communication. `ibmvfc_cmd` is especially sensitive because v1/v2 IU offsets are used to compute response DMA addresses.

Queue sizing depends on defaults and a macro that references `disc_threads` from the implementation file. This is convenient but creates non-obvious coupling: changes to discovery-thread behavior affect reserved event counts and can starve recovery if not considered.

Host and target action enums define allowed transitions in `ibmvfc.c`; adding states without updating `ibmvfc_set_host_action`, `ibmvfc_set_tgt_action`, `ibmvfc_work_to_do`, and `ibmvfc_do_work` can strand work or unblock I/O too early.

Capability flags select behavior at runtime. If the header and implementation disagree about `IBMVFC_HANDLE_VF_WWPN`, `IBMVFC_CAN_SUPPORT_CHANNELS`, suppress-ABTS, migration, or channel flags, the driver can send an IU version or channel request the partner does not understand.

The async event set includes FPIN constants, but the implementation's logged descriptor table does not include `IBMVFC_AE_FPIN` in the viewed source. Any functional FPIN handling would need explicit implementation support rather than only header constants.

## Test Signals
Header-focused validation should include compile coverage for big-endian conversions, struct size/offset assumptions around `ibmvfc_cmd.v1.rsp` and `v2.rsp`, and builds with trace enabled/disabled.

Protocol tests should validate NPIV login capability negotiation, channel enquiry/setup flags, discovery buffer entry parsing, target login MAD fields, TMF flags/cancel keys, passthrough payload descriptors, and CRQ/SCRQ message sizes.

State-machine tests should cover every `ibmvfc_host_action`, `ibmvfc_host_state`, and `ibmvfc_target_action` value through the implementation transitions, including reset, reenable, target delete, move login, and host offline removal.

Resource tests should validate event-pool depth math for base CRQ and sub-CRQ queues across different `disc_threads`, `scsi_qdepth`, hardware queue counts, and channel counts, ensuring reserved events remain available for initialization and recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvfc.h -->
