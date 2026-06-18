<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/unix_bpf.c -->
# sources/distributed-fs/ceph-client/net/unix/unix_bpf.c

## Purpose
`unix_bpf.c` integrates AF_UNIX sockets with BPF sockmap/sk_msg infrastructure. It replaces socket protos with BPF-aware wrappers that route recvmsg through psock queues, use sockmap close/unhash hooks, and restore original protocols when sockets leave maps.

## Important APIs, Types, and Functions
- `unix_bpf_recvmsg()` reads from BPF psock queues first and falls back to normal AF_UNIX recv paths when needed.
- `unix_msg_wait_data()` waits for data in the socket receive queue or psock ingress queues while temporarily releasing `u->iolock`.
- `unix_dgram_bpf_rebuild_protos()` and `unix_stream_bpf_rebuild_protos()` clone base protos and override close/recvmsg/readability and stream unhash.
- `unix_dgram_bpf_update_proto()` and `unix_stream_bpf_update_proto()` install or restore BPF proto wrappers.
- `__unix_recvmsg()` dispatches to the raw AF_UNIX datagram or stream receive functions.
- `__init unix_bpf_build_proto()` builds initial wrapper protos during AF_UNIX init.

## Control Flow
When sockmap attaches a psock, the proto update hook in `af_unix.c` calls the matching update function. Restore puts back saved write-space and proto. Attach rebuilds the BPF proto wrapper if the saved base proto changed, then replaces `sk_prot`. Stream sockets also pin their peer in `psock->sk_pair` once so sockmap redirection can safely reference it until final cleanup. `unix_bpf_recvmsg()` obtains the psock, serializes with `u->iolock`, prefers already queued AF_UNIX skbs when no psock data exists, otherwise drains `sk_msg` data, waits if necessary, and falls back to normal recv when socket data arrives.

## State and Persistence
Global cached BPF proto wrappers and saved base proto pointers are protected by spinlocks and release/acquire stores. Per socket state is in `sk_prot`, `sk_write_space`, and `sk_psock` fields, including `psock->sk_pair` for streams. No persistent storage exists outside socket lifetime.

## Dependencies and Integration Points
The file depends on BPF sockmap/skmsg helpers, `af_unix.h` raw recv functions, AF_UNIX `u->iolock`, psock ingress queues, and the proto update hooks configured in `unix_dgram_proto` and `unix_stream_proto`.

## Risks and Edge Cases
The wrapper must not recursively call itself, so it uses raw `__unix_*_recvmsg()` fallbacks. Waiting releases and reacquires `u->iolock`, so queue state is rechecked after wake. Stream peer references must be taken only once even if a psock is inserted into multiple maps. Restore intentionally delays peer ref release to sockmap cleanup after RCU and pending sends.

## Test Signals
Sockmap selftests should attach AF_UNIX datagram and stream sockets, send through psock queues, mix normal receive queue data with BPF ingress data, restore sockets from maps, close/unhash streams, and verify no recursive recv, peer ref leaks, or missed wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/unix_bpf.c -->
