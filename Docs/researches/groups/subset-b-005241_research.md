# Research Group subset-b-005241

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcpim.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcpim.c

## Purpose
`bfa_fcpim.c` implements the HAL-side Fibre Channel Protocol initiator module for the QLogic/Brocade BR-series driver. It owns the runtime mechanics for initiator-target nexus objects (`bfa_itnim_s`), SCSI IO objects (`bfa_ioim_s`), task-management objects (`bfa_tskim_s`), IO tags, firmware request construction, firmware completion dispatch, offline path timeout behavior, LUN masking, IO profiling, and persistent throttle configuration. It is the lower half of the FCS FCP initiator path: FCS code negotiates FC-4 state and then calls into this file to create, online, offline, and delete firmware ITN resources and to execute host SCSI requests.

## Important APIs, Types, And Functions
The public entry points are the module hooks `bfa_fcp_meminfo()`, `bfa_fcp_attach()`, `bfa_fcp_iocdisable()`, and `bfa_fcp_res_recfg()`, plus ITN/IO/TM APIs declared in `bfa_fcpim.h`: `bfa_itnim_create/delete/online/offline()`, `bfa_ioim_alloc/free/start/abort()`, and `bfa_tskim_alloc/free/start()`. `bfa_itn_create()` and `bfa_itn_isr()` bind per-rport ITN firmware messages to an ISR function. `bfa_iotag_attach()` builds the IO tag pools.

`bfa_itnim_s` objects are preallocated per remote port and maintain active IO, cleanup IO, pending IO, task-management, and delayed-completion queues. `bfa_ioim_s` tracks one SCSI command, its firmware IO tag, SG page allocation, request queue wait item, completion callback state, and retry tag bits. `bfa_tskim_s` tracks task-management commands, affected IOs, wait counters, and firmware task status. The FCPIM module object stores resource arrays, free queues, active IO count, path timeout, IO profiling callbacks, deleted-ITN aggregate stats, and throttle state.

## Control Flow
Attach/memory flow starts in `bfa_fcp_meminfo()`, which clamps IO/TM counts, sizes KVA objects, and sizes DMA sense buffers. `bfa_fcp_attach()` records firmware-configured resource counts, registers sense-buffer DMA addresses with IOCFC, attaches FCPIM submodules, initializes IO tags, and builds the ITN dispatch table. `bfa_fcp_res_recfg()` later moves excess IO tags to `iotag_unused_q` after firmware reports effective throttle limits.

ITN control is a state machine from uninitialized to created, firmware create, online, cleanup, firmware delete, offline, IOC-disable, and deletion variants. `bfa_itnim_online()` sends a firmware ITN create request, while offline/delete paths clean up IO/TM resources before sending firmware delete. Request queue back-pressure moves states into `*_qfull` variants and resumes through `bfa_reqq_wait()` callbacks. Firmware create/delete/SLER messages enter through `bfa_itnim_isr()`.

IO control starts with `bfa_ioim_alloc()`, which consumes an IO tag and adds the IO to the ITN active queue. `bfa_ioim_start()` chooses a request queue, optionally allocates SG pages, builds `bfi_ioim_req_s`, maps scatter-gather entries, copies SCSI CDB/LUN/direction/data length, and produces a firmware request. Completions enter through `bfa_ioim_isr()` or `bfa_ioim_good_comp_isr()` and are translated into state-machine events such as good completion, normal completion, done-with-resource-held, resource-free, host-aborted, unknown-tag, and sequence-recovery retry. Callback states queue driver completions and only free IO resources after callbacks and firmware resource-free semantics allow it.

Task-management flow uses `bfa_tskim_start()` to gather affected IOs by LUN or target-reset scope, send a firmware TM command, then clean up gathered IOs after firmware response. If the ITN is already offline, the TM does not go on wire and only cleans up scoped IOs. TM abort/cleanup paths mirror IO cleanup with queue-full and IOC-failure states.

## State And Persistence Behavior
Most state is in preallocated arrays and Linux lists. Wait counters (`bfa_wc_s`) are used as barriers before ITN or TM cleanup completion. Offline path timeout (`path_tov`) holds pending IO while an ITN is temporarily offline; timer expiry fails held IO with `BFI_IOIM_STS_PATHTOV`, while a return online fails delayed completions with retryable abort-style status. IO profiling is transient: enabling clears ITN stats, records start time, and installs start/complete callbacks that bucket latency by transfer size. Persistent behavior is limited to dynamic config: LUN mask updates and throttle writes call `bfa_dconf_update()`, and throttle reads/writes use the dconf throttle config when available.

## Dependencies And Integration Points
This file depends on BFA core queue, timer, wait-counter, request-queue, SG page, DMA memory, callback queue, tracing, and firmware-interface helpers. It consumes SCSI core types (`struct scsi_cmnd`, `struct scsi_lun`, scatterlists, DMA direction) and Fibre Channel protocol builders/definitions. It integrates upward with BFAD via `bfa_cb_ioim_*()` and `bfa_cb_tskim_done()` callbacks, and with FCS through ITN callbacks (`bfa_cb_itnim_online/offline/sler/tov*`) and LUN-mask lookup through `bfa_fcs_lookup_port()`/rport lookup.

## Risks And Edge Cases
The file is dominated by asynchronous state-machine races: queue-full resume, firmware completion, host abort, cleanup, callback cancellation, IOC failure, path timeout, and resource-free events can interleave. Several paths rely on WARNs rather than recoverable errors when tags or queues are unexpected. `BFA_IOIM_FROM_TAG` and `BFA_ITNIM_FROM_TAG` mask tags into preallocated arrays, so firmware/driver tag consistency is critical. Delayed completions are subtle because callback queue entries may be dequeued and moved under ITN timeout policy. LUN mask operations scan fixed arrays and persist immediately; duplicate/free-index handling and min-config checks are important. The IO profile comments note a time overflow concern in the profile start-time representation.

## Test Signals
Useful tests would exercise ITN online/offline/delete with request-queue full and IOC-disable transitions; IO start with inline SG, multi-page SG, read/write/no-data directions, all firmware completion statuses, host abort races, and sequence-recovery retry exhaustion; TM target reset and LUN-scoped cleanup; path timeout hold/failback behavior; LUN mask add/delete/clear/update/query persistence; throttle get/set and firmware resource reconfiguration. Runtime signals include `bfa_stats()` counters, WARN_ONs, trace events, callback completion order, queue emptiness after ITN deletion, and dconf update results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcpim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcpim.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcpim.h

## Purpose
`bfa_fcpim.h` defines the HAL FCP initiator module contract used by the BFA core, BFAD driver layer, and FCS FCP initiator bridge. It supplies resource limits, tag mapping macros, state-machine event enums, core runtime structures for FCPIM/ITNIM/IOIM/TSKIM, queue helpers, IO profiling helpers, and public function declarations implemented primarily in `bfa_fcpim.c`.

## Important APIs, Types, And Functions
Important resource constants include `BFA_IO_MAX`, `BFA_FWTIO_MAX`, `BFA_ITNIM_MIN/MAX`, `BFA_IOIM_MIN/MAX`, `BFA_TSKIM_MIN/MAX`, and path-timeout bounds. `BFA_IOIM_IOTAG_MASK`, `BFA_IOIM_RETRY_TAG_OFFSET`, and `BFA_IOIM_RETRY_MAX` define how retry generation bits share the IO tag word. `bfa_ioim_get_index()` maps transfer size into IO profile buckets.

The central structures are `bfa_fcp_mod_s` for the whole FCP module, `bfa_fcpim_s` for initiator-mode state, `bfa_itnim_s` for one initiator-target nexus, `bfa_ioim_s` plus `bfa_ioim_sp_s` for host IOs and slow-path state, and `bfa_tskim_s` for SCSI task management. The header declares the IO, TM, and ITN state-machine event enums and callback prototypes. It also declares LUN mask and throttle APIs, IO profile/stat APIs, attach/ISR functions, and BFAD completion callbacks that lower-layer code invokes.

## Control Flow
The header expresses the module layering. BFA core calls `bfa_fcp_meminfo()`, `bfa_fcp_attach()`, `bfa_fcp_iocdisable()`, and `bfa_fcp_res_recfg()`. FCS or BFAD creates ITNIMs through `bfa_itnim_create()` and drives online/offline/delete events. BFAD allocates IOIMs, starts IOs, and aborts them; firmware completions are dispatched through `bfa_ioim_isr()` and `bfa_ioim_good_comp_isr()`. Task-management allocation/start/free and firmware ISR are similarly exposed. Tag macros convert firmware IO/TM/ITN handles into array objects, keeping the C implementation O(1) for completion dispatch.

## State And Persistence Behavior
The header shows that state is mostly in-memory and list-based: ITNIMs own pending, active, cleanup, task, and delayed-completion queues; IOIMs own SG page queues and callback queue elements; TSKIMs own affected-IO queues and cleanup wait counters. Persistent surfaces are exposed through LUN mask and throttle functions, but the underlying persistent storage lives in the dynamic config module used by `bfa_fcpim.c`. IO profile state is transient but externally queryable while enabled.

## Dependencies And Integration Points
The file includes BFA core, service, firmware message, definition, and common-support headers. It references Linux list primitives and SCSI/FCP protocol types through included driver headers. Its callback declarations are an integration contract with BFAD (`bfa_cb_ioim_*`, `bfa_cb_tskim_done`) and FCS (`bfa_cb_itnim_*`). Macros such as `BFA_FCPIM()`, `BFA_MEM_FCP_KVA()`, `BFA_SNSINFO_FROM_TAG()`, and request-queue helpers are used throughout the FCP implementation and other BFA modules.

## Risks And Edge Cases
The tag mapping macros assume power-of-two or mask-compatible resource counts, valid firmware handles, and stable array layout. `BFA_IOIM_FROM_TAG()` references `fcpim` in the macro body instead of the `_fcpim` parameter, which works only in contexts where a local `fcpim` variable exists and is a maintenance hazard. The retry-bit packing means all code that compares or frees tags must mask generation bits correctly. Structure fields are shared across asynchronous state machines, so callers must respect the lifecycle implied by the events.

## Test Signals
Header-level validation is compile-time and integration-oriented: all users should build with the declared APIs, tag mapping should resolve expected array entries, IO retry tags should increment and mask correctly, and resource reconfiguration should not violate min/max constants. Runtime tests should observe state-machine transitions exposed through these event enums and verify callback contracts are honored by BFAD/FCS implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcpim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs.c

## Purpose
`bfa_fcs.c` implements the main Fibre Channel Services object and the base fabric state machine for the BR-series driver. It initializes FCS, reacts to physical link events, performs fabric login for switched, loop, direct-attached, and loopback topologies, propagates fabric online/offline to base and virtual ports, handles unsolicited frames at the fabric level, manages fabric stop/delete waits, initializes symbolic names, and wires FCS into BFA port-event and unsolicited-frame callbacks.

## Important APIs, Types, And Functions
Top-level APIs include `bfa_fcs_attach()`, `bfa_fcs_init()`, `bfa_fcs_update_cfg()`, `bfa_fcs_stop()`, `bfa_fcs_exit()`, `bfa_fcs_pbc_vport_init()`, and `bfa_fcs_driver_info_init()`. Fabric-facing APIs include `bfa_fcs_fabric_modstart/stop()`, `bfa_fcs_fabric_link_up/down()`, `bfa_fcs_fabric_addvport/delvport()`, `bfa_fcs_fabric_vport_lookup()`, `bfa_fcs_fabric_uf_recv()`, `bfa_fcs_fabric_set_fabric_name()`, `bfa_fcs_vf_lookup()`, and `bfa_fcs_vf_get_ports()`.

Key internal functions are the fabric state handlers for uninit, created, linkdown, flogi, flogi_retry, auth, auth_failed, loopback, nofabric, online, EVFP, isolated, deleting, stopping, and cleanup. `bfa_cb_lps_flogi_comp()` translates LPS FLOGI results into fabric events. `bfa_fcs_uf_recv()` strips VFT headers and routes unsolicited frames by VF/fabric. `bfa_fcs_port_event_handler()` converts physical port link events into fabric state-machine events.

## Control Flow
`bfa_fcs_attach()` stores BFA/BFAD pointers, marks `bfa->fcs` true, initializes FC frame builders, registers link and UF callbacks, allocates an LPS object, initializes fabric wait counters, and attaches the base logical port. `bfa_fcs_init()` sends the fabric create event, which initializes base port WWNs and creates the base lport. `bfa_fcs_fabric_modstart()` sends the start event; if link is already up, loop topology goes directly online with ALPA-derived PID, while non-loop topology sends FLOGI through LPS.

FLOGI completion sets BB credit, fabric name, PID, NPIV/auth flags, then either continues to online/authentication or enters no-fabric direct-attach mode. Retryable failures arm a 2-second timer and resend FLOGI. Link down moves the fabric to linkdown, logs out LPS where appropriate, and offlines vports before the base port. Stop/delete paths use wait counters to stop or delete all vports and the base port before completing `bfa_fcs_stop()` or `bfa_fcs_exit()`.

Unsolicited frames are routed first by optional VFT header, then by destination ID. Fabric-port FLOGI frames are consumed by the fabric handler; frames for the base port or vports are delivered to lport handlers; in non-switched mode unmatched frames fall back to the base port. Incoming direct-attach FLOGI is accepted by building and sending a FLOGI ACC.

## State And Persistence Behavior
The main persistent-like state is in `struct bfa_fcs_s` and `struct bfa_fcs_fabric_s`: fabric type, operation type, NPIV/auth flags, BB credit, VF ID, vport queues, fabric name/IP, LPS pointer, stats, and wait counters. State is volatile driver runtime state, not persisted to flash. Driver info is copied into `fcs->driver_info` and used to rebuild port and node symbolic names. Fabric name changes generate AEN events after an initial zero-name assignment.

## Dependencies And Integration Points
The file depends on BFA port services (`bfa_fcport_*`), login services (`bfa_lps_*`), unsolicited-frame services (`bfa_uf_*`), FC frame builders (`fc_flogi_acc_build()` and `fcbuild_init()`), lport/vport modules, BFAD callbacks for PBC vport creation, and vendor AEN posting. It is the fabric-level dispatcher for downstream lport, vport, rport, and FCPIM code declared in `bfa_fcs.h`.

## Risks And Edge Cases
Topology transitions are race-prone: link down can arrive during stop/delete/FLOGI retry, loopback detection can interrupt FLOGI, and IOC down can overlap cleanup. Several states intentionally ignore selected events, so regressions may surface as hung waits rather than immediate faults. Unsolicited-frame routing must handle VFT headers and unknown VF IDs correctly to avoid misdelivering frames. FLOGI acceptance and fabric-name update paths are sparse on error handling when FCXP allocation fails. Symbolic-name construction depends on bounded string concatenation and truncation behavior.

## Test Signals
High-value tests include attach/init/start with link down/up, loop topology, switched FLOGI success, direct N2N FLOGI, FLOGI retry errors, loopback detection, auth success/failure events, stop/delete wait-counter completion, vport add/delete propagation, VFT-tagged UF routing, unknown VF drop, fabric-name-change AEN, and symbolic-name formatting. Runtime stats such as FLOGI sent/accept/reject/retry counters, fabric online/offline counters, UF tagged/untagged/unknown counters, traces, and wait-counter completion are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs.h

## Purpose
`bfa_fcs.h` is the shared internal interface for Fibre Channel Services in the BR-series driver. It defines FCS trace categories, fabric/lport/vport/rport/FCPIM state-machine events, major runtime structures, helper macros, protected module APIs, and BFAD callback contracts. The file is the type and API spine connecting `bfa_fcs.c`, lport/vport/rport modules, `bfa_fcs_fcpim.c`, BFAD, and lower BFA HAL services.

## Important APIs, Types, And Functions
The header defines service-specific state for name server, state-change notification, management server, FDMI, fabric topology, logical ports, virtual ports, remote ports, rport feature probing, and FCS ITNIM. `struct bfa_fcs_s` holds the FCS root; `struct bfa_fcs_fabric_s` holds base-fabric/vf state; `struct bfa_fcs_lport_s` holds each local port; `struct bfa_fcs_rport_s` holds discovered remote ports; `struct bfa_fcs_itnim_s` holds FCP initiator FC-4 state over an rport.

Externally visible APIs include main lifecycle (`bfa_fcs_attach/init/stop/exit`), VF lookup/listing, fabric module start/stop/link/UF/vport operations, lport lifecycle and discovery helpers, vport lifecycle, rport lookup/create/PRLO/SCN helpers, rport feature helpers, and FCS ITNIM create/delete/online/offline/attribute/stat APIs. BFAD callback declarations define allocation and notification hooks for lports, PBC vports, rports, and ITNIMs.

## Control Flow
The event enums document the expected flow. Fabric moves through create/start/link/FLOGI/auth/online/offline/stop/delete events. Lports react to create/online/offline/delete/stop and own subcomponents for NS, SCN, MS, and FDMI. Vports react to fabric online/offline, FDISC/LOGO responses, retry timers, duplicate WWN, and fabric capacity failures. Rports react to PLOGI, LOGO, PRLO, address changes, SCN, timeout, and FC-4 completion events. FCS ITNIM reacts to rport online, PRLI sent/response/retry, HAL online callback, driver callback, offline, initiator-only remote ports, and delete.

## State And Persistence Behavior
All structures are runtime driver objects. The header shows list-based ownership: fabrics contain vport queues, lports contain rport queues, rports own optional FC-4 role objects, and ITNIMs reference both FCS rports and HAL `bfa_itnim_s` objects. Timers and FCXP wait elements encode asynchronous protocol progress. Stats fields are maintained for UF, fabric/vf, lport, rport, and ITNIM paths. Persistent storage is not defined here; any persistent settings are handled by other modules.

## Dependencies And Integration Points
The file includes BFA common definitions, module state, and FC protocol definitions. It integrates with FCXP allocation through `bfa_fcs_fcxp_alloc()` and wait macros, with BFAD through callback declarations and driver-private pointers, with BFA HAL rport/itnim objects through embedded pointers, and with protocol code through FC WWN, COS, FDMI, ELS, and SCSI/FCP-related types. Many modules rely on the inline getters for WWNs, FCIDs, driver handles, fabric properties, and HAL handles.

## Risks And Edge Cases
The header exposes many state machines whose enum values are implicitly version-sensitive for traces; the comment warns to append only. Because structures are shared across modules, field ownership must remain clear: FCS ITNIM holds protocol negotiation flags while HAL ITNIM handles IO execution. Some comments contain stale names or typos, so maintainers should rely on field usage as well as comments. Several max constants are fixed policy values, such as rport login caps and tentative rport support limits, which can constrain scaling.

## Test Signals
Compile-time tests should catch API drift across FCS, FCPIM, BFAD, and BFA modules. Runtime tests should validate fabric/lport/vport/rport/ITNIM event sequencing, BFAD allocation/free callback pairing, inline getter correctness, FCXP wait allocation paths, and stats visibility. Trace consumers depend on stable enum values, so trace decoding compatibility is a specific regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_fcpim.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_fcpim.c

## Purpose
`bfa_fcs_fcpim.c` implements the FCS-layer FCP initiator nexus state machine. It negotiates FC-4 initiator-to-target readiness over an FCS remote port by sending PRLI, parsing PRLI responses, detecting initiator-only remote ports, creating/onlining the HAL `bfa_itnim_s`, delivering BFAD online/offline notifications, posting AENs, and handling PRLO. It bridges discovery/login state in FCS to the lower IO-execution machinery in `bfa_fcpim.c`.

## Important APIs, Types, And Functions
The file centers on `struct bfa_fcs_itnim_s` from `bfa_fcs.h`. Public functions are `bfa_fcs_itnim_create()`, `bfa_fcs_itnim_delete()`, `bfa_fcs_itnim_brp_online()`, `bfa_fcs_itnim_rport_offline()`, `bfa_fcs_itnim_is_initiator()`, `bfa_fcs_itnim_get_online_state()`, `bfa_fcs_itnim_lookup()`, `bfa_fcs_itnim_attr_get()`, `bfa_fcs_itnim_stats_get()`, `bfa_fcs_itnim_stats_clear()`, and `bfa_fcs_fcpim_uf_recv()`. HAL callbacks implemented here are `bfa_cb_itnim_online()`, `bfa_cb_itnim_offline()`, `bfa_cb_itnim_tov_begin()`, `bfa_cb_itnim_tov()`, and `bfa_cb_itnim_sler()`.

## Control Flow
Creation calls BFAD allocation, initializes the ITNIM to offline, and waits for rport progress. On FCS online, the state machine sends PRLI using an FCXP; FCXP allocation can wait asynchronously. A sent PRLI moves to the PRLI response state. Accept responses are parsed with `fc_prli_rsp_parse()`. If the remote port advertises initiator behavior, the ITNIM becomes a no-op initiator state and no HAL ITN is created. Otherwise the response records sequence recovery, REC support, task retry ID, and confirmation-completion support, then signals the rport that FC-4 FCS online is done.

After the rport/HAL rport is online, `bfa_fcs_itnim_brp_online()` drives the HAL-online event. The state creates a HAL ITN through `bfa_itnim_create()` if needed and calls `bfa_itnim_online()`. HAL completion calls back to `bfa_cb_itnim_online()`, which moves to online, notifies BFAD, logs, and posts an ITNIM online AEN. Offline from the rport notifies BFAD, calls `bfa_itnim_offline()`, logs disconnect/offline distinction based on lport state, and waits for HAL offline callback before acknowledging FC-4 offline to the rport.

PRLI errors enter a retry state with `BFA_FCS_RETRY_TIMEOUT` and up to `BFA_FCS_RPORT_MAX_RETRIES`; exhaustion causes implicit LOGO. PRLI command-not-supported moves offline without creating an ITN. Delete events cancel waits/discard FCXPs/stop timers as appropriate and free the BFAD ITNIM; if a HAL ITN exists, it is deleted first. PRLO unsolicited frames are routed to `bfa_fcs_rport_prlo()`.

## State And Persistence Behavior
State is runtime-only and encoded in the ITNIM state-machine function pointer plus fields in `bfa_fcs_itnim_s`: PRLI retry count, negotiated sequence-recovery/REC/FCP_CONF/task-retry flags, active FCXP, wait element, stats, BFAD handle, rport pointer, and optional HAL ITN pointer. The timeout callback increments stats and drives retry. AEN sequence uses the parent FCS `fcs_aen_seq`, but no persistent configuration is written here.

## Dependencies And Integration Points
The file depends on FCS rport/lport/fabric structures, FCXP allocation/send/discard, FC ELS PRLI builders/parsers, BFAD ITNIM allocation and online/offline/free callbacks, HAL FCPIM ITN APIs, and vendor event posting. It integrates with rport state via events such as `RPSM_EVENT_FC4_FCS_ONLINE`, `RPSM_EVENT_FC4_OFFLINE`, `RPSM_EVENT_LOGO_IMP`, and `RPSM_EVENT_DELETE`. It also updates driver-visible ITN timeout state in `bfa_cb_itnim_tov()`.

## Risks And Edge Cases
The state machine has many asynchronous cancellation points: FCXP allocation wait, in-flight PRLI, retry timer, HAL online/offline callbacks, rport offline/delete, and initiator-role changes. PRLI parse errors increment stats but do not always immediately send a state event, so behavior depends on surrounding timeout/offline progress. Well-known addresses skip HAL-online and AEN posting. If HAL ITN creation fails, the code offlines and requests rport delete. Logging/AEN behavior distinguishes connectivity loss from intentional offline by checking local-port online state.

## Test Signals
Tests should cover PRLI accept as target, PRLI accept as initiator, malformed PRLI response, LS_RJT command-not-supported, retryable response errors through retry exhaustion, FCXP allocation wait cancellation, rport offline/delete during PRLI send and PRLI wait, HAL ITN create failure, online/offline callback ordering, path-timeout callback effects, SLER-driven implicit LOGO, stats get/clear, attribute negotiation fields, and PRLO UF routing. Observable signals include ITNIM state encoding, BFAD online/offline/free callbacks, rport events, AEN records, and PRLI stats counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_fcpim.c -->
