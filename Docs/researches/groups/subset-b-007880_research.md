# subset-b-007880 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_server.go

Purpose: constructs and wires the SeaweedFS S3 API server. It owns server options, IAM/STS integration, filer and master clients, bucket registries, policy engines, request routing, CORS, chunk read caching, write locking, lifecycle/background loops, and helper methods used by embedded APIs.

Important APIs/types/functions: `S3ApiServerOption` is the startup contract for filers, masters, IAM config, CORS, cache, cipher, upload limits, and external URL behavior. `S3ApiServer` is the central state holder, embedding generated IAM/lifecycle gRPC server stubs and references to IAM, STS, bucket config cache, bucket policy engine, circuit breaker, filer client, `ReaderCache`, route-by-key lock client, and versioning heal queue. `NewS3ApiServerWithStore` performs all initialization. `Shutdown` stops the reconciler and IAM. `syncBucketPolicyToEngine`, `checkPolicyWithEntry`, and `recheckPolicyWithObjectEntry` bridge bucket policy state into request authorization. `classifyDomainNames`, `handleCORSOriginValidation`, `UnifiedPostHandler`, and `registerRouter` are the key HTTP-routing helpers. `loadIAMManagerFromConfig`, `AuthenticateRequest`, `DefaultAllow`, `ValidateS3Credential`, and `GetCredentialByAccessKey` expose auth integration points.

Control flow: construction rejects empty filer lists, loads security signing keys and CORS defaults, creates legacy IAM and a bucket policy engine, then configures `wdclient.FilerClient` either directly or through master discovery. With masters, it also subscribes to lock-ring updates before starting master keepalive so route-by-key ownership is not missed. It initializes SSE-S3 key management, reloads IAM config asynchronously from the filer, creates a shared `filer.ReaderCache`, wires object write locks, optionally loads advanced IAM and STS, optionally exposes embedded IAM, registers reload callbacks, creates an HTTP client or Unix-socket transport, registers all mux routes, starts metadata-event subscription and bucket-size metrics, and launches the versioning reconciler. Requests then pass through request-id middleware, optional S3 Tables routing, health routes, host/path-style bucket routing, CORS/path validation, IAM/public-read auth, and circuit-breaker upload/read limits before reaching object or bucket handlers.

State and persistence behavior: most state is process-local cache or client state backed by filer metadata. IAM identities and policies are loaded from file/filer and refreshed by metadata events or gRPC cache updates. Bucket policies are mirrored into `policyEngine`. Shared `ReaderCache` persists for the process lifetime and may contain an in-memory chunk cache when `CacheSizeMB > 0`. Object locks are short-lived cluster locks with TTL renewal. Reload callbacks refresh config-file IAM and JWT signing keys. Versioning heal state is an in-memory bounded queue stopped by `Shutdown`.

Dependencies and integration: integrates gorilla/mux, SeaweedFS filer/master clients, cluster lock ring, credential manager, IAM integration, STS service, bucket policy engine, lifecycle protobufs, security guards, chunk cache, request IDs, grace reload, and the many S3 object/bucket handlers registered elsewhere. `registerS3TablesRoutes` and `STSHandlers` are wired here, making this file the convergence point for regular S3, IAM, STS, and S3 Tables traffic.

Risks: initialization order is sensitive: IAM, policy engine, filer client, SSE-S3 keys, and STS signing keys have fallback dependencies. The zero-config `EnableIam` path intentionally preserves permissive behavior unless a config file is provided, so changes can break mini/default deployments or accidentally tighten/loosen auth. Route order is load-bearing: object routes must precede bucket routes; explicit STS and S3 Tables routes must avoid being swallowed by IAM or regular S3 routes. Shared read cache and route-by-key owner skipping affect memory and availability. `UnifiedPostHandler` reads and restores request bodies under a size limit; regressions can break SigV4 verification or cause DoS exposure.

Test signals: routing tests cover STS/IAM dispatch and hostless bucket fallback. S3 Tables routing tests protect route collision behavior. Versioning tests indirectly cover reconciler startup state. High-value additional signals are constructor tests for negative cache capacity, IAM config default-effect behavior, chunk cache sizing, CORS origin rejection, object route ordering, reload key rotation, and `Shutdown` stopping background loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_grpc.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_grpc.go

Purpose: implements the generated `SeaweedS3IamCacheServer` methods used by the filer to push unidirectional IAM cache updates into an S3 API server.

Important APIs/functions: `PutIdentity` validates and upserts an identity; `RemoveIdentity` deletes by username; `PutPolicy`, `DeletePolicy`, `GetPolicy`, and `ListPolicies` mutate or query cached IAM policy documents; `PutGroup` and `RemoveGroup` update group membership policy state. All methods are `S3ApiServer` methods and use `iam_pb` request/response types with gRPC status errors.

Control flow: each mutating RPC validates required fields, checks `s3a.iam` where needed, logs the update, invokes the corresponding `IdentityAccessManagement` cache method, and returns either an empty protobuf response or `InvalidArgument`/`Internal` status. `GetPolicy` treats lookup failure as cache miss rather than RPC failure and returns an empty response.

State and persistence behavior: this file does not persist data itself. It updates process-memory IAM caches that are backed elsewhere by filer configuration, metadata subscriptions, or credential stores. Updates are intended as cache refreshes, not authoritative writes from S3 back to the filer.

Dependencies and integration: depends on generated `iam_pb` messages, `IdentityAccessManagement` cache APIs, `glog`, and gRPC status/codes. It complements metadata-event subscription in `s3api_server.go` and embedded IAM API mutation paths.

Risks: nil `s3a.iam` checks are inconsistent: identity removal/upsert assumes IAM exists, while policy/group methods check. Cache miss in `GetPolicy` is indistinguishable from other `GetPolicy` errors. Since this is cache-only, ordering and delivery guarantees from the filer matter; stale updates could leave one S3 gateway with divergent auth behavior.

Test signals: useful tests would exercise invalid argument handling, nil IAM behavior, successful identity/policy/group cache mutation, `GetPolicy` cache miss behavior, and concurrent update/read races under the IAM cache locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_routing_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_routing_test.go

Purpose: regression tests for S3 API mux routing, especially overlapping STS, embedded IAM, and bucket routes.

Important APIs/functions: `setupRoutingTestServer` creates a minimal server with enabled IAM, seeded static credentials, embedded IAM, and placeholder `STSHandlers`. `signRoutingTestRequest` signs requests with AWS SigV4 for a requested service. Tests cover query/body STS actions, authenticated IAM, matcher logic, GetFederationToken dispatch, and hostless path-style bucket fallback.

Control flow: tests construct a mux, call `s3a.registerRouter`, send synthetic requests through `router.ServeHTTP` or inspect `router.Match`, and assert status codes or matched routes. STS tests expect 503 from uninitialized STS as proof routing reached `STSHandlers`, while IAM tests assert requests do not reach STS. Host fallback tests only match routes and avoid invoking real handlers.

State and persistence behavior: the test server stores IAM identity state in memory and does not connect to filer/master services. Seeded credentials allow `UnifiedPostHandler` to pass `AuthSignatureOnly` and test body-based STS dispatch.

Dependencies and integration: uses gorilla/mux, AWS SDK v4 signer, memory credential manager, SeaweedFS IAM types, and testify assertions. It directly protects route ordering in `s3api_server.go`.

Risks: expected status codes are proxies for route selection, so unrelated handler validation changes can require test adjustment. The zero-value `STSHandlers` path is intentionally uninitialized; if STS readiness behavior changes, routing assertions may need a more explicit spy handler. Fake IAM setup bypasses some production initialization, so it is not a full auth integration test.

Test signals: this file is itself a signal that `Action=GetFederationToken` must route to STS whether supplied in query or authenticated body, anonymous STS body requests must hit fallback STS, authenticated non-STS POST must hit IAM, and bucket routes must still match arbitrary Host headers when `DomainName` is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_routing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sosapi.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sosapi.go

Purpose: implements Smart Object Storage API virtual objects for backup software discovery. It synthesizes `.system-.../system.xml` and `.system-.../capacity.xml` inside buckets without requiring physical objects.

Important APIs/types/functions: constants define the SOSAPI system folder, XML object names, client user-agent marker, protocol version, and recommended block size. `SystemInfo`, `APIEndpoints`, `SystemRecommendations`, and `CapacityInfo` model XML payloads. `isSOSAPIObject`, `generateSystemXML`, `generateCapacityXML`, `getCapacityInfo`, `collectBucketUsageFromTopology`, `calculateClusterCapacity`, `handleSOSAPIGetObject`, `handleSOSAPIHeadObject`, and `generateSOSAPIContent` implement discovery and response generation.

Control flow: GET/HEAD handlers first check whether the object path is one of the SOSAPI virtual objects. Content generation verifies bucket existence through `getBucketConfig`, then either emits static system capability XML or asks masters for topology and quota-derived capacity. GET responses compute MD5 ETags, set XML content type, and use `http.ServeContent` for range/content metadata; HEAD emits headers and status without a body.

State and persistence behavior: virtual XML is generated on demand and not persisted. Capacity uses bucket quota from filer entry metadata when available, otherwise master topology disk/volume information. Bucket usage is approximated by summing unique volume sizes in the bucket collection.

Dependencies and integration: depends on S3 bucket config/entry helpers, filer errors, master `VolumeList`, SeaweedFS version metadata, S3 error writers, and protobuf topology structures. It is intended to be called from object HEAD/GET handlers before normal object lookup.

Risks: capacity is only as accurate as master topology and volume collection mapping; shared volumes, stale topology, or missing masters produce zero/default capacity. `time.Now()` is used for Last-Modified/ServeContent, so caches may see changing validators for identical XML. `ModelName` and protocol version include quoted string values, which appears spec-driven but is easy to regress. The user-agent constant is defined here but detection is not in this file.

Test signals: valuable tests would cover virtual path detection, XML schema fields, bucket-not-found mapping to `NoSuchBucket`, quota-vs-cluster capacity choice, duplicate volume ID suppression, HEAD header correctness, and GET range behavior through `ServeContent`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sosapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_decrypt_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_decrypt_test.go

Purpose: executable documentation for AES-CTR IV handling differences across SSE-C, SSE-KMS, and SSE-S3 decryption paths.

Important APIs/functions: `TestSSECDecryptChunkView_NoOffsetAdjustment` uses `CreateSSECDecryptedReader` and `calculateIVWithOffset` to prove SSE-C must decrypt with the stored random IV directly. `TestSSEKMSDecryptChunkView_RequiresOffsetAdjustment` proves SSE-KMS must apply offset adjustment exactly once. `TestSSEDecryptionDifferences` records the intended semantics.

Control flow: tests generate random AES keys and IVs, encrypt plaintext with a chosen IV strategy, then compare correct decryption against anti-tests that intentionally use the wrong offset behavior. Failure occurs if the anti-test unexpectedly recovers plaintext.

State and persistence behavior: no persistent state. The test models metadata state by passing stored IVs and offsets directly, representing chunk metadata produced by upload paths.

Dependencies and integration: uses Go crypto AES/CTR primitives plus SeaweedFS SSE helpers. It protects object read/range paths that must choose whether stored metadata IVs are already adjusted.

Risks: randomized cryptographic tests are stable for equality/corruption checks but still depend on correct helper assumptions. The tests do not invoke full filer-backed object retrieval, so they isolate crypto semantics rather than end-to-end metadata serialization.

Test signals: these tests signal that SSE-C uses random per-part IVs with no offset adjustment, SSE-KMS uses base IV plus object/chunk offset, and double-adjustment corrupts data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_decrypt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_s3_upload_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_s3_upload_test.go

Purpose: regression tests for SSE-S3 multipart upload IV derivation and metadata encoding.

Important APIs/functions: `TestSSES3MultipartUploadStoresDerivedIV` validates `CreateSSES3EncryptedReaderWithBaseIV` returns the offset-derived IV that must be serialized. `TestHandleSSES3MultipartEncryptionFlow` simulates the full encrypt-update-key-decrypt cycle with `SSES3Key.IV`. `TestSSES3HeaderEncoding` checks base-IV base64 header round trip and AES block-size validation.

Control flow: tests generate keys and base IVs, calculate expected derived IVs with `calculateIVWithOffset`, encrypt data at multiple part offsets, confirm returned IV equals expected, and show that decrypting with the original base IV corrupts non-zero-offset parts.

State and persistence behavior: no filesystem state. The tests model persisted chunk metadata by copying the derived IV into `SSES3Key.IV`, matching the upload path's intended serialized metadata.

Dependencies and integration: uses global SSE-S3 key manager, `SSES3Key`, `CreateSSES3EncryptedReaderWithBaseIV`, AES/CTR primitives, base64, and S3 constants. It protects multipart upload handlers that store encryption metadata on chunks.

Risks: tests avoid `SerializeSSES3Metadata` and full KMS setup, so serialization-specific regressions need separate coverage. Global key manager state may be shared with other tests if not isolated.

Test signals: passing tests prove SSE-S3 multipart upload stores derived IVs, not base IVs; non-zero offsets require different IVs; and HTTP IV headers must decode to `AESBlockSize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_s3_upload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_status_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_status_handlers.go

Purpose: provides the minimal liveness/readiness/status handler registered for `/status`, `/healthz`, and `/readyz`.

Important APIs/functions: `StatusHandler` is an `S3ApiServer` method that writes HTTP 200 with an empty body through `s3err.WriteResponse`.

Control flow: the handler ignores request method details and server dependency health; route registration in `s3api_server.go` allows GET and HEAD.

State and persistence behavior: no state is read or written. It is a process-level HTTP reachability probe, not a filer/master readiness check.

Dependencies and integration: depends on `net/http` and the S3 error/response utility package. Registered before bucket routes.

Risks: because it always returns OK, orchestration systems may consider a server ready even when filer, IAM, master discovery, or STS dependencies are unhealthy. If stronger readiness is desired, this endpoint is too shallow.

Test signals: simple tests can assert GET/HEAD status 200 and empty body; integration tests should decide whether dependency failures need separate readiness endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_status_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_stream_error_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_stream_error_test.go

Purpose: tests the decision logic for whether streaming read errors should be written as error responses after a stream failure.

Important APIs/functions: `TestShouldWriteStreamingErrorResponse` covers `shouldWriteStreamingErrorResponse` with nil errors, raw and wrapped `context.Canceled`, gRPC canceled status, and deadline exceeded.

Control flow: table-driven cases pass errors through the helper and assert the boolean. Canceled client connections are expected to suppress error writes; deadline exceeded remains reportable.

State and persistence behavior: no state. It models error classification for streaming handlers that may already have begun sending data.

Dependencies and integration: uses `StreamError`, context package, and gRPC status/codes. It protects object GET streaming behavior and noisy logging/client-disconnect response handling.

Risks: only cancellation and deadline cases are covered; other transport errors, EOFs, and wrapped multi-error chains may need additional classification tests. The behavior depends on how `StreamError` exposes/unpacks its wrapped error.

Test signals: passing tests indicate client-initiated cancellation should not trigger an additional S3 error response, while server-side timeout/deadline should.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_stream_error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts.go

Purpose: implements AWS-compatible STS HTTP endpoints for SeaweedFS: `AssumeRole`, `AssumeRoleWithWebIdentity`, `AssumeRoleWithLDAPIdentity`, `GetCallerIdentity`, and `GetFederationToken`.

Important APIs/types/functions: constants define AWS STS parameter names, actions, version, and duration bounds. `validateRoleSessionName`, `computePackedPolicySize`, `parseDurationSecondsWithBounds`, and `parseDurationSeconds` validate common input. `STSHandlers` wraps `sts.STSService` plus S3 IAM. `HandleSTSRequest` dispatches by `Action`. Action handlers validate parameters, SigV4 or identity-provider credentials, trust/action permissions, optional session policies, and response XML. `prepareSTSCredentials` centralizes session ID, JWT session-token claims, role policy embedding, temporary credential generation, and assumed-role response fields. XML response/error structs model AWS response shapes, and `writeSTSErrorResponse` maps `STSErrorCode` to HTTP/XML.

Control flow: `HandleSTSRequest` parses form/query data, validates API version, then dispatches. Web identity requests allow empty `RoleArn` for claim-based mode and prefer routing through IAMManager so provider account scope and max-session-duration checks run. `AssumeRole` verifies SigV4, checks `sts:AssumeRole`, validates role trust policy when a role is explicit, or falls back to caller principal for self/session context. LDAP identity finds an LDAP provider, authenticates username/password, then checks trust. `GetFederationToken` validates name/duration, rejects temporary credentials before SigV4, verifies caller permission, merges direct and IAM-manager-resolved policies, embeds optional session policy, and returns federated-user credentials. `GetCallerIdentity` verifies SigV4 and returns ARN/account/user ID.

State and persistence behavior: STS credentials are stateless JWT-backed sessions plus deterministic temporary access/secret material derived from session IDs and expirations. Policies and role attachments are read from IAM manager or identity state and embedded into token claims where needed. No server-side session table is written here.

Dependencies and integration: depends on SeaweedFS IAM integration, policy and role stores, STS token/credential generation, LDAP providers, SigV4 verification, request IDs, and S3 XML/error writers. It is registered by `s3api_server.go` both as explicit STS routes and fallback POST handling.

Risks: security correctness depends on matching AWS validation and preserving exact auth order: rejecting temporary credentials for GetFederationToken, not bypassing IAMManager for web identity, and failing closed when policy resolution errors are not user-not-found legacy cases. Empty `RoleArn` support is intentional but widens the code path relying on downstream STS validation. XML namespace shapes and error codes are client-visible. Policy embedding can become stale but makes tokens self-sufficient.

Test signals: tests cover empty RoleArn web identity, IAMManager dispatch, AssumeRole fallback/role policy embedding, GetCallerIdentity XML, GetFederationToken validation, temporary credential rejection, session-policy normalization, policy merge/dedup, default/max durations, and STS-not-ready responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_dispatch_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_dispatch_test.go

Purpose: verifies that public `AssumeRoleWithWebIdentity` STS handling dispatches through `IAMManager` when available instead of directly calling the bare STS service.

Important APIs/functions: `TestAssumeRoleWithWebIdentity_DispatchesThroughIAMManager` directly exercises `STSHandlers.assumeRoleWithWebIdentity`.

Control flow: one subtest wires an uninitialized IAMManager and nil STS service, expecting an IAM-manager-not-initialized error. The other omits IAM integration and expects fallback to an uninitialized bare STS service error.

State and persistence behavior: no persistent state; the test relies on distinct initialization errors as behavioral evidence of dispatch choice.

Dependencies and integration: uses `integration.IAMManager`, `NewS3IAMIntegration`, and STS request types. It guards cross-account provider-scope and max-session-duration enforcement that live on IAMManager.

Risks: error-message-based assertions are fragile if initialization errors are reworded. The test does not build a full OIDC provider stack, so it validates dispatch path rather than successful assumption.

Test signals: passing test means web identity HTTP paths will not silently skip IAMManager-only validation when an IAM manager is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_dispatch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_empty_arn_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_empty_arn_test.go

Purpose: regression test that `AssumeRoleWithWebIdentity` no longer rejects missing `RoleArn` at the HTTP handler layer.

Important APIs/functions: `TestAssumeRoleWithWebIdentity_AllowsEmptyRoleArn` invokes `handleAssumeRoleWithWebIdentity` with `RoleArn` omitted.

Control flow: the form includes action, web identity token, and session name. The handler runs and the test asserts the body does not contain a pre-STS "RoleArn is required" rejection.

State and persistence behavior: no persistent state. It uses a test STS service and in-memory request/response recorder.

Dependencies and integration: relies on the shared test STS setup and `STSHandlers`. It protects claim-based policy mode where role ARN can be derived from token claims/policy.

Risks: the test asserts absence of one error string rather than a full successful claim-based flow. Downstream STS failures are acceptable and not differentiated.

Test signals: passing test indicates the HTTP layer allows empty RoleArn to reach STS service validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_empty_arn_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_test.go

Purpose: tests `AssumeRole` credential preparation behavior, especially caller-principal fallback and embedding attached role policies into STS session tokens.

Important APIs/functions: `TestAssumeRole_CallerIdentityFallback` exercises `prepareSTSCredentials` with IAM user ARNs, assumed-role ARNs, explicit role ARNs, and malformed ARNs. `TestAssumeRole_EmbedsRolePolicies` verifies attached role policy names are embedded in token claims. `newTestSTSIntegrationManager` builds an in-memory IAM/ST​S manager for tests.

Control flow: tests call `prepareSTSCredentials` directly, validate returned assumed-role ARN/id strings, and then validate the generated JWT session token through the STS service to inspect `RoleArn`, admin request context, and embedded policies.

State and persistence behavior: state is in-memory IAM manager configuration: policy documents, role definitions, and generated JWTs. No filer or external store is used.

Dependencies and integration: uses IAM integration, policy documents, STS service token validation, S3 constants, and testify. It protects the shared credential generation function used by `AssumeRole` and LDAP identity paths.

Risks: direct helper testing bypasses SigV4 permission and trust-policy checks in `handleAssumeRole`. Malformed ARN fallback is permissive by design; changes to ARN parsing utilities could alter response formatting and token claims.

Test signals: passing tests mean fallback sessions use caller principals, admin claims are preserved, explicit roles retain their RoleArn, and role attached policies become self-contained STS token policy names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_caller_identity_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_caller_identity_test.go

Purpose: validates XML marshaling shape for `GetCallerIdentity` responses.

Important APIs/functions: `TestGetCallerIdentityResponse_XMLMarshal` builds `GetCallerIdentityResponse` with `GetCallerIdentityResult`, marshals with `encoding/xml`, and checks namespace, ARN, user ID, account, and request ID.

Control flow: no HTTP handler is invoked; this isolates the response struct tags and field names.

State and persistence behavior: no state. It uses default account ID constants and an in-memory response value.

Dependencies and integration: depends on STS response types in `s3api_sts.go`, XML marshaling, and testify. It protects AWS SDK/client compatibility for the response envelope.

Risks: it does not validate SigV4 auth or runtime handler behavior. String containment assertions catch gross XML drift but not full schema conformance.

Test signals: passing test means response XML includes the expected AWS STS namespace and core identity fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_caller_identity_test.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables.go

Purpose: exposes AWS S3 Tables/Iceberg-compatible APIs on the S3 gateway, bridging HTTP target-style and REST-style requests into the `s3tables` package while using the S3 server's filer and IAM context.

Important APIs/types/functions: `S3TablesApiServer` wraps `S3ApiServer` and `s3tables.S3TablesHandler`. Setter methods configure region, account, default allow, and IAM authorizer. `registerS3TablesRoutes` installs target and REST routes. `handleRestOperation` converts REST path/query/body into target-style JSON payloads. Builder helpers create table bucket, namespace, table, policy, tag, and get-table requests. `readS3TablesJSONBody`, `writeS3TablesError`, `getDecodedPathParam`, namespace/int/tag parsers, `isS3TablesSignedRequest`, `extractCredentialScope`, and `authenticateS3Tables` provide validation and auth glue.

Control flow: registration creates the handler, wires IAM default behavior and authorizer, then registers a target-header route and REST routes gated by `serviceMatcher`. REST handlers build a typed payload, replace the request body with AWS JSON protocol content, set `X-Amz-Target`, and invoke the common S3 Tables handler. Auth wrapper authenticates signatures when IAM is enabled, stores identity in context, and delegates authorization to the S3 Tables handler.

State and persistence behavior: this file itself stores no table metadata. It passes filer access through `WithFilerClient`; actual table bucket, namespace, table, policy, and tag persistence is in the `s3tables` implementation/filer backend. It may read identity context for IAM checks.

Dependencies and integration: uses gorilla/mux, S3 IAM context constants, S3 error utilities, generated filer client, and the `s3tables` package. Route registration is called from `s3api_server.go` before regular S3 bucket routes.

Risks: route collisions are the main hazard because REST paths like `/buckets` and `/get-table` can also be regular S3 bucket names. The code deliberately requires SigV4 credential scope service `s3tables` for REST routes; weakening that matcher can hijack regular S3 traffic. Path decoding rejects traversal/NUL but individual builders must still validate table names and namespaces. Body reads are limited to 10 MiB. DefaultAllow behavior can permit unauthenticated access when IAM is disabled or permissive.

Test signals: routing tests ensure S3-signed `/buckets` and `/get-table` fall through to regular S3 while s3tables-signed requests match S3 Tables. REST validation tests ensure invalid namespace query values produce JSON `InvalidRequest` responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_rest_validation_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_rest_validation_test.go

Purpose: tests validation and error mapping for S3 Tables REST namespace query parsing.

Important APIs/functions: tests call `buildListTablesRequest`, `buildGetTableRequest`, and `S3TablesApiServer.handleRestOperation` with invalid namespace values.

Control flow: table-driven cases supply uppercase, hyphenated, and slash-containing namespaces. Builder tests assert an error containing "invalid namespace". Handler test asserts HTTP 400 with AWS JSON error shape and `s3tables.ErrCodeInvalidRequest`.

State and persistence behavior: no persistent state. Requests are synthetic and mux vars are injected directly.

Dependencies and integration: uses gorilla/mux, httptest, JSON decoding, and `s3tables` error codes. It protects parser helpers in `s3api_tables.go`.

Risks: tests are narrow to namespace query validation; path namespace parsing, table-name validation, and ARN parsing have separate or missing coverage. Error-message substring assertions can drift with parser wording.

Test signals: passing tests mean invalid namespaces are rejected before hitting storage and are surfaced as client bad-request JSON errors, not internal errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_rest_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_routing_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_routing_test.go

Purpose: regression tests for S3 Tables route disambiguation from regular S3 routes with colliding paths.

Important APIs/functions: `TestIsS3TablesSignedRequest` tests credential-scope parsing. Routing tests use `setupRoutingTestServer`, `signRoutingTestRequest`, and mux route matching for `/buckets`, PUT `/buckets`, and `/get-table`.

Control flow: requests signed for service `s3` must not match S3 Tables REST routes, even when paths overlap; requests signed for `s3tables` must match the intended S3 Tables route.

State and persistence behavior: no persistent state. The test uses route matching rather than executing handlers, avoiding filer dependencies.

Dependencies and integration: depends on AWS SigV4 signing, mux route templates, and the route registration in `s3api_tables.go`/`s3api_server.go`.

Risks: route-template assertions rely on exact path templates. The tests intentionally require signed S3 Tables traffic; unsigned default-allow S3 Tables REST requests will not match REST routes, which is a design tradeoff for collision safety.

Test signals: passing tests mean regular S3 clients can use bucket names such as `buckets` and `get-table` without receiving S3 Tables JSON, while legitimate S3 Tables clients remain routable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_routing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_test.go

Purpose: small smoke/documentation tests for XML encoding of copy responses.

Important APIs/functions: `TestCopyObjectResponse` creates `CopyObjectResult` and prints encoded XML; `TestCopyPartResponse` does the same for `CopyPartResult` using `s3err.EncodeXMLResponse`.

Control flow: tests instantiate result structs with an ETag and current time, encode, and print. They contain no assertions.

State and persistence behavior: no state beyond transient timestamps.

Dependencies and integration: depends on copy response types defined elsewhere in S3 API handlers and the S3 XML response encoder.

Risks: because there are no assertions, these tests are weak as regressions; they only fail on panic/build failure. `println` output can add noise but documents expected XML interactively.

Test signals: minimal smoke signal that copy result structs still marshal without panic. Stronger tests should assert XML element names, LastModified format, and ETag placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id.go

Purpose: defines S3 object version ID generation, validation, format detection, timestamp extraction, ordering, and helper paths for versioned object storage.

Important APIs/functions: `isValidVersionID` validates opaque client version IDs as safe path segments. `generateVersionId` creates 32-character IDs from a 16-hex timestamp prefix plus 8 random bytes, using either old raw timestamps or new inverted timestamps. `isNewFormatVersionId`, `getVersionTimestamp`, and `compareVersionIds` distinguish and sort old/new/null versions. `getVersionedObjectDir`, `getVersionFileName`, `getVersionIdFormat`, and `generateVersionIdForObject` map versions into `.versions` directories and choose format based on existing metadata.

Control flow: new format IDs use `math.MaxInt64 - now` so lexicographic order sorts newest first. Old format IDs sort newest first by reversing raw timestamp lexicographic comparison. Mixed formats compare extracted real timestamps. `getVersionIdFormat` reads the object's `.versions` directory and uses `ExtLatestVersionIdKey` metadata to preserve old-format continuity, defaulting to new format when no directory/metadata exists.

State and persistence behavior: version IDs become filenames under `.versions` via `v_<versionId>`. Format selection depends on persisted filer metadata in the `.versions` directory. Random suffix avoids collisions for same-nanosecond writes. Invalid/path-traversal version IDs are rejected by segment validation.

Dependencies and integration: uses crypto/rand, timestamp math, S3 constants for `.versions` and metadata keys, and S3 server path helpers. It is consumed by versioned object put/list/delete logic elsewhere.

Risks: format threshold assumes old raw nanoseconds remain below `0x4000...` and new inverted timestamps remain above it for relevant eras. Random-read failure falls back to zero suffix, increasing collision risk. Mixed-format compare returns equal when timestamps match, ignoring random suffix ordering. Format inference from latest metadata can choose new format for old directories missing metadata.

Test signals: version ID tests cover format detection, safe path validation, generation lengths, timestamp extraction, old/new/mixed sorting, null ordering, backward compatibility, and transition behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id_test.go

Purpose: verifies compatibility and ordering behavior for old and new S3 version ID formats.

Important APIs/functions: tests cover `isNewFormatVersionId`, `isValidVersionID`, `generateVersionId`, `getVersionTimestamp`, `compareVersionIds`, and helper constructors for deterministic old/new IDs.

Control flow: table tests classify threshold-based formats and invalid path segments. Sorting tests assert negative results when the first argument is newer. Transition tests create chronological old then new IDs and assert mixed comparisons preserve newest-first order.

State and persistence behavior: no filer state. Tests model persisted version IDs as strings and validate their safe use as path segments and sort keys.

Dependencies and integration: depends on time/math and version ID helpers in `s3api_version_id.go`. It protects list/delete/latest-version logic that relies on ordering.

Risks: generated IDs use current time, so timestamp tolerance is used. Helper `sprintf` manually formats hex to avoid fmt; bugs there could affect deterministic fixtures, though tests mostly use it internally.

Test signals: passing tests show old-format buckets remain sortable, new inverted IDs sort lexicographically newest-first, null sorts last, mixed old/new upgrades are ordered by actual timestamp, and traversal/NUL version IDs are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_heal_log_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_heal_log_test.go

Purpose: pins the log format and sanitization behavior for versioning heal/reconciler events.

Important APIs/functions: tests cover `versioningHealLogPrefix`, `versioningHealInfof`, `sanitizeHealArg`, `sanitizeHealArgs`, and the documented event vocabulary.

Control flow: tests reproduce expected log-line assembly, smoke-call the logger with percent-containing strings, assert unsafe strings/errors are `strconv.Quote` escaped, and verify event names are explicit and token-safe.

State and persistence behavior: no persistent state. It protects operator-facing logs rather than data paths.

Dependencies and integration: uses glog, flag initialization, errors, fmt, strings, and testify. It guards helper functions in `s3api_versioning_reconciler.go` used by queue and healing events.

Risks: tests mostly avoid capturing glog output, so final sink formatting is not fully asserted. The vocabulary list includes events emitted outside the visible reconciler file, making it a documentation contract that must be updated alongside code changes.

Test signals: passing tests mean user-controlled bucket/object/error fields cannot split log tokens or inject fake `event=` fields, and the `[versioning-heal] event=...` prefix remains stable for dashboards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_heal_log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler.go

Purpose: implements a background reconciler for versioned objects whose `.versions` directory latest pointer references a missing version file after a partial delete/update failure.

Important APIs/types/functions: `versioningHealLogPrefix` and logging helpers emit sanitized structured log lines. `sanitizeHealArgs`, `sanitizeHealArg`, and `needsHealQuote` prevent log injection. Queue constants define capacity, poll interval, retry count, and backoff bounds. `versionsHealCandidate` and `versionsHealQueue` store pending bucket/object repairs. Queue methods `Enqueue`, `popReady`, `requeue`, and `Len` manage bounded deduplicated work. Server methods `startVersioningReconciler`, `runVersioningReconciler`, `drainVersionsHealQueue`, and `healVersionsPointer` run and execute repairs.

Control flow: producers enqueue bucket/object candidates. The reconciler ticks every 5 seconds, pops candidates whose retry time has arrived, increments attempts, calls `healVersionsPointer`, and either logs drain success or requeues with exponential backoff capped at 30 seconds. After max retries it drops the candidate and relies on read-path heal. `healVersionsPointer` reads the `.versions` directory, treats missing directory/no pointer/consistent pointer as success, retries transient read/probe errors, and calls `healStaleLatestVersionPointer` when the latest-file pointer is missing.

State and persistence behavior: the queue is in-memory, bounded to 4096 entries, and deduplicated by `bucket/object`. Durable state lives in filer entries and extended metadata under `.versions`; the reconciler repairs that metadata by delegating to the read-path heal function. Queue state is lost on restart, but stranded state can still be healed by reads or future enqueue events.

Dependencies and integration: depends on S3 server bucket/path helpers, filer `getEntry`, versioning constants, gRPC status codes, and the existing `healStaleLatestVersionPointer` implementation. It is started by `NewS3ApiServerWithStore` and stopped by `Shutdown`.

Risks: bounded queue drops newest candidates under flood, so hot failure modes may rely on read-path heal. `versionsHealKey` concatenates bucket/object with `/`, which is adequate for a map key but can collide in pathological bucket/object combinations if bucket names and object names are not constrained. Healing after a transient listing/probe anomaly could rewrite to an older version if transient errors are misclassified, so non-NotFound probe errors are retried. Queue iteration order is map-random, so fairness is best-effort.

Test signals: reconciler tests cover deduplication, capacity cap, due-only popping, backoff requeue, give-up behavior, and retry helper semantics. Heal-log tests protect observability formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler_test.go

Purpose: tests queue mechanics for the versioning reconciler and retry semantics for filer operations used by version pointer updates.

Important APIs/functions: tests cover `newVersionsHealQueue`, `Enqueue`, `Len`, `popReady`, `requeue`, `versionsHealMaxRetries`, and `retryFilerOp` with transient, exhausted, canceled, and terminal errors.

Control flow: queue tests enqueue duplicates, overfill capacity, inject delayed candidates, requeue with backoff, and assert give-up drops max-attempt candidates. Retry tests use closures counting calls and validate success before exhaustion, wrapped exhaustion errors, context cancellation interrupting sleep, and short-circuiting NotFound/canceled/deadline errors.

State and persistence behavior: no persistent state. Queue tests mutate in-memory pending maps; retry tests do not access a filer.

Dependencies and integration: uses context, filer not-found sentinel, gRPC status/codes, testify, and retry constants defined elsewhere in versioning object logic. It complements `s3api_versioning_reconciler.go`.

Risks: tests access queue internals directly for deferred candidates, so internal representation changes require updates. `retryFilerOp` is not defined in the reconciler file but is part of the same versioning repair behavior; failures here indicate broader update-latest retry regressions.

Test signals: passing tests mean heal queue growth is bounded/deduplicated, retries honor backoff and caps, shutdown/client cancellation can interrupt retry sleep, and terminal errors are not retried or wrapped as exhausted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler_test.go -->
