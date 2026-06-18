# sources/cloud-native/buildkit/util/apicaps/caps.go

## Purpose
Capability registry and negotiation helper for BuildKit APIs. CapList defines known capabilities; CapSet compares a remote APICap list against local definitions; CapError produces actionable unsupported/disabled messages.

## Important APIs, Types, And Functions
Package: `apicaps`. Build tags: `none`. Key declarations observed in the file: `PBCap, ExportedProduct, CapStatus, CapID, Cap, CapList, Init, All, CapSet, Supports, Contains, CapError, ...`.

## Control Flow, State, And Persistence
Init populates an in-memory map, All emits sorted protobuf state, CapSet indexes remote capabilities by ID, Supports checks definition existence, remote presence, and enabled state. No disk persistence.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/apicaps/pb, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are non-concurrent Init and message quality depending on ExportedProduct/SupportedHint. caps_test.go validates disabled-cap error behavior.
