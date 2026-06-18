# sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2.go

Purpose: Implements AWS S3 Signature Version 2 authentication and POST policy signature checks.

Important APIs, types, and functions: `isReqAuthenticatedV2` dispatches header vs presigned V2 requests. `doesPolicySignatureV2Match`, `doesSignV2Match`, and `doesPresignV2SignatureMatch` validate POST policy, Authorization header, and query-string signatures. Helpers include `validateV2AuthHeader`, `signatureV2`, `preSignatureV2`, `getStringToSignV2`, `canonicalizedResourceV2`, `canonicalizedAmzHeadersV2`, `calculateSignatureV2`, and `compareSignatureV2`. `resourceList` defines whitelisted subresources for canonical resources.

Control flow and state: Verification parses access key/signature fields, looks up credentials through IAM, rejects missing/invalid/expired keys, optionally checks write permission for POST policies, canonicalizes request components, calculates HMAC-SHA1/base64 signatures, and compares decoded signatures in constant time. Presigned requests additionally parse and enforce `Expires`.

State and persistence behavior: Stateless aside from reading IAM identity/credential maps. It does not persist or mutate request bodies.

Dependencies and integration points: Called from `authenticateRequestInternal` for V2 auth types. Depends on IAM credential lookup, legacy `Identity.CanDo`, S3 constants/errors, HMAC/SHA1/base64, and HTTP headers/query encoding.

Risks and test signals: SigV2 canonicalization is compatibility-sensitive: whitelisted query resources must stay sorted, `x-amz-date` suppresses `Date`, and header casing/value joining affect signatures. Tests cover auth-header validation, signature format, valid signed requests with content/query/amz headers, and malformed/unknown-key cases.
