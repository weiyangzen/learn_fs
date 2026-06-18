# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.c

## Purpose
`mptcp_connect.c` is the core userspace data-transfer helper for MPTCP selftests. It can act as client or server, use MPTCP or TCP sockets, and exercise multiple I/O paths, socket options, control messages, truncation/reset behavior, repeated disconnect/reconnect, and MPTCP fast open.

## Important APIs and Functions
Option parsing is handled by `parse_opts`, `parse_proto`, `parse_mode`, `parse_peek`, `parse_cmsg_types`, and `parse_setsock_options`. Socket setup uses `sock_listen_mptcp`, `sock_connect_mptcp`, `set_rcvbuf`, `set_sndbuf`, `set_mark`, `set_transparent`, `set_mptfo`, and `sock_test_tcpulp`. Data paths include `copyfd_io_poll`, `copyfd_io_mmap`, `copyfd_io_sendfile`, `copyfd_io_splice`, `do_rnd_write`, `do_rnd_read`, `do_recvmsg_cmsg`, `process_cmsg`, `do_mmap`, `do_sendfile`, and `do_splice`. Connection loops are `main_loop_s` for listeners and `main_loop` for clients; `xdisconnect` tests reconnect on an existing socket.

## Control Flow and State
`main` seeds RNG, installs a SIGUSR1 handler to set `quit`, parses options, then either listens and accepts one or more connections or connects to a peer. In poll mode, it interleaves reads and writes with nonblocking `poll`, optional random write/read chunking, truncation limits, and shutdown when input EOF is reached. In mmap/sendfile/splice modes, regular input files are transferred through the selected zero/copy path before reading the reply. Global `cfg_*` variables drive behavior; `wstate` tracks pre-read or MPTFO data still needing transmission.

## Dependencies and Integration
It depends on Linux MPTCP protocol number 262, TCP ULP behavior, socket options such as `SO_MARK`, `SO_RCVBUF`, `SO_SNDBUF`, `TCP_FASTOPEN`, `TCP_INQ`, `SO_TIMESTAMPNS_NEW`, `IP_TRANSPARENT`, and `IPV6_TRANSPARENT`, plus system calls `poll`, `mmap`, `sendfile`, `splice`, `shutdown`, and reconnect-by-`AF_UNSPEC`. It is orchestrated by `mptcp_connect.sh`, `diag.sh`, and wrapper scripts.

## Risks and Test Signals
Many code paths are intentionally sensitive to kernel semantics. Cmsg validation expects timestamp and TCP_INQ ancillary data when requested. Negative truncation tolerates reset/EPIPE to test fastclose. MPTFO preloads data into `wstate` and requires careful spool handling. Pass signals are zero exit status, matching stdout file contents in shell harnesses, and optional runtime output within `cfg_time`; failures print detailed syscall or validation errors.
