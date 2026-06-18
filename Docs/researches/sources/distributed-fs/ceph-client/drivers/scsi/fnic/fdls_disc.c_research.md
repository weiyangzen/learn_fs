# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_disc.c

## Purpose

`fdls_disc.c` implements FNIC Fabric Discovery and Login Services for FCoE. It drives non-FIP fabric login, name-server registration, state-change registration, target discovery, target login/PRLI/ADISC, FDMI registration, RSCN handling, LOGO/ABTS handling, and link-down cleanup. It is the main FC control-plane state machine that turns link availability into registered SCSI remote ports.

## Important APIs, Types, and Functions

Externally referenced functions include:

- `fdls_alloc_frame()`: allocates a zeroed FCoE frame from `fnic->frame_pool`.
- `fdls_alloc_oxid()`, `fdls_free_oxid()`, `fdls_schedule_oxid_free()`, `fdls_reclaim_oxid_handler()`, and `fdls_schedule_oxid_free_retry_work()`: manage the bitmap-based OXID pool and delayed OXID reclamation.
- `fnic_del_fabric_timer_sync()` and `fnic_del_tport_timer_sync()`: cancel fabric/target timers while temporarily releasing `fnic_lock`.
- `fdls_send_tport_abts()`, `fdls_send_fabric_logo()`, `fdls_tgt_logout()`, and `fdls_delete_tport()`: explicit abort, logout, and target deletion helpers used by discovery and teardown paths.
- `fnic_find_tport_by_fcid()` and `fnic_find_tport_by_wwpn()`: lookup live, non-terminating target ports.
- `fnic_fdls_disc_start()`: starts FDLS after link/FIP login.
- `fnic_fdls_validate_and_get_frame_type()`: classifies received FC/FCoE frames after checking frame control, type, S_ID/D_ID, and OXID frame type.
- `fnic_fdls_recv_frame()`: top-level receive dispatcher for fabric, FDMI, target, ABTS, and unsolicited ELS frames.
- `fnic_fdls_disc_init()` and `fnic_fdls_link_down()`: initialize/reset FDLS state and process link down.

Major internal senders include `fdls_send_fabric_flogi()`, `fdls_send_fabric_plogi()`, `fdls_send_rpn_id()`, `fdls_send_register_fc4_types()`, `fdls_send_register_fc4_features()`, `fdls_send_scr()`, `fdls_send_gpn_ft()`, `fdls_send_tgt_plogi()`, `fdls_send_tgt_prli()`, `fdls_send_tgt_adisc()`, `fdls_send_fdmi_plogi()`, `fdls_fdmi_register_hba()`, and `fdls_fdmi_register_pa()`.

Major response handlers include `fdls_process_flogi_rsp()`, `fdls_process_fabric_plogi_rsp()`, `fdls_process_rpn_id_rsp()`, `fdls_process_rft_id_rsp()`, `fdls_process_rff_id_rsp()`, `fdls_process_scr_rsp()`, `fdls_process_gpn_ft_rsp()`, `fdls_process_tgt_plogi_rsp()`, `fdls_process_tgt_prli_rsp()`, `fdls_process_tgt_adisc_rsp()`, `fdls_process_fabric_abts_rsp()`, `fdls_process_tgt_abts_rsp()`, `fdls_process_fdmi_plogi_rsp()`, `fdls_process_fdmi_reg_ack()`, `fdls_process_fdmi_abts_rsp()`, `fdls_process_rscn()`, `fdls_process_logo_req()`, `fdls_process_adisc_req()`, `fdls_process_rls_req()`, and generic ELS accept/reject helpers.

## Control Flow

Discovery begins with `fnic_fdls_disc_start()`. It posts an FC host LIP reset event and either sends a fabric FLOGI for non-FIP operation or, when FIP already completed login, starts with fabric PLOGI to the directory server. On non-FIP first link-up, it also calls `fnic_fcpio_reset()` before sending FLOGI.

The non-FIP fabric sequence is FLOGI, PLOGI to directory server, RPN_ID, RFT_ID, RFF_ID, SCR, and GPN_FT. Each sender allocates an OXID, fills the FC header/payload, sends through `fnic_send_fcoe_frame()`, and arms a fabric retry timer. The response handlers validate state and OXID, free the OXID, cancel timers, update fabric/iport parameters, and advance to the next step. Busy/unable rejects set `FNIC_FDLS_RETRY_FRAME` so `fdls_fabric_timer_callback()` retries from a controlled timer path.

Target discovery is driven by GPN_FT. `fdls_process_gpn_ft_tgt_list()` parses each returned FCID/WWPN, creates new `fnic_tport_s` entries, reconciles FCID changes for an existing WWPN, and after RSCN marks missing targets for deletion. `fdls_tgt_discovery_start()` sends PLOGI to new targets or ADISC to targets marked by RSCN. Successful target PLOGI learns WWNN/WWPN, max frame size, and concurrent sequence limits, then sends PRLI. Successful PRLI verifies SCSI FCP target capability, records retry support, moves the target to READY, and queues `TGT_EV_RPORT_ADD` on `fnic_event_queue`.

Timers provide abort-and-retry control. `fdls_fabric_timer_callback()` sends ABTS when a fabric request times out, schedules delayed OXID reclaim when ABTS times out, and retries or falls back to PLOGI depending on state. `fdls_tport_timer_callback()` performs the analogous logic for target PLOGI, PRLI, and ADISC, deleting target ports when retries are exhausted. `fdls_fdmi_timer_callback()` aborts pending FDMI PLOGI/RHBA/RPA exchanges and retries FDMI registration up to its limit.

The receive path enters at `fnic_fdls_recv_frame()`. It finds the FC header at the supplied offset, logs/debug-dumps when enabled, classifies the frame with `fnic_fdls_validate_and_get_frame_type()`, suppresses unrelated frames during FLOGO, and dispatches to response or request handlers. Unsolicited RSCN triggers GPN_FT and RSCN accept, LOGO removes a target and may restart GPN_FT, ADISC/RLS/ECHO/RRQ are accepted or rejected based on current iport/tport state, and unsupported ELS requests are rejected.

Link down enters `fnic_fdls_link_down()`. It moves the fabric state to LINKDOWN, clears fabric flags, calls `fnic_fcpio_reset()` outside `fnic_lock`, deletes all tports, cancels FDMI pending state, and clears the FDMI-active flag.

## State and Persistence Behavior

The file mutates the in-memory `fnic_iport_s` and `fnic_tport_s` control-plane state. Key state includes `iport->fabric.state`, fabric retry flags, retry counters, timer-pending flags, active fabric/FDMI OXIDs, FDMI pending bitmask, `iport->state`, `iport->fcid`, `r_a_tov`, `e_d_tov`, `max_payload_size`, host transport fields, the OXID bitmap/reclaim lists, and `iport->tport_list`. Target state includes FCID, WWPN/WWNN, active OXID, PRLI service parameters, retry support, max payload size, timers, SCSI registration flags, and deletion/terminating flags.

No data is persisted to disk. State persists in memory across I/O until link down, device removal, reset, LOGO, RSCN reconciliation, or module unload. Some target operations queue work to `fnic_event_queue`, so target lifetime spans both FDLS lock-protected state and asynchronous SCSI transport registration/deletion handlers.

## Dependencies and Integration Points

The file depends on `fnic.h`, `fdls_fc.h`, `fnic_fdls.h`, Linux FC/FCoE headers, SCSI transport FC, workqueues, timers, mempools, and UTS host identity. It integrates with `fnic_fcs.c` through `fnic_send_fcoe_frame()`, `fnic_fdls_register_portid()`, `fnic_fdls_learn_fcoe_macs()`, `fnic_fcpio_reset()`, and SCSI remote-port add/remove helpers. It also integrates with `fip.c`: FIP completion can skip FDLS FLOGI and start FDLS at fabric PLOGI, while FIP cleanup calls FDLS link-down paths.

## Risks and Edge Cases

- Locking is delicate. Many functions assume `fnic_lock` is held, and timer cancellation helpers intentionally drop and reacquire it.
- OXID lifecycle is central. Stale responses, timed-out ABTS, delayed reclaim, and OXID reuse can misassociate responses if state/OXID checks regress.
- `fnic_fdls_validate_and_get_frame_type()` is the security and correctness gate for unsolicited FC frames; missing validation can let wrong S_ID/D_ID/type combinations mutate discovery state.
- RSCN processing handles malformed payloads, port-change RSCN, zero-FCID wildcard pages, and optional PCRSCN host reset. These branches are easy to regress.
- Target deletion spans local list removal, exchange reset, queued SCSI transport events, and timer state. Double deletion or use-after-free is the primary lifetime risk.
- FDMI is optional and parallel to fabric PLOGI, which makes its timers and active OXIDs independent from the main fabric active OXID.
- Several paths continue after allocation/send failure by arming retry timers, so tests need to observe recovery rather than only immediate return values.

## Test Signals

Useful signals include full fabric login through FLOGI/PLOGI/RPN/RFT/RFF/SCR/GPN_FT, FIP-complete entry into PLOGI, target PLOGI/PRLI registration, RSCN-triggered ADISC and target deletion, LOGO from target, fabric LOGO, ABTS accept/reject paths, timeout and busy-reject retries, OXID delayed reclaim, FDMI PLOGI/RHBA/RPA registration and abort timeout, malformed RSCN payloads, unsupported ELS rejection, RLS/ECHO/RRQ/ADISC request handling, link-down during discovery, and remote-port add/remove event ordering under SCSI I/O.
