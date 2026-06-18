<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/doc.go -->
# sources/cloud-native/containerd/api/services/ttrpc/events/v1/doc.go

## Purpose
Package documentation and compatibility aliases for the ttrpc events API.

## Important APIs and Types
Declares package `events` and imports `github.com/containerd/containerd/api/types`. It defines deprecated type alias `Envelope = types.Envelope`, preserving older package users while directing them to `types.Envelope`.

## Control Flow
No executable flow beyond compile-time aliasing.

## State and Persistence
No state is stored. Event state is represented by `types.Envelope` in generated protobuf messages.

## Dependencies and Integration Points
Integrates with older event-forwarding code that referenced `events.Envelope`, while the canonical type lives in `api/types/event.proto`.

## Risks
Removing the alias could break downstream consumers. Keeping it may hide migrations, but the deprecation notice makes the canonical path clear.

## Test Signals
Package compile tests and downstream compatibility checks that `events.Envelope` remains assignable to `types.Envelope` are enough.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/doc.go -->
