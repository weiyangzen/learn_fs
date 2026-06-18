# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_create_table_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_create_table_test.go

Purpose: small tests for table creation request validation and the stage-create feature flag.

Important tests: `TestValidateCreateTableRequestRequiresName` checks an empty `CreateTableRequest` returns `errTableNameRequired`; `TestValidateCreateTableRequestAcceptsWithName` accepts a named request. `TestIsStageCreateEnabledDefaultsToTrue` verifies an unset `ICEBERG_ENABLE_STAGE_CREATE` defaults to enabled. `TestIsStageCreateEnabledFalseValues` checks false-like values `0`, `false`, `FALSE`, `no`, and `off`.

State and dependencies: tests use `t.Setenv` for environment isolation and plain error comparison. Integration points are `handleCreateTable` stage-create handling and request validation before metadata writes. Risks covered are accidental rejection of default stage-create workflows or accepting empty table names. Test signal is narrow but protects high-level branch conditions.
