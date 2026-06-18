# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_updates.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_updates.go

Purpose: parses Iceberg REST commit updates while compensating for `iceberg-go` versions that do not yet decode `set-statistics` and `remove-statistics` update actions.

Important APIs: `statisticsUpdate` stores either a `table.StatisticsFile` upsert or snapshot-id removal. `ErrIncompleteSetStatistics` rejects incomplete legacy-form `set-statistics`. `setStatisticsUpdate.asStatisticsFile` accepts either nested `statistics` or flattened required fields, ensuring `BlobMetadata` is non-nil. `parseCommitUpdates` separates statistics updates from regular `table.Updates` by reading raw JSON action names and unmarshalling only non-statistics actions through iceberg-go. `applyStatisticsUpdates` unmarshals metadata JSON into a map, indexes existing statistics by snapshot id while preserving order, applies set/remove changes, deletes the key when empty, and remarshal the object.

State and persistence: functions are pure over JSON bytes, but their output is later persisted in metadata files and S3 Tables `FullMetadata`. Dependencies are `encoding/json` and `iceberg-go/table`. Integration points are both regular commit and create-on-commit. Risks: map remarshal in `applyStatisticsUpdates` can reorder top-level metadata keys; duplicate snapshot IDs collapse to the last value; schema drift in Iceberg statistics JSON can break parsing. Tests cover separation, incomplete updates, upsert/remove behavior, and conflict classification.
