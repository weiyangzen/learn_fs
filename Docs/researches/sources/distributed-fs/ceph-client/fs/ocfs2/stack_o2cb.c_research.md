# sources/distributed-fs/ceph-client/fs/ocfs2/stack_o2cb.c

## Purpose
`stack_o2cb.c` implements the OCFS2 stack plugin for the classic in-kernel O2CB cluster stack. It adapts OCFS2 stackglue operations to o2dlm locks, o2net connectivity checks, heartbeat node maps, and o2dlm eviction notifications.

## Important APIs, types, and functions
The file defines private `struct o2dlm_private`, plugin instance `o2cb_stack`, and operation table `o2cb_stack_ops`. Key functions map lock modes and flags (`mode_to_o2dlm`, `flags_to_o2dlm`), translate `enum dlm_status` through `status_map`, wrap lock/blocking/unlock AST callbacks, implement lock/unlock/status/LVB helpers, check cluster readiness in `o2cb_cluster_check`, connect/disconnect domains, handle evictions, and report this node's number.

## Control flow
Module init registers the `o2cb` stack plugin with stackglue. On mount, `o2cb_cluster_connect` verifies that the local node is configured, heartbeat is active, and o2net has connected to all heartbeating nodes, waiting up to sixty seconds for maps to stabilize. It allocates private state, registers an eviction callback, computes a DLM key from the domain name, joins/registers the o2dlm domain, negotiates protocol version, stores the lockspace, and registers eviction handling. Lock operations translate generic OCFS2 DLM flags/modes and call `dlmlock`/`dlmunlock`; AST wrappers route callbacks back to the connection protocol. Disconnect unregisters eviction callbacks, leaves the DLM domain, and frees private state.

## State and persistence
State is runtime-only: the plugin registration, per-connection private eviction callback, o2dlm lockspace pointer, negotiated protocol version, and lock status blocks. Cluster membership comes from heartbeat and network maps, not from this file. No filesystem metadata is persisted here.

## Dependencies and integration points
It depends on O2CB node manager, heartbeat, TCP networking, o2dlm APIs, crc32, module infrastructure, and OCFS2 stackglue. Eviction callbacks call OCFS2 recovery handlers, so this plugin is the bridge from cluster node death to filesystem recovery.

## Risks and test signals
Risks include incomplete status-to-errno mapping, AST ordering around cancel-after-grant, racing heartbeat/network maps during connect, leaking private state on failed domain registration, incorrect DLM key/name agreement across nodes, and eviction callbacks during disconnect. Test signals include mount with unconfigured node, heartbeat without o2net connectivity, multi-node lock mode/flag conversions, trylock/cancel/unlock AST behavior, LVB access, protocol negotiation mismatch, node eviction triggering recovery, and module unload after failed or successful connects.
