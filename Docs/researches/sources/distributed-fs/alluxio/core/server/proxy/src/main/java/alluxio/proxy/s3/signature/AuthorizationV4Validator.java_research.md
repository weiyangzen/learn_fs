# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AuthorizationV4Validator.java

Purpose: `AuthorizationV4Validator` verifies an AWS Signature Version 4 request by deriving the signing key from the string-to-sign credential scope and comparing the computed HMAC-SHA256 signature to the request signature.

Important APIs are `validateRequest(String strToSign, String signature, String userKey)` and private helpers `getSignedKey` and `sign`. Control flow extracts date, region, and service from line 3 of the string-to-sign (`date/region/service/aws4_request`), derives `kDate`, `kRegion`, `kService`, and `kSigning` using the AWS4 key schedule, signs the full string-to-sign, hex-encodes it, and compares it to the supplied signature.

State and persistence are absent. Dependencies include AWS SDK `SigningAlgorithm`, Kerby `Hex`, JCA `Mac`, and S3 authorization charset constants. Integration is expected from custom `Authenticator` implementations; `PassAllAuthenticator` documents this path, and `TestAWSV4Authenticator` uses it directly. Risks include strict dependence on string-to-sign line layout, no constant-time comparison, logging the derived signing key at info level, and no normalization of signature case. Test coverage validates one known signature/secret pair.
