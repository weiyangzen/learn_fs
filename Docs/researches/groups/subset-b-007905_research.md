# Research: subset-b-007905

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage.py

## Purpose
This file is the broad unit and integration-style test surface for Tahoe-LAFS local storage primitives. It covers storage-index encoding, immutable share containers, mutable share containers, bucket writers/readers, Foolscap-facing bucket wrappers, storage-server allocation and lease semantics, corruption advisory persistence, MDMF/SDMF mutable layout proxies, latency statistics, schema compatibility, `LeaseInfo`, and `_WriteBuffer` batching. It is intentionally low-level: most tests instantiate `StorageServer`, `BucketWriter`, `BucketReader`, `ShareFile`, `MutableShareFile`, and layout proxies directly instead of going through a full node.

## Important APIs, Types, And Helpers
The main test classes are `UtilTests`, `Bucket`, `BucketProxy`, `Server`, `MutableServer`, `MDMFProxies`, `Stats`, `ShareFileTests`, `MutableShareFileTests`, `LeaseInfoTests`, and `WriteBufferTests`. Local helpers include `bchr`, `FakeStatsProvider`, `RemoteBucket`, `make_lease`, `Server.allocate`, `MutableServer.allocate`, MDMF/SDMF share builders, and `compare_leases_without_timestamps`.

The production APIs under test are `storage_index_to_dir`, `si_b2a`, `si_a2b`, `get_share_file`, `BucketWriter`, `BucketReader`, `FoolscapBucketWriter`, `FoolscapBucketReader`, `WriteBucketProxy`, `WriteBucketProxy_v2`, `ReadBucketProxy`, `StorageServer`, `FoolscapStorageServer`, `MutableShareFile`, `ShareFile`, `LeaseInfo`, `MDMFSlotWriteProxy`, `MDMFSlotReadProxy`, `SDMFSlotWriteProxy`, and `_WriteBuffer`. The file also validates protocol constants such as `MDMFHEADER`, `MDMFOFFSETS`, `MDMFSIGNABLEHEADER`, `SIGNED_PREFIX`, field sizes for private keys/signatures/verification keys/share hash chains, and schema collections `ALL_IMMUTABLE_SCHEMAS` and `ALL_MUTABLE_SCHEMAS`.

## Control Flow
The immutable bucket tests build incoming and final filesystem paths, write byte ranges through `BucketWriter`, close or abort writers, then read finalized data through `BucketReader`. Several tests use Hypothesis to explore overlapping writes, conflicting writes, required-range tracking, read truncation at the end of share data, and `_WriteBuffer` coalescing.

The storage-server tests create a `StorageServer` attached to a `LoggingServiceParent`, allocate immutable buckets, write or abort writers, and inspect the resulting bucket readers, available-space accounting, leases, readonly/discard behavior, sparse-file behavior, and advisory files. Foolscap tests wrap the local server with `FoolscapStorageServer` or the writer/reader wrappers and use `RemoteBucket.callRemote` to simulate remote method dispatch while counting mutable read/write RPCs.

The mutable-server tests drive `slot_testv_and_readv_and_writev` and `slot_readv` directly. They create mutable shares, exercise test/write/read vector semantics, verify operators, ensure reads happen before writes in combined operations, validate write-enabler failures, confirm zero-fill behavior when writes extend past EOF, test truncation and deletion via `new_length=0`, and check lease renewal/addition behavior across share growth.

The MDMF/SDMF proxy tests hand-construct binary shares. `build_test_mdmf_share` writes the checkstring, encoding parameters, offset table, encrypted private key, share hash chain, signature, verification key, share data, and block hashes. `build_test_sdmf_share` constructs legacy SDMF layout. Tests then publish through `MDMFSlotWriteProxy` or `SDMFSlotWriteProxy`, read through `MDMFSlotReadProxy`, and assert ordering, offset, checkstring, prefetch, tail-segment, empty-file, and legacy compatibility behavior.

## State And Persistence Behavior
The tests persist share state under relative `storage/...` work directories, mirroring Tahoe-LAFS storage layout with `shares`, prefix directories, storage-index directories, incoming temporary share paths, finalized share files, and `corruption-advisories`. Immutable uploads create incoming writers that become readable only after close; abort and disconnect paths must remove provisional allocation and temporary files. Mutable writes alter share files in place and can delete a share and its storage-index directory when truncated to zero.

Lease state is stored inside immutable and mutable share containers. Tests distinguish renewing an existing lease from adding a new one, validate lease serialization lengths, verify renew/cancel secret matching, ensure overflow attempts leave share file bytes unchanged, and assert optional `renew_leases=False` paths leave grant timestamps or lease lists untouched. Clock-controlled tests assert expiration times use `DEFAULT_RENEWAL_TIME`.

Disk-space behavior is stateful. `FakeDisk` patches `fileutil.get_disk_stats` to force `NoSpace` for additional immutable/mutable leases and corruption reports. Reserved-space tests count provisional allocations while writers are open, then real allocation overhead after close. Sparse-file tests are skipped on platforms where they are too expensive.

## Dependencies And Integration Points
The file depends on Twisted Trial, Deferreds, `Clock`, Hypothesis, `testtools.matchers`, and Tahoe test utilities (`LoggingServiceParent`, `FakeDisk`, `FakeCanary`, `upload_immutable`, `upload_mutable`). It integrates with local storage modules (`server`, `immutable`, `mutable`, schemas, lease/common/share helpers), immutable layout proxies, mutable layout proxies, Foolscap wrappers, and the storage-client `_StorageServer` adapter used by mutable layout proxies.

Important integration points are the Foolscap method names (`slot_readv`, `writev` variants), `StorageServer.get_version` capability flags (`prevents-read-past-end-of-share-data`, `maximum-immutable-share-size`, `maximum-mutable-share-size`, `available-space`, `fills-holes-with-zero-bytes`), and on-disk compatibility with older immutable and SDMF formats.

## Risks And Edge Cases
High-risk areas covered include overlapping immutable writes, write conflicts, read-past-share-data leakage, stale incoming writers, disconnect cleanup, reserved-space accounting, corruption advisory persistence under low disk, bad container magic/version handling, mutable conditional writes, zero-fill after truncation, deletion of final mutable shares, lease-table relocation when containers grow, lease-count overflow, and MDMF layout ordering. MDMF-specific risks include invalid salt/root hash/block sizes, too many blocks, publishing with stale checkstrings, uncoordinated writes, prefetch cache correctness, and SDMF fallback.

Some risks remain implicit: many tests depend on relative `storage/...` paths and cleanup behavior in test infrastructure; large-share behavior is skipped on common platforms or low-disk environments; several MDMF tests use simplified keys/hash bytes rather than cryptographic end-to-end verification; and error-message assertions can be brittle when migration diagnostics change.

## Test Signals
Passing this file signals that core local storage semantics are stable across immutable, mutable, Foolscap-wrapper, and layout-proxy layers. It also signals compatibility across mutable and immutable schema variants because Hypothesis samples all schema collections. The tests are a strong regression net for storage persistence, lease accounting, allocation cleanup, protocol layout, and storage capability advertisement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_client.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_client.py

## Purpose
This file tests Tahoe-LAFS client-side storage discovery and server-selection behavior. It covers native storage server announcement parsing, plugin matching, Foolscap storage adapters, plugin web resources, static server configuration, introducer-driven broker updates, HTTP-over-Foolscap upgrade selection, connection threshold notifications, and the helper that races multiple HTTP NURLs and chooses the first successful endpoint.

## Important APIs, Types, And Helpers
The main production APIs are `NativeStorageServer`, `HTTPNativeStorageServer`, `StorageFarmBroker`, `StorageClientConfig`, `_FoolscapStorage`, `_NullStorage`, `_pick_a_http_server`, `IFoolscapStorageServer`, `IStorageServer`, `IConnectionStatus`, `ANONYMOUS_STORAGE_NURLS`, and `MissingPlugin`. Test helpers include `NativeStorageServerWithVersion`, `new_tub`, `make_broker`, `SpyEndpoint`, and `SpyHandler`.

The test classes are `TestNativeStorageServer`, `GetConnectionStatus`, `UnrecognizedAnnouncement`, `PluginMatchedAnnouncement`, `FoolscapStorageServers`, `StoragePluginWebPresence`, `TestStorageFarmBroker`, and `PickHTTPServerTests`. Fixtures such as `UseNode`, `UseTestPlugins`, `MemoryIntroducerClient`, `SameProcessStreamEndpointAssigner`, `TempDir`, and `WebishServer` provide an in-process node, introducer, web server, and test storage plugin environment.

## Control Flow
The announcement tests instantiate `NativeStorageServer` with modern, old, missing, unrecognized, and plugin-shaped announcements. They call connection lifecycle methods (`start_connecting`, `stop_connecting`, `try_to_connect`) and accessor methods to ensure unsupported announcements degrade to `_NullStorage` or raise `MissingPlugin` only when explicit plugin configuration requires it.

Plugin tests create a node with a configured dummy storage plugin, publish storage announcements to the node's introducer subscription, and inspect the `StorageFarmBroker.servers` entry. Matching announcements produce a plugin-backed storage client that verifies `IFoolscapStorageServer` and receives the expected configuration and announcement. Non-enabled plugin names are ignored.

Storage broker tests configure static servers from YAML, simulate duplicate introducer announcements, verify permutation seed derivation from explicit base32 values, server public-key-like identifiers, or hashed server ids, and test service replacement when an initially Foolscap-only announcement is updated with HTTP NURLs and `force_foolscap = False`. The connection-threshold test uses fake Foolscap `Tub`s and `SpyHandler` endpoints to observe connection attempts, then injects `LocalWrapper(StorageServer(...))` references until `when_connected_enough(5)` fires.

`PickHTTPServerTests` provides a fake `Clock` and request function whose Deferreds fire after configured delays. `_pick_a_http_server` is expected to ignore early failures, return the first successful URL, or raise `MultiFailure` containing all reasons when every candidate fails.

## State And Persistence Behavior
Most tests use temporary node directories containing `private/` and generated node configuration. Static server configuration is loaded from YAML into the broker and persists in broker memory as `_static_server_ids` and `servers`. Plugin web-resource tests exercise persistent in-memory plugin resource state across HTTP requests by checking a counter increases on repeated calls to `/storage-plugins/<plugin>/counter`.

Broker state is Twisted service state. Tests assert old services are running and parented to the broker, then become stopped and unparented when replaced by `HTTPNativeStorageServer`. The connection-threshold test keeps mutable lists of pending fake `Tub`s and observed connection attempts to model asynchronous Foolscap connection establishment.

## Dependencies And Integration Points
The file depends on Foolscap `Tub`, connection hint handlers, Twisted `Service`, Deferreds, Trial, `FilePath`, `Clock`, `hyperlink.URL`/`DecodedURL`, testtools matchers, attrs, and zope interface verification. It integrates with Tahoe node configuration (`config_from_string`, `EMPTY_CLIENT_CONFIG`), introducer subscription handling, web resources, storage plugin loading, storage server wrappers, and HTTP NURL announcement keys.

The plugin tests are an important integration point between the introducer announcement schema (`storage-options`) and plugin-provided `IFoolscapStoragePlugin` clients. The HTTP upgrade test is an integration point between storage-client policy and the newer HTTP storage protocol advertisement key.

## Risks And Edge Cases
Covered risks include old servers lacking `available-space`, announcements missing nicknames, entirely unrecognized announcements, configured-but-missing plugins, plugin name mismatches, plugin resources losing state between requests, duplicate static/introducer server ids, incorrect permutation seed derivation, stale Foolscap services after HTTP upgrade, connection thresholds firing too early, and losing failure reasons when all HTTP NURLs fail.

Residual risk is mostly around simulated networking. Foolscap negotiation is skipped by directly injecting a local reference, so these tests verify broker orchestration and state transitions rather than full network handshakes. The hard-coded Tub certificate improves performance but means certificate-generation behavior is not exercised here.

## Test Signals
Passing this file signals that storage discovery remains backward-compatible, plugin matching is explicit and safe, static server declarations override duplicate introducer announcements, HTTP storage announcements are preferred when allowed, connection waiters are notified only after enough usable servers connect, and multi-NURL HTTP selection reports useful aggregate failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_http.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_http.py

## Purpose
This file tests the Tahoe-LAFS HTTP storage protocol client and server together with in-memory Twisted/treq infrastructure. It covers common HTTP utilities, authorization secret extraction, storage-index route parsing, client and server CBOR schema validation, request body limits/timeouts, immutable upload/download/abort APIs, mutable read/test/write APIs, shared read/range/lease/corruption APIs, and HTTP error-code mapping.

## Important APIs, Types, And Helpers
The production APIs under test include `HTTPServer`, `BaseApp`, `_authorized_route`, `_add_error_handling`, `_extract_secrets`, `Secrets`, `ClientSecretsException`, `StorageIndexConverter`, `read_encoded`, server `_SCHEMAS`, `StorageClient`, `StorageClientFactory`, `StorageClientGeneral`, `StorageClientImmutables`, `StorageClientMutables`, `ImmutableCreateResult`, `UploadProgress`, `TestWriteVectors`, `WriteVector`, `ReadVector`, `ReadTestWriteResult`, `TestVector`, `ClientException`, `limited_content`, `_encode_si`, `get_content_type`, `CBOR_MIME_TYPE`, and `response_is_not_html`.

The main test/support types are `HTTPUtilities`, `ExtractSecretsTests`, `RouteConverterTests`, `TestApp`, `CustomHTTPServerTests`, fake `Reactor`, `HttpTestFixture`, `StorageClientWithHeadersOverride`, `assert_fails_with_http_code`, `GenericHTTPAPITests`, `ImmutableHTTPAPITests`, `MutableHTTPAPIsTests`, `SharedImmutableMutableTestsMixin`, `ImmutableSharedTests`, and `MutableSharedTests`. `SECRETS_STRATEGY`, `_post_process`, `SWISSNUM_FOR_TEST`, `gen_bytes`, and `result_of` provide reusable inputs and synchronous Deferred extraction.

## Control Flow
Utility tests validate header parsing, base64 authorization secret extraction, and the werkzeug storage-index route converter. `TestApp` is a minimal Klein app with authorized routes for no-op calls, upload-secret verification, intentionally invalid version responses, bounded byte generation, never-finishing streaming responses, broken connections, and CBOR body reads.

`CustomHTTPServerTests` builds a `StorageClient` over `StubTreq(TestApp.resource())`. It checks bad swissnum decoding, malformed Tahoe authorization secrets, `_authorized_route` enforcement, client-side schema validation, `limited_content` success and oversize failures, quiescent timeout cancellation after no body data for 60 seconds, cleanup of timeout delayed calls on failed responses, CBOR default content type, and unsupported request content types.

`HttpTestFixture` creates a fake reactor with `callFromThread`, patches Twisted's global `Cooperator`, creates a real `StorageServer`, wraps it in `HTTPServer`, attaches `StubTreq`, and exposes `result_of_with_flush` to drive async endpoints by advancing fake time, flushing treq, and briefly sleeping for threadpool-backed work. The generic API tests then exercise missing/bad authentication, unsupported `Accept`, version responses, and server-side schema validation.

Immutable API tests allocate uploads, write content chunks with `Content-Range`, read back ranges, list shares only after completion, reject wrong upload secrets, allocate additional shares without overwriting in-progress uploads, reject malformed content ranges, return 404 for missing storage indexes or share numbers, keep shares separate, surface conflicts for mismatching overlapping chunks, allow reupload after timeout or abort, reject unknown/unauthorized/too-late aborts, and return 404 for lease renewal on unknown storage indexes.

Mutable API tests create shares via read/test/write vectors, read small and large data, verify combined read/test/write reads pre-write state, apply writes only when test vectors match, list mutable shares, return 404 for unknown mutable lists, and reject wrong write enablers without modifying share data. Shared mixin tests run over both immutable and mutable clients for corruption advisories, unknown-share advisory 404s, lease renew/add behavior, wrong storage-index/share read failures, invalid `Range` headers, full-body reads with no range, and `Content-Range` response headers.

## State And Persistence Behavior
Each fixture creates a temporary `StorageServer` rooted in a `TempDir`; all immutable and mutable operations persist actual Tahoe share files through the normal server implementation. Immutable uploads have in-progress writer state protected by upload secrets and timeout/abort behavior; only finished shares appear in list/read results. Mutable shares persist write-vector changes immediately when tests pass and retain their write-enabler secret for authorization.

Lease state is verified through server-side `get_leases` or `get_slot_leases`. Tests advance the fake clock to confirm renewals and new leases receive expected expiration times. Corruption advisory tests replace `StorageServer.advise_corrupt_share` with a recorder to confirm the HTTP layer passes kind, storage index, share number, and UTF-8 reason bytes.

HTTP body state is also modeled. `limited_content` accumulates streamed response bytes up to a caller-specified cap, sets delayed calls for silence timeouts, and must cancel those delayed calls on completion or failure. The fake reactor queue ensures call-from-thread callbacks are executed when time advances.

## Dependencies And Integration Points
The file depends on treq test utilities, Klein, werkzeug routing, Twisted HTTP/Headers/Clock/Cooperator/Deferreds, Hypothesis, fixtures, pycddl schema validation, `collections_extended.RangeMap`, and Tahoe CBOR utilities. It integrates the HTTP server and client modules against the real `StorageServer` rather than mocks for most protocol endpoints.

Important integration points are HTTP status codes (`401`, `400`, `406`, `416`, `404`, `409`, `405`), `Authorization` swissnum handling, `X-Tahoe-Authorization` secret headers, CBOR request/response schemas, `Range`/`Content-Range` request and response handling, immutable upload progress encoding through `RangeMap`, and shared semantics between mutable and immutable endpoints.

## Risks And Edge Cases
Covered risks include malformed auth headers, invalid base64/secret lengths, unsupported MIME types, schema drift, oversized responses, silent or failed streaming responses, missing content-type defaults, invalid storage-index path segments, in-progress upload overwrite, wrong upload keys, conflicting chunks, upload timeout/abort cleanup, late aborts, mutable conditional-write races, wrong write enablers, lease renewal on missing shares, range-header parsing, and corruption reports for unknown shares.

Residual risks include the fact that tests use in-memory treq and fake reactor traversal rather than a real TCP server. Some async paths still rely on short real sleeps in `result_of_with_flush` for backend threadpool behavior. Large mutable data is tested at 50MB, which is useful for streaming/producer behavior but can be costly in constrained CI.

## Test Signals
Passing this file signals the HTTP storage protocol can authorize, validate, encode, stream, and map errors consistently across client and server. It also confirms the HTTP layer preserves core `StorageServer` semantics for immutable and mutable shares, including upload progress, range reads, leases, aborts, conflicts, corruption advisories, and shared read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_http.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_https.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_https.py

## Purpose
This file tests the TLS-specific part of Tahoe-LAFS HTTP storage, especially SPKI-hash pinning used as a replacement for Foolscap-style server authentication. It validates RFC 7469-style SubjectPublicKeyInfo hashing against test vectors and checks that the HTTP storage HTTPS client policy accepts only the pinned certificate hash while ignoring normal CA validity windows when the pin matches.

## Important APIs, Types, And Helpers
The production APIs are `get_spki`, `get_spki_hash`, `_StorageClientHTTPSPolicy`, and `_TLSEndpointWrapper`. Test infrastructure uses certificate helpers `generate_private_key`, `generate_certificate`, `private_key_to_file`, and `cert_to_file`, plus Twisted `serverFromString`, `Site`, static `Data`, web `Agent`, `HTTPConnectionPool`, `ResponseNeverReceived`, and treq `HTTPClient`.

The test classes are `HTTPSNurlTests` and `PinningHTTPSValidation`. `spki_test_vectors_path` points to `data/spki-hash-test-vectors.yaml`. `PinningHTTPSValidation.listen` is an async context manager that binds a local HTTPS endpoint using the supplied key/certificate, serves a small static body, and stops listening on exit. `request` creates a non-persistent HTTPS treq client using `_StorageClientHTTPSPolicy(expected_spki_hash=...)`.

## Control Flow
`test_spki_hash` loads YAML vector cases, parses PEM certificates with `cryptography.x509`, extracts expected SPKI bytes and URL-safe base64 hashes, and asserts both low-level `get_spki` and higher-level `get_spki_hash` match each vector.

The pinning tests allocate a same-process endpoint, generate private keys and self-signed certificates, write them to temporary files, wrap the endpoint with `_TLSEndpointWrapper.from_paths`, and issue HTTPS GET requests. `test_success` uses the same certificate for server and expected pin and expects the static body. `test_server_certificate_has_wrong_hash` uses one certificate on the server and a different certificate as the expected pin and expects `ResponseNeverReceived`. `test_server_certificate_expired` and `test_server_certificate_not_valid_yet` prove that pin match, not X.509 date validity, controls acceptance.

## State And Persistence Behavior
The tests write temporary private-key and certificate files via `FilePath(self.mktemp())`. The HTTPS server exists only inside the async context manager and is explicitly stopped with `stopListening`; cleanup is followed by `spin_until_cleanup_done` in `tearDown` to avoid dirty reactor state. The client uses a non-persistent `HTTPConnectionPool` so connections are not kept open after each request.

No Tahoe storage shares are persisted here. The persistent artifacts are limited to temporary certificate/key files and the YAML test-vector file read from the source tree.

## Dependencies And Integration Points
This file depends on `cryptography.x509`, PyYAML, Twisted endpoints/web/client, treq, Tahoe certificate-generation test helpers, Tahoe HTTP common TLS hash helpers, and Tahoe HTTP client/server TLS integration. It is the direct integration point between NURL pin material, TLS endpoint wrapping, and the client policy used by HTTP storage.

## Risks And Edge Cases
Covered risks include incorrect SPKI extraction, incorrect URL-safe base64 hash generation, accepting the wrong server certificate, rejecting pinned self-signed certificates because of normal CA validation, rejecting expired/not-yet-valid pinned certificates, and leaking reactor/listening-port resources after TLS tests.

Residual risk includes private-key/certificate mismatch handling. The file notes this is hard to test because OpenSSL refuses to listen with mismatched material. The tests also focus on single-request HTTPS behavior and intentionally avoid persistent connections.

## Test Signals
Passing this file signals that Tahoe-LAFS HTTP storage can authenticate HTTPS servers by SPKI hash, that vector-compatible pin strings are generated, and that TLS validation policy is intentionally pin-based rather than CA/date-based for these storage connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_https.py -->
