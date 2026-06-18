<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node_nic.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/node_nic.rs

Purpose: handles persistent network interface records associated with nodes and maps them into BeeMsg-compatible NIC structures.

Important APIs/types/functions: `NodeNic` represents node UID, IP address, port, NIC type, and name. `get_all_addrs()` returns socket addresses grouped by UID for connection-pool seeding. `get_with_node()` and `get_with_type()` read NICs. `ReplaceNic` and `replace()` delete and recreate a node's NIC list. `map_bee_msg_nics()` converts DB NICs into `shared::bee_msg::node::Nic`.

Control flow: reads join `node_nics` with `nodes` to combine stored addresses with current node port. `replace()` removes all old rows for a node before inserting the provided list.

State and persistence: persists `node_nics` rows; these are refreshed at startup for management and from node registration/heartbeat paths for other nodes.

Dependencies and integration points: used by `lib.rs` startup, connection-pool initialization, gRPC `get_nodes`, gRPC `set_alias` heartbeat notification, and v7 import.

Risks: address strings are parsed at read time; malformed DB data causes errors. `replace()` is destructive for a node's NICs and should run inside transactions with validated input. Ordering is by node UID, not NIC priority.

Test signals: tests cover grouped address retrieval, per-node reads, type-filtered reads, clearing NICs, and inserting a replacement NIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node_nic.rs -->
