<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/header.go

Purpose: defines the fixed 40-byte BeeMsg header and helpers for recognizing and patching serialized headers.

Important APIs/types/functions: `HeaderLen`, `MsgPrefix`, `Header`, `NewHeader`, `Serialize`, `Deserialize`, `IsSerializedHeader`, `ExtractMsgLen`, `OverwriteMsgLen`, and `OverwriteMsgFeatureFlags`.

Control flow: `NewHeader` pre-populates the message ID and prefix while using sentinel values for length and feature flags. `Serialize` and `Deserialize` write/read fields in the exact wire order. The overwrite helpers validate length and prefix before patching little-endian bytes in-place.

State and persistence: no persistence; state is a byte-level header prefix at the beginning of each BeeMsg. `MsgLen` includes header and body, and `MsgFeatureFlags` is finalized after body serialization.

Dependencies and integration points: used by `util.AssembleBeeMsg`, `ReadFrom`, `RequestUDP`, and tests. Depends on `encoding/binary` for direct little-endian patching and `beeserde` for structured serialization.

Risks: `IsSerializedHeader` only checks buffer length and prefix, not message length sanity or message ID validity. Any header layout change breaks transport and every message. Little-endian offsets are hard-coded but align with the serialized field order.

Test signals: `header_test.go` validates round-trip serialization and overwrite behavior for length and feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header.go -->
