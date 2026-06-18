# sources/distributed-fs/ceph-client/include/net/9p/transport.h

Purpose: This header defines the pluggable transport module interface for 9P clients, plus default port and RDMA queue settings.

Important APIs, types, and functions: Constants define reserved-port bounds, FD/TCP port 564, RDMA port 5640, default RDMA SQ/RQ depths, and RDMA timeout. `struct p9_trans_module` contains module list node, name, max packet size, pooled response-buffer flag, default flag, vmalloc-buffer support, owner module, create/close/request/cancel/cancelled callbacks, zero-copy request callback, and option display callback. Registration helpers are `v9fs_register_trans()`, `v9fs_unregister_trans()`, `v9fs_get_trans_by_name()`, `v9fs_get_default_trans()`, and `v9fs_put_trans()`. `MODULE_ALIAS_9P()` declares transport module aliases.

Control flow: A transport backend registers a static `p9_trans_module`. Client creation selects a backend by name or default, gets its module reference, calls `create()` with the fs context, and later sends requests through `request()` or `zc_request()`. Cancellation invokes `cancel()` and then `cancelled()` if no reply will arrive. Destroy calls `close()` and puts the module.

State and persistence behavior: Transport registry state is global and protected by the 9P transport lock in the implementation. Per-client transport state is opaque in `p9_client.trans`. No persistent storage is defined.

Dependencies and integration points: It depends on Linux modules, seq_file, fs_context, iov_iter, and the 9P client/request types. It integrates with TCP, FD, virtio, RDMA, or other transport implementations.

Risks: Backends must honor `maxsize` and pooled-buffer restrictions during msize negotiation. `supports_vmalloc` must be accurate or zero-copy/vmalloc buffers can break DMA transports. Cancellation races with late replies are a core transport hazard. Module reference handling must prevent unloading while clients exist.

Test signals: Register/unregister ordering, default transport selection, per-transport option printing, request and zero-copy paths, cancellation before send and after send, module alias autoloading, vmalloc buffer behavior, RDMA pooled-response sizing, and teardown with in-flight requests.
