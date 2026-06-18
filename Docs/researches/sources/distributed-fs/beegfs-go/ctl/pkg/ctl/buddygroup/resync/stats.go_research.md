# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/stats.go

Purpose: retrieves metadata or storage buddy resync statistics by resolving a buddy group to its primary target and querying the owning node.

Important APIs/types/functions: `GetMetaResyncStats`; `GetStorageResyncStats`; `getNode`; `GetPrimaryTarget`.

Control flow: stats functions call `getNode` for a primary target, initialize the node store, send the appropriate BeeMsg stats request to the owning node, and return the response. `getNode` uses mappings to map target alias to node. `GetPrimaryTarget` scans buddy groups and matches the provided entity ID by UID, alias, or legacy ID.

State and persistence: read-only; queries live node stats.

Dependencies and integration points: uses `config.NodeStore`, util mappings, buddygroup listing, BeeMsg resync messages, and BeeGFS entity ID variants.

Risks: `getNode` ignores only RST mapping errors but still assumes `mappings` is usable; a nil mappings value after ignored errors would be dangerous if `GetMappings` can return nil. Mapping by `pTarget.Alias` requires alias population. Legacy ID matching calls `ToProto` repeatedly and compares numeric/type fields. Stats should use primary targets only, so stale buddy group state can mislead callers.

Test signals: no direct tests. Useful tests would cover all entity ID match forms, not-found behavior, mapping failures, and correct BeeMsg request target IDs.
