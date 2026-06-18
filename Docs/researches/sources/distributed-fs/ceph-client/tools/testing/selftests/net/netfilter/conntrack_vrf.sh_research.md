## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_vrf.sh

Purpose: verifies conntrack and NAT behavior on VRF devices, including conntrack zone assignment by incoming interface and masquerade behavior when traffic is transmitted through a VRF or its lower veth device.

Important APIs and tools: requires `nft`, `conntrack`, `socat`, namespace helpers, VRF device type, veth pair, `ip vrf exec`, nft `ct zone set`, `ct original zone`, `masquerade random`, and conntrack flushing.

Control flow: creates two namespaces, connects them with a veth, creates a VRF in ns0, enslaves ns0 veth to it, assigns addresses, and starts a TCP listener in ns1. `test_ct_zone_in()` loads nft rules that set ct zone for packets from the VRF/veth and checks a VRF-sourced TCP connection is tracked in the expected zone. `test_masquerade_vrf()` tests masquerade with the VRF as output, both default and pfifo qdisc variants. `test_masquerade_veth()` verifies NAT table evaluation during the lower-device iteration, expecting the veth-output masquerade counter to increment.

State and persistence: temporary netns, VRF, nft rules, conntrack entries, and socat listener. Dependencies include VRF support, nft ct zone/NAT support, and `ip vrf exec`. Risks include device-name/qdisc assumptions, NAT hook double-iteration behavior changes, and counter exactness. Test signals are PASS/FAIL lines and final `ret`.
