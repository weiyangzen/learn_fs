# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_metadata_test.go

Purpose: Unit-tests the `BucketMetadata` value object and update pattern.

Important APIs/types/functions: `TestBucketMetadataStruct`, `TestBucketMetadataUpdatePattern`, and `TestBucketMetadataHelperFunctions`.

Control flow: tests create metadata with `NewBucketMetadata`, add tags/encryption/CORS, and assert `IsEmpty`, `HasTags`, `HasEncryption`, and `HasCORS` behavior. The update-pattern test simulates the callback used by `UpdateBucketMetadata`.

State and persistence: all state is local Go structs; there is no filer or cache persistence. The test validates logical state transitions before serialization into `s3_pb.BucketMetadata`.

Dependencies and integration: uses `s3_pb.EncryptionConfiguration` and `cors.CORSConfiguration`. It supports tagging, CORS, and bucket encryption handlers that share the structured metadata API.

Risks: does not test protobuf marshal/unmarshal, nil maps returned from protobuf, concurrent updates, cache interactions, or persistence failure handling.

Test signals: basic but useful guard that helper predicates remain aligned with default empty metadata semantics.
