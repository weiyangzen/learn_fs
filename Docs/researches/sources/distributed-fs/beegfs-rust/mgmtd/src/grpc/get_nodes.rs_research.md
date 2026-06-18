<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_nodes.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_nodes.rs

Purpose: implements node listing, optional NIC expansion, filesystem UUID reporting, and meta-root identification.

Important APIs/types/functions: `get_nodes()` reads nodes from `nodes_ext`, optionally reads NICs, resolves root inode owner to `meta_root_node` and optional `meta_root_buddy_group`, and reads `Config::FsUuid`.

Control flow: one read transaction fetches raw nodes/NICs/root/UUID. After the transaction, if NICs were requested, it groups NIC rows by node UID and formats addresses with the node port. Invalid stored IP strings fall back to IPv6 unspecified during formatting.

State and persistence: read-only; exposes `nodes`, `node_nics`, `root_inode`, and config state.

Dependencies and integration points: used by management clients and tests. Depends on DB views, `EntityIdSet`, SQLite enum conversion, and IP/socket formatting.

Risks: optional NIC inclusion can add load. The post-query NIC grouping is O(nodes * nics). Root-query joins assume one root row. IP parse fallback may hide malformed stored NIC addresses in responses.

Test signals: async test verifies node counts with/without NICs, selected NIC counts, and meta-root node UID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_nodes.rs -->
