# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmcommon.h

## Purpose

`dlmcommon.h` is the private shared header for the OCFS2 DLM implementation. It defines core DLM context/resource/lock structures, mastery list entries, recovery context, work items, lock resource state flags, wire message structures, message IDs, migration payload limits, helper functions, and cross-file prototypes.

## Important APIs, Types, and Functions

Hashing and sizing constants include `DLM_LOCKID_NAME_MAX`, `DLM_HASH_SIZE_DEFAULT`, `DLM_HASH_BUCKETS`, and `dlm_lockid_hash()`. Recovery and context state are represented by `struct dlm_recovery_ctxt` and `enum dlm_ctxt_state`.

`struct dlm_ctxt` is the domain-wide DLM object. It holds lockres and master hashes, dirty/purge/pending AST/BAST/tracking lists, domain maps, recovery context, master-list state, counters, debugfs root, refcount/state, heartbeat callbacks, DLM/recovery threads, workqueue, work list, network handler list, eviction callbacks, and filesystem/DLM locking protocol versions.

`struct dlm_lock_resource` is a named lock resource with hash/list nodes, refcount, granted/converting/blocked/purge/dirty/recovering/tracking lists, owner, state flags, LVB, inflight counters, AST reservation count, waitqueue, and refmap. `struct dlm_lock` stores the migratable lock header, list nodes, lock resource pointer, spinlock/refcount, AST/BAST callbacks, callback data, LKS pointer, and pending bits.

Wire structures cover mastery, migration, create/convert/unlock/proxy AST, domain join/exit, recovery, node/region query, and deref flows. Message IDs range from `DLM_MASTER_REQUEST_MSG` through `DLM_DEREF_LOCKRES_DONE`. Migration sizing is explicitly tied to `O2NET_MAX_PAYLOAD_BYTES`.

Inline helpers include lockres hash accessors, work item initialization, joining-node wakeup, LVB empty check, list index mapping, lock resource state-to-status mapping, cookie node/sequence extraction, proxy AST/BAST wrappers, lock compatibility, error-to-DLM-status mapping, node iterators, and owner changes.

## Control Flow

The header describes the DLM's major flows. Domain setup creates a `dlm_ctxt`, registers O2NET handlers, starts the DLM and recovery threads, and tracks live/domain/recovery maps. Lock acquisition creates or looks up a `dlm_lock_resource`, negotiates mastery through MLEs and mastery messages, then moves `dlm_lock` objects through blocked, converting, and granted lists. AST and BAST work is queued on pending lists and processed by DLM thread code.

Recovery and migration use the recovery context, recovery node data states, migratable lock resource payloads, request-all-locks flows, migration requests, and finalize messages. Work items allow handlers to defer operations that cannot run directly from network message context.

The wire structs and prototypes make O2NET the communication substrate: every `*_handler()` takes `struct o2net_msg`, payload length, handler data, and optional return data, matching the transport API.

## State and Persistence Behavior

All core state is in-memory cluster lock state. It is persistent only for the lifetime of a DLM domain and is reconstructed/recovered through cluster protocols after node death. The LVB in `dlm_lock_resource` is cluster-visible logical state and is migrated/recovered with lock resources, but it is not directly disk-persistent.

State flags on lock resources (`UNINITED`, `RECOVERING`, `READY`, `DIRTY`, `IN_PROGRESS`, `MIGRATING`, `DROPPING_REF`, `BLOCK_DIRTY`, `SETREF_INPROG`, `RECOVERY_WAITING`) gate whether handlers return `DLM_RECOVERING`, `DLM_MIGRATING`, or `DLM_FORWARD`, and whether callers must wait.

Migration payloads persist across the network only for one operation. `DLM_MAX_MIGRATABLE_LOCKS` is chosen so one lock resource plus 240 locks and reserved bytes fit into the O2NET payload limit.

## Dependencies and Integration Points

`dlmcommon.h` depends on `dlmapi.h`, O2NET payload limits/link classification, node manager limits, heartbeat callbacks, Linux list/hlist/kref/workqueue/waitqueue/bitmap/spinlock types, full-name hash, and OCFS2 debugfs/logging code. It is included by all DLM implementation units and is the glue between domain, mastery, recovery, AST, conversion, locking, and unlocking files.

The header also integrates DLM protocol negotiation with filesystem locking protocol versions through `struct dlm_protocol_version` fields in `dlm_ctxt` and join packets.

## Risks and Edge Cases

This header is high blast radius. Changes to structures used on the wire require coordinated protocol handling and length checks. Endianness annotations are mixed with fixed-size fields; missing conversions in implementations can break multi-architecture clusters. Lock resource list ordering is documented as significant because some functions iterate granted/converting/blocked in order.

State flag combinations are subtle. `__dlm_lockres_state_to_status()` prioritizes recovery over migration over in-progress forwarding; callers depend on that ordering. Refcounts are layered: DLM context refs, lock resource refs, lock refs, inflight refs, and list-held refs all coexist.

Migration sizing depends on `O2NET_MAX_PAYLOAD_BYTES`; changing the transport header size or payload limit affects `DLM_MIG_LOCKRES_RESERVED`. Lock names are capped at 32 bytes for DLM resources while some network messages have larger name arrays from node-manager constants.

## Test Signals

Configuration/build signals include all DLM object files compiling against this header and no wire-size overflows. Runtime tests should cover domain join/protocol negotiation, lock mastery, remote create/convert/unlock, AST/BAST, lock resource purge, node death recovery, lock resource migration, refmap deref flows, recovery lock handling, hash lookup, and DLM shutdown.

Fault injection should target O2NET link-down errors, message payload length boundaries, lock name length rejection, recovery/migration state races, duplicate or stale mastery messages, and multi-node recovery with many locks approaching `DLM_MAX_MIGRATABLE_LOCKS`.
