# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV4HeaderParser.java

Purpose: `TestAuthorizationV4HeaderParser` validates selected AWS V4 Authorization header parser behavior.

Important tests are `testAuthHeaderV4` and `testIncorrectHeader`. Setup formats the current local date with `DATE_FORMATTER` because production `AwsCredential` rejects dates outside yesterday/tomorrow. The valid test constructs a V4 header, parses it, and checks access ID, credential date, signed headers, and signature. The malformed test omits `SignedHeaders` and expects an `AuthorizationHeaderMalformed` S3 error code.

State and persistence are absent. Dependencies are JUnit, Java time, S3 constants, parser utility, and `S3Exception`. Integration signal: these tests protect the first parser in `AwsSignatureProcessor`. Risks covered include current-date credential acceptance and missing-field rejection. Gaps include algorithm rejection, non-hex signatures, malformed credential scopes, date parse failures, query auth, and full string-to-sign generation.
