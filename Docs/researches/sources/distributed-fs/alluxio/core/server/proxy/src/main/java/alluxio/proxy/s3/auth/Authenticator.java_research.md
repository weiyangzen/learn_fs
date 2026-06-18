# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/Authenticator.java

Purpose: `Authenticator` defines the S3 proxy's pluggable authentication boundary. It receives parsed AWS authentication material and decides whether a request should be accepted.

Important APIs are the `isAuthenticated(AwsAuthInfo)` method and nested `Factory.create(AlluxioConfiguration)`. The factory uses `CommonUtils.createNewClassInstance` with `PropertyKey.S3_REST_AUTHENTICATOR_CLASSNAME`, allowing deployments to swap in a custom implementation without changing S3 request parsing. Control flow is simple: `S3RestUtils.getUserFromSignature` constructs an `AwsSignatureProcessor`, obtains `AwsAuthInfo`, constructs an authenticator from configuration, and calls `isAuthenticated`; success returns the access ID as the Alluxio user.

State and persistence are absent in this interface. Its behavior is completely determined by the configured class and the provided `AwsAuthInfo`. Dependencies are Alluxio configuration, `PropertyKey`, `CommonUtils`, `AwsAuthInfo`, and `S3Exception`.

Integration points include the legacy Jersey S3 path and the newer servlet-based S3 path, both through `S3RestUtils.getUser` overloads. The main risk is operational: the default authenticator is permissive, so enabling `S3_REST_AUTHENTICATION_ENABLED` without changing `S3_REST_AUTHENTICATOR_CLASSNAME` parses signatures but does not validate secrets. Factory errors also surface at request time if the configured class is missing or incompatible. Test signals include `TestAWSV4Authenticator`, which demonstrates a custom implementation delegating to `AuthorizationV4Validator`.
