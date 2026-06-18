# sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_validation.go

Purpose: Validates copy-source/destination paths and encryption headers for S3 copy operations.

Important APIs/types/functions: `CopyValidationError`, `ValidateCopyEncryption`, `validateSSECCopyRequirements`, `validateSSEKMSCopyRequirements`, `validateEncryptionCompatibility`, SSE-C header completeness helpers, `validateEncryptionContext`, `ValidateCopySource`, `validateCopySource`, `ValidateCopyDestination`, and `MapCopyValidationError`.

Control flow: encryption validation requires SSE-C copy-source headers when source metadata says SSE-C, forbids copy-source SSE-C headers for non-SSE-C sources, validates destination SSE-C completeness, checks KMS key format and context constraints, and rejects multiple destination encryption modes. Copy source validation rejects empty bucket/object/header, invalid bucket/object names, unsafe path segments via `IsValidObjectKey`, and invalid version IDs. Destination validation requires non-empty bucket/object.

State and persistence: pure validation; no state mutation or persistence.

Dependencies and integration: depends on S3 encryption header constants, S3 error codes, object key validators, KMS/version ID validators, and SSE metadata helpers. Copy handlers can map returned errors to S3 error codes with `MapCopyValidationError`.

Risks: `validateEncryptionContext` currently only checks non-empty despite comments about base64/JSON validation. KMS validation depends on `isValidKMSKeyID` elsewhere. Validation does not check that `copySource` string itself matches parsed bucket/object; callers must parse consistently.

Test signals: no direct tests in this subset. Security-sensitive path traversal and SSE-C/KMS combinations should have dedicated tests.
