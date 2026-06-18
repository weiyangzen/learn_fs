# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-arp-interval-causes-panic.sh

Purpose: Regression test for a kernel panic in `bond_rr_gen_slave_id` when changing bond mode/options around ARP monitoring.

Important APIs/functions: `finish()`, `trap`, `ip netns`, `ip link add type bond`, `miimon`, `all_slaves_active`, `arp_interval`, `arp_ip_target`, `ping`, and `/proc/sys/kernel/panic`.

Control flow: The script creates `server` and `client` namespaces connected by veth, validates active-backup traffic, detaches the slave, recreates bond settings as round-robin with ARP interval and target, reattaches the slave, and validates traffic again.

State and persistence: It writes `/proc/sys/kernel/panic` to 180, which persists beyond the process until changed. Network namespaces are deleted by `finish()` on exit.

Dependencies and integration points: Requires bonding, veth, namespace support, root privileges, and IPv4 ping. It targets bonding mode transition and ARP monitor kernel paths.

Risks and test signals: The panic sysctl side effect is notable. A kernel crash or script failure indicates regressions in bond mode changes, slave reattachment, ARP monitor setup, or round-robin slave selection.
