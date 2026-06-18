# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV2HeaderParserUtils.java

Purpose: `AwsAuthV2HeaderParserUtils` parses legacy AWS Signature V2 Authorization headers of the form `AWS accessKey:signature`.

Important API: `parseSignature(String authHeader)` returns null when the header is absent or does not start with `AWS `, throws `AUTHORIZATION_HEADER_MALFORMED` for malformed V2-looking values, and returns a `SignatureInfo` with version `V2`, access key, signature, and empty V4 fields for valid values. Control flow splits first on a single space and then on `:`, rejecting blank access ID or signature.

State and persistence are absent. Dependencies are `SignatureInfo`, `S3Exception`, `S3ErrorCode`, and Apache `StringUtils`. Integration is the second parser attempted by `AwsSignatureProcessor`. Risks include `String.split(":")` rejecting signatures containing additional colons and no V2 canonical string production or secret validation in the local auth path. Test signals in `TestAuthorizationV2HeaderParser` cover a valid header and a nonmatching prefix returning null.
