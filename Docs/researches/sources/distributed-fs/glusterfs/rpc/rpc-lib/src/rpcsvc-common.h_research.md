## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc-common.h

Purpose: defines common RPC service state, service event types, notification callback shape, and DRC policy enums shared by RPC service implementations.

Important types: `rpcsvc_event_t` covers accept, disconnect, transport destroy, and listener dead events. `rpcsvc_notify_t` is the service notification callback type. `rpcsvc_t` stores the service rwlock, auth schemes, options, anonymous IDs, context, listener/program/notify lists, memfactor, owner xlator, callback data, rxpool, DRC pointer, outstanding request limit, lookup/throttle/security flags, and portmap registration behavior. DRC enums define operation idempotence, DRC type, LRU factors, XID state, op state, and policy. Defaults set in-memory DRC, cache size `0x20000`, and 25 percent eviction factor.

Control flow: no implementation. It establishes the state read and mutated by `rpcsvc-auth.c`, `rpc-drc.c`, `rpcsvc.c`, and transports.

State and persistence: all state is runtime service state. It includes mutable lists and flags but no persistence.

Dependencies and integration: includes pthread, xlator, compat, and dict headers. It is included by `rpc-transport.h`, so these definitions sit low in the RPC include graph.

Risks: `rpcsvc_t` is broad shared mutable state; lock discipline is critical but not enforced here. DRC enum values are used in cache logic and actor metadata, so changes can alter duplicate request behavior. Defaults are security/performance relevant.

Test signals: service initialization/teardown tests, auth and DRC integration tests, and compile checks for modules including `rpcsvc-common.h` through different paths.
