# sources/distributed-fs/ceph-client/net/xdp/xskmap.c

Purpose: implements the BPF `BPF_MAP_TYPE_XSKMAP` used by XDP programs to redirect packets into AF_XDP sockets.

Important APIs/functions: `xsk_map_ops` provides allocation, free, lookup, JIT lookup generation, update, delete, redirect, BTF, memory usage, and metadata comparison methods. Helpers manage per-socket `xsk_map_node` membership and `xsk_map_try_sock_delete()` removes sockets during release.

Control flow: map allocation validates key/value sizes, entry count, and flags, then allocates a flexible `xsk_map`. Updates look up a PF_XDP fd, require an RX ring, allocate a membership node, lock the map, enforce `BPF_NOEXIST`/`BPF_EXIST`, add the socket to its map list, publish the entry with RCU, and remove any old socket membership. Deletes exchange the entry with NULL and unlink the old socket node. Redirect uses `__bpf_xdp_redirect_map()` with the XSK lookup callback.

State and persistence: map state includes RCU socket pointer array, lock, and node count. Each socket tracks map entries it occupies via `xsk_map_node` on `xs->map_list`; node allocation holds a BPF map ref and count.

Dependencies and integration: integrates BPF map infrastructure, AF_XDP sockets, RCU/BH lookup contexts, generated BPF lookup instructions, BTF IDs, and socket release cleanup in `xsk.c`.

Risks and test signals: lock ordering between map lock and socket map-list lock is crucial to avoid deadlock during socket release and map update/delete. Tests should cover invalid attr sizes/flags, update with non-XDP fd, update without RX ring, map flag semantics, concurrent update/delete/close, redirect to bound/unbound sockets, RCU grace-period free, and map memory accounting.
