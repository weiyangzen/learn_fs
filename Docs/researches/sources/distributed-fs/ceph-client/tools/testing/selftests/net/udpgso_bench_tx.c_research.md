# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_tx.c

Purpose: Transmitter for UDP/TCP GSO benchmarks and audit tests. It can send plain UDP chunks, UDP_SEGMENT GSO messages, sendmmsg batches, TCP streams, zerocopy sends, and TX timestamped sends while tracking completion/error-queue acknowledgements.

Important APIs/functions: supports `SO_ZEROCOPY`, `MSG_ZEROCOPY`, `SO_TIMESTAMPING`, `SOF_TIMESTAMPING_TX_SOFTWARE/HARDWARE`, `UDP_SEGMENT`, `sendmmsg`, `sendmsg`, `sendto`, TCP `send`, PMTU discovery, error queue `recvmsg(MSG_ERRQUEUE)`, and optional CPU affinity. `flush_cmsg()` accounts timestamp and zerocopy completions; `print_audit_report()` enforces expected completion counts in audit mode.

Control flow: parses options requiring `-4` or `-6` and a destination, validates incompatible combinations, computes MSS and maximum payload, fills rotating payload buffers, creates and optionally connects a socket, enables zerocopy/timestamp/PMTU, then loops sending until message count, runtime, or SIGINT. Periodically flushes error queue for zerocopy/timestamps and prints per-second throughput; final audit flush waits for completions and validates counts.

State and persistence: global config, total counters, timestamp/zerocopy completion counters, start/end time, and static packet buffers. No persistent files.

Dependencies and integration: driven by `udpgso_bench.sh`, `udpgro*.sh`, `veth.sh`, and `udpgro_fwd.sh`. Requires receiver availability, optional kernel zerocopy/timestamp support, and returns `KSFT_SKIP` when zerocopy is unsupported.

Risks: audit mode depends on timely error queue completions within `cfg_poll_loop_timeout_ms`. Hardware TX timestamping may not be available on virtual devices. Payload length is capped by `ETH_MAX_MTU - hdrlen`.

Test signals: normal mode prints throughput and exits on socket errors. Audit mode fails if TX timestamp count or zerocopy completion count does not match sends, making it useful as a correctness check in shell wrappers.
