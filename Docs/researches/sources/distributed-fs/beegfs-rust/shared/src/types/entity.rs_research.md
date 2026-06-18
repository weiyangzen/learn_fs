## sources/distributed-fs/beegfs-rust/shared/src/types/entity.rs

### Purpose
Defines entity identity abstractions: entity type, validated aliases, legacy numeric IDs, flexible entity ID selectors, and complete entity ID sets.

### Important APIs, Types, and Functions
- `EntityType` distinguishes node, target, buddy group, and pool, with display strings and optional protobuf conversion.
- `Alias` wraps `String` and validates aliases with regex `^[a-zA-Z][a-zA-Z0-9-_.]+$` and max length 32.
- `TryFrom<String>` and `TryFrom<&str>` construct aliases; `AsRef<str>`, `From<Alias> for String`, and `Display` expose values.
- `LegacyId` stores `NodeType` plus numeric ID and displays as `type:num`.
- Optional protobuf conversions validate `LegacyId` node type and nonzero numeric ID.
- `EntityId` is a selector enum: alias, legacy ID, or UID, with display and optional protobuf conversion from `EntityIdSet`.
- `EntityIdSet` contains all three identifiers and provides `node_type()` and `num_id()` accessors plus display formatting.

### Control Flow and State
No persistent state. Validation occurs during alias and protobuf conversions. Ambiguous protobuf `EntityIdSet` conversion to `EntityId` prefers UID, then alias, then legacy ID if multiple fields are present.

### Dependencies and Integration Points
Uses shared `NodeType`/`Uid`, `regex::Regex` with `LazyLock`, `anyhow`, display traits, and optional protobuf types. Used by management APIs, gRPC request parsing, and entity lookup logic.

### Risks and Edge Cases
Alias regex requires at least two characters because it has one leading character plus `+` for the remainder; a single-letter alias is rejected. Protobuf `EntityIdSet` to `EntityId` precedence can hide conflicting fields rather than rejecting them. `EntityIdSet` itself assumes a node-style legacy ID, which may not fit target/pool/buddy-group entities without higher-level context.

### Test Signals
No local tests. Needed tests include alias boundary lengths, single-character alias behavior, invalid characters, protobuf conflict handling, and display output.
