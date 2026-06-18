# sources/cloud-native/containerd/plugins/services/namespaces/local.go

## Purpose
`local.go` implements the local namespaces service plugin. It exposes the namespaces API client directly against the metadata database, with event publication for create, update, and delete operations.

## Important APIs, Types, And Functions
The registered service plugin has ID `services.NamespacesService` and requires the metadata and event plugins. The `local` type stores a `*metadata.DB` and an `events.Publisher` and implements `api.NamespacesClient`. Main methods are `Get`, `List`, `Create`, `Update`, `Delete`, plus transaction helpers `withStore`, `withStoreView`, and `withStoreUpdate`.

## Control Flow
Reads run inside `metadata.DB.View` and writes inside `metadata.DB.Update`, each wrapping a `metadata.NewNamespaceStore(tx)`. `Create` stores the namespace and labels, then publishes `/namespaces/create` with the namespace placed in context. `Update` either applies field-mask paths under `labels.` or replaces all labels, then publishes `/namespaces/update`. `Delete` removes the namespace and publishes `/namespaces/delete`.

## State And Persistence
Namespace names and labels persist in the shared Bolt-backed metadata database. Events are transient but important for subscribers. Label deletion is represented by setting an empty string through the namespace store contract.

## Dependencies And Integration Points
This file integrates the plugin registry, metadata namespace store, containerd events, protobuf namespace service types, and `errgrpc` conversion. It is consumed by the gRPC wrapper in `service.go`.

## Risks
The code assumes `req.Namespace` is non-nil in `Create` and `Update`; malformed direct client calls can panic before validation. `Update` only accepts label field paths and rejects all other field-mask paths. Event publication happens after the DB transaction, so a publish failure returns an error even though the metadata change already committed.

## Test Signals
No direct tests are in this subset. Coverage is expected through namespace service integration tests elsewhere and event subscriber behavior.
