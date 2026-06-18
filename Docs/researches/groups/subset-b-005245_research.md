# subset-b-005245 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_svc.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_svc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_svc.h

## Purpose

`bfa_svc.h` is the internal service-layer interface for the QLogic/Brocade BFA driver. It declares the data structures, constants, callback types, state-machine events, memory macros, and public/protected APIs implemented mainly by `bfa_svc.c`. The header is the contract between BFA core modules, FCS, the Linux BFAD driver, and firmware-facing services for FCXP, RPORT, UF, LPS, FC port control, and FC diagnostics/D-port.

## Important APIs, Types, And Functions

Scatter/gather page support is represented by `struct bfa_sgpg_s`, `struct bfa_sgpg_wqe_s`, and `struct bfa_sgpg_mod_s`, plus constants `BFA_SGPG_MIN`, `BFA_SGPG_MAX`, `BFA_SGPG_NPAGE()`, `BFA_SGPG_DMA_SEGS`, and `BFA_SGPG_ROUNDUP()`. APIs `bfa_sgpg_malloc()`, `bfa_sgpg_mfree()`, `bfa_sgpg_winit()`, `bfa_sgpg_wait()`, and `bfa_sgpg_wcancel()` expose pool allocation and wait/cancel behavior.

FCXP support is declared through `struct bfa_fcxp_mod_s`, `struct bfa_fcxp_req_info_s`, `struct bfa_fcxp_rsp_info_s`, `struct bfa_fcxp_s`, `struct bfa_fcxp_wqe_s`, and callback typedefs for send completion, allocation completion, and SG address/length lookup. Public APIs include `bfa_fcxp_req_rsp_alloc()`, `bfa_fcxp_req_rsp_alloc_wait()`, `bfa_fcxp_walloc_cancel()`, `bfa_fcxp_discard()`, `bfa_fcxp_get_reqbuf()`, `bfa_fcxp_get_rspbuf()`, `bfa_fcxp_free()`, `bfa_fcxp_send()`, `bfa_fcxp_get_maxrsp()`, `bfa_fcxp_res_recfg()`, and `bfa_fcxp_isr()`.

RPORT support centers on `struct bfa_rport_mod_s`, `struct bfa_rport_info_s`, `enum bfa_rport_event`, and `struct bfa_rport_s`. APIs include `bfa_rport_create()`, `bfa_rport_online()`, `bfa_rport_speed()`, `bfa_rport_isr()`, `bfa_rport_res_recfg()`, `bfa_rport_set_lunmask()`, and `bfa_rport_unset_lunmask()`, while callback declarations define how upper layers learn about online/offline/QoS state changes.

UF support declares `struct bfa_uf_s`, `struct bfa_uf_buf_s`, `struct bfa_uf_mod_s`, `bfa_cb_uf_recv_t`, `BFA_UF_BUFSZ`, `BFA_PER_UF_DMA_SZ`, and APIs `bfa_uf_recv_register()`, `bfa_uf_free()`, `bfa_uf_isr()`, and `bfa_uf_res_recfg()`. Inline helpers `bfa_uf_get_frmbuf()` and `bfa_uf_get_frmlen()` expose received frame contents.

LPS support declares `enum bfa_lps_event`, `struct bfa_lps_s`, `struct bfa_lps_mod_s`, and APIs for local-port login lifecycle: `bfa_lps_get_max_vport()`, `bfa_lps_alloc()`, `bfa_lps_delete()`, `bfa_lps_flogi()`, `bfa_lps_fdisc()`, `bfa_lps_fdisclogo()`, `bfa_lps_set_n2n_pid()`, `bfa_lps_get_fwtag()`, `bfa_lps_get_base_pid()`, `bfa_lps_get_tag_from_pid()`, and `bfa_lps_isr()`.

FC port support declares `enum bfa_fcport_sm_event`, `struct bfa_fcport_s`, `struct bfa_fcport_ln_s`, `struct bfa_fcport_trunk_s`, and many configuration/query APIs: enable/disable, speed/topology/hard ALPA/max frame size, BB credit, attributes, event registration, QoS bandwidth, ratelimit, beacon, linkup, stats get/clear, D-port mode toggles, PBC status, BBCR config and query. The `BFA_FCPORT_MOD()` and `BFA_MEM_FCPORT_DMA()` macros map the service to the owning `struct bfa_s`.

Diagnostic support declares queue-test, loopback, D-port, and FC diagnostic aggregate structs: `struct bfa_fcdiag_qtest_s`, `struct bfa_fcdiag_lb_s`, `enum bfa_dport_sm_event`, `struct bfa_dport_s`, and `struct bfa_fcdiag_s`. APIs include `bfa_fcdiag_intr()`, `bfa_fcdiag_loopback()`, `bfa_fcdiag_queuetest()`, `bfa_fcdiag_lb_is_running()`, `bfa_dport_enable()`, `bfa_dport_disable()`, `bfa_dport_start()`, and `bfa_dport_show()`.

## Control Flow

The header describes a moduleized service model. Each service embeds a module struct in `bfa->modules`, exposes a `*_MOD()` accessor, contributes memory descriptors through companion implementation functions, then participates in attach/start/ISR paths owned by the BFA core.

The declared state-machine events show the expected control flow: LPS moves through login, logout, firmware response, resume, delete, offline, CVL, and N2N PID events; RPORT moves through create, delete, online, offline, firmware response, hardware failure, QoS SCN, speed update, and queue resume; FC port moves through start, stop, enable, disable, firmware response, link up/down, queue resume, hardware failure, D-port/DDPORT events, and FAA misconfiguration; D-port moves through enable, disable, firmware response, queue resume, hardware failure, start, request failure, and SCN.

The callback typedefs make completion paths explicit. FCXP send completion returns request status, response length, residual length, and response FC header. LPS, RPORT, UF, FC port, and diagnostics callbacks cross from firmware/BFA context into FCS or driver context, sometimes through callback queues.

## State And Persistence Behavior

All structures in this header describe in-memory runtime state, not persistent on-disk data. Persistent-like behavior comes from firmware-maintained handles and flash/PBC configuration mirrored into these structs during attach, enable, or login responses.

The important state fields are queue heads and descriptors; firmware tags/handles; DMA segment arrays and KVA segment descriptors; cached FC headers and payload metadata; lport WWNs/PIDs/MACs/login status; FC port speed/topology/config/stats/trunk/QoS/BBCR/FEC/beacon data; rport max frame size, PID, local PID, virtual fabric fields, speed, stats and QoS attributes; UF posted buffer metadata; and diagnostic locks/timers/results.

The header also encodes allocation limits. `BFA_FCXP_MAX`, `BFA_UF_MAX`, `BFA_SGPG_MAX`, and LPS/RPORT minimums/maximums constrain module parameter handling and memory sizing in implementation code.

## Dependencies And Integration Points

`bfa_svc.h` depends on `bfa_cs.h` and `bfi_ms.h`, which provide common BFA structures, list/callback/timer infrastructure, memory descriptors, FC protocol types, and firmware message definitions. It also refers to many BFA/FCS/driver types declared elsewhere, including `struct bfa_s`, `struct bfa_fcxp_s`, `struct bfa_rport_s`, `struct fchs_s`, `struct bfa_cb_pending_q_s`, `struct bfa_diag_*`, `struct bfa_port_attr_s`, and FCP/QoS/trunk/BBCR definitions.

The header is included by implementation and consumer files that need service APIs. It bridges firmware concepts such as BFI request classes, tags, DMA addresses, and unsolicited frame posts with upper-layer concepts such as SCSI initiator rports, local ports, FC host attributes, and diagnostic callbacks.

## Risks And Edge Cases

Because this header exposes concrete structs rather than opaque handles, field layout is part of the internal contract across multiple driver files. Changes to queue fields, tags, callback members, or DMA descriptors can break assumptions in `bfa_svc.c`, BFA core attach code, FCS code, or BFAD integration.

Macro correctness matters: address calculation macros for FCXP payload buffers and UF/SGPG DMA memory must stay consistent with memory sizing. `BFA_RPORT_FROM_TAG()` masks tags using `num_rports - 1`, so `num_rports` must be a power of two as the implementation warns.

The event enums are consumed by state-machine functions. Reordering is less risky than changing semantics, but adding events requires auditing every state handler for expected default/fault behavior.

Several callbacks are declared here but implemented elsewhere. Missing or mismatched callback behavior can surface only at runtime under firmware events, link changes, unsolicited frame receive, or diagnostics completion.

## Test Signals

Compile coverage should catch struct, typedef, macro, and prototype mismatches across `bfa_svc.c`, BFA core, FCS, BFAD, and FCPIM users. Runtime test signals should include successful resource sizing, attach, service ISR dispatch, callback delivery, and clean module parameter bounds behavior.

Focused validation should include max/min configuration for SGPG/FCXP/UF/RPORT/LPS, FCXP internal buffer address calculations, rport tag masking with power-of-two counts, event-driven state transitions, UF inline helpers returning valid frame data, and diagnostic callback ABI compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad.c

## Purpose

`bfad.c` is the Linux PCI/module entry point for the QLogic/Brocade BR-series Fibre Channel/FCoE SCSI driver. It owns module parameters, firmware image loading, PCI probe/remove, PCI error recovery, interrupt setup, driver instance state transitions, BFA/FCS attach/start/stop, memory allocation for BFA modules, physical/vport setup, and top-level module init/exit.

The file integrates Linux kernel services with the BFA hardware abstraction and FCS stack. It claims supported PCI devices, loads the correct firmware blob for the ASIC family, maps PCI BARs, configures DMA and interrupts, attaches the BFA core, starts FC services, and exposes the adapter to the SCSI/FC transport through BFAD IM helpers.

## Important APIs, Types, And Functions

Module-scope configuration includes `num_rports`, `num_ios`, `num_tms`, `num_fcxps`, `num_ufbufs`, `reqq_size`, `rspq_size`, `num_sgpgs`, `rport_del_timeout`, `bfa_lun_queue_depth`, `bfa_io_max_sge`, `bfa_log_level`, `ioc_auto_recover`, `bfa_linkup_delay`, MSI-X disable knobs, FDMI/debugfs toggles, PCIe read request size, `max_xfer_size`, and `max_rport_logins`. Firmware globals hold image pointers and sizes for CB, CT, and CT2 firmware.

The BFAD instance state machine is implemented by `bfad_sm_uninit()`, `bfad_sm_created()`, `bfad_sm_initializing()`, `bfad_sm_operational()`, `bfad_sm_stopping()`, `bfad_sm_failed()`, and `bfad_sm_fcs_exit()`. Events drive creation, init success/failure, HAL init failure recovery, FCS exit, stop, and final cleanup.

BFA/FCS callbacks include `bfad_hcb_comp()`, `bfa_cb_init()`, `bfa_fcb_lport_new()`, `bfa_fcb_rport_alloc()`, and `bfa_fcb_pbc_vport_create()`. These complete HAL commands, respond to BFA init, allocate Linux/FCS port objects, allocate FCS rport wrappers, and create preboot vports.

Memory/configuration functions include `bfad_hal_mem_alloc()`, `bfad_hal_mem_release()`, and `bfad_update_hal_cfg()`. They obtain default BFA configuration, apply module-parameter overrides, request BFA memory descriptors, allocate KVA with `vzalloc()`, allocate DMA with `dma_alloc_coherent()`, and mirror resolved defaults back into module globals.

PCI and driver lifecycle functions include `bfad_pci_init()`, `bfad_pci_uninit()`, `bfad_drv_init()`, `bfad_drv_start()`, `bfad_fcs_stop()`, `bfad_stop()`, `bfad_cfg_pport()`, `bfad_uncfg_pport()`, `bfad_start_ops()`, `bfad_worker()`, `bfad_pci_probe()`, and `bfad_pci_remove()`.

Interrupt functions include `bfad_intx()`, `bfad_msix()`, `bfad_init_msix_entry()`, `bfad_install_msix_handler()`, `bfad_setup_intr()`, and `bfad_remove_intr()`. They select MSI-X or line interrupt mode, dispatch to BFA interrupt handlers, dequeue/process/free BFA completion callbacks, and clean up vectors.

PCI error recovery is implemented by `bfad_pci_error_detected()`, `restart_bfa()`, `bfad_pci_slot_reset()`, `bfad_pci_mmio_enabled()`, and `bfad_pci_resume()`, registered in `bfad_err_handler`.

Module and firmware functions include `bfad_init()`, `bfad_exit()`, `bfad_read_firmware()`, `bfad_load_fwimg()`, `bfad_free_fwimg()`, the PCI ID table, `bfad_pci_driver`, `MODULE_FIRMWARE()`, and module metadata declarations.

## Control Flow

Module load starts in `bfad_init()`: it logs driver version, remembers the SGPG module parameter, initializes the initiator-mode module, enables supported FC4 roles, propagates auto-recover and rport limits to BFA/FCS globals, and registers the PCI driver.

PCI probe allocates a `struct bfad_s`, trace module, AEN queues, firmware image, PCI resources, instance number, locks, lists, debugfs, BFA memory, and BFA/FCS attachment. It initializes the BFAD state machine to uninit and sends `BFAD_E_CREATE`.

The create/init state path creates `bfad_worker`, sets up interrupts, calls `bfa_iocfc_init()`, installs MSI-X handlers when enabled, starts the BFA timer, and waits for `bfa_cb_init()` to complete. On successful HAL init it stops the worker and calls `bfad_start_ops()`. On HAL init failure it initializes enough FCS/physical-port state to allow a deferred recovery path and marks the state failed.

`bfad_start_ops()` clamps transfer size, fills FCS driver info from module parameters and PCI name, initializes or updates FCS config, allocates the physical SCSI host, initializes FC host attributes, probes the initiator mode, starts IOC/FCS operations, completes preboot vport creation by creating FC transport vports, waits for rports online according to link-up delay policy, and logs device claim.

Interrupt flow is shared between INTx and MSI-X. The handler enters under `bfad_lock`, calls the appropriate BFA interrupt routine, dequeues completion callbacks, drops the lock, processes callbacks, then frees the completion list under lock.

The periodic BFA timer runs `bfa_timer_beat()`, drains and processes completion callbacks, and re-arms itself at `BFA_TIMER_FREQ`.

Remove sends `BFAD_E_STOP`, lets the state machine stop FCS and IOC, detaches BFA, releases HAL memory, removes debugfs, removes the instance from the global list, unmaps/release PCI resources, and frees trace and BFAD allocations.

PCI error recovery suspends or stops BFA/FCS depending on error severity. Frozen-channel recovery stops FCS, removes interrupts, deletes the timer, disables PCI, then slot reset re-enables PCI, restores state, verifies config space, restores DMA mask/mastering, reattaches BFA, initializes IOC, reinstalls interrupts/timer, and restarts driver operations.

Firmware loading is lazy and per ASIC family. `bfad_load_fwimg()` picks CB, CT, or CT2 image based on PCI device ID and calls `request_firmware()` only if the cached image size is zero. Module exit frees cached images.

## State And Persistence Behavior

Persistent external state comes from module parameters, PCI device IDs, firmware files, PCI config state saved with `pci_save_state()`, and hardware/firmware configuration. Driver state is in memory: global instance count/list protected by `bfad_mutex`, per-device flags, completions, kthread pointer, locks, timer, mapped BARs, DMA/KVA memory descriptors, FCS/BFA structs, vport lists, AEN queues, and firmware image caches.

`bfad_update_hal_cfg()` normalizes user-provided module parameters into BFA config, then writes resolved defaults back to globals so sysfs/module parameter views expose actual values rather than zero. `bfad_start_ops()` temporarily derives default link-up delay when `bfa_linkup_delay` is negative, then restores `-1`.

The firmware image cache is process/module lifetime state. Images are loaded on first matching probe and reused until `bfad_exit()` calls `bfad_free_fwimg()`.

State-machine flags are central to cleanup decisions: `BFAD_DRV_INIT_DONE`, `BFAD_HAL_START_DONE`, `BFAD_CFG_PPORT_DONE`, `BFAD_FC4_PROBE_DONE`, `BFAD_HAL_INIT_DONE`, `BFAD_HAL_INIT_FAIL`, `BFAD_MSIX_ON`, `BFAD_INTX_ON`, and EEH flags determine whether resources are active and what teardown path should execute.

## Dependencies And Integration Points

The file depends heavily on Linux kernel PCI, firmware, DMA, interrupt, timer, kthread, completion, module parameter, debugfs, and FC transport APIs. It includes `bfad_drv.h`, `bfad_im.h`, `bfa_fcs.h`, `bfa_defs.h`, and `bfa.h`.

It integrates downward with BFA core through `bfa_attach()`, `bfa_detach()`, `bfa_cfg_get_default()`, `bfa_cfg_get_meminfo()`, `bfa_iocfc_init()`, `bfa_iocfc_start()`, `bfa_iocfc_stop()`, `bfa_intx()`, `bfa_msix()`, `bfa_msix_getvecs()`, `bfa_msix_init()`, `bfa_timer_beat()`, and completion queue helpers.

It integrates with FCS through `bfa_fcs_attach()`, `bfa_fcs_init()`, `bfa_fcs_exit()`, `bfa_fcs_driver_info_init()`, `bfa_fcs_update_cfg()`, `bfa_fcs_fabric_modstart()`, `bfa_fcs_pbc_vport_init()`, `bfa_fcs_vport_create()`, `bfa_fcs_vport_start()`, and FCS rport/vport callbacks.

It integrates upward with Linux SCSI/FC transport through BFAD IM helpers such as `bfad_im_module_init()`, `bfad_im_probe()`, `bfad_im_probe_undo()`, `bfad_im_port_new()`, `bfad_im_port_delete()`, `bfad_im_scsi_host_alloc()`, `bfad_im_scsi_host_free()`, `bfad_fc_host_init()`, and `fc_vport_create()`.

## Risks And Edge Cases

Probe failure unwind is multi-stage and must stay aligned with allocation order. A missing unwind step can leak DMA, KVA, IRQs, debugfs entries, trace memory, or PCI mappings; an extra step can double free partially initialized resources.

`bfad_read_firmware()` always calls `release_firmware(fw)` on exit, even after `request_firmware()` failure leaves `fw` uninitialized in the local scope. That pattern is suspicious in isolation and should be checked against the exact kernel version/compiler behavior and any downstream patches.

The state machine mixes synchronous waits, kthread fallback, and callback completions. Races around `bfad->bfad_tsk`, `bfad->comp`, timer deletion, and interrupt removal are high-risk, especially during init failure, remove, and PCI error recovery.

MSI-X setup first enables vectors, then handlers are installed later in the state-machine path. Error handling must preserve whether vectors are merely enabled or handlers are installed. The code falls back to INTx when MSI-X allocation fails, and CT hardware can retry with one vector.

PCI error recovery reattaches and restarts BFA using existing memory/configuration. Any state not reset by `bfa_attach()` or `bfad_drv_start()` can leak across reset. Permanent failure intentionally defers cleanup to normal remove to avoid inconsistent state.

Module parameter bounds are partial. Some parameters are clamped or ignored if invalid, while others are passed through to deeper layers. Tests should verify invalid values do not produce undersized queues, unsupported speeds, or unsafe memory sizing.

## Test Signals

Static signals include successful kernel build, module parameter registration, firmware declarations, and no resource-leak warnings from static analysis on probe/remove paths. Runtime load tests should verify firmware request by ASIC family, successful PCI probe, DMA mask and BAR mapping, BFA attach/init/start, physical SCSI host registration, interrupt delivery in both MSI-X and INTx modes, timer-driven completion processing, and clean module unload.

Failure-path tests should inject firmware missing, memory allocation failure, `pci_enable_device()`/`pci_request_regions()`/DMA mask/BAR map failures, MSI-X allocation/handler failures, BFA init failure, BFAD IM probe failure, vport creation failure, and PCI EEH frozen/permanent failures. Good signals are correct state-machine transitions, no hangs on completions, no live timers/IRQs after remove, no leaked DMA/KVA memory, and successful recovery after slot reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad.c -->
