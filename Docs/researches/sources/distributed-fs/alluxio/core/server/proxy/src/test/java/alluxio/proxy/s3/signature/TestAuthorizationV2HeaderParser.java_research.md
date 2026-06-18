# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV2HeaderParser.java

Purpose: `TestAuthorizationV2HeaderParser` validates the legacy AWS V2 authorization header parser.

Important tests are `testAuthHeaderV2` and `testIncorrectHeader`. The first parses `AWS accessKey:signature` and verifies access key and signature in the returned `SignatureInfo`. The second uses an incorrect prefix and expects a null parser result rather than an exception, allowing `AwsSignatureProcessor` to try the next parser.

State and persistence are absent. Dependencies are JUnit, `AwsAuthV2HeaderParserUtils`, `SignatureInfo`, and `S3Exception`. Integration signal: V2 parsing is part of `AwsSignatureProcessor`'s parser chain. Risks covered include valid splitting and nonmatching prefix behavior. Gaps include malformed V2-looking headers, blank access IDs/signatures, extra spaces, and signatures containing colons.
