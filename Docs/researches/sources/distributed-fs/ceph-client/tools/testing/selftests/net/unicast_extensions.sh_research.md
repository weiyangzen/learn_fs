# sources/distributed-fs/ceph-client/tools/testing/selftests/net/unicast_extensions.sh

Purpose: IPv4 unicast extension selftest that validates Linux behavior for historically reserved address ranges: allowed 0/8, 240/4, and high 255.255 subnets; forbidden 0.0.0.0, 255.255.255.255, 127/8, and 224/4 class D.

Important APIs/functions: uses `nettest`, `ping`, namespaces, veth, and routes. `_do_segmenttest()` checks assignment, ping both directions, and TCP connectivity on a shared segment. `_do_route_test()` checks gateway routing through a router namespace with IP forwarding. `segmenttest()` and `route_test()` wrap setup/cleanup, invert result when `expect_failure=true`, and report via `show_result()`.

Control flow: after `check_gen_prog nettest`, the script runs a fixed sequence of positive tests for 240/4, 0/8, 255.255/16, 255.255.255/24, route tests across extended ranges, and lowest-subnet-address cases. It then sets `expect_failure=true` and runs forbidden address/routing cases.

State and persistence: temporary namespaces and veths are killed/cleaned per test. `result` accumulates failures. Output is hidden during operations and restored for result lines. No persistent files.

Dependencies and integration: requires root, iproute2 netns/veth, ping, and generated `nettest`. Uses `lib.sh` for namespace setup/cleanup.

Risks: expected behavior is intentionally policy-sensitive; kernel changes to reserved address handling require flipping expectations. Use of global `expect_failure` inverts all following tests until unset.

Test signals: each scenario prints `[ OK ]` or `[FAIL]`; final exit status is `result`.
