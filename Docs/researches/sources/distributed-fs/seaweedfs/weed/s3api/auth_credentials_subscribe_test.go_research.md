# sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe_test.go

Purpose: Tests IAM metadata change handling and provides shared memory-IAM helpers for related tests.

Important APIs, types, and functions: `TestOnIamConfigChangeLegacyIdentityDeletionReloadsConfiguration`, `TestOnIamConfigChangeReloadsOnIamIdentityDirectoryChanges`, `newTestS3ApiServerWithMemoryIAM`, and `hasIdentity`.

Control flow and state: The legacy deletion test simulates deletion of `/etc/iam/identity.json` and expects a full reload from the credential manager so migrated identities remain available. The identity-directory test seeds config, creates `alice` in the credential manager, simulates a new identity JSON event, and expects the in-memory IAM index to include Alice.

State and persistence behavior: Uses a memory credential manager as durable backing for the tests, then initializes a minimal `IdentityAccessManagement` with maps, locks, and `ReplaceS3ApiConfiguration`.

Dependencies and integration points: Depends on `weed/credential`, memory credential store registration, filer IAM constants, `filer_pb.Entry`, and `iam_pb.S3ApiConfiguration`.

Risks and test signals: Protects live-reload behavior during migration from legacy single-file IAM config to multi-file stores. The helper creates only the IAM fields needed by these tests, so future production code that assumes additional initialized fields may need helper updates.
