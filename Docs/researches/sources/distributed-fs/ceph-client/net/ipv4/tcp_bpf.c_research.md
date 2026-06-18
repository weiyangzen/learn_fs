# sources/distributed-fs/ceph-client/net/ipv4/tcp_bpf.c

## Purpose
`tcp_bpf.c` wires TCP sockets into sockmap/sk_msg BPF infrastructure. It replaces selected protocol operations for sockets with BPF programs attached, supports redirecting sendmsg data to another TCP socket or back into ingress queues, supports parser/verdict receive paths, and restores original protocol callbacks when BPF state is removed.

## Important APIs, Types, And Functions
Public functions include `tcp_eat_skb()`, `tcp_bpf_sendmsg_redir()`, `tcp_bpf_strp_read_sock()`, `tcp_bpf_update_proto()`, and `tcp_bpf_clone()`. Core private paths are `bpf_tcp_ingress()`, `tcp_bpf_push()`, `tcp_bpf_recvmsg_parser()`, `tcp_bpf_recvmsg()`, `tcp_bpf_send_verdict()`, and `tcp_bpf_sendmsg()`. It maintains `tcp_bpf_prots[TCP_BPF_NUM_PROTS][TCP_BPF_NUM_CFGS]`, covering IPv4/IPv6 and base, TX, RX, and TXRX configurations. The code is conditional on `CONFIG_BPF_SYSCALL`, with stream parser support additionally guarded by `CONFIG_BPF_STREAM_PARSER`.

## Control Flow
Transmit redirection enters through `tcp_bpf_sendmsg()` or exported `tcp_bpf_sendmsg_redir()`. User data is copied into `sk_msg`, evaluated by BPF verdict programs, and either pushed with `tcp_bpf_push()`, redirected through `tcp_bpf_sendmsg_redir()`, corked for later evaluation, or dropped with copied-byte adjustment. Receive-side paths use `tcp_bpf_recvmsg()` for queued sk_msg ingress and `tcp_bpf_recvmsg_parser()` for parser-backed streams; both wait on `sk_sleep()` when no data is available and fall back to `tcp_recvmsg()` when no psock or queued TCP data requires normal handling. `tcp_bpf_update_proto()` chooses the correct replacement proto based on installed parser/verdict programs, handles IPv6 proto rebuilds, and restores saved ULP/proto callbacks on teardown.

## State, Persistence, Dependencies, And Integration
Persistent state is socket-local in `struct sk_psock`, saved proto pointers, corked `sk_msg`, apply-bytes accounting, redirect sockets, copied sequence tracking, and ingress queues. Global state is the rebuilt proto table plus a saved IPv6 proto pointer protected by `tcpv6_prot_lock`. The file depends on skmsg, sockmap, stream parser, TLS ULP, TCP send/receive internals, wait queues, socket memory accounting, and proto replacement helpers.

## Risks And Test Signals
Key risks are lock ordering around `lock_sock()`, reference leaks on redirected sockets/pages, incorrect copied byte accounting after BPF cuts or drops, fallback assumptions checked by `tcp_bpf_assert_proto_ops()`, IPv6 proto rebuild races, and interaction with TLS ULP callbacks. Useful tests attach sockmap programs for TX, RX, and TXRX, exercise `SK_PASS`, `SK_DROP`, `SK_REDIRECT`, cork/apply-byte cases, parser FIN handling, `SIOCINQ`, TLS sockets, IPv6 sockets, accept-child cloning, and removal/restore of psock state under active traffic.
