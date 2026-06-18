# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_fcs.h

## Purpose
`bfa_defs_fcs.h` defines Fibre Channel Services visible configuration, state, statistics, and attribute contracts for virtual fabrics, local ports, virtual ports, remote ports, and initiator-target nexuses. It is the management-facing companion to the wire definitions in `bfa_fc.h` and service definitions in `bfa_defs_svc.h`.

## Important APIs and Types
The header defines `enum bfa_vf_state` plus `bfa_vf_stats_s` and `bfa_vf_attr_s` for fabric login lifecycle. Local port contracts include `BFA_FCS_MAX_LPORTS`, symbolic-name structs, `enum bfa_lport_role`, `struct bfa_lport_cfg_s`, `enum bfa_lport_state`, `enum bfa_lport_type`, `enum bfa_lport_offline_reason`, `struct bfa_lport_stats_s`, and `struct bfa_lport_attr_s`. Virtual port definitions include `enum bfa_vport_state`, `bfa_vport_stats_s`, and `bfa_vport_attr_s`. Remote port and IT nexus definitions include `enum bfa_rport_state`, `enum bfa_rport_function`, `bfa_rport_stats_s`, `bfa_rport_attr_s`, `bfa_rport_remote_link_stats_s`, `bfa_rport_qualifier_s`, `enum bfa_itnim_state`, `bfa_itnim_stats_s`, and `bfa_itnim_attr_s`.

## Control Flow and State
The enums document expected FCS state machines: VF login progresses through link down, FLOGI, auth, online, EVFP, or isolation; lports move through FDISC/online/offline; vports include FDISC retry, LOGO, cleanup, and error states; rports progress through PLOGI, online, ADISC, LOGO, rediscovery, and offline paths; ITNIMs track PRLI and online/offline callbacks. Statistics counters map directly to those transitions and protocol exchanges.

## State and Persistence Behavior
Most state is runtime discovery and login state, while `bfa_lport_cfg_s` carries configured WWNs, symbolic names, roles, preboot-vport flag, and opaque application tags that can originate from persisted or preboot configuration. Attributes expose derived runtime topology, PID, fabric name, FCoE MAC, and authentication status.

## Dependencies and Integration Points
The file includes `bfa_fc.h` for protocol structs and `bfa_defs_svc.h` for port and rport QoS/service types. `bfa_fcbuild.h` consumes `enum bfa_lport_role` in PRLI and name-server registration builders. FCS modules and management paths use these structs for queries, counters, and event payloads.

## Risks and Test Signals
Risks include enum drift from actual state machines, duplicated state values in vport definitions, statistics counters not matching transitions, and role limitations that currently only expose FCP initiator. Test with FLOGI/FDISC/PLOGI/PRLI success and reject paths, NPIV unsupported/max-resource cases, RSCN rediscovery, ADISC validation, LOGO cleanup, and management queries for each state and counter block.
