# Research Group: subset-b-007906

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_web.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_web.py

## Purpose

This file tests Tahoe-LAFS storage-server web/status behavior, especially the interaction between `StorageServer`, the bucket-counting crawler, the lease-checking/expiration crawler, and `allmydata.web.storage.StorageStatus`. It verifies both HTML and JSON status surfaces, crawler progress and persistence state, old crawler-state migration from pickle to JSON, corrupt-share reporting, disk-space reporting, and rendering helpers.

The tests are integration-heavy unit tests: they instantiate real `StorageServer` services in temporary storage directories, create immutable and mutable shares directly through storage-server APIs, manipulate lease timestamps, run Twisted services/crawlers, and render the web status resource or element.

## Important APIs, Types, and Helpers

`remove_tags`, `renderSynchronously`, `renderDeferred`, and `renderJSON` are local rendering helpers. They normalize rendered HTML for substring assertions and render `StorageStatusElement` through Twisted `flattenString`, or render `StorageStatus` with `t=json` through `.common_web.render`.

`MyBucketCountingCrawler` subclasses `BucketCountingCrawler` to fire test hook Deferreds from `finished_prefix`. `MyStorageServer.add_bucket_counter` installs this crawler so `test_bucket_counter_eta` can inspect ETA behavior at exact prefix-completion points.

`InstrumentedLeaseCheckingCrawler` subclasses `LeaseCheckingCrawler` to force controlled yielding after the first bucket. `No_ST_BLOCKS_LeaseCheckingCrawler.stat` returns an `os.stat`-like object with `st_blocks` removed to exercise disk-byte fallback behavior. `InstrumentedStorageServer` and `No_ST_BLOCKS_StorageServer` inject those crawler classes through `LeaseCheckerClass`.

`LeaseCrawler.make_shares` is the central fixture builder. It creates two immutable and two mutable shares using `StorageServer.allocate_buckets`, `StorageServer.slot_testv_and_readv_and_writev`, and `StorageServer.add_lease`, with one single-lease and one double-lease share of each mutability type. It records storage indexes, renew secrets, and cancel secrets for later lease manipulation.

`LeaseCrawler.backdate_lease` uses `ShareFile.renew_lease(..., allow_backdate=True)` to rewrite expiration times so age and cutoff-date expiration modes can be tested deterministically.

## Control Flow

`BucketCounter` starts a `service.MultiService` in `setUp` and attaches storage servers to it. `test_bucket_counter` forces the bucket crawler to yield after one prefix, checks the initial "not computed yet" HTML, waits through crawler progress with `fireEventually` and `PollMixin.poll`, then restores `cpu_slice` and verifies final bucket count and next-crawl text. `test_bucket_counter_cleanup` mutates bogus crawler state mid-cycle and verifies the end-of-cycle cleanup removes invalid buckets and samples. `test_bucket_counter_eta` uses hook Deferreds to render after successive prefixes and verify when ETA text becomes available.

`LeaseCrawler` follows a similar service lifecycle but exercises the lease checker. `test_basic` checks pre-cycle state, controlled in-cycle state after the first bucket, HTML progress predictions, completed history, recovered-space counters, lease counts, and JSON keys. The expiration tests then reuse `make_shares`, rewrite lease times, start the crawler, inspect in-cycle predictive HTML, and verify final share deletion or retention.

`test_expire_age` configures `expiration_mode="age"` and `expiration_override_lease_duration=2000`, backdates one lease per share, and expects only single-lease shares to be deleted while double-lease shares survive with one lease. `test_expire_cutoff_date` configures `expiration_mode="cutoff-date"` and verifies that `actual-*`, `original-*`, and `configured-*` recovery counters differ as expected for cutoff semantics. `test_only_immutable` and `test_only_mutable` use `expiration_sharetypes` to prove expiration is scoped by share type.

Other lease-crawler paths cover invalid expiration mode validation, history retention capped to ten cycles, inability to predict remaining recovery when progress is too early, disk-byte fallback without `st_blocks`, corrupt share detection in current and historical JSON/HTML, and migration of old pickle state/history files with the `admin migrate-crawler` command.

`WebStatus` verifies the web status page independent of crawler details. It covers no-server rendering, normal HTML/JSON stats, missing disk stats (`AttributeError`), failed disk stats (`OSError`), correct disk-stat arithmetic with reserved space, readonly storage, reserved-space rendering, and `StorageStatusElement` utility renderers.

## State and Persistence Behavior

The tests intentionally exercise persistent crawler state files under each storage directory. Bucket counting uses `bucket_counter.state`; lease checking uses `lease_checker.state` and `lease_checker.history`, with serializers `_LeaseStateSerializer` and `_HistorySerializer` validating post-migration JSON loads. The migration tests copy real historical pickle fixtures from `test/data`, invoke `migrate_crawler`, and assert that pickle files are replaced or accompanied by JSON-compatible state.

Storage state is on disk under `storage/.../shares`, including immutable share files, mutable share containers, empty buckets, non-share files, and corrupted share bytes. Lease state is persisted inside share files; tests mutate leases through share APIs and then assert post-crawl deletion, lease counts, and recovered byte counters.

Service state is Twisted-driven. Crawler timing is manipulated with `slow_start`, `cpu_slice`, `timer.reset(0)`, subclass hooks, and `fireEventually`, so many assertions depend on a crawler being mid-cycle or just finished.

## Dependencies and Integration Points

The file depends on Twisted Trial, Twisted services, `flattenString`, Foolscap `fireEventually`, Tahoe storage modules (`StorageServer`, `BucketCountingCrawler`, `LeaseCheckingCrawler`, serializers, storage-index path helpers), web storage rendering (`StorageStatus`, `StorageStatusElement`, `remove_prefix`), admin CLI option parsing and `migrate_crawler`, and test utilities (`fileutil`, `hashutil`, `base32`, `pollmixin`, `.common_web.render`).

It integrates storage internals with public operator-facing status pages. Assertions tie crawler state dictionaries to specific HTML phrases and JSON keys, so changes to `allmydata.web.storage` templates, crawler state schemas, serializer migration, share layout errors, or disk-stat handling will surface here.

## Risks and Edge Cases

These tests are timing-sensitive because they force background crawlers into specific progress windows. Changes to crawler scheduling, prefix ordering, progress estimation, or CPU-slice behavior may require updated synchronization. Some expected predictive counts rely on fixed storage-index positions in the crawler ring.

Several tests assert exact state dictionaries and rendered phrases, including large historical pickle-derived structures. Schema changes can cause noisy failures even when user-visible behavior is acceptable. The pickle migration tests are skipped on Windows because the fixture data is not portable there.

Disk-space assertions are platform-aware but still touch platform-dependent `st_blocks` behavior. The explicit no-`st_blocks` subclass covers fallback logic. Corruption tests intentionally log mutable/immutable container version errors and flush them afterward; new logging or error classes can affect Trial error handling.

## Test Signals

Strong signals include successful HTML and JSON rendering for storage status, crawler progress state transitioning from in-cycle to history, expiration deleting exactly the intended shares, lease counts matching single/double lease scenarios, migration of historical crawler pickle data to JSON serializers, and disk-stat failure modes producing safe availability values.

The file itself is test code. Relevant commands would be targeted Trial runs for `allmydata.test.test_storage_web.BucketCounter`, `LeaseCrawler`, and `WebStatus`, with attention to skipped Windows pickle cases and runtime-sensitive crawler polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_web.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_system.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_system.py

## Purpose

This file contains broad Tahoe-LAFS system/integration tests for a multi-node grid. It exercises upload/download, helper-assisted uploads, mutable files, directory nodes, web UI/API routes, command-line operations, checker APIs, connection loss detection, and both Foolscap and HTTP storage-protocol variants.

`SystemTest` inherits from `SystemTestMixin`, `RunBinTahoeMixin`, and Twisted Trial `TestCase`. The same core system tests run with `FORCE_FOOLSCAP_FOR_STORAGE=True`; `HTTPSystemTest` subclasses `SystemTest` with `FORCE_FOOLSCAP_FOR_STORAGE=False`. Likewise `Connections` and `HTTPConnections` cover server connection state under both protocols.

## Important APIs, Types, and Helpers

`RunBinTahoeMixin.run_bintahoe` launches `python -b -m allmydata.scripts.runner` in a subprocess with optional stdin, environment, and Python options via Twisted `getProcessOutputAndValue`. It normalizes signal failures into negative return codes.

`run_cli` wraps `.common_util.run_cli_unicode` with the older inline argument style used by these tests. `do_http` wraps `.common_web.do_http` and decodes response bytes as UTF-8 text.

`CountingDataUploadable` subclasses `upload.Data` to count requested bytes and fire `interrupt_after_d` after a threshold. The resumable-helper test uses it to bounce a helper connection mid-upload.

`_find_all_shares` walks client storage directories and returns `(client_num, storage_index, filename, shnum)` tuples for share files. `_corrupt_mutable_share` reads a `MutableShareFile`, unpacks it with `mutable.layout.unpack_share`, mutates selected fields, repacks, and writes it back. `flip_bit` and `mangle_uri` create corrupted keys/caps for negative download tests.

The HTTP helpers `PUT`, `GET`, `POST`, and `POST2` target `self.webish_url` or `self.helper_webish_url` and construct request bodies, including multipart form data.

`shouldFail` and `shouldFail2` centralize Deferred failure assertions for expected exception types and optional message substrings.

## Control Flow

`_test_upload_and_download` sets up a grid, forces `happy=5`, uploads 4000 bytes with either random-key or convergent encryption, uploads again, downloads through different clients, exercises partial reads, verifies corrupted-key and nonexistent-URI failures, then adds an extra node that uploads through a helper. It covers helper duplicate-upload avoidance for convergent encryption and helper upload interruption/resumption by bouncing client 0 after partial ciphertext fetch. It finally checks helper cleanup and storage stats counters.

`_test_mutable` runs for both SDMF and MDMF. It creates a mutable file, uses `tahoe debug dump-share --offsets` to inspect a share, downloads through cached and newly-created nodes, overwrites contents from different clients, performs an offset update through the async mutable-version API, corrupts SDMF shares in multiple fields while leaving enough shares intact, verifies retrieval, creates empty mutable files, and builds a recursive directory node manifest.

`test_filesystem` builds a small directory tree, bounces a client, verifies access through iterative and path APIs, creates a private directory with read-write and read-only links to another subdirectory, tests read-only mutation failures, moves children around, computes manifest/deep-stats, then calls `_test_web`, `_test_cli`, and `_test_checker`.

`_test_web` checks welcome pages, connection indicators, directory listing, file GET routes, URI-embedded downloads, bogus URI error status 410, PUT upload and replacement including a multi-segment file, unlinked POST uploads with and without helper, operation status pages, helper status HTML/JSON including old incoming/encoding temp files, non-helper helper-status behavior, and statistics HTML/JSON counters.

`_test_runner` finds a CHK share on disk and exercises debug CLI tools: `dump-share --offsets`, `find-shares`, and `catalog-shares`, checking share metadata, verifier cap output, and expected share counts.

`_test_cli` is an extensive inline CLI flow. It verifies `root_dir.cap` compatibility as the default `tahoe:` alias, alias creation/listing, `ls`, `mkdir`, `put` from files and stdin including SDMF format, `get` to stdout/files, `unlink`, `ls -l`, URI and readonly-URI listing, `mv`, `ln`, `cp` between Tahoe and local disk in both directions, overwrite behavior for immutable and mutable targets, recursive copy disk-to-Tahoe, Tahoe-to-disk, caps-only copy, and Tahoe-to-Tahoe recursive copy.

`test_filesystem_with_cli_in_subprocess` verifies a smaller CLI sequence through the actual runner subprocess, including `create-alias`, `put`, `mv` with bogus HTTP proxy environment variables, and `ls`. `_test_checker` validates check/verify behavior for mutable directory nodes, immutable CHK file nodes, and literal file nodes.

`Connections.test_rref` sets up two nodes, records a connected storage server reference, disowns the server service, closes idle HTTP connections, polls until the broker notices only one connected server, and verifies the disconnected server wrapper retains its storage-server object while `is_connected()` becomes false.

## State and Persistence Behavior

The tests create full node directories under `system/SystemTest/...`, including client configs, storage shares, helper working directories, aliases, private root caps, and local files used for CLI copy tests. They intentionally inspect and mutate on-disk share files to validate debug tools, corruption handling, and cleanup of partial uploads.

Upload state spans immutable ciphertext, helper temp directories (`CHK_encoding`, `CHK_incoming`), uploader/downloader/retrieve/publish/mapupdate histories, and stats providers. The helper-resumption scenario depends on partial upload state being cleaned from storage servers and, for convergent uploads, resumable helper state reducing second-upload work.

Mutable file state includes cached node identity, share maps, mutable version updates, sequence/root/hash/signature fields, readonly/writeable caps, and directory manifests/deep stats. CLI state includes aliases and `private/root_dir.cap`.

Connection state is held in storage brokers and remote server wrappers. The HTTP/Foolscap subclasses ensure storage transport selection changes without changing high-level test expectations.

## Dependencies and Integration Points

The file touches much of Tahoe-LAFS: `allmydata.uri`, immutable upload/download/offloaded helper code, mutable share files/layout/publish data, storage server share decoding, node APIs, directory/file interfaces, monitor/checker APIs, web status routes, CLI runner/debug commands, statistics/history providers, and common test system setup.

External libraries include Twisted Deferreds and process utilities, Foolscap errors and eventual scheduling, BeautifulSoup/html5lib for welcome-page inspection, and Python filesystem/process environment APIs.

`SystemTestMixin` is the major harness dependency, providing node setup, `clients`, `numclients`, helper URLs, `add_extra_node`, `bounce_client`, `poll`, `getdir`, and HTTP connection cleanup.

## Risks and Edge Cases

The tests are intentionally long-running and broad. `SystemTest.timeout` is 300 seconds and `test_filesystem.timeout` is 360 seconds, signaling CI slowness risk. Failures can arise from timing, helper reconnection, process environment, network endpoint cleanup, or platform filesystem differences.

The helper-resumption test mutates `offloaded.CHKCiphertextFetcher.CHUNK_SIZE` globally and notes this can affect later helper usage in the same test. Corruption scenarios depend on share counts and 3-of-10 encoding assumptions. Some assertions inspect exact CLI/debug textual output, making them sensitive to wording changes.

Several flows assume UTF-8 text bodies from web routes even when underlying HTTP helpers return bytes. The subprocess CLI test explicitly suppresses Python warnings and validates proxy environment isolation because HTTP proxy variables once affected CLI behavior.

`Connections.test_rref` relies on aggressive timeouts rather than immediate connection refusal because adopted listening file descriptors remain alive after service disowning. Transport-level behavior changes may affect polling duration.

## Test Signals

Passing this file is a strong end-to-end signal that Tahoe nodes can form a grid, upload/download immutable data, handle mutable SDMF/MDMF operations, maintain directory semantics, expose working web/CLI APIs, tolerate helper interruption, produce correct debug/status output, and detect disconnected storage peers under both Foolscap and HTTP storage protocols.

Targeted Trial selections are useful because the full file is expensive: `SystemTest.test_upload_and_download_random_key`, `SystemTest.test_upload_and_download_convergent`, `SystemTest.test_mutable_sdmf`, `SystemTest.test_mutable_mdmf`, `SystemTest.test_filesystem`, `SystemTest.test_filesystem_with_cli_in_subprocess`, `Connections.test_rref`, and their HTTP subclass variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_system.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_testing.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_testing.py

## Purpose

This file tests `allmydata.testing.web`, the verified fake WebAPI test infrastructure. It proves that `create_tahoe_treq_client` behaves enough like Tahoe's WebAPI for tests that need upload/download semantics without a real grid.

The scope is intentionally narrow: fake `PUT /uri` uploads produce CHK caps, repeated uploads are recognized, existing caps can be downloaded, missing caps return HTTP 410, and malformed download requests return HTTP 400.

## Important APIs, Types, and Helpers

`create_tahoe_treq_client` constructs the fake treq-style HTTP client under test. `capability_generator` produces plausible capabilities for missing-data tests. `allmydata.uri.from_string` and `CHKFileURI` validate returned caps.

`FakeWebTest` inherits from `.common.SyncTestCase`, not regular Trial async setup, because Hypothesis is used and the file explicitly avoids `setUp`. Each property-based test creates its own fake client.

The file uses Hypothesis `@given(content=binary())` for arbitrary byte content. Testtools matchers (`Equals`, `IsInstance`, `MatchesStructure`, `AfterPreprocessing`, `Contains`, `Always`) and `testtools.twistedsupport.succeeded` assert Deferred outcomes. `hyperlink.DecodedURL` builds query URLs, and Twisted `GONE` supplies the 410 status constant.

## Control Flow

`test_create_and_download` creates a fake client, uploads arbitrary bytes with `PUT http://example.com/uri`, checks status 201, parses the response body as a CHK cap, downloads through `/uri?uri=<cap>`, checks status 200, and verifies round-tripped content. The comment says the `/uri/<cap>` form is valid, but the implementation repeats the query-argument form.

`test_duplicate_upload` uploads the same arbitrary content twice. The first response must be 201 with a CHK cap body; the second must return 200, proving the fake tracks already-uploaded content/caps.

`test_download_missing` generates a CHK-looking cap that the fake has not stored, issues a GET with `?uri=...`, and asserts a succeeded response with status 410 and content containing `No data for`.

`test_download_no_arg` calls `/uri/` without a `uri` query argument and expects status 400.

## State and Persistence Behavior

All state is in-memory inside the fake treq client for the lifetime of each test. There is no filesystem persistence. The duplicate-upload test demonstrates that the fake maintains an upload map from content/capability to stored bytes. Hypothesis-generated cases are isolated because each test constructs a fresh client inside the test body.

## Dependencies and Integration Points

The file integrates testing helpers with Tahoe URI parsing and a treq-like response API (`code`, `content()`, `put`, `get`). Downstream tests that rely on `create_tahoe_treq_client` can use these guarantees when they need deterministic fake WebAPI behavior.

It depends on Twisted Deferreds through `inlineCallbacks`, testtools Deferred matchers, Hypothesis, hyperlink URL construction, and Tahoe URI classes.

## Risks and Edge Cases

The fake is deliberately smaller than the real WebAPI. These tests only cover CHK upload/download behavior and a couple of error statuses; they do not cover directory APIs, mutable caps, streaming semantics, headers, content types, authorization, or alternate `/uri/<cap>` path behavior despite the comment.

Because Hypothesis can generate empty and arbitrary binary content, the fake's content storage and cap generation are tested across byte edge cases. However, without a fixed example database or explicit settings in this file, runtime and shrinking behavior follow project/global Hypothesis configuration.

## Test Signals

Passing tests signal that fake WebAPI clients can be used for property tests needing simple upload/download and duplicate detection. The strongest behavioral checks are CHK cap parseability, byte-for-byte round trips for arbitrary bytes, 201-vs-200 duplicate semantics, and correct 410/400 error statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_testing.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_time_format.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_time_format.py

## Purpose

This file tests `allmydata.util.time_format`, covering UTC ISO formatting/parsing, duration/date parsing, stable struct-time formatting, Y2038-adjacent behavior, and human-readable delta formatting. It protects Tahoe code that displays crawler/operator times, parses lease durations or dates, and needs timezone-stable UTC conversions.

## Important APIs, Types, and Helpers

`TimeFormat` inherits from Twisted Trial `TestCase` and `.common_util.TimezoneMixin`. `TimezoneMixin` supplies `have_working_tzset` and `setTimezone` so timezone-sensitive behavior can be tested without permanently changing process state.

The tested APIs are `iso_utc_time_to_seconds`, `iso_utc`, `iso_utc_date`, `parse_duration`, `parse_date`, `format_time`, and `format_delta`.

`_help_test_epoch` is shared by default timezone and Europe/London timezone tests. It captures `time.tzname`, performs conversions, and asserts the original timezone name is restored.

## Control Flow

`test_epoch` and `test_epoch_in_London` verify that ISO UTC strings around the Unix epoch convert to absolute seconds regardless of local timezone oddities. The London test is conditional on working `time.tzset()` because Europe/London had a GMT+1 standard-time offset in 1970.

`_help_test_epoch` accepts `T`, underscore, and space separators, validates `iso_utc` output with underscore and custom separator, round-trips current time to whole seconds, accepts a callable `t=` provider, rejects incomplete ISO strings with `ValueError`, parses fractional seconds, and checks a 2009 daylight-savings-sensitive timestamp.

`test_iso_utc` checks date-only and full UTC formatting for a fixed fractional timestamp and a custom separator. `test_parse_duration` covers seconds, days, 31-day months, and 365-day years with whitespace/case/plural variations, plus invalid strings. `test_parse_date` checks YYYY-MM-DD parsing to UTC midnight seconds.

`test_format_time` validates formatting of `time.gmtime` results at epoch, minute/hour boundaries, and January 1, 2015 using manually computed leap-year days. `test_format_time_y2038` computes January 1, 2048, skips if the platform cannot represent it, and otherwise checks formatting. `test_format_delta` verifies positive deltas from seconds through multi-day spans, reverse-time `-`, and fractional start times truncating displayed whole seconds.

## State and Persistence Behavior

There is no file persistence. The only mutable state is process timezone environment/state managed through `TimezoneMixin` and `time.tzset` where available. The tests explicitly assert that timezone names are restored after helper execution.

## Dependencies and Integration Points

The file depends on Python `time`, Twisted Trial, Tahoe `TimezoneMixin`, and `allmydata.util.time_format`. These functions are integration points for lease expiration display, status pages, command-line date/duration parsing, and other operator-facing time formatting.

## Risks and Edge Cases

Timezone behavior is platform-dependent, so London epoch testing is skipped if `tzset` support is missing. Y2038/post-2037 behavior is also platform-dependent and skipped on systems whose `time.gmtime` cannot handle 2048.

Duration parsing encodes Tahoe-specific approximations: a month is 31 days and a year is 365 days. Changes to those semantics would require deliberate test updates. `format_delta` floors fractional start times in a way that is visible in expected strings.

## Test Signals

Passing tests signal that UTC parsing/formatting is independent of local timezone, fractional seconds are preserved where expected, date/duration parsers accept documented human forms and reject unitless/unknown units, and display formatting remains stable across boundary dates and negative deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_time_format.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_tor_provider.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_tor_provider.py

## Purpose

This file tests `allmydata.util.tor_provider`, including Tor control-port connection attempts, launching Tor through txtorcon, generating Tor onion node configuration from CLI options, runtime provider handler/listener creation, onion configuration validation, and service start/stop behavior for hidden services.

The tests use mocks rather than real Tor or txtorcon processes. They focus on endpoint descriptions, configuration output, private-key file handling, Twisted Deferred behavior, and graceful absence of optional Tor dependencies.

## Important APIs, Types, and Helpers

`mock_txtorcon` and `mock_tor` patch provider import helpers so tests can simulate installed or missing optional dependencies. `make_cli_config` builds `CreateNodeOptions` with a parent `runner.Options`, basedir, stdout, and parsed CLI flags such as `--listen=tor`, `--tor-launch`, `--tor-executable`, and `--tor-control-port`.

`FakeTor` mimics a txtorcon Tor instance by exposing a `.protocol`. `FakeConfig` is a dict-backed Tahoe config facade with `get_config` and `get_config_path`. `EmptyContext` supports `tor.add_context` usage in handler-launch tests.

Main test classes map to provider internals: `TryToConnect` for `_try_to_connect`, `LaunchTor` for `_launch_tor`, `ConnectToTor` for `_connect_to_tor`, `CreateOnion` for `create_config`, `Provider` for `_Provider.get_tor_handler` and control endpoint memoization, `ProviderListener` for `get_listener`, `Provider_CheckOnionConfig` for validation, and `Provider_Service` for Twisted service lifecycle.

## Control Flow

`TryToConnect` patches `clientFromString`, calls `_try_to_connect`, and verifies successful `txtorcon.build_tor_connection`, handled `ConnectError` returning `None` with a stdout message, and unhandled errors propagating without stdout output.

`LaunchTor` patches `allocate_tcp_port`, calls `_launch_tor`, and checks that a Tor result is returned for default and explicit executable paths. `ConnectToTor` simulates trying default control endpoints (`unix:/var/run/tor/control`, `tcp:127.0.0.1:9051`, `tcp:127.0.0.1:9151`) or a CLI-specified endpoint, returning the first reachable protocol or raising `ValueError` if none are reachable.

`CreateOnion` verifies `create_config`. Missing txtorcon fails with a user-facing install message. Launch mode calls `_launch_tor`, allocates a local TCP port, creates an `EphemeralHiddenService`, adds/removes it from Tor, writes the private key to `private/tor_onion.privkey`, and emits `[tor]` config plus tub ports/locations. Control-endpoint mode uses `_connect_to_tor` instead and writes equivalent onion config with `control.port`.

`Provider` verifies `tor_provider.create` and `get_tor_handler`. Disabled config, missing `tor`, and launch-without-txtorcon return no handler. Launch mode creates a Tor control endpoint maker through `tor.control_endpoint_maker`, lazily launches Tor only once in `_make_control_endpoint`, then reuses the endpoint description. Socks and control endpoint configs call `clientFromString` and appropriate `tor.socks_endpoint` or `tor.control_endpoint`; default config uses `tor.default_socks`.

`ProviderListener` checks that `onion.local_port` becomes a `TCP4ServerEndpoint` on `127.0.0.1`. `Provider_CheckOnionConfig` validates combinations of `onion`, txtorcon availability, `launch`, `control.port`, `onion.local_port`, `onion.external_port`, and `onion.private_key_file`.

`Provider_Service` verifies service lifecycle. With `onion=False`, `startService` does not start an onion and toggles `running`. Launch mode reads a private key file, launches Tor, creates an `EphemeralHiddenService`, adds it to the Tor protocol, stores `_onion_ehs` and `_onion_tor_control_proto`, and removes the onion on `stopService`. Control-endpoint mode connects with `txtorcon.connect` through `clientFromString`, starts the hidden service, and removes it on stop.

## State and Persistence Behavior

`create_config` and service tests write private-key files beneath temporary basedirs, especially `private/tor_onion.privkey` for generated config and arbitrary `keyfile` paths for service startup. Runtime provider instances cache launch results for `_make_control_endpoint` so Tor is launched only once and endpoint descriptions are reused.

Provider service state includes Twisted `running`, `_onion_ehs`, and `_onion_tor_control_proto`. Onion hidden services are expected to be removed from Tor on stop. CLI config state is represented in `tor_config.node_config["tor"]`, `tor_config.tub_ports`, and `tor_config.tub_locations`.

## Dependencies and Integration Points

The tests integrate `allmydata.util.tor_provider` with Twisted endpoint parsing (`clientFromString`, `TCP4ServerEndpoint`), Twisted Deferreds, txtorcon APIs (`launch`, `connect`, `build_tor_connection`, `EphemeralHiddenService`, endpoint/handler factories), optional `tor` helper module APIs (`default_socks`, `socks_endpoint`, `control_endpoint`, `control_endpoint_maker`, `add_context`), Foolscap's eventual queue flushing, and Tahoe node-creation CLI parsing.

These are important startup/network integration points because Tor configuration affects tub ports, tub locations, onion key persistence, and client endpoint handlers.

## Risks and Edge Cases

The tests do not start real Tor, so they validate provider orchestration and API calls but not actual network behavior or txtorcon compatibility beyond mocked call shapes. Mocked objects sometimes use class objects rather than instances, so the tests emphasize identity/call arguments.

Configuration values in `FakeConfig` can be booleans, strings, or ints; production config parsing may normalize differently. Error-message assertions are exact and will fail on wording changes. Endpoint defaults and order are part of the contract in `_connect_to_tor`.

The launch-handler test relies on `flushEventualQueue` to allow lazy launch work to complete and verifies launch memoization. Changes to scheduling or context-manager behavior in tor integration may need updated synchronization.

## Test Signals

Passing tests signal that Tahoe can construct Tor client handlers and onion listeners from config, produce correct Tor-related node config during `create-node`, handle missing optional dependencies with clear errors or disabled behavior, cache lazy Tor launches, and cleanly add/remove onion services during service lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_tor_provider.py -->
