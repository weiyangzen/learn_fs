# Research: subset-b-004988

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/fc.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/fc.c

## Purpose
This file implements the Linux NVMe over Fibre Channel host transport. It exposes the LLDD-facing registration API for FC local and remote ports, owns FC-NVMe association and connection setup through Link Service requests, maps blk-mq NVMe requests into FC-NVMe command IUs, handles completions and transport errors, and registers the `fc` NVMe fabrics transport. It also provides a temporary FC class device used for NVMe discovery uevents and optional blk-cgroup FC appid plumbing.

The file is the bridge between the generic NVMe core/fabrics layers and Fibre Channel low-level drivers. The NVMe core sees a `struct nvme_ctrl` with `nvme_ctrl_ops` and blk-mq operations; LLDDs see `struct nvme_fc_port_template` callbacks and `nvmefc_ls_req`, `nvmefc_ls_rsp`, and `nvmefc_fcp_req` work items.

## Important APIs, Types, And Functions
Exported LLDD entry points are `nvme_fc_register_localport()`, `nvme_fc_unregister_localport()`, `nvme_fc_register_remoteport()`, `nvme_fc_unregister_remoteport()`, `nvme_fc_rescan_remoteport()`, `nvme_fc_set_remoteport_devloss()`, `nvme_fc_rcv_ls_req()`, and `nvme_fc_io_getuuid()`. Module initialization registers `nvme_fc_transport` with `nvmf_register_transport()` so userspace can create controllers using `transport=fc`.

Core private objects are `struct nvme_fc_lport`, `struct nvme_fc_rport`, `struct nvme_fc_ctrl`, `struct nvme_fc_queue`, `struct nvmefc_ls_req_op`, `struct nvmefc_ls_rcv_op`, and `struct nvme_fc_fcp_op`. `struct nvme_fc_fcp_op` embeds `struct nvme_request` as its first member to satisfy NVMe core request-private layout requirements. Controller flags include `ASSOC_ACTIVE`, `ASSOC_FAILED`, and `FCCTRL_TERMIO`; queue flags include `NVME_FC_Q_CONNECTED` and `NVME_FC_Q_LIVE`.

Connection setup is centered on `nvme_fc_create_association()`, `nvme_fc_connect_admin_queue()`, `nvme_fc_connect_queue()`, `nvme_fc_create_io_queues()`, and `nvme_fc_recreate_io_queues()`. Request submission uses `nvme_fc_queue_rq()`, `nvme_fc_start_fcp_op()`, `nvme_fc_map_data()`, `nvme_fc_fcpio_done()`, `nvme_fc_complete_rq()`, and `nvme_fc_timeout()`. Error and lifecycle code includes `nvme_fc_error_recovery()`, `nvme_fc_delete_association()`, `__nvme_fc_abort_outstanding_ios()`, `nvme_fc_reset_ctrl_work()`, `nvme_fc_reconnect_or_delete()`, and `nvme_fc_delete_ctrl()`.

## Control Flow
LLDDs first register local ports with `nvme_fc_register_localport()`. The function validates required template callbacks, reattaches a previously deleted matching local port when possible, otherwise allocates a new lport, assigns a port number with `ida_alloc()`, stores LLDD private memory after the object, and adds it to `nvme_fc_lport_list`. Remote-port registration similarly reattaches suspended deleted rports within `dev_loss_tmo` or allocates a new rport under the local port, then emits discovery uevents for discovery-capable targets.

Controller creation starts from `nvme_fc_create_ctrl()`, which parses host and target FC WWN pairs from fixed-format traddr strings, finds matching online lport/rport objects, and calls `nvme_fc_init_ctrl()`. Controller initialization allocates `struct nvme_fc_ctrl`, initializes the admin queue, registers with the NVMe core, creates an admin tag set, links the controller to the rport, transitions to `NVME_CTRL_CONNECTING`, and queues `connect_work`.

`nvme_fc_create_association()` creates the link-side association and then makes the NVMe controller live. It creates the admin hardware queue through the LLDD, sends a Create Association LS, runs `nvmf_connect_admin_queue()`, enables and finishes the controller, checks FC-specific constraints such as no `icdoff` and mandatory SGL support, initializes AEN operations, creates and connects I/O queues, transitions to `NVME_CTRL_LIVE`, and starts the NVMe controller. On failure it sends Disconnect Association, clears association state, responds to any pending received disconnect LS, deletes hardware queues, clears active counters, and lets reconnect logic decide what happens next.

The blk-mq request path starts in `nvme_fc_queue_rq()`. It rejects nonready paths, builds the NVMe command with `nvme_setup_cmd()`, determines data direction from physical segments, and calls `nvme_fc_start_fcp_op()`. That helper checks remote-port liveness, gets a controller reference, fills FC-NVMe CMD IU fields including connection ID and CSN, maps request data into an SG table, syncs the command IU for DMA, marks the op active, starts the request, and hands it to `lport->ops->fcp_io()`. Completion returns through `nvme_fc_fcpio_done()`, which validates response lengths, ERSP IU fields, transfer length, command ID, and LLDD status before completing the NVMe request or scheduling reset.

Receive-side LS handling is asynchronous. `nvme_fc_rcv_ls_req()` copies the incoming request and allocates a response buffer, maps the response for DMA, queues the operation on `rport->ls_rcv_list`, and schedules `lsrcv_work`. `nvme_fc_handle_ls_rqst_work()` dispatches supported LS commands. Disconnect Association is validated, matched against an active controller association, and either rejected immediately or deferred until `nvme_fc_delete_association()` has aborted outstanding exchanges.

## State And Persistence
Persistent runtime state is in global lists and IDAs (`nvme_fc_lport_list`, `nvme_fc_local_port_cnt`, `nvme_fc_ctrl_cnt`), per-port krefs and active counters, rport LS request/receive/control lists, controller queue arrays, work items, and NVMe core state. State is in-memory only; link identifiers such as association ID, connection ID, queue CSN, controller number, port number, and dev-loss deadline are recreated as ports and controllers are registered or reconnected.

FC association state is deliberately split across link-side objects and NVMe core state. `ASSOC_ACTIVE` gates whether a controller currently owns an association on the rport; `ASSOC_FAILED` records connection failure while setup is in progress; `FCCTRL_TERMIO` tracks termination so aborted operations can decrement `iocnt` and wake `ioabort_wait`. Queue state uses connected/live bits plus LLDD queue handles. Rport state includes `dev_loss_end`, allowing remote-port deletion to trigger reconnect attempts until the timeout expires.

DMA mappings are per LS request, per received LS response, per request command IU/response IU, and per data SG table. The fcloop special case passes `dev == NULL`; wrapper helpers intentionally no-op or pseudo-map DMA for that mode.

## Dependencies And Integration Points
The file depends on NVMe core and fabrics helpers from `nvme.h` and `fabrics.h`, FC-NVMe wire structures from UAPI FC headers and `linux/nvme-fc.h`, LLDD contracts from `linux/nvme-fc-driver.h`, blk-mq, DMA mapping, SCSI FC transport naming, sysfs/device class APIs, krefs, IDAs, workqueues, timers, and optional blk-cgroup appid support.

Important integration points include LLDD callbacks (`localport_delete`, `remoteport_delete`, `ls_req`, `ls_abort`, `xmt_ls_rsp`, `create_queue`, `delete_queue`, `fcp_io`, `fcp_abort`, `map_queues`), NVMe fabrics connect helpers, NVMe core controller lifecycle, request timeout/error handling, discovery uevents, and sysfs attributes under the temporary `fc` class.

## Risks
The highest risk is lifecycle concurrency. Local ports, remote ports, controllers, LS requests, received LS operations, AENs, blk-mq requests, reconnect work, reset work, and module exit all hold independent references and locks. Bugs can produce use-after-free, stale LLDD handles, double delete callbacks, stuck reconnects, or IO that never completes.

Protocol correctness is also sensitive. Create Association/Create Connection accept responses are manually validated by descriptor tags, lengths, command echo, association IDs, and connection IDs. Any missing validation or endian mistake can make host and target disagree about association state. Disconnect Association is intentionally asynchronous and deferred after ABTS, which is correct for cleanup but makes ordering fragile.

Request completion is strict about transfer length, ERSP IU length, response result, and command ID. Invalid responses schedule controller reset, which is safe but can amplify transient LLDD bugs into repeated reconnects. Timeout handling starts an LLDD abort and returns `BLK_EH_RESET_TIMER`; if the LLDD never completes the aborted exchange, teardown can wait indefinitely.

Other risks include traddr parser assumptions, global discovery list retry limits, no-op DMA behavior for NULL devices differing from real DMA behavior, and optional appid parsing accepting only a narrow `hex:appid` shape.

## Test Signals
Useful tests include LLDD port register/unregister/re-register, remote-port dev-loss and reappearance, discovery uevent contents, controller create/delete by FC traddr, duplicate connect rejection, admin and I/O queue connection validation, reconnect after remote-port loss, reconnect timeout expiry, module unload with live controllers, received Disconnect Association LS during normal I/O, and LS abort during remote-port deletion.

I/O tests should cover reads, writes, compare, no-data commands, write zeroes with no physical payload, AEN submission, request timeout and abort completion, LLDD `fcp_io()` returning `-EBUSY` versus hard errors, bad ERSP lengths, bad transferred lengths, and blkcg appid retrieval when `CONFIG_BLK_CGROUP_FC_APPID` is enabled. Runtime signals include lockdep, KASAN, refcount warnings, stuck workqueues, controller state transitions, queue live/connected bits, and FC target logs for association/connection IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/fc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/fc.h -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/fc.h

## Purpose
This header provides common FC-NVMe Link Service definitions shared by the host FC transport and the target FC transport implementation. It wraps FC-NVMe request and response wire structures into aligned unions, provides helpers to format ACC/RJT response headers and Disconnect Association requests, defines validation error codes and human-readable names, and validates received Disconnect Association LS payloads.

## Important APIs, Types, And Functions
`union nvmefc_ls_requests` contains all supported host/target LS request shapes: generic word zero, Create Association, Create Connection, Disconnect Association, and Disconnect Connection. `union nvmefc_ls_responses` mirrors the response forms: RJT, Create Association accept, Create Connection accept, Disconnect Association accept, and Disconnect Connection accept. Both unions are aligned to 128 bytes so callers can allocate private data after them with predictable alignment.

Important inline helpers are `nvme_fc_format_rsp_hdr()`, `nvme_fc_format_rjt()`, `nvmefc_fmt_lsreq_discon_assoc()`, and `nvmefc_vldt_lsreq_discon_assoc()`. The file also defines validation error indexes (`VERR_*`), `validation_errors[]`, `NVME_FC_LAST_LS_CMD_VALUE`, and `nvmefc_ls_names[]`.

## Control Flow
The header has no independent runtime loop, but its helpers are called in the LS send and receive paths. Host-side disconnect transmission calls `nvmefc_fmt_lsreq_discon_assoc()` to populate request and response buffer pointers, timeout, descriptor list length, association descriptor, and disconnect command descriptor. Receive-side Disconnect Association handling calls `nvmefc_vldt_lsreq_discon_assoc()` before matching an association and formatting an accept.

Response formatting uses `nvme_fc_format_rsp_hdr()` for the common ACC/RJT prefix and `nvme_fc_format_rjt()` to add the reject descriptor. These helpers are used when rejecting unsupported, invalid, or temporarily unavailable LS requests.

## State And Persistence
The header allocates no dynamic state. It defines static string tables and constants compiled into every translation unit that includes it. The inline functions mutate caller-supplied LS buffers and therefore depend on the caller passing correctly sized `fcnvme_*` structures.

Because the validation error enum indexes into `validation_errors[]`, the order of both tables is a persistent source-level contract. FC-NVMe descriptor constants and endian conversions are wire ABI details; changes affect compatibility with targets and initiators.

## Dependencies And Integration Points
The header depends on FC-NVMe UAPI structures and constants such as `FCNVME_LS_*`, `FCNVME_LSDESC_*`, `fcnvme_lsdesc_len()`, `struct fcnvme_ls_rjt`, and disconnect descriptor layouts. It also depends on kernel endian helpers. It is included by `fc.c` and can be shared with target-side FC code so both sides use the same formatting and validation conventions.

## Risks
`nvme_fc_format_rjt()` passes `FCNVME_LSDESC_RQST` as the LS command argument to `nvme_fc_format_rsp_hdr()` rather than `FCNVME_LS_RJT`; this mirrors the current source but is a subtle field that deserves protocol-level scrutiny because a reject header with the wrong LS command would confuse peers. More generally, all helpers assume caller-provided buffers are large enough and aligned.

Validation is intentionally narrow for Disconnect Association. It checks length, descriptor list length, descriptor tags, descriptor lengths, and old-format scope, but it does not validate every reserved field. The static string tables are non-const `char *`, which is common in older kernel code but less robust than `const char * const`.

## Test Signals
Tests should serialize and inspect Disconnect Association requests, valid and invalid Disconnect Association receives, RJT formatting for unsupported LS commands, descriptor lengths after endian conversion, and each `VERR_*` mapping printed by `fc.c`. Interoperability tests with an FC-NVMe target are the strongest signal because this header encodes wire-format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/hwmon.c

## Purpose
This file exposes NVMe controller temperature data through the Linux hwmon subsystem. It reads the NVMe SMART / health log for composite and secondary temperature sensors, exposes critical warnings and critical temperature limits, and maps hwmon max/min threshold attributes to the NVMe Temperature Threshold feature.

## Important APIs, Types, And Functions
The private state is `struct nvme_hwmon_data`, containing the owning `struct nvme_ctrl`, a cached `struct nvme_smart_log`, and `read_lock` to serialize SMART log reads. Public entry points are `nvme_hwmon_init()` and `nvme_hwmon_exit()`, declared through `nvme.h` when `CONFIG_NVME_HWMON` is enabled.

Important helpers are `nvme_get_temp_thresh()`, `nvme_set_temp_thresh()`, `nvme_hwmon_get_smart_log()`, `nvme_hwmon_read()`, `nvme_hwmon_write()`, `nvme_hwmon_read_string()`, and `nvme_hwmon_is_visible()`. The hwmon contract is described by `nvme_hwmon_info`, `nvme_hwmon_ops`, and `nvme_hwmon_chip_info`.

## Control Flow
Initialization allocates `nvme_hwmon_data` and a SMART log buffer, records the controller pointer, initializes the mutex, reads the SMART log once, and registers a hwmon device named `nvme` with `hwmon_device_register_with_info()`. The initial SMART read is important because visibility decisions use `data->log->temp_sensor[]` to decide which secondary sensors exist.

Reads first handle attributes that do not need a SMART log refresh. `hwmon_temp_max` and `hwmon_temp_min` issue Get Features for the selected sensor and over/under threshold type. `hwmon_temp_crit` returns the controller's critical composite temperature from identify data. For live attributes, `nvme_hwmon_read()` locks `read_lock`, refreshes the SMART log with `nvme_get_log()`, and returns composite or secondary sensor temperature in millidegrees Celsius, or the composite temperature alarm bit.

Writes support only `hwmon_temp_max` and `hwmon_temp_min`. The value is converted from millidegrees Celsius to Kelvin, clamped into the NVMe threshold field, combined with sensor select and threshold type bits, and sent through Set Features. Exit unregisters the hwmon device and frees the log and data objects.

## State And Persistence
The only persistent in-memory state is the hwmon device pointer stored in `ctrl->hwmon_device`, the private data object attached to that device, and the cached SMART log. Threshold writes persist in the controller according to NVMe feature semantics, not in this file. Temperature values are refreshed on demand rather than periodically cached.

Visibility is partially determined from identify-controller fields (`wctemp`, `cctemp`) and quirks (`NVME_QUIRK_NO_TEMP_THRESH_CHANGE`, `NVME_QUIRK_NO_SECONDARY_TEMP_THRESH`) plus the initial SMART log sensor presence. If sensor presence changes later, visibility does not automatically expand because hwmon attributes are created at registration time.

## Dependencies And Integration Points
This module depends on the NVMe admin command helpers `nvme_get_log()`, `nvme_get_features()`, and `nvme_set_features()`, temperature constants from NVMe headers, hwmon registration APIs, unit conversion helpers, and unaligned little-endian reads. It is called from controller setup/teardown paths through `nvme_hwmon_init()` and `nvme_hwmon_exit()`.

## Risks
Temperature threshold handling relies on controller compliance. Some devices do not support threshold changes or secondary thresholds, which is why visibility honors quirks. A positive NVMe status from Get/Set Features is normalized to `-EIO`, so callers do not see the exact NVMe status. The SMART log buffer is reused under a mutex, but visibility reads some cached fields without refreshing the log.

Secondary sensor exposure is based on nonzero `temp_sensor[]` entries. A valid sensor reading of zero Kelvin is not realistic, so this is acceptable, but devices with lazy or delayed SMART sensor population may hide attributes until the hwmon device is recreated.

## Test Signals
Test by registering controllers with and without `wctemp`, `cctemp`, secondary sensors, and threshold quirks. Verify sysfs permissions for `temp*_max`, `temp*_min`, `temp*_crit`, `temp*_input`, labels, and alarm. Exercise threshold writes and reads around clamp boundaries, controller errors from Get/Set Features, SMART log read failures, and teardown while userspace polls hwmon attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/ioctl.c

## Purpose
This file implements the userspace command submission surface for NVMe block devices, namespace character devices, namespace-head multipath character/block devices, and controller character devices. It supports legacy ioctls (`NVME_IOCTL_*`) and `io_uring_cmd` passthrough for admin and I/O commands, including vectored and fixed-buffer paths, metadata mapping, polling, and nonblocking request allocation.

## Important APIs, Types, And Functions
Public entry points are `nvme_ioctl()`, `nvme_ns_chr_ioctl()`, `nvme_ns_chr_uring_cmd()`, `nvme_ns_chr_uring_cmd_iopoll()`, `nvme_ns_head_ioctl()`, `nvme_ns_head_chr_ioctl()`, `nvme_ns_head_chr_uring_cmd()`, `nvme_dev_uring_cmd()`, and `nvme_dev_ioctl()`. The file also handles deprecated controller-char `NVME_IOCTL_IO_CMD` through `nvme_dev_user_cmd()`.

Permission and setup helpers include `nvme_cmd_allowed()`, `nvme_to_user_ptr()`, `nvme_alloc_user_request()`, `nvme_map_user_request()`, `nvme_submit_user_cmd()`, `nvme_submit_io()`, `nvme_validate_passthru_nsid()`, `nvme_user_cmd()`, and `nvme_user_cmd64()`. `struct nvme_uring_data` snapshots user command fields, and `struct nvme_uring_cmd_pdu` stores request, bio, result, and status in the io_uring command private data.

## Control Flow
Legacy namespace ioctls dispatch through `nvme_ns_ioctl()`. `NVME_IOCTL_ID` returns the namespace ID. `NVME_IOCTL_SUBMIT_IO` copies `struct nvme_user_io`, validates read/write/compare opcodes, computes data and metadata lengths from namespace format, handles protection information and extended LBA cases, builds an NVMe read/write command, and submits it synchronously. Passthrough ioctls copy 32-bit or 64-bit passthrough structures, validate namespace ID, construct `struct nvme_command`, check permissions, map user data and metadata, execute the request, unmap the bio, and copy the result back to userspace.

`nvme_cmd_allowed()` is the main security gate. It allows only safe unprivileged commands: no partition escape, no vendor/fabrics commands, only a small admin identify subset without a namespace, and only I/O commands that the Command Effects log marks supported and not intrusive. Writes or logical-block-content-changing commands require the file to be open for write. Otherwise `CAP_SYS_ADMIN` is required.

`io_uring_cmd` flow starts with `nvme_uring_cmd_checks()`, requiring 128-byte SQEs and 32-byte CQEs. `nvme_uring_cmd_io()` snapshots command fields with `READ_ONCE()`, validates flags and nsid, applies the same permission policy, imports fixed buffers when requested, sets `REQ_NOWAIT` or `REQ_POLLED` from issue flags, allocates a request, maps data and metadata, stores the bio for later unmap, installs `nvme_uring_cmd_end_io()`, and submits with `blk_execute_rq_nowait()`. Completion either finishes inline for matching IOPOLL context or posts task work so completion runs in the owning io_uring context.

Multipath namespace-head ioctls select a live path under `head->srcu` with `nvme_find_path()`. Controller-level ioctls deliberately drop the namespace-head SRCU reference early after taking a controller reference to avoid deadlocks when passthrough deletes namespaces.

## State And Persistence
This file does not create persistent device state, but it mutates controller and namespace state through submitted admin/I/O commands and through controller management ioctls such as reset, subsystem reset, and rescan. Per-request state lives in blk-mq requests, mapped bios, request flags (`NVME_REQ_USERCMD`), optional metadata mappings, and io_uring PDU fields. For multipath, SRCU protects selected namespace paths during ioctl or io_uring submission.

Passthrough effects are bracketed by `nvme_passthru_start()` and `nvme_passthru_end()`, allowing command effects to trigger namespace/controller rescans, quiescing, or other core behavior after command completion.

## Dependencies And Integration Points
The file depends on Linux ioctl, block, blk-integrity, compat, ptrace syscall return, io_uring command, request mapping, and SED OPAL helpers. NVMe integration points include command setup/execution, command effects, namespace ID validation, namespace-head path selection, controller reset/rescan, metadata integrity mapping, and multipath SRCU.

It is wired into block-device operations, namespace character file operations, namespace-head file operations from `multipath.c`, and controller character-device operations declared in `nvme.h`.

## Risks
This is a high-risk userspace boundary. Incorrect permission checks could expose vendor/admin/fabrics commands, writes through read-only descriptors, or partition escape. Incorrect user pointer handling can break compat tasks; `nvme_to_user_ptr()` intentionally truncates upper bits for compat behavior. Metadata mapping must match namespace integrity support and extended LBA/PI rules or user buffers can be interpreted incorrectly.

io_uring adds lifetime risk because request completion may be inline, task-work based, polled, cancelled, or nonblocking. The PDU stores the bio because `req->bio` can be cleared by completion time; missing that unmap would leak user mappings. Multipath head controller ioctls must avoid holding SRCU across operations that delete namespaces, which is why `nvme_ns_head_ctrl_ioctl()` drops SRCU before calling controller ioctl.

## Test Signals
Test unprivileged and privileged passthrough for allowed identify commands, denied vendor/admin/fabrics commands, partition passthrough denial, write commands on read-only fds, command effects handling, metadata mapping with and without integrity, extended LBA namespaces, PRACT metadata stripping, compat `NVME_IOCTL_SUBMIT_IO32`, and result copyout failures.

io_uring tests should cover admin and I/O commands, vectored and non-vectored fixed buffers, `IO_URING_F_NONBLOCK`, `IO_URING_F_IOPOLL`, cancellation, inline poll completion, task-work completion, metadata buffers, invalid nsids, missing SQE128/CQE32 support, and multipath namespace-head path disappearance while commands are issued. Controller ioctl tests should cover reset, subsystem reset, rescan, SED ioctls, and deprecated char-device I/O passthrough with one versus multiple namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/multipath.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/multipath.c

## Purpose
This file implements native NVMe multipath support for namespace heads. It creates shared multipath disks and character devices, selects a live namespace path for each bio or passthrough request, requeues I/O when paths fail, tracks ANA state, exposes multipath sysfs attributes, and manages delayed removal of namespace-head devices.

## Important APIs, Types, And Functions
Module parameters are `multipath`, `multipath_always_on`, and `iopolicy`. I/O policies are `numa`, `round-robin`, and `queue-depth`. Public functions include `nvme_mpath_default_iopolicy()`, freeze helpers, `nvme_failover_req()`, `nvme_mpath_start_request()`, `nvme_mpath_end_request()`, `nvme_kick_requeue_lists()`, `nvme_mpath_clear_current_path()`, `nvme_mpath_clear_ctrl_paths()`, `nvme_mpath_revalidate_paths()`, `nvme_find_path()`, `nvme_mpath_alloc_disk()`, `nvme_mpath_add_disk()`, `nvme_mpath_remove_disk()`, `nvme_mpath_put_disk()`, `nvme_mpath_init_ctrl()`, `nvme_mpath_init_identify()`, `nvme_mpath_update()`, `nvme_mpath_stop()`, and `nvme_mpath_uninit()`.

The namespace-head block operations are `nvme_ns_head_ops`, with `submit_bio`, open/release, ioctl, geometry, unique-id, zones, and persistent reservation hooks. Character-device operations are `nvme_ns_head_chr_fops`. Sysfs attributes include subsystem `iopolicy`, per-path `ana_grpid`, `ana_state`, `queue_depth`, `numa_nodes`, and head `delayed_removal_secs`.

## Control Flow
Initialization starts when a namespace head is allocated. `nvme_mpath_alloc_disk()` initializes locks, requeue work, partition-scan work, delayed removal work, and optionally allocates a head disk if multipath is enabled or forced and the namespace ID is unique enough. It suppresses partition scanning until a separate work item can run outside controller scan context.

Bio submission enters `nvme_ns_head_submit_bio()`. The bio is split to queue limits, `head->srcu` is taken, and `nvme_find_path()` selects a namespace path by the current subsystem policy. A found path remaps the bio to the path disk, marks it `REQ_NVME_MPATH`, emits a block remap trace, and submits it. If no usable path exists but a path may recover, the bio is put on `head->requeue_list`; otherwise it is failed.

Path selection filters disabled paths by controller state, ANA pending flag, and namespace readiness. NUMA policy caches a current optimized path per NUMA node and falls back to nearest non-optimized. Round-robin walks siblings after the current path and prefers optimized paths while still allowing non-optimized fallback. Queue-depth policy chooses the optimized path with the lowest active count, falling back to lowest-depth non-optimized.

ANA handling starts in `nvme_mpath_init_identify()`, which validates controller ANA capabilities, computes the ANA log size, allocates or resizes `ana_log_buf`, and reads the ANA log. `nvme_read_ana_log()` gets the log page, parses each ANA group with bounds checks, updates namespace ANA states, and arms or deletes the ANATT timer depending on groups in change state. `nvme_update_ns_ana_state()` clears pending state, records group and ANA state, and makes the namespace-head disk live when a path becomes optimized or non-optimized and the controller is live.

Failover uses `nvme_failover_req()`: clear cached current paths, queue an ANA reread on ANA errors, move bios from the failed request to the namespace-head requeue list, clear status, end the original request, and schedule requeue work. `nvme_requeue_work()` resubmits queued bios through the head so path selection runs again.

## State And Persistence
Multipath state is attached to `struct nvme_subsystem`, `struct nvme_ns_head`, `struct nvme_ns`, and `struct nvme_ctrl`. The subsystem stores `iopolicy`. Each namespace head stores a multipath disk, cdev, SRCU-protected path list, per-node current path pointers, requeue list, flags, delayed removal seconds, and work items. Each namespace stores ANA group/state and flags such as `NVME_NS_ANA_PENDING` and `NVME_NS_SYSFS_ATTR_LINK`. Each controller stores ANA log buffer, ANA lock, ANATT timer/work, and queue-depth active count.

State is mostly runtime. Sysfs writes to `iopolicy` and `delayed_removal_secs` persist until module/controller teardown. ANA state is refreshed from controller log pages. Current path caches are intentionally invalidated on iopolicy changes, path failures, capacity mismatches, and controller path clearing.

## Dependencies And Integration Points
This file depends on blk-mq, gendisk, bio remapping, kblockd, sysfs, SRCU, module parameters, timers, NVMe identify/log helpers, NVMe namespace/controller/subsystem structures from `nvme.h`, optional zoned block support, and ioctl functions from `ioctl.c`.

Integration points are broad: core namespace scanning calls allocation/add/remove helpers, request completion calls start/end accounting helpers, transport error paths call failover and path clearing helpers, ANA AEN or error handling queues `ana_work`, and userspace observes/controls policy and delayed removal through sysfs.

## Risks
Path selection and removal are concurrency-sensitive. SRCU protects path traversal, but disk add/remove, sysfs link creation, delayed removal, requeue work, and namespace scan can overlap. Incorrect ordering can leave stale current-path pointers, duplicate sysfs links, live head disks without paths, or bios queued forever.

ANA parsing trusts controller-provided log structure after explicit bounds checks. Bad `ngrps`, `nnsids`, group IDs, or states return errors and can disable ANA support during identify. ANATT handling uses one timer for all changing groups, trading precision for simplicity. Queue-depth policy depends on `nvme_mpath_start_request()` and `nvme_mpath_end_request()` balancing active counts; missed end paths would bias routing.

The delayed removal feature intentionally queues I/O when no path is available. Misconfiguration can make failures appear as hangs until the delay expires. `multipath_always_on` can create head devices even for cases that would otherwise stay single-path, so namespace uniqueness checks are important.

## Test Signals
Test with single-path, multi-controller shared namespace, private namespace, ANA and non-ANA controllers, `multipath=0`, `multipath_always_on=1`, and each iopolicy. Exercise optimized/non-optimized/inaccessible/persistent-loss/change ANA transitions, ANA log parse errors, ANATT timeout reset, failover on ANA status, controller reset, path removal and re-addition, capacity mismatch, and namespace deletion during queued I/O.

Sysfs tests should verify iopolicy changes clear cached paths, queue-depth and numa_nodes visibility/content, ana state attributes, sysfs path links, and delayed_removal_secs behavior. I/O tests should verify bio remap tracing, accounting on the head disk, requeue then successful resubmit, final failure when no path is available, polled and nowait features on the head disk, zoned report forwarding, persistent reservations, and ioctl/io_uring passthrough through namespace heads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/multipath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/nvme.h -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/nvme.h

## Purpose
This header is the central private contract for the Linux NVMe host stack. It defines shared controller, subsystem, namespace, namespace-head, request, quirk, and operation structures; declares workqueues and core helper APIs; and provides inline helpers used by PCI, fabrics, multipath, ioctl, hwmon, authentication, zoned, and core code.

## Important APIs, Types, And Functions
Major types are `struct nvme_request`, `struct nvme_ctrl`, `struct nvme_subsystem`, `struct nvme_ns_ids`, `struct nvme_ns_head`, `struct nvme_ns`, `struct nvme_ctrl_ops`, `struct nvme_fault_inject`, and `struct nvme_zone_info`. Important enums include `enum nvme_quirks`, `enum nvme_ctrl_state`, `enum nvme_ctrl_flags`, `enum nvme_iopolicy`, namespace feature bits, and `nvme_submit_flags_t`.

Key inline helpers include `nvme_req()`, `nvme_req_qid()`, `nvme_ctrl_state()`, `nvme_ns_head_multipath()`, `nvme_ns_has_pi()`, `nvme_get_virt_boundary()`, command ID generation/extraction helpers, `nvme_find_rq()`, `nvme_strlen()`, `nvme_print_device_info()`, `nvme_reset_subsystem()`, LBA/sector conversion, `nvme_bytes_to_numd()`, `from0based()`, `nvme_is_ana_error()`, `nvme_is_path_error()`, `nvme_try_complete_req()`, `nvme_get_ctrl()`, `nvme_put_ctrl()`, `nvme_is_aen_req()`, `nvme_state_terminal()`, `nvme_req_op()`, `nvme_check_ready()`, `nvme_is_unique_nsid()`, `nvme_ctrl_use_ana()`, `nvme_disk_is_ns_head()`, `nvme_get_ns_from_dev()`, `nvme_start_request()`, `nvme_ctrl_sgl_supported()`, `nvme_ctrl_meta_sgl_supported()`, and `nvme_multi_css()`.

The header declares controller lifecycle APIs, queue freeze/quiesce APIs, passthrough/ioctl APIs, multipath APIs, hwmon APIs, auth APIs, zoned APIs, char-device helpers, command execution helpers, namespace lookup/refcount helpers, and exported attribute groups/operation tables.

## Control Flow
The header does not run standalone control flow, but it defines the shared state machine and call graph shape. Transports allocate a `struct nvme_ctrl`, provide `struct nvme_ctrl_ops`, call `nvme_init_ctrl()` / `nvme_add_ctrl()`, allocate admin and I/O tag sets, and transition controller state through `NVME_CTRL_NEW`, `CONNECTING`, `LIVE`, reset/delete states, and terminal states. Request paths use `struct nvme_request` as the common request-private prefix, initialize commands, call transport-specific queueing, then complete through `nvme_try_complete_req()`, `nvme_complete_rq()`, or batch completion.

Namespace code groups paths by `struct nvme_ns_head`; multipath builds on the optional fields under `CONFIG_NVME_MULTIPATH`. ioctl and io_uring paths use declared passthrough functions and command effects helpers. hwmon and auth are compiled as real hooks or no-op stubs depending on configuration.

## State And Persistence
`struct nvme_ctrl` is the main persistent runtime object. It stores controller identity, queues, device nodes, subsystem linkage, capabilities, limits, feature fields, work items, keepalive state, firmware activation work, fault injection, quirks, fabrics options, discard page state, optional ANA state, optional authentication state, TLS key identity, power-saving configuration, PCI-only host memory buffer fields, and namespace lists.

`struct nvme_subsystem` persists subsystem identity and shared namespace heads across controllers. `struct nvme_ns_head` stores identifiers, format information, features, cdev/disk, shared path list, and optional multipath state. `struct nvme_ns` stores per-controller namespace state, queue/disk, path sibling linkage, flags, cdev, and fault injection. `struct nvme_request` persists per-request command pointer, result, generation counter, retry count, flags, status, optional multipath accounting time, and controller pointer.

Most state is in-memory kernel state rebuilt from identify/log data and transport discovery. Some fields mirror device persistent configuration or capabilities, but this header itself only defines storage and APIs.

## Dependencies And Integration Points
The header includes Linux NVMe UAPI, cdev, PCI, kref, blk-mq, SED OPAL, fault injection, RCU/SRCU, waitqueues, T10 PI, ratelimit, and block trace headers. It is included across NVMe host source files and therefore forms the integration point between transport drivers, core, sysfs, block layer, char devices, multipath, hwmon, authentication, and zoned support.

`struct nvme_ctrl_ops` is the primary transport integration interface. It supplies register access, reset/delete/free behavior, async event submission, subsystem reset, address formatting, device info printing, P2P DMA support, and virtual boundary behavior. Feature-specific sections use `#ifdef` stubs so callers can compile regardless of configuration.

## Risks
This header has high blast radius. Layout changes to `struct nvme_request` are especially risky because transports require it to be the first member of request-private data. Changes to `struct nvme_ctrl`, `nvme_ns_head`, or `nvme_ns` affect many lifecycle paths and can break assumptions about locking, SRCU, or object ownership.

Inline helpers encode behavior, not just declarations. `nvme_try_complete_req()` increments command generation, stores status/result, performs fault injection, handles fake timeouts, and may complete remotely. `nvme_check_ready()` changes behavior for fabrics controllers in `NVME_CTRL_DELETING`. `nvme_is_unique_nsid()` controls whether multipath head disks may be created for private namespaces. Seemingly small edits can alter request completion, failover, or userspace-visible devices.

Configuration stubs must match real function signatures. Mismatches can hide compile coverage when features are disabled. Several fields are conditionally present under `CONFIG_NVME_MULTIPATH`, `CONFIG_NVME_HWMON`, `CONFIG_NVME_HOST_AUTH`, fault injection, and zoned block support, so structure users must stay inside the right guards.

## Test Signals
Build coverage should include representative configurations: with and without multipath, hwmon, host authentication, zoned block, fault injection, SED OPAL, and architectures with `CONFIG_ARCH_NO_SG_CHAIN`. Runtime tests should cover controller state transitions, reset/delete races, request timeout and completion generation counters, namespace add/remove, char and block device lifetime, multipath failover, hwmon init/exit, auth stubs versus real auth, command effects, and zoned operations.

Static analysis should check request-private layout assumptions, missing `#ifdef` guards, stale prototypes, enum/string mapping drift for quirks, and inline helpers that dereference optional fields. Lockdep, KASAN, refcount, and SRCU diagnostics are important because this header defines the shared objects used by most NVMe host concurrency paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/nvme.h -->
