# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf-xfrm-tests.sh

Purpose: Tests combinations of VRF, XFRM/IPsec tunnel policies/states, xfrm interfaces, and qdisc delay to ensure VRF-routed traffic still matches XFRM policy and works with/without netem on the VRF device.

Important APIs/functions: namespace/veth/VRF setup helpers, `setup_xfrm()` adding IPv4/IPv6 XFRM policies and ESP states with fixed auth/enc keys and SPIs, `setup_xfrm_dev()` creating `xfrm0` with `if_id`, and `run_cmd_host1()` executing commands in host1. `log_test()` tracks pass/fail counts and optional pause.

Control flow: main cleans/sets up two namespaces connected by veth, enslaves host1 eth0 to VRF `red`, then runs `run_tests()` twice: once with no qdisc and once after adding `tc qdisc netem delay 100ms` to the VRF. `run_tests()` verifies ping without IPsec, address-based XFRM policy for IPv4/IPv6, IPv6 VRF selector behavior, and IPv4/IPv6 traffic over an xfrm device. Some known-failure selector cases are commented out.

State and persistence: ephemeral namespaces, VRF, XFRM state/policy databases, xfrm device, qdisc, routes, addresses, and sysctls. Cleanup flushes XFRM and deletes namespaces/devices. No files.

Dependencies and integration: requires root, VRF, XFRM/ESP algorithms, xfrm interface support, ping/ping6, tc netem, and `lib.sh`.

Risks: crypto algorithm availability and xfrm interface support can vary. Commented known failures document unresolved selector matching behavior. The second run reuses topology with qdisc, so cleanup between runs is focused on XFRM rather than full namespace rebuild.

Test signals: ping exit status under `ip vrf exec` is compared to expected 0; totals are printed and final status is nonzero on any failure.
