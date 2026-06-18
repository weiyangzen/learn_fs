# sources/distributed-fs/beegfs-protobuf/proto/beegfs.proto

**Purpose:** This proto defines shared BeeGFS identity and state vocabulary used by other service contracts. It is package `beegfs` with Go package `github.com/thinkparq/protobuf/go/beegfs`, and centralizes entity, node, target, quota, network, and capacity enums plus reusable entity identifier messages.

**Important APIs/types/functions:** Enums include `EntityType` (`NODE`, `TARGET`, `BUDDY_GROUP`, `POOL`), `NodeType` (`CLIENT`, `META`, `STORAGE`, `MANAGEMENT`), `ReachabilityState`, `ConsistencyState`, `CapacityPool`, `NicType`, `QuotaIdType`, and `QuotaType`, all with explicit unspecified zero values. `LegacyId` carries BeeGFS numeric ID plus `NodeType`. `EntityIdSet` can carry a globally unique `uid`, globally unique `alias`, and/or legacy numeric ID. Comments define request behavior where one identifier may be enough, while response behavior should return all known identifiers.

**Control flow:** This file has no executable flow; it is a schema dependency. Consumers choose one of the identifier forms when making requests, and management-style responders expand that to a fuller `EntityIdSet` when possible. The proto3 `optional` labels on `EntityIdSet` fields preserve explicit presence for `uid`, `alias`, and `legacy_id`.

**State and persistence behavior:** Persistent compatibility depends on the numeric enum values and field numbers. `0` is reserved as invalid/unspecified across enums and identifiers. `LegacyId.num_id` treats `0` as invalid by contract, but generated code does not enforce that. Alias syntax and uniqueness rules are documented, not enforced in the schema.

**Dependencies and integration points:** This file is imported by management proto/generated Go code and likely all other BeeGFS protobuf packages needing entity references or state enums. It is the common type layer for management inventory, target states, storage pools, quota filters, and NIC reporting.

**Risks:** Reusing generic enums across contexts can allow semantically invalid combinations unless service code validates them. `LegacyId` is not globally unique without entity type context, so APIs must not treat it as a universal identifier by itself. Changing enum numbers or field numbers would break wire compatibility. Alias validation must be implemented outside generated protobuf code.

**Test signals:** Schema tests should verify round-trip presence for `EntityIdSet` optionals, unknown enum tolerance, and cross-language serialization. API tests should cover lookup by `uid`, `alias`, and `legacy_id`, invalid zero IDs, mismatched node/entity types, and response expansion to full identifier sets.
