# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.sh

## Purpose
`mptcp_sockopt.sh` is the shell harness for MPTCP socket-option and TCP_INQ tests. It builds a two-namespace, four-link topology with endpoint signaling, verifies that MPTCP traffic uses marked packets on expected subflows, then runs the C helpers `mptcp_sockopt` and `mptcp_inq`.

## Important APIs, Types, And Functions
The script uses `mptcp_lib.sh` for feature checks, namespace setup, PM commands, TAP output, file generation, counters, and transfer comparison. Key functions are `init()`, `cleanup()`, `add_mark_rules()`, `check_mark()`, `do_transfer()`, `do_mptcp_sockopt_tests()`, `do_tcpinq_test()`, and `do_tcpinq_tests()`. External dependencies are `ip`, `iptables`, `ip6tables`, `mptcp_connect`, `mptcp_sockopt`, `mptcp_inq`, and either `pm_nl_ctl` or `ip mptcp`.

## Control Flow
After `-i` option parsing, the script checks MPTCP, kallsyms, and tools, creates namespaces `ns1`, `ns2`, and `ns_sbox`, and provisions four veth pairs. Both peers receive IPv4 and IPv6 addresses, routes, endpoint signals, and `8/8` PM limits. `add_mark_rules()` permits packets with the expected fwmark and drops unmarked TCP packets to catch marking regressions. `do_transfer()` runs `mptcp_connect` listener/client pairs, captures nstat, compares files, and checks iptables DROP counters. Then `do_mptcp_sockopt_tests()` runs `./mptcp_sockopt` and `./mptcp_sockopt -6` in the sandbox namespace if `mptcp_diag_fill_info` exists. `do_tcpinq_tests()` runs `mptcp_inq` across TCP/MPTCP transmit/receive combinations when `mptcp_ioctl` exists.

## State, Persistence, And Dependencies
State consists of temporary input/output files, three namespaces, endpoint tables, route state, iptables rules, and nstat histories. Cleanup removes temp files and namespaces. The script depends on root privileges for namespaces/firewall setup, MPTCP support, kallsyms visibility, and same-directory compiled helpers.

## Integration Points
This harness connects the lower-level C helpers to the kselftest environment and the MPTCP PM setup. It uses `mptcp_lib_pm_nl_*` wrappers so the same scenarios can use either the in-tree `pm_nl_ctl` utility or the system `ip mptcp` interface. It also tests interaction with `mptcp_connect` control-message options by passing `TIMESTAMPNS` and conditionally `TCPINQ`.

## Risks
The packet-marking rules are strict: unexpected unmarked TCP control traffic can fail the mark check. The test depends on iptables legacy/nft behavior matching the options used. Feature gates skip sockopt or TCP_INQ portions when symbols are missing, so full coverage requires a kernel exposing `mptcp_diag_fill_info` and `mptcp_ioctl`. Fixed port `12001` and timeout assumptions can be fragile under parallel runs.

## Test Signals
Signals include TAP records for IPv4/IPv6 transfer, mark checks, sockopt v4/v6, and TCP_INQ variants. Failures include nonzero client/server exits, file mismatches, nonzero DROP counters, missing helper support, and C helper assertion failures.
