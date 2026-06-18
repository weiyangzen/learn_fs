## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils.go

Purpose: centralizes S3 Tables ARN parsing/building, filer path construction, internal metadata structs, tag validation, namespace/table/bucket validation, and version token generation.

Important APIs: `parseBucketNameFromARN`, `ParseBucketNameFromARN`, `parseTableFromARN`, `GetTableBucketPath`, `GetNamespacePath`, `GetTablePath`, `GetTableObjectRootDir`, `GetTableObjectBucketPath`, `IsTableBucketEntry`, `BuildBucketARN`, `BuildTableARN`, `ValidateTags`, `generateVersionToken`, `validateNamespace`, `ParseNamespace`, `validateTableName`, `ValidateTableName`, `flattenNamespace`, and `expandNamespace`.

Control flow: validation rejects malformed or reserved bucket names, namespace parts with path traversal, slashes, invalid characters, or `aws` prefix, and table names with invalid path/name characters. A single dotted namespace is split into multi-level parts and then flattened back to dot notation for internal paths and ARNs.

State and persistence: defines `tableBucketMetadata`, `namespaceMetadata`, and `tableMetadataInternal`, which are stored as filer extended attributes. Version tokens use 16 random bytes with timestamp fallback.

Risks: regex ARN parsing only supports the chosen namespace/table character set, tag validation is shared with normal S3 tags through `s3api/tags.go`, and dotted namespace normalization must stay consistent with client expectations. Namespace tests cover multi-level behavior and metadata properties.
