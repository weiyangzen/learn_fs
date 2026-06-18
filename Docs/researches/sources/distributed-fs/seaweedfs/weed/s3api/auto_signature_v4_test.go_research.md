# sources/distributed-fs/seaweedfs/weed/s3api/auto_signature_v4_test.go

Purpose: broad regression suite for S3/IAM/STS Signature V4 authentication, canonical request construction, proxy header handling, presigned URLs, payload hashing, and streaming-body limits.

Important APIs/helpers: tests cover `isRequestPresignedSignatureV4`, `reqSignatureV4Verify`, `authRequest`, `doesSignatureMatch`, `doesPresignedSignatureMatch`, `extractHostHeader`, `getStringToSign`, `EncodePath`, `streamHashRequestBody`, `signRequestV4`, `signV4WithPath`, `preSignV4`, and `preSignV4WithPath`.

Control flow: unsigned requests are denied unless anonymous policy allows the action. Signed and presigned requests build canonical requests from method, URI, query, selected headers, signed headers, and payload hash. Proxy tests require forwarded prefix/host/port/proto to reconstruct externally signed paths and hosts, preserving trailing slash and default-port behavior, including IPv6. Presigned URLs must reject missing `X-Amz-Expires`.

State and persistence: IAM identities and credential maps are in-memory. Body hashing preserves or truncates request bodies after hashing for downstream use.

Dependencies and integration points: uses mux URL vars, IAM protobuf config loading, S3 constants, and SigV4 implementation helpers.

Risks and test signals: guards path cleaning, port normalization, service names, and payload hash regressions. GitHub issue #7080 is covered by IAM/STS service scope and bounded 10 MiB body hashing. Benchmarks compare signing/hash paths.
