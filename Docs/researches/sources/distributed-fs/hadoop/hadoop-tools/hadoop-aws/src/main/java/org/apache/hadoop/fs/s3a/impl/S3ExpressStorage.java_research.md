# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3ExpressStorage.java

## Purpose
`S3ExpressStorage` holds constants and helpers for detecting Amazon S3 Express One Zone bucket names and capability signaling.

## Important APIs and Types
Constants include `STORE_CAPABILITY_S3_EXPRESS_STORAGE`, `PRODUCT_NAME`, `ZONE_LENGTH`, and `S3EXPRESS_STORE_SUFFIX`. `isS3ExpressStore(bucket, endpoint)` checks AWS endpoint plus bucket suffix. `hasS3ExpressSuffix(bucket)` checks suffix only.

## Control Flow
Detection is a simple suffix check gated by `NetworkBinding.isAwsEndpoint(endpoint)` to avoid false positives on third-party endpoints.

## State and Persistence
The class is stateless.

## Dependencies and Integration Points
It depends on `NetworkBinding.isAwsEndpoint`. It integrates with capability reporting and S3 Express-specific configuration or warnings elsewhere in S3A.

## Risks and Edge Cases
Suffix-only detection may misclassify names on AWS-compatible stores if endpoint detection is wrong. `SUFFIX_LENGTH` is private and not used in this file. Null bucket values would throw from `endsWith`.

## Test Signals
Tests should cover AWS endpoint empty/default behavior, non-AWS endpoint false negatives, valid S3 Express suffixes, normal buckets, and null/empty bucket handling if expected by callers.
