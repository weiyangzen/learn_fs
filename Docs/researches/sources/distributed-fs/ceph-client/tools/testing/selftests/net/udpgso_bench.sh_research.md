# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench.sh

Purpose: kselftest-style launcher for UDP/TCP GSO benchmark helper pair. It runs functional audit modes for plain UDP, sendmmsg, UDP GSO, zerocopy, TX timestamping, and TCP over IPv4/IPv6 loopback namespaces.

Important APIs/functions: maintains kselftest counters `num_pass`, `num_skip`, and `num_err` and emits PASS/SKIP/FAIL. `run_one()` starts UDP and TCP receivers on the same port, waits via `ss` until both listen, and runs `udpgso_bench_tx`. `run_udp()` enumerates UDP, sendmmsg, GSO, zerocopy, timestamp, and audit combinations. `run_tcp()` runs TCP and TCP zerocopy, with intermittent TCP zerocopy audit intentionally disabled.

Control flow: no-arg path runs full IPv4 and IPv6 matrices inside `in_netns.sh` and then calls `kselftest_exit()`. `__subprocess` runs the actual receiver/TX pair. Other args are wrapped into `run_in_netns()`.

State and persistence: process-local pass/skip/fail counters and background receiver PIDs. The namespace wrapper owns network state. No files are persisted.

Dependencies and integration: requires compiled `udpgso_bench_rx`/`tx`, `ss`, namespace wrapper, and kernel support for optional zerocopy/timestamping. TX helper returns `KSFT_SKIP` for unsupported zerocopy.

Risks: readiness check expects two `ss` listening entries for the port. Background jobs are killed with SIGHUP on exit. Throughput is not thresholded; audit modes validate completion counts.

Test signals: each subtest exit code is classified into PASS/SKIP/FAIL and final script status follows kselftest semantics.
