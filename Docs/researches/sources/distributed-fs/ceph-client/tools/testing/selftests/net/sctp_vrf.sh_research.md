<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_vrf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_vrf.sh

## Purpose

`sctp_vrf.sh` validates SCTP behavior with VRFs and `net.sctp.l3mdev_accept`. It builds two client namespaces that use identical addresses and one server namespace with two VRFs, then checks which clients can connect to SCTP listeners under different bind and sysctl settings.

## Important APIs, Types, and Functions

The script sources `lib.sh`, loads `sctp` and `sctp_diag`, and uses `setup_ns`/`cleanup_ns`. Functions include `setup`, `cleanup`, `start_server`, `stop_server`, `wait_client`, `do_test`, `do_testx`, and `testup`. It uses `ip netns exec`, `ip link`, `ip route`, `ss -S`, `sysctl net.sctp.l3mdev_accept`, and the `sctp_hello` helper.

## Control Flow

`setup` creates `CLIENT_NS1`, `CLIENT_NS2`, and `SERVER_NS`, adds two veth pairs, configures duplicate client IPv4/IPv6 addresses, creates `vrf-1` and `vrf-2` in the server namespace, and installs per-VRF routes. `testup` runs 12 expectations for one address family, toggling `l3mdev_accept` and binding the server to no device, physical veth, or VRF. The main path runs `testup` once for IPv4 and once for IPv6.

## State and Persistence Behavior

State is scoped to temporary namespaces, veth devices, VRFs, routes, and SCTP sockets. Cleanup waits for clients, kills `sctp_hello`, and deletes namespaces. The SCTP sysctl changes are inside the server namespace.

## Dependencies and Integration Points

The test depends on SCTP, SCTP diagnostic support, VRF/l3mdev behavior, `ss`, `timeout`, and the compiled `sctp_hello` helper. It integrates with kernel socket lookup paths that decide whether unbound or bound SCTP listeners can accept packets arriving through VRF devices.

## Risks and Edge Cases

The client namespaces intentionally share the same addresses, so routing and VRF isolation must be correct for the test to mean anything. Poll loops time out after about three seconds, which can be sensitive on slow systems. Missing SCTP modules or helper binaries cause setup failure.

## Test Signals

Success is all 12 IPv4 and all 12 IPv6 cases printing `[PASS]`. Expected denies are as important as expected allows, especially no-bind behavior when `l3mdev_accept=0` and device/VRF-specific listener matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_vrf.sh -->
