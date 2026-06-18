# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSCannedACL.java

## Purpose
SDK migration enum mapping legacy AWS canned ACL names used by Hadoop configuration/code to the string values expected by AWS SDK v2/S3.

## Important APIs, Types, And Functions
Enum values include `Private`, `PublicRead`, `PublicReadWrite`, `AuthenticatedRead`, `AwsExecRead`, `BucketOwnerRead`, `BucketOwnerFullControl`, and `LogDeliveryWrite`. `toString()` returns the wire/config value such as `private` or `bucket-owner-full-control`.

## Control Flow
No complex control flow; callers select an enum and serialize it through `toString()`.

## State And Persistence
Each enum stores a fixed string value. No mutable or persistent state.

## Dependencies And Integration Points
Used by S3A request construction where canned ACL configuration must be translated to AWS headers or SDK values.

## Risks
AWS canned ACL string values are compatibility-sensitive. Missing new ACLs or typo changes would break object ACL configuration.

## Test Signals
Assert all enum `toString()` values match AWS S3 canned ACL names and verify configuration parsing/request construction uses the expected string.
