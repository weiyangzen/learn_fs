<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/event.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/event.go

Purpose: serializes a BeeWatch/protobuf file event payload into BeeMsg wire form.

Important APIs/types/functions: `FileEvent` contains protobuf event `Type`, path bytes, and optional target bytes. `Serialize` writes the event type, C-string path, and a boolean `targetValid` followed by target C-string when `Target != nil`.

Control flow: serialization rejects negative protobuf enum values before writing because BeeMsg expects an unsigned value. Target serialization is conditional on nil, not length, so an empty non-nil target still means target-present.

State and persistence: no persistence; event data is carried in a single serialized message body.

Dependencies and integration points: depends on `beeserde` and `github.com/thinkparq/protobuf/go/beewatch`. This is likely embedded in larger event-carrying messages, while `entry.go` comments show some file-event support is not implemented for certain entry messages.

Risks: there is no deserializer or direct tests here. The signed-to-unsigned enum assumption depends on protobuf event definitions staying non-negative.

Test signals: no direct test file in this subset; behavior is simple but protocol-facing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/event.go -->
