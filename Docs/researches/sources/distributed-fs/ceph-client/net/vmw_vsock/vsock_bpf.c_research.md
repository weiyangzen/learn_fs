# sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_bpf.c

## Purpose
This file integrates AF_VSOCK sockets with BPF sockmap/sk_msg redirection. It swaps the socket protocol callbacks so BPF can intercept receive paths while preserving normal vsock receive behavior when BPF queues are empty or unsupported.

## Important APIs, types, and functions
`vsock_sk_has_data` checks the normal receive queue plus psock ingress skb and message queues. `vsock_has_data()` combines transport-level `vsock_connectible_has_data()` with BPF ingress state. `vsock_msg_wait_data()` waits on `sk_sleep(sk)` with `SOCKWQ_ASYNC_WAITDATA` set until normal or BPF data arrives. `__vsock_recvmsg()` dispatches to stream/seqpacket or datagram receive implementations based on `sk_type`.

`vsock_bpf_recvmsg()` is the replacement `recvmsg` callback. It obtains the `sk_psock`, locks the socket, falls back to native vsock receive when BPF queues are empty and normal data is present, otherwise drains BPF messages with `sk_msg_recvmsg()` and waits if necessary. `vsock_bpf_rebuild_protos()` copies a base `struct proto` and overrides `close`, `recvmsg`, and `sock_is_readable`. `vsock_bpf_update_proto()` installs or restores the protocol under sockmap control.

## Control flow
On BPF attach, `vsock_bpf_update_proto(..., restore=false)` checks that a transport exists and supports `read_skb`, rebuilds the cached BPF proto if the base proto changed, and calls `sock_replace_proto()`. On detach, it restores saved write-space and protocol pointers from `sk_psock`.

During receive, the BPF path first handles no-psock fallback. With psock present, it locks the socket and checks transport validity. If normal vsock data is present and the BPF queue is empty, it releases the lock and calls native receive. Otherwise it drains sk_msg data, waiting according to `sock_rcvtimeo()` when a zero-length read result means no message data is currently available.

## State and persistence
Global in-memory state includes `vsock_prot_saved`, `vsock_prot_lock`, and `vsock_bpf_prot`. Release/acquire ordering protects publication of rebuilt proto function pointers. Per-socket state lives in `sk_psock` and the socket proto pointer.

## Dependencies and integration points
This code depends on `linux/skmsg.h`, sockmap psock APIs, BPF infrastructure, and AF_VSOCK internal receive helpers. It integrates with transports that implement `read_skb`; transports without that callback return `-EOPNOTSUPP`.

## Risks
Incorrect proto rebuild ordering could publish stale callback pointers. Receive fallback must avoid holding the socket lock across native receive in cases where the native path expects to lock. Waiting behavior must correctly handle shutdown, nonblocking flags, and mixed normal/BPF ingress queues.

## Test signals
Sockmap tests should cover stream, seqpacket, datagram rejection/fallback, attach/detach restore, transport without `read_skb`, blocking and nonblocking receives, shutdown wakeups, and simultaneous native plus BPF queued data.
