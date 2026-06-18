# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.proto

Purpose: Defines the protobuf schema for overlay peer records exchanged through NetworkDB.

Important APIs and types: `PeerRecord` contains `endpoint_ip`, `endpoint_mac`, and `tunnel_endpoint_ip` fields with gogo custom names `EndpointIP`, `EndpointMAC`, and `TunnelEndpointIP`. File options enable gogo marshaler, unmarshaler, stringer, go-string, and sizer generation while disabling standard Go proto stringer.

Control flow: schema is declarative; `overlay.pb.go` is generated from it.

State and persistence: serialized records represent endpoint-to-VTEP mappings in the overlay peer table.

Dependencies and integration points: imported by generated Go code and used by Linux/Windows overlay join and event handling.

Risks: changing field numbers or meanings breaks NetworkDB compatibility. String fields require downstream parsing and validation.

Test signals: no direct proto tests; generated code and peer unmarshal code consume this schema.
