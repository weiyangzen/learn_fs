# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_lport.c

## Purpose

`bfa_fcs_lport.c` implements the Fibre Channel Services logical-port layer for the QLogic/Brocade BFA SCSI driver. It owns logical port lifecycle state, unsolicited frame routing, switched-fabric service registration, direct attach and loop discovery behavior, and NPIV virtual port creation/deletion. The file bridges the driver-facing `bfad` port objects, the FCS fabric state machine, low-level login service (`bfa_lps_*`) operations, FC exchange (`bfa_fcxp_*`) allocation/sending, and remote-port discovery in `bfa_fcs_rport.c`.

The source is not Ceph-specific despite living in the `distributed-fs/ceph-client` source copy. It is kernel FC HBA driver code used to discover and maintain FCP initiator connectivity.

## Important APIs, Types, and Functions

Core types come from `bfa_fcs.h` and `bfa_defs_fcs.h`. `struct bfa_fcs_lport_s` stores the logical port state-machine function, fabric pointer, `struct bfa_lport_cfg_s` identity/configuration, 24-bit FCID/PID, firmware lport tag, remote-port queue, topology-specific union, driver peer `bfad_port`, optional parent `struct bfa_fcs_vport_s`, FC exchange wait state, statistics, and wait counters. `struct bfa_fcs_vport_s` wraps an lport with an NPIV state machine, LPS object, retry timer, driver handle, and vport stats.

The exported lport lifecycle APIs are `bfa_fcs_lport_attach()`, `bfa_fcs_lport_init()`, `bfa_fcs_lport_online()`, `bfa_fcs_lport_offline()`, `bfa_fcs_lport_stop()`, and `bfa_fcs_lport_delete()`. They are event wrappers around the lport state machine. `bfa_fcs_lport_is_online()`, `bfa_fcs_lport_get_attr()`, `bfa_fcs_lport_get_stats()`, `bfa_fcs_lport_clear_stats()`, `bfa_fcs_get_base_port()`, and `bfa_fcs_lookup_port()` provide inspection.

Remote-port helpers maintain `port->rport_q`: `bfa_fcs_lport_get_rport_by_pid()`, `bfa_fcs_lport_get_rport_by_old_pid()`, `bfa_fcs_lport_get_rport_by_pwwn()`, `bfa_fcs_lport_get_rport_by_qualifier()`, `bfa_fcs_lport_add_rport()`, `bfa_fcs_lport_del_rport()`, `bfa_fcs_lport_get_rport_quals()`, and `bfa_fcs_lport_get_rport_max_speed()`.

Unsolicited receive handling is centralized in `bfa_fcs_lport_uf_recv()`. It handles login-independent ELS/BLS/FC-GS traffic itself and delegates known remote-port traffic to `bfa_fcs_rport_uf_recv()`. Important local handlers include `bfa_fcs_lport_plogi()`, `bfa_fcs_lport_echo()`, `bfa_fcs_lport_rnid()`, `bfa_fcs_lport_abts_acc()`, `bfa_fcs_lport_send_ls_rjt()`, and `bfa_fcs_lport_send_fcgs_rjt()`.

Switched fabric service submodules live in this same file. Name-server code is under `bfa_fcs_lport_ns_*()`, management-server code under `bfa_fcs_lport_ms_*()`, FDMI registration under `bfa_fcs_lport_fdmi_*()`, and state-change notification under `bfa_fcs_lport_scn_*()`. NPIV APIs are `bfa_fcs_vport_create()`, `bfa_fcs_pbc_vport_create()`, `bfa_fcs_vport_start()`, `bfa_fcs_vport_stop()`, `bfa_fcs_vport_delete()`, `bfa_fcs_vport_get_attr()`, `bfa_fcs_vport_lookup()`, plus fabric/internal callbacks such as `bfa_fcs_vport_online()`, `bfa_fcs_vport_offline()`, `bfa_cb_lps_fdisc_comp()`, `bfa_cb_lps_fdisclogo_comp()`, and `bfa_cb_lps_cvl_event()`.

## Control Flow

The top-level lport state machine starts in `uninit`, moves to `init` on create, to `online` on fabric/vport online, to `offline` on fabric/vport offline, and to `stopping` or `deleting` while waiting for remote ports to drain. Stop and delete paths iterate `port->rport_q` and send `RPSM_EVENT_DELETE`; completion is driven by `bfa_fcs_lport_del_rport()` sending `BFA_FCS_PORT_SM_DELRPORT`. Base-port completion decrements fabric wait counters, while vport completion calls `bfa_fcs_vport_stop_comp()` or `bfa_fcs_vport_delete_comp()`.

Online entry calls topology-specific operations through `__port_action[port->fabric->fab_type]`. Switched fabric initializes and starts name-server, RSCN, and management-server handling. N2N mode compares local and remote PWWNs to decide who assigns the well-known direct attach PIDs and who initiates PLOGI. Loop mode reads ALPA bitmap state from the FC port module, maps ALPAs through `loop_alpa_map`, and creates rports for discovered loop members.

For unsolicited frames, `bfa_fcs_lport_uf_recv()` first rejects or drops traffic while offline, except that offline PLOGI gets an LS_RJT. Online PLOGI is parsed and either updates N2N addressing, delivers to an existing rport by PWWN/PID, replaces a stale PID owner, or creates a new rport. ECHO and RNID get immediate ACC responses; ABTS receives BA_ACC; unsupported FC-GS receives CT reject. Known PID traffic is delegated to the rport state machine. RSCN is processed locally and may trigger targeted rport SCN or a fresh name-server query.

The switched-fabric name-server state machine logs into the name server with PLOGI, registers node name (`RNN_ID`), node symbolic name (`RSNN_NN`), port symbolic name (`RSPN_ID`), FC-4 type (`RFT_ID`), FC-4 feature (`RFF_ID`), and then optionally sends `GID_FT` for FCP initiator discovery. `bfa_fcs_lport_ns_process_gidft_pids()` filters out the local base port and sibling vports before creating or notifying rports.

The management-server state machine logs into the management server, starts FDMI registration, and for base ports queries `GMAL` for fabric IP data and `GFN` for fabric name. Fabric-name RSCNs call `bfa_fcs_lport_ms_fabric_rscn()` to refresh `GFN`.

FDMI registration sends `RHBA` for base ports, `RPRT` for vports, and `RPA` port attributes. Attribute builders gather adapter identity from IOC helpers, driver/OS metadata from `fcs->driver_info`, FC port speed/capability from `bfa_fcport_get_attr()`, and lport names/roles from `port_cfg`.

The RSCN submodule sends SCR on online, retries on reject/error, ACKs incoming RSCNs, ignores QoS-only events, routes fabric-name RSCNs to the management server, processes port-ID RSCNs directly, and uses area/domain/fabric RSCNs to SCN existing rports and trigger `GID_FT`.

The vport state machine is driven by user/API start, fabric online/offline, LPS FDISC completions, timers, stop/delete requests, and FDISC LOGO completions. Creation validates WWNs, duplicate vports, max vport count, and LPS allocation. Start sends FDISC if the fabric is online and NPIV-capable. Successful FDISC fills `lport.pid` from `vport->lps->lp_pid` and brings the lport online. Delete/stop first drains the lport, then sends FDISC LOGO when appropriate, or skips LOGO when the fabric is already offline.

## State and Persistence Behavior

State is in memory only. Persistent configuration is not written by this file. The lport persists its current FCID/PID, WWN identity, symbolic names, role flags, discovered remote-port list, topology scratch state, counters, and timer/exchange handles for as long as the driver object exists. Vport state similarly lives in the allocated `struct bfa_fcs_vport_s` and its associated LPS object.

The code mutates external fabric state in controlled cases: N2N sets the LPS PID with `bfa_lps_set_n2n_pid()`, management server `GFN` can update `fabric_name`, `GMAL` writes the fabric IP buffer, and vport add/delete mutates the fabric vport list. Driver-visible events are emitted through AEN helpers and `bfad_im_post_vendor_event()`.

Statistics in `struct bfa_lport_stats_s` and `struct bfa_vport_stats_s` are the main durable-in-runtime observability mechanism. They count PLOGI attempts/results, name-server commands, management-server commands, RSCN totals, unsolicited receive drops, FDISC retries/rejects/timeouts, and fabric online/offline notifications.

## Dependencies and Integration Points

This file depends on FC frame builders and parsers in `bfa_fcbuild.h`/`bfa_fc.h`, including builders for PLOGI, LS_ACC/LS_RJT, CT rejects, FDMI requests, GMAL/GFN, RNN_ID/RSNN_NN/RSPN_ID/RFT_ID/RFF_ID/GID_FT, SCR, BA_ACC, ECHO, and RNID. It depends on `bfa_fcxp_*` for exchange allocation, wait queues, send completion, discard, and response buffers.

Fabric integration is through `struct bfa_fcs_fabric_s`, `bfa_fcs_vf_lookup()`, fabric state checks, vport queue helpers, NPIV capability checks, and fabric wait counters. Remote-port integration is through `bfa_fcs_rport_create()`, `bfa_fcs_rport_create_by_wwn()`, `bfa_fcs_rport_plogi_create()`, `bfa_fcs_rport_plogi()`, `bfa_fcs_rport_scn()`, and rport state events.

Hardware/firmware integration is through FC port and IOC helpers such as `bfa_fcport_get_attr()`, `bfa_fcport_get_maxfrsize()`, `bfa_fcport_get_rx_bbcredit()`, `bfa_fcport_is_ratelim()`, `bfa_lps_alloc()`, `bfa_lps_fdisc()`, `bfa_lps_fdisclogo()`, `bfa_lps_delete()`, `bfa_lps_get_max_vport()`, and `bfa_iocfc_get_bootwwns()`.

Driver integration is through `bfad` and `bfad_im`: logical port creation via `bfa_fcb_lport_new()`, AEN allocation/posting, logging, driver flags such as `BFAD_PORT_ONLINE`, vport completion objects, and queued port deletion via `bfad_im_port_delete()`.

## Risks and Edge Cases

Several paths are asynchronous and stateful. Correctness depends on FCXP wait cancellation, timer cancellation, and discard happening in the matching offline/delete states. Missed events can leave lports or submodules stuck waiting for rports, FCXP allocation, or a timer.

The file performs many payload writes into FC request buffers using computed lengths and C struct overlays. FDMI builders in particular depend on correct padding and length accounting. The `FDMI_HBA_ATTRIB_BIOS_VER` block uses `fc_roundup(attr->len, sizeof(u32))` while `attr->len` has not yet been assigned in that block, which is a suspicious length calculation and should be treated as a review hotspot.

`bfa_fcs_lport_ns_gid_ft_response()` returns early when `resid_len != 0` without sending a state-machine response event. The local comment says a larger buffer/retry is needed, but the current behavior risks leaving the NS state in `gid_ft` waiting indefinitely after a truncated response.

PLOGI and N2N address assignment compare raw `wwn_t` memory with `memcmp()`. This follows the local code pattern, but any endianness or representation mismatch would affect which port assigns addresses and whether direct attach rejects WKA IDs correctly.

The code assumes list iteration and state-machine event delivery are serialized by the surrounding driver/FCS context. Remote-port queue mutation during stop/delete uses safe iteration in some paths, but helpers such as lookups and stats iteration do not take local locks.

Some rejected or unsupported operations intentionally degrade: `RFF_ID` with `CT_RSN_NOT_SUPP` is treated as success, min-config mode suppresses broad discovery and uses boot WWNs, and vports enter offline/error states for no-NPIV, duplicate WWN, or max-fabric-login conditions. These cases need explicit test coverage because they look like partial failure but are expected behavior.

## Test Signals

Useful test signals are state transitions, stats increments, and FC frame emission rather than persistent outputs. Unit or fault-injection coverage should verify lport create/online/offline/stop/delete with zero and nonzero rports; rport delete completion driving lport stop/delete completion; offline unsolicited PLOGI rejection; online PLOGI matching by PWWN/PID and stale-PID replacement; ECHO/RNID/ABTS response building; and FC-GS reject behavior.

Switched-fabric discovery tests should cover NS PLOGI success/failure, RNN_ID/RSNN_NN/RSPN_ID/RFT_ID/RFF_ID sequencing, RFF_ID unsupported acceptance, GID_FT accept/reject/truncated-response behavior, filtering of base-port and sibling-vport PIDs, min-config boot-target discovery, and `bfa_fcs_lport_set_symname()` issuing an RSPN_ID update only when appropriate.

RSCN tests should include port-ID events, duplicate entries, QoS-only events, fabric-name events refreshing management-server fabric name, area/domain/fabric events triggering both rport SCN and NS query, and LS_ACC send failures caused by FCXP allocation failure.

FDMI and management-server tests should validate base-port `RHBA -> RPA`, vport `RPRT`, retry exhaustion, disabled-FDMI behavior, GMAL parsing of HTTP-prefixed entries, and GFN-driven fabric-name updates.

Vport tests should exercise invalid/duplicate/base WWN rejection, max vport handling, LPS allocation failure, NPIV-unavailable offline behavior, successful FDISC online, protocol/timeout/fabric reject retry limits, duplicate WWN and fabric max AENs, stop/delete while online, delete while FDISC is outstanding, LOGO completion, fabric offline during stop/delete, and clear virtual link causing offline then online events.
