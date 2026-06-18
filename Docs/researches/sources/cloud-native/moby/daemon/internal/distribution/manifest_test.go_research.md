# sources/cloud-native/moby/daemon/internal/distribution/manifest_test.go

## Purpose
Validates manifest content-store caching, fallback to remote, ingest cleanup, and media-type detection.

## APIs, Control Flow, and Integration
`TestManifestStore` uses a local labeled content store and mock remote manifest getter. It covers no local/remote, remote fetch and cache, cached reuse without remote calls, digested refs, unknown media type with and without cache, writer/commit errors that should not block remote result, and no active ingest left behind. Detection tests cover mediaType precedence, OCI manifest/index inference, schema1 deprecation, and invalid field combinations.

## State, Dependencies, and Risks
State is temporary content store data and labels. Tests strongly document content-cache semantics, but they do not cover concurrent pulls or remote existence failures for canonical refs without matching source labels.
