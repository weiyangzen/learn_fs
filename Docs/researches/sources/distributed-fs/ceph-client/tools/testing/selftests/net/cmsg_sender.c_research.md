# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_sender.c

Purpose: this reusable C helper sends packets with configurable socket options and ancillary data so shell tests can validate kernel cmsg behavior. It can send IPv4 or IPv6 UDP, UDP with `MSG_MORE`, ICMP/ICMPv6, or raw packets, and can set mark, priority, don't-fragment, TOS/TCLASS, TTL/HOPLIMIT, TXTIME, timestamping, and IPv6 extension-header ancillary data.

Important APIs and types: central state is the global `struct options opt`, including nested `sockopt`, `sock`, `mark`, `priority`, `txtime`, `ts`, and `cmsg` fields. It uses `getaddrinfo`, `socket`, `setsockopt`, `sendmsg`, `recvmsg(MSG_ERRQUEUE)`, `struct msghdr`, `struct cmsghdr`, `CMSG_SPACE`, `CMSG_LEN`, `SO_MARK`, `SO_PRIORITY`, `SO_TXTIME`, `SCM_TXTIME`, `SO_TIMESTAMPING`, `SO_TIMESTAMPING_OLD`, `IP_TOS`, `IP_TTL`, `IPV6_DONTFRAG`, `IPV6_TCLASS`, `IPV6_HOPLIMIT`, `IPV6_RECVERR`, and `IP_RECVERR`.

Control flow: `cs_parse_args` maps command-line options to `opt`. `memrnd` fills the payload. `main` resolves the destination, adjusts ICMPv6 protocol when needed, opens the socket, initializes ICMP/raw packet headers, applies persistent socket options in `ca_set_sockopts`, records realtime/monotonic start timestamps, builds the `msghdr`, and calls `cs_write_cmsg` to append ancillary records. It then sends `opt.num_pkt` messages and, for `MSG_MORE`, flushes with a zero-length write. If timestamping is enabled it polls the error queue through `cs_read_cmsg` until a send timestamp is observed or retry budget is exhausted.

State and persistence: the process owns one socket and one dynamically allocated payload buffer. It persists no files. Kernel-visible state is limited to the socket options and error queue. Return codes are intentionally stable for some cases, especially `ERN_SEND = 1`, because shell tests compare them.

Dependencies and integration points: included by multiple cmsg shell tests as `./cmsg_sender`. It assumes Linux socket ancillary semantics, timestamping definitions, and enough privilege for options such as `SO_MARK` in some configurations.

Risks and test signals: argument parsing uses `atoi`, so invalid numeric strings silently become zero. `malloc` is not checked before `memrnd`. Error-code labels for getaddrinfo/socket failure appear swapped in `main`, which can complicate diagnostics though most tests care about send success/failure. Strong signals are exact send length, expected return code, packet capture fields, tc filter counters, and printed `SCHED`/`SND` timestamp lines.
