<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/header_test.go

Purpose: unit tests for header serialization and in-place header mutation helpers.

Important APIs/types/functions: `TestHeaderSerialization`, `TestOverwriteMsgLen`, and `TestOverwriteMsgFeatureFlags`.

Control flow: the serialization test writes a header through `beeserde`, deserializes it, and compares all fields. Overwrite tests first assert failures for short or prefixless buffers, then install `MsgPrefix` and verify little-endian field updates.

State and persistence: in-memory byte slices only.

Dependencies and integration points: depends on `encoding/binary`, `testify/assert`, and `beeserde`. It protects `util.AssembleBeeMsg` because that function relies on the overwrite helpers after body serialization.

Risks: tests do not cover `ExtractMsgLen`, invalid message IDs, or malformed but correctly prefixed headers with impossible lengths.

Test signals: good coverage for the core happy path and validation gates of header overwrites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header_test.go -->
