# sources/distributed-fs/seaweedfs/weed/s3api/s3api_list_normalization_test.go

## Purpose
Tests that list prefixes and object keys use consistent normalization, preventing mismatches when clients send leading slashes, duplicate slashes, or backslashes.

## Important APIs, Types, And Functions
`TestPrefixNormalizationInList` calls `s3_constants.NormalizeObjectKey` for table-driven prefixes. `TestListPrefixConsistency` checks that a normalized object key starts with a normalized list prefix. The local `startsWithPrefix` helper normalizes the prefix and handles the empty-prefix case.

## Control Flow
The first test verifies simple prefix preservation, leading slash stripping, duplicate slash cleanup, and backslash conversion to forward slash. The second test normalizes a representative parquet object key and asserts it matches a conventional prefix.

## State And Persistence
No state is persisted. The file is pure normalization logic.

## Dependencies And Integration Points
The tests depend on `weed/s3api/s3_constants.NormalizeObjectKey`, which is used by S3 write/list code to map external S3 keys onto filer paths.

## Risks And Test Signals
The tests catch regressions that would make objects written under one normalized form disappear from list results using another form. `startsWithPrefix` slices by prefix length without first checking length, so the test helper assumes the object key is at least as long as the prefix; adding shorter-key cases would need a safer helper.
