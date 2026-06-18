# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_lacp_prio.sh

Purpose: Tests 802.3ad actor port priority handling and aggregator reselection.

Important APIs/functions: `setup_links()`, `test_port_prio_setting()`, `test_agg_reselect()`, `setup_ns`, `cmd_jq`, `ip -d -j link`, bond mode `802.3ad`, `ad_select actor_port_prio`, and `actor_port_prio`.

Control flow: Three namespaces emulate a client and two switches. The client bond has four slaves, split across switch and backup-switch bonds. The test sets per-slave actor priorities, verifies JSON-reported values, toggles a link to trigger aggregator reselection, then reverses priorities and verifies selection moves to the expected slave.

State and persistence: Temporary namespaces, veth links, and bonds are cleaned by `cleanup_all_ns`.

Dependencies and integration points: Requires bonding 802.3ad, LACP, iproute JSON fields for bond slave data, `jq`, and net library namespace helpers.

Risks and test signals: Failures indicate actor priority not being applied, bad aggregator reporting, or aggregator reselection regressions.
