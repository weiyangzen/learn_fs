# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter_setsockopt.c

## Purpose
This serial selftest verifies that a TCP BPF iterator can call socket option helpers to change congestion control on listening, reuseport listening, established, and accepted TCP sockets. It specifically migrates sockets from the test `bpf_cubic` congestion-control implementation to `bpf_dctcp`.

## Important APIs, Types, And Functions
Key helpers are `create_netns()`, `set_bpf_cubic()`, `check_bpf_dctcp()`, `make_established()`, `get_local_port()`, `do_bpf_iter_setsockopt()`, and `serial_test_bpf_iter_setsockopt()`. It uses `unshare(CLONE_NEWNET)`, `system("ip link set dev lo up")`, `start_server()`, `start_reuseport_server()`, `connect_to_fd()`, `accept()`, `setsockopt(TCP_CONGESTION)`, `getsockopt(TCP_CONGESTION)`, `bpf_program__attach_iter()`, `bpf_iter_create()`, and struct_ops attachment through `bpf_map__attach_struct_ops()`.

## Control Flow
The entry point creates a private network namespace, loads and attaches the iterator skeleton, then loads and attaches `bpf_cubic` and `bpf_dctcp` struct_ops. `do_bpf_iter_setsockopt()` creates one non-reuseport listener and 256 accepted/established connections, creates 256 reuseport listeners, records the listen ports in the iterator BSS, drains the iterator FD, and then checks every participating socket reports `bpf_dctcp` as its congestion algorithm. The same workflow runs with `random_retry` enabled and disabled.

## State And Persistence Behavior
State is transient in the new network namespace, socket FDs, congestion-control struct_ops links, and iterator skeleton BSS fields `listen_hport`, `reuse_listen_hport`, and `random_retry`. The test leaves no intended persistent state; all sockets, links, and skeletons are destroyed in `done` paths.

## Dependencies And Integration Points
It depends on network namespace support, loopback configuration via `ip`, TCP congestion-control socket options, BPF iterator helpers, and the `bpf_iter_setsockopt`, `bpf_cubic`, and `bpf_dctcp` BPF programs. It integrates with selftest network helpers for server setup, reuseport fanout, connection creation, and FD cleanup.

## Risks And Edge Cases
The test is resource-heavy because it creates hundreds of sockets twice. It can fail if network namespaces are unavailable, `ip` is missing, loopback cannot be brought up, struct_ops TCP CA attachment is unsupported, or congestion-control names collide with system algorithms. Read handling tolerates `EAGAIN` retry from iterator draining.

## Test Signals
Passing signals are successful netns setup, successful struct_ops attachment, all sockets initially accepting `bpf_cubic`, iterator read completion without error, and `check_bpf_dctcp()` returning the full socket count for reuseport listeners, normal listener, established clients, and accepted server sockets.
