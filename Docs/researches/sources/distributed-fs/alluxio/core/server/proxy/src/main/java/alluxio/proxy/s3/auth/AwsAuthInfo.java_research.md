# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/AwsAuthInfo.java

Purpose: `AwsAuthInfo` is a small immutable carrier for the values a configured S3 authenticator needs: access ID, string-to-sign, and request signature.

Important APIs are the constructor, `getStringTosSign`, `getSignature`, `getAccessID`, and `toString`. Control flow is data-only; instances are created by `AwsSignatureProcessor.getAuthInfo` after parsing either header or query authentication. For V4 requests, `mStringToSign` is computed by `StringToSignProducer`; for V2 requests it remains an empty string because only parsing is supported in this code path.

State and persistence are limited to final fields in memory. Dependencies are only Guava `MoreObjects` for diagnostic `toString`. Integration points include `Authenticator.isAuthenticated`, `PassAllAuthenticator`, and `AuthorizationV4Validator` consumers. Risks are mostly naming/API polish: `getStringTosSign` has a typo that is nevertheless part of the local API, and `toString` includes signature material, so logging it on authentication failure can expose sensitive request data. Test signals appear in `TestAWSV4Authenticator`, which constructs `AwsAuthInfo` manually and validates the signature with a dummy authenticator.
