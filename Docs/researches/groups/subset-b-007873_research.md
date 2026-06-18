# subset-b-007873 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_middleware.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_middleware.go

## Purpose
`s3_iam_middleware.go` connects the SeaweedFS S3 API to the newer IAM/STS/OIDC stack. It authenticates bearer JWTs, converts validated STS or external OIDC identities into S3 `IAMIdentity` values, extracts request context for policy conditions, and sends authorization checks to `integration.IAMManager`.

## Important APIs, Types, and Functions
Important types are `IAMIntegration`, `IAMManagerProvider`, `S3IAMIntegration`, `IAMIdentity`, and `OIDCIdentity`. `NewS3IAMIntegration` wires an `IAMManager` and its STS service. `AuthenticateJWT` validates bearer tokens, `AuthorizeAction` builds an `integration.ActionRequest`, `ValidateSessionToken` and `ValidateTrustPolicyForPrincipal` delegate to IAM services, and `DefaultAllow` exposes IAM's default behavior.

Key helpers are `buildS3ResourceArn`, `extractRequestContext`, `extractSourceIP`, `isPrivateIP`, `ParseUnverifiedJWTToken`, `validateExternalOIDCToken`, `selectPrimaryRole`, and `isSTSIssuer`. `SetIAMIntegration` attaches the integration to `S3ApiServer`.

## Control Flow
`AuthenticateJWT` rejects disabled IAM, missing bearer headers, empty tokens, and obvious invalid token strings. It parses the JWT without verifying it only to read `iss`; exact issuer matching via `isSTSIssuer` routes STS tokens to `stsService.ValidateSessionToken`, while other issuers are validated through `ValidateWebIdentityToken` with a timeout. STS identities are built from trusted `SessionInfo`; OIDC identities are built from validated provider output and copied attributes, with `sub`, `role`, email, display name, and groups populated for policy variable use.

`AuthorizeAction` rejects missing principals, extracts policy condition context, special-cases list operations by setting `s3:prefix` and bucket-level resource ARNs, adds identity claims and `jwt:` aliases without overwriting request-derived keys, resolves the concrete S3 action, and asks `IAMManager.IsActionAllowed`.

## State and Persistence Behavior
This file keeps only process memory state: the integration holds `iamManager`, `stsService`, filer address, and enabled flag. Private network CIDRs are initialized once in `privateNetworks`. No on-disk state is written here; identity claims and request context exist only for an authorization decision.

## Dependencies and Integration Points
The file depends on `github.com/golang-jwt/jwt/v5`, SeaweedFS IAM integration, OIDC provider identity types, STS session validation, S3 action/error constants, and HTTP request state. It integrates with `IdentityAccessManagement.authenticateJWTWithIAM` and `authorizeWithIAM`, with `ResolveS3Action`, and with IAM policy evaluation.

## Risks and Edge Cases
The unverified JWT parse is intentionally used only for routing, but any future use of those claims for authorization would be a security regression. `extractSourceIP` trusts forwarding headers only from private or local `RemoteAddr`; deployments using public CDN/proxy addresses need external controls because there is no configurable trusted proxy CIDR list here. OIDC role selection simply chooses the first role returned by the provider, so provider ordering becomes security-critical. `requestTime` may be nil unless upstream middleware sets it. `AuthorizeAction` compares `action == "List"` instead of using a typed constant, so action naming changes can break list-prefix semantics.

## Test Signals
Related tests cover exact STS issuer matching, first-role selection, JWT auth/authorization flows, invalid token handling, request context extraction, and IP-based policy enforcement. High-value additions would cover list-prefix IAM conditions, `jwt:` claim alias precedence, public-proxy header spoofing, and OIDC identities without roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_middleware.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_role_selection_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_role_selection_test.go

## Purpose
This unit test documents the role-selection contract for external OIDC identities in the S3 IAM bridge. It verifies that `S3IAMIntegration.selectPrimaryRole` is intentionally simple: return the first role in the provider-supplied role list.

## Important APIs, Types, and Functions
The only production API under test is `selectPrimaryRole(roles []string, externalIdentity *providers.ExternalIdentity) string`. The test constructs lightweight `providers.ExternalIdentity` values with empty attributes and uses `stretchr/testify/assert`.

## Control Flow
The test creates an empty `S3IAMIntegration`, then runs subtests for empty roles, single role, multiple roles, order sensitivity, and enterprise-looking role names. Each subtest invokes `selectPrimaryRole` directly and asserts the returned string. The `ExternalIdentity` parameter is currently not used by the implementation, and the test implicitly locks in that behavior.

## State and Persistence Behavior
No persistent state is touched. All state is local to the test process. There is no IAM manager setup, provider registration, network I/O, or filer interaction.

## Dependencies and Integration Points
The test depends on `providers.ExternalIdentity` from the IAM provider package and on `selectPrimaryRole` in `s3_iam_middleware.go`. It protects the behavior used by `validateExternalOIDCToken` after it parses the provider's comma-separated `roles` attribute.

## Risks and Edge Cases
Because the tested behavior trusts provider order, policy safety depends on the upstream provider returning roles in priority order. The test does not cover whitespace trimming or comma splitting; that is done before `selectPrimaryRole`. It also does not verify trust-policy authorization for the selected role.

## Test Signals
Passing tests signal that empty role lists return `""`, one-role lists return that role, and reordered role lists produce different selected roles. A regression to privilege-based sorting, admin preference, or attribute-driven selection would intentionally fail these tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_role_selection_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_jwt_auth_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_jwt_auth_test.go

## Purpose
`s3_jwt_auth_test.go` exercises the S3 IAM JWT authentication and authorization path using in-memory IAM components. It verifies STS-issued JWT acceptance, policy-driven S3 permissions, invalid token rejection, request context extraction, and IP-address condition enforcement.

## Important APIs, Types, and Functions
Test helpers include `createTestJWTAuth`, `setupTestIAMManager`, `setupTestIdentityProviders`, `setupIAMWithIntegration`, `setupTestReadOnlyRole`, `setupTestAdminRole`, `setupTestIPRestrictedRole`, `testJWTAuthentication`, and `testJWTAuthorizationWithRole`. The main tests are `TestJWTAuthenticationFlow`, `TestJWTTokenValidation`, `TestRequestContextExtraction`, and `TestIPBasedPolicyEnforcement`.

## Control Flow
The IAM manager is initialized with in-memory policy and role stores plus STS config. Mock OIDC and LDAP providers are registered. Role setup helpers create trust policies for web identity assumption and attach S3 policies. Tests create a signed external JWT, call `AssumeRoleWithWebIdentity` to obtain an STS session token, authenticate it through `IdentityAccessManagement.authenticateJWTWithIAM`, and authorize representative S3 actions through `authorizeWithIAM`.

The IP-condition test synthesizes requests with `X-Forwarded-For` and localhost `RemoteAddr`, then verifies the extracted `aws:SourceIp` drives policy allow/deny decisions.

## State and Persistence Behavior
All state is in-memory: policies, roles, identity providers, STS config, and JWT sessions. No filer, disk, or external network is required. Request headers carry the session token and synthesized principal header in authorization tests.

## Dependencies and Integration Points
The test covers interaction between S3 IAM middleware, `integration.IAMManager`, mock OIDC/LDAP providers, STS session issuance/validation, `policy.PolicyDocument`, S3 constants, and S3 error codes.

## Risks and Edge Cases
The helper `testJWTAuthorizationWithRole` manually sets a principal header using a test role name, so it verifies authorization mechanics but not every real request path that derives principals. The invalid-token cases are coarse and do not cover malformed JWTs with plausible length, wrong signature, missing issuer, or OIDC validation failures. IP tests rely on private `RemoteAddr` to trust forwarded headers, matching the production heuristic.

## Test Signals
Passing tests demonstrate read-only roles cannot write, admin roles can write/delete buckets, invalid/empty tokens fail, source IP and user-agent context extraction works, and IP-restricted policies distinguish office/internal ranges from external IPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_jwt_auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_list_parts_action_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_list_parts_action_test.go

## Purpose
This test file documents and verifies S3 action resolution for multipart `ListParts` requests. It exists to prevent GET requests with an `uploadId` query parameter from being authorized as ordinary `s3:GetObject` reads.

## Important APIs, Types, and Functions
All tests call `ResolveS3Action(req, fallbackAction, bucket, objectKey)`. Test groups are `TestListPartsActionMapping`, `TestListPartsActionMappingSecurityScenarios`, and `TestListPartsActionRealWorldScenarios`.

## Control Flow
Each test builds a minimal `http.Request` with method, URL path, and query values. It passes a fallback S3 action constant and asserts the resolved IAM action string. Cases distinguish plain GET, GET with `uploadId`, GET with `versionId`, GET ACL, POST with `uploads`, multipart upload workflow steps, and multiple realistic upload ID formats.

## State and Persistence Behavior
The tests use no persistent state. Requests are constructed in memory and there is no server, filer, IAM manager, or object metadata.

## Dependencies and Integration Points
The file depends on `ResolveS3Action` from the S3 authorization layer and `s3_constants` action constants. It protects integration with IAM policy evaluation because the resolved action is sent to `integration.ActionRequest.Action`.

## Risks and Edge Cases
The test confirms the presence of `uploadId` changes GET semantics, including with additional multipart pagination parameters. It does not test duplicate query parameters, case variations in `uploadId`, or actual handler authorization with a policy engine. Since AWS query names are case-sensitive, that is likely acceptable.

## Test Signals
Passing tests signal that `GET ?uploadId=...` maps to `s3:ListMultipartUploadParts`, plain GET maps to `s3:GetObject`, versioned GET maps to `s3:GetObjectVersion`, ACL GET maps to `s3:GetObjectAcl`, and multipart create/upload/complete/list steps remain distinct for fine-grained permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_list_parts_action_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_metadata_util.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_metadata_util.go

## Purpose
`s3_metadata_util.go` centralizes parsing of upload/copy request headers into SeaweedFS filer metadata. It captures S3 storage class, standard HTTP metadata, object tags, user metadata, SSE-C metadata, and ACL owner/grant markers for storage in `Entry.Extended`.

## Important APIs, Types, and Functions
The file exposes `ParseS3Metadata(r *http.Request, existing map[string][]byte, isReplace bool) (map[string][]byte, s3err.ErrorCode)`.

## Control Flow
The function creates a new metadata map, copies existing metadata unless the caller requested replacement, then selectively records `x-amz-storage-class`, `Content-Encoding`, `Cache-Control`, `Content-Disposition`, `Content-Language`, and `Expires`. It intentionally does not persist response override headers such as response content disposition. Object tags are parsed with `url.ParseQuery`, URL-decoded, checked for duplicate keys, and stored as `x-amz-tagging-<key>`. User metadata headers with the S3 metadata prefix are stored under their canonical Go header name with multiple values comma-joined. SSE-C algorithm and key MD5 are stored, but the customer key itself is not. ACL owner and grants are copied from SeaweedFS extension headers when present.

## State and Persistence Behavior
The returned map is intended for persistence in filer entry extended metadata. Existing metadata can be preserved across metadata updates when `isReplace` is false. Tag and ACL values become durable object metadata once written by the caller.

## Dependencies and Integration Points
The function depends on S3 constants, S3 error codes, Go HTTP header canonicalization, URL query parsing, and glog warnings. It feeds object PUT, copy, and multipart-create paths that later need metadata, ACL, tags, and SSE headers.

## Risks and Edge Cases
Header names are stored in canonicalized form for user metadata, which may matter for consumers expecting lower-case keys. Tag storage prefixes each key into separate metadata entries rather than preserving original tag order. Duplicate tag detection depends on `url.ParseQuery` grouping repeated keys. SSE-C stores only algorithm and MD5 here; IV storage is handled separately.

## Test Signals
Useful tests should cover replacement versus merge behavior, invalid or duplicate tags returning `ErrInvalidTag`, URL-decoded tag values, duplicate user metadata header values, non-persistence of response override headers, and SSE-C/ACL metadata preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_metadata_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_objectlock/object_lock_check.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_objectlock/object_lock_check.go

## Purpose
`object_lock_check.go` provides shared object-lock checks used before destructive bucket operations. It detects active legal holds and retention periods on current objects and versions by scanning filer entries.

## Important APIs, Types, and Functions
Public helpers are `EntryHasActiveLock`, `HasObjectsWithActiveLocks`, `IsObjectLockEnabled`, and `CheckBucketForLockedObjects`. Internal helpers are `paginateEntries`, `recursivelyCheckLocksWithClient`, and `checkVersionsForLocksWithClient`.

## Control Flow
`EntryHasActiveLock` checks `Entry.Extended` for a legal hold set to `ON` or for governance/compliance retention whose retain-until timestamp is in the future. Unparseable retention dates fail safe as locked. `HasObjectsWithActiveLocks` starts a recursive scan at a bucket path. `paginateEntries` streams directory entries with a 10,000 entry page limit, tracks the last name, skips invalid names that could cause path traversal, and allows callback-controlled early stop. Recursion skips multipart upload scratch folders, descends ordinary directories, and gives `.versions` folders to a version-specific scanner. `CheckBucketForLockedObjects` first looks up the bucket entry, returns early if object lock is disabled, then scans for active locks and returns an error if any exist.

## State and Persistence Behavior
The file reads bucket and object metadata from the filer but does not mutate it. It treats `Entry.Extended` object-lock fields as durable source of truth and uses current wall-clock time for retention comparisons.

## Dependencies and Integration Points
It integrates with `filer_pb.SeaweedFilerClient` listing and lookup RPCs, S3 object-lock constants, admin UI, shell commands, and S3 bucket deletion logic.

## Risks and Edge Cases
The retention date parser expects Unix seconds in metadata; any other format is treated as locked, which is safe but may block deletion after metadata corruption. Pagination relies on entries being returned in stable name order. The scan can be expensive on large buckets, though it exits as soon as a lock is found. Invalid entry names are skipped, preventing traversal but potentially hiding malformed locked entries.

## Test Signals
Tests should cover legal hold case/whitespace normalization, governance and compliance retention before/after current time, malformed retain-until values, version folder scanning, multipart folder skipping, invalid name skipping, object-lock-disabled buckets, and propagation of filer list/lookup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_objectlock/object_lock_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_c.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_c.go

## Purpose
`s3_sse_c.go` implements SSE-C support for customer-provided AES-256 keys. It parses and validates request headers, creates AES-CTR encrypt/decrypt readers, supports offset-aware CTR streams, decides copy strategies, and maps SSE-C errors to S3 errors.

## Important APIs, Types, and Functions
Core types are `SSECustomerKey`, `SSECCopyStrategy`, and `decryptReaderCloser`. Key functions include `IsSSECRequest`, `IsSSECEncrypted`, `ParseSSECHeaders`, `ParseSSECCopySourceHeaders`, `CreateSSECEncryptedReader`, `CreateSSECDecryptedReader`, `CreateSSECEncryptedReaderWithOffset`, `CreateSSECDecryptedReaderWithOffset`, `GetSourceSSECInfo`, `CanDirectCopySSEC`, `DetermineSSECCopyStrategy`, `createCTRStreamWithOffset`, and `MapSSECErrorToS3Error`.

## Control Flow
SSE-C header parsing requires algorithm, key, and key-MD5 to appear together. The algorithm must be `AES256`; the key must base64-decode to 32 bytes; the provided MD5 must match the base64 MD5 of the raw key. Encryption creates an AES block with the customer key, generates a random 16-byte IV, and wraps the source reader in a CTR stream. Decryption validates the metadata IV, creates the same CTR stream, and preserves close behavior when the input reader is an `io.Closer`. Offset variants derive an adjusted IV and discard intra-block keystream bytes through `calculateIVWithOffset`.

## State and Persistence Behavior
The raw customer key is never stored by this file. Persistent metadata elsewhere stores the SSE-C algorithm, key MD5, and IV. Copy decisions use source metadata and request-provided source/destination keys but do not mutate state.

## Dependencies and Integration Points
The file depends on AES/CTR, MD5, base64, S3 constants/errors, and shared IV validation/offset helpers. It integrates with object PUT/GET/copy paths, metadata helpers, and multipart chunk encryption.

## Risks and Edge Cases
AES-CTR provides confidentiality but not authentication; the broader SSE implementation mitigates key/IV confusion with commitments only for some paths. Key MD5 is an identifier/checksum, not a secret. `IsSSECRequest` treats KMS headers as mutually exclusive and ignores malformed mixes by returning false, so caller validation must catch invalid combinations. Direct copy is allowed only when source and destination key MD5s match the stored source MD5; collision risk is theoretical but MD5 is still not collision-resistant.

## Test Signals
High-value tests include complete/missing header combinations, wrong algorithm, wrong key length, MD5 mismatch, encrypt/decrypt round trips, IV validation, offset decrypt reads, copy strategy errors, and error-to-S3-code mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_c.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_ctr_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_ctr_test.go

## Purpose
This test file validates the shared AES-CTR IV offset logic used by SSE-C, SSE-KMS, and SSE-S3 range and multipart paths. It specifically guards non-block-aligned range decryption.

## Important APIs, Types, and Functions
The production API under test is `calculateIVWithOffset(baseIV []byte, offset int64) ([]byte, int)`. Tests are `TestCalculateIVWithOffset`, `TestCTRDecryptionWithNonBlockAlignedOffset`, `TestCTRRangeRequestSimulation`, and `TestCTRDecryptionWithIOReader`.

## Control Flow
Tests generate keys, IVs, and deterministic plaintext, encrypt full buffers with AES-CTR, then simulate reads from many offsets. For each offset, they derive an adjusted IV and skip value, start ciphertext reads at the block-aligned offset, decrypt, discard skip bytes, and compare with the original plaintext slice.

## State and Persistence Behavior
There is no persistent state. Random keys/IVs and plaintext/ciphertext buffers live only within the test process.

## Dependencies and Integration Points
The test depends on Go AES/CTR and the shared helper in `s3_sse_utils.go`. It protects S3 range-request behavior and multipart chunk decryption in all server-side encryption modes that use CTR.

## Risks and Edge Cases
The tests cover positive offsets but not negative offsets or IV counter overflow. Subtest names derived from runes are not very descriptive for large offsets, but failures still include offset values. The tests model the caller-side requirement that ciphertext fetches begin at the block boundary, not at the requested byte offset.

## Test Signals
Passing tests signal that skip equals `offset % 16`, block-aligned offsets need no skip, non-aligned offsets decrypt correctly after discarding intra-block bytes, and range reads across block boundaries match plaintext exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_ctr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms.go

## Purpose
`s3_sse_kms.go` implements SSE-KMS envelope encryption for S3 objects. It generates/decrypts data keys through the configured KMS provider, encrypts object data with AES-CTR, serializes KMS metadata, supports bucket-key caching, handles multipart offsets, detects encryption state, and selects copy strategies.

## Important APIs, Types, and Functions
Primary types include `SSEKMSKey`, `SSEKMSMetadata`, `SSECMetadata`, `SSEKMSCopyStrategy`, `UnifiedCopyStrategy`, and `EncryptionState`. Important functions include `CreateSSEKMSEncryptedReaderWithBucketKey`, `CreateSSEKMSEncryptedReaderWithBaseIVAndOffset`, `CreateSSEKMSEncryptedReaderForBucket`, `CreateSSEKMSDecryptedReader`, `SerializeSSEKMSMetadata`, `DeserializeSSEKMSMetadata`, `AddSSEKMSResponseHeaders`, `IsSSEKMSRequest`, `IsSSEKMSEncrypted`, `MapKMSErrorToS3Error`, `DetermineSSEKMSCopyStrategy`, `ParseSSEKMSCopyHeaders`, `DetermineUnifiedCopyStrategy`, and entry-aware encryption detectors.

## Control Flow
Encryption requests validate/generate KMS data keys, create AES-CTR streams, generate IVs or derive offset IVs, and return `SSEKMSKey` metadata containing key ID, encrypted data key, encryption context, bucket-key flag, IV, chunk offset, and HMAC key commitment. Decryption calls KMS `Decrypt`, clears plaintext key material after use, verifies returned key ID, verifies the stored commitment, validates IV length, derives chunk IVs when needed, and returns a decrypting reader. Metadata serialization writes JSON with base64 binary fields and optional commitment; deserialization reverses it and is lenient about missing algorithm for compatibility.

## State and Persistence Behavior
Object metadata persists encrypted data keys, IVs, encryption context, bucket-key flags, offsets, and commitments. Plaintext data keys are cleared from memory after use. Bucket-key support can cache KMS data keys in per-bucket caches with TTL, reached through bucket configuration cache.

## Dependencies and Integration Points
The file depends on the global SeaweedFS KMS provider, filer entry/chunk metadata, S3 constants/errors, bucket config caches, shared commitment/IV helpers, and copy/object handlers. `DetectEncryptionStateWithEntry` unifies SSE-C, SSE-KMS, and SSE-S3 state for copy decisions.

## Risks and Edge Cases
AES-CTR requires unique key/IV pairs; offset helpers and commitments reduce reuse/tamper risk, but correctness depends on storing base versus derived IV consistently. `CleanupAllBucketKMSCaches` logs using `len(s3a.bucketConfigCache.cache)` after checking only inside the if block, so nil cache handling deserves review. Some validation differs between `parseEncryptionContext` and `generateKMSDataKey` length limits. Direct copy by key ID may be unsafe if aliases resolve to different concrete keys or if source metadata lacks resolved key IDs.

## Test Signals
Useful signals include KMS key ID validation, metadata round trips, KMS error mapping, commitment verification failures, bucket-key fallback, range/multipart offset decryption, copy strategy decisions, and mixed encryption-state detection for source and destination objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms_utils.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms_utils.go

## Purpose
`s3_sse_kms_utils.go` contains shared helper logic for SSE-KMS data-key generation, validation, AES block creation, plaintext clearing, and construction of commitment-bearing `SSEKMSKey` metadata.

## Important APIs, Types, and Functions
The file defines `KMSDataKeyResult` and functions `generateKMSDataKey`, `clearKMSDataKey`, and `createSSEKMSKey`.

## Control Flow
`generateKMSDataKey` validates KMS key ID format and optional encryption context, obtains the global KMS provider, requests an AES-256 data key, and constructs an AES cipher from the plaintext key. If cipher creation fails, plaintext is cleared before returning. `clearKMSDataKey` zeroes the plaintext in a result. `createSSEKMSKey` packages KMS response fields plus encryption context, bucket-key flag, IV, chunk offset, and HMAC commitment over plaintext key, IV, and KMS algorithm.

## State and Persistence Behavior
The helper itself keeps no persistent state. It receives sensitive plaintext key material from KMS and expects callers to defer `clearKMSDataKey`. The returned `SSEKMSKey` carries persistent metadata fields, but not plaintext key bytes.

## Dependencies and Integration Points
The file depends on the global `kms` package, AES, shared key-ID and commitment validators, and `s3_constants`. It is used by multiple SSE-KMS encryption creation paths to keep metadata and commitment behavior consistent.

## Risks and Edge Cases
`generateKMSDataKey` uses `context.Background()` rather than request context, so KMS calls are not request-cancellable here. Context validation allows up to 2048 chars in this helper while `parseEncryptionContext` elsewhere uses 256, which may surprise callers. Global KMS provider absence returns an ordinary error that caller must map to S3 response codes.

## Test Signals
Tests should cover invalid key IDs, invalid context keys/values/counts, no global KMS provider, KMS generate failures, AES cipher failure with plaintext clearing, and commitment presence in `createSSEKMSKey`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_metadata.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_metadata.go

## Purpose
`s3_sse_metadata.go` provides small metadata helpers for SSE-C IV storage and retrieval. It normalizes the current raw-IV format while preserving backward compatibility with a legacy base64-encoded IV format.

## Important APIs, Types, and Functions
The file exposes `StoreSSECIVInMetadata(metadata map[string][]byte, iv []byte)` and `GetSSECIVFromMetadata(metadata map[string][]byte) ([]byte, error)`.

## Control Flow
`StoreSSECIVInMetadata` writes non-empty IV bytes directly to the `SeaweedFSSSEIV` metadata key. `GetSSECIVFromMetadata` reads that key, returns it directly if it is exactly 16 bytes, otherwise tries base64 decoding and validates the decoded value is 16 bytes. Missing or malformed metadata produces descriptive errors.

## State and Persistence Behavior
The helper mutates the caller-provided metadata map. The stored IV becomes durable when the object entry is persisted. The current canonical storage format is raw 16-byte IV, not base64 text.

## Dependencies and Integration Points
It depends on base64, S3 constants, and AES block size constants. It is used by SSE-C upload/copy/GET paths and aligns CopyObject behavior with `putToFiler` metadata format.

## Risks and Edge Cases
Legacy compatibility accepts any base64 string decoding to 16 bytes, even if the stored byte length is not exactly the normal 24-byte base64 length. That is permissive and useful for migration. Empty IVs are not stored, so callers must enforce IV generation before persistence.

## Test Signals
Tests should verify raw IV round trips, legacy base64 IV decode, missing metadata errors, invalid base64 errors, and wrong decoded length errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3.go

## Purpose
`s3_sse_s3.go` implements SSE-S3 server-managed encryption. It generates per-object or per-chunk data encryption keys, encrypts object data with AES-CTR, stores encrypted DEKs in metadata under a key-encryption key, manages KEK loading/configuration/migration, and initializes the global SSE-S3 key manager.

## Important APIs, Types, and Functions
Important types are `SSES3Key`, `SSES3KeyManager`, and `KeyManagerFilerClient`. Important functions include `IsSSES3RequestInternal`, `IsSSES3EncryptedInternal`, `GenerateSSES3Key`, `CreateSSES3EncryptedReader`, `CreateSSES3DecryptedReader`, `SerializeSSES3Metadata`, `DeserializeSSES3Metadata`, `NewSSES3KeyManager`, `SetKEKPassphrase`, `InitializeWithFiler`, `loadSuperKeyFromFiler`, `wrapKEK`, `unwrapKEK`, `deriveWrappingKey`, `deriveKeyFromSecret`, `encryptKeyWithSuperKey`, `decryptKeyWithSuperKey`, `GetMasterKey`, `InitializeGlobalSSES3KeyManager`, `GetSSES3IV`, and `CreateSSES3EncryptedReaderWithBaseIV`.

## Control Flow
Encryption generates a 32-byte DEK and random IV, encrypts data using AES-CTR, and serializes metadata by encrypting the DEK with the manager's KEK using AES-GCM. Metadata includes algorithm, key ID, encrypted DEK, nonce, optional IV, and key commitment. Decryption deserializes metadata, decrypts the DEK through the key manager, validates IV and commitment, and returns a decrypting reader.

`InitializeWithFiler` resolves the KEK from config or filer in priority order: hex `s3.sse.kek`, derived `s3.sse.key`, existing filer KEK, or disabled SSE-S3. It refuses conflicting config, checks config KEK against existing filer KEK when reachable, refuses derived keys while a filer KEK exists, and migrates passphrase-wrapped legacy formats toward salted v2 wrapping. The global initializer wires a `wdclient.FilerClient` adapter and reads the KEK passphrase from Viper or environment.

## State and Persistence Behavior
The key manager stores the active KEK in memory under a mutex. Filer-backed KEKs live at `/etc/s3/sse_kek`, possibly plaintext hex for legacy deployments or passphrase-wrapped AES-GCM payloads. Object metadata stores encrypted DEKs and IV/commitment data. No plaintext DEKs are stored persistently.

## Dependencies and Integration Points
The file depends on AES/CTR/GCM, HKDF-SHA256, Viper config helpers, filer protobuf clients, wdclient, gRPC, S3 constants, and shared validation/commitment helpers. It integrates with S3 PUT/GET/copy handlers and with STS via `GetMasterKey`.

## Risks and Edge Cases
`GenerateSSES3Key` uses `math/rand.Int63` for key IDs, which are identifiers not keys but can collide. SSE-S3 is disabled silently at init when no KEK exists; first encrypt/decrypt returns an error. Legacy plaintext KEK support is upgrade-friendly but sensitive; warning visibility matters. `IsSSES3EncryptedInternal` requires both algorithm header and encrypted key metadata, preventing stale-header false positives. Correct multipart decryption depends on per-chunk metadata validation and IV handling.

## Test Signals
Tests cover inline and chunked end-to-end flows, per-chunk key decryption, invalid IV failure before fetch, passphrase wrapping round trips and random salts, CTR offset behavior, and type detection. Additional coverage should exercise config/filer KEK conflict handling and disabled SSE-S3 errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_integration_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_integration_test.go

## Purpose
This integration-style test file validates critical SSE-S3 encryption/decryption flows without standing up the full S3 server and filer. It focuses on inline IV retrieval, chunk metadata, primary SSE type detection, and multipart readers that decrypt each chunk with its own metadata.

## Important APIs, Types, and Functions
Tests cover `GenerateSSES3Key`, `CreateSSES3EncryptedReader`, `SerializeSSES3Metadata`, `DeserializeSSES3Metadata`, `CreateSSES3DecryptedReader`, `detectPrimarySSEType`, and `buildMultipartSSES3Reader`. Helpers include `initSSES3KeyManagerForTest` and `encryptSSES3Part`.

## Control Flow
Tests reset the global SSE-S3 key manager and seed a deterministic super key. Small-file tests encrypt data, store IV in object-level metadata, deserialize the key, retrieve the IV, decrypt, and compare plaintext. Chunked tests create per-chunk metadata and verify each chunk decrypts. Type detection tests synthesize entries for inline SSE-S3, chunked SSE-S3, and SSE-KMS. Multipart reader tests pass chunks out of order, use fetch callbacks for encrypted chunk bytes, verify offset-sorted decrypted output, and assert the caller's chunk slice is not mutated.

## State and Persistence Behavior
State is local and in-memory. Mock `filer_pb.Entry` and `FileChunk` values represent persisted object metadata and chunk SSE metadata. The global key manager is reset with `t.Cleanup` to avoid cross-test pollution.

## Dependencies and Integration Points
The tests depend on filer protobuf entry/chunk structures, S3 metadata constants, the global SSE-S3 key manager, and the multipart reader helper used by GET paths.

## Risks and Edge Cases
These tests intentionally avoid full HTTP/filer integration, so they do not verify request handlers, actual volume fetches, or metadata persistence RPCs. They do verify an important resource contract: malformed chunk metadata must be detected before opening any chunk reader. Invalid IV tests manually craft metadata because serializers reject bad IVs.

## Test Signals
Passing tests signal that inline files carry object-level IVs, chunked files carry per-chunk IVs, multipart readers sort by offset without mutating input, per-chunk DEKs/IVs are honored, invalid IVs return clear errors, and malformed chunks fail before any fetch callback is called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_kek_passphrase_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_kek_passphrase_test.go

## Purpose
This test file verifies passphrase-based KEK wrapping for SSE-S3. It locks in that `SetKEKPassphrase` enables encrypted KEK round trips, random salts prevent identical wrapped output, and no-passphrase mode remains the legacy plaintext-hex path.

## Important APIs, Types, and Functions
Tests call `NewSSES3KeyManager`, `SetKEKPassphrase`, `wrapKEK`, and `unwrapKEK`. Main tests are `TestSetKEKPassphraseEnablesEncryptedRoundTrip`, `TestSetKEKPassphraseDifferentInstancesNoCollision`, and `TestNoPassphraseKeepsLegacyHexDecodePath`.

## Control Flow
The first test sets a passphrase, wraps a deterministic 32-byte KEK, unwraps it, asserts v2 format detection, and compares bytes. The second creates two managers with the same passphrase, wraps identical KEKs, asserts ciphertext differs due to random salt/nonce, then verifies each manager can unwrap its own output. The third verifies a default manager has no passphrase and that `wrapKEK` fails instead of producing output.

## State and Persistence Behavior
No filer state is written. The tests exercise only in-memory wrapping payloads that would normally be stored in `/etc/s3/sse_kek`.

## Dependencies and Integration Points
The tests cover the passphrase plumbing used by `InitializeGlobalSSES3KeyManager` and `loadSuperKeyFromFiler` migration paths. They indirectly verify HKDF-derived wrapping keys and AES-GCM wrapping.

## Risks and Edge Cases
The tests do not cover legacy v1 fixed-salt unwrapping, plaintext-to-wrapped migration, or failed filer updates. They also do not test wrong-passphrase unwrap failure. They are still a strong signal that passphrase setup reaches the key manager before wrapping is attempted.

## Test Signals
Passing tests mean v2 wrapped payloads self-roundtrip, same passphrase plus same KEK does not produce byte-identical payloads across instances, and wrapping without a passphrase fails explicitly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_kek_passphrase_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_multipart_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_multipart_test.go

## Purpose
This file tests SSE-S3 multipart encryption assumptions, especially per-chunk IV behavior and offset-derived IV calculation. It documents how single-part and multipart chunk views should decrypt.

## Important APIs, Types, and Functions
Tests directly use AES-CTR and `calculateIVWithOffset`. They create `filer_pb.FileChunk` values with `SSEType_SSE_S3` and optional `SseMetadata`.

## Control Flow
`TestSSES3MultipartChunkViewDecryption` simulates two multipart parts at different offsets, encrypts each with an offset-adjusted IV, and verifies decryption with the chunk IV. `TestSSES3SinglePartChunkViewDecryption` verifies single-part objects can decrypt with object-level IV and no per-chunk metadata. `TestSSES3IVOffsetCalculation` checks deterministic offset adjustment and skip values across part offsets. `TestSSES3ChunkMetadataDetection` verifies the condition for per-chunk metadata detection. `TestSSES3EncryptionConsistency` checks ordinary AES-CTR round trips with a fresh stream.

## State and Persistence Behavior
The tests do not persist state. Mock chunk metadata represents what would be stored in filer chunk records.

## Dependencies and Integration Points
The tests protect the shared IV offset helper and chunk metadata conventions consumed by SSE-S3 multipart upload and GET paths.

## Risks and Edge Cases
The tests use simulated encryption and not the production serialization/deserialization helpers for most cases. They do not verify malformed metadata handling, volume fetching, or mixed encrypted/unencrypted chunks. They do, however, pin down the distinction between object-level IVs for single-part objects and per-chunk IVs for multipart objects.

## Test Signals
Passing tests signal that non-zero part offsets produce different IVs, skip values are deterministic, chunks with SSE-S3 type plus metadata are treated as multipart encrypted chunks, and AES-CTR decryption with the selected IV reproduces plaintext.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_multipart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_test_utils_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_test_utils_test.go

## Purpose
This test utility file provides reusable helpers for SSE-C and SSE-KMS tests. It generates deterministic customer keys, configures request headers, sets up a local KMS provider, builds test metadata, and provides assertion helpers for response headers.

## Important APIs, Types, and Functions
Important test-only types are `TestKeyPair` and `TestSSEKMSKey`. Helpers include `GenerateTestSSECKey`, `SetupTestSSECHeaders`, `SetupTestSSECCopyHeaders`, `SetupTestKMS`, `SetupTestSSEKMSHeaders`, `CreateTestMetadata`, `CreateTestMetadataWithSSEC`, `CreateTestMetadataWithSSEKMS`, `CreateTestHTTPRequest`, `CreateTestHTTPResponse`, `SetupTestMuxVars`, `AssertSSECHeaders`, `AssertSSEKMSHeaders`, corrupted metadata creators, and `GenerateTestData`.

## Control Flow
SSE-C helpers derive a 32-byte deterministic key from a seed, base64-encode it, compute base64 MD5, and set the expected S3 request headers. KMS setup creates a local KMS provider, installs it globally, creates a test key, and returns cleanup that resets the global provider and closes it. Metadata helpers populate maps with the same keys production code expects.

## State and Persistence Behavior
Most helpers are in-memory. `SetupTestKMS` mutates global KMS provider state and must be paired with cleanup. No filesystem or filer persistence is used.

## Dependencies and Integration Points
The file depends on Gorilla mux, local KMS provider, KMS global provider, S3 constants, SSE serialization helpers, and Go HTTP test utilities. It supports many SSE tests by hiding repetitive setup.

## Risks and Edge Cases
Because helpers mutate global KMS state, tests using them must avoid parallel interference or always defer cleanup. `CreateTestMetadataWithSSEKMS` ignores serialization errors and stores both raw encrypted data key and serialized context, so malformed test keys could hide setup failures. The deterministic SSE-C keys are suitable for tests only.

## Test Signals
This file is not a test target by itself, but failures in dependent SSE-C/KMS tests often indicate these helpers no longer match production header or metadata conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_test_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_utils.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_utils.go

## Purpose
`s3_sse_utils.go` provides the shared AES-CTR IV offset calculation used by SSE-C, SSE-KMS, and SSE-S3. It enables safe range and multipart decryption without reusing the same counter block for different byte positions.

## Important APIs, Types, and Functions
The file exposes `calculateIVWithOffset(baseIV []byte, offset int64) ([]byte, int)`.

## Control Flow
The helper validates that `baseIV` is 16 bytes, copies it, computes `blockOffset = offset / 16` and `skip = offset % 16`, then adds the block offset to the last eight bytes of the IV as a big-endian counter. It returns the derived IV and the number of intra-block bytes the caller must discard from the CTR stream.

## State and Persistence Behavior
The helper is stateless and does not mutate the input IV. Derived IVs are often used transiently for range reads or stored in chunk metadata by higher-level SSE code depending on encryption mode.

## Dependencies and Integration Points
It depends only on glog and is called by SSE-C offset streams, SSE-KMS chunk/range handling, and SSE-S3 multipart helpers. The behavior is covered by CTR-specific tests.

## Risks and Edge Cases
Invalid IV length logs an error and returns the original IV with skip 0, leaving security/correctness enforcement to callers. Negative offsets are not explicitly rejected and would produce surprising arithmetic. Counter overflow beyond the last eight bytes is not surfaced as an error.

## Test Signals
`s3_sse_ctr_test.go` verifies skip calculations, block-aligned and non-block-aligned offsets, range simulations, and reader-based decryption behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_token_differentiation_test.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_token_differentiation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils.go

## Purpose
`s3_validation_utils.go` holds validation and commitment helpers shared by server-side encryption implementations. It can enforce HMAC key commitments, validate KMS key IDs, validate IV lengths, and validate SSE-KMS/SSE-S3 key structures.

## Important APIs, Types, and Functions
The file defines `RequireKeyCommitmentEnv`, the atomic `requireKeyCommitment`, and functions `SetRequireKeyCommitment`, `ComputeKeyCommitment`, `VerifyKeyCommitment`, `isValidKMSKeyID`, `ValidateIV`, `ValidateSSEKMSKey`, and `ValidateSSES3Key`.

## Control Flow
`init` reads `WEED_S3_REQUIRE_KEY_COMMITMENT` and enables strict mode for missing commitments. `ComputeKeyCommitment` returns HMAC-SHA256 keyed by encryption key over IV plus algorithm. `VerifyKeyCommitment` accepts missing commitments by default for legacy compatibility, rejects missing commitments in strict mode, and compares present commitments with `hmac.Equal`. KMS key validation rejects empty strings, whitespace, spaces, controls, and overlong IDs. SSE-S3 validation checks key size, algorithm, key ID, and optional IV length.

## State and Persistence Behavior
The only state is the process-wide atomic commitment requirement. Commitments themselves are stored by SSE metadata code in object or chunk metadata. This file does not persist anything directly.

## Dependencies and Integration Points
It depends on HMAC/SHA256, environment variables, S3 constants, and glog. It is used by SSE-C/KMS/S3 encryption and decryption paths to prevent IV/key/algorithm tampering and malformed metadata panics.

## Risks and Edge Cases
Default acceptance of missing commitments is compatibility-friendly but leaves legacy objects without downgrade protection unless strict mode is enabled after migration. `ValidateSSEKMSKey` only checks nil, leaving deeper field validation to serializers/KMS. KMS key validation is intentionally permissive and does not enforce ARN/UUID patterns despite regexes elsewhere.

## Test Signals
`s3_validation_utils_require_test.go` covers default missing-commitment acceptance, strict missing-commitment rejection, valid strict commitments, tampered key/IV/algorithm/commitment rejection, and runtime toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils_require_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils_require_test.go

## Purpose
This test file verifies runtime behavior of SSE key commitment enforcement. It ensures SeaweedFS can remain compatible with legacy objects by default while supporting a strict mode that rejects missing commitments.

## Important APIs, Types, and Functions
Tests cover `VerifyKeyCommitment`, `ComputeKeyCommitment`, `SetRequireKeyCommitment`, and the package-level `requireKeyCommitment` atomic.

## Control Flow
Each test snapshots the previous atomic value and restores it with `t.Cleanup`. Tests explicitly set strict mode on or off, then verify missing commitment acceptance/rejection, valid commitment acceptance, and rejection of tampered key, IV, algorithm, or commitment bytes. The final test checks that the public setter updates the atomic.

## State and Persistence Behavior
State is limited to the process-wide atomic flag. The tests do not read environment variables or write metadata; they exercise the verifier directly.

## Dependencies and Integration Points
The file protects commitment checks used during SSE-S3 and SSE-KMS decryption. It indirectly validates the compatibility contract documented by `WEED_S3_REQUIRE_KEY_COMMITMENT`.

## Risks and Edge Cases
The tests use short byte slices as HMAC inputs in some cases; that is fine for commitment logic but not full AES validation. They do not cover environment-variable initialization directly. They also do not test malformed but non-empty commitment lengths separately; HMAC comparison handles that by mismatch.

## Test Signals
Passing tests signal legacy acceptance when strict mode is disabled, missing-commitment rejection when enabled, valid HMAC acceptance, tamper detection across all bound inputs, and correct setter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils_require_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_acl_helper.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_acl_helper.go

## Purpose
`s3api_acl_helper.go` parses, validates, transforms, serializes, and renders S3 ACL grants. It supports ACL XML bodies, canned ACL headers, custom grant headers, account/email resolution, default private ACLs, and storing ACP data in filer entry metadata.

## Important APIs, Types, and Functions
Key types/functions are `AccountManager`, `ExtractAcl`, `ParseAndValidateAclHeadersOrElseDefault`, `ParseAndValidateAclHeaders`, `ParseAclHeaders`, `ParseCustomAclHeaders`, `ParseCustomAclHeader`, `ParseCannedAclHeader`, `ValidateAndTransferGrants`, `buildAccessControlList`, `GetAcpGrants`, and `AssembleEntryWithAcp`.

## Control Flow
`ExtractAcl` prefers an XML request body when present, verifies the ACP owner matches the immutable owner ID, and validates/transfers grants. If the body is empty, it parses headers. Header parsing gives custom grant headers priority for non-PutAcl operations, otherwise parses canned ACLs. Canned ACL handling creates grants for object writer, public/authenticated groups, log delivery, and bucket-owner read/full-control cases, with bucket-owner-preferred ownership able to switch owner ID during object upload. Validation resolves canonical IDs and email grantees through `AccountManager` and validates group URIs.

## State and Persistence Behavior
ACL owner and grants are stored in `filer_pb.Entry.Extended` under SeaweedFS extension keys. Grants are JSON-marshaled AWS SDK `s3.Grant` values. Missing grants render as a default owner full-control ACL for responses.

## Dependencies and Integration Points
The file depends on AWS SDK S3 ACL structs/XML utilities, SeaweedFS S3 constants/errors, filer protobuf entries, and request close utilities. It integrates with bucket/object ACL APIs and object metadata assembly.

## Risks and Edge Cases
`ParseCustomAclHeader` splits on `", "` and `"="`, so unusual spacing or quoted values containing `=` may fail or parse incorrectly. JSON unmarshal errors for quoted grant values are ignored, potentially producing empty IDs/emails that validation later catches if account lookup fails. `CannedAclAwsExecRead` is not implemented. Account manager correctness is security-critical for email-to-ID transfer.

## Test Signals
Tests should cover XML owner mismatch, body/header precedence, canned ACL variants, bucket-owner-preferred ownership, invalid group URIs, nonexistent canonical IDs/emails, default private ACL fallback, JSON persistence round trips, and malformed custom grant headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_acl_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_acp.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_acp.go

## Purpose
`s3api_acp.go` contains small access-control-policy helpers for account identification and bucket ownership checks. It determines requester account IDs from headers and enforces bucket-owner-only operations unless the requester is an admin.

## Important APIs, Types, and Functions
The file defines `getAccountId(r *http.Request) string` and the method `(*S3ApiServer).checkAccessByOwnership(r *http.Request, bucket string) s3err.ErrorCode`.

## Control Flow
`getAccountId` reads the SeaweedFS/S3 account ID header and falls back to anonymous account ID when absent. `checkAccessByOwnership` reads bucket metadata from `bucketRegistry`, allows errors to propagate, allows admins based on capabilities, then compares the request account ID with the bucket owner ID. Non-admin, non-owner requests are denied.

## State and Persistence Behavior
The helper reads bucket metadata but does not mutate it. Authorization decisions are per request. Account identity is sourced from request headers, while admin status is derived from server auth state.

## Dependencies and Integration Points
It depends on `bucketRegistry.GetBucketMetadata`, `isUserAdmin`, account constants, S3 header constants, and S3 error codes. It is used by ACL/ACP handlers that require bucket ownership.

## Risks and Edge Cases
The comment notes admin is by capability, not account ID, because account-less identities can share an admin-looking ID. Correctness depends on upstream authentication setting trusted account headers; this helper itself does not verify signatures. Missing owner metadata causes denial unless admin.

## Test Signals
Tests should cover bucket lookup errors, admin bypass, owner allow, anonymous/non-owner deny, and buckets with nil owner metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_acp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_auth.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_auth.go -->
