<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.c

## Purpose

`so_txtime.c` is the command-line exerciser for the `SO_TXTIME` API. It sends or receives timestamp-scheduled one-byte UDP packets and validates delivery timing, packet order, and transmit error-queue behavior.

## Important APIs, Types, and Functions

Important globals configure clock, port, variance, start time, socket mark, rx/tx mode, packet list, expected error-queue cmsg level/type, and source/destination sockaddrs. Core functions are `gettime_ns`, `do_send_one`, `do_recv_one`, `do_recv_verify_empty`, `do_recv_errqueue_timeout`, `recv_errqueue_msgs`, `start_time_wait`, `setsockopt_txtime`, `setup_tx`, `setup_rx`, `do_test_tx`, `do_test_rx`, `setup_sockaddr`, `parse_io`, `parse_opts`, and `main`.

Kernel APIs include `setsockopt(SO_TXTIME)` with `SOF_TXTIME_REPORT_ERRORS`, `getsockopt(SO_TXTIME)`, `SCM_TXTIME` cmsgs, `sendmsg`, `recv`, `recvmsg(MSG_ERRQUEUE)`, `poll(POLLERR)`, `SO_EE_ORIGIN_TXTIME`, and optional `SO_MARK`.

## Control Flow

`parse_opts` selects IPv4 or IPv6, `CLOCK_TAI` or monotonic, source/destination addresses, rx mode, start time, mark, and a comma-separated payload/delay stream. TX mode connects a UDP socket, enables `SO_TXTIME`, waits for the synchronized start, sends each packet with optional `SCM_TXTIME`, and drains error-queue messages until all expected reports or max delivery time. RX mode binds, waits for the same start, receives packets in expected order, checks arrival time against configured variance, then verifies the queue is empty.

## State and Persistence Behavior

State is per-process globals and per-socket txtime configuration. `glob_tstart` is the local reference time for converting relative delays to absolute delivery times. No files or sysctls are changed by this program; qdisc state is configured by `so_txtime.sh`.

## Dependencies and Integration Points

It depends on UDP, socket timestamping ABI headers, `SO_TXTIME`, error queues, and a qdisc that honors txtime for strict scheduling tests, typically `fq` or `etf`. It integrates with the shell wrapper that runs TX and RX instances in separate namespaces with synchronized start times.

## Risks and Edge Cases

Timing assertions are sensitive to scheduler latency; `KSFT_MACHINE_SLOW` downgrades excessive variance. Negative delays omit `SCM_TXTIME` and mean immediate send. Error queue parsing must match IPv4 `IP_RECVERR` or IPv6 `IPV6_RECVERR` cmsg types. The max packet count is eight, and malformed payload streams are not deeply validated.

## Test Signals

TX logs dropped packets with `missed txtime` or `invalid txtime` reasons from the error queue. RX logs payload delay and expected delay. Success is zero exit; failures indicate timing variance, payload mismatch, unexpected delivery, missing error-queue semantics, or `SO_TXTIME` getsockopt mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.c -->
