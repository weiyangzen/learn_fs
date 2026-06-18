# subset-b-006990 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_kms.cc

Purpose: Implements RGW server-side encryption key retrieval for SSE-KMS and SSE-S3. It bridges object encryption metadata to configured KMS backends: local testing keys from Ceph config, OpenStack Barbican, HashiCorp Vault KV/transit, and KMIP.

Important APIs and functions: `make_actual_key_from_kms()`, `reconstitute_actual_key_from_kms()`, `make_actual_key_from_sse_s3()`, `reconstitute_actual_key_from_sse_s3()`, `create_sse_s3_bucket_key()`, and `remove_sse_s3_bucket_key()` are the public entry points declared in `rgw_kms.h`. Internal helpers include `ZeroPoolAllocator` for zeroing RapidJSON allocations, `VaultSecretEngine`, `TransitSecretEngine`, `KvSecretEngine`, `KmipSecretEngine`, `get_actual_key_from_barbican()`, `get_actual_key_from_conf()`, and `maybe_cache_kms_fetch()`.

Control flow: KMS calls build a context object (`KMSContext` or `SseS3Context`) around Ceph config, select a backend, then call a backend-specific fetch function. Barbican validates UUID-like key ids, obtains a Keystone token, and fetches `/v1/secrets/<id>/payload`. Vault sends HTTP requests with optional token file auth, namespace, TLS CA/client certificates, and SSL verification settings. Vault KV reads `.data.data.key`; Vault transit either exports old-style keys, creates data keys and stores ciphertext in `RGW_ATTR_CRYPT_DATAKEY`, or decrypts wrapped data keys. KMIP locates by configured key template and then retrieves the unique id. The testing backend decrypts a per-object key selector with an AES-256 master key from config.

State and persistence: The source updates encryption attrs for wrapped Vault transit data keys and consumes attrs such as `RGW_ATTR_CRYPT_KEYID`, `RGW_ATTR_CRYPT_KEYSEL`, `RGW_ATTR_CRYPT_CONTEXT`, and `RGW_ATTR_CRYPT_DATAKEY`. It stores no objects itself, but it may create or delete Vault transit bucket keys for SSE-S3. Sensitive buffers are explicitly zeroed in many paths.

Dependencies and integration points: Depends on RGW crypto helpers, `RGWHTTPTransceiver`, Keystone, KMIP transceiver, RapidJSON, Ceph config, perf counters, and optional `rgw::kms::KMSCache`. It is called by RGW object encryption/decryption paths.

Risks: KMS errors map to object IO failures, so backend availability directly affects reads and writes. Vault transit compatibility mode changes cache identity and attr semantics. Logging must avoid exposing secrets; this file mostly logs ids and status, but error responses may include Vault response text. The testing backend intentionally sleeps for configured delay and should not be confused with production key storage.

Test signals: Unit and integration tests should cover backend selection, invalid key ids, Vault KV/transit JSON parsing, wrapped key reconstitution, cache behavior through `KMSCache`, token file permission checks, KMIP locate edge cases, and secret zeroization-sensitive regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_kms.h

Purpose: Declares the public KMS/SSE-S3 key retrieval interface used by RGW encryption code, backend name constants, Vault/KMIP secret engine constants, and the `SecretEngine` abstraction for backend implementations and tests.

Important APIs and types: Backend constants include `RGW_SSE_KMS_BACKEND_TESTING`, `BARBICAN`, `VAULT`, and `KMIP`. Vault auth constants include `token` and `agent`; Vault secret engine constants include `transit` and `kv`; KMIP currently exposes `kv`. Public functions derive or reconstitute actual object encryption keys from KMS or SSE-S3 metadata, and manage SSE-S3 bucket keys. `SecretEngine::get_key()` provides the minimal polymorphic contract for backend secret retrieval.

Control flow: This header does not implement behavior, but it defines the split between generating a new actual key (`make_actual_key_*`) and reconstructing an existing actual key (`reconstitute_actual_key_*`). The caller supplies object attrs, an optional KMS cache for SSE-KMS, an `optional_yield`, and an output string for the actual key.

State and persistence: Functions operate primarily through the supplied attrs map. Implementations may read or mutate encryption attributes such as key id and wrapped data key. The cache pointer is non-owning and may share secrets across KMS users.

Dependencies and integration points: The declarations rely on Ceph/RGW common types such as `DoutPrefixProvider`, `bufferlist`, `optional_yield`, and `rgw::kms::KMSCache`. It is the narrow interface between RGW encryption code and KMS-specific implementation details in `rgw_kms.cc`.

Risks: The output `actual_key` is a raw string containing cryptographic material; callers are responsible for clearing it when done. The attrs map is mutable in some APIs, which is necessary for wrapped keys but means callers need to persist updated attrs correctly.

Test signals: API-level tests should use a mock `SecretEngine` or test backend to verify make versus reconstitute semantics, error propagation, attribute mutation, and cache-enabled versus uncached behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.cc

Purpose: Implements an RGW KMS secret cache that stores fetched KMS secrets in a Ceph keyring-backed secret store and uses `WebCache` for TTL and capacity management.

Important APIs and functions: `KMSCache::KMSCache()` configures cache size and positive TTL from Ceph config and disables the cache if the keyring is unsupported. `initialize_ttl_reaper()` starts either a dedicated `std::jthread` or an async Boost.Asio reaper. `stop_ttl_reaper()` cancels/stops that reaper. `do_cache()` performs lookup, stampede-protected fetch, keyring insertion, TTL adjustment, and final secret readback.

Control flow: `do_cache()` constructs a namespaced cache key from `rgw_sse_`, a caller prefix, and key id. It obtains a shared `once_result` from `WebCache::lookup_or()`, then calls `ceph::async::call_once()` so concurrent readers of the same key share one fetch. Fetch result `-ENOENT` is treated as permanent and assigned the negative TTL; other errors are transient and assigned the transient error TTL. Successful fetches are inserted into `Keyring` with a UUID-suffixed keyring key so racing fetches never share a physical secret entry.

State and persistence: Cache entries hold `shared_ptr<KeyringSecret>` references rather than raw strings. Secrets are zeroized after keyring insertion, and `actual_key` is populated only when read back from the keyring. Reaper state is a variant containing no reaper, a service thread, or async state with strand/cancellation/future.

Dependencies and integration points: Depends on `common/web_cache.h`, `common/keyring.h`, `common/async/call_once.h`, Boost.Asio, RGW perf counters, and Ceph config keys under `rgw_crypt_s3_kms_cache_*`. It is invoked through `maybe_cache_kms_fetch()` in `rgw_kms.cc`.

Risks: If keyring add/read fails, the implementation removes the cache entry, disables cache globally in config, and returns internal error. The async reaper waits on a future after dispatching cancellation; executor shutdown ordering must ensure the cancellation is serviced. TTL minimum is computed from positive, negative, and transient TTLs, so zero or very small config values can make reaping aggressive.

Test signals: Tests should exercise concurrent fetch coalescing, positive/negative/transient TTL assignment, keyring failure disablement, clear-cache behavior, thread and async reaper lifecycle, and perf counter increments for permanent, transient, and secret-store errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.h

Purpose: Declares `rgw::kms::KMSCache`, the cache layer for RGW KMS secrets. It combines a bounded web cache, keyring-backed secret storage, TTL reaping, and fetch stampede mitigation.

Important APIs and types: `SharedSecret`, `CacheResult`, `CacheValue`, `KMSSecretCache`, and `FetchFn` describe cached secret storage and fetch callbacks. The constructor takes `CephContext*` and an owned `Keyring`. Public APIs include `initialize_ttl_reaper()`, `stop_ttl_reaper()`, `reaper_initialized()`, `make_ttl_reaper_thread()`, `make_ttl_reaper_async()`, `clear_cache()`, `do_cache()`, and `disable_cache()`.

Control flow: Callers initialize the cache with a keyring, optionally start a TTL reaper on either a supplied Asio executor or an owned thread, then call `do_cache()` for each KMS key. `do_cache()` delegates cache-miss retrieval to a caller-provided `FetchFn`, making the class backend-agnostic.

State and persistence: The class owns a `WebCache<std::string, CacheValue>`, a `Keyring`, and reaper state. Reaper state is intentionally single-instance and non-copyable/non-movable to avoid duplicate reapers over one cache. `disable_cache()` mutates the Ceph config flag `rgw_crypt_s3_kms_cache_enabled`.

Dependencies and integration points: Depends on Boost.Asio executor/cancellation types, Ceph async yield/call-once helpers, keyring, web cache, and expected-style error returns. It integrates with `rgw_kms.cc` but does not know about Barbican, Vault, or KMIP.

Risks: `actual_key` is returned as a string and must be cleared by higher layers. `disable_cache()` changes runtime config globally for the daemon, so secret-store failures can affect all KMS users. Reaper initialization is idempotent but not explicitly synchronized, so callers should initialize from controlled startup code.

Test signals: Header-level consumers should validate non-copyable ownership assumptions, executor and non-executor reaper modes, cache namespace prefixes, and behavior when the configured cache is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_lc.cc

Purpose: Implements RGW bucket lifecycle execution: expiration, noncurrent expiration, delete-marker expiration, object transition, noncurrent transition, aborting incomplete multipart uploads, lifecycle shard scheduling, and S3 lifecycle response headers.

Important APIs and functions: Core public methods are `RGWLC::initialize()`, `start_processor()`, `stop_processor()`, `process()`, `process_bucket()`, `bucket_lc_process()`, `set_bucket_config()`, and `remove_bucket_config()`. Rule expansion is handled by `RGWLifecycleConfiguration::_add_rule()`. Execution is organized through `LCObjsLister`, `LCOpRule`, `LCOpAction_*`, `remove_expired_obj()`, `handle_multipart_expiration()`, and helpers in namespace `rgw::lc`.

Control flow: Lifecycle XML/config is decoded into `LCRule` objects and expanded into prefix-keyed `lc_op` entries. Worker threads run only during configured work windows, choose lifecycle index shards in random order, lock a shard object, read or initialize its head marker, mark a bucket entry processing, advance the head, drop the shard lock, process the bucket, then reacquire the lock to mark the entry complete, failed, or remove stale entries. Per-bucket processing groups rules by prefix, lists current and versioned objects, evaluates candidate actions, fetches tags only when needed, and dispatches object work through an async spawn throttle. Versioned hard deletes for the same key are grouped so `rgw::multi_delete::dispatch()` can skip redundant OLH updates.

State and persistence: Lifecycle configs are stored in bucket attrs under `RGW_ATTR_LC`. Bucket work is persisted in SAL lifecycle entries stored under hashed `lc.N` objects and coordinated by `LCSerializer` locks named `lc_process`. `LCHead` tracks shard marker, start date, and rollover date. Object actions mutate bucket indexes and objects through SAL delete/transition APIs and emit notifications. Per-bucket counters are batched through `LCBatchCounters`.

Dependencies and integration points: Uses SAL `Driver`, `Bucket`, `Object`, `Lifecycle`, `Restore`, `Notification`, lock serializers, RGW tags, object lock attrs, multipart upload APIs, placement tiers including cloud-S3 tiers, perf counters, and Boost.Asio coroutine throttling.

Risks: Lifecycle is concurrency-heavy and relies on lock/relock ordering around bucket processing. Bugs can cause skipped buckets, repeated daily processing, stale processing sessions, or unsafe deletes around object lock and delete markers. Prefix grouping and unordered listing improve scale but raise boundary risks for versioned delete marker handling. Notification failures are logged but do not roll back object mutations.

Test signals: Tests should cover rule expansion, duplicate ids, days/date conflict validation, work-window scheduling, shard rollover, stale session clearing, bucket-marker mismatch removal, object lock blocking, delete marker exposure checks, tag/size filters, versioned multi-delete grouping, transition to local and cloud tiers, multipart aborts, counters, and `x-amz-expiration`/abort header calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_lc.h

Purpose: Declares the lifecycle data model, serialization format, rule expansion structures, lifecycle worker class, and helper APIs used by RGW lifecycle processing.

Important APIs and types: `LCExpiration`, `LCTransition`, `LCFilter`, and `LCRule` model lifecycle rule components. `transition_action` and `lc_op` are execution-ready forms used by `rgw_lc.cc`. `RGWLifecycleConfiguration` owns `rule_map` and `prefix_map`, validates and encodes rules, and converts rules into `lc_op`. `RGWLC` owns lifecycle workers and exposes processor/config APIs. Namespace `rgw::lc` declares shard repair and S3 header helpers.

Control flow: Lifecycle XML or stored attrs decode into `RGWLifecycleConfiguration`, whose decode path rebuilds the prefix map by calling `_add_rule()`. `RGWLC::LCWorker` threads call `RGWLC::process()` repeatedly, and `RGWLC` methods use SAL lifecycle services to list, lock, and mutate lifecycle entries. Header helpers decode bucket lifecycle attrs on demand to compute response metadata.

State and persistence: The classes encode with Ceph `ENCODE_START` versioning, preserving backward compatibility across lifecycle schema changes. `LCExpiration` tracks days, date, and newer-noncurrent versions. `LCFilter` tracks prefix, tags, size bounds, and extension flags such as `ArchiveZone`. `LCRule` carries expiration, noncurrent expiration, multipart expiration, transitions, noncurrent transitions, and delete-marker expiration. `RGWLC` stores daemon-local worker state, lifecycle object names, shutdown flag, and lock cookie.

Dependencies and integration points: Depends on Ceph buffer encoding, librados types, RGW tags, SAL driver/bucket abstractions, RGW common request/debug infrastructure, and lifecycle class types. It is included by S3 XML parsing, lifecycle execution, and operation handlers that install or remove lifecycle configs.

Risks: Several fields are stored as strings and converted with `atoi()` or `stoull()` style parsing, so validation must happen before execution. Versioned encoding makes compatibility important when adding fields. The worker owns raw `obj_names` allocated in `initialize()` and freed in `finalize()`, so lifecycle object lifetime must stay ordered.

Test signals: Serialization compatibility tests should cover all struct versions, especially `LCExpiration` and `LCFilter`. Rule tests should cover id length, empty actions, date/day conflicts, duplicate ids, tag restrictions, size filters, transitions, archive-zone flags, and prefix map reconstruction after decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.cc

Purpose: Implements S3 XML parsing and rendering for RGW lifecycle configuration, converting between S3 XML elements and the internal lifecycle model in `rgw_lc.h`.

Important APIs and functions: `LCExpiration_S3::decode_xml()/dump_xml()`, `LCNoncurExpiration_S3`, `LCMPExpiration_S3`, `LCFilter_S3`, `LCTransition_S3`, `LCNoncurTransition_S3`, `LCRule_S3`, and `RGWLifecycleConfiguration_S3` provide S3-specific XML behavior. `check_date()` validates ISO-8601 lifecycle dates are day-aligned.

Control flow: `RGWLifecycleConfiguration_S3::decode_xml()` decodes all `Rule` entries, auto-generates a random lowercase id for missing ids, and enforces `rgw_lc_max_rules`. `LCRule_S3::decode_xml()` requires valid status, accepts either modern `Filter` or legacy top-level `Prefix`, parses expiration/noncurrent/multipart expiration and transitions, rejects rules with no action, and inserts transition actions by storage class. `rebuild()` revalidates parsed S3 rules into a generic `RGWLifecycleConfiguration`.

State and persistence: This file does not persist directly; it prepares lifecycle objects that later encode into bucket attrs. It preserves S3-specific details such as `ExpiredObjectDeleteMarker`, `NewerNoncurrentVersions`, `ObjectSizeGreaterThan`, `ObjectSizeLessThan`, and the Ceph extension `ArchiveZone`.

Dependencies and integration points: Depends on RGW XML decoder/formatter, S3 tag XML support, Ceph time parsing, random id generation from the Ceph context, and the lifecycle execution data model. Operation handlers use it when handling S3 lifecycle configuration APIs.

Risks: XML compatibility is delicate because old clients may omit `Filter` and use top-level `Prefix`. Size bounds are stored as strings and compared lexically in the current code path (`size_lt <= size_gt`), which is a risk for numeric correctness unless constrained elsewhere. `ExpiredObjectDeleteMarker` only accepts the literal string `"true"` as enabling.

Test signals: Tests should cover malformed dates, multiple expiration choices, missing status/storage class, empty filters, prefix/tag/size/ArchiveZone filters, legacy prefix compatibility, max rule enforcement, duplicate transition storage classes, dump/decode round trips, and S3 error mapping for invalid XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.h

Purpose: Declares S3 XML-specialized subclasses for lifecycle filters, expirations, transitions, rules, and whole lifecycle configurations.

Important APIs and types: `LCFilter_S3`, `LCExpiration_S3`, `LCNoncurExpiration_S3`, `LCMPExpiration_S3`, `LCTransition_S3`, `LCNoncurTransition_S3`, `LCRule_S3`, and `RGWLifecycleConfiguration_S3` each add `decode_xml()` and/or `dump_xml()` to their generic lifecycle base type. `RGWLifecycleConfiguration_S3::rebuild()` copies S3-parsed rules into a generic validated configuration.

Control flow: The header establishes a two-phase parse model: parse XML into S3 subclasses, then rebuild into the generic encoded lifecycle configuration consumed by `RGWLC`. Dump methods perform the reverse for GET lifecycle responses.

State and persistence: S3 subclasses mostly reuse base-class storage. `LCExpiration_S3` adds `dm_expiration` to represent `ExpiredObjectDeleteMarker` before it is copied into `LCRule::dm_expiration`.

Dependencies and integration points: Depends on `rgw_lc.h`, XML helpers, S3 tag XML handling, and Ceph include types. It is consumed by S3 REST lifecycle operation code and implemented by `rgw_lc_s3.cc`.

Risks: The subclasses rely on casts between generic and S3 lifecycle types in dump paths. That is safe only when objects actually originated from S3-specific classes or layout-compatible base state. The default constructor without `CephContext` cannot decode full configurations because id generation requires context.

Test signals: Compile and runtime tests should cover decode with and without context, XML dump casts, delete-marker expiration transfer, noncurrent version fields, and rebuild validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ldap.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_ldap.cc

Purpose: Implements LDAP password loading and, when OpenLDAP is available, LDAP user authentication for RGW.

Important APIs and functions: `parse_rgw_ldap_bindpw()` reads the configured bind password secret file. `rgw::LDAPHelper::auth()` builds an LDAP search filter for a uid, searches under the configured search DN, and verifies the supplied password by binding as the discovered user DN.

Control flow: Bind password parsing reads `rgw_ldap_secret`, trims whitespace, and zeroizes the stack buffer. Authentication chooses a Microsoft AD style filter if `msad` is enabled, otherwise uses either a default `(<dnattr>=<uid>)`, a configured filter containing `@USERNAME@`, or an AND-combined custom filter plus uid condition. It serializes access with `mtx`, searches the existing LDAP connection, attempts one rebind and retry on search failure, then calls `simple_bind()` on a temporary LDAP connection for password verification.

State and persistence: The helper owns a persistent `LDAP*` connection initialized and service-bound by code in the header. It does not persist RGW state. The password buffer from the secret file is zeroed after reading.

Dependencies and integration points: Depends on OpenLDAP when `HAVE_OPENLDAP` is set, Ceph config and safe file IO, Boost trim, and RGW auth setup in `rgw_main`. Without OpenLDAP, the header provides a stub returning unsupported/access denied.

Risks: Filter construction concatenates uid into LDAP filters without visible escaping in this file, which is a classic LDAP injection concern unless sanitized by callers or config constraints. `ldap_get_dn()` return handling assumes a DN is returned. Search errors collapse to `-EACCES` after one rebind, which can obscure operational LDAP failures from users.

Test signals: Tests should cover secret file trimming/zeroization behavior, default and custom filter construction, `@USERNAME@` substitution, search miss handling, rebind retry, password bind failures, OpenLDAP-disabled behavior, and injection-shaped usernames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ldap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ldap.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_ldap.h

Purpose: Declares RGW LDAP integration, with an OpenLDAP-backed helper when available and a stub helper when RGW is built without OpenLDAP support.

Important APIs and types: `rgw::LDAPHelper` stores LDAP URI, service bind DN/password, search DN/filter, DN attribute, optional AD mode flag, the `LDAP*` connection, and a mutex. Key methods are `init()`, `bind()`, `rebind()`, `simple_bind()`, `auth()`, and the destructor. The global helper `parse_rgw_ldap_bindpw()` loads the bind password from config.

Control flow: OpenLDAP builds initialize a protocol v3 LDAP connection, disables referrals, performs service bind, and later authenticates users by search plus simple bind. Non-OpenLDAP builds expose the same constructor and methods but return `-ENOTSUP` for setup and `-EACCES` for auth.

State and persistence: `LDAPHelper` owns and unbinds one service LDAP connection. It creates temporary LDAP connections for user password checks. No RGW metadata is persisted here.

Dependencies and integration points: Guarded by `HAVE_OPENLDAP` and includes `ldap.h` with deprecated APIs enabled. Also includes Ceph context/debug/safe IO headers because the password parser is declared here. Used by RGW main initialization and auth paths.

Risks: The helper is synchronous and protected by a single mutex, so LDAP search throughput can serialize. The destructor unbinds the service connection but temporary bind behavior depends on `simple_bind()` always reaching unbind after initialize. Stub behavior should be surfaced clearly in configuration tests so LDAP auth is not silently expected in unsupported builds.

Test signals: Build-matrix tests should verify both OpenLDAP and no-OpenLDAP paths. Runtime tests should cover init option failures, bind failure mapping, rebind behavior, destructor cleanup, and thread serialization during auth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lib.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_lib.cc

Purpose: Implements the embedded librgw frontend/process used by RGW-as-a-library clients such as NFS-style integrations. It initializes RGW subsystems, processes in-memory requests through normal RGW operation machinery, and manages mounted filesystem garbage collection.

Important APIs and functions: `RGWLibProcess::run()`, `handle_request()`, `process_request()`, `start_request()`, and `finish_request()` execute regular and continued requests. `RGWLibFrontend::init()` creates the process. `RGWLib::init()` and `stop()` initialize and shut down the RGW daemon stack. `RGWLibIO::set_uid()` loads a user. `RGWLibRequest::read_permissions()` builds bucket/object policies. `RGWHandler_Lib::authorize()` grants full control to the cached user.

Control flow: Initialization calls `rgw_global_init()`, sets librgw defaults, arms an init timeout, initializes frontends, common Ceph state, perf counters, HTTP clients, storage, APIs, LDAP, opslog, signal handling, tracepoints, frontends, Lua, and optionally dedup. Request processing constructs `RGWLibIO` and `req_state`, initializes the request/handler, initializes the `RGWOp`, authorizes, transforms legacy auth info if needed, reads policies, verifies op mask/permissions/params, then executes and completes the op. Continued requests split execution into start and finish callbacks.

State and persistence: `g_rgwlib` is the global instance pointer. `RGWLibProcess` tracks mounted `RGWLibFS` instances, a generation counter, and a shutdown flag. Its run loop periodically calls filesystem GC and user update based on namespace expiration config. Requests mutate normal RGW backend state through SAL and RGW operations.

Dependencies and integration points: Depends on `rgw_main`, RGW REST/op/auth/log/process infrastructure, `RGWLibFrontend`, `RGWLibFS`, perf counters, signal handlers, timers, and Ceph global initialization. It deliberately reuses standard RGW op logic rather than a separate object path.

Risks: Authorization is simplified and grants full control to the supplied user, so correctness relies on mount-time identity handling. `abort_req()` increments failed counters but does not emit HTTP responses. The GC loop releases and reacquires its mutex around filesystem calls and restarts iteration when generation changes.

Test signals: Tests should cover init failure cleanup, request init/auth/policy failures, admin permission override, continued request lifecycle, mounted filesystem registration churn during GC, shutdown signal cleanup, and `set_uid()` user load failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lib.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lib.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_lib.h

Purpose: Declares the librgw embedding API and request abstractions that let non-HTTP clients drive RGW operations through in-process request and IO objects.

Important APIs and types: `RGWLib` owns `AppMain`, a Ceph context, and a frontend pointer. `RGWLibIO` implements `BasicClient` and `Accounter` around `RGWEnv` and optional `RGWUserInfo`. `RGWRESTMgr_Lib` and `RGWHandler_Lib` adapt REST handler behavior. `RGWLibRequest` combines `RGWRequest` and `RGWHandler_Lib` and requires descendants to implement `header_init()`, `op_init()`, and `only_bucket()`. `RGWLibContinuedReq` adds `exec_start()`, `exec_continue()`, and `exec_finish()` for multi-step operations.

Control flow: A librgw request is constructed with a user, initialized with an environment and driver, populated with req ids, tenant, and user state, then passed to process code in `rgw_lib.cc`. Descendant request classes provide operation-specific header and op initialization.

State and persistence: `RGWLibIO` owns the environment and loaded user info for a request. `RGWLibRequest` temporarily owns a SAL user during initialization and then transfers it into `req_state`. Continued requests embed their own IO context and request state so they can survive across start/continue/finish calls.

Dependencies and integration points: Depends on RGW client IO, REST, request, LDAP, main initialization, SAL driver/user types, and frontend classes. It is the boundary between external librgw callers and normal RGW operation execution.

Risks: Several IO methods are minimal or return zero accounting, so callers expecting byte-accurate accounting need to verify behavior. `RGWLibRequest` uses global `g_rgwlib` to obtain driver ids during construction. Descendants must set up `op` correctly or processing falls back to runtime dynamic casting.

Test signals: Tests should validate request state initialization, tenant/user transfer, bucket-only permission reads, continued request state retention, IO environment setup, and behavior when descendant initialization omits required operation state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lib_frontend.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_lib_frontend.h

Purpose: Declares the librgw process frontend that queues and executes in-process RGW library requests and tracks mounted `RGWLibFS` instances for lifecycle/GC coordination.

Important APIs and types: `RGWLibProcess` derives from `RGWProcess` and stores an access key, mutex/condition variable, generation counter, shutdown flag, and a flat map of mounted filesystems. It exposes `run()`, `checkpoint()`, `stop()`, `register_fs()`, `unregister_fs()`, `enqueue_req()`, regular request handlers, continued request handlers, and `set_access_key()`. `RGWLibFrontend` derives from `RGWProcessFrontend` and wraps process initialization, stop, enqueue, execute, start, and finish APIs.

Control flow: The frontend creates a `RGWLibProcess`. Callers either queue async requests through `enqueue_req()` or execute synchronously through `execute_req()`. Continued requests use `start_req()` and `finish_req()`. `stop()` propagates shutdown to mounted filesystems and wakes the process loop.

State and persistence: Mounted filesystem pointers are registered in a flat map and generation changes invalidate current GC iteration. Request queueing uses inherited `req_throttle` and `req_wq`. This header does not persist data, but process methods execute operations that mutate RGW storage.

Dependencies and integration points: Depends on `rgw_lib.h`, `rgw_file_int.h`, `RGWProcess`, and Boost flat map. It sits between `AppMain` frontend setup and embedded filesystems using librgw.

Risks: Mounted filesystem pointers are raw and rely on external lifetime/reference conventions. `stop()` iterates mounted filesystems without taking the mutex in the inline method, while register/unregister use the mutex; callers need coordinated shutdown. Async `enqueue_req()` transfers ownership to the work queue, so request deletion responsibility is in the handler.

Test signals: Tests should cover register/unregister during process loop, stop wakeups, synchronous versus async request processing, continued request sequencing, throttling behavior, and mounted filesystem shutdown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lib_frontend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_loadgen.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_loadgen.cc

Purpose: Implements a synthetic client IO and request environment for RGW load generation. It signs generated S3 requests and feeds them into RGW processing without real network IO.

Important APIs and functions: `RGWLoadGenRequestEnv::set_date()` formats the request date. `RGWLoadGenRequestEnv::sign()` builds an S3 v2 canonical header and authorization header. `RGWLoadGenIO::init_env()` populates `RGWEnv` from the generated request. `read_data()`, `write_data()`, status/header methods, `flush()`, and `complete_request()` implement no-op or byte-counting IO behavior.

Control flow: A generated request sets method, URI, content type/length, date, and headers. `sign()` uses the configured access key to add `HTTP_DATE` and `HTTP_AUTHORIZATION`. `RGWLoadGenIO` then exposes this data through `RGWEnv` and simulates request body reads by decrementing `left_to_read`; response writes and headers are discarded.

State and persistence: The request environment is per request. `left_to_read` tracks remaining synthetic body bytes. No response data is persisted and no actual network traffic is emitted. Storage mutations occur later when the request is processed by RGW.

Dependencies and integration points: Depends on `rgw_auth_s3` for canonicalization/signing, global Ceph context for S3 signature helper, and RGW client IO abstractions. It is used by `RGWLoadGenProcess` in `rgw_loadgen_process.cc`.

Risks: This is not a full HTTP client and intentionally ignores response bodies/headers, so it is suitable for load generation rather than protocol validation. It uses S3 v2 signing and a global context dependency. `read_data()` does not fill the buffer with deterministic payload bytes, which may matter for checksum-sensitive paths.

Test signals: Tests should cover canonical header inputs, authorization header format, env variable population, body length simulation, zero-length bodies, and operation paths that require response handling or request body content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_loadgen.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_loadgen.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_loadgen.h

Purpose: Declares request environment and IO classes used by the RGW load generator to synthesize signed in-process S3 requests.

Important APIs and types: `RGWLoadGenRequestEnv` stores port, content length, content type, method, URI, query string, date, and headers, with `set_date()` and `sign()` helpers. `RGWLoadGenIO` derives from `rgw::io::RestfulClient` and implements environment initialization, synthetic body receive/send, response status/header hooks, flush, and request completion.

Control flow: The load generator constructs an environment, signs it, then passes an `RGWLoadGenIO` into `RGWRestfulIO`/RGW request processing. Read calls consume synthetic request bytes; write/status/header calls discard output.

State and persistence: The IO object points at an external request environment and owns an `RGWEnv`. `left_to_read` is initialized from content length on env init. No persistent state is created here.

Dependencies and integration points: Depends on `rgw_client_io.h`, RGW access keys, Ceph time formatting, and the loadgen process. It provides enough of the client IO contract for RGW ops to execute.

Risks: The request environment pointer must outlive the IO object. Output is ignored and byte accounting is minimal, so failures may only surface through return codes in the process layer. It is not appropriate as a correctness oracle for HTTP serialization.

Test signals: Tests should verify environment lifetime assumptions, content length handling, receive-body exhaustion, header propagation, signing integration, and behavior for GET/PUT/DELETE style generated requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_loadgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_loadgen_process.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_loadgen_process.cc

Purpose: Implements the RGW load generation process that creates buckets, uploads objects, reads objects, deletes objects, deletes buckets, and then shuts the RGW process down.

Important APIs and functions: `RGWLoadGenProcess::run()` orchestrates the load sequence. `checkpoint()` drains queued work. `gen_request()` allocates and queues `RGWLoadGenRequest` objects. `handle_request()` converts each queued request into a signed loadgen IO path and calls `process_request()`.

Control flow: `run()` starts the thread pool, reads `num_objs` and `num_buckets` from frontend config, creates random bucket names, queues bucket PUTs and drains, creates random object names, queues object PUTs and drains, then queues GETs, object DELETEs, and bucket DELETEs with drain points between phases. It stops the thread pool, deletes the object name array, and signals RGW shutdown. `handle_request()` builds `RGWLoadGenRequestEnv`, signs it, wraps it in `RGWRestfulIO`, processes the request, and deletes the request.

State and persistence: The generated workload mutates normal RGW bucket/object state through the standard request path. Local state includes bucket and object name vectors/arrays, an access key, a request queue, and an optional failure flag shared by setup phases.

Dependencies and integration points: Depends on RGW process/work queue infrastructure, `RGWLoadGenIO`, request processing, frontend config, random name helpers, and RGW signal shutdown. It is a synthetic frontend-like process rather than an external benchmark client.

Risks: On request failure, `handle_request()` does `req->fail_flag++` instead of incrementing the atomic value it points to, so the phase failure flag may not be set as intended. Error messages after object PUT failures still say bucket creation failed. The object array is allocated after bucket creation and deleted unconditionally at `done`, which is safe in the current flow because allocation precedes the first `goto done` after that point.

Test signals: Tests should cover generated phase ordering, config defaults, request signing and processing, failure flag mutation, cleanup after failures, thread pool drain behavior, and final shutdown signaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_loadgen_process.cc -->
