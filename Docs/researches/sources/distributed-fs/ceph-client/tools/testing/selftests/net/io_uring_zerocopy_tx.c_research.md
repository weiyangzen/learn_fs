# sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.c

Purpose: Transmit-side exerciser for io_uring send and send zerocopy paths over TCP or UDP. It is paired with `msg_zerocopy` by the shell harness to verify normal, zerocopy, fixed-buffer zerocopy, and mixed send modes.

Important APIs and types: Uses `mini_liburing`, `io_uring_queue_init`, `io_uring_register_buffers`, `io_uring_prep_send`, `io_uring_prep_sendzc`, `IORING_RECVSEND_FIXED_BUF`, `IORING_CQE_F_MORE`, `IORING_CQE_F_NOTIF`, sockets, `connect`, `SO_SNDBUF`, optional `UDP_CORK`, and IPv4/IPv6 sockaddr parsing.

Control flow: Option parsing selects family, destination, port, payload length, runtime, batch size, corking, and mode. `do_test` fills a page-aligned payload buffer. `do_tx` connects a socket, registers the payload as an io_uring fixed buffer, repeatedly queues `cfg_nr_reqs` sends until the runtime expires, submits, drains completions, and tracks zerocopy notification CQEs separately from send completion CQEs.

State and persistence: Global `cfg_*` variables and the static payload buffer define runtime state. No persistent state exists. CQE accounting via `compl_cqes` enforces notification balance.

Dependencies and integration: Depends on io_uring send zerocopy kernel support and the local `mini_liburing` header. The harness runs it inside veth-connected namespaces against `msg_zerocopy`.

Risks: Notification ordering and `F_MORE` semantics are subtle; mismatches cause hard failure. The test assumes fixed buffer registration succeeds and that transient send failures other than `EAGAIN` are regressions.

Test signals: Successful runs print transmit counts and complete with balanced notifications across UDP/TCP, IPv4/IPv6, and modes 1 to 3.
