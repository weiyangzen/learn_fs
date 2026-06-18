# subset-b-007884 Research

This grouped report covers the requested SeaweedFS S3 API/S3 Tables files and Tahoe-LAFS CI, documentation, benchmark, and integration harness files. Each section preserves the source path in its title and is bounded for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_table.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_table.go

Purpose: implements S3 Tables table operations for create, get, list, delete, and update. The handlers decode JSON RPC-style requests, validate bucket ARN, namespace, table name, and ICEBERG format, then map logical resources to filer paths under the table-bucket tree.

Important APIs: `handleCreateTable`, `handleGetTable`, `handleListTables`, `handleDeleteTable`, `handleUpdateTable`, `listTablesInNamespaceWithClient`, `listTablesWithClient`, and `listTablesInAllNamespaces`. Responses are built from `tableMetadataInternal` and public response types in `types.go`.

Control flow: create validates namespace existence, loads namespace and bucket policies/tags, checks either namespace or bucket permission, creates the table directory plus `data/`, then writes metadata/tags as extended attributes. Get supports lookup by table ARN or bucket/namespace/name and hides unauthorized reads as `NoSuchTable`. List handles namespace-scoped and whole-bucket listings with continuation tokens. Delete and update load metadata first, enforce optional version tokens, authorize against table or bucket policy, then delete the directory or rewrite metadata.

State and persistence: table metadata, tags, and policies live in filer extended attributes; table data lives in directories below `TablesPath/{bucket}/{namespace}/{table}`. Version tokens are regenerated on updates for optimistic concurrency.

Dependencies and integration: depends on filer gRPC list/entry operations, path/ARN helpers from `utils.go`, policy evaluation from `permissions.go`, and request identity/default-allow behavior from IAM helpers. Risks include policy fetch failures becoming 500s, list pagination edge cases across namespaces, and authorization behavior that differs between 403 and not-found hiding. Test signals are indirect through manager, permission, namespace, and layout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iam.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iam.go

Purpose: bridges S3 Tables handlers to SeaweedFS IAM without importing the broader S3 API server package. It decides when to use IAM, builds IAM action requests, and extracts request identity details through reflection.

Important APIs: `IAMAuthorizer`, `SetIAMAuthorizer`, `shouldUseIAM`, `defaultAllowFor`, `authorizeIAMAction`, `extractSessionToken`, `getIdentityPrincipalArn`, `getIdentityPolicyNames`, `getIdentityClaims`, `buildIAMRequestContext`, and `getIdentityStructValue`.

Control flow: IAM is selected only when an authorizer and identity exist, except anonymous default-allow requests stay on the legacy fallback. Session tokens, missing inline actions, or named policies push evaluation through IAM. `authorizeIAMAction` normalizes action names to `s3tables:*`, resolves principal from headers or identity fields, forwards session token and policy names, and requires every non-empty resource to be allowed.

State and persistence: no persistent state; it reads request context, headers, query parameters, and handler configuration flags. Dependencies include `s3_constants`, IAM `integration.ActionRequest`, `glog`, and reflected identity structs.

Risks: reflection makes field-name drift easy to miss, missing principal/resource is a hard denial, and `defaultAllowFor` treats identity name without full identity as authenticated. Tests in `manager_test.go` cover default-allow/trusted manager distinctions; broader IAM policy paths need integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout.go

Purpose: validates object paths written into table buckets so Iceberg tables only contain accepted metadata and data layouts.

Important APIs: `IcebergLayoutValidator.ValidateFilePath`, `validateDirectoryPath`, `validateFilePatterns`, `validateFile`, `IcebergLayoutError`, `TableBucketFileValidator`, and `ValidateTableBucketUpload`.

Control flow: `ValidateFilePath` strips a leading slash, requires a top-level `metadata` or `data` directory, permits explicit directory keys with trailing slash, then dispatches to metadata or data validation. Metadata is flat and accepts strict Iceberg names plus safe catch-alls for `.avro`, `.metadata.json`, `version-hint.text`, and `.stats`. Data paths allow partition/subdirectory segments and `.parquet`, `.orc`, or `.avro` files. `ValidateTableBucketUpload` ignores non-table-bucket paths, validates non-empty bucket/namespace/table segments, rejects double slashes, and validates the table-relative path.

State and dependencies: stateless regex-based validation using `path` and `strings`. It integrates with upload handling elsewhere to block invalid table bucket writes.

Risks: the catch-all metadata patterns are intentionally permissive for engine compatibility; they rely on safe-character and suffix limits to avoid accepting arbitrary metadata junk. Tests cover real Flink/Spark/Trino names and clearly bad metadata names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout_test.go

Purpose: pins Iceberg layout compatibility and regression behavior for metadata and data filename validation.

Important tests: `TestIcebergLayoutValidator_AcceptsRealWorldManifestNames`, `TestIcebergLayoutValidator_RejectsClearlyBadMetadataNames`, and `TestIcebergLayoutValidator_AcceptsRealWorldDataFiles`.

Control flow: each test creates a fresh `IcebergLayoutValidator`, iterates table-driven cases, and asserts acceptance or rejection from `ValidateFilePath`.

State and dependencies: no persistent state; depends only on the validator in `iceberg_layout.go` and Go `testing`.

Signals and risks: the tests document why the metadata regex set includes catch-all safe names: strict UUID/snapshot-only patterns rejected manifests from real writers such as Flink. Negative cases ensure random extensions, metadata subdirectories, bad top-level directories, and deceptive suffixes still fail. Coverage does not directly test `ValidateTableBucketUpload` full filer path parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iceberg_layout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager.go

Purpose: provides a reusable non-HTTP facade for S3 Tables operations, aimed at shell/admin tooling and the Iceberg catalog while reusing the HTTP handler implementation.

Important APIs: `Manager`, `NewManager`, `SetRegion`, `SetAccountID`, `SetDefaultAllow`, `SetTrusted`, `Execute`, `decodeS3TablesHTTPResponse`, `ManagerClient`, and `NewManagerClient`.

Control flow: `Execute` marshals a request object, builds an in-memory POST with `application/x-amz-json-1.1` and `X-Amz-Target: S3Tables.<operation>`, optionally injects identity headers/context, sends it through `HandleRequest` using `httptest.ResponseRecorder`, then decodes either JSON response or `S3TablesError`.

State and dependencies: owns an embedded `S3TablesHandler`. `ManagerClient` adapts `filer_pb.SeaweedFilerClient` to the local `FilerClient` callback interface. No persistence beyond handler configuration.

Risks: reusing HTTP machinery means manager callers inherit routing/auth semantics and error encoding. Identity name alone is treated as an authenticated principal unless manager is trusted or admin. `manager_test.go` covers the key authorization boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager_test.go

Purpose: verifies manager authorization behavior before filer mutation by using a sentinel filer client.

Important test assets: `recordingFilerClient` marks whether `WithFilerClient` was reached, and `TestManagerCreateTableBucketAuthorization` exercises authenticated, unauthenticated, trusted, and admin paths.

Control flow: each case configures a `Manager`, executes `CreateTableBucket`, expects an error either from denied authorization or the sentinel filer, and asserts whether reaching the filer matches expected authorization.

State and dependencies: uses fake identity structs, `s3_constants` context helpers, and `testify` assertions. It does not persist anything because the sentinel client returns immediately.

Signals and risks: the test locks down a security-sensitive distinction: default allow only falls open for trusted/anonymous zero-config access, not arbitrary identity names. It also confirms admin principal bypass. Coverage is operation-specific but protects shared manager auth plumbing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions.go

Purpose: implements S3 Tables resource-policy evaluation, identity action shortcuts, condition matching, and authorization error construction.

Important APIs/types: `PolicyDocument`, custom `UnmarshalJSON`, `Statement`, `PolicyContext`, `CheckPermissionWithContext`, `checkPermission`, `hasIdentityPermission`, `hasAdminAction`, `matchesPrincipal`, `matchesAction`, `matchesActionPattern`, `matchesConditions`, `getConditionContextValues`, `matchesResource`, and `AuthError`.

Control flow: authorization rejects empty principal/owner, allows account admin and owner, then checks static identity actions. If no resource policy exists, `DefaultAllow` decides fallback. Otherwise it parses AWS-style statements, requires principal/action/resource/condition matches, records explicit allow, and lets explicit deny win immediately. Condition evaluation delegates operators to `policy_engine`.

State and persistence: stateless over policy JSON and `PolicyContext`. Dependencies include SeaweedFS policy engine, wildcard matching, glog, and S3 constants.

Risks: invalid policy JSON silently denies; default allow can still permit unmatched statements after policy evaluation; condition context maps only selected S3 Tables and AWS tag keys. Tests cover wildcard matching, AWS principal forms, condition operators, and default-allow/deny precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions_test.go

Purpose: unit-tests policy matching primitives and default-allow behavior for S3 Tables authorization.

Important tests: `TestMatchesActionPattern`, `TestMatchesPrincipal`, `TestEvaluatePolicyWithConditions`, and `TestCheckPermissionWithDefaultAllow`.

Control flow: table-driven tests assert exact, suffix, middle, question-mark, and combined wildcard behavior; direct, wildcard, array, and AWS-map principal matching; multi-operator condition evaluation over namespace, table name, request tags, and resource tags; and explicit deny overriding fallback allow.

State and dependencies: no persistence. The condition test marshals a `PolicyDocument` to exercise the same JSON path used by production.

Signals and risks: coverage is strong for matching semantics but does not test resource ARN arrays or every supported condition key. It confirms the move to `policy_engine` wildcard support for middle wildcards and protects the security rule that deny wins over `DefaultAllow`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/types.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/types.go

Purpose: defines public JSON request/response and model types for S3 Tables bucket, namespace, table, policy, tagging, metadata, and error APIs.

Important types: `TableBucket`, create/get/list/delete bucket requests and responses, policy requests/responses, `Namespace`, namespace CRUD/list types, `IcebergSchema`, `IcebergMetadata`, `TableMetadata`, `Table`, table CRUD/list/update types, tag request/response types, and `S3TablesError`.

Control flow: this file contains no active control flow beyond `S3TablesError.Error`. Its struct tags define wire compatibility with the JSON RPC handler layer.

State and persistence: public types mirror persisted internal metadata from `utils.go` but are not themselves persistence logic. `json.RawMessage` in `TableMetadata.FullMetadata` allows preserving Iceberg metadata payloads that are not modeled.

Dependencies and integration: used throughout `handler_table.go`, namespace/bucket/policy/tag handlers, manager calls, and tests. Risks are schema drift between public and internal metadata, omitempty hiding empty properties/tags, and enum-like strings such as `ICEBERG` being untyped. Error code constants centralize handler response types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils.go

Purpose: centralizes S3 Tables ARN parsing/building, filer path construction, internal metadata structs, tag validation, namespace/table/bucket validation, and version token generation.

Important APIs: `parseBucketNameFromARN`, `ParseBucketNameFromARN`, `parseTableFromARN`, `GetTableBucketPath`, `GetNamespacePath`, `GetTablePath`, `GetTableObjectRootDir`, `GetTableObjectBucketPath`, `IsTableBucketEntry`, `BuildBucketARN`, `BuildTableARN`, `ValidateTags`, `generateVersionToken`, `validateNamespace`, `ParseNamespace`, `validateTableName`, `ValidateTableName`, `flattenNamespace`, and `expandNamespace`.

Control flow: validation rejects malformed or reserved bucket names, namespace parts with path traversal, slashes, invalid characters, or `aws` prefix, and table names with invalid path/name characters. A single dotted namespace is split into multi-level parts and then flattened back to dot notation for internal paths and ARNs.

State and persistence: defines `tableBucketMetadata`, `namespaceMetadata`, and `tableMetadataInternal`, which are stored as filer extended attributes. Version tokens use 16 random bytes with timestamp fallback.

Risks: regex ARN parsing only supports the chosen namespace/table character set, tag validation is shared with normal S3 tags through `s3api/tags.go`, and dotted namespace normalization must stay consistent with client expectations. Namespace tests cover multi-level behavior and metadata properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils_namespace_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils_namespace_test.go

Purpose: verifies namespace normalization, ARN handling, and namespace metadata property round-tripping.

Important tests: `TestValidateNamespaceSupportsMultiLevel`, `TestValidateNamespaceSupportsDottedInput`, `TestValidateNamespaceRejectsEmptyDottedSegment`, `TestParseNamespace`, `TestParseTableFromARNWithMultiLevelNamespace`, `TestBuildTableARNWithDottedNamespace`, `TestExpandNamespace`, and `TestNamespaceMetadataPropertiesRoundTrip`.

Control flow: the tests compare normalized dot-separated strings, expanded string slices, parsed ARN components, and JSON marshal/unmarshal behavior for nil, empty, and populated `Properties`.

State and dependencies: no persistent state. Uses Go JSON and reflection only.

Signals and risks: these tests protect compatibility between AWS-style dotted namespaces and internal single-directory namespace keys. They also document that empty properties disappear due to `omitempty`. Invalid namespace coverage includes reserved `aws` prefix and empty dotted segments, but not every bucket/table validation branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils_namespace_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sses3_multipart_repro_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/sses3_multipart_repro_test.go

Purpose: regression-tests SSE-S3 multipart decryption behavior for production-like chunking and lazy chunk fetching.

Important tests/helpers: `TestMultipartSSES3RealisticEndToEnd`, `TestBuildMultipartSSES3Reader_LazyChunkFetch`, and `liveTrackingReadCloser`.

Control flow: the end-to-end test generates one data encryption key and base IV shared by all parts, encrypts each part from offset zero, slices ciphertext at 8 MB chunk boundaries, stores per-chunk IV metadata derived from part-local offsets, assigns global file offsets, then verifies `buildMultipartSSES3Reader` decrypts concatenated plaintext. The lazy test creates many encrypted chunks and asserts construction opens no readers, first read opens one, draining opens all eventually, and peak live readers stays at one.

State and dependencies: in-memory ciphertext map simulates volume fetches; filer chunks carry offsets, sizes, SSE type, and serialized metadata. Depends on SSE-S3 key generation, IV calculation, metadata serialization, and reader assembly code outside this file.

Risks and signals: protects issue paths where global offsets and part-local IVs diverge, and where eager fetches held many HTTP responses open. It does not hit real volume servers but accurately models chunk metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sses3_multipart_repro_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/stats.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/stats.go

Purpose: wraps S3 HTTP handlers with metrics, server header injection, bucket activity tracking, and audit fallback logging.

Important APIs: `track`, `TimeToFirstByte`, `BucketTrafficReceived`, and `BucketTrafficSent`.

Control flow: `track` increments an in-flight gauge by action, extracts bucket/object, sets `Server`, wraps the response writer to capture status, installs audit and identity holder context, invokes the handler, blanks bucket labels on forbidden responses, records latency/counter/bucket activity, and emits fallback `PostLog` if the handler did not already audit. TTFB and traffic helpers update histograms/counters and active bucket time.

State and dependencies: metrics are stored in global stats collectors. Request context carries audit tracking and identity holder state. Dependencies include `s3_constants`, `s3err`, SeaweedFS version, and stats package.

Risks: fallback auditing relies on the handler seeing the same request object and setting the tracking flag; status defaults come from the status recorder. Tests cover direct `WriteHeader` fallback and no double-log behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/stats_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/stats_test.go

Purpose: tests audit fallback behavior in the S3 handler metrics wrapper.

Important tests: `TestTrackAuditFallbackForDirectWriteHeader` and `TestTrackAuditSkipsFallbackWhenHandlerEmits`.

Control flow: each test wraps a small handler with `track`, captures the request passed to the handler, invokes the wrapper using `httptest`, and checks `s3err.AuditAlreadyLogged`. The first handler only calls `WriteHeader`; the second calls `PostLog` before writing.

State and dependencies: no external persistence. Uses request context mutation from `s3err.EnsureAuditTracking` and the audit flag set by `PostLog`.

Signals and risks: covers a regression where successful handlers bypassing shared response helpers missed audit logs. It also prevents double logging. It does not assert metrics values, labels, or forbidden bucket redaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sts_packed_policy_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/sts_packed_policy_test.go

Purpose: validates STS packed policy size percentage calculation for inline session policies.

Important test: `TestComputePackedPolicySize` plus the shared `repeat` helper from the session-name test file.

Control flow: table cases pass empty, tiny, half-budget, full-budget, and oversized strings to `computePackedPolicySize`, checking nil for empty policy, integer percentages for non-empty policy, and a 100 percent cap for oversized input.

State and dependencies: no persistence; depends on `sessionPolicyBudgetBytes` and `computePackedPolicySize` production code.

Signals and risks: protects AWS-compatible response metadata for packed policy size. It tests length-based behavior only, not actual compression or policy validation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sts_packed_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sts_params_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/sts_params_test.go

Purpose: tests routing of STS `AssumeRole` POST requests when `Action` appears in the query string or form body.

Important types/tests: `mockIAMIntegration`, `TestSTSAssumeRolePostBody`, and `extractSTSRequestID`.

Control flow: the test constructs a minimal `S3ApiServer` with IAM enabled, registers routes, then sends three POST variants. Query-string `Action=AssumeRole` should hit STS and return missing-parameter 400. Form-body action with bearer auth should route to STS and return service-unavailable 503 instead of IAM 501. SigV4-style form-body action should return 503 or 403, but never 501.

State and dependencies: in-memory IAM identity maps and mock IAM integration; no filer or STS backend. Uses mux routing, request ID headers, and XML error body parsing.

Risks and signals: protects real AWS STS clients that send form-encoded POST bodies. It focuses on routing and request ID propagation, not successful AssumeRole execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sts_params_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sts_session_name_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/sts_session_name_test.go

Purpose: tests STS role session name validation rules.

Important APIs under test: `validateRoleSessionName`; helper `repeat` is also used by packed policy tests in the same package.

Control flow: table cases assert missing name maps to `STSErrMissingParameter`; one-character, overlong, invalid charset, whitespace, slash, colon, and Unicode values map to `STSErrInvalidParameterValue`; length 2, normal ASCII, allowed symbols `+=,.@-`, email-style, and 64-character valid names are accepted.

State and dependencies: no persistence. Uses package-level STS error code constants.

Signals and risks: covers AWS-compatible min/max length and allowed character set. The zero-byte 64-length case explicitly proves length alone is insufficient. It does not test every STS parameter, only role session names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/sts_session_name_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/tags.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/tags.go

Purpose: represents S3 object tagging XML, converts between XML tag sets and maps, parses `x-amz-tagging` style query strings, and delegates validation.

Important APIs/types: `Tag`, `TagSet`, `Tagging`, `ToTags`, `FromTags`, `parseTagsHeader`, and `ValidateTags`.

Control flow: `ToTags` folds XML tags into a map where duplicate keys overwrite. `FromTags` creates XML with the S3 namespace and stable key ordering. `parseTagsHeader` splits on `&`, then `=`, URL-decodes keys and values, allows empty values, and returns decoding errors for malformed percent escapes. `ValidateTags` delegates to `s3tables.ValidateTags`, sharing key/value limits and character rules.

State and dependencies: stateless conversions. Depends on XML, URL decoding, sorting, SeaweedFS string splitting, and S3 Tables tag validation.

Risks: `strings.Split` rather than `SplitN` ignores unencoded `=` inside values, so callers must URL-encode special characters. Tests cover encoded timestamps, keys, values, empty values, invalid encoding, plus signs, and encoded equals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/tags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/tags_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/tags_test.go

Purpose: verifies URL-decoding behavior for tag headers.

Important test: `TestParseTagsHeader`.

Control flow: table cases parse simple tags, encoded timestamp with spaces/colons, encoded key and value, empty value, encoded slash/exclamation, invalid percent escape, and encoded plus/equals in values. The test checks either an expected error or exact map contents.

State and dependencies: no persistence. Exercises the package-private `parseTagsHeader` function.

Signals and risks: protects issue behavior where encoded timestamps and special values must decode before tag validation/storage. It does not test XML `FromTags` ordering or delegated tag validation limits, which are covered through S3 Tables utilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/tags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/config.yml -->
## sources/distributed-fs/tahoe-lafs/.circleci/config.yml

Purpose: primary CircleCI pipeline for Tahoe-LAFS tests, packaging checks, documentation, integration runs, coverage finish, Nix builds, Debian packaging verification, and Docker image builds.

Important elements: pipeline parameters `build-images` and `run-tests`, workflows `ci` and `images`, jobs `debian-12`, Ubuntu variants, `windows-server-2022`, `nixos`, `integration`, `typechecks`, `docs`, `pyinstaller`, `debian-13-package`, `finish-coverage-report`, and `build-image-*`, plus reusable YAML anchors for Docker Hub auth, tox install, setup/test steps, artifacts, and Nix command.

Control flow: normal CI runs platform jobs, code checks, packaging, docs, integration after Debian unit tests, Windows matrix, and coverage finalization. Image builds run only when requested. Debian-style jobs run helper scripts to set up virtualenvs and execute tox as non-root. Windows builds cache pip/wheelhouse, run trial under coverage, upload Coveralls data, and convert subunit results.

State and dependencies: stores test artifacts, caches pip/wheelhouse, uploads coverage to Coveralls, pushes Docker images with Docker Hub context, and fetches Debian packaging sources for Trixie validation.

Risks: embedded Coveralls token and local image tags are sensitive operational dependencies; comments note flaky integration ignore behavior. YAML anchors reduce duplication but make job behavior implicit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/create-virtualenv.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/create-virtualenv.sh

Purpose: creates and bootstraps a virtualenv for CircleCI Docker images using a specified Python executable.

Important behavior: strict Bash mode, positional inputs `WHEELHOUSE_PATH`, `BOOTSTRAP_VENV`, and `PYTHON`, creation via `virtualenv --python`, then pip installs `certifi`, upgrades pip, upgrades setuptools/wheel, and installs `tox~=4.0`.

Control flow: it shifts required positional arguments, derives `PIP` under the new virtualenv, and performs sequential bootstrap installs. Comments explain `certifi` is installed first to avoid older TLS client issues during setup-requires flows.

State and dependencies: creates the virtualenv directory and installs packages into it; does not itself populate the wheelhouse. Depends on `virtualenv`, network or configured pip access, and a valid Python executable.

Risks: no explicit argument validation beyond shell failures; pip/network issues fail the image prep. It is invoked as `nobody` by `prepare-image.sh`, so permissions are tied to the preceding fix-permissions step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/create-virtualenv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/fix-permissions.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/fix-permissions.sh

Purpose: prepares CircleCI image filesystem permissions so tests and setup can run as the non-root `nobody` user.

Important behavior: strict Bash mode, accepts wheelhouse path, bootstrap virtualenv path, and project root, changes `nobody` home to `/tmp/nobody`, recursively chowns the project root, creates the wheelhouse, and chowns it to `nobody`.

Control flow: defines `CHOWN_NOBODY` from `id --group nobody`, applies it to project and wheelhouse, and exits on any failure.

State and dependencies: mutates system user metadata with `usermod`, file ownership under the checkout, and wheelhouse directory ownership. Requires root privileges in the image build context.

Risks: recursive chown over the project root can be expensive and broad; incorrect paths could alter unintended files. It is deliberately paired with non-root CI runs that require readable checkout and writable wheelhouse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/fix-permissions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/populate-wheelhouse.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/populate-wheelhouse.sh

Purpose: builds or downloads wheels for Tahoe-LAFS test dependencies into a shared CI wheelhouse.

Important behavior: strict Bash mode, inputs wheelhouse path, bootstrap virtualenv, and project root, exports `PIP_FIND_LINKS` to the local wheelhouse, and runs `pip wheel --wheel-dir` for project extras `[testenv]` and `[test]`.

Control flow: uses the bootstrap virtualenv pip and forces `LANG=en_US.UTF-8` for the wheel operation because some dependencies historically require UTF-8 when building.

State and dependencies: writes wheel files to the wheelhouse and reads package metadata from the project root. Depends on pip, build tooling installed in the bootstrap venv, and package indexes unless all wheels are already available.

Risks: wheelhouse contents are platform/Python specific, so cache keys must match environment. Build failures surface during image preparation rather than test execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/populate-wheelhouse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/prepare-image.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/prepare-image.sh

Purpose: orchestrates all CircleCI image preparation steps for permissions, virtualenv creation, and wheelhouse population.

Important behavior: strict Bash mode, takes wheelhouse path, bootstrap virtualenv, project root, and Python executable. It calls `fix-permissions.sh`, then runs `create-virtualenv.sh` and `populate-wheelhouse.sh` as `nobody` via `sudo --set-home`.

Control flow: it sequences privileged ownership setup before non-root Python setup, ensuring the later test user owns or can access generated artifacts.

State and dependencies: mutates project/wheelhouse permissions, creates a virtualenv, and fills the wheelhouse. Depends on all three helper scripts, `sudo`, and the target user.

Risks: failures in any child script abort image prep. The script assumes it is run from an image build context where root can sudo to `nobody`; this may not work unchanged in local shells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/prepare-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/rebuild-images.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/rebuild-images.sh

Purpose: convenience script to trigger the CircleCI image-building workflow through the CircleCI API v2.

Important behavior: strict Bash mode, expects API token and branch arguments, then POSTs to the Tahoe-LAFS project pipeline endpoint with parameters `{build-images: true, run-tests: false}`.

Control flow: shifts positional arguments and invokes `curl --verbose` with token and JSON payload.

State and dependencies: does not modify local files; creates a remote CircleCI pipeline. Depends on a valid user API token, network access, and CircleCI project permissions.

Risks: token is passed on the command line where local process listings or shell history may expose it. The script intentionally suppresses normal tests for image rebuilds, so image changes need separate validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/rebuild-images.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/run-build-locally.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/run-build-locally.sh

Purpose: legacy helper for triggering a CircleCI v1.1 build against a specific branch/config for local experimentation.

Important behavior: defines a hard-coded `CIRCLE_TOKEN`, posts current `git rev-parse HEAD`, `config.yml`, and `notify=false` to a CircleCI v1.1 project URL under `exarkun/tahoe-lafs`.

Control flow: a single `curl --user` call sends multipart form fields.

State and dependencies: no local persistence; creates remote CI activity. Depends on git, curl, and validity of the embedded token/API endpoint.

Risks: the hard-coded token is a clear secret-management concern and may be obsolete. The endpoint references a personal fork/branch path, so this script is likely historical and fragile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/run-build-locally.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/run-tests.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/run-tests.sh

Purpose: executes tox test environments in CircleCI, captures subunit/JUnit artifacts, and supports allowed-failure jobs.

Important behavior: strict Bash mode; inputs bootstrap venv, project root, allowed-failure flag, artifact path, tox environment, and extra tox args. It configures subunit output paths, enforces a 45 minute timeout with 1 minute kill grace, exports trial args and unbuffered output, and runs tox with `/tmp/tahoe-lafs.tox` workdir.

Control flow: if artifacts are enabled, it requires the subunit file after tox and converts it to JUnit XML using the environment's `subunit2junitxml`. If `ALLOWED_FAILURE=yes`, failures are converted to success via `true`; otherwise they fail.

State and dependencies: writes artifacts, tox workdir, and possibly trial logs in the checkout. Depends on GNU timeout, tox, and subunit tooling.

Risks: `|| "${alternative}"` relies on `true`/`false` command strings; binary subunit handling is brittle but explicit. Timeout may kill very slow legitimate jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/run-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/setup-virtualenv.sh -->
## sources/distributed-fs/tahoe-lafs/.circleci/setup-virtualenv.sh

Purpose: pre-installs dependencies for a tox environment without running tests.

Important behavior: strict Bash mode; inputs bootstrap venv, project root, wheelhouse path, tox environment, and extra tox args. It invokes bootstrap `tox` against the project `tox.ini` with `--workdir /tmp/tahoe-lafs.tox --notest`.

Control flow: argument shifts collect optional tox args, then a single tox command creates or refreshes the target environment.

State and dependencies: writes tox environment state under `/tmp/tahoe-lafs.tox`; reads project configuration. Wheelhouse-related pip flags are commented out, so actual behavior depends on surrounding environment such as `PIP_FIND_LINKS`.

Risks: commented `PIP_NO_INDEX` means jobs can reach PyPI unless environment overrides. Failure here prevents tests from starting, but catches dependency issues early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.circleci/setup-virtualenv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.github/workflows/ci.yml -->
## sources/distributed-fs/tahoe-lafs/.github/workflows/ci.yml

Purpose: GitHub Actions CI for Tahoe-LAFS coverage, integration, and packaging across Linux, macOS, Windows, CPython, and PyPy.

Important elements: triggers on master pushes and pull requests, read-only token permissions, concurrency cancellation for pull request branches, global Hypothesis CI profile, jobs `coverage`, `finish-coverage-report`, `integration`, and `packaging`.

Control flow: coverage matrix checks out full history, sets up Python with pip cache, installs tox/tox-gh-actions, runs tox, uses a Windows passthrough helper for non-blocking pipe ENOSPC behavior, uploads logs, and reports parallel Coveralls results. Integration installs Tor per OS, runs tox integration or force-Foolscap mode, and uploads Eliot logs on failure. Packaging runs PyInstaller and uploads built artifacts.

State and dependencies: uses GitHub artifact storage, Coveralls tokens, pip cache, Tor packages, Chocolatey on Windows, Homebrew on macOS, and setup-python.

Risks: third-party action versions are pinned only by major version; Coveralls token is embedded. Integration depends on Tor package availability and OS-specific setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.pre-commit-config.yaml -->
## sources/distributed-fs/tahoe-lafs/.pre-commit-config.yaml

Purpose: configures a local pre-commit hook for Tahoe-LAFS code checks.

Important behavior: defines one local hook `codechecks`, active at `pre-push`, using system language, matching `.py` files, running `tox -e codechecks`, and ignoring passed filenames.

Control flow: pre-commit invokes tox once for the push rather than per changed file.

State and dependencies: no repo state beyond pre-commit execution. Requires developers to have pre-commit installed and tox available in the environment.

Risks: `language: system` makes behavior dependent on the developer machine. Because `pass_filenames: false`, any Python change triggers full codechecks, which is slower but avoids partial-check blind spots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.pre-commit-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.readthedocs.yaml -->
## sources/distributed-fs/tahoe-lafs/.readthedocs.yaml

Purpose: configures Read the Docs builds for Tahoe-LAFS documentation.

Important fields: config version 2, Ubuntu 22.04 build image, Python 3.10 toolchain, install requirements from `docs/requirements.txt`, and Sphinx configuration at `docs/conf.py`.

Control flow: Read the Docs provisions the environment, installs documentation requirements, and builds Sphinx using the configured file.

State and dependencies: no local runtime state; remote docs builds depend on RTD infrastructure and requirements availability.

Risks: docs build can diverge from CI docs jobs if Python or requirements differ. The config is minimal and does not specify extra apt packages, so binary/documentation dependencies must come from Python requirements or the base image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.readthedocs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.ruff.toml -->
## sources/distributed-fs/tahoe-lafs/.ruff.toml

Purpose: defines Ruff lint rules for Tahoe-LAFS.

Important configuration: selects Pyflakes `F`, tab/trailing-whitespace rules `W191`, `W291`, `W293`, Bugbear rules `B023`, `B012`, `B006`, and PyLint error category `PLE`.

Control flow: no code execution; Ruff reads this when invoked by tox/codechecks or developer tooling.

State and dependencies: no persistence. Depends on Ruff version support for selected rule codes.

Risks: only a narrow set of rules is enabled, so style and many bugbear/pycodestyle checks remain out of scope. Rule semantics can shift with Ruff upgrades unless tox pins the tool version elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/.ruff.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/Makefile -->
## sources/distributed-fs/tahoe-lafs/Makefile

Purpose: developer and release task entrypoint for Tahoe-LAFS using GNU make.

Important targets: `test`, `test-venv-coverage`, `test-py3-all`, `make-version`, OS X package targets, `code-checks` and its subchecks, `doc-checks`, `count-lines`, `test-git-ignore`, `test-clean`, `clean`, `distclean`, `tarballs`, `upload-tarballs`, `.tox/create-venvs.log`, `release`, `release-test`, and `release-upload`.

Control flow: defensive make settings use bash strict mode, no built-in rules, delete-on-error, and undefined variable warnings. Test targets create tox envs and run code checks/tests. Release target verifies clean git state, builds docs/news/version, commits NEWS, tags version, builds/signs wheel and sdist, and upload target pushes artifacts.

State and dependencies: mutates build artifacts, tox envs, version files, dist files, release commits/tags, and remote upload targets. Depends on tox, coverage, Twisted trial, towncrier, gpg, twine, scp, flappclient, and project helper scripts.

Risks: release targets embed user-specific upload identity and assume clean git/credential setup. Some targets are obsolete placeholders, showing historical maintenance surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/benchmarks/__init__.py -->
## sources/distributed-fs/tahoe-lafs/benchmarks/__init__.py

Purpose: package marker and usage documentation for pytest-based Tahoe-LAFS end-to-end benchmarks.

Important content: module docstring explains running benchmarks under `systemd-run --user --scope pytest benchmark --number-of-nodes=3` and that `--number-of-nodes` can be repeated.

Control flow: no executable code.

State and dependencies: as a package marker, it enables imports under `benchmarks`. The documented workflow depends on systemd cgroups for accurate CPU accounting.

Risks and test signals: no direct tests. The docstring aligns with `benchmarks/conftest.py`, which reads cgroup v2 CPU stats; environments without systemd/cgroup v2 may not support the intended measurement mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/benchmarks/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/benchmarks/conftest.py -->
## sources/distributed-fs/tahoe-lafs/benchmarks/conftest.py

Purpose: pytest infrastructure for Tahoe-LAFS benchmarks, parameterizing storage-node counts and creating an ephemeral grid.

Important APIs/fixtures: `pytest_addoption`, `pytest_generate_tests`, `port_allocator`, `grid`, `storage_nodes`, `client_node`, `get_cpu_time_for_cgroup`, `Benchmarker.record`, and `tahoe_benchmarker`.

Control flow: pytest receives repeated `--number-of-nodes` values, parametrizes tests, creates a temp grid with flog gatherer and introducer, starts requested storage nodes, creates a client with matching needed/happy shares, and records wall/CPU time around benchmark blocks.

State and dependencies: creates temp directories, Tahoe processes, flog gatherer, storage servers, clients, and reads `/proc/self/cgroup` plus `/sys/fs/cgroup/*/cpu.stat`. Depends on pytest-twisted, Twisted reactor, integration grid helpers, and Tahoe utilities.

Risks: assumes Linux cgroup v2 and systemd-run context; benchmark output is printed rather than persisted structurally. Session fixtures mean tests share grid state and must avoid name collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/benchmarks/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/benchmarks/test_cli.py -->
## sources/distributed-fs/tahoe-lafs/benchmarks/test_cli.py

Purpose: measures basic Tahoe CLI put/get latency against the benchmark grid.

Important tests/fixtures: autouse `cli_alias` creates alias `cli`; `test_get_put_files_sequentially` is parametrized over file sizes from 1 KB to 10 MB.

Control flow: for each size, it builds deterministic bytes, records a benchmark block for five sequential `tahoe put - cli:<name>` subprocesses with stdin data, then records five sequential `tahoe get cli:<name> -` subprocesses and verifies stdout matches.

State and dependencies: writes files into the Tahoe grid through the client node alias. Depends on the `tahoe` CLI in PATH, benchmark fixtures, subprocess pipes, and integration util `cli`.

Risks: subprocess I/O errors can deadlock if commands misbehave, though data sizes are modest. File names include loop indexes but not file size, so repeated parameter cases share prefixes and rely on overwrite or independent caps semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/benchmarks/test_cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/Makefile -->
## sources/distributed-fs/tahoe-lafs/docs/Makefile

Purpose: Sphinx-generated documentation Makefile exposing common builders.

Important targets: `help`, `clean`, `html`, `dirhtml`, `singlehtml`, `pickle`, `json`, `htmlhelp`, `qthelp`, `applehelp`, `devhelp`, `epub`, `latex`, `latexpdf`, `latexpdfja`, `text`, `man`, `texinfo`, `info`, `gettext`, `changes`, `linkcheck`, `doctest`, `coverage`, `xml`, `pseudoxml`, and `livehtml`.

Control flow: validates `sphinx-build` exists at parse time, builds with doctree output under `_build/doctrees`, passes paper and user options, and routes each builder to the appropriate `_build/<builder>` directory. `livehtml` uses `sphinx-autobuild`.

State and dependencies: writes documentation build artifacts under `_build`. Depends on Sphinx, make, optional LaTeX/makeinfo/linkcheck/autobuild tooling depending on target.

Risks: parse-time `which` failure prevents even non-build introspection. The Makefile is mostly stock, so project-specific behavior lives in `docs/conf.py` and requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/check_running.py -->
## sources/distributed-fs/tahoe-lafs/docs/check_running.py

Purpose: small utility demonstrating or checking whether a Tahoe node pidfile represents a live process.

Important API: `can_spawn_tahoe(pidfile)`.

Control flow: computes a lock path beside the pidfile, acquires a file lock, reads `pid create_time`, returns true if the pidfile is absent, checks `psutil.Process(pid)`, compares recorded create time to avoid PID reuse, returns false for a matching live process, and unlinks stale pidfiles before returning true. The module then prints the result for `running.process`.

State and dependencies: reads and may delete a pidfile; creates/uses a `.lock` file. Depends on `psutil`, `filelock`, and `pathlib`.

Risks: top-level print makes import execute behavior immediately, so it is script-like rather than library-safe. Floating-point process create time equality depends on psutil/platform precision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/check_running.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/conf.py -->
## sources/distributed-fs/tahoe-lafs/docs/conf.py

Purpose: Sphinx configuration for Tahoe-LAFS documentation.

Important settings: extensions `recommonmark` and `sphinx_rtd_theme`, source suffixes `.rst` and `.md`, `master_doc = index`, project metadata, language `en`, exclude `_build`, Pygments style, RTD HTML theme, static path, HTML help base name, and LaTeX/man/Texinfo document tuples.

Control flow: Sphinx imports this file to configure builders; there is no dynamic project import or version discovery.

State and dependencies: no persistent state; docs output paths are controlled by Sphinx/Makefile. Depends on recommonmark and sphinx_rtd_theme being installed by docs requirements.

Risks: hard-coded version/release `1.x` can drift from package version. Markdown support depends on recommonmark, which may lag modern MyST-style docs. Most settings are stock defaults, so warnings or strictness are likely configured elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/specifications/Makefile -->
## sources/distributed-fs/tahoe-lafs/docs/specifications/Makefile

Purpose: builds raster/vector derivatives for specification diagrams from SVG sources.

Important targets: default `all`, `images-png`, `images-eps`, pattern rules `%.png: %.svg` and `%.eps: %.svg`, and `clean`.

Control flow: lists SVG sources, derives PNG and EPS names, uses Inkscape to export white-background 90 DPI PNGs and EPS files, and removes generated outputs on clean.

State and dependencies: writes generated image files beside the SVGs. Depends on Inkscape command-line flags compatible with the installed version.

Risks: Inkscape CLI flags have changed across versions, so builds may fail on newer installations. Generated files are deterministic only to the extent Inkscape output is stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/specifications/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/specifications/derive_renewal_secret.py -->
## sources/distributed-fs/tahoe-lafs/docs/specifications/derive_renewal_secret.py

Purpose: reference implementation and self-test for Tahoe-LAFS lease renewal secret derivation as of 1.16.0.

Important APIs: `derive_renewal_secret`, `demo`, and `test`.

Control flow: `derive_renewal_secret` asserts exact byte lengths for lease secret, storage index, and tubid, derives client renewal secret with tagged hash, derives file renewal secret with tagged pair hash over storage index, then derives bucket renewal secret with peer id/tubid. `test` decodes base32 vectors, re-derives secrets, asserts expected base32 output, and prints success. `demo` prints one example. Both run at import/execution time.

State and dependencies: stateless cryptographic derivation using `allmydata.util.base32` and `hashutil`. No persistence.

Risks: top-level `test()` and `demo()` make import side-effectful. Assertions can be disabled with optimized Python, so this is a reference script, not hardened validation code. Test vectors provide strong regression signal for protocol compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/docs/specifications/derive_renewal_secret.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/__init__.py -->
## sources/distributed-fs/tahoe-lafs/integration/__init__.py

Purpose: package marker for Tahoe-LAFS integration tests.

Important APIs: none; the file is empty.

Control flow: none.

State and dependencies: no persistence and no imports. Its role is to make `integration` importable by tests, benchmarks, and helper modules such as `benchmarks/conftest.py`.

Risks and signals: because it has no behavior, risk is limited to package discovery. Changes here would only matter if import side effects or package metadata were introduced later.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/conftest.py -->
## sources/distributed-fs/tahoe-lafs/integration/conftest.py

Purpose: pytest fixture hub for Tahoe-LAFS integration tests, building shared grids, clients, Tor resources, and logging.

Important APIs/fixtures: `pytest_addoption`, `pytest_collection_modifyitems`, `eliot_logging`, `reactor`, `port_allocator`, `temp_dir`, `flog_binary`, `flog_gatherer`, `grid`, `introducer`, `introducer_furl`, `tor_introducer`, `tor_introducer_furl`, `storage_nodes`, `alice`, `bob`, `chutney`, `ChutneyTorNetwork`, and `tor_network`.

Control flow: options control temp retention, coverage, Foolscap forcing, and slow-test selection. Session fixtures create a temp directory, flog gatherer, introducer, grid, five storage nodes, clients, and optional Tor/Chutney network. Finalizers stop processes, dump logs, and remove tempdirs unless retained.

State and dependencies: writes `integration.eliot.json`, temp Tahoe node directories, pid/config files, flog logs, and Tor network state. Depends on Twisted, pytest-twisted, Eliot, Foolscap, Chutney, Tor binaries, Tahoe node helpers, and port allocation.

Risks: session-scoped shared mutable grid can cause test interference. Tor setup is slow and environment-sensitive. The file sets global environment variables for Tahoe HTTP timeout and Foolscap logging at import time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/grid.py -->
## sources/distributed-fs/tahoe-lafs/integration/grid.py

Purpose: object model and process orchestration helpers for integration-test Tahoe grids.

Important APIs/classes: `FlogGatherer`, `create_flog_gatherer`, `StorageServer.restart`, `create_storage_server`, `Client.reconfigure_zfec`, `Client.restart`, `Client.add_sftp`, `create_client`, `Introducer`, `_validate_furl`, `create_introducer`, `Grid.add_storage_node`, `Grid.add_client`, and `create_grid`.

Control flow: helpers spawn flog gatherer and `twistd`, create introducers and nodes through Tahoe runner utilities, wait for readiness strings/furls, register cleanup finalizers, and wrap process transports/protocols in attr classes. `Grid` allocates ports, adds storage nodes and clients, and stores them in lists/maps. `Client.add_sftp` creates an alias, generates SSH keys, writes SFTP config/accounts, and restarts the node.

State and dependencies: creates temp directories, Tahoe configs, private keys, accounts files, flog dumps, running processes, and client/server node state. Depends on Twisted deferreds/process protocols, Foolscap furl decoding, Eliot, attrs validators, pytest-twisted, and integration util helpers.

Risks: many methods mutate live object process/protocol fields on restart. Furl validation prevents hangs from missing location hints. Cleanup must handle process termination races and log dumping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/grid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_aaa_aardvark.py -->
## sources/distributed-fs/tahoe-lafs/integration/test_aaa_aardvark.py

Purpose: intentionally early integration smoke tests that instantiate expensive session fixtures and print progress.

Important tests: `test_create_flogger`, `test_create_introducer`, and `test_create_storage`.

Control flow: each test depends on one fixture (`flog_gatherer`, `introducer`, or `storage_nodes`) and prints a short confirmation. The filename sorts early so prerequisite startup happens before more substantive tests.

State and dependencies: triggers creation of flog gatherer, introducer, and storage nodes through `conftest.py`/`grid.py`. It does not add additional persistent state beyond fixture side effects.

Risks and signals: skipping these tests is safe but shifts startup cost to the first later test. Their main value is visibility and early failure isolation for grid bootstrapping rather than behavioral validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_aaa_aardvark.py -->
