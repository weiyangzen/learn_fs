# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_config.go

Purpose: Defines bucket lifecycle storage keys and helpers for persisted lifecycle XML and transition minimum object size metadata.

Important APIs/types/functions: `bucketLifecycleConfigurationXMLKey`, `bucketLifecycleTransitionMinimumObjectSizeKey`, `bucketLifecycleTransitionMinimumObjectSizeHeader`, `defaultLifecycleTransitionMinimumObjectSize`, `maxBucketLifecycleConfigurationSize`, `normalizeBucketLifecycleTransitionMinimumObjectSize`, `getStoredBucketLifecycleConfiguration`, `storeBucketLifecycleConfiguration`, and `clearStoredBucketLifecycleConfiguration`.

Control flow: get reads `BucketConfig.Entry.Extended`, returns copied XML bytes plus normalized header value when present, or `found=false`. store and clear wrap `updateBucketConfig`, editing only lifecycle-related extended attributes. Normalization trims whitespace and defaults empty values to `all_storage_classes_128K`.

State and persistence: lifecycle XML is persisted directly in bucket extended attributes, not in structured protobuf metadata. This allows `populateBucketConfigDerivedFields` to build `LifecycleTTLResolver` from canonical XML when the fast-path opt-in flag is set.

Dependencies and integration: used by `GetBucketLifecycleConfigurationHandler`, `PutBucketLifecycleConfigurationHandler`, and `DeleteBucketLifecycleHandler` in the main bucket handlers file. Depends on `s3err` and shared bucket config mutation.

Risks: stores raw XML bytes; validation is performed by callers, so direct helper misuse could persist invalid XML. Lifecycle data shares extended-attribute namespace and update semantics with versioning/Object Lock/ACL/policy.

Test signals: lifecycle response tests cover stored XML retrieval, default header behavior, oversized PUT body, and read error mapping.
