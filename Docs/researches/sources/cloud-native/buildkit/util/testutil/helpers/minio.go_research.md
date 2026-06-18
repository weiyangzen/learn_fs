<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/minio.go -->
# sources/cloud-native/buildkit/util/testutil/helpers/minio.go

Purpose: starts a MinIO server and creates a bucket for S3-compatible integration tests.

Important APIs and types: `MinioOpts`, `NewMinioServer`, `waitMinio`, and `randomString`.

Control flow: verifies `minio` and `mc` binaries, chooses an ephemeral address, starts MinIO with root credentials, waits for live health endpoint, configures an `mc` alias, creates a random bucket with requested region, starts `mc admin trace`, and returns server address, bucket, and cleanup function.

State and persistence: creates temp server data, external processes, `mc` alias state, bucket, and trace process. Cleanup removes alias and stops processes via `MultiCloser`.

Dependencies and integration: depends on external MinIO tools and BuildKit integration sandbox command/log helpers.

Risks: same close-open port race as Azurite helper. Random string ignores `rand.Read` errors and maps bytes modulo alphabet length, which is fine for test identifiers but not cryptographic selection. External command availability controls test viability.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/minio.go -->
