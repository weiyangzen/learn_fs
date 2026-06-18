# Research report: subset-b-005255

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.h

## Purpose
`efct_xport.h` declares the transport-facing state and control API used by the Emulex `efct` SCSI/Fibre Channel driver. It bridges the base driver, libefc discovery objects, the Linux FC transport template, I/O pool accounting, port online/offline control, and statistics collection.

## Important APIs, Types, And Functions
The main control enums are `enum efct_xport_ctrl` for actions such as port online/offline, shutdown, posting node events, and requested WWNN/WWPN updates, and `enum efct_xport_status` for link, port, statistics, speed-support, and quiesce queries. `struct efct_xport_link_stats`, `struct efct_xport_host_stats`, `struct efct_xport_host_statistics`, and `union efct_xport_stats_u` carry async link/host statistic results. `struct efct_xport_fcp_stats` tracks FCP request and byte counters. `struct efct_xport` is the central runtime object, with a back pointer to `struct efct`, requested names, node pointer array, I/O pool, pending I/O list, atomic counters, configured link state, stats timer, and stats snapshots. The exported lifecycle/control surface is `efct_xport_alloc`, `efct_xport_attach`, `efct_xport_initialize`, `efct_xport_detach`, `efct_xport_control`, `efct_xport_status`, and `efct_xport_free`, plus FC transport attach/release helpers.

## Control Flow And State
The header itself has no logic, but its fields show the runtime flow: transport allocation creates a node table and I/O pool, initialization wires the FC transport and hardware, control calls alter link and node state, status calls read link/config/statistics, and shutdown drains pending I/O before detach/free. Pending I/O is explicitly serialized by `io_pending_lock`; lifecycle counters are atomic because completions can race with scheduling and resource-shortage paths.

## Dependencies And Integration Points
This interface depends on Linux completions, timers, atomics, spinlocks, lists, and SCSI FC transport templates. It also references libefc `struct efc_node` and driver-local `struct efct_io_pool`. Callers should expect implementation in `efct_xport.c`, FC transport glue in the SCSI transport layer, and node/I/O integration with `efct_scsi.c` and libefc discovery.

## Risks And Test Signals
Risks include mismatched pending I/O counters, races around `io_pending_recursing`, stats completion timeouts, and stale node pointers in the node array during shutdown. Good test signals include link up/down transitions through `efct_xport_control`, stats queries with and without reset, supported-speed rejection, heavy I/O allocation pressure, quiesce detection during shutdown, and vport/remote-port registration exercising `struct efct_rport_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/include/efc_common.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/include/efc_common.h

## Purpose
`efc_common.h` provides the smallest shared definitions used across the Emulex FC discovery library and transport driver: a DMA buffer descriptor and device-scoped logging macros.

## Important APIs, Types, And Functions
`struct efc_dma` records CPU-visible DMA memory (`virt`), allocation base (`alloc`), bus address (`phys`), allocation size, active length, and the PCI device used for DMA ownership. The logging macros `efc_log_crit`, `efc_log_err`, `efc_log_warn`, `efc_log_info`, and `efc_log_debug` route libefc messages through `dev_*(&efc->pci->dev, ...)`.

## Control Flow And State
There is no executable control flow. The important state behavior is contractual: files that allocate DMA memory fill `virt`, `phys`, and `size`, update `len` when a payload length is meaningful, and clear the structure after freeing. Logging assumes every object passed as `efc` has a valid `pci` pointer.

## Dependencies And Integration Points
The header includes `<linux/pci.h>` and is pulled into `efclib.h`, `efc.h`, command code, ELS construction, and transport code. It is a common ABI between mailbox-command helpers, ELS request buffers, node service-parameter buffers, and hardware receive buffers.

## Risks And Test Signals
Risks are mostly misuse risks: freeing DMA with the wrong `pci_dev`, stale `len` after buffer reuse, or logging with a partially initialized `struct efc`. Test signals include fault-injected DMA allocation/free paths, driver init failure cleanup, and log paths invoked during early attach errors before all higher-level objects exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/include/efc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc.h

## Purpose
`efc.h` is the umbrella include for the libefc Fibre Channel discovery stack. It assembles common definitions, core object declarations, state-machine events, hardware command helpers, domain/nport/node/device/fabric/ELS APIs, and tracing macros.

## Important APIs, Types, And Functions
The header defines `EFC_MAX_REMOTE_NODES`, `NODE_SPARAMS_SIZE`, and SCSI deletion reason enums used when notifying the backend of initiator or target removal. `EFC_FC_ELS_DEFAULT_RETRIES` gives the default ELS retry budget. The trace macros `domain_sm_trace`, `domain_trace`, `node_sm_trace`, and `nport_sm_trace` standardize debug messages around current state handlers and `efc_sm_event_name`.

## Control Flow And State
There is no direct control flow, but this file shapes compilation and layering. Any `.c` file including `efc.h` sees the full discovery object graph and can post state-machine events, issue hardware commands, and send ELS messages. The tracing macros assume local variables named `evt`, `domain`, `node`, or `nport` exist in state handlers.

## Dependencies And Integration Points
`efc.h` includes `efc_common.h`, `efclib.h`, `efc_sm.h`, `efc_cmds.h`, and the state-machine-specific headers. This makes it the integration point between SLI-4 mailbox code, FC protocol helpers, Linux SCSI callbacks, and libefc object state machines.

## Risks And Test Signals
The main risk is include coupling: subtle changes to `efclib.h` or event enums propagate to all libefc implementation files. Trace macros also create compile-time coupling to variable names. Test signals are build coverage with all libefc objects, warning-free state handler compilation, and debug logging on domain/nport/node transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.c

## Purpose
`efc_cmds.c` translates libefc domain, nport, and remote-node lifecycle requests into SLI-4 resources and mailbox commands. It owns VFI/VPI/RPI allocation, registration, unregistration, DMA service-parameter staging, and callback-to-event conversion.

## Important APIs, Types, And Functions
Public entry points are `efc_cmd_nport_alloc`, `efc_cmd_nport_attach`, `efc_cmd_nport_free`, `efc_cmd_domain_alloc`, `efc_cmd_domain_attach`, `efc_cmd_domain_free`, `efc_cmd_node_alloc`, `efc_cmd_node_attach`, `efc_cmd_node_detach`, and `efc_node_free_resources`. Internal helpers validate mailbox status, allocate/read service parameters (`READ_SPARM64`), initialize VPI/VFI, register/unregister VPI/VFI/RPI, and call `efc_nport_cb`, `efc_domain_cb`, or `efc_remote_node_cb` with the corresponding libefc events.

## Control Flow And State
Nport allocation reserves a VPI, optionally reads hardware WWPN/WWNN into DMA, then issues `INIT_VPI`. Attach sets `fc_id`, sends `REG_VPI`, marks `attaching`, and on callback posts attach ok/fail. Free either unregisters an attached VPI, defers via `free_req_pending` while attach is outstanding, or posts `NPORT_FREE_OK`. Domain allocation allocates service-parameter DMA, reserves a VFI, runs `INIT_VFI`, then `READ_SPARM64`; domain attach sends `REG_VFI`; domain free sends `UNREG_VFI`. Node allocation reserves an RPI and stores `fc_id`/nport; attach sends `REG_RPI`; detach sends `UNREG_RPI`, treating `RPI_NOT_REG` as acceptable when appropriate.

## Dependencies And Integration Points
This file depends on `sli_resource_alloc/free`, `sli_cmd_*` builders, `efc->tt.issue_mbox_rqst`, Linux DMA APIs, and libefc state-machine callbacks. It is the hardware-facing half of the higher-level domain/nport/node state machines.

## Risks And Test Signals
Risks include leaked SLI resources on mailbox-format or issue failures, event callbacks after partially freed DMA, duplicate `return -EIO` and comment artifacts indicating lightly curated code, and deferred nport free racing attach completion. Test signals should cover mailbox success/failure for every VFI/VPI/RPI command, DMA allocation failure, attach-then-immediate-free, RPI-not-registered detach, and correct posting of alloc/attach/free events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.h

## Purpose
`efc_cmds.h` declares the libefc-to-SLI command API implemented by `efc_cmds.c`. It lets state machines request hardware allocation, attach, detach, and resource cleanup without knowing mailbox formats.

## Important APIs, Types, And Functions
`EFC_SPARAM_DMA_SZ` defines the DMA staging size used for service parameters. The exported functions cover nport/VPI allocation, attach, and free; domain/VFI allocation, attach, and free; remote-node/RPI allocation, attach, detach, and resource release.

## Control Flow And State
The declarations encode the lifecycle ordering expected by callers: allocate a domain or nport, attach it once an FC_ID is known, and later free it; allocate a remote node, attach it with service parameters, detach it when shutting down, then free resources. Some functions are asynchronous by design because mailbox completions post libefc events later.

## Dependencies And Integration Points
Callers pass `struct efc`, `struct efc_domain`, `struct efc_nport`, `struct efc_remote_node`, and `struct efc_dma` from `efclib.h`/`efc_common.h`. Implementations use SLI-4 mailbox helpers and base-driver `issue_mbox_rqst`.

## Risks And Test Signals
The header does not expose ownership annotations, so tests need to verify callers do not free objects before callbacks. Useful signals include state-machine unit/integration traces showing each command result mapped to the documented `EFC_EVT_*` event and resource leak checks over repeated link flap cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.c

## Purpose
`efc_device.c` implements the remote device node state machine for ordinary FC peer devices. It handles PLOGI/PRLI/LOGO/ADISC interactions, node attach, FCP enablement, backend SCSI session notifications, and orderly shutdown/relogin behavior.

## Important APIs, Types, And Functions
Externally declared state handlers include `__efc_d_init`, `__efc_d_wait_plogi_rsp`, `__efc_d_wait_node_attach`, `__efc_d_port_logged_in`, `__efc_d_device_ready`, `__efc_d_device_gone`, and the shutdown/wait states. Helper APIs include `efc_node_init_device`, `efc_process_prli_payload`, `efc_d_send_prli_rsp`, and `efc_send_ls_acc_after_attach`.

## Control Flow And State
New or discovered peers enter `__efc_d_init`. Initiator-capable ports may send PLOGI; target-side PLOGI reception saves service parameters, defers LS_ACC until RPI registration, and waits for domain/topology if needed. Once the node is attached, pending PLOGI or PRLI accepts are sent and the machine advances to port logged-in/device-ready. PRLI payloads set `node->init`/`node->targ`; backend callbacks via `scsi_new_node` and session registration drive `NODE_SESS_REG_OK/FAIL`. Ready nodes enable FCP and react to repeated PLOGI by implicit logout/re-attach, LOGO by explicit shutdown, RSCN missing by `device_gone`, and ADISC by revalidation.

## Dependencies And Integration Points
The file depends on ELS send helpers, domain/topology state from `efc_fabric.c`, hardware node attach/detach commands, `libefc_function_template` SCSI callbacks, and common node cleanup in `efc_node.c`.

## Risks And Test Signals
Risks include ordering races between sent PLOGI completions and incoming PRLI/PLOGI, LS_ACC state stored in `send_ls_acc`/`ls_acc_oxid`, backend async delete/session callbacks, and FCP gating. Several comments note possible ordering problems. Test signals should cover initiator-only, target-only, and I+T logins; PLOGI while ready; LOGO during attach; PRLI before PLOGI response; backend async registration failure; RSCN missing/refound; and shutdown with outstanding ELS and SCSI I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.h

## Purpose
`efc_device.h` exposes the remote device node state-machine entry points and helper functions used by node dispatch, fabric/P2P flows, and device login handling.

## Important APIs, Types, And Functions
The header declares `efc_node_init_device`, PRLI processing, deferred PRLI response, deferred LS_ACC setup, and all `__efc_d_*` state functions for loop waiting, PLOGI handling, domain/topology/node attach waits, shutdown, logged-in, ready, gone, ADISC wait, and LOGO wait.

## Control Flow And State
The declarations reveal the main state chain: init, wait for login response or inbound login, wait for domain/topology/attach, transition to logged-in/ready, and route shutdown through attach-wait, delete, ELS quiesce, node-free, and I/O-drain states. The header itself holds no data but assumes `struct efc_node` fields in `efclib.h` carry the mutable login and shutdown state.

## Dependencies And Integration Points
It depends on `struct efc_sm_ctx`, `enum efc_sm_event`, `struct efc_node`, and FC frame headers from the umbrella include path. Fabric code calls device helpers for P2P PRLI acceptance and topology integration.

## Risks And Test Signals
Risks are interface-level: all state handlers share the same callback signature, so mismatched events or callback payload types can compile but fail at runtime. Test signals are state traces entering every declared `__efc_d_*` handler, plus login/shutdown scenarios that confirm the headers and implementations stay synchronized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.c

## Purpose
`efc_domain.c` implements the FC domain lifecycle and top-level receive-frame dispatch. A domain represents the fabric/loop context containing local nports and remote nodes.

## Important APIs, Types, And Functions
Key public functions are `efc_domain_cb`, `efc_domain_alloc`, `efc_domain_free`, `efc_register_domain_free_cb`, `efc_domain_attach`, `efc_domain_post_event`, `efc_dispatch_frame`, `efc_domain_dispatch_frame`, and `efc_node_dispatch_frame`. State handlers include init, wait alloc, allocated, wait attach, ready, wait nports free, wait shutdown, and wait domain lost.

## Control Flow And State
Hardware domain callbacks enter under `efc->lock` and translate found/lost/alloc/attach/free results into state-machine events. On `DOMAIN_FOUND`, the code allocates a domain and physical nport, chooses requested or default WWNs, handles loop topology, allocates hardware domain resources, and starts fabric login through the FLOGI node. Attach stores the nport in `domain->lookup`, registers the domain, marks `attached`, accepts held frames, and broadcasts `DOMAIN_ATTACH_OK` to nodes. Domain loss holds frames, shuts down nports, waits for `ALL_CHILD_NODES_FREE`, frees hardware, and may replay a pending found record.

## Dependencies And Integration Points
The file integrates hardware callbacks, `efc_cmd_domain_*`, nport/node allocation, fabric/device state machines, xarray lookups, pending-frame queues, and base-driver frame free callbacks. `efc_dispatch_frame` is the receive ingress point from hardware.

## Risks And Test Signals
Risks include pending-frame ordering during hold/unhold, domain replacement while callbacks still reference old objects, xarray lookup lifetime, and unsolicited frame creation of nodes before topology is final. Test signals include domain found/lost during alloc and attach, private loop and public loop paths, P2P fallback dispatch, FCP frame drops with invalid D_ID, pending frame flush, and correct sequence freeing on handled vs unhandled frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.h

## Purpose
`efc_domain.h` declares the public domain state-machine API and frame-dispatch hooks for libefc.

## Important APIs, Types, And Functions
Exports include domain allocation/free, all domain state handlers, `efc_domain_attach`, `efc_domain_post_event`, `__efc_domain_attach_internal`, `efc_domain_dispatch_frame`, and `efc_node_dispatch_frame`.

## Control Flow And State
The header lays out the expected domain lifecycle: init after a domain-found callback, wait for hardware allocation, attach with an FC_ID, become ready, then wait for child nports and hardware shutdown on loss. Dispatch declarations show that domain-level receive classification routes frames to node-level handlers.

## Dependencies And Integration Points
It depends on `struct efc_domain`, `struct efc_sm_ctx`, `enum efc_sm_event`, and `struct efc_hw_sequence` from `efclib.h`. Hardware and transport code call into `efc_domain_cb`/`efc_dispatch_frame`, while node/fabric code calls `efc_domain_attach`.

## Risks And Test Signals
Risks include callers posting events to an uninitialized `drvsm` or dispatching frames before `efc->domain` is attached. Test signals include state transition traces across each declared handler and receive-frame tests that validate the domain-to-node dispatch contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.c

## Purpose
`efc_els.c` builds, sends, completes, retries, and frees ELS, CT, and BLS discovery I/O used by libefc state machines.

## Important APIs, Types, And Functions
Allocation APIs are `efc_els_io_alloc`, `efc_els_io_alloc_size`, `efc_els_io_free`, and `_efc_els_io_free`. Completion ingress is `efc_disc_io_complete`. Send APIs include PLOGI, FLOGI, FDISC, PRLI, LOGO, ADISC, SCR, name-server RFT_ID/RFF_ID/GID_PT, LS_ACC/LS_RJT variants, CT response, BLS accept, and frame-header accept/reject helpers declared in the header.

## Control Flow And State
Each ELS request allocates a pooled `efc_els_io_req` and coherent request/response buffers, links it on `node->els_ios_list`, increments `els_req_cnt` or `els_cmpl_cnt`, fills `struct efc_disc_io`, and calls `efc->tt.send_els`. Completion callbacks translate SLI WCQE statuses into `EFC_EVT_SRRS_ELS_REQ_OK/FAIL/RJT` or `EFC_EVT_SRRS_ELS_CMPL_OK/FAIL`, retrying sequence timeouts and LS_RJT busy conditions using timers. Cleanup posts the event to the node under the common lock and drops the ELS ref, freeing DMA and possibly signaling empty I/O lists.

## Dependencies And Integration Points
The file depends on Linux DMA/timer/mempool/list primitives, FC ELS/CT structures, SLI-4 status codes, and base-driver send callbacks. It is consumed by device, fabric, namespace, and shutdown state machines.

## Risks And Test Signals
Risks include counter underflow if completions arrive after state changes, timer retry lifetime against freed ELS objects, response length overrun, and subtle misuse of request vs response DMA for CT responses. Test signals include allocation failures, all WCQE statuses, LS_RJT busy retry, local reject timeout retry exhaustion, response-length overflow, ELS disabled during shutdown, and successful cleanup causing `NODE_ACTIVE_IO_LIST_EMPTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.h

## Purpose
`efc_els.h` declares the ELS/CT/BLS discovery I/O object and all protocol send helpers used by libefc state machines.

## Important APIs, Types, And Functions
`struct efc_els_io_req` wraps list/refcount state, node ownership, callback pointer, retry budget, delayed retry timer, display name, and `struct efc_disc_io`. The header defines `EFC_STATUS_INVALID`, `EFC_ELS_IO_POOL_SZ`, the hardware SRRS callback typedef, ELS allocation/free helpers, command send helpers, response send helpers, CT response, BLS accept/reject, and list-empty query.

## Control Flow And State
The header shows that ELS I/O is reference-counted, node-owned, linked for shutdown tracking, and completed asynchronously through callbacks. State machines call send helpers and later receive events from `efc_els_io_cleanup`.

## Dependencies And Integration Points
It depends on `struct efc_node`, `struct efc_disc_io`, FC frame headers, CT headers, and SLI/BLS parameter types via included umbrella headers. It is the protocol construction interface for device, fabric, and name-server code.

## Risks And Test Signals
Risks include calling send helpers after `node->els_io_enabled` is false and mismatched event counters for request vs response I/O. Test signals include pool exhaustion, timer cancellation/expiry, all declared ELS helper paths, and shutdown that waits for `els_ios_list` to become empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.c

## Purpose
`efc_fabric.c` implements fabric, fabric-controller, name-server, and point-to-point node state machines. It is responsible for FLOGI/FDISC login, topology detection, domain attach initiation, SCR/RSCN processing, GID_PT discovery, and P2P winner setup.

## Important APIs, Types, And Functions
Important state handlers include `__efc_fabric_init`, FLOGI/FDISC waits, fabric wait/idle, namespace PLOGI/RFT_ID/RFF_ID/GID_PT states, fabric-controller SCR/RSCN states, P2P FLOGI/PLOGI/domain/node attach states, and `__efc_fabric_wait_attach_evt_shutdown`. Helpers include `efc_fabric_set_topology`, `efc_fabric_notify_topology`, `efc_p2p_setup`, and internal GID_PT/RSCN processors.

## Control Flow And State
The physical fabric node sends FLOGI. If the response is an F_Port, topology becomes fabric, pending topology waiters are notified, and `efc_domain_attach` uses the returned FC_ID. If the response is N_Port, P2P winner logic assigns local/remote IDs and either attaches the domain or waits for the peer's PLOGI path. After domain/nport attach, the code starts a name-server node and optional fabric-controller node. Name-server flow logs into directory services, registers FC4 types/features, issues GID_PT, creates missing remote nodes, marks absent nodes missing, and handles RSCN-driven rediscovery with optional target delay. Fabric-controller flow sends SCR, accepts RSCN, and forwards it to name-server.

## Dependencies And Integration Points
This file depends on ELS/CT helpers, node allocation and attach, domain/nport attach APIs, FC well-known IDs, xarray node lookup, timers for delayed GID_PT, and backend node/device state machines for discovered peers.

## Risks And Test Signals
Risks include P2P winner comparison correctness, topology notification timing for nodes waiting on PLOGI, GID_PT payload parsing, RSCN coalescing delays, and repeated discovery during shutdown. Test signals include FLOGI to F_Port and N_Port, FDISC vport login, SCR/RSCN acceptance, GID_PT with new/missing/refound nodes, target-only delayed RSCN, P2P loopback and winner/loser paths, and fabric shutdown while attach is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.h

## Purpose
`efc_fabric.h` declares fabric, namespace, fabric-controller, and P2P state handlers plus topology helpers.

## Important APIs, Types, And Functions
The header exports state functions for FLOGI, FDISC, name-server PLOGI/RFT_ID/RFF_ID/GID_PT, delayed GID_PT, fabric-controller SCR/RSCN, and P2P login/attach paths. It also declares `efc_p2p_setup`, `efc_fabric_set_topology`, and `efc_fabric_notify_topology`.

## Control Flow And State
Declarations mirror the fabric discovery pipeline: login to fabric, attach domain/nport, start namespace/fabric-controller nodes, process name-server and RSCN events, or take the P2P route when FLOGI reveals an N_Port peer. Topology helpers mutate `nport->topology` and notify nodes that were blocked waiting for topology.

## Dependencies And Integration Points
It includes Linux FC ELS/FS/NS headers and depends on `efc_sm_ctx`, `efc_node`, and `efc_nport` from the libefc object model. Device code uses topology helpers when inbound FLOGI/PLOGI indicates P2P behavior.

## Risks And Test Signals
Risks are mostly event-contract risks across multiple state-machine families. Test signals should ensure every declared fabric state is reachable through login/discovery tests and that topology notifications are delivered exactly once to waiting nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.c

## Purpose
`efc_node.c` implements core remote-node allocation, reference management, event posting, generic node shutdown, pending-frame handling, and receive-frame-to-event decoding.

## Important APIs, Types, And Functions
Key APIs are `efc_remote_node_cb`, `efc_node_find`, `efc_node_alloc`, `efc_node_free`, `efc_node_attach`, `efc_node_post_event`, `efc_node_transition`, `efc_node_recv_els_frame`, `efc_node_recv_ct_frame`, `efc_node_recv_fcp_cmd`, `efc_process_node_pending`, SCSI completion hooks, WWN helpers, pause support, and generic shutdown states.

## Control Flow And State
Allocation uses the node mempool and DMA pool, reserves an RPI, stores the node in the nport xarray by FC_ID, initializes pending-frame and ELS lists, and takes an nport reference. Event posting increments `evtdepth`, invokes the current state, processes held frames when safe, and frees the node if `req_free` is set at outermost depth. Shutdown disables or waits for ELS I/O, detaches hardware if needed, waits for active I/O empty, purges pending frames for default shutdown, and frees resources/xarray entries. ELS receive decoding maps protocol opcodes to `EFC_EVT_*`; CT defaults to reject; FCP commands become `EFC_EVT_FCP_CMD_RCVD`.

## Dependencies And Integration Points
The file integrates command helpers, ELS send/reject helpers, domain frame dispatch, backend SCSI completion callbacks, Linux xarray/list/spinlock/timer primitives, and FC protocol headers.

## Risks And Test Signals
Risks include event-depth lifetime bugs, freeing a node while callbacks still hold implicit references, duplicate or stale pending frames, counter underflow in shutdown states, and `efc_node_check_els_req`/`efc_node_check_ns_req` currently returning 0 without validation. Test signals include allocation failure cleanup, xarray lookup/refcount behavior, nested event transitions, pending-frame hold/replay, unsupported ELS rejection, CT reject, SCSI completion event posting, and shutdown with active ELS/I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.h

## Purpose
`efc_node.h` declares node-level helpers, generic state handlers, frame receive entry points, and inline utilities for remote-node state tracking.

## Important APIs, Types, And Functions
The header defines node database pause bits, `MAX_ACC_REJECT_PAYLOAD`, `enum efc_node_enable`, tracing helpers, `efc_node_evt_set`, frame hold/accept helpers, `efc_node_get_enable`, allocation/attach/free APIs, event posting, common state handler, cleanup, pause state, pending-frame processing, WWN helpers, node lookup, ELS response posting, and receive handlers for ELS/CT/FCP.

## Control Flow And State
Inline helpers update state names and current/previous events on enter/exit, toggle `hold_frames`, and compute local/remote initiator/target capability combinations. Declared functions support the lifecycle from node allocation through attach, login, frame dispatch, pause/resume, shutdown, and free.

## Dependencies And Integration Points
The header includes FC name-server definitions and depends on `struct efc_node`, `struct efc_nport`, `struct efc_sm_ctx`, `struct efc_hw_sequence`, and `struct list_head` from libefc/Linux headers. Device and fabric state machines include it through `efc.h`.

## Risks And Test Signals
Risks include exposing many internals across files, state-name buffers becoming misleading if handlers do not call `efc_node_evt_set`, and capability enum assumptions. Test signals include state trace correctness, pause/resume behavior, `efc_node_get_enable` coverage for all 16 combinations, and frame hold/unhold with pending queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.c

## Purpose
`efc_nport.c` implements local FC port and NPIV vport lifecycle management: allocation, attach, backend registration, shutdown, vport persistence records, and reconstruction after domain attach.

## Important APIs, Types, And Functions
Public functions include `efc_nport_cb`, `efc_nport_alloc`, `efc_nport_free`, `efc_nport_find`, `efc_nport_attach`, `efc_vport_start`, `efc_nport_vport_new`, `efc_nport_vport_del`, `efc_vport_del_all`, and `efc_vport_create_spec`. State handlers include allocated, vport init/wait alloc/allocated, attached, wait shutdown, and wait port free.

## Control Flow And State
Allocation checks duplicate WWNs, initializes xarray/refcount/state, copies domain service parameters, adds the nport to `domain->nport_list`, and references the domain. Attach stores the nport in domain lookup by FC_ID, updates display names, and sends `REG_VPI`. Attached entry calls `efc->tt.new_nport`; exit calls `del_nport`. Shutdown marks `shutting_down`, handles vport link-down references, either frees immediately if no nodes exist or posts shutdown to each node and waits for `ALL_CHILD_NODES_FREE`. Vport specs persist requested WWNN/WWPN/FC_ID/backend data and are started when the domain enters ready.

## Dependencies And Integration Points
The file depends on domain lookup and list ownership, node shutdown, ELS LOGO for vport logout, `efc_cmd_nport_*`, backend nport callbacks, and spinlocks for `efc->lock` and `vport_lock`.

## Risks And Test Signals
Risks include vport spec and nport reference mismatches, shutdown while VPI attach is pending, domain lookup erasure ordering, and duplicate WWN handling. Test signals include physical nport attach, NPIV FDISC path, vport creation/deletion across link down/up, node-drain shutdown, attach failure, backend callback ordering, and duplicate vport rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.h

## Purpose
`efc_nport.h` declares the local nport and vport lifecycle API used by domain and fabric code.

## Important APIs, Types, And Functions
Exports include `efc_nport_find`, `efc_nport_alloc`, `efc_nport_free`, `efc_nport_attach`, nport/vport state handlers, and `efc_vport_start`.

## Control Flow And State
The lifecycle is allocate under a domain, attach after an FC_ID is known, transition through attached state, and free after child nodes have drained. Vport-specific declarations show an initial VPI allocation path followed by FDISC or hard-coded FC_ID attach.

## Dependencies And Integration Points
It depends on `struct efc_domain`, `struct efc_nport`, `struct efc_sm_ctx`, and `enum efc_sm_event`. Domain code allocates physical nports; fabric code attaches vports after FDISC; transport code may request vport start/delete through higher-level wrappers.

## Risks And Test Signals
Risks include callers assuming `efc_nport_find` returns a borrowed pointer when it actually takes a reference in the implementation. Test signals include reference-balanced find/release paths, physical and virtual attach success/fail, and shutdown while children remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.c

## Purpose
`efc_sm.c` implements the minimal generic state-machine dispatcher used by libefc domain, nport, node, fabric, and device state handlers.

## Important APIs, Types, And Functions
`efc_sm_post_event` calls the current state handler with an event and optional data, returning `-EIO` when no handler is installed. `efc_sm_transition` posts EXIT to the old state, updates `current_state`, then posts ENTER to the new state, or posts REENTER if the target state is already current. `efc_sm_event_name` maps event enum values to strings via `EFC_SM_EVENT_NAME`.

## Control Flow And State
The dispatcher is synchronous and does not queue events. State handlers may recursively post additional events or transition again. State ownership and locking are entirely the caller's responsibility; most libefc callback entry points take `efc->lock` before posting.

## Dependencies And Integration Points
It includes `efc.h` and `efc_sm.h` and is used by every stateful object embedding `struct efc_sm_ctx`. Node-specific code wraps transition/post to add event-depth tracking and deferred freeing.

## Risks And Test Signals
Risks include recursion depth, handlers freeing their context during nested events, and `efc_sm_event_name` only checking `evt > EFC_EVT_LAST` rather than negative values. Test signals include transition enter/exit ordering, reenter behavior, disabled/null state handling, and event-name coverage for all enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.h

## Purpose
`efc_sm.h` defines libefc's event vocabulary and generic state-machine API.

## Important APIs, Types, And Functions
`enum efc_sm_event` covers common lifecycle events, domain events, nport events, ELS/login events, unsolicited FC protocol events, node discovery/refound/missing events, shutdown reasons, and SCSI/backend completion events. `EFC_SM_EVENT_NAME` provides string mappings. The API declares `efc_sm_post_event`, `efc_sm_transition`, `efc_sm_disable`, and `efc_sm_event_name`.

## Control Flow And State
Events are the cross-file contract for all state machines. Hardware callbacks, ELS completions, receive-frame decoding, SCSI backend completions, timers, and shutdown paths all converge through these enum values. The must-be-last `EFC_EVT_LAST` bounds name lookup.

## Dependencies And Integration Points
The header forward-declares `struct efc_sm_ctx`; the actual context is defined in `efclib.h`. It is consumed by all domain/nport/node/device/fabric headers and implementations.

## Risks And Test Signals
Risks include incomplete string mapping for newer events, stale comments for "Sport" naming, and callers relying on events not handled by a given state. Test signals include compile coverage after enum edits, event-name assertions, and transition traces verifying every hardware/protocol callback maps to a meaningful event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.c

## Purpose
`efclib.c` initializes and destroys shared libefc runtime resources and documents the broad locking model for discovery state transitions.

## Important APIs, Types, And Functions
`efcport_init` initializes `efc->lock`, vport and pending-frame lists, pending-frame lock, node mempool, node DMA pool, and ELS I/O mempool. `efcport_destroy` purges pending domain-level frames and destroys pools. `efc_purge_pending` frees held hardware sequences through `efc->tt.hw_seq_free`.

## Control Flow And State
Initialization is sequential: core locks/lists first, then node object pool, node DMA pool, then ELS I/O pool. Destroy purges held receive frames before releasing pools. The top comment explains that libefc uses broad locking around base-driver entry points because discovery state is not on the hot I/O path.

## Dependencies And Integration Points
The file depends on Linux mempool and DMA pool APIs, base-driver sequence-free callbacks, and constants from `efc.h`/`efclib.h`. It must run before any domain/node/ELS allocation and after all live objects have been shut down.

## Risks And Test Signals
Risks include cleanup gaps on partial init failure: if ELS I/O pool creation fails, the node pool and DMA pool are not both unwound in the visible path. Destroy assumes pools were initialized and no active objects remain. Test signals include init fault injection for each allocation step, destroy after pending-frame accumulation, and lockdep checks around libefc entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.h

## Purpose
`efclib.h` defines the shared libefc object model, protocol constants, callback template, and top-level APIs used by the Emulex discovery library.

## Important APIs, Types, And Functions
It defines topology, shutdown, LS_ACC, domain event enums, `struct efc_sm_ctx`, `struct efc_domain_record`, `struct efc_nport`, `struct efc_domain`, `struct efc_remote_node`, `struct efc_node`, `struct efc_vport`, receive buffers/sequences, discovery I/O request structures, `struct libefc_function_template`, and root `struct efc`. It also declares initialization/destruction, domain/nport/node callbacks, vport management, frame dispatch, discovery I/O completion, and SCSI backend completion APIs.

## Control Flow And State
The object graph is explicit: `struct efc` owns global locks, pools, vport list, pending domain frames, callback template, and current domain; a domain owns nports and D_ID lookup; nports own remote-node lookup and service parameters; nodes own RPI state, ELS I/O lists, pending frames, login flags, timers, and state-machine context. `libefc_function_template` is the base-driver integration contract for backend node/nport notifications, mailbox issue, ELS/BLS send, and hardware sequence release.

## Dependencies And Integration Points
The header includes Linux FC protocol headers, `efc_common.h`, and SLI-4 declarations. It is the central ABI between `efct`, SLI mailbox code, libefc state machines, and SCSI initiator/target backend glue.

## Risks And Test Signals
Risks include large cross-file coupling, lock-order mistakes across `efc->lock`, `vport_lock`, pending-frame locks, and ELS locks, plus lifetime bugs around kref-owned domain/nport/node objects. Test signals include struct initialization audits, lockdep, repeated link flap/vport cycles, pool exhaustion, and backend callback paths for all `libefc_function_template` methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.h -->
