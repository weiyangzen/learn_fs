## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/publish_capacities.rs

### Purpose
Defines `PublishCapacities`, a BeeGFS message asking metadata or storage nodes to publish capacity information, normally by sending target-info updates. The comment notes that nodes already publish periodically, so this is only for on-demand freshness.

### Important APIs, Types, and Functions
- `PublishCapacities` contains an `ack_id` encoded as `CStr<0>`.
- `impl Msg for PublishCapacities` assigns message ID `1059`.

### Control Flow and State
The file is protocol-only and has no state. When sent, the receiver should respond by publishing capacity information through the existing target-info path; the message itself only carries an acknowledgement identifier.

### Dependencies and Integration Points
Uses `super::*` for BeeSerde, C-string helper, and `Msg`. It should integrate with UDP acknowledgement and target-info update flows near `SetStorageTargetInfo` in `target.rs`.

### Risks and Edge Cases
The implementation uses `const ID: MsgID = 1059;` while the rest of the crate defines `MsgId` in `bee_msg.rs`. Unless a `MsgID` alias exists elsewhere, this is a compile-time typo. The module is also not listed in `bee_msg.rs`'s visible `pub mod` set in the inspected root, so it may currently be dead or excluded code.

### Test Signals
No tests. A simple compile check or targeted message round-trip would catch the `MsgID`/`MsgId` issue and module export status.
