# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentials.java

## Purpose
`MarshalledCredentials` is a serializable, Hadoop `Writable` container for AWS access key, secret key, optional session token, role ARN, and expiration. It intentionally avoids AWS SDK types so token identifiers can be deserialized without AWS SDK classes.

## Important APIs and control flow
Constructors normalize null session token to empty. Getters/setters maintain non-null fields. `isEmpty()` requires both access and secret to be non-empty. `isValid(CredentialTypeRequired)` validates empty/full/session/any shapes. `write()` validates fields and serializes strings plus expiration. `readFields()` reads bounded-length strings and expiration. `validate()` throws `DelegationTokenIOException` on invalid shape. `setSecretsInConfiguration()` writes secrets into a Hadoop configuration. `toString()` avoids printing secrets while reporting type, validity, expiration, and role ARN.

## State, dependencies, and integration
State is the credential fields and expiration timestamp. Dependencies are Hadoop `Writable`, `Text`, `Configuration`, S3A constants/utilities, and delegation token IO exceptions. It is used by `MarshalledCredentialBinding`, delegation token code, and providers.

## Risks and test signals
This class handles secrets and must not leak values via `toString()`, logs, equality failures, or exception messages. Tests should cover serialization bounds, null rejection, all credential-type validations, empty semantics, expiration datetime conversion, configuration patching, and secret-free string output.
