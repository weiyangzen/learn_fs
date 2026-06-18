# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_bench.sh

Purpose: UDP/TCP GRO benchmark harness over veth with an XDP dummy program attached to the receiver side so data is touched while measuring GSO/GRO throughput paths.

Important APIs/functions: `run_one()` creates a peer namespace and veth, assigns IPv4/IPv6 addresses, attaches `lib/xdp_dummy.bpf.o` to `veth1`, starts UDP and TCP receivers (`udpgso_bench_rx`, one with `-t`), waits for UDP port 8000, and runs `udpgso_bench_tx`. `run_udp()` runs GSO-only and GSO+GRO (`-G` receiver) modes; `run_tcp()` runs TCP.

Control flow: checks that the BPF object exists, then with no args runs IPv4 and IPv6 benchmark sets. With `__subprocess` it performs setup and execution; otherwise it wraps arguments through `in_netns.sh`.

State and persistence: temporary namespace/veth/XDP state and background receiver processes are cleaned on exit. No result file is persisted; throughput is printed by helpers.

Dependencies and integration: requires built BPF object, compiled bench helpers, XDP attach support, root privileges, and `lib.sh`. It is a performance-oriented selftest/benchmark rather than a strict functional validator.

Risks: script appears to call `run_tcp "${ipv4_args}"` under the IPv6 heading, likely preserving existing upstream behavior but worth noting because it means IPv6 TCP benchmark may not use IPv6 args. Benchmark output depends on CPU/load and is not checked against thresholds.

Test signals: primarily successful command completion and printed throughput. Missing BPF object exits nonzero with a build hint.
