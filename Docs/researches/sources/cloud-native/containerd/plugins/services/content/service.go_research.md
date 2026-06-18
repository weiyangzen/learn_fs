# sources/cloud-native/containerd/plugins/services/content/service.go

## Purpose
Registers the gRPC content service plugin.

## Important APIs, Types, And Functions
`init` registers gRPC plugin ID `content`; init loads the content service plugin and wraps it with `contentserver.New`.

## Control Flow
During startup, the plugin retrieves `services.ContentService`, asserts it is a content store, constructs the gRPC server, and returns it for registration by the main gRPC server.

## State And Persistence
No state here; persistence is in the underlying content store.

## Dependencies And Integration Points
Requires service plugin and integrates with `contentserver` and gRPC server registration.

## Risks
Type assertion assumes the service plugin returns `content.Store`.

## Test Signals
No direct tests.
