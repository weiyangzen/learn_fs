# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialBinding.java

## Purpose
`MarshalledCredentialBinding` bridges AWS SDK credential objects and S3A's SDK-free `MarshalledCredentials` representation used in delegation tokens and credential propagation.

## Important APIs and control flow
`fromSTSCredentials()` copies STS access key, secret, session token, and expiration into `MarshalledCredentials`. `fromAWSCredentials()` copies v2 session credentials. `fromEnvironment()` reads AWS environment variable names into possibly incomplete credentials. `fromFileSystem()` loads access/secret/session values from S3A configuration and Hadoop credential providers after excluding incompatible providers. `toAWSCredentials()` validates required credential type, throws `NoAwsCredentialsException` for empty credentials, throws `NoAuthWithAWSException` for invalid shape, and returns either `AwsSessionCredentials` or `AwsBasicCredentials`. `requestSessionCredentials()` builds an STS client and requests temporary credentials with retry translation.

## State, dependencies, and integration
The class is stateless. It depends on AWS SDK auth/STS classes, `MarshalledCredentials`, S3A constants, `STSClientFactory`, `Invoker`, and Hadoop provider utilities. It integrates with delegation token bindings, session credential providers, and tests that need marshalled credentials without loading AWS SDK in token identifier classes.

## Risks and test signals
Keeping AWS SDK references out of `MarshalledCredentials` is intentional; moving conversion there would hurt deserialization. Tests should cover full/session/empty validation, environment loading, filesystem credential-provider lookup, STS region error logging, expiration conversion, and exception types.
