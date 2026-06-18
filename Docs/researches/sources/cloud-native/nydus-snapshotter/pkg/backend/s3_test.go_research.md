# sources/cloud-native/nydus-snapshotter/pkg/backend/s3_test.go

Purpose: tests S3 backend config parsing and checksum algorithm defaults/overrides.

Important APIs and functions: `Test_newS3Backend` calls `newS3Backend` with JSON configs and compares the resulting `S3Backend` struct using `reflect.DeepEqual`.

Control flow: the first case omits checksum and expects CRC32 with the configured endpoint, scheme, bucket, region, prefix, and credentials. The second sets `"checksum_algorithm": "SHA256"` and expects the AWS SDK SHA256 enum.

State and persistence: no remote S3 calls are made; tests inspect constructed state only.

Dependencies and integration points: imports AWS S3 checksum enum types and validates JSON tags on `S3Config`.

Risks and gaps: no negative cases for missing bucket/region or invalid checksum. No tests for default endpoint/scheme, `forcePush`, client construction, `HeadObject`, transfer manager upload, or object sizing.

Test signals: confirms the main positive config paths and checksum mapping.
