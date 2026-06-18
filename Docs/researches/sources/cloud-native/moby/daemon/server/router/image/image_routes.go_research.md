# sources/cloud-native/moby/daemon/server/router/image/image_routes.go

## Purpose
`image_routes.go` implements the image API HTTP handlers, including pull/import, push, save/load, delete, inspect, list, history, tag, search, prune, and attestations.

## Important APIs, Types, And Functions
Key handlers include `postImagesCreate`, `postImagesPush`, `getImagesGet`, `postImagesLoad`, `deleteImages`, `getImagesByName`, `getImagesJSON`, `getImagesHistory`, `postImagesTag`, `getImagesSearch`, `postImagesPrune`, and `getImageAttestations`. Helper types include `missingImageError`; `validateRepoName` rejects `scratch`.

## Control Flow
Handlers parse forms/JSON, decode platforms based on API version, decode registry auth permissively, convert references with distribution/reference helpers, and delegate to backend methods. Streaming handlers use `ioutils.WriteFlusher` and write JSON progress/errors once output has begun. Inspect/list handlers perform extensive API-version shaping: legacy `VirtualSize`, descriptor removal, container count compatibility, legacy config fields, graph-driver restoration, and manifest/identity constraints.

## State And Persistence
Persistent state changes occur in the backend: pulling, importing, loading, deleting, tagging, pruning, and pushing images. The router mutates only request option structs and response payloads.

## Dependencies And Integration Points
Integrates authconfig, registry search, remote context downloads, stream formatters, filters, platform parsing, digest/tag references, `imagebackend` options, and API compatibility wrappers.

## Risks
Most risks are wire-compatibility and streaming-error related. Platform support is version-gated across multiple endpoints, `identity` requires `manifests`, `manifests` conflicts with `platform`, invalid auth is intentionally ignored, and errors after progress flush must be emitted as stream entries rather than normal HTTP errors.

## Test Signals
Local tests cover `VirtualSize` and legacy inspect config fields. Broader image API integration tests should cover reference parsing, reserved names, platform gates, streaming pull/push/load/save, and attestations.
