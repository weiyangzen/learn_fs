# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs_rport.c

## Purpose

`bfa_fcs_rport.c` implements Fibre Channel Services remote-port management for the BFA driver. It creates, logs in, authenticates, offlines, ages out, and deletes remote port objects seen by a logical port, and it bridges between fabric/lport discovery, FC ELS/CT exchanges, FC-4 initiator-target nexus management, the lower BFA hardware rport object, and BFAD/vendor event reporting.

The file is state-machine driven. The main rport state machine handles PLOGI, PLOGI accept, name-server rediscovery, ADISC validation, LOGO/PRLO handling, FC-4 online/offline callbacks, HAL rport online/offline callbacks, and deletion. A second remote-port-features state machine sends Brocade RPSC2 requests to learn remote-port speed for target-rate-limit/QoS integration.

## Important APIs, Types, and Functions

Important public entry points include `bfa_fcs_rport_create()`, `bfa_fcs_rport_create_by_wwn()`, `bfa_fcs_rport_plogi_create()`, `bfa_fcs_rport_plogi()`, `bfa_fcs_rport_scn()`, `bfa_fcs_rport_uf_recv()`, `bfa_cb_rport_online()`, `bfa_cb_rport_offline()`, scan/QoS callbacks, `bfa_fcs_rport_get_state()`, `bfa_fcs_rport_get_attr()`, `bfa_fcs_rport_lookup()`, `bfa_fcs_rport_set_del_timeout()`, `bfa_fcs_rport_set_max_logins()`, and RPF APIs `bfa_fcs_rpf_init()`, `bfa_fcs_rpf_rport_online()`, and `bfa_fcs_rpf_rport_offline()`.

Important internal helpers include PLOGI/PLOGI-ACC/ADISC/name-server/LOGO/PRLO/LS_RJT send and response routines, `bfa_fcs_rport_alloc()`, `bfa_fcs_rport_free()`, `bfa_fcs_rport_update()`, online/offline action helpers, unsolicited ELS processors, and the RPF RPSC2 send/response path. Key local state comes from `struct bfa_fcs_rport_s`: `pid`, `old_pid`, `pwwn`, `nwwn`, `reply_oxid`, `plogi_pending`, `prlo`, `scn_online`, retry counters, FCXP pointers/wait queues, timers, stats, `itnim`, `bfa_rport`, and embedded `rpf` state.

## Control Flow

Outbound discovery starts by allocating an rport, adding it to the lport queue, creating ITNIM for initiator lports, initializing the state machine, and sending PLOGI. PLOGI accept updates WWN, class-of-service, CISC, max frame size, and possibly direct-attach BB credit. The response path detects duplicate/twin rports when a newly discovered PID logs in with a WWN already represented by another rport, transfers stats, deletes the transient object, updates the existing PID, and drives the existing object online.

Inbound PLOGI stores `reply_oxid`, updates login parameters, and sends PLOGI ACC. FC-4 online then either creates a lower `bfa_rport` for target-capable peers and calls `bfa_rport_online()`, or directly marks initiator-only peers online. HAL online callback triggers ITNIM BRP online, RPF online, logging, and AEN posting.

RSCN/address-change handling uses name-server GID_PN/GPN_ID in switched fabrics and ADISC or PLOGI in loop/direct attach. Accepted responses confirm or update PID; failures retry and eventually offline/age out. Offline/delete paths first offline FC-4 and lower HAL rport as needed, then rediscover, acknowledge LOGO/PRLO, send LOGO, start a stale timer, or free the rport. FCXP allocation waits are cancelled and in-flight FCXPs are discarded on many transitions.

`bfa_fcs_rport_uf_recv()` handles only ELS frames. LOGO, ADISC, PRLO, PRLI, and RPSC are accepted or routed to FC-4 helpers; unsupported ELS commands receive LS_RJT. The RPF state machine sends RPSC2 only for non-WKA rports on switched Brocade fabrics and reports discovered speed to `bfa_rport_speed()`.

## State and Persistence Behavior

No disk state is written. The file maintains global timeout/login caps, `fcs->num_rport_logins`, lport rport-list membership, identity fields across address changes, FC-4/HAL resource pointers, retry/delete timers, stats, AEN data, and RPF speed state. Stale offline rports persist in memory until rediscovery or delete timeout.

## Dependencies and Integration Points

The file depends on BFA FCS, BFAD, FCXP, FC ELS/CT builders/parsers, lport/fabric topology helpers, ITNIM/FCPIM, HAL `bfa_rport`, physical-port attributes, timer/list/stat macros, and BFAD vendor event posting. It is called from lport/fabric discovery and lower HAL callbacks, and it feeds SCSI target nexus state through ITNIM.

## Risks and Edge Cases

The event matrix is large and sensitive to ordering among FCXP callbacks, allocation waits, timers, FC-4 callbacks, HAL callbacks, SCN, LOGO/PRLO, and delete. `bfa_rport_sm_to_state()` lacks a visible sentinel entry and can read past the table for unknown state functions. Name-server response parsing casts payloads with limited visible length validation. Twin handling can corrupt identity if PID/WWN comparisons are wrong. Freeing relies on BFAD allocation ownership. RPF only inspects the first RPSC2 entry and treats malformed speed as retryable.

## Test Signals

Validate outbound and inbound PLOGI, retry on insufficient resources, max-retry age-out, GID_PN/GPN_ID rediscovery, PID/twin changes, ADISC success/failure, LOGO/PRLO ACC paths, ITNIM online/offline callbacks, HAL rport callbacks, stale timer deletion, scan online/offline fan-out, RPSC/RPSC2 speed discovery, unsupported ELS rejection, max-login exhaustion, and unload/delete with pending FCXPs or timers.
