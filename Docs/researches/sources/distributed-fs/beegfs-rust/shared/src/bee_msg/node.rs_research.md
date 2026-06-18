## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/node.rs

### Purpose
Defines BeeGFS node discovery, heartbeat, registration, removal, and NIC wire representations. It is the protocol bridge for management, client, metadata, storage, fsck, ctl, and monitor node identity flows.

### Important APIs, Types, and Functions
- `GetNodes` (`1017`) and `GetNodesResp` (`1018`) fetch nodes by `NodeType`, with metadata-root ownership fields `root_num_id` and `is_root_mirrored`.
- `Node` is a BeeSerde struct containing alias, NIC list, numeric ID, port, unused TCP port, and node type.
- `Nic` manually serializes IPv4/IPv6 addresses, truncates interface names to 15 bytes plus a null/ignored byte, serializes `NicType`, and includes two padding bytes.
- `HeartbeatRequest` (`1019`) asks a node to send heartbeat data.
- `Heartbeat` (`1020`) and `RegisterNode` (`1039`) publish node details, ports, NICs, machine UUID, and root metadata ownership.
- `RegisterNodeResp` (`1040`) returns assigned numeric ID, gRPC port, and filesystem UUID.
- `RemoveNode` / `RemoveNodeResp` (`1013` / `1014`) remove a node and return `OpsErr`.

### Control Flow and State
The file defines state snapshots used in registration and liveness updates. The custom `Nic` deserializer validates protocol byte `4` or `6`, reads little-endian address integers, strips null bytes from names, and decodes `NicType`. Actual state insertion, heartbeat handling, and removal occur in node stores or message handlers outside this file.

### Dependencies and Integration Points
Depends on `anyhow::bail`, `std::net::{IpAddr, Ipv4Addr}`, BeeSerde primitives, and shared types. It integrates with local NIC discovery in `nic.rs`, connection address management in `conn/outgoing.rs` via `Pool::replace_node_addrs`, and BeeGFS management registration workflows.

### Risks and Edge Cases
NIC name truncation can collapse distinct interface names beyond 15 bytes. The 16th name byte is ignored on deserialization to match C/C++ behavior; changing that would create compatibility mismatches. IPv6 serialization uses little-endian conversion through `u128`, so tests should protect byte order. `Heartbeat` and `RegisterNode` have similar but not identical field order, which is a wire-compatibility trap.

### Test Signals
No tests in this file. Good test signals would include round-tripping IPv4/IPv6 `Nic`, verifying name truncation/null stripping, and rejecting invalid protocol bytes.
