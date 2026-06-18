# sources/cloud-native/buildkit/client/solve.go

## Purpose
This is the main BuildKit client solve implementation. It validates solve inputs, prepares session file sync and content-store attachments, builds control API solve requests, streams status updates, manages cache import/export metadata, updates local OCI indexes after exports, and supports local cache reset by deleting unreferenced blobs.

## Important APIs, Types, and Functions
- `SolveOpt` is the high-level solve configuration: exporters, frontend attrs/inputs, local mounts, cache import/export, sessions, entitlements, source policy, proxy network, compatibility version, and reference override.
- `ExportEntry` describes each output exporter and local file/dir/content-store target.
- `CacheOptionsEntry` describes cache import/export entries.
- `Client.Solve` validates frontend/definition exclusivity and delegates to `solve`.
- `solve` coordinates sessions, exports, status streaming, control API invocation, cache index updates, image output index updates, and cache reset.
- `prepareSyncedFiles` filters local mount filesystems and resets UID/GID to zero for sync providers.
- `parseCacheOptions` converts client cache options to control API options, opens local content stores, resolves local import tags through `ociindex`, and prepares frontend attrs for frontend/gateway cache imports.
- `resetCacheStore` walks descriptors referenced by `index.json` and deletes content-store blobs that are not reachable.

## Control Flow
`Solve` rejects empty definitions and invalid frontend+definition combinations. `solve` prepares local mounts, creates or uses a session, parses cache options, registers file-sync providers, session attachables, content stores, export targets, source policy providers, and starts the session unless preinitialized. It merges cache-import frontend attrs, then runs concurrent goroutines for the control `Solve` RPC, optional gateway callback, and status stream. After all goroutines complete, it updates local cache `index.json` entries from `cache.manifest`, updates local image output stores from exported image descriptors and names, and resets requested local cache stores.

## State and Persistence Behavior
Local persistent state includes output directories, OCI content stores, `oci-layout`, `index.json`, and cache blobs. Session state is transient and scoped to the solve unless `SharedSession` or `SessionPreInitialized` is used. Status streaming uses a separate background context and an inactivity timeout so status RPCs terminate after solve completion. Cache reset preserves all blobs reachable from index manifests and removes unreferenced blobs best-effort, logging delete failures rather than failing the solve.

## Dependencies and Integration Points
This file integrates with the BuildKit control API, LLB definitions, session transport, file sync, session content providers, local containerd content stores, OCI index helper, exporter response keys, source policy protobufs, OpenTelemetry trace propagation, and containerd image traversal. It is the central adapter between user-facing client options and daemon-side solver/exporter behavior.

## Risks and Edge Cases
Important guarded risks include invalid frontend/definition combinations, duplicate OCI store keys, unsupported output target combinations, missing output writers/directories, local cache imports with missing stores or missing tag digests, status goroutine leaks, gateway callback errors racing solve completion, `res` being nil if solve succeeds unexpectedly without a response, local index corruption from failed writes, and cache reset accidentally deleting reachable blobs if descriptor traversal misses a media type.

## Test Signals
`solve_resetcache_test.go` directly covers `resetCacheStore`. `ociindex_test.go` covers the index helper used here. The broader client integration suite, including merge/diff, policy, validation, and compatibility tests, exercises exporter validation, status streaming, local outputs, cache import/export, session providers, and provenance options.
