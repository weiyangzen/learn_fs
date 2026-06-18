# sources/distributed-fs/ceph-client/include/net/ping.h

Purpose: declares the IPv4/IPv6 ping socket protocol interface, hash sizing, IPv6 module glue, proc iteration, and send/receive helpers.

Important APIs and types: `struct pingv6_ops` supplies IPv6 error/control-message callbacks when IPv6 is modular. `struct ping_iter_state` supports proc sequence iteration. `struct pingfakehdr` carries a fake ICMP header and checksum context for send fragmentation. Functions manage port allocation/hash removal, socket init/close/bind, ICMP errors, send fragments, recvmsg, common sendmsg, receive queueing, packet receive, proc init/exit, and pingv6 init/exit.

Control flow: ping sockets bind to an ICMP identifier, sendmsg builds ICMP payload/checksum, receive path matches packets to sockets, queues skbs, and reports errors/control messages through IPv4 or IPv6 glue.

State and persistence: hash tables and socket state are runtime-only; proc iteration exposes current sockets.

Dependencies and integration points: depends on ICMP, sock/proto core, netns hash, procfs, IPv6 optional hooks, and skb drop reasons.

Risks and test signals: risks include identifier hash collisions, GID permission ranges, IPv6 module glue lifetime, checksum construction, and proc iteration races. Test bind conflicts, send/recv IPv4 and IPv6 echo, ICMP errors, proc dumps, namespace isolation, and IPv6 module unload paths.
