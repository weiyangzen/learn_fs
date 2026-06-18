# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3ExpressStorage.java

## Purpose
`TestS3ExpressStorage` validates S3 Express bucket detection based on bucket naming and endpoint classification.

## Important APIs, Types, and Functions
- Tests `S3ExpressStorage.isS3ExpressStore(bucket, endpoint)`.
- Uses an S3 Express-style bucket name `bucket--usw2-az2--x-s3`.
- Covers empty/default endpoint, AWS regional endpoints, China/Gov/FIPS/accesspoint-style endpoints, and a third-party endpoint.

## Control Flow
Default endpoint tests classify the S3 Express-style bucket as Express and a normal bucket as non-Express. AWS endpoint tests preserve Express classification across known AWS endpoint forms. Third-party endpoint test forces non-Express even with an Express-shaped bucket name.

## State and Persistence Behavior
No persistent state. All checks are pure string classification.

## Dependencies and Integration Points
This protects logic used when deciding S3 Express-specific behavior such as create-session handling and feature differences.

## Risks and Edge Cases
Endpoint pattern matching must keep up with AWS endpoint variants. Third-party endpoints are deliberately excluded to avoid misclassifying compatible stores.

## Test Signals
Passing confirms S3 Express detection is tied to both bucket naming and AWS endpoint recognition.
