# sources/distributed-fs/beegfs-protobuf/proto/beewatch.proto

**Purpose:** This proto defines BeeGFS Watch event delivery and subscriber acknowledgement messages. It provides a common `Event` envelope for versioned event payloads and a bidirectional streaming `Subscriber.ReceiveEvents` RPC.

**Important APIs/types/functions:** `Event` carries `seq_id`, `meta_id`, optional `meta_mirror`, `event_flags`, and oneof `event_data` with either `V1Event` or `V2Event`. `V1Event` models legacy BeeGFS v7 event types from `FLUSH` through `READ` and includes dropped/missed sequence counters plus path and entry ID fields. `V2Event` models BeeGFS v8 events with an explicit `INVALID = 0`, link count, path/entry fields, message user ID, timestamp, and newer event kinds such as open modes, writer closed, blocked open, stripe pattern changed, and inode locked. `Response` lets subscribers acknowledge `completed_seq` and request graceful shutdown with `shutting_down`.

**Control flow:** Producers stream `Event` messages to a subscriber; the subscriber streams `Response` messages back as it completes processing. Consumers inspect the `event_data` oneof to branch between v1 and v2 payloads. The envelope intentionally avoids minor-version markers; additive protobuf evolution is expected for minor API changes.

**State and persistence behavior:** Sequence tracking is represented by `seq_id` in the envelope and `completed_seq` in responses, while v1 also reports dropped/missed sequence counts. `meta_mirror` is optional so absence can be distinguished from mirror ID zero. Event flags are a raw bitmask whose constants live outside this proto. Persisted event records must preserve oneof case, sequence IDs, and version-specific fields.

**Dependencies and integration points:** The proto has no imports. It integrates with BeeGFS metadata/watch services and generated C++/Go/Rust protobuf outputs. The `Subscriber` service binds this schema to a stream transport used by watch subscribers.

**Risks:** `V1Event.Type` defaults to `FLUSH = 0`, so default-constructed v1 events can appear valid unless callers check envelope context. The raw flag bitmask needs shared constants from `EventContext.h`. Consumers must handle missing `event_data`, unknown enum values, and v1/v2 semantic differences. Minor version changes must remain additive to avoid breaking subscribers.

**Test signals:** Tests should round-trip v1 and v2 events, verify oneof exclusivity, preserve optional `meta_mirror` presence including explicit zero, process acknowledgement sequencing, and cover unknown future fields/enums. Streaming tests should confirm graceful shutdown signaling and backpressure/error behavior around `ReceiveEvents`.
