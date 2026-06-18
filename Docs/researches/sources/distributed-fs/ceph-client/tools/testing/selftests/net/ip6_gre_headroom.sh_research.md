# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_gre_headroom.sh

Purpose: Regression smoke test that verifies the first packet mirrored through IPv6 GRE-like devices has enough headroom and does not trigger a kernel panic.

Important commands: Creates veth pairs, a VRF, IPv4 and IPv6 addresses, `tc clsact` ingress mirroring, `ip6erspan` and `ip6gretap` devices, and uses `ping` to generate traffic.

Control flow: `setup_prepare` builds local devices, addresses, VRF attachment, traffic-control ingress hook, and two tunnel devices. `test_headroom` attaches a `matchall` ingress filter on `swp1` that mirrors packets to the selected tunnel, sends one ping through `h1`, removes the filter, and prints pass if the system survives. Cleanup deletes tunnel, veth, and VRF devices.

State and persistence: Temporary devices in the current network namespace. Cleanup removes them. No files are written.

Dependencies and integration: Requires root, `ip`, `tc`, `ip6erspan` and `ip6gretap` support, and packet mirroring action support.

Risks: The pass criterion is absence of panic, not packet delivery validation. Device names are fixed and can conflict with existing interfaces if run outside an isolated environment.

Test signals: Printed PASS lines for `ip6gretap headroom` and `ip6erspan headroom`; a kernel crash or command failure indicates regression or missing support.
