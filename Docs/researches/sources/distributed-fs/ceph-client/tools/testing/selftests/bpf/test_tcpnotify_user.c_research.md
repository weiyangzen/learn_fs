<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify_user.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify_user.c

## Purpose
`test_tcpnotify_user.c` is the user-space harness for a TCP sockops notification test. It loads `test_tcpnotify_kern.bpf.o`, attaches it to a cgroup, creates a perf buffer for notifications, uses iptables and `nc` to trigger TCP events, and validates that BPF map counters match received perf events.

## Important APIs, Types, And Functions
- `dummyfn()` validates `struct tcp_notifier` sentinel fields and increments `rx_callbacks`.
- `tcp_notifier_poller()` repeatedly calls `perf_buffer__poll()` until `exit_thread` is set.
- `poller_thread()` runs the perf poll loop in a pthread.
- `verify_result()` checks `tcpnotify_globals.ncalls > 0` and equality with `rx_callbacks`.
- `main()` owns cgroup setup, BPF object loading, sockops attach, map discovery, perf-buffer creation, iptables/nc trigger, map lookup, thread shutdown, and cleanup.

## Control Flow
The harness creates and joins cgroup `/foo`, loads the sockops BPF object with `bpf_prog_test_load()`, attaches it with `BPF_CGROUP_SOCK_OPS`, opens `perf_event_map` and `global_map`, then starts a perf polling thread. It installs an iptables drop rule for `TESTPORT`, runs `nc 127.0.0.1 TESTPORT` to induce TCP behavior, removes the drop rule, reads global stats, waits for late perf events, stops the thread, validates counts, prints `PASSED!`, and detaches/cleans resources.

## State And Persistence
External state includes cgroup hierarchy, attached BPF program, perf buffer, iptables INPUT rule, TCP connection attempt, and BPF map values. Cleanup detaches from the cgroup, closes cgroup fd, cleans cgroup environment, and frees the perf buffer; iptables cleanup only happens on the normal path after rule insertion.

## Dependencies And Integration Points
It depends on libbpf, pthreads, cgroup helpers, `testing_helpers`, `test_tcpnotify.h`, `iptables`, `nc`, perf events, and CAP_NET_ADMIN/root privileges.

## Risks And Edge Cases
If the process exits between adding and deleting the iptables rule, firewall state can be left behind. `sprintf()` into an 80-byte buffer is safe for current constants but brittle. The test sleeps 10 seconds for callbacks, making it slow and timing-sensitive. Missing `nc`, iptables backend differences, or insufficient privileges cause failures unrelated to BPF logic.

## Test Signals
Success prints `PASSED!` and returns zero. Failures include load/attach/map lookup errors, perf polling errors, iptables command failures, `pthread_join` failure, or count mismatch between `global_map.ncalls` and `rx_callbacks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify_user.c -->
