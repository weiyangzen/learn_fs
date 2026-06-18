# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.pb.go

Purpose: Generated gogo/protobuf Go code for the overlay `PeerRecord` message used in NetworkDB peer table entries.

Important APIs and types: `PeerRecord` has `EndpointIP`, `EndpointMAC`, and `TunnelEndpointIP` string fields. Generated methods include proto reset/descriptor, getters, marshal/unmarshal, size, string/go-string, skip logic, and overflow/length errors.

Control flow: marshal writes non-empty string fields in reverse buffer order; unmarshal parses length-delimited fields 1-3 and skips unknown fields.

State and persistence: no runtime state. Serialized bytes are stored/transmitted through libnetwork's NetworkDB table entries.

Dependencies and integration points: produced from `overlay.proto` with gogofaster; used by Linux and Windows overlay join/event paths and `peer.go` parsing.

Risks: generated file should not be hand-edited. Schema changes require regenerating and preserving wire compatibility. Fields are strings, so semantic validation happens outside generated code.

Test signals: peer record use is indirectly exercised by join/event code; no direct generated-code tests.
