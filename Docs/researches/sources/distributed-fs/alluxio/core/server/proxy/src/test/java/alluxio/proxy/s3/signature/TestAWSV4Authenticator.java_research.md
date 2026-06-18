# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAWSV4Authenticator.java

Purpose: `TestAWSV4Authenticator` demonstrates and validates a custom authenticator that performs real AWS V4 signature validation with a known secret.

Important types/APIs include nested `DummyAWSAuthenticator`, which implements `Authenticator.isAuthenticated` by calling `AuthorizationV4Validator.validateRequest`, and `testAuthenticator`, which supplies a fixed string-to-sign, signature, access ID, and secret. Control flow constructs `AwsAuthInfo`, invokes the dummy authenticator, and asserts true.

State and persistence are absent. Dependencies include `Authenticator`, `AwsAuthInfo`, `AuthorizationV4Validator`, `S3Exception`, and JUnit. Integration signal: this test documents the intended replacement for `PassAllAuthenticator` in secure deployments. Risks covered include HMAC key derivation and signature comparison for one vector. Gaps include negative signatures, malformed string-to-sign scopes, region/service variation, and complete request canonicalization through `StringToSignProducer`.
