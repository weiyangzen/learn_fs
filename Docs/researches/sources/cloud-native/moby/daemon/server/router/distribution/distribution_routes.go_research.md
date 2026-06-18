# sources/cloud-native/moby/daemon/server/router/distribution/distribution_routes.go

## Purpose
`distribution_routes.go` implements `GET /distribution/{name}/json`, returning manifest descriptor and platform information from registries.

## Important APIs, Types, And Functions
`getDistributionInfo` parses the reference, decodes `X-Registry-Auth`, asks the backend for repositories, and tries each repository. `fetchManifest` resolves tags to descriptors, fetches manifests, rejects schema1, and extracts platform data from manifest lists or schema2 configs.

## Control Flow
The handler normalizes the image reference and rejects full image IDs or unparseable references as invalid. It iterates repositories in backend order, preserving the last manifest error for fallback. `fetchManifest` gets tag descriptors when the reference is not canonical, obtains the manifest service, fetches by digest, corrects media type/size from payload data, and fills platform arrays.

## State And Persistence
No local state is persisted. It performs remote registry reads only.

## Dependencies And Integration Points
Depends on Docker distribution repositories, manifest list/schema2 packages, Moby distribution media-type helpers, registry auth decoding, `errdefs`, and OCI platform descriptors.

## Risks
Registry endpoints can return inconsistent descriptors or media types, so the code corrects descriptor fields from payloads. It ignores invalid auth headers for compatibility. Schema1 rejection and tag-versus-digest handling are important compatibility/security boundaries.

## Test Signals
No direct tests in this file; registry/distribution integration tests should cover tag lookup, digest lookup, auth, manifest list platforms, schema2 config platform extraction, and schema1 rejection.
