# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_object_lock_config.go

Purpose: Implements S3 bucket Object Lock configuration get/put handlers.

Important APIs/types/functions: `PutObjectLockConfigurationHandler` and `GetObjectLockConfigurationHandler`.

Control flow: PUT checks Object Lock availability via `isObjectLockAvailable`, maps missing bucket to `NoSuchBucket` and unavailable state to `InvalidBucketState`, parses XML, validates retention configuration, then persists by setting `BucketConfig.ObjectLockConfig` through `updateBucketConfig`. GET loads bucket config; if cached Object Lock exists it marshals it with S3 namespace. If absent, it reloads the fresh bucket entry from filer, attempts to load Object Lock extended attrs, refreshes the full cache from that entry, and returns XML. If still absent, it returns `ObjectLockConfigurationNotFoundError`.

State and persistence: Object Lock state is stored in bucket entry extended attributes via shared Object Lock helpers called by `updateBucketConfig` and bucket creation. Metrics record bucket active time on success. Cache refresh is deliberately whole-config to avoid updating just Object Lock while other fields stay stale.

Dependencies and integration: depends on Object Lock parsing/validation/storage helpers, bucket config cache, filer entry lookup, S3 errors/constants, and stats. It integrates with bucket creation/versioning semantics: Object Lock availability implies versioning.

Risks: PUT cannot enable Object Lock on buckets not created with Object Lock support. GET mutates the returned cached config's `XMLNS` field before marshaling, which is harmless but worth noting. Fresh reload compensates for cache timing, indicating subscription consistency sensitivity.

Test signals: direct tests are elsewhere in Object Lock files; this file relies on shared validation helper coverage and integration tests for AWS-compatible object-lock behavior.
