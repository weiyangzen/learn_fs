<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_sockmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_sockmap.c

## Purpose
`test_sockmap.c` is a standalone user-space stress and functional test driver for sockmap/sockhash, SK_SKB, SK_MSG, cgroup sockops, ingress redirection, TLS interaction, and sendmsg/sendpage behavior. It loads `test_sockmap_kern.bpf.o` or `test_sockhash_kern.bpf.o`, attaches BPF programs to maps and cgroups, creates loopback TCP pairs, drives traffic, and validates forwarding, drops, cork/apply/push/pop transformations, and data integrity.

## Important APIs, Types, And Functions
- Global sockets `s1`, `s2`, `c1`, `c2`, `p1`, `p2` model two connected TCP pairs.
- Global flags such as `txmsg_pass`, `txmsg_redir`, `txmsg_drop`, `txmsg_apply`, `txmsg_cork`, `txmsg_start_push`, `txmsg_pop`, `txmsg_ingress`, `txmsg_redir_skb`, `txmsg_ktls_skb`, `ktls`, and `peek_flag` configure BPF behavior.
- `struct sockmap_options` stores verbosity, base/sendpage/data-test mode, expected drop behavior, iovec size/count, rate, map object name, and whitelist/blacklist strings.
- `sockmap_init_sockets()` creates, binds, listens, connects, and accepts the two TCP pairs. `sockmap_init_ktls()` enables TLS ULP and TX/RX crypto info.
- `msg_alloc_iov()`, `msg_loop()`, `msg_loop_sendpage()`, `msg_verify_date_prep()`, and `msg_verify_data()` drive traffic and validate byte streams under push/pop transforms.
- `run_options()` attaches BPF programs, populates BPF maps, runs ping-pong/sendmsg/sendpage/base variants, detaches links, zeroes maps, and closes sockets.
- Test families include `test_txmsg_pass()`, `test_txmsg_redir()`, `test_txmsg_drop()`, `test_txmsg_skb()`, `test_txmsg_apply()`, `test_txmsg_cork()`, `test_txmsg_push()`, `test_txmsg_pull()`, `test_txmsg_pop()`, and `test_txmsg_push_pop()`.

## Control Flow
`main()` parses long options, creates or opens a cgroup, enables libbpf strict mode, and either runs the full selftest suite or one requested traffic mode. Full suite mode calls `test_selftest()`, which runs sockmap, sockhash, and kTLS-prefixed variants. Each suite loads the selected BPF object with `populate_progs()`, filters the test array by whitelist/blacklist, resets global flags per subtest, and calls the selected test function. Each subtest sets global BPF-option flags and delegates through `test_send*()` to `test_exec()` and `run_options()`. Traffic execution forks RX and TX children, uses `sendmsg()`/`sendfile()` and `recvmsg()` with timeouts, then reports child exit status.

## State And Persistence
The file uses extensive process-global state for sockets, BPF map/program/link handles, counters, and current txmsg flags. Kernel state includes cgroups, BPF programs/maps/links, sockmap/sockhash contents, TCP sockets, optional kTLS state, iptables-independent loopback traffic, and socket buffer settings. `run_options()` attempts to detach cgroup sockops, detach all map links, reset map entries to zero, and close all socket fds after each run.

## Dependencies And Integration Points
It depends on libbpf, `bpf/bpf.h`, `cgroup_helpers.h`, `bpf_util.h`, Linux TLS, sockmap attach APIs, cgroup BPF attachment, local BPF objects `test_sockmap_kern.bpf.o` and `test_sockhash_kern.bpf.o`, and root/CAP_NET_ADMIN-capable networking. It complements kernel-side sockmap selftest programs in the same directory.

## Risks And Edge Cases
The driver is highly stateful; missing `test_reset()` or failed cleanup can cross-contaminate later tests. Fixed loopback ports `10000` and `10001` can collide. Forked TX/RX children complicate errno propagation. Data-integrity math for push/pop/cork/apply is subtle and deliberately disables data checking for some cork combinations. kTLS support is kernel/config dependent. BPF program order and map names in `populate_progs()` must match the object exactly.

## Test Signals
The suite prints per-subtest lines of the form `sockmap|sockhash:...:OK/FAIL` and final `Pass: N Fail: M`. A healthy specific run returns zero from `run_options()`. Failures are visible as child nonzero exit, data verification `EDATAINTEGRITY`, select timeouts, map update/attach errors, or unexpected send success/drop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_sockmap.c -->
