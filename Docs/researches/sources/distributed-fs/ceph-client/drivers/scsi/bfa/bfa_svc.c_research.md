# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_svc.c

## Purpose

`bfa_svc.c` implements the BFA service layer for the QLogic/Brocade BR-series Fibre Channel HBA driver. It sits below the Linux-facing `bfad` driver and above firmware request/response queues, providing stateful services for FC exchange packets, local port login service, physical FC port control, remote port lifecycle, scatter/gather page allocation, unsolicited frame receive buffers, and diagnostics including loopback, queue test, and D-port.

The file is mostly a collection of finite state machines and resource pools. It translates driver/FCS operations into BFI firmware messages, handles I2H firmware completions, maintains host-side state cached from firmware events, and dispatches callbacks either directly into FCS context or via BFA callback queues for driver context.

## Important APIs, Types, And Functions

The FCXP service allocates and sends Fibre Channel exchange packets. `bfa_fcxp_meminfo()` and `bfa_fcxp_attach()` size and claim DMA/KVA memory; `bfa_fcxp_req_rsp_alloc()` obtains request or response FCXP objects from split free queues; `bfa_fcxp_send()` fills request/response metadata and queues `BFI_FCXP_H2I_SEND_REQ`; `bfa_fcxp_isr()` receives `BFI_FCXP_I2H_SEND_RSP`. Internal helpers `bfa_fcxp_queue()`, `bfa_fcxp_qresume()`, `hal_fcxp_send_comp()`, and `bfa_fcxp_discard()` handle request-queue backpressure, completion delivery, and cancellation.

The LPS service manages FLOGI/FDISC/FLOGO/FDSIC logout for local ports. `bfa_lps_meminfo()`, `bfa_lps_attach()`, `bfa_lps_alloc()`, `bfa_lps_delete()`, `bfa_lps_flogi()`, `bfa_lps_fdisc()`, `bfa_lps_fdisclogo()`, `bfa_lps_set_n2n_pid()`, and `bfa_lps_isr()` form the public and firmware-facing surface. The central state handlers are `bfa_lps_sm_init()`, `bfa_lps_sm_login()`, `bfa_lps_sm_loginwait()`, `bfa_lps_sm_online()`, `bfa_lps_sm_online_n2n_pid_wait()`, `bfa_lps_sm_logout()`, and `bfa_lps_sm_logowait()`.

The FC port service controls the physical port. `bfa_fcport_meminfo()`, `bfa_fcport_attach()`, `bfa_fcport_init()`, `bfa_fcport_start()`, `bfa_fcport_iocdisable()`, `bfa_fcport_isr()`, `bfa_fcport_enable()`, `bfa_fcport_disable()`, `bfa_fcport_cfg_speed()`, `bfa_fcport_cfg_topology()`, `bfa_fcport_get_attr()`, `bfa_fcport_get_stats()`, `bfa_fcport_clear_stats()`, `bfa_fcport_cfg_bbcr()`, and `bfa_fcport_get_bbcr_attr()` are the primary APIs. The port state machine covers uninitialized, enabling, linkdown, linkup, disabling, disabled, stopped, IOC-down/fail, D-port, dynamic D-port, and FAA-misconfig states. A second link-notification state machine coalesces link up/down notifications so upper layers see serialized callbacks.

The RPORT service manages firmware rport handles for remote ports. `bfa_rport_meminfo()`, `bfa_rport_attach()`, `bfa_rport_create()`, `bfa_rport_online()`, `bfa_rport_speed()`, `bfa_rport_isr()`, `bfa_rport_res_recfg()`, `bfa_rport_set_lunmask()`, and `bfa_rport_unset_lunmask()` allocate host descriptors, create/delete firmware rports, update QoS/speed, and inform FCPIM LUN masking. RPORT state handlers cover create, online, offline, delete, firmware response waits, request-queue-full waits, pending delete/offline, and IOC disable.

The SGPG service provides a shared pool of DMA-backed scatter/gather pages. `bfa_sgpg_meminfo()`, `bfa_sgpg_attach()`, `bfa_sgpg_malloc()`, `bfa_sgpg_mfree()`, `bfa_sgpg_wait()`, `bfa_sgpg_wcancel()`, and `bfa_sgpg_winit()` manage aligned SG page descriptors and waiter callbacks.

The UF service posts unsolicited frame buffers to firmware and returns completed frames to the registered receiver. `bfa_uf_meminfo()`, `bfa_uf_attach()`, `bfa_uf_start()`, `bfa_uf_recv_register()`, `bfa_uf_free()`, `bfa_uf_isr()`, and `bfa_uf_res_recfg()` allocate UF descriptors, build reusable buffer-post messages, receive `BFI_UF_I2H_FRM_RCVD`, and repost buffers after consumption.

The diagnostics service exposes `bfa_fcdiag_loopback()`, `bfa_fcdiag_queuetest()`, `bfa_fcdiag_lb_is_running()`, `bfa_dport_enable()`, `bfa_dport_disable()`, `bfa_dport_start()`, `bfa_dport_show()`, plus `bfa_fcdiag_attach()`, `bfa_fcdiag_iocdisable()`, and `bfa_fcdiag_intr()`. It sends `BFI_DIAG_H2I_LOOPBACK`, queue-test, and D-port requests and tracks completion through timers, locks, and D-port state transitions.

## Control Flow

At attach time, each service contributes memory requirements, then claims memory from BFA-managed KVA/DMA segments. FCXP splits instances into request and response pools; RPORT reserves tag 0 and puts the rest on the free queue; LPS initializes local-port tags; UF initializes receive descriptors and prebuilt post messages; FC port claims stats DMA and sets default configuration; diagnostics initializes D-port state.

Most operations follow the same flow: validate current state and hardware conditions, allocate or reuse a descriptor, attempt to get a firmware request slot with `bfa_reqq_next()`, queue a wait element with `bfa_reqq_wait()` when no slot is available, produce the message with `bfa_reqq_produce()`, then handle firmware I2H response in the relevant ISR. Queue-resume callbacks send state-machine resume events and retry the original message.

FCXP send flow starts with `bfa_fcxp_req_rsp_alloc()`, caller fills internal or external payload buffers, then `bfa_fcxp_send()` records FC header, rport, virtual fabric, lport tag, class, response timeout, callback, and lengths. `bfa_fcxp_queue()` serializes this to `bfi_fcxp_send_req_s`, including request/response DMA addresses, then completion is converted to host endianness and dispatched through `hal_fcxp_send_comp()`.

LPS flow begins with `bfa_lps_alloc()` and then FLOGI or FDISC. Successful login responses populate firmware tag, PID, NPIV/auth/peer WWN/FCoE data, move the LPS from login queue to active queue, and optionally send an N2N PID request. Clear virtual link events reset state and notify vport consumers.

FC port flow starts on `BFA_FCPORT_SM_START` after IOC configuration. Firmware enable responses seed flash-derived port config, stats DMA readiness, QoS/BBCR states, and link events. Link-up events update speed/topology/QoS/FCoE/trunk data and notify upper layers. Link-down and hardware failure paths reset link info, emit AENs, and transition to linkdown or IOC states.

RPORT flow starts with `bfa_rport_create()`, then `bfa_rport_online()` copies port info and sends firmware create. Firmware create response installs firmware handle, QoS data, and LUN mask before online callback. Offline/delete sends firmware delete and frees the descriptor or parks it offline after response.

Diagnostics flow requires the port to be in a valid state. Loopback requires the port disabled and not already in D-port. Queue test sends pattern data over one or all completion queues, expects bitwise-inverted payload in responses, and uses a timer for completion failure. D-port enable/start/disable is a state machine coupled to FC port DPORT/DDPORT state and SCN notifications.

## State And Persistence Behavior

The file does not persist state outside kernel memory and firmware. Durable inputs are inherited from firmware flash/PBC state and IOC attributes. Runtime state is held in BFA module structs, linked lists, timers, callback queues, DMA buffers, and cached firmware attributes.

Important state includes FCXP active/free/wait queues and callback fields; LPS free/active/login queues plus firmware tags, WWNs, PID, FCoE MACs, NPIV/auth flags, and login status; FC port cached WWNs, speed, topology, QoS, trunk, FEC, BBCR, VLAN, beacon flags, stats DMA readiness, and reset timestamp; RPORT active/free/unused queues, firmware handle, rport info, QoS attributes, and LUN mask flag; SGPG free count and waiter partial allocations; UF posted/free/unused queues and received frame metadata; diagnostics locks, timers, result buffers, D-port test state, peer WWNs, and callback slots.

Request queue pressure is persistent only while a wait element remains linked. Hardware failure/IOC disable paths aggressively cancel waits, move unused pools back to free queues, mark operations failed, and send state-machine events to reset or park objects.

## Dependencies And Integration Points

This file depends on the BFA core (`struct bfa_s`, module layout, request queues, timers, callback queues, tracing), BFI firmware message ABI (`bfi_*` request/response structs and message IDs), Linux list primitives, endian conversion helpers, DMA address helpers, and FC/FCoE protocol structs.

It integrates upward with FCS and BFAD callbacks: rport online/offline/QoS callbacks, LPS completion callbacks, FC port link event callbacks, unsolicited frame callbacks, diagnostics callbacks, AEN posting through `bfad_im_post_vendor_event()`, FCPIM helpers for path TOV/Q depth and LUN masking, and port logging through `bfa_plog_*`.

It integrates downward with IOC/firmware through request queues such as `BFA_REQQ_FCXP`, `BFA_REQQ_LPS`, `BFA_REQQ_PORT`, `BFA_REQQ_RPORT`, and `BFA_REQQ_DIAG`, and through ISR demultiplexing for FCXP, LPS, FCPORT, RPORT, UF, and DIAG message classes.

## Risks And Edge Cases

The code is state-machine heavy and many transitions fault on unexpected events, so regressions often show up as `WARN_ON()` or `bfa_sm_fault()` rather than graceful recovery. Queue-full paths are subtle because operations may be partially initialized while waiting on request-queue space.

Several APIs rely on caller preconditions: FCXP external SG support warns unless only one SG element is used; RPORT LUN masking casts `rport_drv` to `struct bfa_fcs_rport_s`; diagnostics assume callers enforce disabled/D-port-compatible port states; many functions expect firmware messages to carry valid tags.

Endian handling is mixed across firmware data paths and must be preserved carefully. Stats and diagnostic result conversion differs between FC QoS and FCoE structures and between little-endian and big-endian hosts.

Resource reconfiguration functions move tail entries from free queues to unused queues without deep validation that enough free descriptors are available, so they depend on being called at a safe time. SGPG waiter cancellation and partial allocation return are also sensitive to list membership and count correctness.

D-port and FC port state are coupled. A bug in DPORT/DDPORT transitions can leave the physical port in diagnostic mode, block normal enable, or incorrectly re-enable a dynamically disabled port.

## Test Signals

Useful static signals are successful kernel build, no sparse/endian warnings around BFI message fields, and no list-debug complaints for queue manipulation. Runtime signals include successful probe/init, port enable and link-up AENs, FCXP request/response completions, FLOGI/FDISC login and logout callbacks, RPORT create/delete callbacks, UF receive/repost behavior, and clean IOC disable/recovery.

Targeted tests should exercise request queue full/resume paths, FCXP discard while waiting and while in flight, LPS login failure statuses including fabric reject and protocol error, FC port stats get/clear timeout and response races, RPORT delete while create is pending, SGPG partial waiter fulfillment and cancel, UF callback plus repost, loopback/queue-test timers, and D-port enable/start/disable/SCN transitions.
