# sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2tp.sh

Purpose: L2TPv3 tunnel connectivity test across two host namespaces and a router namespace, with and without IPsec transport protection and after IPsec teardown.

Important commands: Sources `lib.sh`; uses namespace creation, veth pairs, IPv4/IPv6 forwarding sysctls, `ip l2tp add tunnel/session`, route setup, `ping`/`ping6`, `ip xfrm policy`, and `ip xfrm state` with ESP AEAD `rfc4106(gcm(aes))`.

Control flow: `setup` creates host_1, host_2, and router namespaces, assigns loopback service addresses, connects hosts to the router, enables forwarding, configures routes, and creates IPv4 and IPv6 L2TP sessions. `run_ping` validates basic tunnel endpoint and routed loopback connectivity for both families. `setup_ipsec` installs bidirectional XFRM policies and states for the underlay addresses. `run_tests` validates plain L2TP, L2TP with IPsec, repeats selected protected pings, tears IPsec down, and validates L2TP still works afterward.

State and persistence: Temporary namespaces, l2tp devices, routes, and XFRM state/policy. Cleanup removes namespaces.

Dependencies and integration: Requires root, `ip l2tp`, L2TPv3 kernel support, XFRM ESP with AES-GCM support, and ping utilities.

Risks: `run_cmd` uses `eval`, so command construction must remain controlled. Duplicate ping checks in the IPsec phase make reporting slightly redundant. Missing crypto support will fail setup.

Test signals: Counts of passed and failed tests are printed; any failed ping or XFRM command sets final failure state.
