# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_rule_tests.sh

## Purpose
`fib_rule_tests.sh` validates the IPv4 and IPv6 FIB rule API. It confirms that rule selectors redirect lookups into the expected routing table, that invalid selectors are rejected, that socket traffic observes DS Field / DSCP rules during connect and send, and that VRF master-device matching behaves as expected.

## Important APIs, Functions, and Types
The script sources `lib.sh` and uses `ip`, `nettest`, and namespace helpers. Global constants define routing tables (`RTABLE`, `RTABLE_PEER`, `RTABLE_VRF`), dummy device addresses, gateways, and source addresses. `setup()` creates `testns` with `dummy0`; `setup_peer()` adds a second namespace with veth links and loopback service addresses; `setup_vrf()` creates `vrf0`. `fib_check_iproute_support()` gates optional selectors by checking both `ip rule help` and `ip route get help`.

The helper pairs `fib_rule6_test_match_n_redirect()` / `fib_rule4_test_match_n_redirect()` add a rule, run `ip route get` with a matching selector and a nonmatching selector, and then delete the rule by preference. Reject helpers verify that DS Field values containing ECN bits are not accepted as rule keys. Connect tests use `nettest` for UDP and TCP in isolated namespaces.

## Control Flow
Main parses `-t`, verifies root and `ip`, checks that `nettest` is generated, runs `cleanup`, then `setup`, and dispatches selected tests. The default `TESTS` cover plain IPv6, plain IPv4, IPv6 connect, IPv4 connect, IPv6 VRF, and IPv4 VRF. Each rule test first installs a default route in a non-main table, then adds selectors such as `oif`, `iif`, `tos`/`dsfield`, `fwmark`, `uidrange`, `sport`, `dport`, `ipproto`, `dscp`, and IPv6 `flowlabel`. VRF variants call the same selector matrix after enslaving `dummy0` to `vrf0`.

Connect tests set up a peer namespace with explicit routes in `RTABLE_PEER`, install a DS Field or DSCP rule, then verify `nettest` succeeds for matching ECN variants and fails for nonmatching values. The DS Field loops intentionally combine the configured DS value with all ECN bit combinations to prove ECN is ignored in DSCP-style matching.

## State and Persistence
State is limited to network namespaces, dummy/veth devices, routes, rules, and VRF links created during the run. Rules are deleted by preference or exact expression after each check. Peer namespaces are created only for connect tests and removed by `cleanup_peer()`. No persistent files are written.

## Dependencies and Integration Points
The file is a kselftest networking script integrated through `lib.sh` and the generated `nettest` binary. It requires root, network namespaces, dummy, veth, VRF support for VRF cases, and a sufficiently new iproute2 for optional rule selectors. The script skips optional selector blocks by printing `SKIP` but continues the surrounding test matrix.

## Risks
Because rule deletion derives preference from `ip rule show`, unexpected duplicate rules or formatting changes could delete the wrong rule in a dirty namespace; the script mitigates this by creating an isolated namespace. Some optional feature checks are coarse string matches, so new iproute2 help wording could incorrectly skip or run a block. `nettest` availability is mandatory for the script as written.

## Test Signals
Important signals include successful `ip route get ... | grep "table $RTABLE"` for matches, absence of the table marker for nonmatches, return code `2` for rejected DS Field rule additions, successful `nettest` UDP/TCP connections for matching DS Field and DSCP values, failed connections for mismatches, and VRF `oif` / `iif` selectors redirecting when the physical device is enslaved to `vrf0`.
