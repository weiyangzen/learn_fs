# sources/cloud-native/moby/daemon/server/router/image/backend.go

## Purpose
`backend.go` defines the image router's backend interfaces for image CRUD, import/export, registry push/pull, attestations, prune, and search.

## Important APIs, Types, And Functions
`Backend` embeds `imageBackend`, `importExportBackend`, and `registryBackend`. Methods include `ImageDelete`, `ImageHistory`, `Images`, `GetImage`, `ImageInspect`, `ImageAttestations`, `TagImage`, `ImagePrune`, `LoadImage`, `ImportImage`, `ExportImage`, `PullImage`, and `PushImage`. `Searcher` exposes registry search.

## Control Flow
Router handlers parse HTTP inputs into option structs from `imagebackend` and call these methods. Streaming operations pass writer streams into backend methods for JSON progress.

## State And Persistence
The interface abstracts persistent image store and registry side effects: pulls, imports, loads, tags, deletes, pushes, and prune operations.

## Dependencies And Integration Points
Uses API image/registry types, daemon filters, internal image IDs, distribution references, OCI platforms, and `imagebackend` option structs.

## Risks
Because this is a broad interface, route changes can require daemon image service changes. Platform, manifest, and identity options have API-version gates in the router but must be honored by backends.

## Test Signals
Compilation against daemon image service plus image API integration tests validate the contract.
