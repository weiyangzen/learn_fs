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
