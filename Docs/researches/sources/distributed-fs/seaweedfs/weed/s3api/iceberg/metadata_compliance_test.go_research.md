# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance_test.go

Purpose: test suite for `ensureMetadataSpecCompliance`.

Important tests: `TestEnsureMetadataSpecCompliance_BackfillsMissingFields` mirrors fresh `iceberg-go` output and checks all sentinels. `PreservesExistingFields` ensures real snapshot state is not overwritten. `ReplacesExplicitNullsWithSentinels` handles nulls. `InvalidJSONReturnedUnchanged`, `EmptyInputReturnedUnchanged`, and top-level `null` protect pass-through behavior. `PreservesOriginalKeyOrder` asserts byte-for-byte append order for compact JSON. `EmptyObjectBackfilled` checks no leading comma. `AllPresentReturnsSameBytes` requires exact no-op output when all fields exist.

State and dependencies: pure JSON byte slices and maps. Integration points are all metadata persistence/response paths that call the compliance helper. Risks covered include strict-client parse failures, accidental metadata corruption, and nondeterministic output that could surprise tests or clients. Test signal is strong for edge cases and byte-level behavior.
