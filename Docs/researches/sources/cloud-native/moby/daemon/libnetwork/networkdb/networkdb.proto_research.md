## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.proto

Purpose: authoritative protobuf schema for NetworkDB gossip messages. It defines the versioned data model for node membership events, network membership events, table CRUD events, network push/pull sync, bulk sync, and compound message batching.

Important APIs/types/functions: `MessageType` tags envelope payload classes; `GossipMessage` is the envelope with `type` and raw `data`; `NodeEvent`, `NetworkEvent`, and `TableEvent` each carry event `type`, Lamport time, originating node, and domain-specific identifiers; `NetworkEntry` and `NetworkPushPull` represent membership snapshots; `BulkSyncMessage` carries whole-state payloads; `CompoundMessage.SimpleMessage` batches encoded payloads.

Control flow: sender code chooses a `MessageType`, marshals the matching message body, wraps it, and disseminates it through memberlist. Receivers decode the envelope, dispatch by enum, and apply Lamport ordering and ownership rules in NetworkDB. Bulk and push/pull messages provide state reconciliation outside individual event flow.

State and persistence behavior: this schema expresses state-transfer payloads rather than storing state. Lamport times are central to ordering; `leaving` distinguishes active and leaving network attachments; `residual_reap_time` communicates tombstone lifetime for table deletes during sync.

Dependencies and integration points: uses gogo/protobuf options for generated marshaler/unmarshaler/stringer/sizer code and custom Go names such as `NetworkID`. The Lamport fields use `github.com/hashicorp/serf/serf.LamportTime`, binding the schema to NetworkDB's Serf/memberlist clock model.

Risks: protobuf field numbers are compatibility-sensitive. The schema uses byte payloads for envelope and bulk sync data, so type safety depends on correct `MessageType` dispatch. Typos or semantic ambiguity in comments, such as delete text saying "updated", can mislead maintainers even if the wire format is unaffected.

Test signals: the schema is indirectly exercised by all NetworkDB cluster tests and table-event tests via generated code. There are no standalone proto compatibility tests in this subset, so regression safety comes from integration behavior rather than golden wire fixtures.
