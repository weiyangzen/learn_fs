## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout_test.go

Purpose: pins Iceberg layout compatibility and regression behavior for metadata and data filename validation.

Important tests: `TestIcebergLayoutValidator_AcceptsRealWorldManifestNames`, `TestIcebergLayoutValidator_RejectsClearlyBadMetadataNames`, and `TestIcebergLayoutValidator_AcceptsRealWorldDataFiles`.

Control flow: each test creates a fresh `IcebergLayoutValidator`, iterates table-driven cases, and asserts acceptance or rejection from `ValidateFilePath`.

State and dependencies: no persistent state; depends only on the validator in `iceberg_layout.go` and Go `testing`.

Signals and risks: the tests document why the metadata regex set includes catch-all safe names: strict UUID/snapshot-only patterns rejected manifests from real writers such as Flink. Negative cases ensure random extensions, metadata subdirectories, bad top-level directories, and deceptive suffixes still fail. Coverage does not directly test `ValidateTableBucketUpload` full filer path parsing.
