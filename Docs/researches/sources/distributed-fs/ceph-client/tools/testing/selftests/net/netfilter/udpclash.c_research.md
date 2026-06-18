<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/udpclash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/udpclash.c

## Purpose
This helper emits many concurrent UDP datagrams from one socket to the same remote tuple to exercise conntrack clash-resolution races. It mimics resolver libraries that send parallel requests sharing source and destination tuples.

## Important APIs, Types, And Functions
Core pieces are `struct thread_args`, global `wait`, `thread_main()`, `run_test()`, and `main()`. It uses pthreads, a nonblocking `SOCK_DGRAM|SOCK_CLOEXEC` socket, `sendto()`, `recvfrom()`, `bind()`, `inet_ntop()`, `inet_addr()`, and `usleep()`.

## Control Flow
`main()` parses destination IP/port, creates and binds an unconnected UDP socket to an ephemeral local port, and calls `run_test()`. `run_test()` creates 128 threads that spin on a shared flag, releases them simultaneously, joins all sends, then polls the socket until it receives 128 replies or times out. It validates reply source address and port against the requested remote.

## State, Persistence, And Dependencies
State is process-local: one UDP socket, thread IDs, a shared wait flag, and receive counters. It has no persistent files. The surrounding test must provide an echo server and any netfilter/conntrack rules under test.

## Integration Points
This binary is a targeted stress generator for nf_conntrack insertion clash logic. It pairs with netfilter tests that inspect whether racing UDP packets create correct state and receive all replies.

## Risks
The busy-wait flag is `volatile int`, not a formal synchronization primitive, although thread creation/join timing is sufficient for this test style. A send failure exits the whole process from a worker thread. Nonblocking receive loops use a fixed 5 second aggregate timeout and may be flaky under severe load.

## Test Signals
Success prints `got 128 of 128 replies` and returns 0. Fewer replies, wrong source warnings, socket/bind errors, allocation failure, or pthread failures indicate regressions or environment problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/udpclash.c -->
