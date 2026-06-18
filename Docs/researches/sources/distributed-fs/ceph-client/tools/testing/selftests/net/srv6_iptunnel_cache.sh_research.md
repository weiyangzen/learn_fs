# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_iptunnel_cache.sh

Purpose: this test checks that SRv6 lwtunnel encapsulation does not share `dst_cache` entries between forwarding input path and locally generated output path. It specifically catches a bug where forwarded traffic populates a per-CPU cache that later lets a local ping bypass its own route lookup.

Important APIs and functions: it uses `ip -6 route add ... encap seg6 mode encap`, `seg6local action End.DT6`, IPv6 rules matching `iif`, blackhole routes, static neighbors, `taskset`, and `ping`. Functions are `cleanup`, `check_prerequisites`, `setup`, and `test_cache_isolation`.

Control flow: the script checks root and tools, creates `NS_SRC`, `NS_RTR`, and `NS_DST`, wires them with two veth pairs, sets fixed MACs and static neighbors, and programs the router with an SRv6 encap route to `cafe::1`. The SID route is reachable only through table 100 for packets arriving on `veth-r0`, while the main table blackholes the SID. The test pins all pings to CPU 0, confirms local ping initially fails, forwards one ping from source to destination, then confirms local ping still fails.

State and persistence: network state is temporary and namespace-scoped. The critical state under test is kernel per-CPU destination cache inside the SRv6 lwtunnel path, not userland files. `RET` holds the final kselftest status and cleanup removes all namespaces on EXIT.

Dependencies and integration points: requires root, `ip`, `ping`, `sysctl`, `taskset`, IPv6 forwarding, SRv6 encap and End.DT6 support, policy routing, and `lib.sh`. It integrates as a standalone shell selftest with kselftest skip and fail codes.

Risks: taskset assumes CPU 0 is available to both namespace executions. Topology failures are reported as skips because they invalidate the cache-isolation signal. Static neighbor entries avoid ND noise but make the test sensitive to veth setup errors.

Test signals: a correct kernel prints `PASS: output path dst_cache is independent`. A failure prints `FAIL: output path used dst cached by input path` and exits with `ksft_fail`. If the first local ping succeeds or the forwarded ping fails, the test skips as a broken topology.
