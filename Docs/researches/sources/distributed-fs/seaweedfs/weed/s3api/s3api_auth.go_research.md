# sources/distributed-fs/seaweedfs/weed/s3api/s3api_auth.go

## Purpose
`s3api_auth.go` classifies incoming S3 requests by authentication scheme. It recognizes SigV4, SigV2, presigned variants, streaming signed/unsigned payloads, bearer JWTs, anonymous requests, and unknown authorization headers.

## Important APIs, Types, and Functions
The file defines SigV4/SigV2 date and algorithm constants, helper predicates `isRequestJWT`, `isRequestSignatureV4`, `isRequestSignatureV2`, `isRequestPresignedSignatureV4`, `isRequestPresignedSignatureV2`, `isRequestSignStreamingV4`, `isRequestUnsignedStreaming`, the `authType` enum, and `getRequestAuthType`.

## Control Flow
`getRequestAuthType` checks schemes in order: signed V2, presigned V2, streaming signed V4, streaming unsigned, signed V4, presigned V4, JWT, anonymous, then unknown. Streaming checks require `PUT` and exact `x-amz-content-sha256` sentinel values, including the trailer variant for signed streaming checks.

## State and Persistence Behavior
The file is stateless. It reads request headers and query parameters only.

## Dependencies and Integration Points
It depends on net/http and strings plus streaming checksum constants defined elsewhere. The returned `authType` steers downstream authentication, signature verification, JWT IAM authentication, or anonymous handling.

## Risks and Edge Cases
JWT detection checks `Authorization` prefix `"Bearer"` rather than `"Bearer "`, so strings like `BearerXYZ` classify as JWT and are later rejected by stricter middleware. Query-presigned requests with both V2 and V4 fields prefer V2 due to ordering. Unknown authorization headers are distinct from anonymous, which is important for rejecting malformed auth.

## Test Signals
Tests should cover classification order, streaming signed trailer payloads, unsigned streaming only on PUT, bearer with and without space, mixed presigned query keys, and unknown authorization headers.
