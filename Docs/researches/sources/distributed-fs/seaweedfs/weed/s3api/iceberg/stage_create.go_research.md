# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/stage_create.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/stage_create.go

Purpose: support for Iceberg stage-create/deferred-create workflows. Stage-create writes metadata and a marker without registering the S3 Tables table until a later commit finalizes creation.

Important APIs: `stageCreateMarker` records table UUID, final location, staged metadata location, creation time, and expiry. Path helpers build marker namespace keys with URL-escaped Iceberg namespace encoding and place markers under `s3tables.TablesPath/<bucket>/.iceberg_staged/...`. `pruneExpiredStageCreateMarkers` lists marker files and removes expired ones. `loadLatestStageCreateMarker` finds the newest unexpired marker. `writeStageCreateMarker` prunes old markers, ensures marker directories, and writes a JSON marker file. `deleteStageCreateMarkers` removes all markers for a table. `isStageCreateEnabled` defaults to true and treats `0/false/no/off` as disabled.

State and persistence: staged metadata files are written elsewhere; this file persists marker JSON entries in the filer and deletes them after finalize/create. Dependencies include `filer_pb` streaming/list/create/remove APIs, UUIDs, URL/path encoding, `s3tables.TablesPath`, and 30-second timeouts. Integration points are `handleCreateTable` with `StageCreate` and `handleUpdateTable` create-on-commit. Risks: marker listing limit is 1024; stale staged metadata files may remain after marker expiry; path safety depends on route validation and escaped namespace keys. Tests cover only env flag behavior directly.
