# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ipsec_vxlan.py

Purpose: Tests VXLAN traffic protected by IPsec transport-mode crypto offload, ensuring no physical TX drops and minimum throughput.

Important APIs/functions: `xfrm()`, `check_xfrm_offload_support()`, `check_esp_hw_offload()`, `get_tx_drops()`, `setup_vxlan_ipsec()`, `_vxlan_ipsec_variants()`, `test_vxlan_ipsec_crypto_offload()`, `NetDrvEpEnv`, `Iperf3Runner`, `ksft_variants`, and `defer()`.

Control flow: For each outer/inner IPv4/IPv6 variant, the test checks ESP hardware offload, creates matching VXLAN devices locally/remotely, configures local offloaded XFRM states and mirrored remote software XFRM states, installs UDP dport 4789 policies, validates ping through inner tunnel, measures reverse iperf3 bandwidth, and checks physical TX drops did not increase.

State and persistence: Creates VXLAN links, addresses, XFRM states/policies on local and remote hosts, and reads physical link counters. Deferred cleanup removes all configured objects.

Dependencies and integration points: Requires ESP hardware offload, iproute2 XFRM offload syntax, VXLAN, IPv4/IPv6, remote endpoint, and iperf3.

Risks and test signals: Failures indicate XFRM offload, VXLAN encapsulation, GSO/checksum, drop accounting, or throughput regressions.
