# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_helpers.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_helpers.go

Purpose: helper types and functions for Iceberg REST table commits, especially create-on-commit flows where a commit with `assert-create` finalizes a staged or implicit table creation.

Important APIs: `icebergRequestError` normalizes HTTP/error-type responses. `createOnCommitInput` carries bucket ARN, marker bucket, namespace, table name, identity, location, UUID, base metadata/version, updates, and statistics updates. Error classifiers `isS3TablesConflict`, `isS3TablesNotFound`, and `isS3TablesAlreadyExists` translate S3 Tables manager errors and string fallbacks. `hasAssertCreateRequirement` detects Iceberg `assert-create`. `finalizeCreateOnCommit` applies table updates to a metadata builder, serializes metadata, applies statistics updates, runs metadata spec compliance fixups, saves a new metadata file, creates the S3 Tables row, cleans up on failure, and removes stage-create markers on success.

State and persistence: writes `vN.metadata.json` through `saveMetadataFile`, persists catalog state through `s.tablesManager.Execute("CreateTable")`, and deletes files/markers on failure or completion. Dependencies include `iceberg-go/table`, `s3tables`, `filer_pb`, UUIDs, JSON, and glog. Integration point is `handleUpdateTable` when no existing table is found. Risks: partial failure can leave metadata files or markers; string-based error detection is compatibility-oriented but imprecise; metadata location/version must stay aligned with S3 Tables version state.
