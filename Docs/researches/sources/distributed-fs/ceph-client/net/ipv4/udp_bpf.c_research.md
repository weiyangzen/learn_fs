# sources/distributed-fs/ceph-client/net/ipv4/udp_bpf.c

## Purpose
This file adapts UDP sockets for sockmap/sk_msg BPF redirection. It swaps a UDP socket's protocol table to a BPF-aware clone that can receive bytes from a `sk_psock` ingress queue before falling back to normal UDP receive behavior.

## Important APIs, Types, and Functions
Important functions are `udp_bpf_recvmsg()`, `udp_bpf_update_proto()`, `udp_bpf_rebuild_protos()`, `udp_bpf_ioctl()`, `udp_msg_wait_data()`, and `sk_udp_recvmsg()`. It depends on `struct sk_psock`, `sk_msg_recvmsg()`, `sk_psock_get/put()`, `sock_replace_proto()`, `sock_map_close()`, `udp_prot`, and the saved IPv6 UDP proto pointer.

## Control Flow
When BPF attaches a psock, `udp_bpf_update_proto()` replaces the socket proto with a cloned proto whose close, recvmsg, readability, and ioctl methods are BPF-aware. `udp_bpf_recvmsg()` rejects error queue handling to normal inet errors, returns zero for zero-length reads, obtains the psock, drains `psock` ingress data first, waits on the socket waitqueue if only BPF data may arrive, and falls back to the original UDP receive path when the psock queue is empty. Restore puts the saved proto and write-space callback back.

## State and Persistence Behavior
The cloned protocol tables are static. IPv4 is built at late init from `udp_prot`; IPv6 is rebuilt lazily under `udpv6_prot_lock` if the saved IPv6 proto changes. Per-socket persistent state is the current proto pointer and saved psock callbacks, not packet data. Data remains in UDP receive queues or psock ingress queues.

## Dependencies and Integration Points
This integrates UDP with sockmap, sk_msg, psock lifecycle, socket waitqueues, UDP ioctl semantics, and IPv6 UDP when enabled. `udp_prot.psock_update_sk_prot` calls into this file from the base UDP proto.

## Risks
Risks include proto restoration races, stale IPv6 proto clones, incorrect `SIOCINQ` semantics when data is split between UDP queues and psock queues, and blocking receive behavior when UDP and psock queues change concurrently.

## Test Signals
Test sockmap attach/detach on IPv4 and IPv6 UDP, recvmsg priority between psock and UDP queues, blocking and nonblocking reads, zero-length reads, `MSG_ERRQUEUE`, `SIOCINQ`, socket close, and IPv6 proto rebuild after module init.
