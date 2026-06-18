# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_join.sh

## Purpose
`mptcp_join.sh` is the broad MPTCP path-manager and MP_JOIN regression matrix. It validates subflow creation, ADD_ADDR/RM_ADDR signaling, endpoint flags, port-based endpoints, IPv4/IPv6/v4-mapped behavior, backup/fullmesh/laminar routing, syncookies, checksums, fast close, failover, userspace PM operations, event generation, and endpoint deletion/re-addition while data is flowing.

## Important APIs, Types, And Functions
The script sources `mptcp_lib.sh` and relies on `mptcp_connect`, `pm_nl_ctl` or `ip mptcp`, `ip netns`, `tc netem`, `iptables`, `ip6tables`, `ss`, `nstat`, and optional `tcpdump`. Its state variables configure each test indirectly: `addr_nr_ns1`, `addr_nr_ns2`, `test_linkfail`, `sflags`, `fastclose`, `fullmesh`, `speed`, `bind_addr`, and expected counters such as `join_syn_tx`, `join_syn_rej`, `join_csum_ns1`, and fallback expectations. Major helpers include `init_partial()`, `reset()`, `run_tests()`, `do_transfer()`, `pm_nl_set_endpoint()`, `chk_join_nr()`, `chk_add_nr()`, `chk_rm_nr()`, `chk_prio_nr()`, `chk_mptcp_info()`, `userspace_pm_*()`, `chk_evt_nr()`, and the grouped test functions listed in `all_tests_sorted`.

## Control Flow
The script builds an ordered test suite from `all_tests_sorted`, optionally restricts it with single-letter options or explicit test ids/names, and then invokes each selected group by function name. `reset()` finalizes the previous TAP result, creates or refreshes two namespaces, configures four veth pairs with IPv4 and IPv6 addresses, applies requested sysctls or packet filters, and creates temporary input/output files. `do_transfer()` starts an MPTCP listener and connector with `mptcp_connect`, optionally starts packet capture, starts a timeout watchdog, manipulates endpoints while the connection is live through `pm_nl_set_endpoint()`, waits for both sides, collects `nstat`, and compares transferred files. Each test then checks protocol counters and socket state. The tail of the script wires subtest groups for subflows, error paths, signal addresses, laminar endpoints, link failures, ADD_ADDR timeout, removals, runtime additions, IPv6, v4-mapped and mixed-family operation, backup and fullmesh changes, fast close, MP_FAIL, userspace PM, and endpoint lifecycle.

## State, Persistence, And Dependencies
Runtime state lives in temporary files, namespaces `ns1`/`ns2`, endpoint tables, MPTCP sysctls, iptables rules, tc qdiscs, background event listeners, and running `mptcp_connect` processes. Cleanup removes temp files and namespaces. The script requires root-like namespace privileges, MPTCP kernel support, `/proc/kallsyms`, `ip`, `tc`, `ss`, iptables/ip6tables, and test binaries in the same directory. Feature gates use `mptcp_lib_kallsyms_has()` and selected kernel-version checks to skip cases on older kernels.

## Integration Points
This is a central selftest entrypoint for `tools/testing/selftests/net/mptcp`. It integrates with `mptcp_lib.sh` for TAP output, feature checks, namespace management, PM abstraction, timeout handling, and counter reads. It integrates with `pm_nl_ctl.c` for low-level netlink commands unless `-i` selects `ip mptcp`. It also exercises `mptcp_connect`, `ss -M`, MPTCP MIB counters, and PM event delivery through `pm_nl_ctl events`.

## Risks
The script is intentionally stateful and timing-sensitive. Many checks depend on exact MIB counter values, but some tolerate retransmissions or flaky behavior. Packet filters and tc rules assume interface names, option offsets, and enough privilege. The indirect variable style makes local changes risky because stale environment variables can alter later tests if not reset. Some tests rely on fixed generated ports derived from the TAP counter, so ordering changes affect runtime behavior.

## Test Signals
Success is expressed through per-subtest TAP entries plus `[ OK ]` status lines. Strong signals include byte-identical transfers, expected MP_JOIN SYN/SYNACK/ACK counts, expected ADD_ADDR/RM_ADDR/MP_PRIO/MP_FAIL/MP_RST counters, expected `ss` MPTCP info, and expected event counts. Failures print socket stats, nstat deltas, file-tail diagnostics, failed test ids, and optional packet captures.
