<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_alias.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_alias.rs

Purpose: updates the alias of a non-client entity and broadcasts node alias changes.

Important APIs/types/functions: `set_alias()` parses entity type, entity ID, and new alias. Its local `update_alias_fn` resolves the entity, rejects clients, checks alias uniqueness, updates `entities.alias`, and returns the previous entity identity.

Control flow: for node aliases, the handler updates the alias in a write transaction, re-reads the node and NIC list, then sends a BeeMsg `Heartbeat` to meta/storage/client nodes so they learn the new alias. For targets/pools/buddy groups it only updates the DB.

State and persistence: mutates `entities.alias`. For node aliases, cluster-visible state is refreshed by notification rather than direct writes to other nodes.

Dependencies and integration points: uses entity resolution, node/NIC DB helpers, `map_bee_msg_nics()`, BeeMsg heartbeat shape, and pre-shutdown guard.

Risks: returned response is empty, so clients must rely on subsequent list calls. The notification sends a heartbeat-like message with zero version fields; consumers must tolerate that. Client alias updates are explicitly unsupported.

Test signals: async test covers missing entity, wrong entity type, duplicate alias, client rejection, successful node alias update, notification emission, and DB value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_alias.rs -->
