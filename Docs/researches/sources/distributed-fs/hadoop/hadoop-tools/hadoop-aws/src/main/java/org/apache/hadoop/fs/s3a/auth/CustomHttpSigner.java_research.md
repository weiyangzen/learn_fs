# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomHttpSigner.java

## Purpose
`CustomHttpSigner` is a production test-support signer for the AWS SDK HTTP signer plugin path. It delegates to the standard AWS V4 HTTP signer while logging requests at TRACE.

## Important APIs and control flow
The constructor creates an `AwsV4HttpSigner` delegate. `sign()` logs the synchronous request and returns `delegateSigner.sign(request)`. `signAsync()` logs the async request and returns `delegateSigner.signAsync(request)`.

## State, dependencies, and integration
State is the delegate signer. Dependencies are AWS SDK HTTP auth signer interfaces and `AwsCredentialsIdentity`. It is enabled through S3A HTTP signer configuration for plugin mechanism tests.

## Risks and test signals
TRACE logging should not expose sensitive headers in normal log configurations. Tests should verify synchronous and async signing delegate correctly and that configuration can instantiate the class.
