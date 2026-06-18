# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-break-lacpdu-tx.sh

Purpose: Regression test ensuring LACPDU transmission continues after setting a bond MAC address.

Important APIs/functions: forwarding `lib.sh`, `cleanup()`, bridge creation, `ip link add ... type bond mode 4`, bond `ad_actor_sys_prio`, `lacp_rate fast`, `tc qdisc clsact`, flower filter for protocol `0x8809`, `slowwait_for_counter`, and `tc_rule_handle_stats_get`.

Control flow: It deletes stale test devices, creates bridge `fab-br0`, creates 802.3ad bond `fbond`, sets its MAC and LACP parameters, enslaves two veth ports, brings links up, attaches a TC ingress counter to the peer, and waits for at least two LACPDUs.

State and persistence: Creates bridge, bond, veths, and TC filters; `cleanup()` removes devices on exit.

Dependencies and integration points: Requires bonding 802.3ad, veth, bridge, TC flower, and forwarding library wait/stat helpers.

Risks and test signals: Failure means LACPDUs are not observed after MAC/config changes. Timing can be sensitive to LACP timers and TC counter updates.
