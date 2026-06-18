# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_retention.go

Purpose: this file implements S3 Object Lock retention get/put handlers. It is a thin HTTP layer over object-lock availability checks, XML parsing/validation, governance bypass evaluation, and lower-level retention metadata update/read functions.

Important APIs/types/functions: `PutObjectRetentionHandler` parses and writes retention, while `GetObjectRetentionHandler` reads retention. Both use `s3_constants.GetBucketAndObject`, `handleObjectLockAvailabilityCheck`, query `versionId`, `evaluateGovernanceBypassRequest`, `parseObjectRetention`, `ValidateRetention`, `setObjectRetention`, `getObjectRetention`, `mapValidationErrorToS3Error`, and stats collection.

Control flow: PUT verifies object lock availability for the bucket, reads optional version ID, determines whether governance bypass is allowed, parses XML retention from the request body, validates mode and retain-until values, then calls `setObjectRetention`. Not-found variants map to `NoSuchKey`; active compliance/governance protection maps to access denied; success sets `x-amz-version-id` when provided and returns HTTP 200. GET performs the same availability/version lookup, calls `getObjectRetention`, maps missing object/version to `NoSuchKey`, missing retention config to `ObjectLockConfigurationNotFoundError`, marshals retention XML, and writes an XML response.

State and persistence behavior: this file itself does not manipulate filer entries directly. Persistence is delegated to object-lock helpers that store retention metadata in object/version extended attributes. The handlers enforce that retention APIs are only exposed for object-lock capable buckets, which implies versioning semantics.

Dependencies and integration points: depends on object-lock validation helpers defined across the S3 API package, XML encoding/decoding, S3 error mapping, and stats. It integrates with `put.go` because object writes also set explicit or default object-lock retention metadata, and with governance bypass permission checks used for overwrite/delete protection.

Risks: error mapping is compatibility-sensitive; clients expect distinct `MalformedXML`, `InvalidRetentionPeriod`, `AccessDenied`, `NoSuchKey`, and object-lock-configuration errors. Governance bypass depends on both a request header and permission evaluation outside this file. XML marshal/write errors after status headers can only be logged, so response-body write failures cannot be converted to S3 errors.

Test signals: no local test file is assigned for these handlers, but object-lock validation and bugfix tests in this subset exercise adjacent metadata availability logic. Additional integration tests should cover version-specific retention updates, missing retention response codes, and governance bypass denial.
