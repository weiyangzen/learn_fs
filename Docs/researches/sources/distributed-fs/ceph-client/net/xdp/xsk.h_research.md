# sources/distributed-fs/ceph-client/net/xdp/xsk.h

Purpose: provides internal AF_XDP declarations for mmap offset v1 compatibility, XSKMAP membership nodes, socket casting, and queue pool registration helpers.

Important APIs/types: defines `struct xdp_ring_offset_v1`, `struct xdp_mmap_offsets_v1`, `struct xsk_map_node`, inline `xdp_sk()`, and prototypes for `xsk_map_try_sock_delete()`, `xsk_clear_pool_at_qid()`, and `xsk_reg_pool_at_qid()`.

Control flow: no executable flow beyond `xdp_sk()` casting a `struct sock *` to `struct xdp_sock *`. The structures are consumed by getsockopt compatibility and XSKMAP/socket cleanup paths.

State and persistence: no state is owned here. `xsk_map_node` instances persist on each socket map-list while a socket is stored in BPF XSKMAP entries.

Dependencies and integration: shared by `xsk.c`, `xskmap.c`, `xsk_queue.h`, and buffer-pool code; it ties BPF map entries back to PF_XDP socket state and netdevice queue pool operations.

Risks and test signals: declaration drift would break map cleanup or mmap offset compatibility. Tests should include old userspace offset structure reads, map update/delete while sockets close, and builds across AF_XDP core/map configurations.
