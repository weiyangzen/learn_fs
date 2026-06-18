# sources/distributed-fs/seaweedfs/weed/s3api/s3_bucket_encryption.go

Purpose: implements S3 bucket default encryption configuration handlers and conversion between S3 XML and SeaweedFS protobuf metadata.

Important APIs and types: `ServerSideEncryptionConfiguration`, `ServerSideEncryptionRule`, and `ApplyServerSideEncryptionByDefault` model AWS XML. `ErrNoEncryptionConfig`, `EncryptionTypeAES256`, and `EncryptionTypeKMS` define error/algorithm constants. Public handlers are `GetBucketEncryptionHandler`, `PutBucketEncryptionHandler`, and `DeleteBucketEncryptionHandler`. Internal APIs include `GetBucketEncryptionConfig`, `getEncryptionConfiguration`, `updateEncryptionConfiguration`, `removeEncryptionConfiguration`, `IsDefaultEncryptionEnabled`, and `GetDefaultEncryptionHeaders`.

Control flow: PUT reads XML, validates at least one rule, validates algorithm, optionally validates KMS key IDs, converts to `s3_pb.EncryptionConfiguration`, and updates bucket metadata. GET loads metadata and returns XML or S3 no-config errors. DELETE checks existence and clears metadata. Header helper returns default SSE headers for upload paths.

State and persistence: persists encryption configuration through structured bucket metadata APIs: `GetBucketMetadata`, `UpdateBucketEncryption`, and `ClearBucketEncryption`. Cache invalidation is delegated to those metadata update calls.

Dependencies and integration: uses XML, HTTP, filer and S3 protobufs, S3 constants, S3 errors, and `isValidKMSKeyID` from surrounding S3 KMS code.

Risks: only the first rule is honored, matching AWS but discarding extra XML rules. `removeEncryptionConfiguration` treats metadata lookup failures as internal errors, while get treats missing bucket metadata as no-config in a recreation race. KMS validation depends on external helper correctness.

Test signals: no direct file-specific test in this subset, but SSE policy tests and broader S3 encryption code paths rely on default encryption headers and metadata behavior.
