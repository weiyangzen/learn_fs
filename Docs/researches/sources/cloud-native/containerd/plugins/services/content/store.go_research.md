# sources/cloud-native/containerd/plugins/services/content/store.go

## Purpose
Registers the local content service backed by metadata DB.

## Important APIs, Types, And Functions
`init` registers `services.ContentService` and returns `metadata.DB.ContentStore()`.

## Control Flow
Startup retrieves the metadata plugin and exposes its content store as a service plugin.

## State And Persistence
Content blob metadata and labels are managed by metadata DB; blob storage is through the underlying content store attached to metadata.

## Dependencies And Integration Points
Requires metadata plugin. Used by content gRPC service and other in-memory clients.

## Risks
The plugin is a thin type assertion wrapper; metadata plugin availability and correctness are prerequisites.

## Test Signals
No direct tests.
