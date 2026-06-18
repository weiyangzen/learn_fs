<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/test.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/test.py

## Purpose

`test.py` performs the actual RDS TCP datapath stress test. It creates two network namespaces connected by veth, forces RDS to use TCP transport rather than loopback transport, sends 50,000 RDS messages in a pseudo-random bidirectional pattern, exercises RDS TCP sysctl reset paths, queries RDS info getsockopts, captures packets, and verifies received data by hash.

## Important APIs, Types, and Functions

The script imports Python `socket`, `select.epoll`, `ctypes`, `hashlib`, `subprocess`, `tempfile`, and `lib.py.utils.ip`. `netns_socket` forks, calls libc `setns`, creates an AF_RDS socket in the target namespace, and passes the FD back with `socket.send_fds`/`recv_fds`. It uses `socket.AF_RDS`, `SOCK_SEQPACKET`, `SOL_RDS`, RDS info option numbers `10000..10017`, `tcpdump`, `tc qdisc netem`, `sysctl net.rds.tcp.rds_tcp_rcvbuf`, and `rds_tcp_sndbuf`.

## Control Flow

Argument parsing sets log directory, timeout, packet loss/corruption/duplicate percentages. The script creates namespaces `net0`/`net1`, a veth pair, /32 addresses, routes, and a ping sanity check. It starts tcpdump in each namespace, installs netem qdiscs, arms an alarm timeout if requested, creates nonblocking RDS sockets inside namespaces, binds them to `10.0.0.1:10000` and `10.0.0.2:20000`, and registers epoll. The main loop sends until blocked, receives until caught up, and repeatedly updates RDS TCP buffer sysctls. After all packets, it probes RDS info getsockopts, stops tcpdump, moves pcaps into the log dir, and compares per-sender/receiver SHA256 streams.

## State and Persistence Behavior

State includes two namespaces, veth interfaces, addresses/routes, netem qdiscs, RDS sockets, tcpdump processes and temporary pcaps, send/receive hash dictionaries, epoll registration, and sysctl changes in the namespaces. The script writes pcaps to the log directory. It has no explicit `finally` cleanup for namespaces or qdiscs, so abnormal termination can leave namespace state behind.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root/CAP_NET_ADMIN, Python 3.9 FD-passing APIs, AF_RDS support, RDS TCP, `ip`, `ping`, `/usr/sbin/tcpdump`, `/usr/sbin/tc`, `/usr/sbin/sysctl`, and usable `/var/run/netns` namespace handles. Integration points are RDS TCP transport selection, RDS socket send/receive semantics, RDS info getsockopt ABI, netem loss/corrupt/duplicate behavior, and RDS TCP sysctl reset handling. Risks include no cleanup on exception, high packet count runtime, tcpdump path assumptions, ENOBUFS/ECONNRESET/EPIPE loops under heavy impairment, and treating only absent/mismatched hashes as fatal while most RDS info getsockopt errors are counted. Signals are `done 50000 50000`, per-flow `<sender>/<receiver>: ok`, packet captures, and final `Success`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/test.py -->
