## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/snapshot.rs

### Purpose
`nvmx/snapshot.rs` defines the serialized control message sent in a custom NVMe admin command to request snapshot creation.

### Important APIs, Types, And Functions
`NvmeSnapshotMessageV1` wraps `SnapshotParams` and exposes `new()` and `params()`. `NvmeSnapshotMessage` is a versioned enum currently containing only `V1`.

### Control Flow
`handle.rs` constructs `NvmeSnapshotMessage::V1`, serializes it with bincode, places it in a DMA buffer, and sends it through a custom CREATE_SNAPSHOT admin opcode. This file only defines the payload shape.

### State, Persistence, And Dependencies
No runtime state is stored here. The message derives serde serialization/deserialization and carries `SnapshotParams`; persistence or action occurs on the receiving target side.

### Integration Points
The enum is re-exported by `nvmx/mod.rs` and used by `NvmeDeviceHandle::create_snapshot()`. The versioned enum gives room for future wire-format changes.

### Risks
The fields in `NvmeSnapshotMessageV1` are private, so external deserializers must use the enum and accessor. Bincode format compatibility must be maintained between initiator and target builds. Adding variants requires receiver compatibility handling.

### Test Signals
Test round-trip serde/bincode encoding, accessor correctness, compatibility fixtures for V1, and `handle.rs` snapshot command payload construction.
