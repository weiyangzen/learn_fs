# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/PassAllAuthenticator.java

Purpose: `PassAllAuthenticator` is the default `Authenticator` implementation and always accepts parsed authentication info. It provides compatibility for deployments that want S3 access IDs to map to Alluxio users without enforcing AWS secret validation.

Important API: `isAuthenticated(AwsAuthInfo)` returns `true` unconditionally. The class comment shows the intended pattern for stricter authenticators: call `AuthorizationV4Validator.validateRequest(authInfo.getStringTosSign(), authInfo.getSignature(), secret)`.

State and persistence are absent. Dependencies are only the `Authenticator` interface, `AwsAuthInfo`, and `S3Exception` in the method signature. Integration is through `Authenticator.Factory` when `S3_REST_AUTHENTICATOR_CLASSNAME` points to this class. Risk is direct and security-sensitive: when S3 REST authentication is enabled with this default, malformed requests may be rejected by parsers, but any syntactically valid credential/signature is accepted. Test signals are indirect; `TestAWSV4Authenticator` documents how a non-pass-all validator can be implemented.
