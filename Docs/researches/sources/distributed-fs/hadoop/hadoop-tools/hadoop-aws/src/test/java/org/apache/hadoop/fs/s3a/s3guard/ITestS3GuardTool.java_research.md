# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/ITestS3GuardTool.java

Purpose: integration tests for S3Guard CLI bucket-info and multipart-upload commands against real S3A stores and public/external bucket configuration.

Important APIs/types/functions: extends `AbstractS3GuardToolTestBase`; uses `BucketInfo`, `Uploads`, `MultipartTestUtils` helpers (`createPartUpload`, `countUploadsAt`, `clearAnyUploads`, `assertNoUploadsAt`), public dataset utilities, and command output parsing through `Csvout`-style fields.

Control flow: encryption tests run bucket-info against an external bucket, expecting success for no encryption and `E_BAD_STATE` for AES256. Store-info tests run normal and FIPS bucket probes. Upload tests clear stale uploads, create one MPU part, assert API and CLI listing counts, delete via CLI, and recheck. Age tests verify `-seconds` filtering before and after sleeping. Negative expect verifies `Uploads -expect` failure for a missing path.

State and persistence: creates and aborts real multipart uploads under method paths; cleans uploads on failure. External-bucket tests may remove bucket overrides when default public dataset is used.

Dependencies/integration: live multipart upload capability, S3A configuration, FIPS capability, S3GuardTool command output, and public dataset configuration.

Risks: relies on external bucket availability and multipart support; age checks are timing-sensitive; command-output parsing assumes four whitespace fields on `TOTAL` lines.

Test signals: command exit codes, upload counts via API and CLI, deletion counts, aged listing/deletion behavior, and FIPS skip behavior.
