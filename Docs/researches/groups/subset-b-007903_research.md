# Research Report: subset-b-007903

This grouped report covers the Tahoe-LAFS test files assigned to work item `subset-b-007903`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents under `Docs/researches/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_hung_server.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_hung_server.py

## Purpose
This file exercises downloader behavior when storage servers are broken, missing shares, or hung. It covers both immutable and mutable setup paths where possible, but the actual hung-server behavior is only enabled for immutable tests because the mutable downloader is documented here as still broken for hung servers. The tests use the in-process no-network grid to simulate storage failures without real network services.

## Important APIs, Types, And Helpers
- `HungServerDownloadTest` combines `GridTestMixin`, `ShouldFailMixin`, `PollMixin`, and Trial `TestCase`.
- `_set_up(mutable, testdir, num_clients=1, num_servers=10)` builds a grid, uploads either immutable `upload.Data` or mutable `MutableData`, records `self.uri`, and discovers share files with `find_uri_shares`.
- `_start_download`, `_wait_for_data`, `_download_and_check`, and `_should_fail_download` abstract immutable `download_to_data` versus mutable `download_best_version`.
- `_break`, `_hang`, `_unhang`, `_hang_shares`, `_delete_all_shares_from`, `_copy_all_shares_from`, and `_corrupt_all_shares_in` manipulate the test grid and share files directly.
- `_copy_share` uses `storage_index_to_dir` and the underlying `ss.original._server.storedir` layout to duplicate share files onto another server.

## Control Flow
Most tests build a Deferred chain: set up a grid, mutate server/share state, then download and assert success or expected failure. The basic matrix includes 10 good shares, copied shares, three-good-seven-missing success, two-good-eight-broken failure, two-good-eight-missing failure, and duplicate-share failure. Immutable hung tests verify that stalled servers do not block a successful download if enough good shares can still be found or if a hung server later recovers.

`test_5_overdue_immutable` is the most specific control-flow test. It arranges for the first five selected servers to hang, forces the immutable `ShareFinder` to allow only five outstanding requests, starts a download, verifies the pending requests are stuck but not overdue, manually expires four overdue timers by resetting them to a negative delay, and then polls until the download completes from replacement requests. It asserts the final download data and the internal `pending_requests` and `overdue_requests` counts.

## State And Persistence
The tests persist real share files in the no-network grid's server storage directories. They delete, corrupt, and copy those files to manipulate Tahoe's view of available shares. The fixture stores mutable state in `self.uri`, `self.shares`, `self.servers`, `self.c0`, and sometimes `self._sf`. The overdue test directly mutates downloader runtime state (`max_outstanding_requests`, `OVERDUE_TIMEOUT`, timer handles) rather than persistent configuration.

## Dependencies And Integration Points
The file integrates with immutable upload/download, mutable publishing, URI parsing, storage index directory layout, the no-network grid server controls (`break_server`, `hang_server`, `unhang_server`), and the downloader `ShareFinder` internals. It also depends on `NotEnoughSharesError` and `UnrecoverableFileError` message text for failure assertions.

## Risks And Edge Cases
These tests intentionally reach into private implementation details such as `n._cnode._node._sharefinder`, storage server internals, and on-disk share layout. They can become brittle if downloader object structure or storage layout changes. The mutable hung tests are skipped, which is an explicit coverage gap. `test_10_good_copied_share` returns inside the loop after the first mutable state, so it does not actually exercise both mutable and immutable paths like similar tests do.

## Test Signals
Strong success signals are successful plaintext recovery under degraded or hung-server conditions and specific failure types when not enough distinct shares are recoverable. Performance/resilience signal comes from the overdue-timer test proving the downloader can make progress when outstanding requests stall. Skipped mutable tests signal known missing hung-server handling for mutable files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_hung_server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_i2p_provider.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_i2p_provider.py

## Purpose
This file unit-tests Tahoe's I2P provider and node-creation integration. It checks optional dependency handling, SAM endpoint probing, destination creation, listener descriptor construction, connection-hint handler selection, and configuration validation for `[i2p]`.

## Important APIs, Types, And Helpers
- `mock_txi2p` and `mock_i2p` patch the provider's optional import functions.
- `make_cli_config` builds `CreateNodeOptions` with a `runner.Options` parent and a `StringIO` stdout sink.
- `TryToConnect` tests `_try_to_connect`.
- `ConnectToI2P` tests `_connect_to_i2p`.
- `CreateDest` tests `i2p_provider.create_config`.
- `FakeConfig` implements the subset of `get_config` used by `i2p_provider.create`.
- `Provider`, `ProviderListener`, and `Provider_CheckI2PConfig` cover runtime provider methods and validation.

## Control Flow
The connection tests patch `clientFromString` and `txi2p.testAPI`, then assert handled `ConnectError` failures are converted to `None` plus stdout diagnostics while unexpected failures propagate. `_connect_to_i2p` is tested with default and explicit SAM endpoints and with the unreachable path raising `ValueError`.

Destination creation first verifies missing `txi2p` is fatal and launch-related CLI flags are rejected at option parsing. The SAM endpoint path creates `private/i2p_dest.privkey`, probes the SAM API, calls `generateDestination`, and returns node config plus tub ports/locations. Provider tests then verify handler choice for disabled config, unavailable optional modules, explicit SAM endpoint, launch modes, configdir mode, executable overrides, and default mode. The final validation class asserts specific errors for impossible destination config and success when the required keys are present.

## State And Persistence
The tests create temporary basedirs and private directories. `create_config` writes configuration values, including `dest.private_key_file` relative to `private/i2p_dest.privkey`. Runtime provider state is modeled through `FakeConfig` dictionaries and mocks; no real I2P process is launched.

## Dependencies And Integration Points
The file depends on Twisted Deferreds and endpoint strings, `twisted.python.usage.UsageError`, Tahoe's node creation CLI parser, `allmydata.util.i2p_provider`, and optional `txi2p`/`i2p` APIs. It verifies the exact contract between CLI options, Tahoe config sections, Foolscap tub listener descriptors, and txi2p handler constructors.

## Risks And Edge Cases
The tests assert exact error strings, endpoint descriptor escaping, and positional calls into optional libraries. Those are useful compatibility signals but brittle under message or dependency API changes. Launch destination mode is explicitly `NotImplementedError`, so the tested feature surface is partial. `FakeConfig` only implements the access pattern needed by these tests, so it may not catch broader config-object behavior.

## Test Signals
Passing tests show Tahoe can degrade cleanly when I2P dependencies are absent, reject impossible destination configs early, generate correct SAM destination config, and translate `[i2p]` settings into handlers/listeners without starting real network services.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_i2p_provider.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_immutable.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_immutable.py

## Purpose
This file focuses on immutable-file downloader behavior and a small `LiteralFileNode` equality contract. It validates share-finder behavior in a synthetic race, degraded downloads from the no-network grid, failure when not enough shares remain, and simple immutable node APIs such as `download_to_data`, `download_best_version`, size lookup, and readable-version lookup.

## Important APIs, Types, And Helpers
- `MockShareHashTree` and `MockNode` model the consumer side of immutable downloader/share-finder interactions.
- `TestShareFinder.test_no_reneging_on_no_more_shares_ever` targets ticket-style behavior where a share consumer must not be told "no more shares" and then receive another share.
- `Test` mixes `GridTestMixin`, Trial `TestCase`, and `ShouldFailMixin`.
- `startup` creates a two-client, five-server grid, lowers segment size to create multiple segments, sets `happy` to one, uploads `TEST_DATA`, and creates a read filenode from another client.
- Counter helpers read `storage_server.read`, `allocate`, and `write` counters.
- `LiteralFileNodeTests` verifies URI-based equality.

## Control Flow
The synthetic `ShareFinder` test creates a CHK verify cap and three mocked no-network servers. The first server asynchronously returns two shares and immediately asks the finder for more; the third returns the final share. The `MockNode` fails the test if it receives shares after `no_more_shares` or if fetch failure is reported incorrectly.

Grid-backed tests upload immutable data, directly delete or corrupt shares, and then attempt downloads. They verify normal downloads stay below a read-count threshold, downloads succeed from only three remaining shares, corrupted crypttext hash data can still allow recovery from remaining good shares, and too many missing or version-corrupted shares fail quickly. The filenode methods are then checked as aliases or simple immutable-node capabilities. Literal node equality compares `LiteralFileURI` identity and non-node comparisons.

## State And Persistence
The grid writes real share files and exposes storage server stats counters. Tests mutate share files through `delete_shares_numbered` and `corrupt_shares_numbered`. Runtime state includes `self.uri`, `self.filenode`, and captured share/counter data. There is no long-lived persistence beyond temporary test directories.

## Dependencies And Integration Points
The file integrates with immutable upload `Data`, immutable downloader `finder.ShareFinder`, no-network server wrappers, URI verify caps, downloader consumer APIs, storage stats providers, and corruption helpers in `allmydata.test.common`. It also documents a dependency on Tahoe's erasure parameters (`k=3`, `n=10` assumptions in several tests).

## Risks And Edge Cases
The file itself says `TODO: delete this whole file`, which suggests some coverage may be legacy or duplicated elsewhere. Read-count assertions are regression guards but can become noisy if downloader pipelining changes. The mocked share-finder behavior is tightly coupled to internal callback ordering.

## Test Signals
The strongest signal is that immutable download can recover from degraded share availability and detect unrecoverable states without excessive reads. The share-finder test guards a subtle asynchronous ordering bug. The literal-node test guards stable equality semantics for URI-backed immutable literal nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_immutable.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_introducer.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_introducer.py

## Purpose
This large file tests Tahoe introducer node creation, introducer client/server announcement handling, signed announcement semantics, reconnect behavior, persisted introducer client caches, insufficient-version failures, FURL decoding, and signature validation. It blends unit-style tests with full Foolscap service integration.

## Important APIs, Types, And Helpers
- `LoggingMultiService` provides a Twisted service parent with Tahoe-style logging.
- `Node` validates introducer directory creation, legacy import support, config-file conflict/migration behavior, unreadable `introducers.yaml`, and web static path resolution.
- `ServiceMixin` starts/stops a parent `MultiService` and flushes Foolscap eventual events.
- `Introducer`, `Client`, `Server`, `Queue`, `SystemTest`, `ClientInfo`, `Announcements`, `ClientSeqnums`, `NonV1Server`, `DecodeFurl`, and `Signatures` cover distinct introducer surfaces.
- `fakeseq`, `realseq`, `make_ann`, and `make_ann_t` create announcement payloads and signed Foolscap announcement tuples.
- `TooNewServer` simulates a future/unsupported introducer protocol version.

## Control Flow
Creation tests build introducer directories, exercise private versus legacy public `introducer.furl` paths, and assert conflicts or migrations. Client/server duplicate tests publish signed announcements with newer, older, missing, and invalid sequence numbers to confirm replacement and duplicate suppression. Client-side duplicate delivery verifies subscribers only fire for meaningful updates and that new subscribers receive the latest backlog.

The system test starts a central Tub and introducer service, creates six clients, publishes storage announcements from five of them, subscribes all clients to storage, and polls until connection and delivery settle. It then checks debug counters, web status rendering, nickname and server ID display, introducer Tub restart behavior, and full introducer service restart behavior. The queue test publishes while the introducer is offline, restarts it, and waits for queued delivery.

Announcement cache tests create a client, inject signed announcements through `got_announcements`, flush eventual work, inspect `private/introducer_default_cache.yaml`, verify replacement by key and addition of a second key, then load the cache into a fresh `IntroducerClient` and a fresh `Client` storage broker. The signature tests validate the `sign_to_foolscap`/`unsign_from_foolscap` tuple contract and ensure invalid signatures are not delivered to subscribers.

## State And Persistence
This file exercises real filesystem state heavily: node basedirs, `private/introducer.furl`, legacy public `introducer.furl`, `tahoe.cfg`, `private/introducers.yaml`, `private/introducer_default_cache.yaml`, and `announcement-seqnum`. Runtime state includes introducer announcement tables, subscriber lists, debug counters, outstanding message queues, cached announcements, reconnectors, and Foolscap Tub registrations.

## Dependencies And Integration Points
The tests integrate with Twisted services, Foolscap Tub registration and reconnect behavior, Ed25519 signing, Tahoe introducer client/server common functions, Tahoe client creation, YAML utilities, node config loading, web introducer status rendering, and poll/eventual queue helpers. They are a central compatibility suite for storage server discovery.

## Risks And Edge Cases
Many assertions rely on private debug counters, exact event queue settling, and precise sequence-number semantics. The reconnect tests can be timing-sensitive because they use real Foolscap services and polling. `ClientSeqnums` inherits from `AsyncBrokenTestCase`, marking the sequence-number persistence path as known broken or quarantined. Tests for legacy FURL migration and deprecated paths are compatibility-sensitive and should be preserved during config refactors.

## Test Signals
Passing tests signal that signed v2 announcements are deduplicated, replay-protected, persisted to cache, rendered in the web UI, and redistributed correctly across reconnects/restarts. They also show malformed signatures are dropped, unsupported server versions surface `InsufficientVersionError`, and legacy introducer files are migrated safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_introducer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_iputil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_iputil.py

## Purpose
This file tests Tahoe networking utility behavior around selecting unused Foolscap Tub listen ports, resource-tracker garbage collection, and synchronous local IPv4 address discovery.

## Important APIs, Types, And Helpers
- `retry(stop)` and `stop_after_attempt(limit)` wrap flaky port-allocation tests with bounded retry.
- `ListenOnUsed.create_tub` creates and starts a Foolscap `Tub`.
- `ListenOnUsed` covers `iputil.listenOnUnused`.
- `GcUtil` covers `gcutil._ResourceTracker`.
- `GetLocalAddressesSyncTests` covers `get_local_addresses_sync`.

## Control Flow
The random-port test creates a Tub with no listeners, calls `listenOnUnused`, verifies a socket can connect to the selected loopback port, and confirms a second Tub receives a different port. The specific-port test binds an ephemeral socket to discover a free port, closes it, then asserts `listenOnUnused` uses that exact port. The GC tests monkey-patch `gc.collect` and count collection calls after allocations/releases. The address test uses testtools matchers to assert the returned collection is a list of native strings parseable by `socket.inet_pton(AF_INET, ...)`.

## State And Persistence
The tests create temporary Tub certificate files under named basedirs and open local sockets. Resource-tracker state is in-memory allocation/release counters. No durable Tahoe configuration is written.

## Dependencies And Integration Points
The file integrates with Foolscap Tub listening, Python sockets, Tahoe `iputil`, Tahoe `gcutil`, Twisted Trial cleanup, and testtools matchers. It indirectly protects node startup and introducer tests that use `listenOnUnused`.

## Risks And Edge Cases
Port selection is inherently race-prone, so the retry decorator reduces flakiness. The current `stop_after_attempt` predicate name is slightly counterintuitive because it returns `counter < limit` after an exception; behavior should be reviewed before reuse. Local address discovery depends on host networking and may vary in constrained environments.

## Test Signals
Passing tests show Tahoe can allocate usable listen ports, avoid immediate port reuse collisions in the test scenario, throttle GC after many descriptor allocations, delay GC after releases, and return parseable IPv4 local addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_iputil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_istorageserver.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_istorageserver.py

## Purpose
This file is a protocol-contract suite for `IStorageServer`, which is actually the storage client interface. The same shared, immutable, and mutable API tests are applied to both Foolscap and HTTP storage-client implementations so protocol migrations preserve storage semantics.

## Important APIs, Types, And Helpers
- `new_storage_index`, `new_secret`, and `_randbytes` generate deterministic random test inputs from a seeded `Random`.
- `IStorageServerSharedAPIsTestsMixin` validates `get_version`.
- `IStorageServerImmutableAPIsTestsMixin` validates `allocate_buckets`, bucket writer/reader calls, abort/disconnect cleanup, immutable corrupt-share advice, and immutable leases.
- `IStorageServerMutableAPIsTestsMixin` validates `slot_testv_and_readv_and_writev` (STARAW), `slot_readv`, mutable corrupt-share advice, and mutable leases.
- `_SharedMixin` sets up a real system test node, locates the backing `StorageServer`, replaces its clock with a `Clock`, and obtains the connected `IStorageServer` client.
- `Foolscap*Tests` and `HTTP*Tests` classes apply the mixins with `FORCE_FOOLSCAP_FOR_STORAGE` true or false.

## Control Flow
The shared version test asserts an expected storage protocol key is present. Immutable tests allocate new buckets, repeat allocations, write shares fully or partially, read completed buckets, validate overlapping writes, abort or disconnect mid-upload and then rewrite, read at varied offsets including out-of-bounds ranges, advise corrupt shares, and assert leases are created, renewed, or added. Foolscap has an extra disconnect test because disconnect cleanup is meaningful for that protocol and not for HTTP.

Mutable tests exercise STARAW as Tahoe's read/test/write operation. They confirm writes are readable, reads in a combined operation see pre-write data, tests gate writes atomically, tests and reads past the end truncate to available data, incorrect write-enabler secrets fail, zero new length deletes a share, `slot_readv` can read selected or all shares and returns empty for unknown storage indexes, corrupt-share advice is tolerated, and mutable leases are created/renewed/added.

## State And Persistence
The setup creates actual Tahoe client/server services and persistent storage server state in test basedirs. Share data, slots, and leases are stored by the backing `StorageServer`. Time-sensitive lease assertions use a fake clock installed into `self.server._clock`, so expiration deltas are deterministic.

## Dependencies And Integration Points
This suite ties together `allmydata.interfaces.IStorageServer`, `allmydata.storage.server.StorageServer`, Foolscap remote bucket objects, HTTP storage clients, `SystemTestMixin`, Twisted Deferreds, and Tahoe lease bookkeeping. It is one of the key regression suites for compatibility between Foolscap and HTTP storage protocols.

## Risks And Edge Cases
Because both protocols inherit the same mixins, a semantic divergence should appear as a protocol-specific failure. The tests use Foolscap-style `callRemote` even for bucket abstractions, so adapters must preserve that surface. Assertions expect `RemoteException` for protocol-level failures, which may hide more precise local exceptions. The random generator is module-global and seeded, so order-dependent additions could change generated values unless tests remain independent by storage index.

## Test Signals
Passing tests demonstrate that both storage protocols expose equivalent client semantics for immutable allocation/read/write/lease operations and mutable STARAW/readv/lease operations. The suite is also a signal that in-progress immutable shares are cleaned up correctly after aborts or Foolscap disconnections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_istorageserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_json_metadata.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_json_metadata.py

## Purpose
This file tests `allmydata.web.common.get_filenode_metadata` for immutable, SDMF, and MDMF filenodes with respect to the `size` metadata field.

## Important APIs, Types, And Helpers
- `MockFileNode` implements `get_size`, `is_mutable`, and `get_version`.
- `CommonFixture` defines shared size tests reused by all file-node variants.
- `Test_GetFileNodeMetaData_Immutable`, `Test_GetFileNodeMetaData_SDMF`, and `Test_GetFileNodeMetaData_MDMF` set `self.mutable_version` to `None`, `SDMF_VERSION`, or `MDMF_VERSION`.

## Control Flow
Each concrete class inherits the common fixture. The tests construct a mock filenode with size `0`, `1000`, or `None`, call `get_filenode_metadata`, and assert `size` is included for numeric values and omitted when `get_size` returns `None`.

## State And Persistence
All state is in-memory mock object state. There is no filesystem, network, or persistent Tahoe configuration.

## Dependencies And Integration Points
The test integrates with web JSON metadata generation for directory/file status responses and mutable version constants. It indirectly guards API clients that interpret file metadata from Tahoe web responses.

## Risks And Edge Cases
The fixture only validates the `size` field, not other metadata such as mutability or version fields. `MockFileNode.get_version` raises `AttributeError` for immutable nodes, matching one expected production behavior but not all possible filenode implementations.

## Test Signals
Passing tests show that `0` is treated as a real size, larger values are preserved, and unknown sizes are omitted consistently across immutable, SDMF, and MDMF nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_json_metadata.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_log.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_log.py

## Purpose
This file tests Tahoe's logging utilities, especially `tahoe_log.err` and `PrefixingLogMixin`. It validates error logging integration with Trial and formatting/parenting behavior for prefixed log messages.

## Important APIs, Types, And Helpers
- `SampleError` is a local exception for error logging.
- `Log.setUp` patches `foolscap.logging.log.msg` to capture messages, facilities, parent IDs, positional args, and keyword args.
- `tahoe_log.err` is tested with a `twisted.python.failure.Failure`.
- Several local classes inherit `tahoe_log.PrefixingLogMixin` to exercise constructor options.

## Control Flow
`test_err` raises and captures a `SampleError`, passes it to Tahoe's error logger, and flushes Trial logged errors to confirm the error was reported. The mixin tests create objects with default facilities, string or bytes prefixes, no prefix, multiple instances, grandparent IDs, and explicit parent IDs. They call `.log` and inspect captured Foolscap log messages for exact rendered text and parent-message propagation.

## State And Persistence
State is in-memory captured messages and per-class counters inside `PrefixingLogMixin`. No persistent logs are written because Foolscap logging is patched.

## Dependencies And Integration Points
The tests connect Tahoe log utilities to Foolscap's logging API and Twisted Trial's logged-error handling. They guard log message shapes used by diagnostics and parent-child log correlation.

## Risks And Edge Cases
Exact string formatting assertions are brittle if log presentation changes. The parent ID behavior is documented in the test as "pretty bogus", but it is intentionally frozen. Counter tests assume class-local numbering starts from one for the local class within a test.

## Test Signals
Passing tests show operational error logging surfaces to Trial, default and override facilities are honored, string/bytes prefixes render consistently, parent IDs cascade as implemented, and keyword argument keys are native strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_log.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_monitor.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_monitor.py

## Purpose
This file tests the small `Monitor` control object used by long-running Tahoe operations to track cancellation, status, completion, and completion Deferreds.

## Important APIs, Types, And Helpers
- `Monitor` provides `is_cancelled`, `raise_if_cancelled`, `cancel`, `get_status`, `set_status`, `is_finished`, `when_done`, and `finish`.
- `OperationCancelledError` is the exception raised after cancellation.
- `MonitorTests` contains the direct unit tests.

## Control Flow
`test_cancellation` asserts the initial non-cancelled state, calls `raise_if_cancelled`, cancels the monitor, and then expects `OperationCancelledError`. `test_status` sets and retrieves an arbitrary status string. `test_finish` obtains a Deferred from `when_done`, verifies it is unresolved, calls `finish(300)`, checks the return value, status, and finished flag, and then verifies the Deferred fires with `300`.

## State And Persistence
All state is internal to a `Monitor` instance: cancelled flag, status value, finished flag, and completion Deferred. There is no persistence.

## Dependencies And Integration Points
The monitor is used throughout Tahoe checking, repair, upload, and download workflows as a cancellation/status mechanism. This test ensures those workflows can rely on stable cancellation and completion semantics.

## Risks And Edge Cases
The tests do not cover multiple calls to `finish`, cancellation after finish, status mutation after finish, or multiple waiters from `when_done`. Those are potential edge cases for callers.

## Test Signals
Passing tests show the core monitor lifecycle works: cancel triggers the right exception, status is mutable, and finish both records status and resolves waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_monitor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_multi_introducers.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_multi_introducers.py

## Purpose
This file tests client configuration for multiple introducers, deprecated `tahoe.cfg` introducer FURLs, and `private/introducers.yaml` parsing. It ensures clients can run with multiple introducers, one non-default introducer, or no introducers.

## Important APIs, Types, And Helpers
- `MultiIntroTests` sets up a node config with storage disabled and a private `introducers.yaml`.
- `NoDefault` repeats a similar setup for non-default YAML scenarios.
- `write_node_config` creates baseline `tahoe.cfg` content.
- `create_client` is the system under test.
- `INTRODUCERS_CFG_FURLS`, `INTRODUCERS_CFG_FURLS_COMMENTED`, `SIMPLE_YAML`, and `EQUALS_YAML` provide fixture data, though not all constants are used.

## Control Flow
`test_introducer_count` writes YAML with two named introducers and asserts the client creates two introducer clients. `test_read_introducer_furl_from_tahoecfg` rewrites `tahoe.cfg` with deprecated `[client] introducer.furl`, creates a client, verifies the first introducer FURL, and flushes a deprecation warning. `test_reject_default_in_yaml` combines a deprecated tahoe.cfg FURL with a YAML `default` introducer and expects a `ValueError`.

`NoDefault` verifies a named YAML introducer works, the documented simple YAML shape works, the invalid historical `one: furl = furl1` shape raises `TypeError`, and an empty introducers map creates a client with zero introducer clients.

## State And Persistence
Each test writes a temporary node basedir, `tahoe.cfg`, `private/introducers.yaml`, and storage-disabled config. The resulting client contains `introducer_clients` populated from those files.

## Dependencies And Integration Points
The file integrates with Tahoe CLI/node config writer, YAML serializer/parser, client creation, deprecation warning handling, and the introducer-client construction path. It is a compatibility suite for migration from `tahoe.cfg` to `introducers.yaml`.

## Risks And Edge Cases
Some fixtures are unused, suggesting historical drift. The async `setUp` methods rely on Trial's support for coroutine setup. Exact deprecation and error strings are asserted. The invalid YAML test only checks `TypeError`, not the specific diagnostic quality.

## Test Signals
Passing tests show multiple named introducers are honored, deprecated single-FURL config remains supported with a warning, impossible default duplication is rejected, malformed historical YAML does not silently misconfigure the client, and introducerless clients are allowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_multi_introducers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_netstring.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_netstring.py

## Purpose
This file tests Tahoe's byte-oriented netstring encoder and splitter utility.

## Important APIs, Types, And Helpers
- `netstring(data)` encodes bytes as length-prefixed netstrings.
- `split_netstring(data, count, required_trailer=None)` parses a fixed number of netstrings and returns decoded byte strings plus the consumed offset.
- `Netstring` contains the direct unit tests.

## Control Flow
`test_encode` checks `b"abc"` encodes to `b"3:abc,"` and returns bytes. `test_split` parses two adjacent netstrings, checks byte output, validates exact count handling, optional empty trailer handling, extra-data behavior, successful required trailer matching, and failure on wrong count or wrong trailer. `test_extra` confirms unrequired trailing bytes are ignored after the expected number of netstrings. `test_nested` parses a netstring that itself contains netstrings and then parses the nested payload separately.

## State And Persistence
All state is local byte strings. No external resources are used.

## Dependencies And Integration Points
The utility is likely used in Tahoe serialization/framing code where strict byte output and trailer validation matter. This test provides low-level parser regression coverage.

## Risks And Edge Cases
The tests cover common composition and trailer cases but not malformed length fields, missing commas, non-digit lengths, negative values, or partial input. Those may be covered elsewhere or remain risk areas.

## Test Signals
Passing tests show netstring encoding is byte-stable, splitting respects count and trailer requirements, extra data can be intentionally ignored, and nested netstring payloads remain parseable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_netstring.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_no_network.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_no_network.py

## Purpose
This file smoke-tests the no-network grid harness used heavily by other Tahoe tests. It verifies that a `NoNetworkGrid` can start/stop and can perform a basic immutable upload/download round trip.

## Important APIs, Types, And Helpers
- `Harness.setUp` starts a parent `MultiService` and a `SameProcessStreamEndpointAssigner`.
- `Harness.grid` constructs `NoNetworkGrid` with one client, ten servers, no client config hooks, and the shared port assigner.
- `test_create` starts and stops the grid.
- `test_upload` uploads `Data` and downloads it through a node built from the returned URI.

## Control Flow
The create test constructs a grid, starts it directly, and returns `stopService`. The upload test attaches the grid to the parent service, gets client zero, uploads repeated byte data, creates a filenode from the resulting URI, downloads data with `download_to_data`, and asserts byte equality.

## State And Persistence
The grid creates temporary service state, storage server directories, and client/server objects under the test basedir. The port assigner state is scoped to the test and cleaned up.

## Dependencies And Integration Points
This file integrates with `NoNetworkGrid`, immutable upload `Data`, `download_to_data`, Twisted services, and the same-process endpoint assigner. Many other tests in this subset depend on this harness, so this file is a baseline health check.

## Risks And Edge Cases
Coverage is intentionally shallow: it does not test server failure simulation, share mutation helpers, multiple clients, mutable files, or cleanup details. It is a smoke test, not a full harness contract.

## Test Signals
Passing tests show the no-network grid can be constructed, start and stop cleanly, and support a minimal immutable upload/download path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_no_network.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_node.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_node.py

## Purpose
This file tests Tahoe node configuration, Tub location/listener setup, private config handling, privacy checks, invalid config rejection, and disabled-listener constraints for clients and introducers. It also covers default connection handler creation.

## Important APIs, Types, And Helpers
- `testing_tub` builds a main Tub from config text using I2P/Tor providers, connection handlers, tub options, and `create_main_tub`.
- `TestCase` covers location generation, config parsing, private config, config writes, timestamps, secret directory permissions, log-dir type, and `_Config.set_config`.
- `_stub_get_local_addresses_sync`, `_stub_allocate_tcp_port`, and `_stub_none` support `_tub_portlocation` tests.
- `TestMissingPorts` exercises `_tub_portlocation` edge cases.
- `FakeTub` and `Listeners` test `tub_listen_on`.
- `ClientNotListening` and `IntroducerNotListening` test disabled Tub constraints.
- `Configuration` tests invalid config rejection through `read_config` and `client.create_client`.
- `CreateDefaultConnectionHandlersTests` covers `create_default_connection_handlers`.

## Control Flow
Location tests create a node directory, force a usable test port unless one is supplied, optionally patch local addresses, build a test Tub, register a reference, and inspect the generated FURL for expected hints. Config tests write `tahoe.cfg` or private files, call `read_config`/`config_from_string`, and assert values, missing-entry exceptions, section enumeration behavior, unreadable private file failures, persistence of `set_config`, and unknown-config rejection.

`TestMissingPorts` focuses on `_tub_portlocation`: port zero requires assignment, `AUTO` expands with local addresses, defaults use allocated ports, disabled port/location pairs return `None`, empty values are errors, mismatched disabled values are errors, and TCP hints are rejected when `reveal-IP-address = false`. Listener tests ensure comma-separated Tub ports produce multiple `listenOn` calls and `listen:i2p`/`listen:tor` are delegated to provider endpoints.

Disabled-listener tests create real client/introducer configs with `tub.port = disabled` and `tub.location = disabled`. A non-storage client is allowed to have no listeners, but storage, helper, and introducer modes reject non-listening tubs. Invalid configuration tests ensure unknown sections fail both at read time and client creation.

## State And Persistence
The file creates many test basedirs, writes `tahoe.cfg`, private config files, secrets directories, and sometimes changes permissions. Config persistence is tested by writing then reloading `tahoe.cfg`. Runtime state includes fake and real Tubs, local endpoint assigner state, patched local-address functions, and connection handler maps.

## Dependencies And Integration Points
This is a central integration test for `allmydata.node`, `allmydata.client`, introducer creation, I2P/Tor provider factories, Foolscap Tub configuration, config validation, filesystem permissions, Hypothesis-generated port sets, and Twisted platform behavior. It protects both CLI-created node directories and programmatic node startup.

## Risks And Edge Cases
Several tests are skipped on Windows or when running as superuser because permission behavior differs. Location tests inspect generated FURL strings without binding real ports, so they validate formatting rather than connectivity. Privacy behavior is focused on TCP hints; other hint types depend on provider behavior. Exact error messages are asserted in multiple places.

## Test Signals
Passing tests show Tahoe can parse UTF-8 and hash-containing config safely, reject unescaped FURL hashes, manage private config files, protect secret directories, derive Tub ports/locations correctly, enforce no-IP-leak settings, delegate Tor/I2P listeners, reject invalid configs, and prevent storage/helper/introducer modes from running with no listening Tub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_node.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_observer.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_observer.py

## Purpose
This file tests observer-list utilities used for callback fanout and one-shot notification in Tahoe. It covers eager and lazy one-shot observers, reusable observer lists, reentrant mutation, error isolation, and `KeyboardInterrupt` propagation.

## Important APIs, Types, And Helpers
- `nextTurn` returns a Deferred that fires later via the reactor, allowing asynchronous observer notifications to settle.
- `observer.OneShotObserverList` stores waiters and fires once with a concrete result.
- `observer.LazyOneShotObserverList` stores a result factory and fires once.
- `observer.ObserverList` manages subscribe/unsubscribe and notify.

## Control Flow
One-shot tests register several waiters, fire the list, verify existing and later waiters receive the same result, inspect repr before/after firing, and ensure `fire_if_not_fired` ignores later results. Lazy one-shot follows the same pattern but passes a callable that produces the result.

Observer-list tests subscribe callbacks, notify with positional and keyword arguments, unsubscribe callbacks, wait a reactor turn, and assert each observer saw the right notifications. Reentrant behavior is tested by an observer unsubscribing itself during notification while a later observer still runs. Error isolation is tested by one observer raising a normal exception and a later observer still receiving notification; logged errors are flushed. `KeyboardInterrupt` is intentionally allowed to escape.

## State And Persistence
All state is in-memory lists of callbacks and observed values. Notifications are asynchronous enough to require reactor turns in some tests, but there is no persistence.

## Dependencies And Integration Points
The file integrates with Twisted Deferreds/reactor and Tahoe's observer utilities. These primitives can affect many asynchronous Tahoe workflows, so reentrancy and error isolation are important.

## Risks And Edge Cases
The tests do not cover unsubscribing absent callbacks, duplicate subscriptions, or lazy result factory exceptions. `nextTurn` uses a one-second delay, which is conservative and can slow the suite.

## Test Signals
Passing tests show one-shot observers are idempotent, late subscribers receive completed results, observer-list mutation during notification is safe, normal observer exceptions are logged and isolated, and process-interruption exceptions are not swallowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_observer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_openmetrics.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_openmetrics.py

## Purpose
This file tests the `/statistics?t=openmetrics` web endpoint for OpenMetrics-compatible output. It verifies HTTP status, content type, body decodability, parser compatibility, and presence/order of an expected Tahoe metric family.

## Important APIs, Types, And Helpers
- `FakeStatsProvider.get_stats` returns canned `stats` and `counters` data based on a real Tahoe JSON statistics response.
- `HackItResource` bridges `RequestTraversalAgent` and Tahoe's `MultiFormatResource` expectation that requests have a `fields` attribute.
- `OpenMetrics.test_spec_compliance` builds a local resource tree with `Statistics(FakeStatsProvider())`.
- `matches_stats`, `add_detail`, `readBodyText`, `has_header`, and `parses_as_openmetrics` build testtools matchers for the response.

## Control Flow
The test creates a `HackItResource`, mounts the statistics resource at the root, sends an in-memory GET request to `/?t=openmetrics` using `RequestTraversalAgent`, and asserts the Deferred succeeds with the composed matcher. The matcher checks HTTP 200, the exact OpenMetrics content type, UTF-8 body decoding, adds the body as test detail, parses the body through `prometheus_client.openmetrics.parser.text_string_to_metric_families`, and asserts the last family name is `tahoe_stats_storage_server_total_bucket_count`.

## State And Persistence
The stats data is a large in-memory dictionary containing latencies, disk values, CPU values, and counters. No network socket is opened and no persistent state is written.

## Dependencies And Integration Points
The file integrates Tahoe web status `Statistics`, Twisted Web resources, `treq.testing.RequestTraversalAgent`, Twisted response body reading, testtools matchers, and Prometheus/OpenMetrics parser behavior. It is the main compatibility guard for metrics exposition.

## Risks And Edge Cases
The final assertion that a specific metric family is last also encodes output grouping/sorting behavior, which may be stricter than the OpenMetrics specification alone. The fake stats include `None` percentile values, making the test useful for nil handling. It does not validate every emitted metric value or type.

## Test Signals
Passing tests show the statistics endpoint returns the exact OpenMetrics content type, emits parseable OpenMetrics text, handles realistic Tahoe stats input, and includes expected Tahoe storage metrics in deterministic order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_openmetrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_protocol_switch.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_protocol_switch.py

## Purpose
This file unit-tests a protocol-switch utility metaclass used to make Tahoe objects pretend to be Foolscap `Negotiation` instances for `isinstance` checks. Broader protocol-switch behavior is noted as covered by end-to-end Foolscap and HTTP storage tests.

## Important APIs, Types, And Helpers
- `_PretendToBeNegotiation` is the metaclass under test.
- `foolscap.negotiate.Negotiation` is the class being treated as compatible.
- `UtilityTests.test_metaclass` defines local `Parent`, `Child`, and `Other` classes to exercise `isinstance`.

## Control Flow
The test creates a class with `_PretendToBeNegotiation`, a subclass, and an unrelated class. It asserts normal instances still satisfy normal inheritance checks, a real `Negotiation()` instance is considered an instance of both `Parent` and `Child`, and unrelated objects are not considered instances.

## State And Persistence
All behavior is type/metaclass runtime state. There is no filesystem or network state.

## Dependencies And Integration Points
The utility exists at the boundary between Tahoe's protocol-switch code and Foolscap negotiation handling. The file points to `test_system.py` and `test_istorageserver.py` as broader integration coverage for real protocol behavior.

## Risks And Edge Cases
The test validates only `isinstance`, not `issubclass`, object construction, or any real negotiation flow. Because it deliberately changes type-check semantics, misuse could hide protocol object mismatches if broader integration tests are weak.

## Test Signals
Passing tests show the metaclass preserves ordinary subclass instance behavior while treating Foolscap `Negotiation` instances as compatible with Tahoe protocol-switch classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_protocol_switch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_repairer.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_repairer.py

## Purpose
This file tests immutable file checking, verification, and repair behavior in the no-network grid. It validates health judgments under many corruption modes, repair after share deletion, repair performance counters, server response reporting, and known limitations around repairing corrupted immutable shares.

## Important APIs, Types, And Helpers
- `RepairTestMixin` counts storage reads/allocates/writes, stashes counters, computes deltas, and uploads shared test data.
- Constants `READ_LEEWAY`, `MAX_DELTA_READS`, `WRITE_LEEWAY`, and `DELTA_WRITES_PER_SHARE` define performance-regression thresholds.
- `Verifier` tests `filenode.check(Monitor(), verify=...)`.
- `Repairer` tests `filenode.check_and_repair(Monitor(), verify=...)`.
- Judgment helpers (`judge_no_problem`, `judge_visible_corruption`, `judge_share_version_incompatibility`, `judge_invisible_corruption`) inspect `CheckResults`.

## Control Flow
`Verifier.test_check_without_verify` uploads data, checks health without verify, deletes all shares, and checks unhealthy status without causing storage reads. `_help_test_verify` sets up a two-client grid, uploads data, corrupts a specific share with a supplied corruptor, runs verify, enforces read-count budget, and applies a judgment function. The concrete verifier tests cover benign metadata corruptions, visible server-detected corruption, incompatible share version corruption, and many client-detected corruptions in offsets, share data, URI extension, and hash trees.

`Repairer.test_harness` validates the test harness itself by finding shares, deleting shares, expecting download and repair failure when too few shares remain, corrupting share files, and deleting all shares. `test_repair_from_deletion_of_1` and `test_repair_from_deletion_of_7` delete shares, run repair without full verify, assert pre/post `CheckResults` health, enforce read/allocate budgets, inspect the filesystem for restored share count, verify health, then delete additional shares and prove download still succeeds. `test_repairer_servers_of_happiness` removes seven servers and confirms repair tries to restore enough shares without requiring default happiness distribution. `test_tiny_reads` protects against inefficient tiny repair reads. `test_servers_responding` verifies post-repair results include servers that responded during repair even if not during pre-repair check.

## State And Persistence
The tests create no-network grid storage directories and real immutable share files. They delete and corrupt share files directly, remove servers from the grid, and inspect server stats counters. Runtime state includes `self.uri`, filenodes for two clients, counter snapshots, old share lists, and server IDs in check results.

## Dependencies And Integration Points
The file integrates with immutable upload/download, `Monitor`, `check_results`, no-network grid share helpers, storage server counters, Tahoe corruption helper functions, and `NotEnoughSharesError`. It is a high-value regression suite for checker/verifier/repairer behavior and performance.

## Risks And Edge Cases
The file contains an extensive disabled `OFF_test_repair_from_corruption_of_1` with comments documenting known repairer limitations: minimal verifier coverage, failures when download cannot switch shares, inability to delete corrupt immutable shares through `RIStorageServer`, and potential lost-progress issues. That disabled test is a major explicit coverage gap. Performance thresholds are leeway-based and may permit inefficient behavior while still catching extreme regressions.

## Test Signals
Passing tests show verifier health accounting distinguishes good, corrupt, incompatible, and missing shares; repair can restore deleted shares within bounded storage operations; repaired files remain downloadable after further degradation; server response lists are accurate; and repair avoids pathological tiny-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_repairer.py -->
