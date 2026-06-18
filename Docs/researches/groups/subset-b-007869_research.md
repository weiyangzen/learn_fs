# subset-b-007869 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials.go

Purpose: Owns SeaweedFS S3 identity access management: loading static and dynamic S3 credentials, authenticating requests, authorizing S3 actions, syncing IAM policies/groups, integrating STS/JWT IAM sessions, and preserving account/owner metadata for S3 ACL semantics.

Important APIs, types, and functions: `IdentityAccessManagement` is the central mutable auth state with identity, access-key, policy, group, account, credential-manager, bucket-policy, and IAM-integration caches. `Identity`, `Account`, and `Credential` model users, canonical owners, and access keys. Construction flows through `NewIdentityAccessManagementWithStore`, `SetFilerClient`, `Shutdown`, `loadS3ApiConfigurationFromFile`, and `LoadS3ApiConfigurationFromCredentialManager`. Config mutation APIs include `ReplaceS3ApiConfiguration`, `MergeS3ApiConfiguration`, `RemoveIdentity`, `UpsertIdentity`, `PutPolicy`, `DeletePolicy`, `PutGroup`, and `RemoveGroup`. Request-facing APIs include `Auth`, `AuthPostPolicy`, `AuthenticateRequest`, `AuthSignatureOnly`, `VerifyActionPermission`, `AuthorizeCopySource`, and `AuthorizeBatchDeleteKey`.

Control flow and state: Startup optionally parses `s3.externalUrl`, initializes a credential manager, loads static config first, merges dynamic credential-store config, optionally starts polling for PostgreSQL stores, loads AWS env credentials, publishes static identities to the manager, then enables auth only when identities exist or an explicit caller later invokes `EnableAuthEnforcement`. Static identities are tracked in `staticIdentityNames` and protected from dynamic updates. Replacement mode rebuilds accounts, identities, access-key indexes, groups, and the cached IAM policy engine atomically under `iam.m`; merge mode starts from current state, preserves static users, updates dynamic users/service accounts, handles anonymous deletion, and refreshes group reverse indexes on full reloads.

State and persistence behavior: Runtime state is in-memory maps protected by `sync.RWMutex`, with `hasAnyIdentity` as a process-wide one-way atomic signal. Durable data lives behind `credential.CredentialManager` stores, often filer-backed. Static file/env identities are copied into the credential manager's static identity view for listing, but remain immutable through dynamic reloads. Policy cache sync to the advanced IAM manager is serialized by `iamManagerSyncMu` and reads the live `iam.policies` map at apply time to avoid stale full-state replacement.

Dependencies and integration points: This file bridges `weed/credential`, filer S3 config parsing, KMS config loading, `wdclient.FilerClient`, bucket policy evaluation, `policy_engine`, IAM integration (`S3IAMIntegration`, STS/JWT/session validation), S3 constants/error responses, wildcard action matching, and HTTP middleware. The signature verifier files call `lookupByAccessKey`, `validateSTSSessionToken`, and permission methods here; handlers call context identity setters, copy-source and batch-delete authorizers, and account lookup helpers.

Risks and test signals: Security-sensitive behavior includes fail-closed bucket-policy errors, stripping client-supplied internal IAM headers before auth, rejecting disabled users/inactive/expired credentials, session-token priority over legacy actions, static identity immutability, and not enabling auth solely because an empty IAM integration exists. Risks include stale indexes during partial merges, policy cache desynchronization, map mutation races if future code bypasses locks, and authorization drift between legacy `Actions`, cached IAM policies, and advanced IAM integration. Covered by the sibling tests for static config, policy sync, STS identity policy names/claims, proxy signing, unsigned streaming, and header spoofing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_policy_sync_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_policy_sync_test.go

Purpose: Regression tests for synchronizing runtime S3 IAM policies from `IdentityAccessManagement` into the advanced `integration.IAMManager` policy engine.

Important APIs, types, and functions: `newTestIAMManager` creates a memory-backed IAM manager with STS and policy engines. Tests exercise `SetIAMIntegration`, `PutPolicy`, `DeletePolicy`, `resyncIAMManagerPolicies`, and `integration.IAMManager.IsActionAllowed`.

Control flow and state: Each test installs policy JSON into `iam.policies`, attaches an IAM integration, and asks the manager whether named policies allow `s3:PutObject` on matching resources. The stale-snapshot test mutates `iam.policies` directly under lock, calls `resyncIAMManagerPolicies`, and verifies the manager converges to the current map.

State and persistence behavior: All state is in-memory. The tests model the production behavior where `SyncRuntimePolicies` is a full desired-state replacement, so ordering and snapshot freshness matter.

Dependencies and integration points: Depends on `weed/iam/integration`, `policy`, `sts`, protobuf IAM policies, and `testify/require`. It specifically covers the bridge implemented in `auth_credentials.go` between legacy policy storage and the advanced IAM manager.

Risks and test signals: The tests pin three risks: `PutPolicy` must immediately grant through the IAM manager, `DeletePolicy` must remove grants, and `SetIAMIntegration` must flush policies loaded before integration attachment. The final test protects against concurrent update races that could resurrect deleted policies or drop new ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_policy_sync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_static_config_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_static_config_test.go

Purpose: Tests the distinction between advanced IAM config files with no inline identities and traditional static S3 credential files with identities.

Important APIs, types, and functions: Exercises `loadS3ApiConfigurationFromFile`, `IsStaticConfig`, `onIamConfigChange`, `LoadS3ApiConfigurationFromCredentialManager`, and test helpers `writeTempIamConfig` and `isStaticName`.

Control flow and state: `TestIamConfigWithoutIdentitiesIsNotStatic` loads an STS-only JSON file, creates a dynamic user in the memory credential manager, simulates an `/etc/iam/identities` event, and expects live reload. `TestConfigWithIdentitiesIsStatic` loads inline identities, verifies static mode and `IsStatic`, then ensures metadata events do not import dynamic filer identities. `TestReloadStaticConfigMarksNewIdentitiesWithoutFreezingDynamic` checks reloads add new static names without freezing already dynamic identities.

State and persistence behavior: Uses memory credential storage plus temporary JSON files. The core state under test is `useStaticConfig`, `staticIdentityNames`, `Identity.IsStatic`, and the dynamic credential-manager contents.

Dependencies and integration points: Depends on the memory credential store, filer IAM directory constants, metadata entries, and the `newTestS3ApiServerWithMemoryIAM` helper from `auth_credentials_subscribe_test.go`.

Risks and test signals: Prevents operator-created IAM users from being ignored when `-iam.config` contains only advanced STS/OIDC settings. Also protects the established static-file behavior where inline identities are immutable and should not be overwritten by filer reloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_static_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe.go

Purpose: Handles filer metadata subscriptions for S3 runtime state: bucket metadata, IAM config, OIDC providers, and circuit breaker config.

Important APIs, types, and functions: `subscribeMetaEvents` follows filer metadata and fans each event to `onBucketMetadataChange`, `onIamConfigChange`, `onOIDCProviderChange`, and `onCircuitBreakerConfigChange`. IAM-specific constants and handlers include `oidcProvidersDir`, `onIamConfigChange`, and `onOIDCProviderChange`; bucket cache helpers include `updateBucketConfigCacheFromEntry` and `invalidateBucketConfigCache`.

Control flow and state: The subscription callback handles create/update/delete/rename events. For moves, it processes the destination and then replays delete events for the source directory. For same-directory renames, it replays deletion for stale bucket/circuit-breaker names. `onIamConfigChange` ignores events when IAM is static, reloads on legacy `identity.json`, and reloads on multi-file identities, policies, service accounts, or groups. `onOIDCProviderChange` refreshes the IAM manager's OIDC provider view for changes under `/etc/iam/oidc-providers`.

State and persistence behavior: This file does not persist directly; it reacts to filer metadata and refreshes in-memory IAM, OIDC, circuit breaker, bucket registry, and bucket config cache state from authoritative stores. It uses retry-follow semantics with an incrementing client epoch.

Dependencies and integration points: Integrates with filer path constants, protobuf metadata follow APIs, `pb.WithFilerClientFollowMetadata`, `util.RetryUntil`, S3 bucket registry/cache code, circuit breaker config, and advanced IAM provider storage.

Risks and test signals: Static configs intentionally suppress IAM live reloads, so static detection must be precise. Rename/move handling is subtle because missing source-delete replay can leave stale bucket or config state. The subscribe tests cover legacy identity deletion and multi-file identity directory reloads; static-config tests cover the static/dynamic gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe_test.go

Purpose: Tests IAM metadata change handling and provides shared memory-IAM helpers for related tests.

Important APIs, types, and functions: `TestOnIamConfigChangeLegacyIdentityDeletionReloadsConfiguration`, `TestOnIamConfigChangeReloadsOnIamIdentityDirectoryChanges`, `newTestS3ApiServerWithMemoryIAM`, and `hasIdentity`.

Control flow and state: The legacy deletion test simulates deletion of `/etc/iam/identity.json` and expects a full reload from the credential manager so migrated identities remain available. The identity-directory test seeds config, creates `alice` in the credential manager, simulates a new identity JSON event, and expects the in-memory IAM index to include Alice.

State and persistence behavior: Uses a memory credential manager as durable backing for the tests, then initializes a minimal `IdentityAccessManagement` with maps, locks, and `ReplaceS3ApiConfiguration`.

Dependencies and integration points: Depends on `weed/credential`, memory credential store registration, filer IAM constants, `filer_pb.Entry`, and `iam_pb.S3ApiConfiguration`.

Risks and test signals: Protects live-reload behavior during migration from legacy single-file IAM config to multi-file stores. The helper creates only the IAM fields needed by these tests, so future production code that assumes additional initialized fields may need helper updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_subscribe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_trust.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_trust.go

Purpose: Provides the S3 IAM wrapper for validating whether a principal may assume a role under a role trust policy.

Important APIs, types, and functions: `ValidateTrustPolicyForPrincipal(ctx, roleArn, principalArn)` delegates to `iam.iamIntegration.ValidateTrustPolicyForPrincipal` when an integration is installed.

Control flow and state: There is one conditional path: call the integration or return `IAM integration not available`. It reads `iamIntegration` but does not mutate IAM state.

State and persistence behavior: No persistence and no local caches. Trust policy data is owned by the IAM integration/backend.

Dependencies and integration points: Depends only on `context` and the IAM integration interface implemented elsewhere in the S3 IAM stack. STS assume-role flows use this as a bridge from S3 IAM to the role/trust-policy engine.

Risks and test signals: If called without integration, trust validation fails closed with an error. The method does not acquire `iam.m`, so future concurrent replacement of `iamIntegration` should preserve pointer safety or add locking if mutation patterns change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_trust.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_jwt_streaming_unsigned_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_jwt_streaming_unsigned_test.go

Purpose: Regression tests for JWT bearer authentication on requests classified as `STREAMING-UNSIGNED-PAYLOAD-TRAILER`.

Important APIs, types, and functions: `TestJWTStreamingUnsignedAuth` exercises `getRequestAuthType`, `AuthenticateRequest`, and `authenticateJWTWithIAM` through a `MockIAMIntegration`. `TestJWTStreamingUnsignedChunkedReader` uses streaming payload test helpers to verify body decoding does not require a SigV4 seed signature for bearer-token uploads.

Control flow and state: The auth test creates IAM with memory store, attaches a JWT-auth mock, forces auth enabled, sets unsigned-streaming and bearer headers, verifies request classification remains unsigned-streaming, and expects the JWT identity. The reader test adds a bearer header to an unsigned streaming request and runs the chunked reader path.

State and persistence behavior: Uses transient in-memory IAM state and resets the shared memory store around the first test to avoid cross-test identity leakage.

Dependencies and integration points: Depends on `MockIAMIntegration` from STS tests, streaming body helpers from the S3 test suite, and `s3err`.

Risks and test signals: Covers a subtle dispatch bug: unsigned-streaming describes payload framing, not authentication type. JWT requests with checksum trailers must authenticate via IAM integration and must not be downgraded to anonymous or incorrectly verified as SigV4 streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_jwt_streaming_unsigned_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_proxy_integration_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_proxy_integration_test.go

Purpose: Full HTTP-stack integration tests for SigV4 verification through `httputil.ReverseProxy` with real AWS SDK v4 signatures.

Important APIs, types, and functions: `TestReverseProxySignatureVerification` configures a backend `httptest.Server` calling `iam.authRequest`, a real reverse proxy, and AWS SDK `v4.Signer.SignHTTP`.

Control flow and state: Each case writes temporary S3 credentials, starts backend and proxy servers, configures `s3.externalUrl` when needed, signs a client-facing URL, rewrites the request destination to the proxy while preserving signed headers and `Host`, and checks whether backend auth returns HTTP 200 or 403.

State and persistence behavior: Uses temp JSON config and in-memory credential store state per case. Network state is local `httptest` servers.

Dependencies and integration points: Integrates net/http request normalization, reverse proxy host rewriting, `X-Forwarded-Host` and `X-Forwarded-Proto`, `parseExternalUrlToHost`, `extractHostHeader`, and the SigV4 verifier.

Risks and test signals: Ensures proxy deployments verify against the client-facing host rather than backend host. It covers success with forwarded host, success with `externalUrl` even when the proxy omits forwarded host, default port stripping, and expected failure when neither forwarded host nor external URL preserve the signed authority.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_proxy_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_security_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_security_test.go

Purpose: Security regression tests for S3 authentication enforcement, signature-only paths, internal header spoofing, anonymous unsigned streaming uploads, and proxy/external URL signature behavior.

Important APIs, types, and functions: `signRawHTTPRequest` signs requests with the real AWS SDK. `TestReproIssue7912` exercises `NewIdentityAccessManagementWithStore`, `authRequest`, `AuthSignatureOnly`, `isAdmin`, and `CanDo`. `TestAnonymousStreamingUnsignedUpload` covers anonymous unsigned-streaming auth. `TestExternalUrlSignatureVerification` and `TestRealSDKSignerWithForwardedHeaders` validate host canonicalization against real SDK signatures.

Control flow and state: The issue reproduction loads a config with admin/read-only users and asserts unknown keys, wrong secrets, anonymous protected requests, and arbitrary credentials are denied while valid credentials pass. It also checks `AuthSignatureOnly` accepts valid signatures, rejects bad signatures and unsigned-streaming without auth, and strips client-supplied SeaweedFS principal/session headers. The anonymous streaming test loads only an anonymous identity and expects a checksum-trailer PUT without Authorization to authenticate as anonymous. Proxy tests sign against external/client hosts and verify SeaweedFS extracts matching hosts.

State and persistence behavior: Tests use temporary config files, memory credential store reset around tests that can leak anonymous state, and per-test IAM managers.

Dependencies and integration points: Depends on AWS SDK v2 signing, `httptest`, S3 constants/errors, and the v4 host/signature code. It cross-checks behavior across `auth_credentials.go`, `auth_signature_v4.go`, and auth-type detection/chunked upload support.

Risks and test signals: Protects against auth bypasses and privilege escalation: unknown credentials must not be accepted, internal IAM headers must not be client-spoofable, unsigned streaming must not bypass auth, and reverse-proxy host handling must match AWS SDK canonicalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_security_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2.go

Purpose: Implements AWS S3 Signature Version 2 authentication and POST policy signature checks.

Important APIs, types, and functions: `isReqAuthenticatedV2` dispatches header vs presigned V2 requests. `doesPolicySignatureV2Match`, `doesSignV2Match`, and `doesPresignV2SignatureMatch` validate POST policy, Authorization header, and query-string signatures. Helpers include `validateV2AuthHeader`, `signatureV2`, `preSignatureV2`, `getStringToSignV2`, `canonicalizedResourceV2`, `canonicalizedAmzHeadersV2`, `calculateSignatureV2`, and `compareSignatureV2`. `resourceList` defines whitelisted subresources for canonical resources.

Control flow and state: Verification parses access key/signature fields, looks up credentials through IAM, rejects missing/invalid/expired keys, optionally checks write permission for POST policies, canonicalizes request components, calculates HMAC-SHA1/base64 signatures, and compares decoded signatures in constant time. Presigned requests additionally parse and enforce `Expires`.

State and persistence behavior: Stateless aside from reading IAM identity/credential maps. It does not persist or mutate request bodies.

Dependencies and integration points: Called from `authenticateRequestInternal` for V2 auth types. Depends on IAM credential lookup, legacy `Identity.CanDo`, S3 constants/errors, HMAC/SHA1/base64, and HTTP headers/query encoding.

Risks and test signals: SigV2 canonicalization is compatibility-sensitive: whitelisted query resources must stay sorted, `x-amz-date` suppresses `Date`, and header casing/value joining affect signatures. Tests cover auth-header validation, signature format, valid signed requests with content/query/amz headers, and malformed/unknown-key cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2_test.go

Purpose: Unit tests for SigV2 header parsing and header-auth signature verification.

Important APIs, types, and functions: `setupTestIAMForV2Auth` builds an IAM with one admin credential. `TestValidateV2AuthHeader`, `TestSignatureV2Format`, and `TestDoesSignV2Match` exercise `validateV2AuthHeader`, `signatureV2`, and `doesSignV2Match`.

Control flow and state: The tests generate requests with fixed dates, content headers, query parameters, and `x-amz-*` headers, then compare verifier results to expected S3 errors and identity presence. Negative cases cover invalid signature, unknown key, empty authorization, missing signature, wrong prefix, and missing space after `AWS`.

State and persistence behavior: All IAM state is local to the helper: one identity, one credential, and an access-key map.

Dependencies and integration points: Depends on S3 constants/errors and the SigV2 implementation. It does not cover presigned V2 or POST policy paths.

Risks and test signals: Confirms stricter Authorization prefix parsing and expected constant-time signature path behavior for common request shapes. Remaining gaps are presigned expiry/canonical resource coverage and inactive/expired credential handling on V2 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4.go

Purpose: Implements AWS Signature Version 4 verification for header, presigned, streaming seed, STS session-token, and POST policy flows.

Important APIs, types, and functions: `reqSignatureV4Verify` dispatches to `verifyV4Signature`. `v4AuthInfo`, `signValues`, and `credentialHeader` hold parsed auth state. Parsing helpers include `parseSignV4`, `extractV4AuthInfoFromHeader`, `extractV4AuthInfoFromQuery`, `parseCredentialHeader`, `parseSignedHeaderList`, and `parseSignature`. Verification helpers include `validateSTSSessionToken`, `calculateAndVerifySignature`, `extractSignedHeaders`, `verifySignedHeadersCoverage`, `extractHostHeader`, `buildPathWithForwardedPrefix`, `checkPresignedRequestExpiry`, `getCanonicalRequest`, `getStringToSign`, `getSigningKey`, `encodePath`, and `compareSignatureV4`.

Control flow and state: Verification extracts auth info from header or query, validates STS session tokens when `X-Amz-Security-Token` is present or looks up static credentials otherwise, rejects expired credentials, optionally authorizes streaming seed requests, checks presigned expiration, extracts signed headers using `externalHost` or forwarded host data for `host`, rejects unsigned `x-amz-*` headers except safe protocol/payload-hash exemptions, canonicalizes query/path/headers/payload, and compares HMAC-SHA256 signatures. It retries verification with `X-Forwarded-Prefix`, original escaped path, and decoded path for compatibility.

State and persistence behavior: Mostly stateless. It may read and reset request bodies for non-S3 services with missing payload hashes via `streamHashRequestBody` with a 10 MiB IAM body limit. STS validation constructs transient `Identity` and `Credential` values populated from session info, with principal-scoped accounts, policies, and claims.

Dependencies and integration points: Called by IAM auth dispatch and streaming upload seed verification. Integrates with STS/IAM session validation, request route parsing, S3 action permission checks, AWS host canonicalization behavior, policy variable claims, and POST policy verification.

Risks and test signals: High-risk areas are host canonicalization behind proxies, unsigned `x-amz-*` header injection on presigned URLs, clock-skew/expiry rules, body hashing limits for IAM/S3Tables services, session-token access-key mismatches, and S3 key path encoding. Tests cover S3Tables payload hashing, empty signed-header rejection, forwarded prefix/path behavior, host extraction including IPv6/default ports/external URL, STS authorization, and unsigned header rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_sts_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_sts_test.go

Purpose: Tests STS session identity construction and IAM authorization routing for SigV4 and streaming uploads.

Important APIs, types, and functions: Defines `MockIAMIntegration` implementing authentication, authorization, trust-policy validation, and session-token validation. Tests exercise `validateSTSSessionToken`, `VerifyActionPermission`, and HTTP-method-to-action logic.

Control flow and state: `TestValidateSTSSessionTokenAssignsDistinctAccount` validates that STS sessions own resources under the OIDC subject or assumed-role user rather than shared admin. The authorization tests build STS-like identities with empty `Actions`, optionally attach session tokens, and assert `VerifyActionPermission` calls IAM integration or denies without it. Streaming upload tests verify write authorization for STS identities with `STREAMING-AWS4-HMAC-SHA256-PAYLOAD`.

State and persistence behavior: Uses mock session info and in-memory identity objects only. `authCalled` tracks whether the mock authorization path was invoked.

Dependencies and integration points: Depends on `sts.SessionInfo`, Gorilla mux route vars, S3 constants/errors, and `testify`. It directly tests behavior implemented across `auth_credentials.go` and `auth_signature_v4.go`.

Risks and test signals: Prevents STS sessions from inheriting admin ownership or being evaluated through legacy `CanDo`. It also pins the requirement that streaming seed-signature permission checks use IAM authorization for session-token identities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_sts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_test.go

Purpose: Unit tests for SigV4 parsing, payload hashing, forwarded-prefix joining, host extraction, and signed header canonicalization.

Important APIs, types, and functions: Exercises `extractV4AuthInfoFromHeader`, `parseSignedHeader`, `extractV4AuthInfoFromQuery`, `buildPathWithForwardedPrefix`, `extractHostHeader`, `extractSignedHeaders`, and `getCanonicalHeaders`.

Control flow and state: Tests compare S3 vs non-S3 services for auto body hashing; reject empty signed-header names in Authorization and presigned query paths; verify forwarded prefix joining preserves double slashes and trailing slash S3 key semantics; and run a large table of host extraction cases across forwarded host/port/proto, external host override, IPv6, default ports, and misaligned proxy ports.

State and persistence behavior: No persistent state. Request bodies are in-memory readers; host extraction uses mock requests.

Dependencies and integration points: Tightly coupled to AWS SDK host sanitization expectations used by `auth_security_test.go` and `auth_proxy_integration_test.go`.

Risks and test signals: These tests protect compatibility with S3 clients behind proxies and prevent malformed signed-header lists from silently changing canonical requests. They do not independently verify full signatures except through sibling integration/security tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_unsigned_headers_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_unsigned_headers_test.go

Purpose: Security tests ensuring SigV4 requests cannot carry unsigned `x-amz-*` headers that downstream S3 handlers persist or honor.

Important APIs, types, and functions: `TestVerifySignedHeadersCoverage_Unit` tests `verifySignedHeadersCoverage` directly. `TestPresignedPutRejectsUnsignedTagging`, `TestPresignedPutAcceptsSignedTagging`, and `TestPresignedPutRejectsUnsignedMetadataHeaders` exercise full `reqSignatureV4Verify`. `preSignV4WithHeaders` constructs presigned URLs with custom `SignedHeaders`.

Control flow and state: Unit cases verify allowed unsigned non-amz headers, accepted signed amz headers, rejected unsigned tagging/metadata/ACL/storage/SSE/object-lock/security-token headers, payload-hash exemptions, presigned protocol-header exemptions, and case-insensitive matching. Full-path tests generate presigned PUTs, append dangerous headers after signing, and expect `ErrSignatureDoesNotMatch`; signed tagging is accepted.

State and persistence behavior: Uses test IAM helpers and transient requests. No persistent state.

Dependencies and integration points: Depends on SigV4 signing helpers from other tests, `newTestIAM`, `newTestRequest`, and the verifier's header coverage function.

Risks and test signals: Protects against presigned URL privilege expansion where a URL holder adds metadata, ACL, tagging, encryption, object-lock, redirect, or grant headers not covered by the signature. The explicit `x-amz-security-token` rejection prevents session-token injection on presigned requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_unsigned_headers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_identity_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_identity_test.go

Purpose: Regression and integration tests for STS identity fields needed by IAM authorization and policy variable substitution.

Important APIs, types, and functions: Tests use `setupTestSTSService`, `newTestIdentity`, `sts.NewSTSSessionClaims`, `sts.NewTokenGenerator`, `validateSTSSessionToken`, `Identity.CanDo`, and `SetIAMIntegration`.

Control flow and state: Tests generate STS JWT session tokens with policy names, role info, and request-context claims, validate them with the STS service, and confirm the resulting S3 identity has empty legacy `Actions`, populated `PolicyNames`, `PrincipalArn`, and `Claims`. They also compare identities with and without policy names and verify `CanDo` path construction for wildcard legacy actions.

State and persistence behavior: STS service and IAM manager are in-memory; generated JWTs carry session claims and expiration. The tests model how `validateSTSSessionToken` builds transient request identities.

Dependencies and integration points: Depends on `weed/iam/sts`, `S3IAMIntegration`, IAM credential construction, and S3 authorization semantics from `auth_credentials.go`.

Risks and test signals: Prevents STS identities from being denied because policy names were lost, and ensures request-context claims survive into policy evaluation for substitutions such as JWT user attributes. It also protects legacy wildcard path concatenation for bucket/object actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_identity_test.go -->
