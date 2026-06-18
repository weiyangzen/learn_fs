# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/repair.c

Purpose: this file provides simplified TCP repair helpers for established TCP-AO sockets. It checkpoints TCP sequence queues, options, windows, timestamps, and AO repair state, then restores them into a new repaired socket.

Important APIs and functions: public helpers are `__test_sock_checkpoint`, `test_ao_checkpoint`, `__test_sock_restore`, `test_ao_restore`, `test_sock_state_free`, `test_enable_repair`, `test_disable_repair`, and `test_kill_sk`. Internal helpers include `test_sock_checkpoint_queue`, `test_sock_restore_seq`, and `test_sock_restore_queue`. It uses `TCP_REPAIR`, `TCP_REPAIR_QUEUE`, `TCP_QUEUE_SEQ`, `TCP_REPAIR_WINDOW`, `TCP_REPAIR_OPTIONS`, `TCP_TIMESTAMP`, `TCP_AO_REPAIR`, `SIOCOUTQ`, `SIOCOUTQNSD`, and `SIOCINQ`.

Control flow: checkpointing records `TCP_INFO`, local socket address, repair window, output and input queue lengths/data, MSS, and timestamp option state. AO checkpointing separately reads `TCP_AO_REPAIR`. Restore binds the socket, switches to nonblocking mode, restores queue sequence numbers, optionally binds to a device, connects in repair mode, reinstalls negotiated TCP options, restores queued data and repair window, and lets callers restore AO state.

State and persistence: `struct tcp_sock_state` owns heap buffers for saved send and receive queues; callers must release them with `test_sock_state_free`. Kernel socket state is temporarily put into repair mode. No files are written.

Dependencies and integration points: declared in `aolib.h` and used by TCP-AO restore-style tests outside this subset. It depends on Linux TCP repair UAPI and TCP-AO repair support.

Risks: this is intentionally simplified and only targets established sockets; it is not a general CRIU-quality repair implementation. Queue restore sends in chunks and backs off chunk size only after send failure, so unusual socket states can be fragile. A likely bug passes `opt_nr * sizeof(opts[0])` as the length when setting `TCP_TIMESTAMP` instead of `sizeof(state->timestamp)`.

Test signals: callers observe success by restored sockets continuing data transfer with AO state intact. Any failed getsockopt, setsockopt, ioctl, bind, connect, send, or recv path aborts through `test_error`.
