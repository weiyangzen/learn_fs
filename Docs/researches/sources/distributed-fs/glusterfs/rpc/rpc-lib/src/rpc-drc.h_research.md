## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpc-drc.h

Purpose: declares duplicate request cache structures and API for RPC services.

Important types: `drc_client` stores a peer address, rb tree of cached operations, op count, atomic ref, and list node. `drc_cached_op` stores operation state, program identifiers, cached transport message, owning client, list nodes, ref field, and XID. `drc_globals` stores allocator-compatible first member, lock, hit counters, mempool, global and client lists, counts, cache size, DRC type, LRU factor, and status.

Important APIs: declares need/lookup/send/cache request and reply functions, statedump function, init/deinit, and reconfigure.

Control flow: no implementation. The type layout shows two indexes over cached replies: per-client rb tree and global LRU list.

State and persistence: defines in-memory cache state. No durable persistence.

Dependencies and integration: includes `rpcsvc.h`, Gluster locking/dict headers, and `rb.h`. It depends on DRC enums from `rpcsvc-common.h` and transport message types.

Risks: exposed struct layout makes cache internals available to callers. The `allocator` first-member requirement is subtle and must be preserved. Cached iovec/iobref ownership must follow implementation rules.

Test signals: compile checks under GNFS/non-GNFS variants and runtime DRC tests from `rpc-drc.c`.
