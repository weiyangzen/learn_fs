<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_federation_token_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_federation_token_test.go

Purpose: broad regression and documentation coverage for `GetFederationToken`, including validation, JWT claims, policy embedding, session policy behavior, and response XML.

Important APIs/types/functions: `mockUserStore` supports IAMManager policy lookup tests. Tests cover basic flow, session policy embedding, temporary credential rejection, missing/invalid `Name`, duration bounds, XML response structure, malformed policy rejection, STS readiness, default/max duration constants, `GetPoliciesForUser`, policy merge/dedup, and fallback when no IAM manager is present.

Control flow: many tests simulate the handler's internal claim construction directly, then validate generated tokens with STS service. Handler-level validation tests call `HandleSTSRequest` with crafted forms and assert HTTP status/body. Policy lookup tests exercise IAMManager user-store integration separately.

State and persistence behavior: all state is in-memory: STS sessions are JWTs, IAM policies and users live in memory stores, and temporary credentials are generated for test expirations. No filer persistence is involved.

Dependencies and integration: depends on IAM integration manager, policy engine types, STS service/token generator, generated IAM identity protobufs, XML marshaling, and testify. It is the strongest test signal for the `handleGetFederationToken` branch in `s3api_sts.go`.

Risks: direct simulation can drift from handler code if the handler changes and tests do not call it end-to-end with SigV4. Policy merge from maps is inherently unordered; tests sort where deterministic assertions are needed. Mock user store returns nil,nil for missing users, matching expected manager semantics.

Test signals: passing tests mean GetFederationToken rejects temporary credentials, validates AWS name and duration bounds, defaults to 12h and caps at 36h, embeds caller and group policies, embeds restrictive session policies for later intersection, rejects malformed/oversized policies, and formats AWS-compatible XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_federation_token_test.go -->
