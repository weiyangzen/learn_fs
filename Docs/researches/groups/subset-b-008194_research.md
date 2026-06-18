# subset-b-008194 grouped research

This grouped report covers MinIO server HTTP tracing/statistics helpers, range parsing, IAM persistence and authorization layers, ILM worker configuration, platform-specific directory emptiness checks, and JWT authentication helpers in `sources/object-store/minio/cmd`. Each section is wrapped with reconciliation markers for deterministic split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/http-stats.go -->
# sources/object-store/minio/cmd/http-stats.go

## Purpose

`http-stats.go` defines the in-memory counters used by MinIO to track aggregate network bytes, per-bucket S3 bytes, process-wide HTTP API counts, bucket-level HTTP API counts, request queue depth, rejected requests, errors, cancellations, and request duration histograms. It is part of the observability surface consumed by server info/admin APIs and Prometheus metrics.

## Important APIs, Types, And Control Flow

`connStats` owns atomic byte counters for internode and S3 traffic. Its `inc*` methods use `atomic.AddUint64`, its `get*` methods use `atomic.LoadUint64`, and `toServerConnStats` materializes the public stats DTO. `bucketConnStats` adds per-bucket S3 in/out byte accounting behind an `RWMutex` and returns copies from `getS3InOutBytes` and `getBucketS3InOutBytes` so callers do not share mutable map state.

`HTTPAPIStats` is a mutex-protected map from API name to count with `Inc`, `Dec`, `Get`, and `Load`. `Load(toLower)` copies keys and optionally normalizes API names. `HTTPStats` embeds several `HTTPAPIStats` values for current, total, error, 4xx, 5xx, and canceled request counts. `toServerHTTPStats` snapshots the counters, notably using `atomic.SwapUint64` for `s3RequestsIncoming`, so that field reports and resets interval-style arrivals while other totals remain cumulative. `updateStats` records total requests, Prometheus TTFB duration, HTTP 499 cancellations, and 4xx/5xx buckets.

`bucketHTTPStats` stores a map of bucket name to `bucketHTTPAPIStats`. `updateHTTPStats(bucket, api, nil)` increments active bucket requests; the later call with a `ResponseRecorder` decrements active requests, increments total, classifies status, and observes `bucketHTTPRequestsDuration`.

## State, Dependencies, Integration, Risks, And Tests

State is entirely process-local and reset on restart, except that admin callers may periodically read and persist snapshots elsewhere. Dependencies include `internal/http.ResponseRecorder`, `net/http`, `sync/atomic`, `sync.RWMutex`, and Prometheus collectors. Integration points are S3 request handlers, bucket deletion cleanup, server-info serialization, and metrics endpoints. Risks include paired active-request increments/decrements getting out of balance when middleware paths diverge, byte counters wrapping, `s3RequestsIncoming` being destructive on read, and bucket stats growing until explicit delete. `http-tracer_test.go` adds race-oriented tests for `HTTPStats`, `HTTPAPIStats`, and `bucketHTTPStats`, giving a direct signal that the map locks are required for concurrent request/update/read paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/http-stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/http-tracer.go -->
# sources/object-store/minio/cmd/http-tracer.go

## Purpose

`http-tracer.go` implements MinIO's server-side HTTP trace middleware. It records request and response metadata, optional bodies, timing, byte counts, source IP, sanitized query strings, and normalized handler names, then publishes `madmin.TraceInfo` events to `globalTrace` subscribers.

## Important APIs, Types, And Control Flow

`redactLDAPPwd` uses `ldapPwdRegex` to replace an `LDAPPassword` query parameter value with a redaction marker while preserving surrounding query content. `getOpName` converts Go function names into stable operation labels such as `s3.*`, `admin.*`, `storageR.*`, `peer.*`, and health names. `httpTracerMiddleware` wraps the response writer with `xhttp.ResponseRecorder`, wraps the request body with `xhttp.RequestRecorder`, installs a `mcontext.TraceCtxt` on the request context, executes the handler, and only builds a trace if subscribers exist for S3 or internal traces.

After the handler returns, the middleware reconstructs request headers including Host and either Content-Length or Transfer-Encoding, computes input bytes from recorded body size plus header lengths, strips default HTTP/HTTPS ports from the node name, chooses `TraceS3` when the traced function starts with `s3.`, and publishes `madmin.TraceInfo` with request, response, and latency/TTFB stats. `httpTrace` is the per-handler wrapper that discovers the handler function name with `runtime.FuncForPC`, enables request and response body logging according to `logBody`, and always logs error bodies. `httpTraceAll` and `httpTraceHdrs` are convenience wrappers for body-inclusive and headers-only tracing.

## State, Dependencies, Integration, Risks, And Tests

State is request-scoped until publication; global state is `globalTrace`, distributed node name flags, and response/request recorder buffers. Dependencies include `madmin-go`, `internal/http`, `internal/handlers`, and `internal/mcontext`. Integration is broad: every HTTP handler that uses `httpTrace*` participates in trace naming and body capture. Risks include sensitive data in logged bodies when `logBody` is true, incomplete query redaction beyond LDAP password, body buffering cost, byte-count approximation by adding header key/value lengths, and traces not emitted if handlers bypass the context wrapper. `http-tracer_test.go` validates LDAP password redaction and indirectly shares the package with HTTP stats race tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/http-tracer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/http-tracer_test.go -->
# sources/object-store/minio/cmd/http-tracer_test.go

## Purpose

`http-tracer_test.go` verifies LDAP password query redaction and adds concurrency tests for the HTTP stats types defined in `http-stats.go`. The file acts as a regression suite for trace sanitization and for prior data races in shared HTTP metric maps.

## Important Tests And Control Flow

`TestRedactLDAPPwd` checks empty input, LDAP password in the middle, beginning, and end of a query string, plus a non-LDAP query that should remain unchanged. The expected output preserves all non-password segments and replaces only the password value. The regex therefore needs to handle both prefixed and suffix-only query fragments, not just canonical URL-encoded query parsing.

`TestRaulStatsRaceCondition` creates a `HTTPStats`, launches many writer goroutines that call `updateStats` and direct `HTTPAPIStats.Inc`, and many reader goroutines that call `toServerHTTPStats` and `Load`. It asserts that some total requests survive concurrent activity. `TestRaulHTTPAPIStatsRaceCondition` stresses `HTTPAPIStats.Inc` while readers call `Load`, then asserts no increments were lost for a single API key. `TestRaulBucketHTTPStatsRaceCondition` repeatedly pairs active bucket request updates with response-completion updates and loads bucket stats.

## State, Dependencies, Integration, Risks, And Signals

The tests use goroutines, `sync.WaitGroup`, microsecond sleeps, and `xhttp.ResponseRecorder`. Their strongest signal appears when run with Go's `-race`; without race detection, they still catch obvious lost updates for `HTTPAPIStats`. They cover nil-recorder active request flow and response-recorder completion flow for bucket stats. Gaps remain around `httpTracerMiddleware` end-to-end publication, trace body redaction, status 499 classification, Prometheus histogram side effects, and active-request decrement balance on panic or early return paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/http-tracer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/httprange.go -->
# sources/object-store/minio/cmd/httprange.go

## Purpose

`httprange.go` parses and renders the S3-supported subset of HTTP `Range` headers for object GET requests. It converts string forms such as `bytes=1-10`, `bytes=10-`, and `bytes=-30` into an `HTTPRangeSpec`, then computes concrete object offsets and lengths for a known resource size.

## Important APIs, Types, And Control Flow

`HTTPRangeSpec` has `IsSuffixLength`, `Start`, and `End`. A nil spec means no Range header and therefore the full resource. For suffix ranges, `Start` is stored as a negative length and `End` is `-1`. `GetLength(resourceSize)` validates negative resource sizes, handles nil/full-object ranges, clamps suffix ranges to resource size, rejects starts beyond the resource with `InvalidRange`, clamps explicit end offsets past EOF, and computes inclusive byte counts. `GetOffsetLength` calls `GetLength`, then returns start offset plus length, converting suffix ranges with `max(resourceSize + Start, 0)`.

`parseRequestRangeSpec` requires the `bytes=` prefix, rejects missing `-`, rejects signed byte positions with a leading `+`, parses begin/end as non-negative integers, rejects multi-range strings because S3/MinIO does not support RFC multi-ranges here, and returns `errInvalidRange` for syntactically valid but unsatisfiable or reversed ranges. `String(resourceSize)` renders the concrete inclusive range after resource-size clamping. `ToHeader` reconstructs the original header shape and validates reversed or malformed specs.

## State, Dependencies, Integration, Risks, And Tests

There is no persistent state; the type is a pure request parser used by object GET/range handling. Dependencies are only `errors`, `fmt`, `strconv`, and `strings`, plus package-level `InvalidRange` and `errInvalidRange`. Risks include unsupported multi-range behavior, `ToHeader` converting `int64` through `int` before string conversion on narrow architectures, subtle distinction between parse errors and invalid-range errors, and nil specs needing careful handling by callers. `httprange_test.go` covers valid offsets, suffix clamping, parse failures, invalid range classification, and round-tripping with `ToHeader`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/httprange.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/httprange_test.go -->
# sources/object-store/minio/cmd/httprange_test.go

## Purpose

`httprange_test.go` validates the supported S3 range grammar and the conversion from parsed range specs to object offsets, lengths, and header strings.

## Important Tests And Control Flow

`TestHTTPRequestRangeSpec` uses a resource size of 10 bytes. Valid cases cover open-ended ranges, closed ranges, single-byte ranges, suffix ranges, and suffix ranges larger than the resource. For each, the test parses the header and checks `GetOffsetLength`. It then verifies unparsable strings such as `bytes=-`, `bytes==1-10`, non-numeric values, signed values, and multi-range input return parse errors rather than `InvalidRange`. Finally it checks syntactically valid but unsatisfiable values such as `bytes=5-3`, `bytes=10-`, `bytes=100-`, and `bytes=-0` are classified as invalid ranges either during parsing or offset computation.

`TestHTTPRequestRangeToHeader` parses valid range strings and checks that `ToHeader` reproduces the same header. It also includes malformed inputs where parsing should fail or `ToHeader` should reject the constructed state.

## State, Dependencies, Integration, Risks, And Signals

The test file depends only on Go's `testing` package and package-local range helpers. Its signal is strong for single-range grammar and EOF clamping but does not cover nil `HTTPRangeSpec`, `String(resourceSize)`, negative resource sizes, or very large offsets that might expose the `int64` to `int` conversion in `ToHeader`. The tests intentionally document that multi-range headers are unsupported even though RFC HTTP range syntax permits them.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/httprange_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/iam-etcd-store.go -->
# sources/object-store/minio/cmd/iam-etcd-store.go

## Purpose

`iam-etcd-store.go` implements `IAMStorageAPI` over etcd. It stores IAM identities, groups, policies, and policy mappings under the same logical key prefixes used by the object-store backend, handles optional KMS encryption/decryption, loads bulk IAM data from prefix scans, and exposes an etcd watch stream for live cache updates.

## Important APIs, Types, And Control Flow

`IAMEtcdStore` embeds an `iamCache`, protects it with an `RWMutex`, records the active `UsersSysType`, and holds an `etcd.Client`. Its lock/rlock methods return the cache to satisfy `IAMStorageAPI`. `saveIAMConfig` marshals JSON, encrypts when `GlobalKMS` is configured using a context based on `.minio.sys` metadata paths, and calls `saveKeyEtcd`. `loadIAMConfig`, `loadIAMConfigBytes`, and `getIAMConfig` read keys, decrypt through shared `decryptData`, and unmarshal using jsoniter.

Bulk loaders use etcd prefix scans with a 30 second `defaultContextTimeout`. Policies are loaded from `iamConfigPoliciesPrefix` by `loadPolicyDocs`, parsing each `PolicyDoc`. Users are loaded by user type from regular, service-account, or STS prefixes; expired identities and invalid temporary credentials are deleted along with their policy mappings. Groups are first listed with keys-only prefix scans, normalized by `extractPathPrefixAndSuffix`, then loaded individually. Policy mappings are loaded from user, STS, service-account, or group policydb prefixes into `xsync.MapOf`.

`watch` starts a goroutine that watches a prefix with keys-only events, retries after watch channel closure or watch errors, and emits `iamWatchEvent` values for create/modify and delete events.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is etcd key/value data under IAM config prefixes, optionally encrypted. Integration is through `IAMStoreSys.LoadIAMCache`, notification handlers, and `IAMSys.periodicRoutines` watcher support. Dependencies include etcd v3, mvcc key values, MinIO config/KMS helpers, jsoniter, and xsync maps. Risks include path extraction for identities containing slashes, expensive per-group reloads after key-only scans, best-effort deletion of expired credentials, watch goroutine lifetime/channel blocking, and consistency around TTL options passed to lower-level etcd save helpers. `iam-etcd-store_test.go` covers prefix/suffix extraction normalization, but most behavior relies on shared IAM store tests or integration tests with etcd.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/iam-etcd-store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/iam-etcd-store_test.go -->
# sources/object-store/minio/cmd/iam-etcd-store_test.go

## Purpose

`iam-etcd-store_test.go` tests the path-normalization helper used when deriving IAM entity names from etcd keys.

## Important Tests And Control Flow

`TestExtractPrefixAndSuffix` supplies group-style and nested config paths such as `config/iam/groups/foo.json`, `config/iam/groups/./foo.json`, and `config/iam/groups/foo/config.json`. It asserts that `extractPathPrefixAndSuffix` removes the configured prefix, removes either `.json` or `config.json`-style suffixes, cleans the path, and returns `foo`.

## State, Dependencies, Integration, Risks, And Signals

The test has no external dependencies beyond `testing`. It gives direct coverage for a small but important helper used by etcd bulk loaders and list-to-name conversion. The gap is that it does not spin up etcd, verify encryption/decryption, expired credential deletion, prefix listing, policy mapping loading, or watcher retry semantics. It also does not cover entity names containing slashes in policydb paths; analogous object-store path splitting is covered in `iam-object-store_test.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/iam-etcd-store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/iam-object-store.go -->
# sources/object-store/minio/cmd/iam-object-store.go

## Purpose

`iam-object-store.go` implements `IAMStorageAPI` using MinIO's own object layer, storing IAM configuration objects under the internal metadata bucket. It is the normal non-etcd persistence backend for policies, users, service accounts, STS accounts, groups, and policy mappings.

## Important APIs, Types, And Control Flow

`IAMObjectStore` embeds an `iamCache`, protects it with an `RWMutex`, records the active user-system type, and holds an `ObjectLayer`. `saveIAMConfig` marshals JSON with jsoniter, encrypts with `GlobalKMS` when configured, and writes with `saveConfig`. `decryptData` returns plaintext directly when valid UTF-8, otherwise attempts legacy `madmin.DecryptData`, KMS decrypt with `.minio.sys/<path>` context, and KMS decrypt with raw object path context for compatibility. Load helpers read config bytes and metadata so old policy formats can derive create/update dates from object `ModTime`.

User loading normalizes missing access keys, deletes expired identities and their mappings, extracts JWT claims for temporary/service credentials, and carries comments into descriptions. The object backend has concurrency helpers for users, policies, and policy mappings using `errgroup.WithNErrs`. `listIAMConfigItems` walks the metadata bucket and returns object names trimmed relative to a prefix.

The high-impact method is `loadAllFromObjStore`: it lists all IAM config items once, buckets them by top-level list keys, loads policy documents and user mappings in batches of 32, loads regular users/groups for MinIO user mode, loads group/user policy mappings, loads service accounts, handles STS parent policy mappings for service accounts, builds user-group memberships, purges expired STS users from disk while tolerating errors, and replaces STS maps in cache. The custom `splitPath` treats `policydb/*` specially by splitting on the second slash so slash-containing LDAP/OIDC DNs remain intact.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is object data under `.minio.sys/config/iam/`, optionally encrypted and version/format compatible across releases. Dependencies include `ObjectLayer.Walk`, config read/write/delete helpers, KMS, madmin legacy decryption, logger timing, jsoniter, errgroup, and xsync maps. Risks include UTF-8 plaintext detection around encrypted data, legacy decryption compatibility, object-list staleness during concurrent IAM writes, slash-containing identity path handling, ignored errors while purging expired STS credentials, and batch/concurrency behavior on large IAM stores. `iam-object-store_test.go` covers `splitPath`, especially policydb entries containing slash-heavy LDAP DNs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/iam-object-store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/iam-object-store_test.go -->
# sources/object-store/minio/cmd/iam-object-store_test.go

## Purpose

`iam-object-store_test.go` verifies `splitPath`, the helper used by `IAMObjectStore.listAllIAMConfigItems` to classify walked IAM config objects into top-level buckets while preserving the rest of the entity path.

## Important Tests And Control Flow

`TestSplitPath` covers regular one-level paths such as `users/tester.json`, nested group paths, `format.json`, and policydb paths. The important cases are `policydb/sts-users/...` and `policydb/groups/...` entries whose entity names include one or more `/` characters, as LDAP DNs or other external identifiers can contain slashes. With `secondIndex=true`, `splitPath` returns the list key as `policydb/sts-users/` or `policydb/groups/` and leaves the entire slash-containing entity filename in the item string.

## State, Dependencies, Integration, Risks, And Signals

The test depends only on `testing`. It guards against a subtle IAM data-loss/regression risk: splitting policydb entries at the first slash would corrupt user/group names and prevent policy mappings from loading or reconciling correctly. The test does not cover object walking, config decryption, concurrent loaders, or expired-credential purge; those remain integration concerns for `IAMObjectStore`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/iam-object-store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/iam-store.go -->
# sources/object-store/minio/cmd/iam-store.go

## Purpose

`iam-store.go` is the shared high-level IAM storage layer above both object-store and etcd backends. It defines IAM on-disk paths and data models, owns the in-memory `iamCache`, loads/replaces cache state, and implements the administrative operations for policies, policy mappings, users, groups, service accounts, STS accounts, and notification-driven cache updates.

## Important APIs, Types, And Control Flow

Path helpers build canonical storage locations under `config/iam`: users, service accounts, groups, policies, STS accounts, and policydb maps. Core data models are `UserIdentity`, `GroupInfo`, `MappedPolicy`, and `PolicyDoc`. `PolicyDoc.parseJSON` accepts both the newer document wrapper and older raw `policy.Policy` format. `iamCache` stores policy docs, regular/service users, STS users, user/group/STS policy maps, groups, and reverse user-group memberships. `IAMStorageAPI` is the backend contract implemented by object-store and etcd stores.

`LoadIAMCache` builds a fresh cache, delegates to the optimized object-store full loader when available, otherwise loads policies, users, groups, mappings, and service accounts sequentially from the backend. It then replaces the live cache only if no local cache mutation happened after loading began, unless this is the first load. This prevents stale periodic refreshes from overwriting newer admin changes. STS policy maps are merged because periodic reloads are partial.

Group methods validate regular users, prevent temp/service accounts from group membership, persist `GroupInfo`, and update reverse membership maps. Policy methods attach, detach, set, delete, list, merge, and hot-load missing policies. Delete flows prevent deletion of policies still mapped to regular users/groups and update maps after notification deletes. User methods cover create/update/delete, status/secret changes, notification reloads, derived credential cleanup, and singleflight `LoadUser` for demand-loading individual identities. Service-account methods create/update/list/delete credentials, rewrite session-token claims when policy/status/secret changes, enforce expiration bounds, and hide secret/session values in list responses. STS methods set temporary users with TTL, revoke tokens by parent/type, list accounts, and purge/update derived credentials.

## State, Dependencies, Integration, Risks, And Tests

State spans persistent IAM config plus a mutable process cache protected by backend locks and xsync maps. Dependencies include MinIO auth credentials, madmin DTOs, policy parsing/merging, OpenID role metadata, environment flags, singleflight, errgroup, jsoniter, and JWT claim extraction. Integration points are `IAMSys`, admin APIs, STS flows, site replication hooks, LDAP/OIDC cleanup, and backend notification handlers. Risks include stale cache replacement timing, partial STS reload semantics, policy map consistency after deletes, disabled-group behavior denying access, derived credential cleanup when parents disappear, lock ordering around backend calls, and JWT claim extraction with multiple signing keys. Tests in this subset cover backend path helpers; broader IAM behavior is expected to be exercised by higher-level IAM/admin/STSes tests outside the listed files.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/iam-store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/iam.go -->
# sources/object-store/minio/cmd/iam.go

## Purpose

`iam.go` is the top-level IAM subsystem coordinator. It initializes identity providers and policy plugins, chooses the IAM persistence backend, runs periodic refresh and watch handling, exposes user/group/policy/service-account APIs to the rest of the server, normalizes LDAP imports, purges stale external identities, and evaluates authorization decisions for regular users, STS credentials, and service accounts.

## Important APIs, Types, And Control Flow

`IAMSys` stores refresh metrics, provider configs, user-system type, role ARN policy mappings, the `IAMStoreSys`, refresh interval, and the `configLoaded` readiness channel. `Init` loads TLS STS, OpenID, LDAP, AuthN plugin, AuthZ plugin, and legacy OPA config with retry; initializes either `IAMObjectStore` or `IAMEtcdStore`; populates role mappings from OpenID/AuthN; writes the IAM format file if needed; loads IAM data; then starts `periodicRoutines`. `Load` delegates to `store.LoadIAMCache`, updates atomic refresh metrics, initializes site-replication service-account secret when present, and closes `configLoaded` on first success.

`periodicRoutines` starts backend watch handling when available and otherwise relies on randomized refresh intervals around the base interval. Each refresh reloads IAM data and hourly runs LDAP/OIDC purge/update routines. `loadWatchedEvent` maps changed storage keys to user, STS, service-account, group, policy, or policy-mapping notification handlers.

The public methods wrap store operations with initialization/readiness checks and peer notification when no backend watcher is present. They cover policy CRUD/info/listing, user create/delete/status/secret, group membership/status/listing, policydb attach/detach/set/query for built-in and LDAP identities, STS user creation/revocation, service-account create/update/list/get/delete, access-key listing, and account lookup. LDAP helpers normalize service-account parent/group DNs and imported policy-mapping keys while deleting extraneous non-normalized mappings.

Authorization uses `IsAllowed`. OPA/AuthZ plugin decisions take precedence. Owner credentials bypass policy checks. STS and service-account credentials are validated against parent claims, role ARN mappings, parent/user/group policy mappings, OpenID policy claims, and optional embedded session policies. Regular users resolve policy names through `PolicyDBGet` and evaluate the merged policy.

## State, Dependencies, Integration, Risks, And Tests

State includes global provider configs, role maps, refresh counters, persistent IAM store data, `configLoaded`, and cache data owned by `IAMStoreSys`. Dependencies include LDAP/OpenID/TLS identity config, AuthN/AuthZ plugins, OPA compatibility, madmin, auth credentials, policy evaluation, notification system, site replication hooks, and object/etcd stores. Risks include long initialization retries delaying IAM readiness, race-sensitive readiness behavior before `configLoaded`, watcher path parsing for slash-containing identities, peer notification duplication when watcher support changes, LDAP DN normalization conflicts, service-account session-policy size/claim correctness, root-access and owner bypass handling, and policy fallback from claims when mappings are absent. Test signals in this subset are indirect; the file is a coordinator whose behavior is typically covered by admin, STS, LDAP/OIDC, and authorization integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/iam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/ilm-config.go -->
# sources/object-store/minio/cmd/ilm-config.go

## Purpose

`ilm-config.go` provides a small concurrency-safe holder for ILM worker configuration. It controls the number of lifecycle expiration and transition workers used elsewhere in the server.

## Important APIs, Types, And Control Flow

`globalILMConfig` is initialized with `ilm.Config{ExpirationWorkers: 100, TransitionWorkers: 100}`. `ilmConfig` wraps the config with an `RWMutex`. `getExpirationWorkers` and `getTransitionWorkers` take read locks and return the current worker counts. `update` takes a write lock and replaces the entire `ilm.Config`.

## State, Dependencies, Integration, Risks, And Tests

State is process-local global config and is not persisted in this file; persistence and parsing belong to the broader config subsystem. The only external dependency is `internal/config/ilm`. Integration points are lifecycle expiration/transition schedulers and config reload paths that call `update`. Risks are invalid worker counts if upstream config validation is bypassed, global defaults that may be too high or low for resource-constrained deployments, and whole-struct replacement losing future fields if update callers pass partial configs. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/ilm-config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/is-dir-empty_linux.go -->
# sources/object-store/minio/cmd/is-dir-empty_linux.go

## Purpose

`is-dir-empty_linux.go` provides the Linux implementation of `isDirEmpty`, optimized for filesystems where a directory with no children has link count 2.

## Important APIs, Types, And Control Flow

The build tag selects Linux except App Engine. `isDirEmpty(dirname, legacy)` has two paths. In legacy mode it calls `readDirN(dirname, 1)` and returns true only when the read succeeds and yields no entries. In the optimized mode it calls `syscall.Stat`, confirms the path is a directory via `S_IFMT == S_IFDIR`, and returns true when `Nlink == 2`.

## State, Dependencies, Integration, Risks, And Tests

There is no persistent state. Dependencies are `syscall.Stat` and package-local `readDirN`. The function is intended for metadata/object-store filesystem scanning where checking emptiness cheaply matters. The main risk is filesystem-specific link-count behavior: the comment explicitly calls out btrfs and NFS as cases where the optimization is unreliable, hence the legacy fallback. Other risks are races between stat/read and concurrent creates/deletes, symlink/stat semantics, and platform differences hidden behind build tags. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/is-dir-empty_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/is-dir-empty_other.go -->
# sources/object-store/minio/cmd/is-dir-empty_other.go

## Purpose

`is-dir-empty_other.go` provides the non-Linux implementation of `isDirEmpty`, using a portable directory read instead of Linux link-count optimization.

## Important APIs, Types, And Control Flow

The build tag selects all non-Linux platforms. `isDirEmpty(dirname string, _ bool)` ignores the legacy flag, calls `readDirN(dirname, 1)`, returns false on error, and returns true only when no entry is read. This directly checks whether at least one object/prefix exists in the directory.

## State, Dependencies, Integration, Risks, And Tests

There is no persistent state. The only dependency is package-local `readDirN`. Integration is the same as the Linux implementation: callers can use a single `isDirEmpty` API across platforms. Risks are ordinary directory-read races with concurrent modifications, cost compared with Linux `stat`, and behavior differences if `readDirN` filters entries. There are no direct tests in this subset; correctness is generally covered by platform builds and higher-level filesystem/object layout tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/is-dir-empty_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/jwt.go -->
# sources/object-store/minio/cmd/jwt.go

## Purpose

`jwt.go` contains JWT helpers for node authentication and metrics/web request authentication. It signs long-lived inter-node tokens, validates bearer tokens against root or IAM user secrets, merges embedded credential claims, and reports owner/group information for authorization decisions.

## Important APIs, Types, And Control Flow

Constants define the bearer algorithm label, one-day default web JWT expiry, and roughly 100-year inter-node token expiry. Package errors distinguish missing tokens, invalid access keys, disabled keys, authentication failure, skew, and malformed auth. `authenticateNode(accessKey, secretKey)` builds MinIO standard claims with access key and long expiry, then signs with HS512.

`metricsRequestAuthenticate(req)` extracts a token from the Authorization header using `jwt/v4/request`, parses it into MinIO `MapClaims`, and chooses the signing key by access key. Non-root users are looked up through `globalIAMSys.GetUser`; disabled or expired credentials are rejected. Root credentials are allowed only when `globalAPIConfig.permitRootAccess()` permits them. After successful parsing, non-root users are looked up again, embedded claims from `checkClaimsFromToken` are copied into the parsed claims, root-derived credentials can be disabled when root access is disabled, owner status is computed based on session policy and parent user, and credential groups are returned. `newCachedAuthToken` returns a closure over `globalNodeAuthToken`.

## State, Dependencies, Integration, Risks, And Tests

State is global: active root credentials, IAM cache, API root-access config, and node auth token. Dependencies include `golang-jwt/jwt/v4`, MinIO auth/JWT packages, and policy session claim names. Integration points include metrics endpoints, inter-node calls, and code paths needing cached node bearer tokens. Risks include intentionally collapsed parse errors into `errAuthentication`, reliance on global root-access state, duplicate user lookup with possible cache changes between lookups, owner semantics when session policies are present, and token lifetime for inter-node auth. `jwt_test.go` covers valid, missing, and invalid metric tokens plus benchmarks for parsing and cached token access.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/jwt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/jwt_test.go -->
# sources/object-store/minio/cmd/jwt_test.go

## Purpose

`jwt_test.go` tests metrics/web request JWT authentication for root credentials and benchmarks standard-claims parsing, map-claims parsing, node-token signing, and cached token retrieval.

## Important Tests And Control Flow

`getTokenString` creates a one-day HS512 token with MinIO map claims and an access key. `TestWebRequestAuthenticate` prepares a filesystem-backed test object layer, initializes global test config, signs a token with `globalActiveCred`, and checks three request cases: valid Authorization header succeeds, missing Authorization returns `errNoAuthToken`, and malformed token returns `errAuthentication`.

`BenchmarkParseJWTStandardClaims` signs an inter-node token with `authenticateNode` and repeatedly parses it with `xjwt.ParseWithStandardClaims`. `BenchmarkParseJWTMapClaims` parses the same token through `xjwt.ParseWithClaims` and a callback returning the secret key. `BenchmarkAuthenticateNode` compares repeatedly signing a new node token with reading the cached global token closure returned by `newCachedAuthToken`.

## State, Dependencies, Integration, Risks, And Signals

The test mutates global MinIO test configuration through `prepareFS` and `newTestConfig`, then uses global active credentials. It directly validates the root-token success path and high-level error mapping for missing/malformed headers. Gaps include disabled users, non-root IAM users, expired temporary credentials, root-access-disabled behavior, embedded claim copying, groups/owner return values, and invalid signing-key paths. The benchmarks indicate performance sensitivity around JWT parsing/signing and justify the cached node-token closure.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/jwt_test.go -->
