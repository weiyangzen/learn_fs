# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.c

## Purpose

`fip.c` implements FNIC's FCoE Initialization Protocol control path. It discovers FCoE VLANs, selects an FCF from advertisements, performs FIP-encapsulated FLOGI, maintains FCF/enode/VN-port keepalives, processes Clear Virtual Link messages, and restarts discovery after timeouts or link/control failures.

## Important APIs, Types, and Functions

- `fnic_fcoe_reset_vlans()`: clears the discovered VLAN list under `vlans_lock`.
- `fnic_fcoe_send_vlan_req()`: sends a VLAN request to all FCFs, resets VLAN state, clears VLAN tag, sets `FDLS_FIP_VLAN_DISCOVERY_STARTED`, and arms `retry_fip_timer`.
- `fnic_fcoe_process_vlan_resp()`: parses VLAN notification descriptors and appends available VLANs to `fnic->vlan_list`.
- `fnic_fcoe_start_fcf_discovery()`: sends a discovery solicitation on the selected VLAN and starts FCF discovery timeout.
- `fnic_fcoe_fip_discovery_resp()`: handles solicited FCF advertisements during discovery and unsolicited advertisements as FCF keepalives after FLOGI starts/completes.
- `fnic_fcoe_start_flogi()`: sends FIP FLOGI to the selected FCF with an allocated FDLS OXID.
- `fnic_fcoe_process_flogi_resp()`: validates and processes FIP FLOGI responses, learns FPMA/FCID/timeouts, registers the port ID, and starts FDLS discovery.
- `fnic_common_fip_cleanup()`: cancels FIP timers, removes FPMA from vNIC filters, clears FCF/FCID/timeout state, and resets VLAN list.
- `fnic_fcoe_process_cvl()`: validates Clear Virtual Link, runs FDLS link down, and restarts VLAN discovery.
- `fdls_fip_recv_frame()`: demultiplexes Ethernet FIP frames by op/subcode.
- Timer/work handlers: `fnic_work_on_fip_timer()`, `fnic_handle_fip_timer()`, `fnic_handle_enode_ka_timer()`, `fnic_handle_vn_ka_timer()`, `fnic_vlan_discovery_timeout()`, `fnic_work_on_fcs_ka_timer()`, and `fnic_handle_fcs_ka_timer()`.

## Control Flow

FIP discovery starts with `fnic_fcoe_send_vlan_req()`. It broadcasts a FIP VLAN request, records the state, and waits for responses until `retry_fip_timer` fires. `fnic_fcoe_process_vlan_resp()` records VLAN IDs. On timeout, `fnic_vlan_discovery_timeout()` selects a VLAN, programs it through `fnic->set_vlan()`, marks it sent, and calls `fnic_fcoe_start_fcf_discovery()`.

FCF discovery sends a solicitation and waits for advertisements. `fnic_fcoe_fip_discovery_resp()` stores the available FCF with the best priority and its keepalive parameters. When discovery times out, `fnic_work_on_fip_timer()` either starts FIP FLOGI against the selected FCF or restarts VLAN discovery.

FIP FLOGI builds a FIP LS request containing an FC FLOGI frame, allocates a fabric OXID through FDLS, and arms the FLOGI timeout. `fnic_fcoe_process_flogi_resp()` validates descriptor lengths/types and FC header fields, frees the OXID, cancels the retry timer, and on LS_ACC learns FPMA, FCID, R_A_TOV, and E_D_TOV. It programs the FPMA into the vNIC, registers the port ID, transitions to `FDLS_FIP_FLOGI_COMPLETE` and `FNIC_IPORT_STATE_FABRIC_DISC`, calls `fnic_fdls_disc_start()`, and starts enode/VN keepalive timers when FKA is enabled.

After login, unsolicited FCF advertisements refresh `fcs_ka_timer` and can enable/disable keepalive timers if the FKA descriptor changes. Enode and VN-port keepalive timers send FIP control requests periodically. If no FCF keepalive is received, `fnic_work_on_fcs_ka_timer()` performs common cleanup, brings FDLS down, moves the iport back to FIP state, and restarts VLAN discovery. A CVL message follows a similar cleanup and rediscovery path after validating that it targets the selected FCF and local FPMA.

## State and Persistence Behavior

The file mutates `fnic->vlan_list`, `fnic->vlan_id` through the `set_vlan` callback, `iport->fip.state`, `iport->fip.flogi_retry`, `iport->selected_fcf`, `iport->fpma`, `iport->fcid`, `iport->r_a_tov`, `iport->e_d_tov`, `iport->fcfmac`, `iport->state`, and several timers. State is in-memory only and is reset on link down, CVL, FCS keepalive timeout, or explicit cleanup. VLAN list operations are protected by `vlans_lock`; some CVL and timeout paths coordinate with `fnic_lock` and reset completion state.

## Dependencies and Integration Points

`fip.c` depends on `fnic.h`, `fip.h`, Linux Ethernet helpers, FIP/FC definitions, mempool frame allocation from FDLS, FDLS OXID allocation/free, `fnic_send_fip_frame()`, `fnic_fdls_validate_and_get_frame_type()`, `fnic_fdls_register_portid()`, `fnic_fdls_disc_start()`, `fnic_fdls_link_down()`, and vNIC MAC filter programming through `vnic_dev_add_addr()`/`vnic_dev_del_addr()`.

## Risks and Edge Cases

- FIP timers share `fip_timer_work`; reinitializing work in multiple timer callbacks can be fragile if timers overlap.
- `FCOE_CTLR_MAX_SOL` is used as a solicitation-count threshold but is defined in milliseconds, so retry count semantics deserve scrutiny.
- VLAN response parsing advances by descriptor `fip_dlen` units and stops after adding one VLAN descriptor; multi-VLAN responses need validation.
- FLOGI response validation is strict on descriptor length and FC header fields; fabric variants can be dropped if assumptions are too narrow.
- CVL handling drops and reacquires `fnic_lock` while waiting for reset completion, so reset/link event ordering is a risk.
- Keepalive disable/enable changes require synchronizing FCF, enode, and VN timers to avoid stale cleanup after a valid advertisement.

## Test Signals

Useful tests include VLAN discovery with no VLANs, one VLAN, and multiple FCFs; FCF priority selection; FIP FLOGI accept and reject; FLOGI timeout/retry exhaustion; unsolicited FCF advertisements with changed FKA period/flags; enode/VN keepalive emission; FCS keepalive timeout; CVL for unrelated and local FPMA; link reset during CVL; MAC filter add/delete; and transition from FIP completion into FDLS target discovery.
