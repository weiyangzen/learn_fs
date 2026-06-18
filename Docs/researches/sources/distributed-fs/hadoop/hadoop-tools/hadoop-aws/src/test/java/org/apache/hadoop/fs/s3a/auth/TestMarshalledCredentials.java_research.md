# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestMarshalledCredentials.java

## Purpose

`TestMarshalledCredentials.java` unit-tests serialization and provider behavior for S3A marshalled AWS credentials and encryption secrets.

## Important APIs, Types, and Functions

Setup creates `MarshalledCredentials` with access key, secret key, session token, role ARN, expiration, and bucket URI. Tests use `S3ATestUtils.roundTrip()`, `EncryptionSecrets`, `MarshalledCredentialProvider`, `MarshalledCredentials.CredentialTypeRequired`, and `NoAuthWithAWSException`.

## Control Flow

Round-trip tests serialize and deserialize full credentials, credentials without session data, and encryption secrets, then assert equality and individual fields. Provider tests construct a provider with session-only requirements and resolve AWS credentials, then construct a mismatched full-only provider and expect failure only when credentials are resolved.

## State and Persistence Behavior

State is in-memory serializable test data. No secret values are externalized beyond the test round-trip helper.

## Dependencies and Integration Points

This covers S3A credential marshalling, delegation encryption secret marshalling, AWS SDK v2 credential resolution, and provider validation of required credential type.

## Risks and Edge Cases

Credential mismatch should be lazy until `resolveCredentials()`, and null bucket URIs should fail fast. Tests must avoid leaking secret material in assertion output.

## Test Signals

Signals are object equality after round trips, exact field equality, successful session credential resolution, `NoAuthWithAWSException` for type mismatch, and `NullPointerException` for null URI construction.
