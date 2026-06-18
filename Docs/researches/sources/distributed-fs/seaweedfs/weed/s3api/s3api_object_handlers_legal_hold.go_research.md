# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_legal_hold.go

Purpose: implements S3 Object Lock legal hold GET and PUT handlers. Legal hold is version-aware and only available when object lock prerequisites are met.

Important APIs are `PutObjectLegalHoldHandler` and `GetObjectLegalHoldHandler`. They use package helpers `handleObjectLockAvailabilityCheck`, `parseObjectLegalHold`, `ValidateLegalHold`, `setObjectLegalHold`, `getObjectLegalHold`, and validation-to-S3 error mapping.

Control flow for PUT extracts bucket/object and optional `versionId`, checks object-lock availability, parses XML legal hold configuration from the request body, validates it, writes it through object-lock metadata helpers, sets `x-amz-version-id` when a version was specified, records active bucket time, and returns 200 with no body. GET performs availability checking, fetches the hold configuration, maps not-found and missing-configuration errors to S3 errors, marshals XML, writes XML header and body, and records active bucket time.

State and persistence are delegated to object-lock helpers that store legal hold metadata on object versions or current objects. The handler itself manipulates only HTTP headers/body and metrics.

Dependencies include XML encoding, object-lock errors such as `ErrObjectNotFound`, `ErrVersionNotFound`, and `ErrNoLegalHoldConfiguration`, S3 constants/errors, logging, and stats collection. Integration points are versioning/object lock subsystems and S3 route authorization configured elsewhere.

Risks: malformed XML or validation mistakes map to client errors, while persistence failures map to InternalError. The file does not include explicit tests in this subset; confidence depends on object-lock helper tests elsewhere and S3 compatibility tests. Response writing logs but cannot recover from partial write failures.
