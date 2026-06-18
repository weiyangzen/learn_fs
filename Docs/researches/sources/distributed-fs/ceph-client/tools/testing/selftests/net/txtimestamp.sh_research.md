# sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.sh

Purpose: Namespace wrapper for `txtimestamp` that installs deterministic loopback/ifb netem delays and runs timestamp validation across TCP, UDP, raw, IP_HDRINCL raw, PF_PACKET, setsockopt, cmsg, and timestamp-without-payload modes.

Important APIs/functions: `setup()` adds 10 ms netem delay to `lo`, creates `ifb_netem0`, adds 20 ms netem there, and redirects loopback ingress to IFB with a `mirred` action. `run_test_v4v6()` supplies expected SND and ACK delays to `txtimestamp`. `run_test_tcpudpraw()` enumerates protocol modes, including fixed timestamp key tests with `-o 42`.

Control flow: if not already in a namespace, it re-execs itself through `in_netns.sh`. With no args it calls `run_test_all()`: setup, all protocol/config combinations, and final success message. With `-r|--run`, it sets up netem and passes remaining args to `./txtimestamp`; otherwise it prints usage.

State and persistence: creates temporary qdisc, IFB device, ingress filter, and netns state inside `in_netns.sh` context. No persistent files.

Dependencies and integration: requires `tc`, `ifb` module, iproute2, mirred action, root privileges, and compiled `txtimestamp`. Integrates into kselftest by exiting on first failure due to `set -e`.

Risks: depends on ifb module availability and qdisc/action support. Timing tolerances are broad but still susceptible to severe scheduling delay. It does not define its own cleanup because the namespace wrapper removes the namespace state.

Test signals: all `txtimestamp` invocations must exit 0; the wrapper prints `OK. All tests passed` only after the full matrix succeeds.
