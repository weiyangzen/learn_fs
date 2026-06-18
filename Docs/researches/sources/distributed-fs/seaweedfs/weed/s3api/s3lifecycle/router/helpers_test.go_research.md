# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/helpers_test.go

Purpose: direct coverage for router helper functions and engine snapshot accessor behavior that larger route tests exercise indirectly.

Important tests: `successorModTimeFromContainer` handles missing/empty/non-numeric/non-positive values and positive seconds. `logicalKeyFromVersionPath`, `isVersionsContainerKey`, and `isVersionFolderPath` classify `.versions` paths. `isDeleteMarkerEntry` only accepts literal `"true"`. `extractTags` extracts only object-tagging-prefixed extended keys and returns nil when none. `hasActiveEventDrivenAction` requires the specific kind to be active and mode event-driven, skipping scan-only and nil actions. Snapshot accessor cross-checks cover bucket versioned flags, bucket action keys, unknown action nil, all actions covering kinds, and monotonic snapshot ids.

Control flow/state: tests combine pure helpers with compiled engine snapshots. They model version path strings, filer extended metadata, and prior state modes.

Dependencies/integration: imports router package internals, filer protobufs, S3 constants, lifecycle types, and engine compile APIs. These helpers support route classification for version folders, delete markers, tag filters, and event-driven eligibility.

Risks: path classification must reject bucket-root `.versions` and malformed version paths to avoid treating infrastructure folders as objects. Literal delete-marker parsing avoids truthy ambiguity. Snapshot helper tests overlap engine tests but document router-facing expectations.

Test signals: strong edge-case signal for version path parsing, tag extraction, active-action checks, and snapshot accessor contracts used by router code.
