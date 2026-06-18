# Research: subset-b-005243

This grouped report covers selected QLogic/Brocade BFA Fibre Channel driver files under `sources/distributed-fs/ceph-client/drivers/scsi/bfa/`. Each section is wrapped for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_rport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_rport.c

## Purpose

`bfa_fcs_rport.c` implements Fibre Channel Services remote-port management for the BFA driver. It creates, logs in, authenticates, offlines, ages out, and deletes remote port objects seen by a logical port, and it bridges between fabric/lport discovery, FC ELS/CT exchanges, FC-4 initiator-target nexus management, the lower BFA hardware rport object, and BFAD/vendor event reporting.

The file is state-machine driven. The main rport state machine handles PLOGI, PLOGI accept, name-server rediscovery, ADISC validation, LOGO/PRLO handling, FC-4 online/offline callbacks, HAL rport online/offline callbacks, and deletion. A second remote-port-features state machine sends Brocade RPSC2 requests to learn remote-port speed for target-rate-limit/QoS integration.

## Important APIs, Types, and Functions

Important public entry points include:

- `bfa_fcs_rport_create()`: allocates an rport by FCID and starts outbound PLOGI.
- `bfa_fcs_rport_create_by_wwn()`: allocates an rport by WWN and starts name-server address discovery.
- `bfa_fcs_rport_plogi_create()` and `bfa_fcs_rport_plogi()`: handle inbound PLOGI for new or existing rports, update login parameters, record `reply_oxid`, and drive the accept path.
- `bfa_fcs_rport_scn()`: injects fabric RSCN/SCN events into the rport state machine.
- `bfa_fcs_rport_uf_recv()`: dispatches unsolicited ELS frames from an rport, including LOGO, ADISC, PRLO, PRLI, RPSC, and reject for unsupported commands.
- `bfa_cb_rport_online()`, `bfa_cb_rport_offline()`, `bfa_cb_rport_scn_online()`, `bfa_cb_rport_scn_no_dev()`, `bfa_cb_rport_scn_offline()`: lower-layer callbacks that translate HAL rport and link scan events into state-machine events.
- `bfa_fcs_rport_get_state()`, `bfa_fcs_rport_get_attr()`, `bfa_fcs_rport_lookup()`: management/query helpers.
- `bfa_fcs_rport_set_del_timeout()` and `bfa_fcs_rport_set_max_logins()`: global policy setters for stale-rport deletion and login allocation limits.
- RPF API: `bfa_fcs_rpf_init()`, `bfa_fcs_rpf_rport_online()`, and `bfa_fcs_rpf_rport_offline()`.

Important internal helpers:

- Exchange send/response paths: `bfa_fcs_rport_send_plogi()`, `bfa_fcs_rport_plogi_response()`, `bfa_fcs_rport_send_plogiacc()`, `bfa_fcs_rport_send_adisc()`, `bfa_fcs_rport_adisc_response()`, `bfa_fcs_rport_send_nsdisc()`, `bfa_fcs_rport_gidpn_response()`, `bfa_fcs_rport_gpnid_response()`, `bfa_fcs_rport_send_logo()`, `bfa_fcs_rport_send_logo_acc()`, `bfa_fcs_rport_send_prlo_acc()`, and `bfa_fcs_rport_send_ls_rjt()`.
- Frame handlers: `bfa_fcs_rport_process_prli()`, `bfa_fcs_rport_process_rpsc()`, `bfa_fcs_rport_process_adisc()`, and `bfa_fcs_rport_process_logo()`.
- Lifecycle helpers: `bfa_fcs_rport_alloc()`, `bfa_fcs_rport_free()`, `bfa_fcs_rport_update()`, `bfa_fcs_rport_fcs_online_action()`, `bfa_fcs_rport_hal_online_action()`, `bfa_fcs_rport_fcs_offline_action()`, `bfa_fcs_rport_hal_offline_action()`, `bfa_fcs_rport_hal_online()`, and `bfa_fcs_rport_hal_offline()`.

Key local state comes from `struct bfa_fcs_rport_s`, including `pid`, `old_pid`, `pwwn`, `nwwn`, `reply_oxid`, `plogi_pending`, `prlo`, `scn_online`, retry counters, `fcxp`/wait queue fields, `timer`, `stats`, `itnim`, `bfa_rport`, and embedded `rpf` feature state.

## Control Flow

Outbound discovery usually starts with `bfa_fcs_rport_create()`. The object is allocated with `bfa_fcs_rport_alloc()`, added to the lport rport list, assigned an ITNIM if the lport is an initiator, initialized to `uninit`, and then receives `RPSM_EVENT_PLOGI_SEND`. The `uninit` state moves to `plogi_sending`, allocates an FCXP, builds a PLOGI with local WWNs, frame size, and BB credit, sends it, then transitions to `plogi` once the FCXP is sent.

`bfa_fcs_rport_plogi_response()` validates transport status and the ELS response. LS_RJT with insufficient resources triggers delayed retry; other rejects and request failures drive retry/failure logic. Accept updates WWN, class-of-service, CISC, max frame size, and, in direct attach, may adjust fabric BB credit from the PLOGI payload. The response path also detects an address-change twin: when a transient rport with no WWN logs into a WWN already represented by another rport, stats are transferred, the transient object is deleted, the existing rport's PID is updated, and the existing object receives `PLOGI_COMP`.

Inbound PLOGI starts in `bfa_fcs_rport_plogi_create()` or `bfa_fcs_rport_plogi()`. The rport stores the remote `ox_id` as `reply_oxid`, updates login parameters, and enters the PLOGI-accept send state. Once the ACC is sent, `bfa_fcs_rport_fcs_online_action()` notifies ITNIM/FC-4 state. When FC-4 comes online, target rports create a lower `bfa_rport` object and call `bfa_rport_online()`; initiator-only rports can skip the lower rport and move directly online.

RSCN and address-change handling takes different paths by topology. In a switched fabric the rport sends GID_PN when it knows WWN, or GPN_ID when it only knows PID. Accepted name-server responses either confirm the same PID or update `pid` and notify any twin using the new PID. In loop or direct-attach cases, the state machine uses ADISC or PLOGI relogin. ADISC responses are parsed against the known PWWN/NWWN; accepted responses restore online state, while failures offline the FC-4/HAL layers and may age out the rport.

Offline and deletion are staged. Events such as LOGO, PRLO, implicit LOGO, address change, SCN offline, and delete first offline FC-4 via ITNIM/RPF actions, then offline the lower BFA rport, then either rediscover, send LOGO, send LOGO/PRLO ACC, start an age-out timer, or free the object. The stale offline state starts `bfa_fcs_rport_del_timeout`; expiry deletes the rport. Several states cancel queued FCXP allocation (`bfa_fcxp_walloc_cancel`) or discard in-flight exchanges (`bfa_fcxp_discard`) before changing state.

Unsolicited ELS dispatch is narrow. `bfa_fcs_rport_uf_recv()` ignores non-ELS frames, accepts/handles LOGO, ADISC, PRLO, PRLI, and RPSC, and sends LS_RJT for unsupported ELS commands. PRLI identifies whether the remote port is target or initiator, updates `scsi_function`, notifies ITNIM for initiator-initiator cases, and sends PRLI ACC. ADISC is accepted only when the ITNIM is online; otherwise it is rejected as login-required.

The RPF state machine is triggered when a non-WKA rport becomes online on a switched Brocade fabric and minimum config is not active. It sends RPSC2, parses the returned speed, and calls `bfa_rport_speed()` with the learned or assigned speed. Timeout/error paths retry up to three times and then settle online without speed data.

## State and Persistence Behavior

The file does not write persistent storage, but it owns long-lived in-memory identity and state for FC remote ports:

- Global policy `bfa_fcs_rport_del_timeout` and `bfa_fcs_rport_max_logins` affect all future rports.
- `fcs->num_rport_logins` enforces the max-login cap and is incremented/decremented around allocation/free.
- The lport `rport_q` is the authoritative in-memory list for lookup, duplicate/twin detection, and link SCN fan-out.
- `pid`, `old_pid`, `pwwn`, and `nwwn` preserve identity across address changes and name-server rediscovery.
- `itnim` and `bfa_rport` represent FC-4 and HAL resources that must be brought online/offline in the right order.
- Timers keep retry and deletion behavior alive after transient failures.
- Per-rport stats and AEN sequence state feed diagnostics and vendor events.
- RPF stores `rpsc_speed`, `assigned_speed`, retries, and outstanding FCXP state used by rate-limit reporting.

## Dependencies and Integration Points

This file depends on `bfad_drv.h`, `bfad_im.h`, `bfa_fcs.h`, and `bfa_fcbuild.h`. It builds and parses Fibre Channel ELS/CT payloads via helpers such as `fc_plogi_build()`, `fc_plogi_acc_build()`, `fc_adisc_build()`, `fc_adisc_rsp_parse()`, `fc_gidpn_build()`, `fc_gpnid_build()`, `fc_logo_build()`, `fc_prli_acc_build()`, `fc_rpsc_acc_build()`, `fc_rpsc2_build()`, and `fc_ls_rjt_build()`.

It integrates with:

- FCXP allocation/sending: `bfa_fcs_fcxp_alloc()`, `bfa_fcs_fcxp_alloc_wait()`, `bfa_fcxp_send()`, `bfa_fcxp_discard()`, and wait cancellation.
- Lport/fabric discovery: `bfa_fcs_lport_add_rport()`, `bfa_fcs_lport_del_rport()`, `bfa_fcs_lport_get_rport_by_pwwn()`, topology and switched-fabric checks, and base-port scan callbacks.
- ITNIM/FCPIM: `bfa_fcs_itnim_create()`, delete, online/offline, PRLO frame handling, and initiator notification.
- HAL rport: `bfa_rport_create()`, `bfa_rport_online()`, `BFA_RPORT_SM_OFFLINE`, `BFA_RPORT_SM_DELETE`, `bfa_rport_speed()`, and QoS callbacks.
- Physical port attributes: frame size, BB credit, rate limit status, current speed, and RPSC speed conversion.
- BFAD/vendor event reporting through `bfad_get_aen_entry()` and `bfad_im_post_vendor_event()`.

## Risks and Edge Cases

- State-machine coverage is broad and event ordering is subtle. In-flight FCXP, queued allocation callbacks, FC-4 callbacks, HAL callbacks, SCN, LOGO, PRLO, and delete can race conceptually even if the driver serializes events through its lock.
- `bfa_rport_sm_to_state()` scans a table that lacks an explicit null terminator in the visible initializer; if an unknown state function is queried, it can read past the table. Normal states are listed, but this is fragile.
- There is a duplicated forward declaration of `bfa_fcs_rport_sm_nsdisc_sent()`, suggesting low cleanup pressure around state declarations.
- `bfa_fcs_rport_free()` frees `rport->rp_drv` but does not free `rport` directly; correctness depends on the BFAD allocation contract returning driver-owned storage in a specific shape.
- Offline and deletion paths sometimes send ACCs before full cleanup and sometimes only discard/cancel FCXPs. Missed cancellation can produce callbacks into deleted rports.
- Name-server response parsing mutates CT header endianness in place and assumes response payload lengths are valid enough for cast-based access.
- Twin handling depends on WWN/PID comparisons and can move stats between objects; incorrect address-change handling can delete the wrong rport or leave stale PID mappings.
- RPF RPSC2 parsing accepts only first returned PID and warns if it does not match; multi-entry or malformed responses are not deeply validated.
- Global max-login and timeout setters are not visibly synchronized in this file.

## Test Signals

Useful validation signals include successful PLOGI outbound and inbound login, LS_RJT insufficient-resource retry, PLOGI max-retry age-out, name-server GID_PN and GPN_ID rediscovery after RSCN, PID change/twin handling, ADISC success and failure in loop/direct attach, LOGO and PRLO receive paths with ACC generation, FC-4 ITNIM online/offline callbacks, lower BFA rport online/offline callbacks, stale offline timer deletion, SCN online/offline fan-out for all base-port rports, RPSC/RPSC2 speed discovery on Brocade fabrics, unsupported ELS LS_RJT emission, max-login exhaustion, and driver unload/delete while FCXPs or timers are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_rport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_hw_cb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_hw_cb.c

## Purpose

`bfa_hw_cb.c` supplies Crossbow ASIC-specific IOCFC interrupt register setup, request/response queue acknowledgement behavior, and MSI-X vector handler installation for the BFA core. It is a small hardware dispatch file: higher-level code selects these functions for CB-generation devices, then calls them through `bfa->iocfc.hwif`.

## Important APIs, Types, and Functions

Public functions exported through prototypes in `bfa.h` include:

- `bfa_hwcb_reginit(struct bfa_s *bfa)`: maps function-specific interrupt status and mask registers from BAR0 into `bfa->iocfc.bfa_regs`.
- `bfa_hwcb_rspq_ack(struct bfa_s *bfa, int rspq, u32 ci)`: INTx response-queue acknowledgement by updating cached and hardware consumer indexes when the CI changes.
- `bfa_hwcb_msix_getvecs()`: returns the Crossbow MSI-X vector bitmap, vector count, and highest vector bit for the current PCI function.
- `bfa_hwcb_msix_init()`: validates one-vector or full-vector mode, stores `bfa->msix.nvecs`, and installs dummy handlers.
- `bfa_hwcb_msix_ctrl_install()`: installs mailbox/error handlers, either `bfa_msix_all` for one-vector mode or `bfa_msix_lpu_err` for error/control vectors in full MSI-X mode.
- `bfa_hwcb_msix_queue_install()`: installs queue handlers, either `bfa_msix_all` for one-vector mode or request/response queue handlers in full MSI-X mode.
- `bfa_hwcb_msix_uninstall()`: resets all Crossbow MSI-X handler slots to a dummy handler.
- `bfa_hwcb_isr_mode_set()`: switches the IOCFC hardware acknowledgement function pointers between MSI-X-aware and INTx behavior.
- `bfa_hwcb_msix_get_rme_range()`: reports the Crossbow response-message-engine vector range.

Private helpers are `bfa_hwcb_reqq_ack_msix()`, `bfa_hwcb_rspq_ack_msix()`, and `bfa_hwcb_msix_dummy()`.

## Control Flow

During attach, `bfa_core.c` selects this hardware interface for Crossbow ASICs. `bfa_hwcb_reginit()` uses `bfa_ioc_bar0()` and `bfa_ioc_pcifn()` to select `HOSTFN0_INT_STATUS`/`HOSTFN0_INT_MSK` or `HOSTFN1_INT_STATUS`/`HOSTFN1_INT_MSK`. The core later uses `bfa->iocfc.bfa_regs` for interrupt processing.

When MSI-X is configured, `bfa_hwcb_msix_getvecs()` builds a vector bitmap from function-specific CPE queue bits, RME queue bits, and LPU mailbox bits, then adds shared EMC/LPU/PSS error bits. Crossbow reports 13 vectors. `bfa_hwcb_msix_init()` records whether the driver is using one vector or the full set and clears all handlers to `bfa_hwcb_msix_dummy()`. Control and queue install calls then populate handler slots in phases as the driver enables control and I/O interrupt handling.

Queue acknowledgement differs by interrupt mode. In INTx mode, request queue acknowledgement is left `NULL` because the common INTx path handles CPE status, while response queue acknowledgement updates `rme_q_ci` only when the cached CI changes. In MSI-X mode, request queue acknowledgement writes the CPE bit to the interrupt status register, and response queue acknowledgement writes the RME bit before updating CI if needed.

## State and Persistence Behavior

No persistent storage is used. The file mutates live driver hardware state:

- `bfa->iocfc.bfa_regs.intr_status` and `intr_mask` cache MMIO addresses.
- `bfa->msix.nvecs` records active MSI-X mode.
- `bfa->msix.handler[]` contains the active vector dispatch table.
- `bfa->iocfc.hwif.hw_reqq_ack` and `hw_rspq_ack` are switched by interrupt mode.
- `bfa_rspq_ci(bfa, rspq)` caches response queue consumer indexes to avoid redundant MMIO writes.

## Dependencies and Integration Points

The file includes `bfad_drv.h`, `bfa_modules.h`, and `bfi_reg.h`. It depends on register macros such as `HOSTFN0_INT_STATUS`, `HOSTFN1_INT_STATUS`, `__HFN_INT_CPE_Q*`, `__HFN_INT_RME_Q*`, `__HFN_INT_MBOX_LPU*`, error bits, `CPE_Q_NUM()`, and `RME_Q_NUM()`.

It integrates with `bfa_core.c`, which installs Crossbow `hwif` function pointers, uses `bfa_isr_reqq_ack()` and `bfa_isr_rspq_ack()`, and dispatches MSI-X vectors through handlers installed here. It also relies on common ISR handlers `bfa_msix_all`, `bfa_msix_reqq`, `bfa_msix_rspq`, and `bfa_msix_lpu_err`.

## Risks and Edge Cases

- Vector indexes and bitmaps are PCI-function dependent. An off-by-one in `CPE_Q_NUM()` or `RME_Q_NUM()` use would acknowledge the wrong queue.
- In one-vector mode all queue/control slots are set to `bfa_msix_all`; partial handler installation order must not expose unhandled live vectors.
- `bfa_hwcb_msix_init()` only warns on invalid `nvecs`; it still stores the value. Bad callers could leave handlers inconsistent with allocated vectors.
- INTx mode uses no request-queue ack function. This depends on the common INTx path clearing CPE status correctly.
- Response queue CI writes are skipped if CI is unchanged. That is efficient but depends on cached CI staying coherent with firmware/hardware after reset.

## Test Signals

Useful signals include correct BAR0 interrupt register selection for PCI function 0 and 1, successful one-vector and 13-vector MSI-X operation, request queue and response queue interrupts on all Crossbow queues, LPU/error interrupt delivery, fallback INTx operation with `hw_reqq_ack == NULL`, no spurious handler calls after uninstall, and queue progress under high I/O interrupt rates without repeated stale CI writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_hw_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_hw_ct.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_hw_ct.c

## Purpose

`bfa_hw_ct.c` supplies Catapult and Catapult2 ASIC-specific IOCFC interrupt register setup, queue acknowledgement, and MSI-X handler installation for the BFA core. It mirrors the Crossbow hardware dispatch file but uses CT/CT2 register layouts and interrupt semantics.

## Important APIs, Types, and Functions

Public functions include:

- `bfa_hwct_reginit(struct bfa_s *bfa)`: selects function-specific CT interrupt status and mask registers from BAR0.
- `bfa_hwct2_reginit(struct bfa_s *bfa)`: selects CT2 host-function interrupt status and mask registers.
- `bfa_hwct_reqq_ack(struct bfa_s *bfa, int reqq)`: acknowledges CT request-queue interrupts by read/write of the CPE queue control register.
- `bfa_hwct_rspq_ack(struct bfa_s *bfa, int rspq, u32 ci)`: acknowledges CT response-queue interrupts through RME queue control and writes the response consumer index.
- `bfa_hwct2_rspq_ack(struct bfa_s *bfa, int rspq, u32 ci)`: acknowledges CT2 response progress by writing the consumer index only.
- `bfa_hwct_msix_getvecs()`: reports a contiguous CT MSI-X bitmap and vector count.
- `bfa_hwct_msix_init()`, `bfa_hwct_msix_ctrl_install()`, `bfa_hwct_msix_queue_install()`, and `bfa_hwct_msix_uninstall()`: manage CT MSI-X dispatch handlers.
- `bfa_hwct_isr_mode_set()`: delegates MSI-X enable/disable to the IOC layer through `bfa_ioc_isr_mode_set()`.
- `bfa_hwct_msix_get_rme_range()`: reports the CT response vector range.

The only private helper is `bfa_hwct_msix_dummy()`.

## Control Flow

`bfa_core.c` installs these functions for CT-generation devices and overrides selected callbacks for CT2. For CT, `bfa_hwct_reginit()` chooses `HOSTFN0_*` or `HOSTFN1_*` interrupt registers based on PCI function. For CT2, `bfa_hwct2_reginit()` uses `CT2_HOSTFN_INT_STATUS` and `CT2_HOSTFN_INTR_MASK`, which are not split through the older HOSTFN0/HOSTFN1 offsets.

Queue acknowledgement follows hardware requirements documented in comments. CT request queues are acknowledged by reading and rewriting the corresponding `cpe_q_ctrl` register. CT response queues are acknowledged by reading and rewriting `rme_q_ctrl`, then updating both cached and hardware CI. CT2 response queues only update CI; no RME queue-control acknowledgement is needed in this function.

MSI-X setup is table-driven. The vector bitmap is `(1 << BFI_MSIX_CT_MAX) - 1`, with the highest bit set to the last CT vector and the vector count set to `BFI_MSIX_CT_MAX`. Initialization accepts either one vector or the full CT vector count, stores `nvecs`, and resets all handlers to dummy. Control install routes the LPU/error vector to `bfa_msix_all` in one-vector mode or `bfa_msix_lpu_err` in full mode. Queue install routes all queue vectors to `bfa_msix_all` in one-vector mode, or splits CPE queues to `bfa_msix_reqq` and RME queues to `bfa_msix_rspq`.

## State and Persistence Behavior

No data is persisted. Runtime state modified here includes:

- `bfa->iocfc.bfa_regs.intr_status` and `intr_mask` MMIO pointer cache.
- CPE/RME queue control registers and response queue CI registers.
- `bfa_rspq_ci(bfa, rspq)` cached consumer indexes.
- `bfa->msix.nvecs` and `bfa->msix.handler[]`.
- IOC interrupt mode state via `bfa_ioc_isr_mode_set()`.

## Dependencies and Integration Points

The file includes `bfad_drv.h`, `bfa_modules.h`, and `bfi_reg.h`. It depends on CT/CT2 register macros, CT MSI-X vector constants, and queue register arrays initialized elsewhere in IOCFC setup. It integrates with `bfa_core.c` hardware selection, common ISR functions, IOC interrupt mode programming in `bfa_ioc_ct.c`, and queue macros declared in `bfa.h`.

## Risks and Edge Cases

- CT and CT2 acknowledgement semantics differ. Accidentally using CT queue-control acknowledgement on CT2, or CT2 CI-only acknowledgement on CT, can lose or repeat interrupts.
- `bfa_hwct_msix_init()` warns but does not reject invalid vector counts, so handler setup assumes callers pass either 1 or `BFI_MSIX_CT_MAX`.
- `bfa_hwct_msix_getvecs()` uses `(1 << BFI_MSIX_CT_MAX)`, so it assumes `BFI_MSIX_CT_MAX` fits in a 32-bit shift.
- Full-vector handler installation depends on the CPE/RME min/max constants matching the hardware vector table.
- `bfa_hwct_isr_mode_set()` only delegates to IOC mode control; for CT2 `bfa_core.c` sets `hw_isr_mode_set = NULL`, so callers must tolerate no hardware-mode callback.

## Test Signals

Useful signals include correct interrupt register selection on CT function 0/1 and CT2, INTx operation on CT request and response queues, CT2 response queue progress with CI-only acknowledgement, one-vector MSI-X operation through `bfa_msix_all`, full-vector CT operation with separate request/response/error handlers, no live interrupts after uninstall, correct RME vector range reporting, and reset/reinitialize cycles that do not leave stale handler pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_hw_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc.c

## Purpose

`bfa_ioc.c` is the common IOC and service-module implementation for the BFA Fibre Channel driver. It owns IOC enable/disable/failure state machines, IOCPF firmware boot and synchronization, firmware image compatibility decisions, mailbox send/receive and class dispatch, heartbeat monitoring and recovery, adapter identity reporting, timer infrastructure, firmware trace/core/statistics access, and several mailbox-backed management modules: ASIC block configuration, SFP, flash, diagnostics, PHY, driver configuration, FRU/VPD, TFRU, and raw flash reads.

This file is a central integration point between the Linux driver, PCI/MMIO hardware registers, embedded firmware running on the adapter, and higher-level BFA/BFAD modules. Most operations are asynchronous and callback-based; nearly all management modules depend on IOC operational state and fail outstanding work on IOC disable/failure notifications.

## Important APIs, Types, and Functions

Core IOC APIs:

- Lifecycle and PCI setup: `bfa_ioc_attach()`, `bfa_ioc_detach()`, `bfa_ioc_pci_init()`, `bfa_ioc_mem_claim()`, `bfa_ioc_enable()`, `bfa_ioc_disable()`, `bfa_ioc_suspend()`.
- Firmware boot/version: `bfa_ioc_boot()`, `bfa_ioc_fwver_get()`, `bfa_ioc_fwver_cmp()`, `bfa_ioc_flash_img_get_chnk()`, `bfa_ioc_fwsig_invalidate()`, `bfa_ioc_reset_fwstate()`.
- Mailbox: `bfa_ioc_mbox_send()`, `bfa_ioc_msgget()`, `bfa_ioc_mbox_register()`, `bfa_ioc_mbox_regisr()`, `bfa_ioc_mbox_queue()`, `bfa_ioc_mbox_isr()`, `bfa_ioc_isr()`, `bfa_ioc_error_isr()`.
- State/query: `bfa_ioc_is_operational()`, `bfa_ioc_is_disabled()`, `bfa_ioc_fw_mismatch()`, `bfa_ioc_adapter_is_disabled()`, `bfa_ioc_get_state()`, `bfa_ioc_get_attr()`, `bfa_ioc_get_adapter_attr()`, and adapter serial/FW/optrom/model/MAC helpers.
- Debug/statistics: `bfa_ioc_debug_memclaim()`, `bfa_ioc_debug_fwsave()`, `bfa_ioc_debug_fwtrc()`, `bfa_ioc_debug_fwcore()`, `bfa_ioc_fw_stats_get()`, `bfa_ioc_fw_stats_clear()`, `bfa_ioc_debug_save_ftrc()`.
- Timer API: `bfa_timer_beat()`, `bfa_timer_begin()`, and `bfa_timer_stop()`.

Service modules implemented in this file:

- ASIC block: `bfa_ablk_attach()`, `bfa_ablk_query()`, `bfa_ablk_pf_create()`, `bfa_ablk_pf_delete()`, `bfa_ablk_adapter_config()`, `bfa_ablk_port_config()`, `bfa_ablk_pf_update()`, optrom enable/disable, memory helpers, and ISR/notify handlers.
- SFP: attach/memclaim/show/media/speed APIs, SFP state-change notification handling, EEPROM data reads, media classification, and speed validation.
- Flash: attach/memclaim/get attributes/erase/update/read partition APIs, mailbox response handling, audit AEN, and chunked DMA transfers.
- Diagnostics: memory test boot path, firmware ping DMA test, temperature sensor, LED test, port beaconing, mailbox ISR, memory helpers, and IOC failure cleanup.
- PHY: attach/memclaim/get attributes/get stats/update/read APIs, mailbox response handling, presence/busy checks, and endian conversion.
- Driver configuration: `bfa_dconf_*` state machine, flash read/write of `BFA_FLASH_PART_DRV`, dirty/final sync handling, and IOCFC synchronization notifications.
- FRU/TFRU: attach/memclaim, FRU VPD read/update, max-size query, TFRU read/write, chunked DMA transfer, and mailbox response handling.
- Raw flash read helpers: FLI register programming, flash semaphore acquisition, FIFO flush, status read, fast-read start/check/end, and `bfa_flash_raw_read()`.

Important state-machine tables map internal function pointers to public states for IOC and IOCPF: `ioc_sm_table` and `iocpf_sm_table`.

## Control Flow

Attach initializes the mailbox module, notification list, and IOC state machine, then sends a reset event. PCI setup records class/device information, derives ASIC generation and port/personality mode, selects ASIC-specific IOC hardware interfaces from `bfa_ioc_cb.c` or `bfa_ioc_ct.c`, maps the port, and initializes IOC registers.

IOC enable begins in `bfa_ioc_sm_enabling`, which delegates to the nested IOCPF state machine. IOCPF first checks firmware state and image compatibility while serialized by hardware semaphores and firmware locks. If firmware in shared memory is missing, invalid, wrong boot environment, incompatible, older than driver policy permits, or older than flash policy requires, `bfa_ioc_hwinit()` boots firmware. Boot performs PLL initialization, local memory initialization, firmware image download from driver image or flash, boot-type/environment/device-mode writes into SMEM, and LPU start. IOCPF then polls firmware state until ready, sends IOC enable, waits for firmware reply, releases semaphores, and notifies the outer IOC state machine.

After enable reply, the outer IOC sends GETATTR with a DMA address. The GETATTR reply endian-converts core adapter attributes, updates `fcmode`, and transitions to operational. Operational entry calls the driver enable callback, notifies registered modules with `BFA_IOC_E_ENABLED`, starts heartbeat monitoring, logs an enable message, and posts an IOC AEN. The heartbeat timer compares the firmware heartbeat register with the previous count, polls queued mailbox commands, and either restarts itself or initiates recovery on no progress.

Failure handling splits between outer IOC and IOCPF. Hardware errors, heartbeat failure, and PF failures stop heartbeat monitoring, notify high-level callbacks, save firmware trace once, post AENs, stop LPU/flush mailboxes where needed, update firmware state registers, coordinate with the alternate IOC through sync hooks, and either auto-recover through hardware init or remain failed. Disable sends IOC disable, waits for reply or failure/timeout, leaves sync state, flushes mailbox commands, notifies modules, and calls the driver disable callback.

Mailbox flow is shared. `bfa_ioc_mbox_queue()` sends immediately when the host mailbox command register is free, otherwise links the command on `cmd_q`. Heartbeat polling and mailbox ISR both call `bfa_ioc_mbox_poll()` to drain pending commands. `bfa_ioc_mbox_isr()` reads a firmware-to-host message, handles IOC messages internally, and dispatches other message classes to registered module handlers.

Management modules follow a common pattern: attach registers a mailbox class handler and IOC notification callback; memclaim stores a DMA buffer; public APIs verify IOC operational state and module busy flags, populate state/callback pointers and mailbox request, then queue the request. ISR handlers endian-convert response status, copy DMA payloads into caller buffers, continue chunked transfers when residue remains, clear busy flags, and call callbacks. IOC disabled/failed notifications complete outstanding operations with IOC failure.

Driver configuration (`dconf`) is a deferred persistence state machine. Init reads driver config from flash unless in minimum config; successful reads validate signature/version and signal IOCFC. Updates mark the config dirty and start a debounce timer. Timer expiry writes the driver flash partition. Exit performs final sync or completes if no dirty data remains. IOC disable moves dirty state into `iocdown_dirty` so a later init can resume syncing.

Raw flash reads bypass firmware mailbox services and program FLI registers directly. `bfa_flash_raw_read()` serializes with `FLASH_SEM_LOCK_REG`, splits reads on the 128-byte FIFO boundary, checks flash status and write-in-progress, starts fast-read commands, busy-waits for completion, drains read data with byte swapping, flushes FIFO, and releases the semaphore.

## State and Persistence Behavior

Persistent device state touched by this file includes firmware images in adapter memory, flash partitions, driver configuration, FRU/VPD/TFRU data, and firmware state registers. In-memory runtime state includes:

- IOC FSM state, IOCPF FSM state, timers, heartbeat count, firmware trace save buffer, mailbox queue, notification queue, selected hardware interface, adapter attributes, port mode, capability bitmap, and PCI identity.
- Firmware shared memory contents used for version headers, boot control fields, firmware trace, firmware core dump, and firmware statistics.
- Module busy/lock flags such as `ablk->busy`, `sfp->lock`, `sfp->state_query_lock`, `flash->op_busy`, `diag->block`, `diag->fwping.lock`, `diag->tsensor.lock`, `phy->op_busy`, and `fru->op_busy`.
- DMA buffers for IOC attributes, SFP EEPROM, flash chunks, diagnostic DMA test, PHY transfers, and FRU transfers.
- Driver config state and data under `BFA_DCONF_MOD(bfa)`, including `min_cfg`, flash-read validity, dirty/sync states, and delayed-write timers.
- Global `bfa_auto_recover`, copied into IOCPF reset state and controlling automatic recovery after failure.

Flash and FRU operations are the clearest persistent writes. `bfa_flash_update_part()`, `bfa_flash_erase_part()`, `bfa_dconf_flash_write()`, `bfa_fruvpd_update()`, and `bfa_tfru_write()` can alter adapter nonvolatile storage. Length/alignment rules vary by operation.

## Dependencies and Integration Points

The file includes `bfad_drv.h`, `bfad_im.h`, `bfa_ioc.h`, `bfi_reg.h`, `bfa_defs.h`, `bfa_defs_svc.h`, and `bfi.h`. It depends on Linux MMIO primitives (`readl`, `writel`), delay helpers (`udelay`, `mdelay`), time (`ktime_get_real_seconds()`), endian conversion, list operations, and driver logging/AEN helpers.

Major integration points include:

- ASIC-specific IOC hardware interfaces selected by `bfa_ioc_set_cb_hwif()`, `bfa_ioc_set_ct_hwif()`, and `bfa_ioc_set_ct2_hwif()`.
- Firmware image provider callbacks `bfa_cb_image_get_chunk()` and `bfa_cb_image_get_size()`.
- BFI mailbox ABIs and message classes for IOC, ABLK, SFP, FLASH, DIAG, PHY, and FRU.
- BFAD callbacks in `struct bfa_ioc_cbfn_s` for enable/disable/reset/heartbeat failure and BFAD AEN posting.
- IOCFC orchestration through dconf events such as `IOCFC_E_DCONF_DONE`.
- Higher-level management/diagnostic APIs that call the service modules exposed here.

## Risks and Edge Cases

- The IOC/IOCPF state machines coordinate hardware semaphores, firmware locks, alternate IOC sync, timers, and callbacks. Missing one release or event can deadlock enable/disable or leave firmware state inconsistent.
- `bfa_ioc_adapter_is_disabled()` appears to read current IOC firmware state twice; for multi-function adapters it likely intended to check the alternate IOC state. This can make destructive diagnostics appear safe when the peer function is not disabled.
- `bfa_ioc_send_enable()` and `bfa_ioc_send_disable()` store `ktime_get_real_seconds()` through `be32_to_cpu()` despite assigning a host time value to a firmware field. The comment notes unsigned 32-bit time overflow in year 2106, but the endian helper direction is suspicious and should be checked against the field type.
- `bfa_timer_stop()` warns on empty timer lists. Callers must ensure timers are active before stopping; several state-machine paths assume exact timer state.
- Mailbox queued commands are flushed by dropping list entries without invoking per-command callbacks. Modules that rely on IOC notifications for failure completion must not leave commands only in the generic queue without their own busy cleanup.
- Service modules are mostly single-operation-at-a-time and depend on busy flags. Missing callback or response after firmware reset can leave modules busy unless IOC notification fires.
- Raw flash access uses busy-wait loops and hardware semaphores. Incorrect FIFO-boundary math, failure to release the semaphore on all paths, or concurrent firmware flash access can wedge flash access.
- PHY write path appears to convert from the DMA buffer into the user buffer before sending, while read path converts DMA to user buffer on completion. The write conversion direction deserves review because it may leave outbound DMA data unswapped or stale.
- SFP state-query flow can return `BFA_STATUS_SFP_NOT_READY` while scheduling an async callback; callers must honor the async completion contract.
- Flash update and read enforce 4-byte length and 16 KiB offset alignment for firmware-mediated partitions; callers must not assume byte-granular flash access.
- Firmware compatibility logic chooses between running SMEM firmware, flash firmware, and driver-bundled firmware. Regressions can cause avoidable firmware downloads or refusal to attach.

## Test Signals

Useful validation signals include enable/disable success logs and AENs, firmware mismatch and flash-better-than-driver paths, boot from driver image and flash image, IOCPF timeout and semaphore error handling, heartbeat failure with and without auto-recover, mailbox queue drain under busy firmware command register, GETATTR attribute correctness, firmware trace/core/stat reads and clears, adapter identity/model/MAC reporting across ASIC generations and personalities, ABLK query/config callbacks, SFP insertion/removal/unsupported/POM events and speed validation, flash attribute/erase/update/read with chunking and alignment failures, diagnostic memtest requiring disabled adapter, fwping DMA data verification, temperature/LED/beacon operations, PHY query/stats/read/update on supported and unsupported cards, dconf dirty debounce/final sync and IOC-down resume, FRU/TFRU chunked reads/writes with card-type gating, and raw flash reads across FIFO boundaries and semaphore contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc.c -->
