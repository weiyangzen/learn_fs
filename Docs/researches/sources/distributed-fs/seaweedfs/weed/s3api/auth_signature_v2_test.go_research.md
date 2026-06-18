# sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2_test.go

Purpose: Unit tests for SigV2 header parsing and header-auth signature verification.

Important APIs, types, and functions: `setupTestIAMForV2Auth` builds an IAM with one admin credential. `TestValidateV2AuthHeader`, `TestSignatureV2Format`, and `TestDoesSignV2Match` exercise `validateV2AuthHeader`, `signatureV2`, and `doesSignV2Match`.

Control flow and state: The tests generate requests with fixed dates, content headers, query parameters, and `x-amz-*` headers, then compare verifier results to expected S3 errors and identity presence. Negative cases cover invalid signature, unknown key, empty authorization, missing signature, wrong prefix, and missing space after `AWS`.

State and persistence behavior: All IAM state is local to the helper: one identity, one credential, and an access-key map.

Dependencies and integration points: Depends on S3 constants/errors and the SigV2 implementation. It does not cover presigned V2 or POST policy paths.

Risks and test signals: Confirms stricter Authorization prefix parsing and expected constant-time signature path behavior for common request shapes. Remaining gaps are presigned expiry/canonical resource coverage and inactive/expired credential handling on V2 paths.
