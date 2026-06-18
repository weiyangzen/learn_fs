## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.pb.go

Purpose: generated gogo/protobuf Go implementation for `networkdb.proto`, defining the wire-level gossip payloads used by Docker/libnetwork NetworkDB. It is not handwritten business logic, but it is the compiled serialization contract consumed by the gossip delegate, bulk sync, push/pull, node membership, and table event code.

Important APIs/types/functions: `MessageType` enumerates `NETWORK_EVENT`, `TABLE_EVENT`, `PUSH_PULL`, `BULK_SYNC`, `COMPOUND`, and `NODE_EVENT`; nested enum types model node/network/table event operations; structs include `GossipMessage`, `NodeEvent`, `NetworkEvent`, `NetworkEntry`, `NetworkPushPull`, `TableEvent`, `BulkSyncMessage`, `CompoundMessage`, and `CompoundMessage_SimpleMessage`. The generated methods provide `Reset`, `ProtoMessage`, `Descriptor`, `XXX_Marshal`, `XXX_Unmarshal`, getters, `GoString`, `String`, `Marshal`, `MarshalToSizedBuffer`, `Size`, and `Unmarshal`.

Control flow: callers normally construct typed payloads, marshal them through the generated `Marshal` paths, wrap them in a `GossipMessage`, and decode by message type on receive. `CompoundMessage` carries multiple already-encoded simple payloads to reduce gossip transmission overhead. Unmarshal methods parse protobuf wire fields, skip unknown fields through `skipNetworkdb`, and reject malformed length/varint/EOF cases.

State and persistence behavior: the file owns no durable state; it only serializes transient Lamport-clocked state snapshots and mutations. Persistence semantics are defined by higher-level NetworkDB maps and reaping logic, while this code preserves fields such as `LTime`, `Leaving`, `ResidualReapTime`, `Networks`, and `Payload` across peer communication.

Dependencies and integration points: imports `github.com/gogo/protobuf/proto`, `github.com/gogo/protobuf/sortkeys`, and `github.com/hashicorp/serf/serf` for Lamport time custom types. It is generated from `networkdb.proto`, so edits should happen in the proto and generator flow rather than directly here.

Risks: schema compatibility is the main risk. Field numbers and custom names must remain stable or older daemons may misinterpret cluster state. Generated code also contains hand-unfriendly large marshal/unmarshal loops, so direct modifications are fragile. Unknown fields are skipped, which helps forward compatibility but cannot repair semantic mismatches.

Test signals: direct tests are not in this file, but `networkdb_test.go`, `tableevent_test.go`, and the slow property test exercise these generated message types through real gossip encoding, compound message paths, bulk sync payloads, out-of-order table events, and cluster convergence.
