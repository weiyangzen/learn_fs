# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV4QueryParserUtils.java

Purpose: `AwsAuthV4QueryParserUtils` parses AWS V4 presigned URL query parameters into `SignatureInfo`.

Important APIs are `parseSignature(Map<String,String>)` and `validateDateAndExpires`. Control flow returns null if `X-Amz-Signature` is absent. Otherwise it validates expiration when `X-Amz-Expires` is present by parsing `X-Amz-Date`, adding the expiry seconds, and comparing with current time. It URL-decodes `X-Amz-Credential`, parses it through `AwsCredential`, and returns a V4 `SignatureInfo` using query-supplied algorithm, signed headers, date, credential scope, and signature with `signPayload=false`.

State and persistence are absent. Dependencies include S3 signature constants, `AwsCredential`, `SignatureInfo`, URL decoding, and Java time. Integration is the third parser attempted by `AwsSignatureProcessor`, and its `signPayload=false` drives `StringToSignProducer` to use `UNSIGNED-PAYLOAD`. Risks include missing explicit validation for required query keys besides signature/credential, `IllegalArgumentException` for expired URLs or bad expiry escaping as an internal error through some call paths, local-clock sensitivity, and no upper-bound enforcement for `X-Amz-Expires` here. No direct tests in this subset cover presigned URL parsing.
