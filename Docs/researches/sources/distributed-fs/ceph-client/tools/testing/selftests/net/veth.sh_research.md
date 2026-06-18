# sources/distributed-fs/ceph-client/tools/testing/selftests/net/veth.sh

Purpose: Broad veth selftest for GRO/TSO feature propagation, XDP interactions, UDP GRO forwarding aggregation, channel count constraints, and optional channel-change stress under traffic.

Important APIs/functions: creates paired namespaces and veths, uses ethtool feature/channel APIs, attaches `lib/xdp_dummy.bpf.o`, uses `udpgso_bench_tx/rx` for aggregation checks, and `nstat` with a temp history file to count `IpInReceives`. Helpers validate feature flags (`chk_gro_flag`, `chk_tso_flag`), channel counts (`chk_channels`), and GRO aggregation packet counts (`chk_gro`).

Control flow: checks BPF object, warns about CPU-dependent skips, then runs multiple fresh topologies: default feature state and aggregation, GRO on destination, XDP attach while down with GRO off/on, channel configuration validity, XDP constraints on RX/TX channels, GRO/XDP/TSO flag changes while devices down/up, and final aggregation after disabling GRO/TSO. Optional `-s seconds` runs concurrent channel churn and UDP traffic.

State and persistence: uses temp stats file under `/tmp`, two namespaces, veth features/channels/XDP state, and background jobs. Cleanup removes stats file and namespaces. `ret` tracks failures.

Dependencies and integration: requires root, ethtool channel support for veth, XDP BPF object, `nproc`, `nstat`, and compiled UDP bench helpers.

Risks: CPU count changes test coverage. Some checks rely on ethtool output text. Stress mode can be noisy and is skipped unless enough CPUs are present.

Test signals: feature/channel checks print expected vs actual; aggregation expects one packet when GRO works and ten when it does not. Invalid channel operations are expected to fail and are flagged if they succeed.
