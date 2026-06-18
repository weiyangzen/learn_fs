# sources/cloud-native/buildkit/source/containerblob/source.go

## Purpose
This file registers the container blob source for docker-image blob and OCI-layout blob schemes. It parses frontend attributes into `ImageBlobIdentifier` values and resolves them into `puller` source instances.

## Important APIs
`SourceOpt` carries the content store, cache accessor, and registry host resolver config. `NewSource` constructs `Source`. `Schemes` returns supported blob schemes. `Identifier` dispatches by scheme. `Resolve` type-checks identifiers and returns a `puller`. `registryIdentifier`, `ociLayoutIdentifier`, `parseIdentifierAttrs`, and `parseImageRecordType` handle attributes.

## Control Flow
`Identifier` chooses registry or OCI path. Both create a base `ImageBlobIdentifier`; OCI additionally requires `StoreID`. `parseIdentifierAttrs` accepts HTTP-style filename/permission/UID/GID attributes, image usage record type, and OCI session/store IDs only when allowed. Unknown attributes are ignored.

## State and Persistence
`Source` is a thin holder for content/cache/registry dependencies. Identifier attributes become state on the puller and affect cache keys and file materialization. No content is persisted until `puller.Snapshot`.

## Dependencies and Integration Points
It integrates with BuildKit source registry interfaces, solver sessions, protobuf attribute constants, cache/content backends, Docker registry hosts, and safe filename utilities.

## Risks
Unknown attributes being ignored can hide frontend typos. Numeric attributes are parsed as base-0 integers, so octal-style values are accepted. OCI store/session attributes are ignored for registry blobs by design. Invalid record types and missing OCI store IDs fail early.

## Test Signals
No direct tests in this subset. The attribute parser mirrors container image source parsing, and integration tests should cover the resulting snapshot and usage record behavior.
