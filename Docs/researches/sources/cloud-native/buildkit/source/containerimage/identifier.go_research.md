# sources/cloud-native/buildkit/source/containerimage/identifier.go

## Purpose
This file defines source identifiers for registry images and client-side OCI layout images. Identifiers store parsed references, platform constraints, resolve mode, record type, layer limit, checksum, and OCI layout session/store data.

## Important APIs and Types
`ImageIdentifier` is used for `docker-image://` style sources. `NewImageIdentifier` parses and requires a reference object. `Scheme` returns `DockerImageScheme`, and `Capture` records image provenance. `OCIIdentifier` is the analogous local OCI-layout identifier with session/store fields; its `Scheme` returns `OCIScheme`, and `Capture` records the image as local provenance.

## Control Flow
Both constructors parse containerd references and reject missing objects. Both `Capture` methods parse the pinned digest and call `provenance.Capture.AddImage`, including platform and digest. OCI capture sets `Local: true`.

## State and Persistence
Identifiers are per-source state. They do not persist content but drive resolver selection, cache-key calculation, layer limiting, and provenance capture in `source.go` and `pull.go`.

## Dependencies and Integration Points
Dependencies include containerd reference parsing, BuildKit provenance types, source scheme constants, resolver mode, client usage record types, OCI platform/digest types, and solver frontend attributes parsed elsewhere.

## Risks
Constructors require a reference object, which means callers must provide tag or digest-qualified refs according to containerd parser expectations. Capture validates only the pin digest string, not that it equals the original reference digest; resolution code is responsible for final digest behavior.

## Test Signals
No direct tests in this subset. Identifier behavior is normally exercised through source identifier parsing tests and provenance capture tests elsewhere.
