# sources/distributed-fs/ceph-client/net/sctp/sysctl.c

## Purpose
Registers global and per-network-namespace SCTP sysctls and implements custom handlers for coupled or side-effectful settings such as RTO bounds, authentication, UDP encapsulation port, HMAC algorithm, and PLPMTUD probe interval.

## Important APIs, Types, And Functions
Exports `sctp_sysctl_net_register`, `sctp_sysctl_net_unregister`, `sctp_sysctl_register`, and `sctp_sysctl_unregister`. Custom handlers include `proc_sctp_do_hmac_alg`, `proc_sctp_do_rto_min`, `proc_sctp_do_rto_max`, `proc_sctp_do_alpha_beta`, `proc_sctp_do_auth`, `proc_sctp_do_udp_port`, and `proc_sctp_do_probe_interval`.

## Control Flow
Static tables define global memory sysctls and per-net SCTP settings. Per-net registration duplicates `sctp_net_table`, rebases each `.data` pointer from `init_net.sctp` to the target net namespace, then patches coupled min/max `.extra*` pointers. Custom write handlers parse into temporary variables, validate ranges or strings, and only commit on success. Auth writes also update the control socket endpoint. UDP port writes serialize under `sctp_sysctl_mutex`, stop/start the UDP encapsulation socket, roll back to zero on start failure, and update the control socket cached port.

## State And Persistence
Sysctl values persist only in kernel memory per net namespace or global variables. Registration stores a table header in `net->sctp.sysctl_header`; unregister frees the duplicated table.

## Dependencies And Integration Points
Integrates with Linux sysctl infrastructure, SCTP per-net defaults, control sockets, UDP encapsulation helpers, and optional L3 master-device support.

## Risks
Important risks are incorrect pointer rebasing for netns tables, broken coupling between `rto_min` and `rto_max` or `pf_retrans` and `ps_retrans`, racing UDP socket restart, accepting invalid HMAC strings, and failing to update control socket state after sysctl writes.

## Test Signals
Read/write every custom sysctl in separate net namespaces, validate invalid range rejection, toggle auth and UDP port while associations exist, test UDP bind failure rollback, and confirm unregister frees duplicated tables without use-after-free.
