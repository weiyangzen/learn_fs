# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peer.go

Purpose: Defines the overlay peer table name, typed peer model, and protobuf decoding/validation for peer records.

Important APIs and types: `OverlayPeerTable` is `overlay_peer_table`. `Peer` stores endpoint IP prefix, endpoint MAC, and tunnel endpoint IP. `UnmarshalPeerRecord` unmarshals `PeerRecord` bytes and parses/validates IP prefix, MAC, and VTEP address.

Control flow: any protobuf or semantic parse error is wrapped with field-specific context.

State and persistence: no state. Converts NetworkDB table bytes into typed peer data.

Dependencies and integration points: used by Linux and Windows overlay `EventNotify` handlers. Depends on gogo/protobuf and internal `hashable` types.

Risks: invalid remote data is rejected and logged by callers. String schema means validation is deferred to this boundary.

Test signals: no direct peer parsing tests in this subset.
