# Research: subset-b-007899

Grouped research for Tahoe-LAFS test infrastructure and mutable-file tests. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common.py

Purpose: Provides broad Tahoe-LAFS test-suite scaffolding: fake file nodes, in-memory introducer records, Twisted endpoint fixtures, corruption helpers, HTTP/error assertions, and Tahoe-specific `testtools`/Trial test case classes.

Important APIs and types: `FakeDisk` models disk accounting and raises `NoSpace`; `MemoryIntroducerClient`, `Subscription`, `Announcement`, and `get_published_announcements` model introducer behavior. `UseTestPlugins`, `AdoptedServerPort`, and `SameProcessStreamEndpointAssigner` install test endpoint parsers and allocate reliable same-process listening endpoints. `FakeCHKFileNode` and `FakeMutableFileNode` implement enough of immutable/mutable node interfaces for web and directory tests. URI helpers create CHK, SDMF, MDMF, and verifier caps. `WebErrorMixin`, `ErrorMixin`, corruption helpers, `ConstantAddresses`, `disable_modules`, `SyncTestCase`, `AsyncTestCase`, `AsyncBrokenTestCase`, and `TrialTestCase` are reused throughout tests.

Control flow: Fixture setup mutates Twisted plugin search paths, pre-binds sockets when possible, writes generated node configuration, and returns Deferred-compatible fake nodes. Fake file nodes resolve reads from in-memory dictionaries and build synthetic check/deep-check results. Corruption helpers parse immutable or mutable share headers and mutate targeted fields. Test cases wrap `testtools` run-test factories in Eliot logging via `EliotLoggedRunTest`.

State and persistence: Most state is in-memory: fake content dictionaries, socket cleanup callbacks, introducer announcements, mutable `file_types`, and `tempfile.tempdir` cleanup. `UseNode` writes introducer/client config under a test `FilePath`; `SameProcessStreamEndpointAssigner` holds bound sockets until teardown. No durable production state is mutated.

Dependencies and integration points: Integrates Twisted reactors/endpoints, `testtools`, `treq`, Tahoe URI/check/storage/mutable interfaces, RSA/Ed25519 helpers, storage clients, upload/download helpers, and `allmydata.test.common_util`. It is a central dependency for Tahoe tests that need fake nodes, async test cases, HTTP assertions, or share corruption.

Risks: Fake nodes only partially implement interfaces and may mask production behavior. `mktemp()` and random port fallback can be collision-prone. Some corruption helpers contain unreachable or suspicious slices, so they should be treated as historical test tools rather than general parsers. `disable_modules` only handles top-level modules and must restore `sys.modules` even on failures. `AsyncBrokenTestCase` signals tests that depend on extra reactor cleanup.

Test signals: Downstream tests should cover fake node upload/download/check behavior, read-only mutable caps, exact corruption outcomes, socket reuse on supported reactors, plugin cleanup, Eliot-wrapped async failures, HTTP error body assertions, and reactor cleanup after async tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_storage.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_storage.py

Purpose: Supplies tiny synchronous helpers for directly placing immutable and mutable shares into a `StorageServer` during tests.

Important APIs and functions: `upload_immutable(storage_server, storage_index, renew_secret, cancel_secret, shares)` allocates buckets and writes each immutable share. `upload_mutable(storage_server, storage_index, secrets, shares)` builds test/write vectors and invokes mutable slot write APIs.

Control flow: Immutable uploads call `allocate_buckets`, then write each returned writer at offset zero and close it. Mutable uploads convert each share into `(test_vectors, write_vectors, new_length)` format and call `slot_testv_and_readv_and_writev` with an empty read vector.

State and persistence: The helpers persist share data into the supplied storage server's backing store. They do not track cleanup or leases beyond the arguments passed to the storage APIs.

Dependencies and integration points: Depends on the `StorageServer` immutable bucket API and mutable slot vector API. Used by tests that need pre-arranged storage state without going through full publisher code.

Risks: `upload_immutable` assumes all shares have the same length and uses the first value as the allocation size. Existing `already` buckets are ignored, so tests must supply fresh or intentionally overwrite-compatible inputs. Mutable writes perform no validation beyond whatever the storage server enforces.

Test signals: Exercise empty and multi-share maps, pre-existing shares, mismatched immutable share lengths, mutable test-vector failures, and expected lease/secret behavior in storage tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_storage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_system.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_system.py

Purpose: Provides integration-test infrastructure for running actual introducer and client nodes in-process, with deterministic certificates, assigned ports, HTTP cleanup, and connection polling.

Important APIs and functions: `SYSTEM_TEST_CERTS` supplies precomputed Tub cert/key PEMs. `flush_but_dont_ignore`, `_render_config`, `_render_config_section`, and `_render_section_values` support teardown and config generation. `spin_until_cleanup_done` waits for reactor file descriptors and delayed calls to drain. `SystemTestMixin` owns node grid setup, HTTP client pool tuning, service parenting, introducer/client config generation, node bouncing, extra-node creation, and connection readiness checks.

Control flow: `setUp` enables optional blocking detection, activates HTTP storage client test mode, installs a `SameProcessStreamEndpointAssigner`, and starts a `MultiService`. `_create_introducer` writes introducer config and optional fixed certs, then starts an introducer. `set_up_nodes` creates the introducer, writes client configs, starts the first client to capture helper fURL, starts remaining clients, waits for introducer/storage connectivity, and records web URLs. `tearDown` stops services, flushes Foolscap events, closes HTTP pools, and spins for reactor cleanup.

State and persistence: Writes `tahoe.cfg`, `private/introducers.yaml`, `private/node.pem`, and helper fURL files under each test basedir. Keeps process-local service parent, client list, introducer URL, helper fURL, web URLs, and HTTP connection pools. Certificate material is static test-only data.

Dependencies and integration points: Uses Twisted reactor/services, Foolscap flushing, Tahoe client/introducer creation, file utilities, storage client classes, HTTP client factory test hooks, `pollmixin`, `StallMixin`, and `SameProcessStreamEndpointAssigner`.

Risks: Fixed certificates are expired and suitable only for controlled tests. `spin_until_cleanup_done` reaches into reactor internals such as `_internalReaders`. Connection waiting can take up to 200 seconds and assumes every client should connect to every storage server. Aggressive HTTP timeouts are tuned for local tests and may be brittle on loaded hosts.

Test signals: Validate both Foolscap and HTTP storage modes, helper fURL propagation, client bounce and extra-node behavior, service shutdown without dirty reactors, port assignment reuse, HTTP pool closure, and correct server-class assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_system.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_util.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_util.py

Purpose: Collects general test utilities for CLI execution, random byte mutation, Deferred-friendly failure assertions, signal/reactor cleanup, and timezone manipulation.

Important APIs and types: `skip_if_cannot_represent_filename`, `run_cli_native`, `run_cli_unicode`, `run_cli`, and `parse_cli` exercise Tahoe CLI code in-process. `DevNullDictionary`, `insecurerandstr`, `flip_bit`, and `flip_one_bit` support mutation tests. `ReallyEqualMixin`, `SignalMixin`, `StallMixin`, `FakeCanary`, `ShouldFailMixin`, `TestMixin`, and `TimezoneMixin` provide reusable test behaviors.

Control flow: CLI helpers construct argv, wrap stdin/stdout/stderr in `TextIOWrapper`/`BytesIO`, parse options, dispatch through `runner.dispatch`, and convert normal completion or `SystemExit` to `(rc, stdout, stderr)`. `ShouldFailMixin.shouldFail` runs a callable through `maybeDeferred`, traps expected Failures, checks message substrings, and returns a list-wrapped Failure for later inspection. `TestMixin.clean_pending` cancels delayed calls and optionally fails if the reactor was not quiescent.

State and persistence: Mutates process-level signal handlers for SIGCHLD, reactor delayed calls during cleanup, and `TZ` environment variable during timezone tests. CLI execution is in-process and does not spawn a separate Tahoe binary.

Dependencies and integration points: Depends on Twisted reactor/failure/Trial, Tahoe CLI runner, encoding utilities, and assertion helpers. `FakeCanary` imitates Foolscap disconnect notification for storage tests.

Risks: `clean_pending` cancels all delayed calls visible to the global reactor and can hide ownership bugs when used permissively. `run_cli_native` defaults encoding from `sys.stdout` and may not perfectly match subprocess behavior. `flip_bit`/`flip_one_bit` assume non-empty byte slices. Timezone restoration deletes `TZ` when originally absent and requires cleanup ordering.

Test signals: Cover CLI success and `SystemExit` paths, Unicode argv/stdin encodings, Deferred and synchronous failure assertions, canary disconnect ordering, signal handler restoration, reactor quiescence enforcement, and timezone restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_web.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_web.py

Purpose: Provides HTTP and Twisted Web helpers for Tahoe web tests, including body-returning requests and direct resource rendering.

Important APIs and functions: `VerboseError` extends `twisted.web.error.Error` to include response body text. `do_http(method, url, **kwargs)` performs a non-persistent `treq` request and returns response bytes. `render(resource, query_args)` renders a Twisted `Resource` against a synthetic `TahoeLAFSRequest`.

Control flow: `do_http` awaits `treq.request`, reads content, raises `VerboseError` for 4xx/5xx status codes, and returns the body otherwise. `render` builds a `DummyChannel` and request, calls `resource.render`, handles `UnsupportedMethod` as 405, waits for synchronous bytes or `NOT_DONE_YET`, then parses the HTTP wire response to return only the body.

State and persistence: Uses transient in-memory request/channel objects. No durable state is written.

Dependencies and integration points: Integrates `treq`, Twisted Web test helpers, `TahoeLAFSRequest`, `NOT_DONE_YET`, and HTTP status constants. Used by resource-level tests that avoid starting a full web server.

Risks: `render` always uses GET and minimal request fields, so resources depending on richer request state may not be represented. Splitting the raw response at `\r\n\r\n` assumes a complete HTTP header/body serialization. `do_http` carries a TODO for replacing manual status handling with `fail_for_status`.

Test signals: Exercise successful body reads, 4xx/5xx body reporting, unsupported methods, asynchronous render completion, already-finished `NOT_DONE_YET`, and invalid resource return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_web.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/data/spki-hash-test-vectors.yaml -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/data/spki-hash-test-vectors.yaml

Purpose: Stores certificate/SPKI hash fixtures used to verify SubjectPublicKeyInfo extraction and hash encoding behavior.

Important data shape: The top-level `vector` list contains entries with `expected-hash`, `expected-spki`, and PEM `certificate` fields. Vectors include RSA public keys of different sizes and an Ed25519-style key, giving coverage for multiple key algorithms and DER encodings.

Control flow: This YAML file has no executable control flow. Tests load it, parse each certificate, extract SPKI DER, compare it with `expected-spki`, and compare the derived hash with `expected-hash`.

State and persistence: Static test data only; no runtime mutation. Certificates are fixtures and not trusted operational credentials.

Dependencies and integration points: Consumed by crypto/certificate tests, likely through YAML parsing and cryptography/OpenSSL primitives for certificate loading and SPKI derivation. The base64/base64url fields must stay compatible with those consumers.

Risks: Fixture correctness is binary: a typo in line wrapping, padding, or PEM indentation can break parsing or mask hash regressions. Certificates may be expired, but expiration should be irrelevant for SPKI extraction tests.

Test signals: Confirm all vectors parse, extracted DER equals `expected-spki`, hash encoding equals `expected-hash`, and test logic ignores certificate validity periods while still rejecting malformed fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/data/spki-hash-test-vectors.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/eliotutil.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/eliotutil.py

Purpose: Integrates Eliot structured logging with Tahoe test execution so every test runs inside a named Eliot action and emitted messages are validated.

Important APIs and types: `RUN_TEST` is an Eliot `ActionType` with a test-name field. `EliotLoggedRunTest` composes a delegated `RunTest` factory and patches the actual test method. `with_logging(test_id, test_method)` decorates a callable with a validating `MemoryLogger`. `_TwoLoggers` implements `ILogger` and forwards messages to the original logger plus the validation logger.

Control flow: `EliotLoggedRunTest.run` grabs the test method by `_testMethodName`, wraps it with `with_logging`, monkey-patches it onto the case, invokes the delegated runner, and restores the patch. `with_logging` swaps the global logger to `_TwoLoggers`, opens a `RUN_TEST` action, runs the test, checks Eliot validation errors, and restores the original logger in `finally`.

State and persistence: Temporarily mutates the test case method and Eliot global logger. Validation logs are in-memory and discarded after the test. No filesystem persistence.

Dependencies and integration points: Depends on Eliot, `eliot.testing`, Twisted `MonkeyPatcher`, `attrs`, Zope `ILogger`, `six.ensure_text`, and Tahoe's `AnyBytesJSONEncoder`. Used by `common.py` test case classes as their `run_tests_with` wrapper.

Risks: Global logger swapping is process-wide and sensitive to concurrent test execution. Errors raised during validation occur inside test invocation and can alter failure reporting. `_TwoLoggers` assumes both logger objects implement `write`; a missing original logger would be unsafe if Eliot ever returned `None`.

Test signals: Verify successful log capture, validation failure surfacing, logger restoration on exceptions, delegated runner compatibility, bytes JSON encoding, and test method restoration after repeated runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/eliotutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/matchers.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/matchers.py

Purpose: Defines `testtools` matchers for Tahoe-specific structures such as node public keys, storage announcements, fURLs, NURLs, base32 values, and equality between tuple elements.

Important APIs and types: `MatchesNodePublicKey` verifies a signing key against the private key stored in a node config. `matches_storage_announcement` builds a structural matcher for introducer storage announcements. `matches_furl`, `matches_nurls`, and `matches_base32` use preprocessing decoders with permissive `Always` matching. `MatchesSameElements` asserts a two-tuple has equal elements.

Control flow: Public-key matching reads node config, reconstructs the private key, signs empty bytes, derives the public key from the candidate key, and verifies the signature. Announcement matching composes `MatchesStructure` and `MatchesDict` with optional anonymous storage and plugin option fields.

State and persistence: Reads private node config from `basedir` at match time. No writes or persistent mutation.

Dependencies and integration points: Uses `attrs`, `hyperlink.DecodedURL`, `testtools.matchers`, Foolscap fURL decoding, Tahoe base32, node config loading, and Ed25519 crypto helpers. Used by tests that assert introducer announcements and node identity.

Risks: `matches_furl`, `matches_nurls`, and `matches_base32` accept any successfully decoded value but do not validate semantic constraints beyond decoding. `MatchesNodePublicKey` reads live config, so changes to test directories between matcher construction and execution affect results.

Test signals: Cover matching and mismatching node keys, malformed fURLs/NURLs/base32 values, anonymous and non-anonymous announcement shapes, storage option list matching, and `MatchesSameElements` mismatch messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/matchers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/__init__.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/__init__.py

Purpose: Marks `allmydata.test.mutable` as a Python package for mutable-file tests.

Important APIs and functions: No public APIs, imports, or executable definitions are present.

Control flow: No runtime control flow.

State and persistence: No state or persistence.

Dependencies and integration points: Enables relative imports among mutable test modules such as `.util`, `test_filenode`, `test_checker`, and problem/encoding tests.

Risks: Minimal; package-level side effects are intentionally absent. Adding imports here could change test discovery or introduce global setup costs.

Test signals: Importing `allmydata.test.mutable` should remain side-effect free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_checker.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_checker.py

Purpose: Tests mutable-file checker and verifier behavior for SDMF and MDMF files under missing shares, insufficient shares, corrupted signatures, corrupted blocks, corrupted share hashes, and corrupted encrypted private keys.

Important APIs and functions: `Checker` inherits `AsyncTestCase`, `CheckerMixin`, and `PublishMixin`. Test methods call `_fn.check(Monitor(), verify=...)`, `publish_mdmf`, `publish_sdmf`, `corrupt`, and checker mixin assertions such as `check_good`, `check_bad`, and `check_expected_failure`.

Control flow: `setUp` publishes one mutable file. Each test mutates fake storage directly or via `corrupt`, then runs check or verify. Non-verify checks are expected to miss raw block corruption, while verify paths read enough share data to find block hash, share hash, signature, and private-key problems. Empty SDMF/MDMF files are verified and then flush Foolscap eventual events.

State and persistence: Uses fake in-memory storage from `.util`; tests clear or edit `_storage._peers` share dictionaries. No durable filesystem state.

Dependencies and integration points: Exercises Tahoe mutable checker/verifier, `Monitor`, `CorruptShareError`, Foolscap eventual queue flushing, and the shared publish/corruption helper layer.

Risks: Tests depend on exact storage layout labels such as `share_data`, `block_hash_tree`, `share_hash_chain`, and `enc_privkey`. Read-only verification intentionally cannot validate encrypted private-key corruption, so behavior differs by cap authority.

Test signals: Healthy files stay recoverable; no/insufficient shares are bad; verify detects byte-level corruption; checker-only mode does not inspect all block data; readonly nodes treat private-key corruption as uncheckable; empty mutable files verify cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_checker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_datahandle.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_datahandle.py

Purpose: Tests `MutableData`, the in-memory mutable uploadable wrapper.

Important APIs and functions: `DataHandle.setUp` creates repeated byte test data and wraps it in `MutableData`. Tests cover `read(chunk_size)` and `get_size()`.

Control flow: Read tests repeatedly call `read(10)` and compare joined chunks to sequential slices. Size tests assert the declared size equals the original bytes and that `get_size` does not disturb the read cursor.

State and persistence: State is the `MutableData` object's in-memory cursor and byte buffer. No files or storage servers are touched.

Dependencies and integration points: Uses `SyncTestCase`, `MutableData`, and `testtools` matchers `Equals`/`HasLength`. This validates uploadable behavior consumed by mutable publisher tests.

Risks: The test assumes `read` returns an iterable of byte chunks rather than a single bytes object. Cursor preservation around `get_size` is the main contract.

Test signals: Sequential reads must be ordered and complete; `get_size` must be idempotent and non-seeking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_datahandle.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_different_encoding.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_different_encoding.py

Purpose: Verifies that a mutable file created with one total-share encoding can later be modified by a client configured with a different encoding.

Important APIs and functions: `DifferentEncoding` builds `FakeStorage` and a nodemaker. `test_filenode` modifies `default_encoding_parameters["n"]`, creates a mutable file, reconstructs it from its cap after disabling object reuse, changes `n` again, and calls `modify`.

Control flow: The test creates a 3-of-20 file, discards the original node object, creates a new node from the cap with 3-of-10 defaults, and performs a modifier that replaces the contents.

State and persistence: Uses in-memory fake storage and mutable nodemaker defaults. No filesystem state.

Dependencies and integration points: Depends on `.util.FakeStorage`, `.util.make_nodemaker`, `AsyncTestCase`, and mutable filenode modification logic.

Risks: The test targets historical issue behavior where clients latched to incompatible encoding assumptions. It does not assert downloaded contents, only that modification completes.

Test signals: A successful Deferred is the primary signal; failure would indicate servermap/publisher assumptions tied too strongly to the creator's encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_different_encoding.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_exceptions.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_exceptions.py

Purpose: Tests repr output for mutable exception classes.

Important APIs and functions: `Exceptions.test_repr` constructs `NeedMoreDataError` and `UncoordinatedWriteError` and checks their class names appear in `repr`.

Control flow: Straight-line synchronous assertions.

State and persistence: No state beyond exception instances.

Dependencies and integration points: Uses `SyncTestCase` and exception types from `allmydata.mutable.common`.

Risks: Minimal; duplicate assertion for `NeedMoreDataError` appears redundant. The test intentionally checks representation shape rather than exact text.

Test signals: Repr should remain diagnostic and include exception class names for debugging mutable failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_exceptions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filehandle.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filehandle.py

Purpose: Tests `MutableFileHandle`, the file-like-object uploadable wrapper for mutable publishes.

Important APIs and functions: `FileHandle.setUp` wraps a `BytesIO` in `MutableFileHandle`. Tests cover sequential `read`, `get_size`, cursor preservation, operation against a real file object, and `close`.

Control flow: Reads walk the test data in 10-byte chunks; size tests call `get_size` between reads to ensure the handle seek position is restored. The real-file test writes bytes to a temporary file, opens it, wraps it, reads all content, and checks size. `test_close` closes the uploadable and asserts the underlying handle closed.

State and persistence: Uses in-memory `BytesIO` and one temporary directory/file under `mktemp`. No Tahoe storage state.

Dependencies and integration points: Depends on `SyncTestCase`, Python `BytesIO`, filesystem APIs, and `MutableFileHandle`. This behavior feeds mutable publisher upload paths that accept file handles.

Risks: The test opens a real file without a context manager and relies on process cleanup. Cursor preservation is essential; an implementation that seeks to compute size but does not restore would corrupt uploads.

Test signals: Sequential data equality, accurate size, no cursor movement from `get_size`, compatibility with real file objects, and underlying handle closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filehandle.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filenode.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filenode.py

Purpose: Provides broad mutable filenode behavior tests covering creation, cap types, SDMF/MDMF uploads and downloads, streaming retrieval producer behavior, modification semantics, retry/backoff on uncoordinated writes, maximum share counts, and size reporting.

Important APIs and functions: `Filenode` uses `FakeStorage`, `make_peer`, `make_nodemaker_with_peers`, `MutableFileNode`, `MutableData`, `BackoffAgent`, mutable modes, and several consumer fixtures. Key tests include `test_create`, `test_create_with_keypair`, MDMF cap/readcap/verifier-cap tests, `_test_retrieve_producer`, `test_modify`, `test_modify_backoffer`, and `test_size_after_servermap_update`.

Control flow: `setUp` creates fake storage with ten peer wrappers and a nodemaker. Creation tests publish empty or initial-content nodes and inspect storage/servermap state. Upload/download tests chain Deferred operations through servermap retrieval, overwrite, download, explicit upload, version download, and large-file paths. Producer tests read versions into consumers that pause or stop to assert `DownloadStopped`. Modify tests apply modifiers that change, do not change, return `None`, raise ordinary errors, raise `UncoordinatedWriteError`, or exceed historical size limits, then verify contents and sequence numbers.

State and persistence: All storage is fake/in-memory. Node defaults such as `n`, `k`, `happy`, key generator, and node cache are mutated per test. Sequence numbers and servermaps represent mutable-file version state in fake shares.

Dependencies and integration points: Exercises mutable filenode, publisher, retriever, servermap, cap parsing, RSA key generation, Tahoe client key generator, consumer producer interfaces, and async broken test support for lingering reactor work.

Risks: Many assertions rely on fake storage internals such as `_peers`, peer write counts, and sequence-number expectations. `AsyncBrokenTestCase` indicates some paths leave extra reactor activity. Large MDMF tests allocate multi-megabyte byte strings and may be resource-sensitive.

Test signals: Correct cap class selection, one share per peer under default placement, support for one-share and 255-share configurations, MDMF segmented download correctness, producer stop/pause error propagation, modifier idempotence/no-op handling, UCWE retry/backoff behavior, and accurate size after servermap updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filenode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_interoperability.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_interoperability.py

Purpose: Verifies that the current mutable downloader can read legacy SDMF shares.

Important APIs and data: `Interoperability` embeds ten base64-encoded old SDMF shares, an old SSK cap, and expected contents. `copy_sdmf_shares` writes decoded shares into a no-network grid's server share directories. `test_new_downloader_can_read_old_shares` downloads through a modern nodemaker-created node.

Control flow: The test sets up a grid, maps old shares to ten server numbers, computes the storage index from the cap, writes each share to `shares/<storage_index_dir>/<share>`, confirms all shares are found, constructs a node from the old cap, and downloads the best version.

State and persistence: Writes fixture shares into test server directories under the grid basedir. Class-level fixture bytes are static.

Dependencies and integration points: Uses `GridTestMixin`, `AsyncTestCase`, `ShouldFailMixin`, Tahoe URI parsing, storage index path mapping, file utilities, and no-network grid helpers.

Risks: Large inline fixtures are hard to review and easy to corrupt. The test assumes ten servers and direct on-disk storage layout compatibility. It validates one legacy fixture rather than a full migration matrix.

Test signals: All ten fixture shares are discoverable and `download_best_version` returns `b"This is a test file.\n"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_interoperability.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_encodings.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_encodings.py

Purpose: Tests retrieval behavior when shares for the same mutable file exist with multiple encoding parameters.

Important APIs and functions: `MultipleEncodings` uses `FakeStorage`, `make_nodemaker`, `MutableData`, `Publish`, `ServerMap`, `ServermapUpdater`, `MODE_READ`, and `DevNullDictionary`. `_encode(k, n, data, version)` publishes a temporary representation with custom required/total shares and returns captured peer shares.

Control flow: Setup creates an initial file in fake storage. `_encode` disables node cache, reconstructs from cap, copies key fields, changes `_required_shares`/`_total_shares`, clears storage, publishes, captures shares, and clears storage again. `test_multiple_encodings` creates 3-of-10, 4-of-9, and 4-of-7 share sets, manually merges chosen share numbers from each set into storage, fixes server query order, then downloads from a fresh node.

State and persistence: Mutates fake storage `_peers` and `_sequence`, nodemaker `_node_cache`, and temporary filenode internals. No filesystem state.

Dependencies and integration points: Exercises mutable publisher, servermap updater, retrieval version selection, storage broker server IDs, and fake storage ordering.

Risks: Directly copying private filenode fields and storage internals makes the setup fragile. The expected behavior is "first version recoverable", so a future policy change for multi-version retrieval would need test updates.

Test signals: Download should return the 3-of-10 contents once that version becomes recoverable despite earlier shares from incompatible encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_encodings.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_versions.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_versions.py

Purpose: Tests mutable-file behavior when the grid contains a mix of recoverable and unrecoverable versions.

Important APIs and functions: `MultipleVersions` inherits `PublishMixin` and `CheckerMixin`. It uses `_set_versions`, `download_best_version`, `get_servermap`, `check`, `modify`, `Monitor`, `MODE_READ`, and `MODE_CHECK`.

Control flow: `setUp` publishes multiple prepared versions. `test_multiple_versions` rewrites selected shares to older/newer versions, verifies best-version download, checker badness, unrecoverable newer version reporting, merge-needed detection for parallel recoverable versions, and acceptable download from either parallel version. `test_replace` modifies a mixed-version file and verifies a new highest sequence replaces outliers.

State and persistence: Uses fake share state created by `PublishMixin`; `_set_versions` mutates share contents by index. Servermap state is rebuilt from fake storage.

Dependencies and integration points: Exercises mutable servermap health classification, checker reporting, downloader version selection, and publisher replacement logic.

Risks: Version numbering in comments and indexes can be confusing: fixture indexes map to sequence numbers indirectly. Tests assume query ordering that reveals single-share unrecoverable versions.

Test signals: Latest recoverable version is downloaded, mixed versions are reported unhealthy, one newer unrecoverable share is tracked as `(1,3)` health without merge need, parallel recoverable versions set `needs_merge`, and modify produces one clean recoverable version at the expected highest sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_versions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_problems.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_problems.py

Purpose: Exercises mutable-file failure scenarios around stale servermaps, surprise concurrent writes, unexpected shares, bad or missing servers, private-key query failures, block/hash query failures, and a regression fixture for mutable share hash-tree validation.

Important APIs and types: `SameKeyGenerator` forces deterministic mutable keys. `FirstServerGetsKilled` and `FirstServerGetsDeleted` alter fake server behavior after selected calls. `Problems` uses `GridTestMixin`, `AsyncTestCase`, `ShouldFailMixin`, mutable modes, `MutableData`, `NotEnoughSharesError`, `NotEnoughServersError`, `UncoordinatedWriteError`, URI/hash helpers, storage path helpers, and class-level `TEST_1654_*` fixtures.

Control flow: Surprise tests capture an old servermap, perform a winning overwrite, then attempt upload or download using stale state and expect coordination/share errors. Server placement tests remove, replace, break, or restore servers around publishes and overwrites. Private-key and block/hash query tests install post-call notifiers that make one server fail or appear deleted after initial reads, then verify map update or download can continue. `test_1654` writes crafted two-share data to disk and expects retrieval to fail rather than return corrupted contents.

State and persistence: Uses no-network grid directories and writes fixture shares directly under storage-index paths. Mutates grid membership, server wrapper `broken` flags, nodemaker key generator/cache, server post-call notifiers, and stored share files.

Dependencies and integration points: Integrates mutable publish/retrieve/servermap code, no-network grid server management, Tahoe URI and storage layout helpers, RSA key generation, hash-based cap derivation, Foolscap logging, and file utilities.

Risks: These tests depend on internal fake-grid mechanics and sometimes fixed server query order. Direct disk fixture writes can become stale if storage layout changes. Some failure assertions check substrings, so wording changes can break tests. The large #1654 base64 fixtures are difficult to audit but security-sensitive.

Test signals: Stale publish paths raise `UncoordinatedWriteError`; stale retrieve raises `NotEnoughSharesError`; unexpected share placement is detected; publish succeeds with limited bad servers but fails with all/no servers; privkey/block/hash transient failures are tolerated when enough shares remain; crafted #1654 shares fail retrieval due to corruption detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_problems.py -->
