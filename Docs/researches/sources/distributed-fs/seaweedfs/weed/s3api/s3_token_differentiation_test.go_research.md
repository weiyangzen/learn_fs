# sources/distributed-fs/seaweedfs/weed/s3api/s3_token_differentiation_test.go

## Purpose
This test file verifies that S3 IAM token routing distinguishes STS tokens from external OIDC tokens by exact issuer matching, not substring or heuristic matching.

## Important APIs, Types, and Functions
Tests target `S3IAMIntegration.isSTSIssuer`. They use `sts.NewSTSService`, `sts.STSConfig`, `integration.IAMManager`, and testify assertions.

## Control Flow
The main test initializes an STS service with issuer `https://seaweedfs-prod.company.com/sts`, embeds it in `S3IAMIntegration`, and checks exact match versus similar issuers, substrings, case variants, and common external OIDC issuers. A second test constructs an integration without an STS service and asserts all issuer checks return false.

## State and Persistence Behavior
All state is in-memory. STS config is initialized only for the test process; there is no token issuance, filer access, or network I/O.

## Dependencies and Integration Points
The test protects `AuthenticateJWT` routing in `s3_iam_middleware.go`, where unverified JWT issuer claims are used only to choose STS validation versus external OIDC validation.

## Risks and Edge Cases
Exact matching avoids false positives from issuer strings containing STS-like text, but it means configured issuer changes must align exactly with token `iss` claims. The test does not cover missing `stsService.Config`; production code returns false for nil service or config.

## Test Signals
Passing tests signal that only the configured issuer is classified as STS, external providers remain external, matching is case-sensitive, and missing STS service disables STS issuer recognition.
