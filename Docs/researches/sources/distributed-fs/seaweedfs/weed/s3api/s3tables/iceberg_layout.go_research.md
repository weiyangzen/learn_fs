## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout.go

Purpose: validates object paths written into table buckets so Iceberg tables only contain accepted metadata and data layouts.

Important APIs: `IcebergLayoutValidator.ValidateFilePath`, `validateDirectoryPath`, `validateFilePatterns`, `validateFile`, `IcebergLayoutError`, `TableBucketFileValidator`, and `ValidateTableBucketUpload`.

Control flow: `ValidateFilePath` strips a leading slash, requires a top-level `metadata` or `data` directory, permits explicit directory keys with trailing slash, then dispatches to metadata or data validation. Metadata is flat and accepts strict Iceberg names plus safe catch-alls for `.avro`, `.metadata.json`, `version-hint.text`, and `.stats`. Data paths allow partition/subdirectory segments and `.parquet`, `.orc`, or `.avro` files. `ValidateTableBucketUpload` ignores non-table-bucket paths, validates non-empty bucket/namespace/table segments, rejects double slashes, and validates the table-relative path.

State and dependencies: stateless regex-based validation using `path` and `strings`. It integrates with upload handling elsewhere to block invalid table bucket writes.

Risks: the catch-all metadata patterns are intentionally permissive for engine compatibility; they rely on safe-character and suffix limits to avoid accepting arbitrary metadata junk. Tests cover real Flink/Spark/Trino names and clearly bad metadata names.
