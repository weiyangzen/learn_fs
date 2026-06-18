# subset-b-005954 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libfcoe.h -->
# sources/distributed-fs/ceph-client/include/scsi/libfcoe.h

## Purpose
This header defines the shared FCoE and FIP interface used by Open-FCoE software transports and low-level drivers. It is a contract layer between Ethernet `net_device` handling, libfc local/remote-port logic, FCoE sysfs objects, and driver-owned private state.

## Important APIs, Types, And Functions
The central state types are `struct fcoe_ctlr`, `struct fcoe_fcf`, `struct fcoe_rport`, `struct fcoe_transport`, `struct fcoe_percpu_s`, and `struct fcoe_port`. `enum fip_state` models controller progress from disabled/link-wait through auto, fabric FIP, non-FIP, and VN2VN probing/claim/up states. `enum fip_mode` is the low-level-driver selected target mode and is fixed after `fcoe_ctlr_init()`.

Controller APIs include `fcoe_ctlr_init()`, `fcoe_ctlr_destroy()`, `fcoe_ctlr_link_up()`, `fcoe_ctlr_link_down()`, `fcoe_ctlr_els_send()`, `fcoe_ctlr_recv()`, and `fcoe_ctlr_recv_flogi()`. Library helpers cover libfc setup, WWN derivation and formatting, CRC/trailer work, link-speed and LESB updates, vport validation, pending receive queues, and transport registration through `fcoe_transport_attach()` and `fcoe_transport_detach()`.

## Control Flow
Drivers allocate a controller plus private data, initialize it with a FIP mode, attach it to an `fc_lport`, and provide send/MAC callbacks. Link-up enters the configured discovery mode; received FIP SKBs are queued on `fip_recv_list` and processed by work items/timers. FCF advertisements populate the `fcfs` list, then selection updates `sel_fcf`, destination MACs, keepalive timers, and libfc login behavior. Data-plane receives flow through `fcoe_percpu_s` queues and `fcoe_port` pending-queue throttling.

## State And Persistence
All state is in-memory kernel state. Timers track solicitation, selection, and keepalive deadlines in jiffies. `fcoe_ctlr` combines mutex-protected controller state with a spinlock for `flogi_req`; `fcoe_percpu_s` uses a `local_lock_t`. No durable state is written here, but sysfs device objects expose selected controller/FCF state.

## Dependencies And Integration Points
The header depends on Ethernet, SKB, workqueue, timer, libfc, FCoE FC framing, and fcoe sysfs headers. It integrates with FC transport vports, netdev-backed software HBAs, module aliasing for FCoE PCI drivers, and per-netdev transport mapping.

## Risks
FIP state transitions are timing and locking sensitive. Incorrect callback implementations can leak SKBs, race MAC updates, or select an invalid FCF. MTU/CRC/trailer constants must match FC-over-Ethernet framing. VN2VN login retry limits and FCF selection limits are policy-sensitive and can affect discovery convergence.

## Test Signals
Useful validation includes link up/down sequencing, FIP advertisement selection, FLOGI receive/send paths, VN2VN probe/claim behavior, pending receive queue backpressure, CRC/trailer generation, sysfs controller create/destroy, vport validation, and module alias/transport attach-detach coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libfcoe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/libiscsi.h

## Purpose
This header defines the generic kernel iSCSI initiator library used by software and offload transports. It models hosts, sessions, connections, tasks, command-private data, management pools, error handling, PDU completion, and SCSI mid-layer integration.

## Important APIs, Types, And Functions
Core types are `struct iscsi_task`, `struct iscsi_conn`, `struct iscsi_session`, `struct iscsi_host`, `struct iscsi_pool`, and `struct iscsi_cmd`. Constants bound command counts, ITT encoding, connection flags, address storage, management-command pools, and task states. Inline helpers expose unsolicited data progress, next-header storage, task completion checks, command-private lookup, and iSCSI padding calculations.

Exported APIs include SCSI host template callbacks (`iscsi_queuecommand()`, abort/session/device/target reset handlers, timed-out handling), host allocation/add/remove/free, session setup/teardown/removal/free, parameter get/set, connection setup/bind/start/stop/unbind/failure, transmit/receive work queueing, PDU send/complete, ITT lookup/verification, task refcounting/requeue/completion, and pool/string helpers.

## Control Flow
A driver allocates an iSCSI host, creates a session with a command pool, then creates and binds one or more connections. SCSI commands enter through `iscsi_queuecommand()`, are represented by `iscsi_task`, and move through pending/running/completed or abort/recovery states. Connection transmit work drains management, command, and requeue lists under the forward lock. Receive completion updates CmdSN windows, verifies ITTs, completes SCSI tasks, or triggers recovery/failure.

## State And Persistence
State is volatile and split across host, session, connection, and task objects. The session has strict forward/back lock hierarchy for CmdSN windows, pools, queues, and state. Connection fields persist negotiated operational parameters, TCP/offload attributes, counters, and stats for the lifetime of the connection. User-visible persistent strings are stored as allocated pointers but are not durable storage.

## Dependencies And Integration Points
The header depends on SCSI command, iSCSI protocol/if, and iSCSI transport-class headers. It bridges SCSI mid-layer queueing and EH to the iSCSI control plane, sysfs transport classes, userspace parameter configuration, and transport-specific data through `dd_data`.

## Risks
Lock ordering is explicitly constrained; violating forward/back/eh mutex order can deadlock error recovery. ITT age/index handling must prevent stale-task completion. Queue-depth and pool sizes must remain power-of-two-compatible with masks. Recovery paths must not complete or requeue tasks after refcount teardown.

## Test Signals
Exercise login/session setup, command queuing and completion, R2T/unsolicited data tracking, PDU padding, ITT stale detection, abort/session/device reset EH, connection suspend/resume/failure, parameter round trips, stats counters, pool exhaustion, and command recovery timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi_tcp.h -->
# sources/distributed-fs/ceph-client/include/scsi/libiscsi_tcp.h

## Purpose
This header defines the common TCP data-path helpers for iSCSI. It gives software TCP transports reusable receive segmentation, scatterlist walking, CRC32C digest, task transmit, and R2T pool support on top of `libiscsi`.

## Important APIs, Types, And Functions
`struct iscsi_segment` tracks a receive or transmit segment, copied byte counts, total counts, digest buffers, optional scatterlist mapping, padding, and a completion callback. `struct iscsi_tcp_recv` stores the current PDU header context and a fixed BHS+AHS buffer. `struct iscsi_tcp_conn` binds TCP receive state and optional RX CRC pointer to a generic `iscsi_conn`. `struct iscsi_tcp_task` tracks DataSN/R2T progress and R2T pools/queues.

APIs include header receive preparation, SKB receive processing, task init/cleanup/xmit, segment completion/unmapping, linear and scatter-gather segment initialization, header digest calculation, TCP connection setup/teardown, R2T pool allocation/free, max-R2T parsing, and connection stats export.

## Control Flow
Receive processing prepares a header segment, consumes SKB bytes into the active segment, validates/pads/digests as needed, and advances through header, AHS, data, and digest stages. Transmit paths initialize task-private TCP state, select unsolicited or R2T data, and send task PDUs through the generic iSCSI session/connection framework.

## State And Persistence
All state is per-task or per-connection memory. Segment fields record progress across partial SKBs. R2T pools and FIFOs persist for the session/task lifetime and are protected by spinlocks for pool-to-queue and queue-to-pool transitions. No durable state is represented.

## Dependencies And Integration Points
The header depends directly on `libiscsi.h`, Linux scatterlists, SKBs, and digest constants from the iSCSI protocol. Low-level TCP transports provide socket or offload glue while reusing these helpers for PDU parsing and stats.

## Risks
Partial SKB handling, padding, and digest boundaries are error-prone. Incorrect scatterlist mapping or atomic unmapping can corrupt data or leak mappings. R2T pool sizing and lock use must handle concurrent recovery and cleanup. Digest offload callers must correctly set the `offloaded` receive flag.

## Test Signals
Use segmented SKB tests, header/data digest validation, padding edge cases, scatterlist offset seeks, R2T queue exhaustion, task cleanup during recovery, max-R2T setting changes, and stats accounting for transmitted/received PDUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libsas.h -->
# sources/distributed-fs/ceph-client/include/scsi/libsas.h

## Purpose
This header defines the libsas host-side class contract for SAS low-level drivers. It describes SAS HA, phy, port, discovery, domain-device, expander, SATA/SSP, task, and task-management abstractions plus callbacks drivers implement for discovery, I/O, resets, and GPIO.

## Important APIs, Types, And Functions
Important state types include `struct sas_ha_struct`, `struct asd_sas_phy`, `struct asd_sas_port`, `struct domain_device`, `struct expander_device`, `struct ex_phy`, `struct sata_device`, `struct ssp_device`, `struct sas_task`, `struct sas_task_slow`, and `struct sas_domain_function_template`. Event enums classify port, phy, and discovery events. Task status is modeled by `enum service_response`, `enum exec_status`, and `struct task_status_struct`.

The public API registers/unregisters HAs, suspends/resumes HAs, queues SCSI commands, allocates/configures targets/devices, handles queue depth and BIOS parameters, executes internal aborts, attaches SAS domain transport, handles EH abort/device/target resets, performs SMP/SSP task response work, finds phys, issues TMFs, and notifies port/phy events. `LIBSAS_SHT_BASE` macros populate common `scsi_host_template` entries.

## Control Flow
An LLDD fills HA/phy arrays and registers with libsas. Phy/port events enqueue `sas_work` on event/discovery workqueues, discovery builds `domain_device` trees, and device-found/gone callbacks notify the LLDD. SCSI commands become `sas_task` objects with SSP/STP/SMP/abort-specific unions. Completion fills `task_status_struct` and invokes `task_done`; errors route into SCSI EH and SAS TMF helpers.

## State And Persistence
State is in-memory and heavily asynchronous. HA state bits track registered, draining, ATA EH, frozen, and resuming modes. Ports maintain device/discovery/destroy lists and phy membership. Devices use krefs and bit-state flags for found/gone/reset/EH-pending. Locks include spinlocks, mutexes, waitqueues, workqueues, timers, and completions.

## Dependencies And Integration Points
libsas depends on SAS protocol definitions, SCSI device/command/transport SAS headers, libata, scatterlists, timers, PCI, workqueues, and block queues. It integrates with SCSI mid-layer host templates, libata for SATA/STP devices, SAS transport sysfs objects, and LLDD callbacks.

## Risks
Discovery and teardown races can leave devices in EH queues or destroy lists. Task completion must not race abort/reset state flags. LLDD callbacks have context constraints; TMFs require process context. Wide-port formation depends on address matching and strict-wide-port policy. ATA EH and SAS EH interactions are subtle.

## Test Signals
Validate HA register/unregister, phy up/down/OOB events, expander discovery/revalidation, SATA device reset/abort, SSP sense handling, queuecommand task creation, TMF abort/task-set/LU reset paths, internal aborts by tag/qid, drain/freeze/resume, and host-template macro behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libsas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas.h -->
# sources/distributed-fs/ceph-client/include/scsi/sas.h

## Purpose
This header contains SAS protocol constants and packed wire-format structures for SAS, SSP, SMP, SATA FIS embedding, task management, primitives, open reject reasons, GPIO register types, and endian-specific frame layouts.

## Important APIs, Types, And Functions
It defines address sizing/macros, SMP frame/function/result opcodes, SSP frame types, SAM task-management functions and responses, `enum sas_oob_mode`, `enum sas_device_type`, `enum sas_protocol`, `enum phy_func`, `enum sas_prim`, `enum sas_open_rej_reason`, and `enum sas_gpio_reg_type`. Wire types include `struct dev_to_host_fis`, `struct host_to_dev_fis`, `struct sas_identify_frame`, `struct ssp_frame_hdr`, `struct ssp_response_iu`, `struct ssp_command_iu`, `struct xfer_rdy_iu`, `struct ssp_tmf_iu`, `struct report_general_resp`, `struct discover_resp`, `struct report_phy_sata_resp`, and SMP wrapper responses.

## Control Flow
This header has no executable control flow. It provides the constants and layouts consumed by discovery, SMP command generation, SSP command/response parsing, task management, and SATA/STP tunneling. The preprocessor selects little-endian or big-endian bitfield layouts and fails compilation if bitfield order is unknown.

## State And Persistence
No runtime state is stored here. The packed structs represent transient on-wire frames and device responses. SAS addresses are eight-byte big-endian values, and hashed SAS addresses are three-byte protocol fields.

## Dependencies And Integration Points
The header depends on Linux fixed-width types and byteorder definitions. It is included by libsas and SAS transport headers and must match SAS/SMP/SSP protocol bit layouts expected by firmware, expanders, and low-level drivers.

## Risks
Packed bitfield layout is architecture-sensitive; incorrect endian definitions break protocol parsing. Flexible arrays in SSP responses require careful bounds checks. Constants overlap in protocol-defined ways and must not be interpreted without command context. The `SAS_ADDR()` macro assumes aligned-enough storage for dereferencing as `__be64`.

## Test Signals
Compile on little and big endian configurations, validate struct sizes/offsets against SAS specs, parse sample SMP discover/report-phy-SATA frames, build SSP command/TMF IUs, verify task management response decoding, and exercise SATA FIS passthrough through libsas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas_ata.h -->
# sources/distributed-fs/ceph-client/include/scsi/sas_ata.h

## Purpose
This header gates SATA-over-SAS support for libsas. It exposes helpers for identifying SAS domain devices that are SATA/STP targets and for scheduling ATA reset, aborting ATA links, executing ATA FIS commands, and exposing SAS ATA SCSI-device attributes.

## Important APIs, Types, And Functions
When `CONFIG_SCSI_SAS_ATA` is enabled, `dev_is_sata()` returns true for `SAS_SATA_DEV`, `SAS_SATA_PENDING`, `SAS_SATA_PM`, and `SAS_SATA_PM_PORT`. The header declares `sas_ata_schedule_reset()`, `sas_ata_device_link_abort()`, `sas_execute_ata_cmd()`, `smp_ata_check_ready_type()`, and `sas_ata_sdev_attr_group`. When disabled, it provides no-op or success-returning inline stubs and an empty attribute-group macro.

## Control Flow
The active path lets libsas and LLDD code branch on `dev_is_sata()` and call ATA-specific recovery or FIS execution helpers. The disabled path compiles out SATA behavior while preserving callers, so control flow continues without scheduling resets or aborting links.

## State And Persistence
No state is owned by this header. It operates on `struct domain_device`, `struct ata_link`, and libata-backed state embedded in `struct sata_device`.

## Dependencies And Integration Points
It includes `linux/libata.h` and `scsi/libsas.h`, connecting SAS discovery/EH to libata error handling and sysfs attributes. It is an integration point for STP/SATA devices discovered behind SAS expanders.

## Risks
The disabled stubs returning success can hide missing SATA support if callers assume an ATA command actually executed. `dev_is_sata()` must track `enum sas_device_type` changes. Link abort/reset calls must be coordinated with libata EH and SAS domain teardown.

## Test Signals
Build both with and without `CONFIG_SCSI_SAS_ATA`, verify SATA device detection, run ATA reset/link-abort paths through libsas, check SMP ATA readiness, and confirm sysfs attribute presence only when support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas_ata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi.h

## Purpose
This is a public SCSI initiator header collecting common mid-layer constants, timeout defaults, mode-select structures, well-known LUN helpers, disposition and queuecommand statuses, result-byte helpers, SCSI levels, inquiry qualifiers, ioctls, and good/check-condition status predicates.

## Important APIs, Types, And Functions
It exports `enum scsi_timeouts`, `struct ccs_modesel_head`, well-known LUN constants, `scsi_is_wlun()`, `scsi_status_is_check_condition()`, `enum scsi_disposition`, `enum scsi_qc_status`, `status_byte()`, `host_byte()`, sense byte macros, default long command timeouts, `IDENTIFY()`, SCSI level constants, legacy ioctl constants, and `scsi_status_is_good()`.

## Control Flow
The only executable logic is inline status classification. `scsi_status_is_check_condition()` rejects negative results, masks reserved bit 0, and compares against `SAM_STAT_CHECK_CONDITION`. `scsi_status_is_good()` rejects negative results and `DID_NO_CONNECT`, masks bit 0, then accepts GOOD, CONDITION_MET, obsolete intermediate successes, and COMMAND_TERMINATED for compatibility.

## State And Persistence
No state is owned here. Constants define ABI and mid-layer interpretation of packed result integers.

## Dependencies And Integration Points
It includes `scsi_common.h`, `scsi_proto.h`, and `scsi_status.h`. It is included broadly by drivers, transports, generic SG/ioctl code, and mid-layer error handling.

## Risks
Result-byte packing is an ABI convention; mixing shifted SG status values with SAM status values causes misclassification. Legacy ioctl values overlap with cdrom ranges and must stay stable. `scsi_status_is_good()` intentionally accepts obsolete statuses, which can surprise newer protocol logic.

## Test Signals
Unit-style status tests for negative values, DID_NO_CONNECT, check condition, obsolete intermediate status, and command terminated; ioctl ABI compile checks; and well-known LUN detection for ordinary and `0xc100`-based LUNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_bsg_iscsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_bsg_iscsi.h

## Purpose
This header defines the iSCSI transport BSG SG_IO v4 message ABI shared by kernel and userspace. It currently models host-class vendor messages and their replies.

## Important APIs, Types, And Functions
Key constants are `ISCSI_DEFAULT_BSG_TIMEOUT`, class masks `ISCSI_BSG_CLS_MASK` and `ISCSI_BSG_HST_MASK`, and message code `ISCSI_BSG_HST_VENDOR`. ABI structures are `struct iscsi_bsg_host_vendor`, `struct iscsi_bsg_host_vendor_reply`, `struct iscsi_bsg_request`, and `struct iscsi_bsg_reply`.

## Control Flow
There is no executable control flow. BSG consumers inspect `msgcode`, dispatch host vendor messages, use `vendor_id` to identify the recipient format, and return either a negative errno-style result or a packed SCSI result plus reply payload length.

## State And Persistence
No persistent state is represented. Request and reply structures are transient user/kernel ABI payloads, with flexible vendor command/response arrays.

## Dependencies And Integration Points
The header includes `scsi/scsi.h` and references vendor-id formatting rules from `scsi_netlink.h`. It integrates with iSCSI transport `bsg_request` callbacks and SG_IO v4 user commands.

## Risks
The timeout comment says seconds while the macro multiplies by `HZ`, so callers must interpret it as jiffies in-kernel. Flexible arrays require bounds validation. Vendor payloads are opaque, so ABI validation must happen in the transport callback.

## Test Signals
Validate SG_IO v4 host-vendor dispatch, negative errno result handling, packed SCSI result handling, reply length accounting, timeout behavior, and rejection of unknown class/message codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_bsg_iscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_cmnd.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_cmnd.h

## Purpose
This header defines `struct scsi_cmnd`, the SCSI mid-layer command object embedded in block requests, plus data-buffer, scatterlist, DMA, protection-information, residual, status-byte, and request conversion helpers.

## Important APIs, Types, And Functions
Important types are `struct scsi_data_buffer`, legacy `struct scsi_pointer`, `enum scsi_cmnd_submitter`, `struct scsi_cmnd`, `enum scsi_prot_operations`, `enum scsi_prot_flags`, and `enum scsi_prot_target_type`. Helpers convert between command and request (`scsi_cmd_to_rq()`), access driver-private command allocation (`scsi_cmd_priv()`), complete commands (`scsi_done()`, `scsi_finish_command()`), map DMA, inspect SG lists, copy buffers, compute sector/LBA/logical block count, manage residuals, set/get protection operation/type, access protection SG lists, set/get packed status and host bytes, translate SCSI message bytes, compute transfer length including protection information, build sense, and allocate SCSI requests.

## Control Flow
Commands are allocated as request private data, filled by the block/SCSI mid-layer, submitted to the host template, completed by the LLDD through `scsi_done()`, and finalized by the mid-layer. Inline helpers are used in the hot path for scatterlist iteration, LBA conversion, protection metadata handling, and result-byte updates. Message translation maps parallel-SCSI messages into host-byte error categories.

## State And Persistence
`struct scsi_cmnd` is transient per I/O. It tracks retry budget, submitter, command bytes, data buffers, sense buffer, flags, completion state, host scribble, result, residuals, and protection fields. The fields above the LLDD boundary are explicitly not to be modified by low-level drivers.

## Dependencies And Integration Points
It depends on block multiqueue, DMA mapping, T10 PI, scatterlists, timers, and `scsi_device.h`. It is the primary object exchanged between upper-level drivers, the SCSI core, transports, and LLDD queuecommand/EH callbacks.

## Risks
LLDDs modifying protected fields can corrupt mid-layer accounting. `scsi_get_lba()` assumes sector size is a power-of-two relation to 512-byte sectors. Protection transfer length must match integrity metadata. Packed result-byte updates can clobber unrelated bytes if masks are wrong.

## Test Signals
Exercise command allocation/private data sizing, SG copy helpers, DMA map/unmap fallback builds, residual accounting, status/host byte setting, message-to-host-byte mapping, protection metadata length, sense construction, and queuecommand completion lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_cmnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_common.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_common.h

## Purpose
This header provides SCSI helpers shared by initiator and target code: persistent-reservation type conversion, command-size parsing, CDB control-byte access, device type naming, LUN conversion, and normalized sense handling.

## Important APIs, Types, And Functions
It defines `enum scsi_pr_type`, converters `block_pr_type_to_scsi()` and `scsi_pr_type_to_block()`, `scsi_varlen_cdb_length()`, external `scsi_command_size_tbl`, `COMMAND_SIZE()`, `scsi_command_size()`, `scsi_command_control()`, `scsi_device_type()`, `int_to_scsilun()`, `scsilun_to_int()`, `struct scsi_sense_hdr`, `scsi_sense_valid()`, `scsi_normalize_sense()`, `scsi_build_sense_buffer()`, `scsi_set_sense_information()`, `scsi_set_sense_field_pointer()`, and `scsi_sense_desc_find()`.

## Control Flow
Inline command parsing branches on `VARIABLE_LENGTH_CMD`: variable CDBs derive length from the header, while fixed CDBs index the command-size table. Sense helpers normalize fixed or descriptor sense into `scsi_sense_hdr` and allow descriptor lookup and extra information/field-pointer population.

## State And Persistence
No persistent state is owned. The sense header is a compact transient representation of a larger sense buffer, and callers must retain the original buffer when detailed descriptors are needed.

## Dependencies And Integration Points
The header depends on Linux types, block persistent-reservation UAPI, and SCSI protocol constants. It is consumed by initiator, target, EH, SG, and drivers that need CDB/sense utility logic.

## Risks
Variable-length CDB parsing trusts the header enough to compute length; callers need buffer-length validation. Sense normalization can lose details if callers discard the original buffer. PR type conversion must stay in sync with block-layer reservation semantics.

## Test Signals
Validate CDB lengths for fixed and variable commands, control-byte extraction, LUN integer round trips, fixed/descriptor sense normalization, sense descriptor lookup, field-pointer insertion, and PR type conversion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dbg.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_dbg.h

## Purpose
This header declares SCSI debug formatting and printing helpers for commands, sense data, result codes, opcodes, sense keys, and host-byte/mid-layer return strings.

## Important APIs, Types, And Functions
Public declarations include `scsi_print_command()`, `__scsi_format_command()`, `scsi_print_sense_hdr()`, `scsi_print_sense()`, `__scsi_print_sense()`, `scsi_print_result()`, `scsi_opcode_sa_name()`, `scsi_sense_key_string()`, `scsi_extd_sense_format()`, `scsi_mlreturn_string()`, and `scsi_hostbyte_string()`. When `CONFIG_SCSI_CONSTANTS` is disabled, inline stubs return NULL or limited service-action recognition.

## Control Flow
The configured path formats and prints human-readable diagnostic data. The unconfigured path avoids constant tables: service-action names are only considered for commands where service actions are meaningful, and string lookups return NULL.

## State And Persistence
No state is owned. Output is transient logging/formatting data derived from command and sense buffers.

## Dependencies And Integration Points
The header forward declares SCSI command/device/sense types and relies on SCSI protocol constants for opcode checks. It integrates with driver diagnostics, EH logging, and mid-layer debug paths.

## Risks
Callers must tolerate NULL names when constants are disabled. Formatting command buffers must respect destination sizes. Debug output should not expose stale or uninitialized CDB/sense bytes.

## Test Signals
Build with and without `CONFIG_SCSI_CONSTANTS`, format common CDBs and variable/service-action CDBs, print fixed and descriptor sense, verify result string fallbacks, and check buffer truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_device.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_device.h

## Purpose
This header defines SCSI device and target objects, device state machines, events, VPD storage, queue-depth/blocking behavior, scan helpers, device-handler integration, internal command execution arguments, and many inline state/feature accessors.

## Important APIs, Types, And Functions
Core types are `struct scsi_mode_data`, `enum scsi_device_state`, `enum scsi_scan_mode`, `enum scsi_device_event`, `struct scsi_event`, `struct scsi_vpd`, `struct scsi_device`, `enum scsi_target_state`, `struct scsi_target`, `struct scsi_failure`, `struct scsi_failures`, and `struct scsi_exec_args`. APIs cover add/remove/get/put/lookup/iterate, target iteration, queue-depth changes/tracking, mode sense/select, TEST UNIT READY, VPD/opcode reports, state transitions, event allocation/send, quiesce/resume, scan/remove target, block/unblock, execute internal commands, internal command allocation, disk event disable/enable, VPD ID extraction, and runtime PM helpers.

## Control Flow
Devices are created in `SDEV_CREATED`, probed/configured, moved to `SDEV_RUNNING`, and later blocked, quiesced, offlined, canceled, or deleted through validated state transitions. Queue-full handling updates depth and blocking counters. Events are queued into `event_list` and processed by work. Internal commands use `scsi_execute_cmd()` with explicit retries, timeouts, sense, flags, and failure rules.

## State And Persistence
`struct scsi_device` stores host/queue links, target identity, inquiry/VPD data, black-list flags, feature quirks, power-management policy bits, queue accounting, event bitmaps, counters, sysfs devices, request SG settings, handler state, and aligned private data. `struct scsi_target` stores per-target lists, blocking/busy counters, target state, and transport private data.

## Dependencies And Integration Points
It depends on list/spinlock/workqueue/blk-mq/sbitmap/atomic primitives and SCSI core headers. It is a central integration point for SCSI hosts, upper-level drivers, device handlers, sysfs, VPD, runtime PM, block queues, and transport classes.

## Risks
State transitions are constrained by `scsi_device_set_state()`; bypassing them risks commands on deleted/offline devices. Many single-bit quirks encode compatibility behavior from `scsi_devinfo.h`; regressions can break old devices. VPD pointers are RCU-managed. Queue-depth ramping and blocking counters are concurrency-sensitive.

## Test Signals
Cover add/remove/get/put lifetimes, state transition acceptance/rejection, queue-full depth changes, target iteration locking variants, event delivery, VPD attach/update, mode sense/select fallbacks, internal command retry/failure matching, runtime PM stubs, and pseudo-device checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_devinfo.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_devinfo.h

## Purpose
This header defines typed blacklist/quirk flags for SCSI devices that need nonstandard scanning, probing, command, capacity, VPD, retry, or upper-driver behavior.

## Important APIs, Types, And Functions
Flags include LUN scan controls (`BLIST_NOLUN`, `FORCELUN`, `SPARSELUN`, `MAX5LUN`, `LARGELUN`, `REPORTLUN2`, `NOREPORTLUN`), broken protocol/feature controls (`BORKEN`, `NOTQ`, `INQUIRY_36`, `NO_VPD_SIZE`, `SKIP_VPD_PAGES`, `TRY_VPD_PAGES`, `NO_RSOC`, `NO_DIF`), removable/media quirks, capacity limits (`MAX_512`, `MAX_1024`), retry quirks, and upper-level-driver suppression. It also defines unused/high-unused masks.

## Control Flow
There is no executable flow. Scan and device-configuration code reads these bits and sets corresponding `scsi_device` and `scsi_target` fields that alter later command generation, probing, retry, and attachment behavior.

## State And Persistence
The flags are represented as `blist_flags_t`, a bitwise `__u64` type. Persistence is external to this header: device-info tables or module parameters assign flags, and `struct scsi_device::sdev_bflags` carries them at runtime.

## Dependencies And Integration Points
It depends on `blist_flags_t` from `scsi_device.h`. It integrates with device scanning, INQUIRY/VPD processing, REPORT LUNS, sd capacity logic, retry policy, and upper-level driver binding.

## Risks
Bits are ABI-like internal policy; reusing an unused bit incorrectly can collide with existing tables. Some flags are deprecated or compatibility-only but still affect real hardware. The `__BLIST_UNUSED_MASK` must reflect all reserved gaps.

## Test Signals
Table-driven tests should verify each flag maps to expected `scsi_device` or scan behavior, unused masks exclude active bits, and old quirk combinations still suppress/report LUNs, VPD, DIF, queueing, and capacity limits as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_devinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dh.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_dh.h

## Purpose
This header defines the SCSI device-handler infrastructure used mainly by multipath and special arrays to attach per-device policy for sense checking, activation, request preparation, parameter setting, and rescans.

## Important APIs, Types, And Functions
It defines device-handler result/error codes, `activate_complete`, and `struct scsi_device_handler` with list/module/name fields plus `check_sense`, `attach`, `detach`, `activate`, `prep_fn`, `set_params`, and `rescan` callbacks. If `CONFIG_SCSI_DH` is enabled it declares `scsi_dh_activate()`, `scsi_dh_attach()`, `scsi_dh_attached_handler_name()`, and `scsi_dh_set_params()`. If disabled it provides stubs.

## Control Flow
When enabled, a handler is registered, attached to a request queue/device, can prepare requests, classify sense into retry/fail/activate actions, and can asynchronously activate paths with a completion callback. Disabled builds immediately complete activation successfully but reject attach/parameter operations.

## State And Persistence
Handlers are runtime kernel modules linked on a global list and referenced by `struct scsi_device::handler` plus handler private data. No durable state is owned by the header.

## Dependencies And Integration Points
It includes `scsi_device.h` and integrates with request queues, SCSI sense handling, device state, and multipath/path activation logic.

## Risks
Disabled stubs have mixed semantics: activation succeeds but attachment returns unsupported. Callback completion must be invoked exactly once. Sense classification controls retry/fail behavior, so handler bugs can cause I/O loss or endless retries.

## Test Signals
Build both enabled/disabled configurations, attach/detach handlers, verify activation callback ordering, prep request behavior, sense classification results, parameter parsing, and path rescan interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_dh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_driver.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_driver.h

## Purpose
This header defines the upper-level SCSI driver registration wrapper around the Linux driver model and links `struct scsi_cmnd` commands back to their owning SCSI driver.

## Important APIs, Types, And Functions
`struct scsi_driver` embeds `struct device_driver` and provides callbacks for `probe`, `remove`, `shutdown`, `resume`, `rescan`, command init/uninit, command completion, EH action, and EH reset. Macros convert driver objects and wrap register/unregister calls. `scsi_register_interface()` and `scsi_unregister_interface()` expose class-interface hooks. `scsi_cmd_to_driver()` returns the command device's bound SCSI driver.

## Control Flow
Upper-level drivers register with `scsi_register_driver()`, probe matching `scsi_device` instances, initialize commands before submission, receive `done()` callbacks, and participate in EH-specific actions/resets. Interfaces can subscribe to SCSI class device events independently of a concrete ULD.

## State And Persistence
The only state defined here is driver callback storage in `struct scsi_driver`. Binding state lives in the driver core and `scsi_device::sdev_gendev.driver`.

## Dependencies And Integration Points
It depends on Linux device and block types plus `scsi_cmnd.h`. It integrates SCSI upper-level drivers such as disk/tape/sg with the generic driver model and SCSI command lifecycle.

## Risks
`scsi_cmd_to_driver()` must not be used for passthrough commands without a normal bound SCSI driver. Driver unregister must coordinate with outstanding commands and EH callbacks.

## Test Signals
Register/unregister ULDs, probe/remove devices, command init/uninit pairing, done callback invocation, class-interface registration, and passthrough command paths that avoid `scsi_cmd_to_driver()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_eh.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_eh.h

## Purpose
This header declares SCSI error-handler helpers for finishing recovered commands, reporting resets, blocking I/O while errors are processed, normalizing command sense, checking sense disposition, issuing ioctl resets, and temporarily replacing command contents for EH commands.

## Important APIs, Types, And Functions
Important APIs include `scsi_eh_finish_cmd()`, `scsi_eh_flush_done_q()`, `scsi_report_bus_reset()`, `scsi_report_device_reset()`, `scsi_block_when_processing_errors()`, `scsi_command_normalize_sense()`, `scsi_check_sense()`, `scsi_sense_is_deferred()`, `scsi_get_sense_info_fld()`, `scsi_ioctl_reset()`, `scsi_eh_prep_cmnd()`, and `scsi_eh_restore_cmnd()`. `struct scsi_eh_save` stores command/request state across EH preparation.

## Control Flow
EH can save a command, overwrite it with a REQUEST SENSE or reset-related command, submit it, then restore original fields. Completed EH commands are accumulated on a done queue and flushed back through normal completion. Sense analysis returns a mid-layer disposition for retry, success, fail, or other recovery actions.

## State And Persistence
EH save state is stack/transient and includes result, residual, flags, direction, underflow, CDB, data buffer, sense SG, and optional inline-encryption request fields. Reset reports update runtime device/host awareness but no durable state is defined.

## Dependencies And Integration Points
It depends on scatterlists, `scsi_cmnd.h`, and `scsi_common.h`. It integrates with SCSI host EH threads, ioctl reset handling, sense parsing, and command completion.

## Risks
Incomplete save/restore corrupts original I/O. Deferred sense detection depends on response-code bit semantics. Blocking while processing errors must avoid deadlocking device removal or runtime PM.

## Test Signals
Exercise prep/restore with normal and protection buffers, inline encryption builds, sense disposition matrix, deferred sense detection, reset reporting, ioctl reset paths, and done-queue flush ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_eh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_host.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_host.h

## Purpose
This header defines the SCSI host adapter template and `struct Scsi_Host`, the mid-layer representation of an HBA or virtual SCSI host. It is the main contract between LLDDs, transports, block multiqueue, scanning, error handling, protection information, and sysfs/proc integration.

## Important APIs, Types, And Functions
`struct scsi_host_template` declares queueing, reserved queueing, commit, info, ioctl/compat ioctl, command-private init/exit, EH handlers, device/target allocation/configuration/destruction, scan callbacks, queue-depth changes, queue mapping/polling, DMA drain, BIOS params, native capacity unlock, timeout/retry hooks, host reset, capacity/SG/DMA limits, mode flags, attribute groups, and vendor ID. `enum scsi_timeout_action`, `enum scsi_host_state`, `struct Scsi_Host`, `DEF_SCSI_QCMD`, protection capability enums, guard enums, and helpers like `shost_priv()`, `dev_to_shost()`, `scsi_host_in_recovery()`, `scsi_add_host()`, scan/remove/get/put/block/unblock APIs are central.

## Control Flow
Drivers fill a host template, allocate a host, add it with a parent/DMA device, scan it, accept commands through `queuecommand`, and complete them asynchronously. EH callbacks run in the EH thread with normal queueing stopped. Host state controls scanning, recovery, deletion, and request blocking. Transport templates may add host/target/device private data and workqueues.

## State And Persistence
`Scsi_Host` stores device/target lists, locks, scan mutex, EH queues/thread, blk-mq tag set, host failure counters, IDs/limits, queue capabilities, runtime mode bits, workqueues, PI capabilities, legacy I/O fields, sysfs devices, pseudo-device, transport data, DMA device, autosuspend delay, and aligned driver private hostdata. State is volatile but exposed through sysfs/proc.

## Dependencies And Integration Points
It depends on block, device, workqueue, SCSI device/command/transport concepts, and optional procfs. It is used by all SCSI LLDDs and transport classes including SAS, FC, iSCSI, SPI, and SRP.

## Risks
`queuecommand` return semantics are strict: accepted commands must complete, rejected commands must not be touched. EH context must not race normal queueing. Host/device private data sizing must align with transport reservations. Host-wide tagsets and queue mapping affect block-layer concurrency. State changes require the mid-layer enforcer.

## Test Signals
Validate host allocation/add/remove/lookup, queuecommand accept/reject/commit paths, reserved commands, EH handlers and timeouts, scan callbacks, queue limits, host block/unblock, busy iteration, PI/DIX capability helpers, guard type settings, procfs conditional builds, and driver-private data offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_ioctl.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_ioctl.h

## Purpose
This header defines legacy SCSI ioctl command numbers and kernel helper prototypes for SCSI ioctl dispatch, SG_IO header copying, command permission checks, and blocking ioctls during error handling.

## Important APIs, Types, And Functions
It defines basic ioctl commands such as SEND_COMMAND, TEST_UNIT_READY, START/STOP_UNIT, DOORLOCK/DOORUNLOCK, and removal-prevention constants. Under `__KERNEL__`, it defines `Scsi_Ioctl_Command`, `Scsi_Idlun`, and `Scsi_FCTargAddress`, plus `scsi_ioctl_block_when_processing_errors()`, `scsi_ioctl()`, `get_sg_io_hdr()`, `put_sg_io_hdr()`, and `scsi_cmd_allowed()`.

## Control Flow
Block or character device ioctl paths call `scsi_ioctl()`, which must gate commands based on write permission, error-processing state, and command allowlists before passing work to SCSI/SG execution. SG_IO headers are copied in/out through dedicated helpers.

## State And Persistence
No state is stored here. Structures are ABI payloads exchanged with userspace and transient kernel copies.

## Dependencies And Integration Points
It integrates SCSI block devices, sg passthrough, reset/error handling, FC target-address reporting, and userspace legacy ioctl ABI. Kernel-only declarations depend on `scsi_device`, `gendisk`, and `sg_io_hdr`.

## Risks
Legacy ioctl ABI cannot change. Passthrough command permission must prevent destructive commands without write access. Error-handler blocking must avoid returning unsafe success during recovery. User pointer copying requires compat and bounds care in implementation.

## Test Signals
Check ioctl number stability, command allow/deny matrix by open mode, SG_IO header copy round trips, reset command behavior during EH, door lock/unlock commands, and legacy IDLUN/FC address ABI layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_proto.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_proto.h

## Purpose
This header defines SCSI protocol constants shared by initiator and target code: CDB opcodes, service actions, command sizes, SAM status, sense keys, device types, protocol identifiers, LUN layout, IO advice/stream descriptors, ALUA access states, ZBC zone reporting, version descriptors, and supported-opcode states.

## Important APIs, Types, And Functions
Important definitions include command opcodes from six-byte through variable-length and service-action commands, `SCSI_MAX_VARLEN_CDB_SIZE`, `struct scsi_varlen_cdb_hdr`, `enum sam_status`, sense-key constants, `TYPE_*` peripheral device constants, `enum scsi_protocol`, `struct scsi_lun`, `struct scsi_io_group_descriptor`, `struct scsi_stream_status`, `struct scsi_stream_status_header`, ALUA access-state masks, ZBC reporting/type/condition enums, `enum scsi_version_descriptor`, `enum scsi_support_opcode`, and static assertions for descriptor sizes.

## Control Flow
There is no runtime control flow. The header is consumed by CDB construction, command parsing, sense/status classification, inquiry parsing, ALUA, zoned block command handling, persistent reservations, and target/initiator protocol reporting.

## State And Persistence
No kernel state is owned here. The structs represent on-wire or standards-defined payloads and must stay size/layout stable.

## Dependencies And Integration Points
It depends on build assertions and Linux fixed-width/endian types. It is the protocol vocabulary for virtually all SCSI headers in this shard plus users of SCSI CDBs and responses.

## Risks
Opcode aliases require context-aware interpretation. Endian bitfields in IO advice and stream descriptors must match the protocol. Typographical constants, even if historically present, can become ABI expectations. Static size checks protect only selected structures.

## Test Signals
Compile-time size assertions, CDB opcode table coverage, service-action dispatch tests, SAM status classification, inquiry device-type/modality tests, ALUA state parsing, ZBC report parsing, and cross-build endian validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_status.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_status.h

## Purpose
This header defines SCSI message byte codes and host-byte result codes used in packed SCSI command results.

## Important APIs, Types, And Functions
`enum scsi_msg_byte` includes command completion, extended messages, save/restore pointers, disconnect, initiator/parity errors, abort/clear/reset task management messages, queue tag messages, ACA, QAS, and old SCSI-2 aliases. `enum scsi_host_status` defines `DID_OK`, connection/bus/timeout/target/abort/parity/error/reset/interruption statuses, passthrough, soft/immediate retry, requeue, transport disrupted/failfast/marginal, and compatibility gaps.

## Control Flow
There is no executable flow. Other helpers, especially in `scsi_cmnd.h` and `scsi.h`, pack these host status values into `cmd->result` and translate protocol messages into mid-layer error categories.

## State And Persistence
No state is owned. Values are ABI-visible through SG_IO and driver result reporting.

## Dependencies And Integration Points
It includes SCSI protocol constants and is used by SCSI commands, EH, SG, transports, and low-level drivers to communicate completion or transport status.

## Risks
Changing numeric values breaks userspace and driver ABI. Some old names are aliases and should not guide new code. The unused host-status block is intentionally reserved for compatibility with userspace parsers.

## Test Signals
Validate result packing/unpacking, SG_IO host status reporting, message-to-host-byte translation, transport failfast/disrupted behavior, and preservation of alias values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_tcq.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_tcq.h

## Purpose
This header provides tagged command queue lookup support for SCSI hosts using blk-mq tags.

## Important APIs, Types, And Functions
It defines `SCSI_NO_TAG` and, when `CONFIG_BLOCK` is enabled, inline `scsi_host_find_tag(struct Scsi_Host *shost, int tag)`. The helper decodes a unique blk-mq tag into hardware queue and per-queue tag, looks up the request from the host tag set, verifies the request has started, and returns the embedded `struct scsi_cmnd`.

## Control Flow
Callers pass a tag from an active command or task-management context. The helper rejects `SCSI_NO_TAG`, rejects hardware queue indices outside the tag set, rejects missing or not-started requests, and otherwise converts request private data back into a SCSI command.

## State And Persistence
No state is owned. It reads the live `Scsi_Host::tag_set` and active request state.

## Dependencies And Integration Points
It depends on block, SCSI command/device/host headers, and blk-mq unique tag helpers. It is used by LLDDs and EH/TMF code that need to find an outstanding command from a tag.

## Risks
Tags are only valid while the request is active. Multi-queue tags must be unique blk-mq tags, not raw hardware tags. Concurrent completion can race lookup, so callers need appropriate context/lifetime protection.

## Test Signals
Test `SCSI_NO_TAG`, invalid hardware queue tags, inactive requests, valid single-queue and multi-queue tags, and races with command completion under lockdep/KCSAN-style checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_tcq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport.h

## Purpose
This header defines the generic SCSI transport template used by FC, SAS, iSCSI, SPI, SRP, and other transports to add host/target/device attributes, private data, user scan hooks, workqueues, and optional EH strategy overrides.

## Important APIs, Types, And Functions
`struct scsi_transport_template` contains host/target/device `transport_container`s, `user_scan`, size/private-offset fields for device/target/host data, `create_work_queue`, and `eh_strategy_handler`. Helpers reserve target or device private space, retrieve transport target/device private data from `scsi_target`/`scsi_device`, map transport classes to `Scsi_Host`, and initialize queue limits through `scsi_init_limits()`.

## Control Flow
Transport attach code sizes attribute/private areas before hosts/devices/targets are allocated. Reservation helpers may be called only once per target or device private offset and use `BUG_ON()` to enforce that. Later, drivers use the offset helpers to access their private area behind transport-managed data.

## State And Persistence
The template stores allocation sizing and class containers. Per-object state lives in `Scsi_Host::shost_data`, `scsi_target::starget_data`, or `scsi_device::sdev_data` based on these sizes and offsets.

## Dependencies And Integration Points
It depends on Linux transport class, block queues, bug checks, SCSI host, and SCSI device headers. It is the base template embedded/returned by transport-specific attach functions.

## Risks
Private offsets must be reserved before object allocation and only once. Mis-sized areas corrupt adjacent transport or driver data. `BUG_ON()` makes misuse fatal. Queue-limit initialization must remain consistent with host template limits.

## Test Signals
Validate private-data offsets and alignment, duplicate reservation failure, target/device data retrieval with multiple transports, user-scan callbacks, transport workqueue creation, EH strategy override invocation, and queue-limit initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_fc.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_fc.h

## Purpose
This header defines the Fibre Channel SCSI transport class: FC host, remote-port, virtual-port, target attributes, FC statistics/events, sysfs visibility flags, BSG helpers, and ready/error behavior for FC transports.

## Important APIs, Types, And Functions
Important enums/constants cover FC port types/states, vport states, classes of service, speeds, target-ID binding, port roles, event codes, and vport error returns. Structures include `fc_vport_identifiers`, `struct fc_vport`, `fc_rport_identifiers`, `fc_fpin_stats`, `fc_encryption_info`, `struct fc_rport`, `fc_starget_attrs`, `fc_host_statistics`, `fc_host_attrs`, and `fc_function_template`. APIs attach/release transport, remove hosts, add/delete/role-change remote ports, post events/vendor events/FPINs, create/terminate vports, block rports/EH, and handle timeouts/retry decisions.

## Control Flow
LLDDs attach a transport with an `fc_function_template`, set host attributes, add remote ports as topology is discovered, and optionally create NPIV vports. `fc_remote_port_chkready()` gates I/O based on rport state, role, dev-loss, and fast-fail flags. Work items manage dev-loss, scans, fast-fail, target deletion, rport deletion, and vport deletion. Event APIs publish async FC state to netlink/sysfs consumers.

## State And Persistence
Host attributes store fixed/dynamic FC identity, speeds, FC4s, fabric name, discovered rports/vports, counters, workqueues, BSG queue, and FPIN stats. Rports and vports store transport-managed state, flags, delayed work, devices, and driver-private data. State is runtime/sysfs visible, not durable.

## Dependencies And Integration Points
It depends on scheduler, BSG, unaligned access, SCSI netlink, SCSI host, and SCSI status. It integrates with FC HBAs, libfc/FCoE, SCSI targets, vport NPIV management, BSG vendor commands, and SCSI EH.

## Risks
Rport state transitions drive data loss vs retry behavior; dev-loss and fast-fail timers must be coordinated. Sysfs visibility flags must match implemented callbacks. WWN conversion uses unaligned big-endian helpers. Vport state updates assume external locking.

## Test Signals
Exercise rport add/delete/role changes, `fc_remote_port_chkready()` matrix, dev-loss/fast-fail timers, vport create/delete/disable, host/rport sysfs attributes, FC event posting, FPIN receive stats, BSG host/rport mapping, and EH timeout retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_iscsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_iscsi.h

## Purpose
This header defines the iSCSI transport class control plane for software and hardware/offload transports. It covers transport callback templates, class session/connection/host/endpoint/interface objects, flashnode configuration objects, events, BSG, and helper allocation/lifecycle APIs.

## Important APIs, Types, And Functions
`struct iscsi_transport` contains callbacks for session/connection creation/binding/start/stop/destruction, parameter get/set, PDU send/stats, task init/xmit/cleanup, PDU allocation/transmit/init, ITT parsing, recovery timeout, endpoint connect/poll/disconnect, discovery/path/interface operations, BSG, ping, CHAP, flashnode operations, host stats, and protection checks. State objects include `iscsi_cls_conn`, `iscsi_cls_session`, `iscsi_cls_host`, `iscsi_endpoint`, `iscsi_iface`, `iscsi_bus_flash_conn`, and `iscsi_bus_flash_session`.

## Control Flow
Transports register a template, allocate sessions under a host, add targets, allocate/bind/start connections, and report login/error/PDU/offload/host events to the class. Session work items block/unblock/scan/unbind/destroy targets and delayed work handles recovery timeout. Endpoint APIs model socket/offload connection handles. Flashnode APIs expose firmware-stored discovery/session configuration.

## State And Persistence
Class session/connection state is runtime device-model state with locks, work items, recovery timers, target IDs, creator PID, and private data. Flashnode session/connection structures model firmware-persistent configuration parameters, credentials indices, discovery parent data, and boot-target state, though actual persistence is owned by hardware/firmware.

## Dependencies And Integration Points
It depends on Linux device/list/mutex and `iscsi_if.h`, and integrates with SCSI hosts, iSCSI userspace management via netlink/events, BSG, firmware offload, CHAP management, endpoint lifetimes, and `libiscsi`.

## Risks
Connection `ep_mutex` and spinlock protect different startup/binding/cleanup state; misuse can race endpoint disconnect and workqueue cleanup. Many callbacks return `-ENODATA` for unsupported params, which userspace depends on. Flashnode credential strings/indices need careful lifetime and security handling. Recovery timeout overrides affect failover behavior.

## Test Signals
Validate transport register/unregister, session/connection lifecycle, bind/unbind races, block/unblock/scan work, endpoint lookup/refcounting, parameter get/set unsupported cases, login/error/PDU events, BSG requests, ping completion, CHAP CRUD, flashnode create/login/logout/destroy, and protection callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_iscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_sas.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_sas.h

## Purpose
This header defines the generic SAS transport class sysfs/device model for SAS phys, ports, remote phys/end devices/expanders, link rates, TLR, SMP BSG handling, and driver callback templates.

## Important APIs, Types, And Functions
Key types include `enum sas_linkrate`, `struct sas_identify`, `struct sas_phy`, `struct sas_rphy`, `struct sas_end_device`, `struct sas_expander_device`, `struct sas_port`, `struct sas_phy_linkrates`, and `struct sas_function_template`. APIs allocate/add/delete/free phys, rphys, and ports; add/delete phys to ports; remove children/hosts; query SAS address/TLR/ATA NCQ priority; attach/release transport; read port mode page; and identify SAS device/phy/port/local/expander devices.

## Control Flow
Drivers attach a SAS transport template, allocate phys and ports under host devices, attach rphys for end devices or expanders, and expose link/error attributes. SMP requests can be dispatched through the template `smp_handler`. Port membership is managed by adding/removing phys, while rphy add/remove/delete controls remote-device visibility and SCSI target binding.

## State And Persistence
Transport objects are runtime device-model objects. Phys track enable state, negotiated/min/max link rates, error counters, SAS identity, port siblings, and hostdata. Ports track phy lists and remote rphy under a mutex. End devices track ready LED and TLR settings; expanders track vendor/product/component strings and levels.

## Dependencies And Integration Points
It depends on Linux transport class, mutex, BSG, SAS protocol definitions, and SCSI host/device model. It is used by libsas and SAS LLDDs to expose topology through sysfs and BSG.

## Risks
The `scsi_is_sas_rphy()` stub returns false when attrs are disabled, so code must handle feature-gated builds. Device lifetimes depend on `put_device()` helpers. Linkrate constants include virtual values outside normal four-bit SAS fields. TLR/NCQ helpers depend on remote/device type.

## Test Signals
Build with/without `CONFIG_SCSI_SAS_ATTRS`, allocate/add/delete phys/rphys/ports, SMP BSG dispatch, link error retrieval, phy reset/enable/speed callbacks, TLR enable/disable, expander detection, local phy detection, and port phy refcounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_spi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_spi.h

## Purpose
This header defines the parallel SCSI SPI transport attributes exported to sysfs, including negotiation parameters, domain validation state, signaling type, driver callbacks, and message population helpers.

## Important APIs, Types, And Functions
`struct spi_transport_attrs` stores period/offset/width/IU/DT/QAS/flow/streaming/RTI/precomp/hold-MCS negotiation state, device capability bits, driver flags, and domain-validation mutex/state. `enum spi_signal_type` and `struct spi_host_attrs` model host signaling. Accessor macros map target/host private data to attributes. `struct spi_function_template` contains get/set callbacks and sysfs visibility bits. APIs attach/release transport, schedule/run domain validation, display transfer agreements, print messages, and populate width/sync/PPR/tag messages.

## Control Flow
Transport attach reserves target/host attribute storage. Drivers set capabilities and callbacks. Sysfs get/set invokes template callbacks, while domain validation can be scheduled per device and serialized by `dv_mutex`. Message helpers construct protocol negotiation messages used by LLDDs.

## State And Persistence
SPI state is stored in `scsi_target::starget_data` and `Scsi_Host::shost_data`. Domain-validation pending/in-progress bits and mutex serialize runtime validation. No durable state is owned.

## Dependencies And Integration Points
It depends on Linux transport class and mutex, and forward-declares SCSI target/device/host/command types. It integrates with older parallel SCSI LLDDs, sysfs transport attributes, and negotiation message construction.

## Risks
Accessor macros assume the transport data layout is installed. Domain validation can race target removal if lifetimes are not held. Negotiation values must match protocol units expected by SDTR/PPR messages. Visibility bits must align with implemented callbacks.

## Test Signals
Attach/release transport, sysfs attribute get/set callbacks, DV scheduling and serialization, sync/wide/PPR/tag message bytes, signaling changes, deny-binding callback, and target private-data accessor alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_srp.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_srp.h

## Purpose
This header defines the SCSI RDMA Protocol transport class for SRP remote ports, reconnection/fail-fast/dev-loss timers, and initiator-driver callbacks.

## Important APIs, Types, And Functions
It defines SRP rport roles, `struct srp_rport_identifiers`, `enum srp_rport_state`, `struct srp_rport`, and `struct srp_function_template`. APIs attach/release the transport, get/put/add/delete rports, validate and parse timeout values, reconnect rports, start/stop transport-layer fail timers, remove hosts, handle command timeout with `srp_timed_out()`, and gate I/O with `srp_chkready()`.

## Control Flow
Drivers add SRP rports to a host. In normal state, I/O proceeds. When connectivity is disrupted, reconnect work and fast-I/O-fail/dev-loss delayed work transition rports through blocked, fail-fast, and lost states. `srp_chkready()` maps those states to SCSI result codes for queuecommand paths.

## State And Persistence
`struct srp_rport` stores device identity, 16-byte port ID, role, LLDD private data, mutex-protected state, reconnect delay/counter, and delayed work for reconnect, fast fail, and dev loss. State is runtime and sysfs-visible depending on template flags.

## Dependencies And Integration Points
It depends on transport class, Linux types, mutexes, SCSI host/status/command concepts, and SRP initiator LLDDs. It parallels FC remote-port ready checking but for RDMA/SRP transports.

## Risks
Timer validation must prevent nonsensical reconnect/fast-fail/dev-loss ordering. `srp_chkready()` deliberately allows blocked I/O unless fail-fast/lost, so timeout policy is critical. Reconnect callbacks must coordinate with outstanding I/O termination and rport deletion.

## Test Signals
Validate rport add/delete/refcounting, timeout parsing and validation, reconnect work scheduling, fast-fail/dev-loss transitions, `srp_chkready()` state matrix, `srp_timed_out()` behavior with `reset_timer_if_blocked`, and host removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_srp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsicam.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsicam.h

## Purpose
This small header declares SCSI CAM geometry helper functions used for legacy BIOS/HDIO geometry reporting and partition-table interpretation.

## Important APIs, Types, And Functions
It forward declares `struct gendisk` and declares `scsicam_bios_param()`, `scsi_partsize()`, and `scsi_bios_ptable()`. The functions derive BIOS-style heads/sectors/cylinders, inspect partition size geometry, and locate BIOS partition table data.

## Control Flow
There is no inline control flow. Implementations are called by disk/BIOS-parameter paths when userspace requests legacy geometry or when SCSI disk code needs CAM-compatible calculations.

## State And Persistence
No state is owned. Functions operate on a `gendisk`, capacity, and caller-provided geometry arrays or returned partition-table memory.

## Dependencies And Integration Points
It integrates SCSI disk code with block `gendisk` and legacy HDIO geometry expectations. It is compatibility-oriented rather than part of modern command processing.

## Risks
Legacy geometry is synthetic and can be wrong for large disks. Returned partition-table pointers need clear ownership/lifetime in implementation. Geometry calculations must avoid overflow with large `sector_t` capacities.

## Test Signals
Test geometry output for small, boundary, and large capacities; partition-table parsing with valid and invalid MBR data; and HDIO_GETGEO compatibility behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsicam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sg.h -->
# sources/distributed-fs/ceph-client/include/scsi/sg.h

## Purpose
This header defines the SCSI generic userspace ABI for SG v3 and legacy SG interfaces: SG_IO request headers, iovec compatibility, status/info flags, ioctl numbers, reset values, defaults, request table entries, and old `sg_header`.

## Important APIs, Types, And Functions
Key ABI types are `sg_iovec_t`, `sg_io_hdr_t`, kernel-only `compat_sg_io_hdr`, `sg_scsi_id_t`, `sg_req_info_t`, and legacy `struct sg_header`. Constants define transfer directions (`SG_DXFER_*`), flags (`DIRECT_IO`, `MMAP_IO`, queue placement, no transfer), info bits, obsolete driver/status helpers, SG ioctl numbers, reset scopes, buffer/default queue sizes, timeout defaults, command queue controls, debug controls, and alternate typedef names.

## Control Flow
The ABI supports synchronous `SG_IO` and write/read style command submission. Userspace fills `sg_io_hdr`, command and data pointers, timeout, flags, and pack IDs; the kernel returns SCSI/masked/message/host/driver status, sense length, residual, duration, and info. Legacy `sg_header` paths preserve old write/read behavior and command-length override ioctls.

## State And Persistence
No kernel state is owned by the header, but ioctl constants manipulate per-file sg driver state such as reserved buffer size, force-pack-id, keep-orphan, command queueing, timeout, and debug flags. ABI structs must remain stable for userspace.

## Dependencies And Integration Points
It depends on compiler annotations and kernel compat types under `__KERNEL__`. It integrates userspace passthrough utilities, sg driver implementation, block/SCSI status packing, ioctl reset handling, and compatibility for 32-bit userspace.

## Risks
This is ABI-sensitive: layout, ioctl numbers, and shifted legacy status values must not change. User pointers and iovec counts require strict validation in implementation. Direct/mmap/no-transfer flags can affect data exposure and copying. Obsolete status/driver fields are retained for compatibility even when mid-layer semantics changed.

## Test Signals
Run SG_IO read/write/no-data passthrough, direct and mmap IO, iovec scatter-gather, sense-buffer truncation, residual and duration reporting, pack-id/orphan behavior, reset ioctls, compat 32-bit SG_IO, legacy `sg_header` commands, and ioctl number ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sg.h -->
