# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_passive_lacp.sh

Purpose: Tests that an 802.3ad bond with `lacp_active=off` behaves as a passive LACP participant.

Important APIs/functions: `check_port_state()`, `check_pkt_count()`, `setup()`, forwarding `lib.sh`, `tc` egress counters, `jq` inspection of `ad_actor_oper_port_state_str`, and `slowwait_for_counter`.

Control flow: It builds client/server namespaces connected by veth pairs and 802.3ad bonds, attaches TC filters to count LACPDUs, checks that the passive side does not initiate packets while waiting, then validates expected LACP state and packet exchange when the active peer exists.

State and persistence: Temporary namespaces, bonds, veths, and TC filters are removed by cleanup.

Dependencies and integration points: Requires bonding 802.3ad, TC flower/action pass, JSON bond slave state, and relatively long waits for LACP timers.

Risks and test signals: Long timing windows can be slow. Failure indicates passive LACP transmission/state-machine regressions.
