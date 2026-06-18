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
