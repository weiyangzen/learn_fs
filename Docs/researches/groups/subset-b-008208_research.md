# subset-b-008208 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/sts-handlers_test.go -->
# sources/object-store/minio/cmd/sts-handlers_test.go

Purpose: this is MinIO's broad integration-style IAM/STS test suite. It exercises temporary credentials generated through the internal identity provider, LDAP identity provider, OpenID web identity provider, OpenID role policies, service accounts created by STS principals, token revocation, IAM export/import, and access-management-plugin behavior. The tests run against `TestSuiteIAM` server instances spanning ErasureSD, Erasure, ErasureSet, TLS, and etcd-backed IAM variants.

Important APIs and functions: `runAllIAMSTSTests` sequences the internal-IDP tests, with `TestSTSForRoot` intentionally first because it validates bucket-list state after setup. `TestIAMInternalIDPSTSServerSuite`, `TestIAMWithLDAPServerSuite`, `TestIAMWithOpenIDServerSuite`, and related `TestIAMWithOpenID...` functions build environment-gated suites. `SetUpLDAP`, `SetUpLDAPWithNonNormalizedBaseDN`, `SetUpOpenID`, and `SetUpOpenIDs` configure external IDP settings through admin config APIs and restart IAM state. Test methods such as `TestSTS`, `TestSTSWithGroupPolicy`, `TestSTSWithDenyDeleteVersion`, `TestSTSTokenRevoke`, `TestLDAPSTS`, `TestLDAPUnicodeVariations`, `TestOpenIDSTSWithRolePolicy`, and `TestOpenIDSTSWithRolePolicyWithPolVar` are the behavioral core.

Control flow: tests typically create buckets and canned policies, attach policies to users/groups/LDAP DNs or OpenID roles, retrieve credentials via minio-go credential providers (`STSAssumeRole`, `LDAPIdentity`, `STSWebIdentity`), construct S3/admin clients using the returned access key, secret, and session token, then assert allowed and denied operations. Several flows deliberately detach policies or revoke tokens and immediately verify that temporary credentials lose access. OpenID multi-provider tests validate config acceptance for one claim-based plus one role-based provider and rejection of multiple claim-based providers.

State and persistence: the suite mutates IAM state through `madmin` APIs: users, groups, policy mappings, service accounts, token revocation records, LDAP/OpenID config, and import/export archives. IAM export/import tests build ZIP assets for policies, users, groups, service accounts, and mappings, then verify normalized LDAP DNs and service account metadata after import. External LDAP/OpenID tests depend on `_MINIO_LDAP_TEST_SERVER`, `_MINIO_OPENID_TEST_SERVER`, and `_MINIO_OPENID_TEST_SERVER_2`.

Dependencies and integration points: this file depends on test server helpers from the MinIO test harness, minio-go S3 clients, madmin admin clients, LDAP DN normalization from `github.com/minio/pkg/v3/ldap`, mock OpenID interaction helpers, global IAM/config state, and canned test identity data from external containers. It also exercises policy-variable expansion for `${aws:username}`, `${ldap:username}`, and JWT group claims.

Risks: these tests are sensitive to global test ordering, cache invalidation timing (`time.Sleep` in root STS), external IDP availability, DN normalization edge cases, and policy/session-policy intersection semantics. The explicitly named privilege-escalation regression test protects against a restricted STS principal creating a stronger service account. Unicode, Cyrillic, slash-containing DNs, and mixed-case base DNs reduce the risk of bypasses caused by string normalization drift.

Test signals: the file itself is test coverage. It provides high-value signals for STS authorization, service account inheritance/deletion/update, token revocation, object-lock delete-version denial, OpenID duration bounds, role-policy selection, policy-variable enforcement, IAM import/export compatibility, and behavior under the access management plugin.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/sts-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/stserrorcode_string.go -->
# sources/object-store/minio/cmd/stserrorcode_string.go

Purpose: generated `stringer` output for the `STSErrorCode` enum declared in `sts-errors.go`. It converts STS error constants into stable symbolic strings such as `STSAccessDenied`, `STSMissingParameter`, `STSInvalidParameterValue`, and `STSInternalError`.

Important APIs and functions: the only runtime API is `(STSErrorCode).String() string`. The sentinel `_()` function uses compile-time array indexes to fail the build if enum numeric values move without regenerating this file. `_STSErrorCode_name` is a packed string table and `_STSErrorCode_index` stores offsets into it.

Control flow: `String` bounds-checks the integer enum value. Known values return a substring from the packed table; unknown or negative values return `STSErrorCode(<n>)` using `strconv.FormatInt`.

State and persistence: there is no mutable state or persistence. The file is deterministic generated code and should be regenerated, not manually edited, when STS error constants change.

Dependencies and integration points: depends only on `strconv` and the `STSErrorCode` constants in the same package. It is used wherever MinIO logs, serializes, or tests STS error-code names.

Risks: the main risk is stale generated output after editing `sts-errors.go`. The compile-time checks catch numeric changes, but not semantic renames if the enum order stays compatible. Because STS errors are externally visible through APIs/logs, accidental renames can affect diagnostics and tests.

Test signals: no dedicated test in this file. Build success is the primary generated-code signal; any code path comparing `STSErrorCode.String()` output indirectly exercises it.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/stserrorcode_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/test-utils_test.go -->
# sources/object-store/minio/cmd/test-utils_test.go

Purpose: shared test infrastructure for MinIO command package tests. It sets global test state, creates temporary object-layer backends, signs requests, builds API URLs, registers selected handlers, executes object-layer test matrices, uploads test objects, generates TLS certificates, and unzips test data.

Important APIs and types: `TestMain` initializes global test credentials, disables conflicting environment variables and logging, sets resource limits, initializes console/internode subsystems, and calls `resetTestGlobals`. `TestServer` wraps an `httptest.Server`, temporary endpoints, credentials, object layer, and cleanup. Backend helpers include `prepareFS`, `prepareErasure`, `prepareErasure16`, `prepareErasureSets32`, `newTestObjectLayer`, `initObjectLayer`, `prepareTestBackend`, and endpoint helpers `mustGetPoolEndpoints`/`mustGetNewEndpoints`. HTTP/signing helpers include `newTestRequest`, `newTestSignedRequestV2`, `newTestSignedRequestV4`, `newTestStreamingSignedRequest`, `preSignV4`, `preSignV2`, and request corruption helpers for streaming SigV4. Execution helpers include `ExecObjectLayerAPITest`, `ExecObjectLayerTest`, `ExecObjectLayerTestWithDirs`, `ExecObjectLayerDiskAlteredTest`, and `ExecObjectLayerStaleFilesTest`.

Control flow: tests call server/backend preparation, which creates temp disks, initializes erasure server pools, configures server config/IAM/event subsystems, installs object layers into globals, then runs a supplied test callback. Request helpers calculate hashes, canonical requests, HMAC signatures, query parameters, and encoded paths before returning `http.Request` values. API registration can install all S3 routes or a focused subset by name. Cleanup paths shut down object layers, cancel contexts, remove roots, and reset globals.

State and persistence: the file heavily mutates global test state: `globalObjectAPI`, config dir/server config, endpoints, erasure flags, heal state, IAM system, active credentials, node auth token, and temp directories. Temporary disks are created under `globalTestTmpDir` and removed after tests. `newTestConfig` persists a default server config into the object layer so tests use realistic config paths.

Dependencies and integration points: it connects package tests to MinIO internals (`ObjectLayer`, erasure pools, IAM/config subsystems, object handlers), minio-go signing utilities, mux routing, auth/crypto/hash/logger packages, and Go `httptest`. Its URL helpers are reused across S3 API tests for bucket/object/multipart/notification/policy/lifecycle endpoints.

Risks: global mutable state is the largest risk; missed cleanup can leak config, IAM, heal, or object-layer state across tests. The package-level `rand.Source` is not concurrency-safe, so helpers using `randString` should not be assumed safe under arbitrary parallel use. The signing helpers intentionally duplicate production SigV4/V2 logic, which can become stale if canonicalization rules change. Temporary disk cleanup relies on callers using the provided execution wrappers.

Test signals: `TestToErrIsNil` verifies nil error conversion behavior. The rest of the file supplies indirect test signals because most command tests depend on these helpers; failures here typically appear as setup, signing, routing, upload, or cleanup failures across many suites.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/test-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/1.yaml -->
# sources/object-store/minio/cmd/testdata/config/1.yaml

Purpose: valid YAML fixture for MinIO server configuration parsing. It models a `version: v1` deployment with S3 API address `:9000`, console address `:9001`, certificate directory, two erasure pools, and FTP/SFTP option blocks.

Important structure: each pool contains four HTTPS endpoint patterns. Some hostnames use brace expansion (`server{1...2}-pool1`, `disk{1...4}`), while explicit hosts cover the remaining servers. The options section defines FTP address/passive range and SFTP address/private key.

Control flow and integration: this fixture is consumed by tests that parse configuration files into endpoint pools and service options. It specifically checks that mixed explicit and expanded HTTPS endpoints are accepted and that multiple pools can be represented.

State and persistence: static test data only; it is not mutated at runtime. If loaded successfully, it drives in-memory endpoint/config structures in parser tests.

Dependencies: depends on MinIO's YAML config parser, endpoint expansion logic, and option mapping for FTP/SFTP settings.

Risks: because endpoint patterns encode drive counts and pool topology, small edits can change parser expectations or erasure layout validation. It should remain a known-good baseline fixture.

Test signals: successful parsing should accept all endpoint schemes as remote HTTPS endpoints, preserve two pools, expand disk ranges, and load service option strings.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/2.yaml -->
# sources/object-store/minio/cmd/testdata/config/2.yaml

Purpose: second valid YAML config fixture. It is close to `1.yaml` but replaces some brace-expanded server names with explicit `server1-*` entries, giving parser tests a second accepted topology shape.

Important structure: the file declares `version: v1`, API/console/certs settings, two pools of HTTPS endpoints, disk brace expansion from `disk{1...4}`, and identical FTP/SFTP options. The first two endpoints in each pool differ from `1.yaml` by using explicit `server1-pool*` rather than `server{1...2}-pool*`.

Control flow and integration: parser tests can compare accepted configs where endpoint expansion is partly host-based and partly disk-based. This helps distinguish legal expansion differences from invalid endpoint-type or disk-count errors.

State and persistence: static fixture only. Loaded data becomes in-memory server address, console address, certs dir, pools, and optional FTP/SFTP config.

Dependencies: depends on YAML decoding and MinIO endpoint list construction.

Risks: it can look redundant with `1.yaml`, but the explicit host form is useful coverage for endpoint normalization. Removing or merging it could reduce confidence that both shorthand and expanded host forms parse equivalently.

Test signals: expected to parse as valid, with two pools and homogeneous HTTPS endpoint types per pool.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/invalid-disks.yaml -->
# sources/object-store/minio/cmd/testdata/config/invalid-disks.yaml

Purpose: negative YAML fixture for endpoint/disk-count validation. It mostly mirrors a valid two-pool HTTPS config, but one endpoint uses a single disk path (`/mnt/disk1/`) where peer endpoints use `disk{1...4}`.

Important structure: `version`, addresses, certs dir, options, and pool count are otherwise valid. The intentional defect is the first endpoint in the first pool: `https://server-example-pool1:9000/mnt/disk1/`.

Control flow and integration: config parser tests should load the YAML syntactically, expand endpoint patterns, then reject the topology because disk counts are inconsistent within the erasure pool.

State and persistence: static negative fixture only. It should not produce a usable persisted server config.

Dependencies: relies on MinIO's endpoint expansion and erasure topology validation rules.

Risks: if validation becomes too permissive, this fixture would no longer fail and could allow uneven drive topology into distributed setup. If validation rules intentionally change, this fixture must be updated with the expected error behavior.

Test signals: expected result is a validation failure tied to inconsistent disk/cardinality configuration, not a YAML syntax failure.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/invalid-disks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/invalid-types.yaml -->
# sources/object-store/minio/cmd/testdata/config/invalid-types.yaml

Purpose: negative YAML fixture for endpoint type homogeneity. It mixes a local filesystem endpoint (`/mnt/disk{1...4}/`) into an otherwise HTTPS distributed pool.

Important structure: all top-level config fields and options match the valid examples, but the first endpoint in the first pool lacks an HTTP/S scheme while the remaining endpoints are HTTPS URLs.

Control flow and integration: parser tests should accept the YAML syntax, then reject the endpoint set during endpoint-type validation. Distributed pools must not mix local path endpoints and remote URL endpoints in this shape.

State and persistence: static fixture only; successful parsing should not persist or initialize this topology.

Dependencies: depends on endpoint type detection (`path` versus URL endpoint) and pool validation code.

Risks: accepting mixed endpoint types can lead to ambiguous local/remote disk ownership and broken erasure setup. The fixture protects the validation boundary from regressions.

Test signals: expected failure is a semantic endpoint-type validation error, distinct from malformed YAML or disk-count mismatch.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/invalid-types.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/invalid.yaml -->
# sources/object-store/minio/cmd/testdata/config/invalid.yaml

Purpose: negative YAML config fixture for schema/value validation. It keeps the same endpoint topology as valid examples but leaves `version` empty.

Important structure: `version:` has no value. Address, console address, certs dir, pools, and FTP/SFTP options are otherwise syntactically valid.

Control flow and integration: parser tests should reject this file before treating it as a valid server config because the version field is required for config compatibility handling.

State and persistence: static invalid fixture; it should not result in persisted runtime config.

Dependencies: relies on YAML decoding and MinIO's config schema validation.

Risks: if missing version values are accepted silently, future config migrations may lack a reliable format discriminator. Conversely, changing the required version semantics requires adjusting this test fixture.

Test signals: expected failure is missing/invalid config version, not endpoint expansion or service option parsing.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/testdata/config/invalid.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier-handlers.go -->
# sources/object-store/minio/cmd/tier-handlers.go

Purpose: admin HTTP handlers for managing remote transition tiers. These endpoints let authorized admins add, list, edit, remove, verify, and inspect stats for tier backends used by ILM/object transition.

Important APIs and functions: `AddTierHandler`, `ListTierHandler`, `EditTierHandler`, `RemoveTierHandler`, `VerifyTierHandler`, and `TierStatsHandler` are methods on `adminAPIHandlers`. Admin errors defined here include tier already exists/not found, non-uppercase names, missing bucket, invalid credentials, and reserved name. Handlers authorize with `validateAdminReq` using `policy.SetTierAction` or `policy.ListTierAction`.

Control flow: add/edit decrypt the encrypted admin request body with the caller's secret key, unmarshal JSON into `madmin.TierConfig` or `madmin.TierCreds`, reload disk config to catch missed peer updates, mutate `globalTierConfigMgr`, save the config, then broadcast `LoadTransitionTierConfig`. Add rejects reserved storage class names (`STANDARD`, `RRS`) and supports a `force` query to ignore in-use backend checks. Remove reloads config, parses `force=true`, removes from the manager, saves, and notifies peers. Verify delegates to `TierConfigMgr.Verify`. Stats loads data usage, merges last-day stats from `globalNotificationSys`, marshals `madmin.TierInfo`, and returns JSON.

State and persistence: handlers persist tier config through `TierConfigMgr.Save` into the MinIO metadata bucket. List returns `X-MinIO-TierCfg-RefreshedAt` so clients can see refresh age. Mutating handlers update in-memory and persisted state and ask peer nodes to reload transition tier config.

Dependencies and integration points: depends on `madmin-go` request/response types and request encryption, `jsoniter`, MinIO admin auth/error plumbing, lifecycle storage-class constants, mux path variables, global data-usage loading, and notification system tier stats.

Risks: stale config across distributed nodes is mitigated by reload-before-write and peer notification, but concurrent edits can still race at the object-store persistence boundary. Decrypting with the admin credential secret means body handling must remain aligned with madmin clients. Reserved-name validation prevents ambiguity with internal storage classes.

Test signals: this file is exercised indirectly by admin API and tier manager tests. Useful coverage would verify encrypted body failures, unauthorized policies, reserved names, force semantics, reload/save failures, peer notification, and stats JSON with daily bins.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier-last-day-stats.go -->
# sources/object-store/minio/cmd/tier-last-day-stats.go

Purpose: maintains rolling 24-hour per-tier transfer statistics for remote tiers. It stores hourly `tierStats` bins and can merge per-node maps for cluster-wide reporting.

Important APIs and types: `lastDayTierStats` contains `[24]tierStats` and `UpdatedAt`. Methods include `addStats`, `forwardTo`, `clone`, and `merge`. `DailyAllTierStats` is a map from tier name to `lastDayTierStats`, with `merge` and `addToTierInfo`.

Control flow: `addStats` forwards the ring buffer to `time.Now`, chooses the current hour index, and adds the incoming stats. `forwardTo` clears bins between the previous update hour and target hour; if 24 or more hours elapsed, it clears all bins. `merge` clones both inputs, forwards the older one to the newer timestamp, and adds corresponding bins. `DailyAllTierStats.addToTierInfo` overlays internal stats onto `madmin.TierInfo.DailyStats`.

State and persistence: this type is in-memory aggregation state, with msgp serialization generated in the companion `_gen.go` file. The 24 fixed bins are hour-of-day indexed, so `UpdatedAt` is required to know which bins are current.

Dependencies and integration points: depends on `tierStats` from MinIO data-usage/tier accounting and `madmin.TierInfo` response structs. `TierStatsHandler` integrates these stats into admin API output.

Risks: because bins are indexed by hour, clock jumps and time-zone assumptions can affect which bins are cleared. `forwardTo` treats any elapsed duration below one hour as no movement, and elapsed durations of 24 hours or more as total expiration. Merge correctness depends on forwarding both nodes to a common timestamp before summing.

Test signals: generated serialization tests cover msgp round trips. Behavioral tests should focus on `forwardTo` clearing boundaries, 24-hour expiration, and merging maps with different `UpdatedAt` values.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier-last-day-stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier-last-day-stats_gen.go -->
# sources/object-store/minio/cmd/tier-last-day-stats_gen.go

Purpose: generated msgp serialization implementation for `DailyAllTierStats` and `lastDayTierStats`. It lets rolling tier stats be encoded/decoded efficiently for persistence or inter-node exchange.

Important APIs and functions: for both types, the file implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`. `DailyAllTierStats` serializes as a map of tier name to a two-field stat struct. `lastDayTierStats` serializes fields `Bins` and `UpdatedAt`.

Control flow: decoders read map headers, clear or allocate destination maps, dispatch by field name, skip unknown fields, and wrap errors with field paths. `Bins` must decode as an array of exactly 24 elements; mismatches return `msgp.ArrayError`. Encoders write map/array headers and delegate each `tierStats` bin to its generated msgp methods.

State and persistence: no independent state; this code defines the wire/storage representation of daily tier stats. It preserves forward compatibility by skipping unknown fields but is strict on the fixed bin array length.

Dependencies and integration points: depends on `github.com/tinylib/msgp/msgp` and generated msgp support for `tierStats`. It is generated from `tier-last-day-stats.go` via the `msgp` directive and must stay in sync with struct fields.

Risks: manual edits will be overwritten. Changing the number of bins or field names requires regeneration and compatibility review. Map iteration order is intentionally nondeterministic for maps, so tests should not depend on byte-for-byte order for multi-entry maps unless sorted elsewhere.

Test signals: `tier-last-day-stats_gen_test.go` checks marshal/unmarshal, encode/decode, skip behavior, msg size bounds, and benchmarks generated paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier-last-day-stats_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier-last-day-stats_gen_test.go -->
# sources/object-store/minio/cmd/tier-last-day-stats_gen_test.go

Purpose: generated tests and benchmarks for msgp serialization of `DailyAllTierStats` and `lastDayTierStats`.

Important APIs and functions: `TestMarshalUnmarshalDailyAllTierStats`, `TestEncodeDecodeDailyAllTierStats`, `TestMarshalUnmarshallastDayTierStats`, and `TestEncodeDecodelastDayTierStats` validate both byte-slice and stream msgp paths. Benchmarks cover marshal, append, unmarshal, encode, and decode for both types.

Control flow: each marshal/unmarshal test encodes an empty value, decodes it back, asserts no leftover bytes, and verifies `msgp.Skip` consumes the full buffer. Encode/decode tests write to a `bytes.Buffer`, compare the encoded size to `Msgsize`, decode into a fresh value, and ensure `msgp.NewReader(...).Skip()` succeeds.

State and persistence: no external state. The tests validate generated serialization contracts for empty/default values; persistence semantics are limited to msgp round-trip integrity.

Dependencies and integration points: depends on `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`. It is tied to the generated serializer file and should be regenerated with it.

Risks: generated tests only use zero values, so they do not detect data loss for populated maps, non-zero `UpdatedAt`, or non-empty `tierStats` bins. They mainly catch broken generated plumbing, not domain-specific aggregation behavior.

Test signals: strong signal for msgp API compatibility and skip support, weak signal for real tier-stat content. Additional hand-written tests would be needed for populated stats and bin merging.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier-last-day-stats_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier-sweeper.go -->
# sources/object-store/minio/cmd/tier-sweeper.go

Purpose: decides when a local object mutation should enqueue deletion of a corresponding remote-tier object. It prevents transitioned remote objects from being orphaned after overwrites/deletes while respecting bucket versioning semantics.

Important APIs and types: `objSweeper` tracks bucket/object, requested version ID, bucket versioning state, transition status/tier/version/name, and helper methods `WithVersion`, `WithVersioning`, `GetOpts`, `SetTransitionState`, `shouldRemoveRemoteObject`, and `Sweep`. `jentry` is the tier deletion journal entry. `deleteObjectFromRemoteTier` resolves a `WarmBackend` and calls `Remove`.

Control flow: callers create a sweeper before an operation, use `GetOpts` to fetch the affected object version, call `SetTransitionState` from object info when transition metadata exists, perform the local operation, then call `Sweep`. `shouldRemoveRemoteObject` first requires lifecycle transition status `TransitionComplete`. It then deletes remote data if bucket versioning is disabled, if versioning is suspended, or if versioning is enabled and a specific version ID was targeted. Versioning-enabled deletes without a version ID only add a delete marker and do not remove remote data.

State and persistence: `Sweep` enqueues into `globalExpiryState` rather than synchronously deleting. Actual remote removal is journal-driven. The sweeper itself is per-operation transient state.

Dependencies and integration points: depends on lifecycle transition constants, `ObjectOptions`, `TransitionedObject`, `nullVersionID`, `globalExpiryState`, `globalTierConfigMgr`, and `WarmBackend.Remove`. It integrates object APIs with ILM tier cleanup.

Risks: incorrect versioning decisions can delete remote data still referenced by an older version or leak remote data after overwrite/delete. The suspended-bucket null-version handling in `GetOpts` is especially important for matching the object that will be overwritten. Remote driver lookup failures surface when journal processing calls `deleteObjectFromRemoteTier`.

Test signals: no tests in this file. Good coverage would enumerate disabled/suspended/enabled versioning with and without explicit version IDs, incomplete transition state, and journal entry fields.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier-sweeper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier.go -->
# sources/object-store/minio/cmd/tier.go

Purpose: central configuration and metrics manager for MinIO remote transition tiers. It validates remote tier definitions, caches warm backend drivers, serializes tier config, persists it to MinIO metadata storage, reloads it across distributed nodes, and exposes tier metrics.

Important APIs and types: `TierConfigMgr` holds a mutex, `drivercache`, `Tiers` map, and `lastRefreshedAt`. Methods include `Add`, `Remove`, `Verify`, `Edit`, `Bytes`, `configReader`, `getDriver`, `Reload`, `Save`, `Init`, `ListTiers`, `IsTierValid`, `TierType`, and `Empty`. `tierMetrics` records Prometheus TTLB histograms plus success/failure counters, with `Observe`, `logSuccess`, `logFailure`, and `Report`. Config constants define `tier-config.bin`, format/version headers, and `tierConfigPath`.

Control flow: `Add` validates uppercase unique names, creates a warm backend, optionally checks `InUse`, and inserts config/driver. `Remove` resolves the driver, optionally rejects non-empty/in-use backends, then deletes config/cache entries. `Edit` updates credentials by tier type, rebuilds the warm backend, and replaces the cache. `Bytes` prefixes msgp data with two little-endian uint16 headers for format and version. `configReader` wraps bytes in a hash reader and optionally encrypts with KMS before `Save` writes to `minioMetaBucket/tier-config.bin`. `Reload` calls `loadTierConfig`, clears cache and current tiers, copies loaded tiers, and updates refresh time. `Init` reloads once and starts periodic jittered refresh in distributed erasure mode.

State and persistence: authoritative tier config is persisted as a msgpack blob in the metadata bucket, optionally encrypted when KMS is enabled. In-memory state includes the tier map, cached `WarmBackend` drivers, metrics counters, and last refresh timestamp. `drivercache` is intentionally not serialized.

Dependencies and integration points: integrates with `madmin.TierConfig`, warm backend constructors/checks, `ObjectLayer` config storage, KMS/S3 encryption helpers, hash readers, Prometheus metrics, admin handlers, lifecycle transition code, and distributed notification/refresh behavior.

Risks: `Save` calls `globalTierConfigMgr.configReader(ctx)` instead of the receiver's `configReader`, so alternate manager instances must be treated carefully. Concurrent admin updates rely on locking inside the manager but persistence-level lost updates remain a consideration. Credential edit validation differs by tier type; missing GCS/MinIO credentials fail explicitly, while S3/Azure allow partial updates. Backward compatibility depends on preserving header format/version handling.

Test signals: `tier_test.go` covers metrics counter reporting. Generated msgp tests cover serialization plumbing. Additional coverage should focus on add/edit/remove validation, KMS and non-KMS `configReader`, load version errors, reload-not-found behavior, and concurrent edits.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier_gen.go -->
# sources/object-store/minio/cmd/tier_gen.go

Purpose: generated msgp serializer for `TierConfigMgr`. It serializes only the persistent `Tiers` map and deliberately omits mutexes, driver cache, and refresh timestamp according to struct tags.

Important APIs and functions: implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*TierConfigMgr`. The encoded object is a one-field map containing `"Tiers"`, with string keys and `madmin.TierConfig` values.

Control flow: decoders allocate or clear `z.Tiers`, read each tier name and delegate value decoding to `madmin.TierConfig.DecodeMsg`/`UnmarshalMsg`, skip unknown fields, and wrap errors with field/key context. Encoders write the one-field map and iterate over `z.Tiers`.

State and persistence: this code defines the serialized body used by `TierConfigMgr.Bytes` after the four-byte format/version header. It does not serialize `drivercache` or `lastRefreshedAt`, so those are reconstructed after load.

Dependencies and integration points: depends on `madmin-go/v3` generated msgp support and `tinylib/msgp`. It is generated from `tier.go` and consumed by tier config save/load paths.

Risks: map iteration order is nondeterministic, so serialized byte order can vary for multiple tiers. Field-name changes or moving persistence-relevant fields without regenerating can break config compatibility. Because driver cache is omitted, load paths must always initialize or rebuild `drivercache`.

Test signals: `tier_gen_test.go` validates empty-value marshal/unmarshal and encode/decode paths. Production load/save paths add coverage for real tier configs when admin tier tests exist.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier_gen_test.go -->
# sources/object-store/minio/cmd/tier_gen_test.go

Purpose: generated serializer tests and benchmarks for `TierConfigMgr`.

Important APIs and functions: `TestMarshalUnmarshalTierConfigMgr` validates `MarshalMsg`, `UnmarshalMsg`, and `msgp.Skip`. `TestEncodeDecodeTierConfigMgr` validates stream encode/decode and `Msgsize` bound behavior. Benchmarks cover marshal, append, unmarshal, encode, and decode paths.

Control flow: the tests use a zero-value `TierConfigMgr`, encode it, decode it, assert no leftover bytes, and confirm the reader can skip the encoded object. Benchmarks repeatedly exercise the generated functions and report allocations/bytes.

State and persistence: no external state. The test validates serializer shape for an empty manager, not full persisted tier configs.

Dependencies and integration points: depends on `testing`, `bytes`, and `tinylib/msgp`. It is tied to `tier_gen.go` and should be regenerated with it.

Risks: because it uses an empty `TierConfigMgr`, it will not catch serialization bugs in populated `madmin.TierConfig` values, map entries, credential fields, or driver-cache reconstruction. It also does not validate the four-byte format/version header used by `TierConfigMgr.Bytes`.

Test signals: good generated-code smoke coverage; limited domain coverage. Hand-written tier config load/save tests are still needed.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/tier_test.go -->
# sources/object-store/minio/cmd/tier_test.go

Purpose: hand-written unit test coverage for tier metrics reporting.

Important APIs and functions: `TestTierMetrics` exercises `globalTierMetrics.Observe`, `logSuccess`, `logFailure`, and `Report`. It refers to metric names `tierRequestsSuccess` and `tierRequestsFailure`.

Control flow: the test observes one latency sample for tier `WARM-1`, records ten successes and five failures, calls `Report`, then aggregates returned metric values by description name and asserts expected totals.

State and persistence: mutates package-level `globalTierMetrics`, especially its request counters and Prometheus histogram. There is no persistence. Because the global is shared, test ordering or repeated execution in the same process can affect counts if other tests mutate the same tier metric names.

Dependencies and integration points: depends on the metrics code in `tier.go` and MinIO's `MetricV2` descriptions. It indirectly checks that `Report` includes counter metrics alongside histogram output.

Risks: the test is narrow and uses a global counter map without reset, so additions of other tests using the same tier name could make it flaky. It does not assert histogram buckets or labels, only success/failure totals.

Test signals: provides a small but useful signal that tier success/failure counters are incremented and surfaced by `Report`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/tier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/typed-errors.go -->
# sources/object-store/minio/cmd/typed-errors.go

Purpose: centralizes package-level sentinel errors for common MinIO command-layer failure conditions. These errors are used for identity, IAM, S3 API, multipart upload, range, decompression, RPC, and SFTP validation paths.

Important APIs and values: exported names are package-private `var` sentinels such as `errInvalidArgument`, `errMethodNotAllowed`, `errSignatureMismatch`, `errDataTooLarge`, `errServerNotInitialized`, `errInvalidRange`, `errNoSuchUser`, `errNoSuchServiceAccount`, `errNoSuchPolicy`, `errIAMNotInitialized`, `errUploadIDNotFound`, `errSessionPolicyTooLarge`, `errSftpPublicKeyWithoutCert`, and `errGroupNameContainsReservedChars`.

Control flow: there are no functions. Callers compare, wrap, or convert these sentinel errors through API/admin error conversion code. Keeping them as `errors.New` variables enables identity comparisons with `errors.Is` when wrapped.

State and persistence: immutable process-level sentinel values. No runtime state or persistence.

Dependencies and integration points: depends only on Go `errors`. Integrates broadly with object API handlers, IAM subsystem, admin APIs, STS/session policy validation, multipart upload handling, decompression checks, and SFTP authentication.

Risks: changing message text can alter client-facing diagnostics or tests if conversion code exposes the error string. Replacing sentinel variables with new instances in other files would break identity comparisons. Some comments reveal specific behavior expectations, such as LDAP warning text and session policy max size.

Test signals: no local tests. Coverage is indirect through handlers and subsystem tests that expect these errors to map to specific API/admin responses.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/typed-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/untar.go -->
# sources/object-store/minio/cmd/untar.go

Purpose: streams tar archives, optionally compressed with several formats, into object uploads through a caller-supplied `putObject` callback. It is used when MinIO needs to ingest archive contents as individual objects.

Important APIs and types: `detect` identifies compression by magic headers. `format` enumerates unknown, gzip, zstd, LZ4, S2, and BZ2. `untarOptions` controls directory handling, error tolerance, and prefixing. `disconnectReader` wraps an upstream reader so it can be closed to prevent further reads. `untar` is the main archive extraction function. `bz2Limiter` caps bzip2 concurrency at about half `GOMAXPROCS`.

Control flow: `untar` wraps the input in `bufio.Reader`, detects compression, installs the appropriate decompressor, then iterates `tar.Reader.Next`. It normalizes entry names, skips root entries and symlinks/unsupported types, optionally appends a directory slash, and applies `prefixAll`. Small files (`<= xioutil.MediumBlock`) are fully read into pooled memory and uploaded asynchronously with a 16-slot semaphore. Larger entries stream synchronously through `disconnectReader`. If `ignoreErrs` is false, the loop checks the first async error before continuing and returns sync errors immediately; otherwise errors are logged with `s3LogIf`.

State and persistence: the function does not persist directly; persistence is delegated to `putObject`. It uses pooled buffers for medium objects and goroutines for concurrent small uploads. Header modification time is normalized to `time.Now()` for non-positive large-file modtimes to avoid invalid resulting objects.

Dependencies and integration points: depends on archive/tar, gzip/zstd/lz4/s2/bzip2 libraries, MinIO `xioutil.ODirectPoolMedium`, path helpers (`pathJoin`, `trimLeadingSlash`, `slashSeparator`), and caller-provided object upload logic.

Risks: tar path handling must prevent unexpected absolute/root names; this code cleans and trims leading slashes but still trusts callback-level object semantics. Async small-file uploads require careful error propagation and buffer lifetime management. For small files with invalid modtime, no modtime normalization occurs before `header.FileInfo()` is passed, unlike the large-file path. Decompression limits are explicit for zstd window size and bzip2 concurrency, but archive bombs can still produce many entries.

Test signals: no local tests here. Valuable tests would cover all compression magic headers, symlink skipping, directory ignore/prefix behavior, async error propagation, context cancellation for bzip2, path normalization, and mixed small/large entries.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/untar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/update-notifier.go -->
# sources/object-store/minio/cmd/update-notifier.go

Purpose: formats the server update notification shown when a newer MinIO release is available.

Important APIs and functions: `prepareUpdateMessage(downloadURL string, older time.Duration) string` decides whether to return a message and selects JSON/plain formatting. `colorizeUpdateMessage(updateString, newerThan string) string` builds a terminal-friendly boxed notification.

Control flow: `prepareUpdateMessage` returns empty when no download URL is available or `older <= 0`. It uses `humanize.RelTime` to express how far behind the current release is. In JSON mode (`globalServerCtxt.JSON`) it returns a plain sentence with the update URL. Otherwise it delegates to `colorizeUpdateMessage`. The colorized path computes visible line widths without ANSI escapes, checks terminal width with `pb.GetTerminalWidth`, falls back to plain lines if too narrow, and uses Unicode box drawing except on Windows, where ASCII borders are used.

State and persistence: no persistence. It reads global server context and runtime OS, and produces display strings.

Dependencies and integration points: depends on `go-humanize`, `cheggaaa/pb` terminal-width detection, MinIO color helpers, `runtime.GOOS`, and `globalWindowsOSName`. It integrates with startup/update-check logging paths.

Risks: terminal-width and ANSI handling can regress layout; width calculations are byte-length based, which is acceptable for the current English templates but would be fragile for wide characters. JSON mode deliberately avoids color/box formatting so machine-readable logs remain simple.

Test signals: no local tests. Useful tests would assert empty cases, JSON message format, narrow-terminal fallback, and Windows ASCII border selection.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/update-notifier.go -->
