# sources/cloud-native/containerd/plugins/services/containers/local.go

## Purpose
Registers and implements the local containers service client backed by metadata DB and event publishing.

## Important APIs, Types, And Functions
`local` embeds `containers.Store` and implements `api.ContainersClient`. Methods include `Get`, `List`, `ListStream`, `Create`, `Update`, `Delete`, and transaction helpers. `localStream` implements the client streaming interface for in-memory listing.

## Control Flow
Startup obtains metadata DB and event publisher, creates a metadata container store, and returns `local`. Read methods run in DB view transactions; create/update/delete run in update transactions, convert proto/core types, then publish container events after successful mutation. `ListStream` materializes all results into an in-memory stream.

## State And Persistence
Container metadata is persisted in metadata DB. Events are published through the in-memory event exchange after mutations.

## Dependencies And Integration Points
Requires event and metadata plugins. Integrates with metadata transactions, containers store, protobuf helpers, errgrpc conversion, and event types.

## Risks
Events are emitted after DB commit; event publish failures return errors even after metadata changes. `ListStream` buffers all containers rather than streaming from the DB cursor. Update requires non-empty container ID.

## Test Signals
No direct tests in this subset.
