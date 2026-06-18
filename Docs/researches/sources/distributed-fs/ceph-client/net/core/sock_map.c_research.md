# sources/distributed-fs/ceph-client/net/core/sock_map.c

## Purpose
This file implements BPF `BPF_MAP_TYPE_SOCKMAP` and `BPF_MAP_TYPE_SOCKHASH` maps, helper functions for updating and redirecting sockets, BPF iterator support, BPF link attachment for sockmap programs, and socket protocol hook teardown through psock. It is the bridge between sockets, sk_msg/sk_skb BPF programs, and map-driven redirection.

## APIs, Types, and Functions
Array sockmap state is `struct bpf_stab` with a `struct sock **sks`, map-level `sk_psock_progs`, and a spinlock. Hash sockmap state is `struct bpf_shtab` with bucket array, element count, key-sized `struct bpf_shtab_elem`, and program slots. Map ops are exported through `sock_map_ops` and `sock_hash_ops`.

Update and lookup paths include `sock_map_alloc()`, `sock_map_free()`, `sock_map_update_elem_sys()`, `sock_map_update_elem()`, `sock_map_update_common()`, `sock_map_delete_elem()`, `sock_map_lookup()`, `sock_map_lookup_sys()`, `sock_hash_alloc()`, `sock_hash_free()`, `sock_hash_update_common()`, `sock_hash_delete_elem()`, `sock_hash_lookup()`, and get-next-key functions. BPF helpers include `bpf_sock_map_update`, `bpf_sock_hash_update`, `bpf_sk_redirect_map`, `bpf_sk_redirect_hash`, `bpf_msg_redirect_map`, and `bpf_msg_redirect_hash`, with their `bpf_func_proto` descriptors.

Program and link management uses `sock_map_get_from_fd()`, `sock_map_prog_detach()`, `sock_map_prog_update()`, `sock_map_bpf_prog_query()`, `sock_map_link_create()`, and `sock_map_link_ops`. Socket teardown hooks exported to protocols are `sock_map_unhash()`, `sock_map_destroy()`, and `sock_map_close()`.

## Control Flow, State, and Persistence
Map updates first validate the socket and state, lock the socket, establish or reuse a `sk_psock`, take references to map-level programs, initialize protocol psock hooks, and install stream parser/verdict or skb verdict callbacks. A `sk_psock_link` is then stored on the psock so socket teardown can delete every map entry that references the socket. Array updates replace an indexed pointer under `stab->lock`; hash updates allocate a new RCU element, add it at the bucket head, and remove the old element if replacing.

Lookup and redirect helpers run under RCU. Redirect is refused for missing sockets, TCP listeners, vsock ingress in skb redirects, vsock msg redirects, and non-TCP egress msg redirects. Free paths synchronize with RCU, remove map entries, take socket references where needed, lock sockets outside atomic regions, unlink psock links, stop parser/verdict paths, drop program references, and then free map storage. BPF links are serialized by the global `sockmap_mutex`, which protects attach/detach/update races and map lifetime as seen by `struct bpf_link`.

Persistent state lives in map objects, psock program slots, per-socket psock link lists, saved protocol callbacks, BPF link objects, and RCU hash/list elements. Iterators maintain seq private state over either array indices or hash buckets and expose key and `struct sock *` to BPF iterator programs.

## Dependencies and Integration
Depends on the BPF map subsystem, BPF links, BTF IDs, BPF iterators, sk_msg/sk_psock infrastructure, protocol `psock_update_sk_prot` callbacks, TCP stream parser support, UDP/vsock/UNIX suitability checks, RCU, socket locking, workqueue cancellation, and sock_diag headers. Protocols integrate by allowing psock protocol replacement and by routing close/unhash/destroy through the exported sock_map wrappers.

## Risks and Test Signals
High-risk areas are psock lifetime, program reference transfers, map replacement races, socket close/unhash recursion, RCU bucket iteration, and attach-type conflict handling between stream and skb verdict programs. Bugs can cause leaked psocks, stale map entries after socket close, redirect to closed/listening sockets, deadlocks between socket locks and bucket locks, or BPF link update races. Test signals include BPF selftests for sockmap/sockhash, stream parser/verdict combinations, link attach/update/detach, map replacement under traffic, socket close/unhash teardown, iterator reads during updates, KASAN/KCSAN/lockdep, and TCP/UNIX/vsock suitability edge cases.
