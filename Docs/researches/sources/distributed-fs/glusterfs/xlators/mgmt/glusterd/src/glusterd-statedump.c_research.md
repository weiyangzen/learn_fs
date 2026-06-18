# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.c

## Purpose
`glusterd-statedump.c` implements the glusterd private-state dumper registered from the glusterd xlator. It emits diagnostic state into GlusterFS's statedump framework for peer membership, peer RPC statistics, connected management clients, service online flags, port-map entries, management-v3 locks, and persisted daemon options.

## Important APIs, Types, and Functions
The only exported function is `glusterd_dump_priv(xlator_t *this)`. It is declared in `glusterd-statedump.h` and wired into glusterd's xlator callbacks as the private-state dump hook. File-local helpers include `glusterd_dump_peer()`, `glusterd_dump_peer_rpcstat()`, `glusterd_dump_client_details()`, and `glusterd_dict_mgmt_v3_lock_statedump()`. The `GLUSTERD_DUMP_PEERS` macro wraps RCU iteration over peer lists and dispatches the peer and optional RPC-stat dump.

## Control Flow
`glusterd_dump_priv()` obtains `this->private` as `glusterd_conf_t`, opens a statedump section named `xlator.glusterd.priv`, and then holds `priv->mutex` while reading most glusterd state. It writes identity and version fields first, then service online flags, peers, port-map brick ports, connected client transports, management-v3 lock state, and finally `priv->opts` via `dict_dump_to_statedump()`. Peer iteration uses RCU read-side locking; client transport iteration uses `conf->xprt_lock`.

`glusterd_dict_mgmt_v3_lock_statedump()` is intentionally specialized for the `mgmt_v3_lock` dictionary. For ordinary lock entries it treats `trav->value->data` as `glusterd_mgmt_v3_lock_obj` and dumps the lock owner UUID. For keys containing `debug.last-success-bt`, it dumps the value as a string.

## State and Persistence Behavior
The file does not persist or mutate durable state. It snapshots in-memory daemon state into the statedump output. The dump includes persisted options from `priv->opts`, but only by reading the dictionary. State exposure includes potentially sensitive auth or option values if they are present in `priv->opts`, because the function delegates dictionary dumping without filtering here.

## Dependencies and Integration Points
It depends on `glusterfs/statedump.h`, glusterd core structures, peer and service state from `glusterd_conf_t`, RPC transport accounting, and the management-v3 lock object layout from `glusterd-locks.h`. Its integration point is glusterd xlator diagnostics: operators or tests that trigger a process statedump use this code to inspect glusterd membership and service status.

## Risks and Edge Cases
The management-v3 lock dumper assumes dictionary values have the expected object type unless the key matches the debug backtrace pattern. Passing another dictionary is explicitly unsupported. The lock dump uses a fixed 64 KiB buffer and returns silently if formatting fails or stops producing progress, so oversized lock dictionaries can truncate diagnostic signal. `glusterd_dump_peer_rpcstat()` assumes RPC transport fields are valid while peer RCU iteration is active; this depends on surrounding lifetime rules. The port-map dump reuses the same `glusterd.brick_port` and `glusterd.brickname` keys for every entry, so consumers must understand statedump duplicate-key behavior.

## Test Signals
Useful validation is mostly integration-oriented: trigger a statedump on a glusterd with multiple peers and confirm peer UUIDs, hostnames, quorum fields, RPC counters, service flags, and client transport min/max op-version fields appear. A focused regression should include a held management-v3 lock and a `debug.last-success-bt` entry to exercise both dictionary value interpretations.
