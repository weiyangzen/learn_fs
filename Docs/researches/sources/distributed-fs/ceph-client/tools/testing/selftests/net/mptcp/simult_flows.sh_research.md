# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/simult_flows.sh

## Purpose
`simult_flows.sh` tests MPTCP throughput and scheduler behavior when two subflows are available with different bandwidth and delay profiles. It verifies that simultaneous flows complete within an expected time budget and preserve data in both transfer directions.

## Important APIs, Types, And Functions
The script uses `mptcp_lib.sh`, `ip netns`, `tc netem`, `mptcp_connect`, optional `tcpdump`, `nstat`, and file comparison. Key functions are `setup()`, `cleanup()`, `do_transfer()`, and `run_test()`. Global knobs include `capture`, `bail`, `slack`, `timeout_poll`, `timeout_test`, and `MPTCP_LIB_SUBTEST_FLAKY`.

## Control Flow
`setup()` creates three namespaces: `ns1` as connector, `ns2` as router, and `ns3` as listener. Two `ns1` to `ns2` links carry MPTCP subflows, while `ns2` to `ns3` provides forwarding to the listener. It creates a small file and a large file, enables forwarding in `ns2`, configures one subflow endpoint on `ns1`, and increases timing slack on debug kernels. `run_test()` clears old qdiscs, installs matching netem rate/delay settings on both directions of each subflow link, computes a max runtime from transfer size and aggregate bandwidth, then calls `do_transfer()` twice: small-to-large and reverse. `do_transfer()` runs `mptcp_connect -T <max_time>` on both ends, enforces a watchdog, captures nstat, compares both output files, and optionally records pcap files.

## State, Persistence, And Dependencies
Runtime state includes three namespaces, veth links, qdiscs, forwarding sysctls, endpoint limits, temp files, optional capture files, and nstat histories. Cleanup removes temp files and namespaces. The test depends on MPTCP, `ip`, `tc`, `mptcp_connect`, namespace privileges, and optionally `tcpdump` when `-c` is selected.

## Integration Points
This is a performance-sensitive MPTCP selftest using the same library result/TAP system as other scripts. It integrates with PM wrappers to configure subflow endpoints and with `mptcp_connect`'s join/time-limit options to turn throughput into a pass/fail signal.

## Risks
Timing is inherently noisy. The script compensates with slack and marks some unbalanced-bandwidth cases flaky, but overloaded CI, debug kernels, or inaccurate virtual NIC accounting can still fail. The computed time budget assumes 10 percent header overhead and uses fixed transfer sizes. Optional packet capture can perturb timing.

## Test Signals
Pass signals are both peers exiting successfully, both file comparisons passing, no timeout process remaining, and TAP entries for balanced/unbalanced cases. Failures print client/server exit codes, socket/nstat diagnostics, file sizes, and capture logs.
