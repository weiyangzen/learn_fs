# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance.go

Purpose: fixes Iceberg metadata JSON emitted by `iceberg-go` so strict clients can parse empty-table metadata. Some required keys are omitted or null when empty; this helper backfills sentinel values.

Important APIs: `specRequiredEmptyOrder` and `specRequiredEmptyDefaults` define required keys: `current-snapshot-id=-1`, `snapshots=[]`, `snapshot-log=[]`, `metadata-log=[]`, and `refs={}`. `isJSONNull` detects explicit null. `ensureMetadataSpecCompliance` unmarshals the top-level object, returns invalid/empty/top-level-null input unchanged, appends missing keys without reordering existing JSON when no nulls exist, and remarshal only when replacing explicit nulls. `appendMissingObjectKeys` splices defaults before the final `}`.

State and persistence: pure byte transformation, but applied before metadata files and S3 Tables `FullMetadata` are persisted and before REST responses are serialized. Dependencies are `bytes` and `encoding/json`. Integration points are create-table, commit, create-on-commit, `LoadTableResult.MarshalJSON`, and `CommitTableResponse.MarshalJSON`. Risks: byte-level splicing assumes a valid top-level object; null replacement uses map remarshal and can reorder keys; future Iceberg spec-required fields must be added here. Tests are extensive for missing fields, existing fields, nulls, invalid input, order preservation, empty object, and no-op behavior.
