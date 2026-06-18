# Research: subset-b-007871

This grouped report covers SeaweedFS S3 API filer helpers, IAM regressions, the Iceberg REST catalog bridge, lifecycle XML conversion, object-lock utilities, and POST policy validation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_etag_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_etag_test.go

Purpose: regression tests for multipart ETag behavior when SeaweedFS has both an S3-stored ETag in `Entry.Extended[s3_constants.ExtETagKey]` and a filer-derived MD5 in `Entry.Attributes.Md5`. The tests pin the S3 compatibility rule that part validation and final multipart ETag calculation prefer the stored S3 part ETags, with MD5 fallback only when stored metadata is empty.

Important APIs and flow: `TestGetEtagFromEntryPrefersStoredExtendedETag` calls `getEtagFromEntry` and `validateCompletePartETag` against a synthetic `filer_pb.Entry`; `TestGetEtagFromEntryFallbacksToFilerETag` checks empty stored ETag fallback; `TestCalculateMultipartETagUsesStoredPartETags` verifies `calculateMultipartETag` uses stored part ETags. Helpers `newMultipartETagTestEntry`, `expectedMultipartETagForTest`, and `mustDecodeHexETagForTest` model AWS multipart ETag assembly by concatenating decoded part ETags and appending `-partCount`.

State and persistence: no durable writes occur, but the tests model persisted filer metadata fields. Dependencies are `filer_pb.Entry`, S3 constants, `crypto/md5`, and hex/string utilities. Integration point is the multipart complete path, especially ETag comparison from client CompleteMultipartUpload XML. Risk: changing ETag precedence can break clients that uploaded encrypted, copied, or otherwise non-MD5 parts. Test signal is focused and strong for precedence, fallback, and final multipart hash inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_etag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_sse_s3_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_sse_s3_test.go

Purpose: regression coverage for SSE-S3 multipart completion metadata repair. It verifies completed multipart chunks can be retagged with missing chunk-level SSE-S3 metadata from the upload entry, while preserving already-present metadata and applying object-level SSE headers to the completed entry.

Important tests: `TestCompletedMultipartChunkBackfillsSSES3MetadataFromUploadEntry` extracts upload-level key data/base IV via `extractMultipartSSES3Info`, calls `completedMultipartChunk`, and confirms `SSE_S3` plus per-chunk IV based on the part-local offset. `TestCompletedMultipartChunkPreservesExistingSSES3Metadata` protects existing metadata. `TestApplyMultipartSSES3HeadersFromUploadEntry` backfills `SeaweedFSSSES3Key` and `X-Amz-Server-Side-Encryption` without clobbering. `TestCompletedMultipartChunkBackfilledIVDecryptsActualCiphertext` encrypts realistic multipart streams and proves the repaired IV decrypts each chunk. `TestCompletedMultipartChunkRejectsPartNumberMultiplierFormula` prevents using `PartOffsetMultiplier` in IV derivation.

State and dependencies: synthetic `filer_pb.FileChunk` and `Entry.Extended` maps stand in for filer persistence. The tests depend on the SSE-S3 key manager, `GenerateSSES3Key`, metadata serialization/deserialization, CTR IV math, and S3 constants. Integration points are multipart upload completion, read-side decryption, and object metadata detection. Risks include silent data corruption if IV offsets use final object offsets or part-number math instead of part-local encrypted chunk offsets. Test signal is high because it crosses encryption and decryption paths with random plaintext.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_sse_s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_util.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/filer_util.go

Purpose: S3 API helper methods wrapping SeaweedFS filer CRUD operations for directories, files, listings, deletes, entry lookup/update, bucket collection naming, and object-key normalization.

Important APIs: `mkdir`, `mkFile`, `list`, `rm`, `rmObject`, `exists`, `getEntry`, `updateEntry`, `getCollectionName`, and `objectKey`. `doDeleteEntry` builds `filer_pb.DeleteEntryRequest` with `IgnoreRecursiveError=true`. `deleteObjectEntry` adds S3-specific handling for non-empty directory-marker deletes: when filer reports `MsgFailDelNonEmptyFolder`, it calls `demoteDirectoryMarkerToImplicitDirectory`. That function looks up the entry, verifies it is a directory key object, clears object-facing metadata, and updates the entry so the path remains as an implicit directory rather than a delete-blocking zero-byte object.

State and persistence: methods operate through `WithFilerClient` and persist `filer_pb.Entry` mutations in the filer. `clearDirectoryMarkerMetadata` removes MIME, MD5, file size, content, chunks, and public S3 extended metadata, retaining only `xattr-*` and SeaweedFS internal keys. Dependencies include `filer_pb`, `filer`, `glog`, `util.FullPath`, gRPC status codes, and S3 constants. Integration points are object delete handlers, bucket/object path logic, and callers that expect S3 directory marker semantics. Risks: error-string matching for non-empty-folder detection is brittle, context uses `context.Background`, and metadata filtering must not accidentally drop internal replication/system attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_util_delete_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/filer_util_delete_test.go

Purpose: unit tests for `deleteObjectEntry` and directory-marker demotion in `filer_util.go`. The file uses a stub `deleteObjectEntryTestClient` implementing selected `SeaweedFilerClient` methods to observe delete, lookup, and update requests without a real filer.

Important tests: `TestDeleteObjectEntryDemotesNonEmptyDirectoryMarker` simulates a delete failure with `MsgFailDelNonEmptyFolder`, returns a directory key object, and verifies the update strips object metadata while preserving `xattr-*` and `x-seaweedfs-*` internal keys. `TestDeleteObjectEntryTreatsImplicitDirectoryAsSuccessfulNoop` confirms an already implicit directory requires no update. `TestDeleteObjectEntryIgnoresConcurrentUpdateNotFound` accepts a concurrent not-found during update. `TestDeleteObjectEntryPropagatesNonDirectoryDeleteErrors` ensures unrelated delete errors do not trigger lookup/demotion.

State and dependencies: state is captured inside the test client request fields and synthetic `filer_pb.Entry` objects. Dependencies include filer sentinel messages, S3 constants, gRPC status errors, and testify assertions. Integration point is S3 delete behavior for directory markers in buckets with child entries. Risk covered is accidental recursive data loss or leaving blocking directory-marker metadata behind. Test signal is good for control-flow branches, but still relies on the same string matching used in production.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_util_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_util_tags.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/filer_util_tags.go

Purpose: helper methods for S3 object tagging stored in filer entry extended attributes. The constant `S3TAG_PREFIX` is built from `s3_constants.AmzObjectTagging + "-"`, so each tag key is persisted under a prefixed extended-attribute name.

Important APIs and flow: `getTags` looks up an entry and returns all `Extended` entries whose keys start with `S3TAG_PREFIX`, stripping that prefix. `setTags` looks up the entry, deletes any old tag-prefixed attributes, initializes `Extended` if needed, writes the new tag map, and persists via `filer_pb.UpdateEntry`. `rmTags` removes tag-prefixed attributes and avoids an update if no tag was present.

State and persistence: tags live in `filer_pb.Entry.Extended`, so object tagging changes are metadata-only filer updates. Dependencies are `WithFilerClient`, `LookupEntry`, `UpdateEntry`, `context.Background`, string prefix matching, and S3 constants. Integration points are bucket/object tagging HTTP handlers and any lifecycle/policy code that reads tag metadata. Risks: tag keys are stored verbatim after the prefix, so validation and encoding must occur at the handler layer; concurrent metadata updates could race because the whole entry is read-modify-written; nil `Extended` maps are handled on set but `getTags` assumes a valid lookup response/entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_util_tags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_batch_delete_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iam_batch_delete_test.go

Purpose: regression tests for IAM authorization of S3 multi-object delete requests. The core behavior is that each key in a batch delete must be authorized against its object ARN, not only against the bucket-level ARN.

Important tests: `TestAuthorizeBatchDeleteKey_AwsCanonicalPolicy` creates a policy granting `s3:DeleteObject` on `arn:aws:s3:::bucket/*`, attaches it to an identity, and checks that deleting `objects/a.txt` in the bucket succeeds while another bucket is denied. `TestAuthorizeBatchDeleteKey_PrefixScopedPolicy` grants only `bucket/safe/*` and checks per-key allow/deny.

State and dependencies: tests build in-memory `IdentityAccessManagement` with `isAuthEnabled=true`, use `PutPolicy`, synthetic `Identity`/`Credential`, and `httptest` requests. Integration point is the delete handler loop that calls `AuthorizeBatchDeleteKey` for each object. Risk covered: a bucket-level precheck would reject valid AWS-style object policies or allow a whole batch based on one broad decision. Test signal is focused on object ARN construction and prefix scoping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_batch_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_defaults_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iam_defaults_test.go

Purpose: tests for advanced IAM configuration defaults, STS signing-key fallback, and default allow/deny behavior depending on whether an explicit IAM config file is supplied.

Important tests: `TestLoadIAMManagerFromConfig_Defaults`, `_Overrides`, `_PartialDefaults`, `_ExplicitEmptyKey`, and `_MissingKeyError` exercise STS duration/issuer/signing-key loading and fallback provider behavior. `TestLoadIAMManagerFromConfig_ExplicitFileDefaultsToDeny` verifies explicit config without `policy.defaultEffect` denies by default. `TestLoadIAMManagerFromConfig_NoFileDefaultsToAllow` preserves zero-config startup allow behavior. `TestLoadIAMManagerFromConfig_ExplicitFileEnforcesUserScopedPolicy` covers issue #8366 by loading roles/policies using `${jwt:preferred_username}` and checking arbitrary bucket creation is denied while the user bucket is allowed.

State and dependencies: tests create temporary JSON config files, call `loadIAMManagerFromConfig`, and query `manager.DefaultAllow` or `IsActionAllowed`. Dependencies include `iam/integration`, OS temp files, and testify. Integration points are S3 server startup flags, STS token signing, and policy engine variable substitution. Risks: a missing default signing key must fail clearly, while explicit config should not accidentally create an open S3 gateway. Test signal is broad for config loading and enforcement defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_defaults_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_list_prefix_regression_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iam_list_prefix_regression_test.go

Purpose: regression tests for list-bucket IAM evaluation when S3 list requests carry `prefix` query parameters. The tests pin AWS semantics: list actions remain bucket-level resources, and prefix scoping belongs in the `s3:prefix` condition rather than in the resource ARN.

Important tests: `TestEvaluateIAMPolicies_ListBucketWithPrefix` ensures `s3:ListBucket` on `arn:aws:s3:::bucket` allows list requests with or without a promoted object prefix. `TestEvaluateIAMPolicies_ListBucketPrefixCondition` checks a `StringLike` `s3:prefix` condition accepts matching prefixes and rejects others. `TestEvaluateIAMPolicies_ListBucketVersionsWithPrefix` verifies version listing resolves to `s3:ListBucketVersions` even with a prefix.

State and dependencies: in-memory policies are installed via `PutPolicy`; synthetic identities and `httptest` requests mirror the post-auth promotion path. Dependencies are `s3_constants.ACTION_LIST`, IAM evaluator internals, and JSON policy construction. Integration points are `authRequestWithAuthType`, list-object/list-versions handlers, and policy engine condition context. Risk covered: using the prefix as the object part of the resource ARN breaks valid bucket list policies. Test signal is targeted at action/resource/condition mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_list_prefix_regression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_optional_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iam_optional_test.go

Purpose: tests for optional IAM behavior when the gateway starts without an IAM config or identities. The target is zero-config S3 usability with advanced IAM plumbing present but not enforcing authentication.

Important APIs and tests: `resetMemoryStore` clears the shared memory credential store when it implements `Reset`. `TestLoadIAMManagerWithNoConfig` checks `NewIdentityAccessManagementWithStore` succeeds with an empty `Config`. `TestLoadIAMManagerFromConfig_EmptyConfigWithFallbackKey` checks no anonymous identity exists when not configured. `TestSetIAMIntegrationKeepsAuthDisabledWithoutConfig` covers issue #9557: calling `SetIAMIntegration` must not enable auth enforcement by itself; `EnableAuthEnforcement` is the explicit opt-in.

State and dependencies: tests mutate global credential stores, build `S3ApiServerOption`, and inspect `iam.isEnabled`. Dependencies are the credential package and testify. Integration points are `weed mini`, Docker default startup, and S3 server setup that installs advanced IAM integration. Risks: global in-memory store pollution can make tests order-sensitive; production risk is accidentally returning AccessDenied for anonymous zero-config deployments. Test signal is concise but important for startup defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iam_optional_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_helpers.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_helpers.go

Purpose: helper types and functions for Iceberg REST table commits, especially create-on-commit flows where a commit with `assert-create` finalizes a staged or implicit table creation.

Important APIs: `icebergRequestError` normalizes HTTP/error-type responses. `createOnCommitInput` carries bucket ARN, marker bucket, namespace, table name, identity, location, UUID, base metadata/version, updates, and statistics updates. Error classifiers `isS3TablesConflict`, `isS3TablesNotFound`, and `isS3TablesAlreadyExists` translate S3 Tables manager errors and string fallbacks. `hasAssertCreateRequirement` detects Iceberg `assert-create`. `finalizeCreateOnCommit` applies table updates to a metadata builder, serializes metadata, applies statistics updates, runs metadata spec compliance fixups, saves a new metadata file, creates the S3 Tables row, cleans up on failure, and removes stage-create markers on success.

State and persistence: writes `vN.metadata.json` through `saveMetadataFile`, persists catalog state through `s.tablesManager.Execute("CreateTable")`, and deletes files/markers on failure or completion. Dependencies include `iceberg-go/table`, `s3tables`, `filer_pb`, UUIDs, JSON, and glog. Integration point is `handleUpdateTable` when no existing table is found. Risks: partial failure can leave metadata files or markers; string-based error detection is compatibility-oriented but imprecise; metadata location/version must stay aligned with S3 Tables version state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_updates.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_updates.go

Purpose: parses Iceberg REST commit updates while compensating for `iceberg-go` versions that do not yet decode `set-statistics` and `remove-statistics` update actions.

Important APIs: `statisticsUpdate` stores either a `table.StatisticsFile` upsert or snapshot-id removal. `ErrIncompleteSetStatistics` rejects incomplete legacy-form `set-statistics`. `setStatisticsUpdate.asStatisticsFile` accepts either nested `statistics` or flattened required fields, ensuring `BlobMetadata` is non-nil. `parseCommitUpdates` separates statistics updates from regular `table.Updates` by reading raw JSON action names and unmarshalling only non-statistics actions through iceberg-go. `applyStatisticsUpdates` unmarshals metadata JSON into a map, indexes existing statistics by snapshot id while preserving order, applies set/remove changes, deletes the key when empty, and remarshal the object.

State and persistence: functions are pure over JSON bytes, but their output is later persisted in metadata files and S3 Tables `FullMetadata`. Dependencies are `encoding/json` and `iceberg-go/table`. Integration points are both regular commit and create-on-commit. Risks: map remarshal in `applyStatisticsUpdates` can reorder top-level metadata keys; duplicate snapshot IDs collapse to the last value; schema drift in Iceberg statistics JSON can break parsing. Tests cover separation, incomplete updates, upsert/remove behavior, and conflict classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/commit_updates.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_commit.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_commit.go

Purpose: HTTP handler for Iceberg REST Catalog table commit (`POST /v1/.../tables/{table}`), mapping REST commit requests to S3 Tables catalog updates and filer metadata file writes.

Control flow: `handleUpdateTable` parses namespace/table, resolves bucket ARN and identity, decodes raw requirements/updates, separates statistics updates, then attempts up to three commits. It first loads the table through S3 Tables. If not found and stage-create/assert-create allows creation, it optionally loads the latest stage marker and staged metadata template, validates requirements, creates base metadata if needed, and delegates to `finalizeCreateOnCommit`. For existing tables it parses current full metadata or creates synthetic metadata, validates requirements, applies updates via `MetadataBuilderFromBase`, serializes, applies statistics and spec compliance, writes `v{version+1}.metadata.json`, then calls S3 Tables `UpdateTable` with the version token. Version conflicts trigger metadata cleanup, jittered retry, and eventually `CommitFailedException`.

State and persistence: writes metadata JSON under the table location, updates S3 Tables rows with version token and `FullMetadata`, and cleans orphan metadata on update failures. Dependencies include mux vars, `iceberg-go/table`, `s3tables.Manager`, filer client, path/location helpers, stage-create helpers, and S3 identity context. Risks include partial failure between file write and catalog update, requirement validation against synthetic metadata, retry races, and error classification by string. Test coverage is mostly indirect via commit update helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_namespace.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_namespace.go

Purpose: Iceberg REST namespace and config handlers. They adapt REST namespace operations to S3 Tables manager calls and return Iceberg-shaped JSON.

Important APIs: `handleConfig` returns catalog defaults/overrides and, when `?warehouse=s3://bucket/...` is supplied, sets `overrides.prefix` to the bucket and echoes the warehouse. `handleListNamespaces` parses pagination and optional parent namespace, then calls `ListNamespaces`. `handleCreateNamespace` validates request body, normalizes properties, calls `CreateNamespace`, and returns properties with a default `location`. `handleGetNamespace`, `handleNamespaceExists`, and `handleDropNamespace` wrap get/head/delete with Iceberg error status mapping.

State and persistence: namespace data is persisted by S3 Tables manager in filer-backed metadata. The handlers themselves are stateless, using identity from request context and bucket resolution from prefix/warehouse/env. Dependencies include `s3tables`, `filer_pb`, mux, JSON, pagination helpers, namespace property helpers, and glog. Integration points are Iceberg clients such as DuckDB/Trino that use `/v1/config`, namespace listing, and namespace locations for table creation. Risks: error mapping still relies partly on strings; parent namespace flattening uses dot-separated S3 Tables prefixes; warehouse subpaths are intentionally ignored for bucket routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_namespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth.go

Purpose: OAuth2 client-credentials support for the Iceberg REST catalog. It lets S3 access-key credentials obtain bearer JWTs and lets catalog routes authenticate those bearer tokens.

Important APIs: `OAuthTokenResponse`, `OAuthErrorResponse`, and `IcebergClaims` define wire/token shapes. `handleOAuthTokens` parses form or HTTP Basic credentials, rejects `client_secret` in the URL, requires `grant_type=client_credentials`, validates credentials through `CredentialValidator`, signs an HS256 JWT using `deriveSigningKey(accessKey, secret)`, and returns a one-hour bearer token. `authenticateBearer` extracts the bearer token, parses claims without validation to find the access key, fetches the current credential secret, verifies signature and expiry, and returns identity info. `writeOAuthError` emits OAuth-shaped JSON errors.

State and dependencies: no server-side token store is used; token validity depends on current credential lookup. Dependencies include `golang-jwt/jwt/v5`, HMAC-SHA256, the server credential validator, and shared `writeJSON`. Integration points are `Server.Auth` and `/v1/oauth/tokens`. Risks: unverified parsing is deliberately used only to choose a verification key; credential rotation invalidates old tokens; the token is signed from the client secret, so validator availability is required for both issuance and verification. Tests cover success, invalid credentials, unsupported grant type, and bearer round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth_test.go

Purpose: unit tests for Iceberg OAuth token issuance and bearer authentication.

Important components: `mockCredentialValidator` implements both `ValidateS3Credential` and `GetCredentialByAccessKey` over in-memory access-key maps. `newTestServerWithOAuth` builds a server with one credential. `TestHandleOAuthTokens_Success` posts `client_credentials` form data and verifies status, token type, non-empty access token, and expiry. `TestHandleOAuthTokens_InvalidCredentials` expects 401. `TestHandleOAuthTokens_UnsupportedGrantType` expects 400. `TestBearerTokenRoundTrip` obtains a token then authenticates a bearer request and checks the identity name. `TestBearerTokenInvalid` and `TestBearerTokenNone` reject bad/missing tokens.

State and dependencies: all state is local to the mock validator and httptest recorder/request. Dependencies are JSON, net/http, httptest, strings, and the OAuth handler under test. Integration point is `Server.Auth`, which calls `authenticateBearer` before falling back to S3 request authentication. Risks not covered include Basic auth input, URL secret rejection, expired tokens, wrong signing methods, and credential rotation, but the core issuance/verification path has direct coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_table.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_table.go

Purpose: Iceberg REST table handlers for list, create, load, exists, drop, stale-location cleanup, and metadata construction.

Important APIs and flow: `validateCreateTableRequest` requires a table name. `handleListTables` lists S3 Tables rows in a namespace with pagination. `handleCreateTable` resolves the table location from request, namespace warehouse property, `ICEBERG_WAREHOUSE`, or bucket default; validates bucket/path confinement; builds Iceberg metadata with `newTableMetadata`; writes spec-compliant `v1.metadata.json`; handles idempotent existing-table responses; optionally stage-creates metadata/markers; otherwise creates the S3 Tables row. `handleLoadTable` returns `buildLoadTableResult`. `handleDropTable` deletes the S3 Tables row and then purges the catalog-owned table location to support recreation. `cleanupStaleTableLocation` validates path segments before recursive filer removal. `buildFileIOConfig` advertises S3 endpoint, path-style access, and region.

State and persistence: table metadata files live under the filer-backed S3 Tables path; catalog rows store UUID, `FullMetadata`, version, and location; drop may recursively delete table storage. Dependencies include `iceberg-go`, `s3tables.Manager`, `filer_pb`, path validation helpers, stage-create helpers, environment variables, and S3 identity context. Risks: create writes metadata before catalog registration and lacks cleanup for generic create failures; recursive cleanup must only run after catalog deletion; custom locations are restricted to the catalog bucket. Tests cover validation, stage-create env behavior, namespace locations, issue #9103 bucket/config helpers, and path validation separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg.go

Purpose: package documentation for the Iceberg REST Catalog API implementation. It states that the package implements the Apache Iceberg REST Catalog specification backed by S3 Tables metadata storage.

APIs and control flow: this file exports no functions or types; it defines only the package comment and package name. Its integration role is documentation for generated package docs and for developers navigating the `weed/s3api/iceberg` package.

State and dependencies: no runtime state, persistence, imports, or dependencies. Risks are documentation drift: the package has grown to include OAuth, path validation, stage-create markers, metadata-file persistence, and spec-compliance fixups, so this summary is intentionally broad but not detailed. Test signal is not applicable to this file directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_commit_updates_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_commit_updates_test.go

Purpose: tests for commit update parsing, statistics JSON patching, and S3 Tables conflict classification.

Important tests: `TestParseCommitUpdatesSeparatesStatistics` passes raw updates containing `set-statistics` and `set-properties`, expecting one statistics update and one decoded regular update. `TestParseCommitUpdatesRejectsIncompleteSetStatistics` verifies `ErrIncompleteSetStatistics`. `TestApplyStatisticsUpdatesUpsertAndRemove` starts with two statistics entries, upserts snapshot 1, removes snapshot 2, and verifies only the updated snapshot remains. `statisticsFileForTest` provides a reusable `table.StatisticsFile`. `TestIsS3TablesConflict` checks both sentinel `ErrVersionTokenMismatch` and typed `S3TablesError{ErrCodeConflict}`.

State and dependencies: tests operate on JSON byte slices and in-memory structs. Dependencies are `iceberg-go/table`, `s3tables`, JSON, errors, and testing. Integration points are commit handlers that persist patched statistics in metadata files and detect optimistic-concurrency conflicts. Risks covered include unsupported Iceberg update actions and conflict retry decisions. Test signal is focused but does not run a full HTTP/catalog commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_commit_updates_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_create_table_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_create_table_test.go

Purpose: small tests for table creation request validation and the stage-create feature flag.

Important tests: `TestValidateCreateTableRequestRequiresName` checks an empty `CreateTableRequest` returns `errTableNameRequired`; `TestValidateCreateTableRequestAcceptsWithName` accepts a named request. `TestIsStageCreateEnabledDefaultsToTrue` verifies an unset `ICEBERG_ENABLE_STAGE_CREATE` defaults to enabled. `TestIsStageCreateEnabledFalseValues` checks false-like values `0`, `false`, `FALSE`, `no`, and `off`.

State and dependencies: tests use `t.Setenv` for environment isolation and plain error comparison. Integration points are `handleCreateTable` stage-create handling and request validation before metadata writes. Risks covered are accidental rejection of default stage-create workflows or accepting empty table names. Test signal is narrow but protects high-level branch conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_create_table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_issue_9103_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_issue_9103_test.go

Purpose: regression tests for issue #9103, where Iceberg clients need correct bucket routing and S3 FileIO configuration.

Important tests: `TestGetBucketFromPrefix_WarehouseQueryFallback` verifies `getBucketFromPrefix` uses `?warehouse=s3://bucket/` when no route prefix is present, ignores warehouse subpaths for routing, and falls back to `warehouse` on malformed or missing input. `TestBuildFileIOConfig` checks an empty endpoint yields no config and a configured endpoint advertises `s3.endpoint`, `s3.path-style-access=true`, and a non-empty region.

State and dependencies: tests use `httptest.NewRequest` and simple `Server{s3Endpoint: ...}` state. Integration points are `/v1/config`, load-table responses, DuckDB attach flows, and S3 direct file access by clients. Risks covered include clients landing on the wrong table bucket or requiring an external AWS region setting. Test signal directly targets helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_issue_9103_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_namespace_properties_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_namespace_properties_test.go

Purpose: tests for namespace property normalization.

Important tests: `TestNormalizeNamespacePropertiesNil` verifies nil input becomes an empty non-nil map. `TestNormalizeNamespacePropertiesReturnsInputWhenSet` verifies non-nil maps are reused, not copied.

State and dependencies: state is local map mutation. Integration points are namespace create/get responses and `withDefaultNamespaceLocation`, which mutates the property map to add default Iceberg `location` when missing. Risks: returning nil properties can produce awkward JSON/client behavior; reusing the map means callers must be aware the helper may mutate shared state. Test signal is narrow but documents intentional aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_namespace_properties_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_pagination_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_pagination_test.go

Purpose: tests for Iceberg REST pagination query parsing.

Important tests: `TestParsePaginationDefaultValues` expects empty token and default page size. `TestParsePaginationUsesCamelCaseParameters` accepts `pageToken` and `pageSize`. `TestParsePaginationSupportsHyphenatedFallback` accepts `page-token` and `page-size`. `TestParsePaginationRejectsInvalidPageSize` rejects zero, negative, nonnumeric, and values above the maximum.

State and dependencies: tests use `httptest` requests only. Integration points are list namespaces and list tables handlers, which forward page token and page size to S3 Tables manager as continuation token/max results. Risks covered include client compatibility across camelCase and hyphenated Iceberg parameter spellings and preventing oversized list requests. Test signal is direct for helper boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_pagination_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance.go

Purpose: fixes Iceberg metadata JSON emitted by `iceberg-go` so strict clients can parse empty-table metadata. Some required keys are omitted or null when empty; this helper backfills sentinel values.

Important APIs: `specRequiredEmptyOrder` and `specRequiredEmptyDefaults` define required keys: `current-snapshot-id=-1`, `snapshots=[]`, `snapshot-log=[]`, `metadata-log=[]`, and `refs={}`. `isJSONNull` detects explicit null. `ensureMetadataSpecCompliance` unmarshals the top-level object, returns invalid/empty/top-level-null input unchanged, appends missing keys without reordering existing JSON when no nulls exist, and remarshal only when replacing explicit nulls. `appendMissingObjectKeys` splices defaults before the final `}`.

State and persistence: pure byte transformation, but applied before metadata files and S3 Tables `FullMetadata` are persisted and before REST responses are serialized. Dependencies are `bytes` and `encoding/json`. Integration points are create-table, commit, create-on-commit, `LoadTableResult.MarshalJSON`, and `CommitTableResponse.MarshalJSON`. Risks: byte-level splicing assumes a valid top-level object; null replacement uses map remarshal and can reorder keys; future Iceberg spec-required fields must be added here. Tests are extensive for missing fields, existing fields, nulls, invalid input, order preservation, empty object, and no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance_test.go

Purpose: test suite for `ensureMetadataSpecCompliance`.

Important tests: `TestEnsureMetadataSpecCompliance_BackfillsMissingFields` mirrors fresh `iceberg-go` output and checks all sentinels. `PreservesExistingFields` ensures real snapshot state is not overwritten. `ReplacesExplicitNullsWithSentinels` handles nulls. `InvalidJSONReturnedUnchanged`, `EmptyInputReturnedUnchanged`, and top-level `null` protect pass-through behavior. `PreservesOriginalKeyOrder` asserts byte-for-byte append order for compact JSON. `EmptyObjectBackfilled` checks no leading comma. `AllPresentReturnsSameBytes` requires exact no-op output when all fields exist.

State and dependencies: pure JSON byte slices and maps. Integration points are all metadata persistence/response paths that call the compliance helper. Risks covered include strict-client parse failures, accidental metadata corruption, and nondeterministic output that could surprise tests or clients. Test signal is strong for edge cases and byte-level behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_compliance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_files.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_files.go

Purpose: filer-backed storage helpers for Iceberg metadata JSON files.

Important APIs and flow: `saveMetadataFile` creates a 30-second operation context, ensures the table bucket, table path segments, and `metadata` directory exist under `s3tables.TablesPath`, then writes the metadata file as a filer entry with JSON MIME metadata. `deleteMetadataFile` removes one metadata file from the derived metadata directory. `loadMetadataFile` looks up a metadata file and returns a copy of `Entry.Content`.

State and persistence: this file directly creates directory and file entries in the filer under the S3 Tables storage tree. Dependencies include `filer_pb.LookupEntry`, `CreateEntry`, `DoRemove`, filer error sentinels, `s3tables.TablesPath`, path/string utilities, and timeouts. Integration points are table create, commit, create-on-commit, stage-create template loading, and cleanup after failed updates. Risks: `saveMetadataFile` trusts `tablePath` validation to callers; concurrent ensureDir calls handle already-exists but other errors bubble; file content is stored inline in `Entry.Content`, which is suitable for metadata JSON but not large data files. Test coverage is indirect through handlers and path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation.go

Purpose: middleware and helpers that prevent path traversal through Iceberg REST route variables before they are joined into filer paths.

Important APIs: `validateRequestPath` inspects mux vars `prefix`, `namespace`, and `table`. It requires captured values to be non-empty, validates `prefix` with S3 bucket-name rules, validates table and each unit-separator-delimited namespace segment with `isValidNameSegment`, and rejects bad requests before handlers run. `isValidTablePath` checks slash-separated table locations for unsafe segments. `isValidNameSegment` rejects `.`, `..`, embedded `/`, backslash, and NUL, while allowing empty for helper-level use.

State and dependencies: stateless HTTP middleware depending on mux vars and S3 bucket-name validation. Integration points are `Server.RegisterRoutes`, stage-create marker paths, table location builders, and stale-location cleanup. Risks: route cleaning is disabled with `SkipClean(true)`, so this middleware is the front-line defense for `..` in captured vars; helper-level empty segment allowance is safe only when callers separately reject empty captures. Tests cover traversal, unit separator edge cases, empty captures, and helper rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation_test.go

Purpose: tests for Iceberg path traversal defense.

Important tests: `TestIsValidTablePath` accepts normal paths and rejects `..`, `.`, and backslash forms. `TestValidateRequestPath_RejectsTraversal` builds a mux router with `SkipClean(true)` and checks clean routes pass while `..` in prefix/namespace/table, bare `.`, unit-separator namespace traversal, and leading/trailing/consecutive separators are rejected before the handler runs. `TestValidateRequestPath_RejectsEmptyCapturedVars` directly sets empty mux vars to verify defense-in-depth. `TestIsValidNameSegment` documents allowed dot-containing names and rejected separators/NUL.

State and dependencies: local httptest routers/recorders and mux URL vars. Integration point is `Server.RegisterRoutes`, where the middleware is installed after logging and before authenticated handlers. Risks covered are bucket escape and route-variable collapse into the same namespace. Test signal is strong for HTTP middleware behavior and helper boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/server.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/server.go

Purpose: server wiring for the Iceberg REST Catalog API: dependencies, route registration, logging middleware, and authentication middleware.

Important APIs: `FilerClient`, `S3Authenticator`, and `CredentialValidator` interfaces decouple the catalog from concrete S3/filer/IAM implementations. `Server` stores filer access, S3 Tables manager, authenticator, OAuth credential validator, and advertised S3 endpoint. `NewServer` constructs a manager and mirrors default-allow from the S3 authenticator. `SetCredentialValidator` and `SetS3Endpoint` configure optional OAuth/FileIO behavior. `RegisterRoutes` installs logging and path validation middleware, public config/OAuth endpoints, authenticated namespace/table endpoints with and without `/v1/{prefix}`, and a JSON catch-all. `Auth` prefers bearer OAuth, then falls back to S3 request authentication and maps S3 errors to Iceberg error types.

State and persistence: server holds configuration and delegates durable work to handlers through filer/S3 Tables manager. Dependencies include gorilla/mux, S3 constants/context helpers, `s3err`, `s3tables`, and glog. Integration points are the S3 gateway router and all Iceberg handlers. Risks: `responseWriter.statusCode` defaults to zero when handlers only write body without explicit header; `DefaultAllow` fallback can permit unauthenticated catalog access only when S3 gateway is configured that way; route order and path validation are security-sensitive. Tests cover OAuth and path validation, with route wiring mostly indirect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/stage_create.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/stage_create.go

Purpose: support for Iceberg stage-create/deferred-create workflows. Stage-create writes metadata and a marker without registering the S3 Tables table until a later commit finalizes creation.

Important APIs: `stageCreateMarker` records table UUID, final location, staged metadata location, creation time, and expiry. Path helpers build marker namespace keys with URL-escaped Iceberg namespace encoding and place markers under `s3tables.TablesPath/<bucket>/.iceberg_staged/...`. `pruneExpiredStageCreateMarkers` lists marker files and removes expired ones. `loadLatestStageCreateMarker` finds the newest unexpired marker. `writeStageCreateMarker` prunes old markers, ensures marker directories, and writes a JSON marker file. `deleteStageCreateMarkers` removes all markers for a table. `isStageCreateEnabled` defaults to true and treats `0/false/no/off` as disabled.

State and persistence: staged metadata files are written elsewhere; this file persists marker JSON entries in the filer and deletes them after finalize/create. Dependencies include `filer_pb` streaming/list/create/remove APIs, UUIDs, URL/path encoding, `s3tables.TablesPath`, and 30-second timeouts. Integration points are `handleCreateTable` with `StageCreate` and `handleUpdateTable` create-on-commit. Risks: marker listing limit is 1024; stale staged metadata files may remain after marker expiry; path safety depends on route validation and escaped namespace keys. Tests cover only env flag behavior directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/stage_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/types.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/types.go

Purpose: wire types for Iceberg REST Catalog requests/responses and custom JSON handling around `iceberg-go` metadata.

Important types: `CatalogConfig`, `ErrorModel`, `ErrorResponse`, `Namespace`, `TableIdentifier`, namespace/table list/create/get responses, `CreateTableRequest`, `LoadTableResult`, `CommitTableRequest`, and `CommitTableResponse`. `CreateTableRequest` embeds `iceberg.Schema`, `PartitionSpec`, `table.SortOrder`, stage-create, and properties. `LoadTableResult.MarshalJSON` and `CommitTableResponse.MarshalJSON` serialize `table.Metadata`, run `ensureMetadataSpecCompliance`, and embed raw metadata JSON. Their `UnmarshalJSON` counterparts parse metadata with `table.ParseMetadataBytes`.

State and persistence: types are transient request/response structs, but their marshaled metadata bytes are also used by handlers for persistence. Dependencies include `iceberg-go` and `iceberg-go/table`. Integration points are every Iceberg HTTP handler and strict clients expecting REST spec field names like `metadata-location` and `next-page-token`. Risks: custom marshal must stay in sync with Iceberg spec and `iceberg-go` parser behavior; `table.Metadata` as an interface-like type can fail marshal/parse at runtime; omitting config on commit responses is intentional but client expectations may vary. Tests for metadata compliance indirectly validate the custom marshal fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/utils.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/utils.go

Purpose: shared utility functions for Iceberg namespace encoding, S3 location parsing, JSON/error responses, bucket routing, pagination, and namespace location defaults.

Important APIs: `parseNamespace` splits decoded Iceberg unit-separator namespaces and filters empty parts; `encodeNamespace` joins namespace parts for protocol paths; `flattenNamespacePath` joins with dots for storage. `parseS3Location` validates `s3://bucket/path`; `tableLocationFromMetadataLocation` strips `/metadata/...`; `writeJSON` and `writeError` emit responses. `getBucketFromPrefix` resolves bucket from mux prefix, `warehouse` query, `S3TABLES_DEFAULT_BUCKET`, or default `warehouse`. `buildTableBucketARN` uses S3 Tables default region/account. `parsePagination` supports camelCase and hyphenated params with max 1000. `normalizeNamespaceProperties`, `defaultNamespaceLocation`, and `withDefaultNamespaceLocation` stabilize namespace properties for clients.

State and dependencies: mostly stateless helpers, with environment reads for bucket default. Dependencies include mux, JSON, HTTP, strconv, S3 constants, and `s3tables`. Integration points span all namespace/table handlers and issue #9074/#9103 compatibility paths. Risks: `parseNamespace` filtering means callers must reject empty unit-separator segments before parsing; warehouse subpaths do not scope the catalog; `withDefaultNamespaceLocation` mutates the input map. Tests cover pagination, namespace properties, bucket fallback, and FileIO config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/identity_reflection_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/identity_reflection_test.go

Purpose: reflection-based compatibility test for the `Identity` struct fields consumed by S3 Tables helpers via reflection.

Important tests: `TestIdentityFieldsForS3TablesReflection` checks `Identity` has `PrincipalArn` as a string, `PolicyNames` as a slice, and `Claims` as a map with string keys. `checkField` centralizes field existence/kind assertions.

State and dependencies: no runtime state; uses Go `reflect` over the compile-time `Identity` type. Integration points are `s3tables.getIdentityPrincipalArn`, `getIdentityPolicyNames`, and `getIdentityClaims`, which apparently avoid a direct type dependency by reflection. Risks: refactoring `Identity` field names or kinds can silently break S3 Tables authorization unless this test catches it. Test signal is narrow but valuable as a contract test across package boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/identity_reflection_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical.go

Purpose: converts S3 bucket lifecycle XML wire structs into the lifecycle engine’s canonical `s3lifecycle.Rule` representation.

Important APIs: `Parse` decodes XML bytes into `Lifecycle`. `ParseCanonical` combines parsing and conversion. `LifecycleToCanonical` handles nil safely and converts each `Rule`. `ruleToCanonical` maps ID/status, flattened filters, expiration days/date/delete-marker, noncurrent version expiration, newer noncurrent versions, and abort-incomplete-MPU days. `flattenFilter` supports absent filters, `<Prefix>`, single `<Tag>`, `<And>` with prefix/multiple tags/object-size bounds, and filter-level size bounds.

State and dependencies: pure conversion; no persistence. Dependencies are `encoding/xml`, `bytes`, and `weed/s3api/s3lifecycle`. Integration points are bucket lifecycle configuration handlers and lifecycle worker/shell callers that need canonical rule execution without importing the full S3 API package. Risks: transition and noncurrent transition fields are parsed by types but not currently mapped into canonical output here; prefix fallback from legacy top-level `<Prefix>` occurs only when filter prefix is empty. Tests cover filter forms, multiple actions, dates, delete markers, disabled status, nil, and empty rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical_test.go

Purpose: unit tests for conversion from lifecycle XML to canonical lifecycle engine rules.

Important tests: `TestLifecycleToCanonical_TopLevelPrefix`, `_FilterPrefix`, `_FilterTagAndSize`, and `_SingleTagFilter` cover filter flattening. `TestLifecycleToCanonical_MultipleActions` ensures expiration, noncurrent expiration, and abort-MPU actions all populate one canonical rule. `TestLifecycleToCanonical_ExpirationDate` and `_ExpiredObjectDeleteMarker` cover alternate expiration fields. `_DisabledRulePreserved` keeps status unchanged. `_NilSafe` and `_EmptyRules` cover edge cases. `parseLifecycle` uses the public `Parse` entrypoint.

State and dependencies: pure XML strings, reflection for tag-map equality, and time parsing. Integration points are lifecycle XML handlers and downstream rule compilation. Risks covered include dropping actions when multiple are present and misrepresenting filters. Test signal is broad for currently mapped canonical fields; transition mapping remains outside these assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/round_trip_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/round_trip_test.go

Purpose: XML marshal/unmarshal round-trip tests for lifecycle wire types.

Important tests: noncurrent version expiration and abort-incomplete-MPU rules unmarshal fields and remarshal expected XML. Tag, And, and size-only filters check custom `Filter.UnmarshalXML` state flags and child data. `TestLifecycleXML_TransitionSetFlag` and `_NoncurrentVersionTransitionSetFlag` verify optional transition elements record presence. `TestLifecycleXMLRoundTrip_CompleteRule` models a Terraform-like rule and confirms important fields survive marshal.

State and dependencies: pure XML strings and `encoding/xml`; assertions inspect custom presence flags such as `TagSet`, `AndSet`, `Transition.Set`, and `NoncurrentVersionTransition.Set`. Integration points are S3 Put/Get bucket lifecycle configuration, where absent versus present-empty elements matter. Risks covered include `omitempty` losing optional actions because set flags were not recorded. Test signal is strong for wire-shape preservation, complementary to canonical conversion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/round_trip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/types.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/types.go

Purpose: defines the XML wire model for S3 `BucketLifecycleConfiguration` without importing the full `weed/s3api` package graph.

Important types/APIs: `Lifecycle`, `Rule`, `Filter`, `Prefix`, `And`, `Expiration`, `ExpireDeleteMarker`, `ExpirationDate`, `Transition`, `NoncurrentVersionExpiration`, `NoncurrentVersionTransition`, and `AbortIncompleteMultipartUpload`. Custom marshal/unmarshal methods track presence via private `set`, `andSet`, and `tagSet` flags, so absent elements differ from present-empty elements. Constructors/accessors include `NewPrefix`, `NewExpirationDays`, `Prefix.Set/Val`, `Filter.Set/AndSet/TagSet`, and `Set` methods for optional actions.

State and persistence: structs represent XML request/response state, not durable storage by themselves. Dependencies are `encoding/xml` and `time`. Integration points are lifecycle config handlers, canonical conversion, and external callers such as shell/lifecycle worker. Risks: private set flags are crucial; constructing structs manually without constructors may omit XML on marshal. `Filter.MarshalXML` chooses And, Tag, or Prefix branch and then writes size bounds; unsupported/unknown XML children are skipped on unmarshal. Tests cover round-trip and canonical behavior for major forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/object_lock_utils.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/object_lock_utils.go

Purpose: shared utilities for bucket versioning and S3 Object Lock configuration/validation, used by S3 API handlers and Admin UI.

Important APIs: `StoreVersioningInExtended` and `GetVersioningStatus` persist versioning in filer `Entry.Extended`. `CreateObjectLockConfiguration`, `StoreObjectLockConfigurationInExtended`, `LoadObjectLockConfigurationFromExtended`, `ExtractObjectLockInfoFromConfig`, and `CreateObjectLockConfigurationFromParams` translate between UI parameters, XML structs, and extended attributes. `ValidateObjectLockParameters`, `ValidateRetention`, `ValidateLegalHold`, `ValidateObjectLockConfiguration`, and `validateDefaultRetention` enforce modes, future dates, duration bounds, and days-vs-years exclusivity. `HasObjectsWithActiveLocks` and `CheckBucketForLockedObjects` delegate scans to `s3_objectlock`.

State and persistence: bucket-level object-lock/versioning state is stored in filer extended keys such as enabled/default mode/default days/default years. Object-level validation uses request structs; locked-object scans traverse filer state through delegated package calls. Dependencies include S3 constants, filer proto entries, time, strconv, glog, and object-lock error/types defined elsewhere in `s3api`. Integration points are bucket create/configuration, retention/legal-hold handlers, delete-bucket protection, and Admin UI. Risks: years convert to 365-day UI duration, invalid stored numeric values are ignored, and nil retention/legal-hold inputs would panic if callers fail to validate before calling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/object_lock_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy/post-policy_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/policy/post-policy_test.go

Purpose: tests for S3 POST policy parsing/validation, especially stricter X-Amz field handling and prefix-stem policy conditions.

Important helpers: `EncodePath` percent-encodes non-reserved UTF-8 path characters for tests; `buildParsedPolicy` creates expiring policy JSON and calls `ParsePostPolicyForm`. Tests verify unknown condition keys are rejected with useful context, stray `X-Amz-*` fields are rejected except reserved auth fields, exact X-Amz conditions allow matching fields, prefix-stem conditions like `$x-amz-meta-` authorize matching form-field names, value prefixes are enforced, overlapping exact and prefix conditions both apply, multiple prefix stems all apply, and unknown-key errors include policy value.

State and dependencies: tests use `http.Header` as submitted form fields, time-based future expiration, regex/UTF-8 helpers, and string assertions. Integration points are browser-based S3 POST object uploads and SigV4 form auth fields. Risks covered are both over-permissive acceptance of unexpected fields and over-strict rejection of AWS-valid prefix-stem metadata conditions. Test signal is strong for policy edge cases around X-Amz forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy/post-policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy/postpolicyform.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/policy/postpolicyform.go

Purpose: parser and evaluator for Amazon S3 POST Object policy documents. It is derived from MinIO code and validates policy JSON conditions against multipart form headers.

Important APIs: `ParsePostPolicyForm` unmarshals expiration and conditions, normalizes map conditions to `eq`, parses `eq`, `starts-with`, and `content-length-range`, and rejects malformed/non-string fields. `CheckPostPolicy` verifies expiration, builds exact X-Amz policy keys and prefix-stem rules, rejects extra non-reserved `X-Amz-*` form fields, enforces every matching prefix-stem value prefix, then evaluates each declared condition. `startsWithConds` lists known S3 condition keys and whether `starts-with` is allowed. `postPolicyAuthFields` permits required SigV4 form fields without explicit conditions.

State and persistence: no persistence; `PostPolicyForm` stores parsed expiration, condition policies, and content-length range. Dependencies are JSON, HTTP header canonicalization, reflection for errors, string/time/strconv helpers. Integration points are S3 POST upload handlers. Risks: `content-length-range` is parsed but not enforced in `CheckPostPolicy` here, so callers must enforce size separately or this is incomplete; canonical header casing matters; prefix-stem conditions can overlap and are intentionally all enforced. Tests cover unknown keys, extra X-Amz fields, reserved auth fields, exact/prefix matching, and error context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy/postpolicyform.go -->
