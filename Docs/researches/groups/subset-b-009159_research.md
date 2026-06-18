# subset-b-009159 Research

Grouped source-tree-aligned research for restic backend files.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/http_transport.go -->
# sources/sync-backup/restic/internal/backend/http_transport.go

## Purpose
Builds the standard HTTP transport used by HTTP-like backends, including TLS roots, client certificates, unix-socket transport support, HTTP/2 tuning, debug wrapping, user-agent injection, and optional stuck-request watchdog behavior.

## Important APIs, Types, And Functions
TransportOptions, readPEMCertKey, and Transport are the important API surface. Transport returns an http.RoundTripper configured from options and feature flags.

## Control Flow
Transport starts from net/http defaults, configures HTTP/2, registers unixtransport, applies TLS options, wraps with the custom user-agent round tripper, optionally wraps with a watchdog, then with debug.RoundTripper.

## State And Persistence Behavior
No repository state is persisted. It reads certificate files from disk and mutates tls.Config on the returned transport.

## Dependencies And Integration Points
Depends on crypto/tls/x509/pem, net/http, x/net/http2, peterbourgon/unixtransport, internal debug/errors/feature, and httpuseragent/watchdog helpers in package backend.

## Risks And Edge Cases
Bad PEM parsing, multiple private keys, empty root cert filenames, InsecureSkipVerify, and feature-flag-specific HTTP/2 timeout behavior are the main risks. Panics if http2 transport configuration unexpectedly fails.

## Test Signals
Covered indirectly by HTTP backend tests and specifically by user-agent tests; certificate parsing and watchdog paths rely mostly on integration coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/http_transport.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper.go -->
# sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper.go

## Purpose
Provides a small RoundTripper decorator that overwrites the User-Agent header for every outgoing HTTP request.

## Important APIs, Types, And Functions
httpUserAgentRoundTripper, newCustomUserAgentRoundTripper, and RoundTrip implement the decorator.

## Control Flow
RoundTrip clones the request with its context, sets User-Agent, and delegates to the wrapped RoundTripper.

## State And Persistence Behavior
No persistence. The only state is the configured userAgent string and wrapped transport reference.

## Dependencies And Integration Points
Depends only on net/http and is consumed by Transport when TransportOptions.HTTPUserAgent is non-empty.

## Risks And Edge Cases
If the wrapped transport is nil, RoundTrip will panic; callers construct it through Transport with a concrete base transport. Cloning avoids mutating shared request state.

## Test Signals
Directly tested by httpuseragent_roundtripper_test.go with an httptest server checking the header.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper_test.go -->
# sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper_test.go

## Purpose
Tests that the custom user-agent RoundTripper injects the configured User-Agent on outgoing requests.

## Important APIs, Types, And Functions
TestCustomUserAgentTransport is the only test.

## Control Flow
An httptest server validates the header, a client uses httpUserAgentRoundTripper, and the test asserts HTTP 200 response status.

## State And Persistence Behavior
No persistent state; uses an in-memory test server and closes response bodies.

## Dependencies And Integration Points
Depends on net/http, net/http/httptest, testing, and package-local round tripper type.

## Risks And Edge Cases
The test validates header setting but not request cloning or nil wrapped transport behavior.

## Test Signals
Provides focused unit coverage for custom user-agent injection used by HTTP transports.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout.go -->
# sources/sync-backup/restic/internal/backend/layout/layout.go

## Purpose
Defines the storage layout abstraction used by backends to map restic handles to concrete file/object paths.

## Important APIs, Types, And Functions
Layout interface exposes Filename, Dirname, Basedir, Paths, and Name.

## Control Flow
No control flow beyond interface definition; implementations supply path mapping for local/SFTP/S3/Swift and REST.

## State And Persistence Behavior
No state or persistence in this file; implementations encode layout state such as repository prefix or base URL.

## Dependencies And Integration Points
Depends on internal/backend for Handle and FileType types.

## Risks And Edge Cases
Any layout implementation must keep Filename, Dirname, and Basedir consistent or listing/deletion will miss objects.

## Test Signals
Exercised by layout tests and by backend suite tests that create, list, and remove files.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_default.go -->
# sources/sync-backup/restic/internal/backend/layout/layout_default.go

## Purpose
Implements the default on-disk/object layout: config at repository root, pack files under data/xx/name, and metadata under snapshots, index, locks, and keys.

## Important APIs, Types, And Functions
DefaultLayout, NewDefaultLayout, String, Name, Dirname, Filename, Paths, and Basedir form the API.

## Control Flow
Dirname selects the file-type base path and adds the first two pack-name characters as a data subdirectory; Filename special-cases config; Paths enumerates base dirs plus all 256 data subdirs.

## State And Persistence Behavior
Stores only layout configuration: base path and join function. Persistence is external through backends that use returned paths.

## Dependencies And Integration Points
Depends on encoding/hex and internal/backend. Consumers include local, sftp, s3, swift, and layout tests.

## Risks And Edge Cases
Short pack names bypass subdir insertion; callers must provide valid handles. Map iteration order in Paths is not stable, so tests sort before comparing.

## Test Signals
Covered by layout/layout_test.go plus backend fixture layout tests for local and sftp.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_rest.go -->
# sources/sync-backup/restic/internal/backend/layout/layout_rest.go

## Purpose
Implements REST protocol path layout, where data files are not sharded into two-character subdirectories.

## Important APIs, Types, And Functions
RESTLayout, NewRESTLayout, String, Name, Dirname, Filename, Paths, and Basedir are the API.

## Control Flow
Filename and Dirname join the base URL with type directories; ConfigFile is special-cased to base/config and base directory. Basedir always reports no subdirectories.

## State And Persistence Behavior
Stores only a base URL string. REST server persistence is handled by HTTP requests in the rest backend.

## Dependencies And Integration Points
Depends on path and internal/backend; consumed by internal/backend/rest and rclone via the REST backend.

## Risks And Edge Cases
URL concatenation assumes the supplied base URL has already had trailing slash normalization by rest.Open.

## Test Signals
Covered by layout/layout_test.go and REST backend list/save/load tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_rest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_test.go -->
# sources/sync-backup/restic/internal/backend/layout/layout_test.go

## Purpose
Verifies DefaultLayout and RESTLayout path mapping, directory lists, Basedir behavior, and layout names.

## Important APIs, Types, And Functions
TestDefaultLayout and TestRESTLayout are the core tests with table-driven cases.

## Control Flow
The tests build layouts with filepath.Join or path.Join, compare filenames, sort Paths output where necessary, and validate pack subdirectory behavior.

## State And Persistence Behavior
No persistent state except temporary directories allocated by the test helper.

## Dependencies And Integration Points
Depends on filepath/path, reflect/sort/testing, internal/backend, and internal/test.

## Risks And Edge Cases
The tests focus on known file types and path expectations; invalid handle/file-type behavior remains a caller contract.

## Test Signals
Strong unit signal for source-tree path layout invariants used by several backends.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter.go -->
# sources/sync-backup/restic/internal/backend/limiter/limiter.go

## Purpose
Declares the bandwidth limiter interface shared by backend wrappers and HTTP transports.

## Important APIs, Types, And Functions
Limiter exposes Upstream, UpstreamWriter, Downstream, DownstreamWriter, and Transport.

## Control Flow
No implementation flow in this file; it defines how upload/download readers, writers, and RoundTrippers are wrapped.

## State And Persistence Behavior
No state. Implementations hold any token buckets or policy data.

## Dependencies And Integration Points
Depends on io and net/http. Used by limiter backends, static limiter, rclone stdio wrapping, and backend factories.

## Risks And Edge Cases
Implementations must preserve reader/writer semantics and close behavior; incorrect direction choice throttles the wrong traffic.

## Test Signals
Validated by static limiter and backend limiter tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend.go -->
# sources/sync-backup/restic/internal/backend/limiter/limiter_backend.go

## Purpose
Wraps a backend so Save uploads and Load downloads are rate-limited through a Limiter.

## Important APIs, Types, And Functions
WrapBackendConstructor, LimitBackend, rateLimitedBackend.Save/Load/Unwrap, limitedRewindReader, limitedReader, and newDownstreamLimitedReader are the key pieces.

## Control Flow
Save replaces the RewindReader Read path with limiter.Upstream while preserving Rewind/Length/Hash. Load wraps the callback reader in limiter.Downstream and preserves WriterTo by routing writes through DownstreamWriter.

## State And Persistence Behavior
No persistence; it decorates an existing backend and carries a Limiter reference.

## Dependencies And Integration Points
Depends on context/io, internal/backend, and limiter implementations. Integrated through location.NewLimitedBackendFactory and backend construction.

## Risks And Edge Cases
A subtle risk is losing io.WriterTo fast paths or RewindReader metadata; the wrapper explicitly preserves both but only when source reader implements WriterTo.

## Test Signals
TestLimitBackendSave and TestLimitBackendLoad verify byte integrity and WriterTo preservation paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend_test.go -->
# sources/sync-backup/restic/internal/backend/limiter/limiter_backend_test.go

## Purpose
Tests rate-limited backend wrapping for Save and Load without depending on timing-sensitive throughput assertions.

## Important APIs, Types, And Functions
TestLimitBackendSave, TestLimitBackendLoad, randomBytes, and tracedReadWriteToCloser are the main helpers.

## Control Flow
Mock backends consume or return data while wrappers apply a static limiter. Load tests vary whether inner/outer readers expose WriterTo to ensure optimized copy paths still work.

## State And Persistence Behavior
No persisted state; random test data is in memory.

## Dependencies And Integration Points
Depends on mock backend, backend.NewByteReader, crypto/rand, and internal/test assertions.

## Risks And Edge Cases
The tests validate correctness, not actual bandwidth rate. Timing behavior is covered in static limiter tests.

## Test Signals
Strong regression signal for decorator semantics and data integrity.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter.go -->
# sources/sync-backup/restic/internal/backend/limiter/static_limiter.go

## Purpose
Implements a fixed upload/download byte-rate limiter using x/time/rate token buckets.

## Important APIs, Types, And Functions
Limits, NewStaticLimiter, staticLimiter Upstream/Downstream methods, Transport, rateLimitedReader/Writer, consumeTokens, and toByteRate are the important APIs.

## Control Flow
NewStaticLimiter creates upload/download buckets when limits are positive. Reader and writer wrappers wait for tokens after each read/write. Transport wraps request bodies and response bodies in the correct directions.

## State And Persistence Behavior
State is in rate.Limiter buckets shared by all wrappers from the staticLimiter instance; there is no repository persistence.

## Dependencies And Integration Points
Depends on context, io, net/http, and x/time/rate. Used by backend and HTTP transport wrapping.

## Risks And Edge Cases
Shared buckets mean concurrent operations share total bandwidth. consumeTokens loops for chunks larger than bucket burst, so context-less waits use context.Background and cannot be canceled directly.

## Test Signals
static_limiter_test.go covers wrapping identity, read/write throttling, response body close propagation, nil body, and nil limiter cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter_test.go -->
# sources/sync-backup/restic/internal/backend/limiter/static_limiter_test.go

## Purpose
Tests static limiter wrappers for non-nil wrapping, actual read/write delay, HTTP body wrapping, close propagation, and corner cases.

## Important APIs, Types, And Functions
TestLimiterWrapping, TestReadLimiter, TestWriteLimiter, TestRoundTripperReader, TestRoundTripperCornerCases, and tracedReadCloser are key.

## Control Flow
Tests read/write known byte counts through low KB/s limits and assert elapsed time exceeds a minimum. RoundTripper tests inject response bodies and inspect wrapper behavior.

## State And Persistence Behavior
No persistent state; timing is wall-clock based and in-memory.

## Dependencies And Integration Points
Depends on bytes, io, net/http, testing, time, and package limiter.

## Risks And Edge Cases
Timing assertions can be noisy on overloaded hosts; tests choose coarse thresholds to reduce flakes.

## Test Signals
Provides direct unit coverage for limiter correctness and body close behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/static_limiter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config.go -->
# sources/sync-backup/restic/internal/backend/local/config.go

## Purpose
Parses and registers configuration for local filesystem repositories.

## Important APIs, Types, And Functions
Config, NewConfig, init option registration, and ParseConfig are the API.

## Control Flow
ParseConfig requires the local: prefix, strips it, and leaves the remaining path unchanged so platform-specific paths and colons are preserved.

## State And Persistence Behavior
Config stores Path and Connections only; no persistence happens here.

## Dependencies And Integration Points
Depends on strings, internal/errors, and internal/options. Used by location factory and local.Open/Create.

## Risks And Edge Cases
Invalid prefix is rejected; path normalization is intentionally not done, which preserves Windows paths but leaves validation to filesystem operations.

## Test Signals
config_test.go covers absolute, relative, colon-containing, and Windows-style paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config_test.go -->
# sources/sync-backup/restic/internal/backend/local/config_test.go

## Purpose
Table-tests local backend config parsing.

## Important APIs, Types, And Functions
configTests and TestParseConfig are the test surface.

## Control Flow
Each input is parsed and compared against expected Config with default Connections set to 2.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Uses backend/test.ParseConfigTester.

## Risks And Edge Cases
The tests do not cover invalid prefixes or empty paths.

## Test Signals
Good signal that ParseConfig preserves platform path syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/doc.go -->
# sources/sync-backup/restic/internal/backend/local/doc.go

## Purpose
Provides package documentation for the local backend.

## Important APIs, Types, And Functions
No API beyond the package declaration.

## Control Flow
No control flow.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
Integrated by Go documentation tooling.

## Risks And Edge Cases
No functional risk.

## Test Signals
No direct tests needed.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/layout_test.go -->
# sources/sync-backup/restic/internal/backend/local/layout_test.go

## Purpose
Validates that a fixture repository using the default layout can be opened by the local backend and lists expected pack files.

## Important APIs, Types, And Functions
TestLayout is the only test.

## Control Flow
The test extracts a tar fixture, opens the repo, lists PackFile handles, verifies expected IDs and no unexpected IDs, then closes and removes the repo.

## State And Persistence Behavior
Uses temporary filesystem state from test fixtures.

## Dependencies And Integration Points
Depends on local.Open, backend.PackFile, filepath, context, and internal/test fixture helpers.

## Risks And Edge Cases
Coverage is fixture-based and skips alternate layouts; failures often indicate path mapping or List regression.

## Test Signals
Strong integration signal for local layout compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/layout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local.go -->
# sources/sync-backup/restic/internal/backend/local/local.go

## Purpose
Implements the local filesystem backend for restic repositories.

## Important APIs, Types, And Functions
Local, NewFactory, open/Open/Create, Properties, Hasher, IsNotExist, IsPermanentError, Save, Load/openReader, Stat, Remove, List, Delete, Close, Warmup/WarmupWait, and traversal helpers are the important API.

## Control Flow
Create builds all layout directories after checking config absence. Save writes to a temp file, optionally preallocates, copies exact bytes, fsyncs file, closes, renames atomically, fsyncs directory, and makes the file read-only. Load delegates to util.DefaultLoad with offset/length validation in openReader. List walks base dirs or pack subdirs and feeds regular files to the callback.

## State And Persistence Behavior
Persists repository files on the local filesystem using DefaultLayout. Modes are derived from existing config or defaults; temp files are cleaned after errors.

## Dependencies And Integration Points
Depends on os/syscall/path/filepath/io, backend/layout/limiter/location/util, fs preallocation, backoff, and platform helpers in local_unix.go/local_windows.go.

## Risks And Edge Cases
Risks include filesystem-specific fsync/chmod behavior, partial temp files, ENOSPC/permanent error classification, short reads, and concurrent directory creation. Atomic replace is advertised as true due rename behavior.

## Test Signals
Covered by local tests, backend suite usage, layout fixture tests, and internal temp-file failure tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_internal_test.go -->
# sources/sync-backup/restic/internal/backend/local/local_internal_test.go

## Purpose
Tests local backend internal cleanup/error behavior around failed temp file saves.

## Important APIs, Types, And Functions
The tests override tempFile and exercise Save failure paths.

## Control Flow
Control flow creates a local backend, injects temp-file behavior, triggers Save errors, and asserts cleanup expectations.

## State And Persistence Behavior
Uses temporary filesystem state and restores package-level tempFile after testing.

## Dependencies And Integration Points
Depends on local package internals, backend.NewByteReader, context, and internal/test helpers.

## Risks And Edge Cases
Because it mutates a package variable, test isolation depends on restoring tempFile correctly.

## Test Signals
Provides regression coverage for partial-file cleanup paths that normal suite tests rarely hit.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_test.go -->
# sources/sync-backup/restic/internal/backend/local/local_test.go

## Purpose
Runs the generic backend suite against the local backend and tests permission behavior.

## Important APIs, Types, And Functions
newTestSuite, TestBackendLocal, BenchmarkBackendLocal, and permission-related tests are the main items.

## Control Flow
The suite creates a temporary repo, runs standard save/load/list/stat/remove/delete behavior, and benchmarks common operations.

## State And Persistence Behavior
Uses real temporary directories and local filesystem metadata.

## Dependencies And Integration Points
Depends on backend/test Suite, local.NewFactory, and internal/test helpers.

## Risks And Edge Cases
Tests are sensitive to filesystem permission semantics; chmod behavior can vary on non-POSIX or special mounts.

## Test Signals
Broad integration signal for backend contract compliance.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_unix.go -->
# sources/sync-backup/restic/internal/backend/local/local_unix.go

## Purpose
Provides Unix-specific helpers for directory fsync, macOS ENOTTY handling, read-only chmod, and file removal.

## Important APIs, Types, And Functions
fsyncDir, isMacENOTTY, setFileReadonly, and removeFile are the API used by local.go.

## Control Flow
fsyncDir opens and syncs a directory; setFileReadonly clears write bits; removeFile chmods write permission back before removing.

## State And Persistence Behavior
Mutates filesystem permissions and sync state; no repository metadata beyond file mode changes.

## Dependencies And Integration Points
Depends on os, runtime/syscall behavior, and internal/errors.

## Risks And Edge Cases
Risks are platform-specific syscall errors and filesystems that do not support directory fsync or chmod semantics.

## Test Signals
Covered indirectly by local backend tests and platform-specific CI.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_windows.go -->
# sources/sync-backup/restic/internal/backend/local/local_windows.go

## Purpose
Provides Windows-specific local backend helpers.

## Important APIs, Types, And Functions
fsyncDir, isMacENOTTY, setFileReadonly, and removeFile match the Unix helper API.

## Control Flow
Directory fsync is a no-op; setFileReadonly clears owner write bit; removeFile chmods writable then removes.

## State And Persistence Behavior
Mutates Windows-visible file mode bits through os.Chmod/remove.

## Dependencies And Integration Points
Depends on os and internal/errors.

## Risks And Edge Cases
Windows permission semantics differ from Unix; helper behavior is deliberately minimal.

## Test Signals
Covered indirectly by local backend tests on Windows CI.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/display_location_test.go -->
# sources/sync-backup/restic/internal/backend/location/display_location_test.go

## Purpose
Tests password stripping through the public registry/factory path rather than only package-local functions.

## Important APIs, Types, And Functions
TestStripPassword is the primary test.

## Control Flow
The test registers backend factories and checks displayed locations no longer include secrets.

## State And Persistence Behavior
No persisted state beyond an in-memory registry.

## Dependencies And Integration Points
Depends on location package, backend factories, and testing.

## Risks And Edge Cases
Coverage focuses on masking behavior and protects logging/display paths from leaking credentials.

## Test Signals
Complements location and backend-specific StripPassword tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/display_location_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location.go -->
# sources/sync-backup/restic/internal/backend/location/location.go

## Purpose
Parses repository location strings into scheme and config, with local-path fallback and password masking support.

## Important APIs, Types, And Functions
Location, NoPassword, Parse, StripPassword, extractScheme, and isPath are important.

## Control Flow
Parse extracts a scheme, looks it up in a Registry, and calls the factory parser; when no known scheme exists and the input looks like a path, it falls back to local: parsing. StripPassword delegates to the matched factory.

## State And Persistence Behavior
No persistence; returns parsed config objects and scheme metadata.

## Dependencies And Integration Points
Depends on strings, unicode helpers, internal/errors, and Registry/Factory from registry.go.

## Risks And Edge Cases
Ambiguous strings on Windows or with colons are sensitive; invalid schemes are rejected unless path fallback applies.

## Test Signals
location_test.go covers parse success, fallback, and invalid schemes; display_location_test.go covers masking.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location_test.go -->
# sources/sync-backup/restic/internal/backend/location/location_test.go

## Purpose
Tests repository location parsing and fallback behavior.

## Important APIs, Types, And Functions
testConfig, testFactory, TestParse, TestParseFallback, and TestInvalidScheme are key.

## Control Flow
The tests register a small synthetic factory, parse scheme-prefixed inputs, check local path fallback, and assert invalid schemes fail.

## State And Persistence Behavior
State is a temporary in-memory Registry.

## Dependencies And Integration Points
Depends on location package, backend/location factory constructors, and testing helpers.

## Risks And Edge Cases
The synthetic factory keeps tests focused on parser behavior rather than real backend configs.

## Test Signals
Good unit signal for user-facing repository location parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/registry.go -->
# sources/sync-backup/restic/internal/backend/location/registry.go

## Purpose
Defines the backend factory registry and generic factory adapters used to construct backends from parsed config.

## Important APIs, Types, And Functions
Registry, NewRegistry, Register, Lookup, Factory, genericBackendFactory, NewHTTPBackendFactory, and NewLimitedBackendFactory are the API.

## Control Flow
Factories parse config, strip passwords, and create/open backends. HTTP factories pass RoundTripper; limited factories pass Limiter. Generic adapters convert typed config/backend constructors to interface-based Factory methods.

## State And Persistence Behavior
Registry stores factory references in a map; no repository persistence.

## Dependencies And Integration Points
Depends on context, net/http, internal/backend, and internal/backend/limiter.

## Risks And Edge Cases
Type assertions in generic factory methods will panic if callers pass a config of the wrong concrete type; location.Parse and registry usage must stay paired.

## Test Signals
Covered indirectly by config tests, location tests, and all backend factory suite tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/logger/log.go -->
# sources/sync-backup/restic/internal/backend/logger/log.go

## Purpose
Provides a backend decorator that logs calls and forwards them to the wrapped backend.

## Important APIs, Types, And Functions
Backend, New, IsNotExist, Save, Remove, Load, Stat, List, Delete, Close, and Unwrap are relevant.

## Control Flow
Each method logs the operation through debug.Log and delegates to the embedded backend. Load logs the request and passes through the consumer callback.

## State And Persistence Behavior
No state beyond wrapped backend pointer. Persistence is entirely delegated.

## Dependencies And Integration Points
Depends on context, io, internal/backend, and internal/debug.

## Risks And Edge Cases
Logging must avoid altering behavior; Unwrap allows later layers to recover the original backend.

## Test Signals
Covered indirectly by backend wrapper usage; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/logger/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend.go -->
# sources/sync-backup/restic/internal/backend/mem/mem_backend.go

## Purpose
Implements an in-memory backend for tests and ephemeral repositories.

## Important APIs, Types, And Functions
MemoryBackend, NewFactory, New, Save, Load/openReader, Stat, Remove, List, Properties, Hasher, Delete, Close, Warmup/WarmupWait, and error helpers are important.

## Control Flow
Save normalizes metadata/config handles, rejects overwrite, reads all bytes, verifies length and xxhash content hash, then stores bytes in a mutex-protected map. Load/Stat/Remove/List copy map metadata under lock and honor context errors.

## State And Persistence Behavior
All repository state is held in a map[backend.Handle][]byte. NewFactory intentionally returns a persistent singleton for create/open calls.

## Dependencies And Integration Points
Depends on sync, bytes, xxhash, backend/location/util, debug/errors.

## Risks And Edge Cases
Because state is process-local, it is not durable and can grow unbounded in tests. Hash verification assumes RewindReader.Hash matches Hasher output.

## Test Signals
mem_backend_test.go runs the generic backend suite and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend_test.go -->
# sources/sync-backup/restic/internal/backend/mem/mem_backend_test.go

## Purpose
Runs the generic backend contract suite against the in-memory backend.

## Important APIs, Types, And Functions
newTestSuite, TestSuiteBackendMem, and BenchmarkSuiteBackendMem are the test entry points.

## Control Flow
The suite builds a mem factory and executes shared tests/benchmarks.

## State And Persistence Behavior
State is in-memory through MemoryBackend.NewFactory.

## Dependencies And Integration Points
Depends on backend/mem and backend/test Suite.

## Risks And Edge Cases
Does not test process restart durability, by design.

## Test Signals
Good signal that the memory backend satisfies the backend interface.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mock/backend.go -->
# sources/sync-backup/restic/internal/backend/mock/backend.go

## Purpose
Defines a callback-driven mock backend for unit tests of wrappers and retry/semaphore logic.

## Important APIs, Types, And Functions
Backend struct with function fields, NewBackend, and methods implementing backend.Backend are the API.

## Control Flow
Each method calls its configured function when set, otherwise returns a useful default such as nil Close, default Properties, or not-implemented errors for operations.

## State And Persistence Behavior
No persistence unless a test callback stores state.

## Dependencies And Integration Points
Depends on context, hash, io, internal/backend, and internal/errors.

## Risks And Edge Cases
Tests using it must set function fields needed by the code path; missing functions can hide behavior behind defaults.

## Test Signals
Used heavily by limiter, retry, and sema tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mock/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend.go -->
# sources/sync-backup/restic/internal/backend/rclone/backend.go

## Purpose
Implements the rclone backend by starting `rclone serve restic --stdio` and speaking REST over a single HTTP/2 stdio connection.

## Important APIs, Types, And Functions
rclone struct, NewFactory, run, wrapConn, newBackend, Open, Create, Close, and Properties are central.

## Control Flow
newBackend parses command strings, starts rclone with stdin/stdout pipes, wraps the stdio connection with optional limiter, builds an h2 Transport with a one-shot DialTLSContext, probes a random URL until the server responds, then Open/Create wrap it in the REST backend. Close closes idle h2 connections, waits briefly, then closes pipes if needed.

## State And Persistence Behavior
Repository state is remote through rclone. Local process state includes exec.Cmd, pipes, wait result, HTTP/2 transport, and goroutines reading stderr/waiting.

## Dependencies And Integration Points
Depends on os/exec, pipes, terminal foreground/background handling, HTTP/2, backend/rest, limiter, location, debug/errors/backoff.

## Risks And Edge Cases
Risks include subprocess lifecycle leaks, one-connection HTTP/2 assumptions, command shell splitting, startup timeout/error mapping, and stdio pipe shutdown races.

## Test Signals
backend_test.go and internal_test.go cover availability, failed start, and exit behavior; REST suite covers behavior once connected.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend_test.go -->
# sources/sync-backup/restic/internal/backend/rclone/backend_test.go

## Purpose
Runs backend suite tests against rclone when the rclone binary is available.

## Important APIs, Types, And Functions
TestBackendRclone and BenchmarkBackendRclone are the main entry points.

## Control Flow
The test locates rclone, builds a temporary local remote, and runs the shared backend suite/benchmarks.

## State And Persistence Behavior
Uses subprocesses and temporary filesystem state behind rclone.

## Dependencies And Integration Points
Depends on rclone.NewFactory, backend/test Suite, os/exec, and internal/test helpers.

## Risks And Edge Cases
Skipped when rclone is missing; failures can come from external rclone behavior rather than restic code only.

## Test Signals
Provides integration coverage for the stdio REST bridge.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config.go -->
# sources/sync-backup/restic/internal/backend/rclone/config.go

## Purpose
Parses and registers rclone backend configuration.

## Important APIs, Types, And Functions
Config, defaultConfig, NewConfig, init, and ParseConfig are the API.

## Control Flow
ParseConfig requires rclone:, strips the prefix, and stores the remaining remote while applying defaults for program, args, connections, and timeout.

## State And Persistence Behavior
No persistence; config controls later subprocess creation.

## Dependencies And Integration Points
Depends on strings, time, internal/errors/options.

## Risks And Edge Cases
Remote strings are not validated here; command/args splitting happens in backend.go and can fail later.

## Test Signals
config_test.go covers the canonical remote parse case.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config_test.go -->
# sources/sync-backup/restic/internal/backend/rclone/config_test.go

## Purpose
Tests rclone config parsing defaults.

## Important APIs, Types, And Functions
configTests and TestParseConfig are the test surface.

## Control Flow
A rclone: remote is parsed and compared with default program/args/connections/timeout values.

## State And Persistence Behavior
No persistent state.

## Dependencies And Integration Points
Depends on backend/test.ParseConfigTester.

## Risks And Edge Cases
Invalid config inputs are not covered in this file.

## Test Signals
Basic regression coverage for user-facing rclone repository syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/internal_test.go -->
# sources/sync-backup/restic/internal/backend/rclone/internal_test.go

## Purpose
Tests rclone subprocess failure and exit handling paths without running full backend suite.

## Important APIs, Types, And Functions
TestRcloneExit and TestRcloneFailedStart are key.

## Control Flow
The tests start commands that exit or fail and assert newBackend/Open reports useful errors and cleans up.

## State And Persistence Behavior
State is subprocess-local and temporary.

## Dependencies And Integration Points
Depends on package internals, context, exec-like behavior, and testing.

## Risks And Edge Cases
External shell/command behavior can vary by platform; tests target robust error propagation.

## Test Signals
Covers lifecycle paths that normal happy-path integration tests may miss.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/stdio_conn.go -->
# sources/sync-backup/restic/internal/backend/rclone/stdio_conn.go

## Purpose
Adapts rclone process stdin/stdout pipes to net.Conn for HTTP/2 transport use.

## Important APIs, Types, And Functions
StdioConn Read, Write, Close, CloseAll, LocalAddr, RemoteAddr, SetDeadline, SetReadDeadline, SetWriteDeadline, Addr, and interface assertion are important.

## Control Flow
Read delegates to receive pipe, Write to send pipe. Close closes send only; CloseAll closes both pipes and kills the command. Deadline methods are unsupported/no-ops with errors where appropriate.

## State And Persistence Behavior
Holds pipe and process references; no repository persistence.

## Dependencies And Integration Points
Depends on io, net, os, os/exec, time, and internal/errors.

## Risks And Edge Cases
HTTP/2 expects net.Conn semantics; missing deadline support can affect timeout behavior, so higher layers use client timeouts and process cleanup.

## Test Signals
Covered indirectly by rclone backend startup/close tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/stdio_conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/readerat.go -->
# sources/sync-backup/restic/internal/backend/readerat.go

## Purpose
Provides io.ReaderAt access over the backend Load API.

## Important APIs, Types, And Functions
backendReaderAt, ReaderAt, and ReadAt are the API.

## Control Flow
ReadAt logs the read, calls backend.Load for len(p) at offset, uses io.ReadFull in the consumer, and translates EOF/short read behavior into ReaderAt-compatible results.

## State And Persistence Behavior
No persistence; carries context/backend/handle for the lifetime of the reader.

## Dependencies And Integration Points
Depends on context, io, backend.Backend/Handle, debug, and errors.

## Risks And Edge Cases
The returned ReaderAt should not escape the caller because it embeds a context that may be canceled.

## Test Signals
Covered indirectly by backend load tests and code paths that require random access.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/readerat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config.go -->
# sources/sync-backup/restic/internal/backend/rest/config.go

## Purpose
Parses, masks, registers, and environment-augments REST backend configuration.

## Important APIs, Types, And Functions
Config, NewConfig, ParseConfig, StripPassword, prepareURL, ApplyEnvironment, and option registration are important.

## Control Flow
ParseConfig requires rest:, normalizes a trailing slash, and parses a URL. StripPassword parses the URL and replaces any password with ***. ApplyEnvironment fills username/password only when neither is present in the URL.

## State And Persistence Behavior
Config holds URL and connection count; no repository persistence.

## Dependencies And Integration Points
Depends on net/url, os, strings, internal/backend/errors/options.

## Risks And Edge Cases
Malformed URLs may be returned unchanged by StripPassword for logging safety. Environment credentials are ignored when any URL user info is already present.

## Test Signals
config_test.go covers URL normalization, unix URL syntax, and password stripping cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config_test.go -->
# sources/sync-backup/restic/internal/backend/rest/config_test.go

## Purpose
Tests REST config parsing and password masking.

## Important APIs, Types, And Functions
parseURL, configTests, TestParseConfig, passwordTests, and TestStripPassword are key.

## Control Flow
Inputs are parsed with default connections and compared; masking tests call the factory StripPassword path to ensure registry integration.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on net/url, backend/test, and rest factory functions.

## Risks And Edge Cases
Environment application is not covered in this file.

## Test Signals
Good regression signal for user-facing REST URLs and secret redaction.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest.go -->
# sources/sync-backup/restic/internal/backend/rest/rest.go

## Purpose
Implements the REST protocol backend over HTTP.

## Important APIs, Types, And Functions
Backend, restError, NewFactory, Open, Create, Save, Load/openReader, Stat, Remove, List/listv1/listv2, Delete, Close, Warmup/WarmupWait, and content type constants are central.

## Control Flow
Open normalizes layout URL and installs an http.Client. Create checks config absence then POSTs ?create=true. Save POSTs object bytes with ContentLength and rewindable GetBody. Load issues Range GETs and drains/EOF-checks bodies. List GETs a type directory and decodes v1 names with per-file HEADs or v2 name/size JSON.

## State And Persistence Behavior
Repository state is remote on a REST server. Local state is URL, connection count, client, and layout.

## Dependencies And Integration Points
Depends on net/http/url/json, backend/layout/location/util, debug/errors/feature, and the configured RoundTripper.

## Risks And Edge Cases
Risks include HTTP status classification, body drain requirements for connection reuse, rclone-specific 404 handling, range/content-length mismatch under BackendErrorRedesign, and retryability decisions.

## Test Signals
REST unit and integration tests cover list protocols, rest-server execution, unix sockets, and generic backend behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_int_test.go -->
# sources/sync-backup/restic/internal/backend/rest/rest_int_test.go

## Purpose
Integration-tests the REST backend against an external rest-server binary.

## Important APIs, Types, And Functions
runRESTServer and backend suite tests are the main logic.

## Control Flow
The helper starts rest-server, parses stderr for the listen address, runs shared backend tests/benchmarks, and cleans up via process cancellation/kill fallback.

## State And Persistence Behavior
Uses temporary directories, external process state, and HTTP network sockets.

## Dependencies And Integration Points
Depends on os/exec, net/url, regexp, syscall, backend/test Suite, and rest config.

## Risks And Edge Cases
Skipped when rest-server is unavailable; startup log parsing and process cleanup are platform-sensitive.

## Test Signals
Provides high-value integration coverage against the actual REST server protocol.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_int_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_test.go -->
# sources/sync-backup/restic/internal/backend/rest/rest_test.go

## Purpose
Unit-tests REST List behavior for API v1 and v2 response formats.

## Important APIs, Types, And Functions
TestListAPI is the key test.

## Control Flow
An httptest server returns JSON list data. v1 cases require subsequent HEAD requests for sizes; v2 includes sizes in one request. The test asserts returned FileInfo slices and request counts.

## State And Persistence Behavior
No persisted state beyond httptest server counters.

## Dependencies And Integration Points
Depends on net/http/httptest, backend/rest, reflect, strconv.

## Risks And Edge Cases
Does not exercise Save/Load; focused on list parsing and protocol negotiation.

## Test Signals
Strong regression signal for REST listing efficiency and compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_unix_test.go -->
# sources/sync-backup/restic/internal/backend/rest/rest_unix_test.go

## Purpose
Tests REST backend behavior over Unix-domain HTTP transport when supported.

## Important APIs, Types, And Functions
The file contains Unix-specific integration tests for http+unix repository URLs.

## Control Flow
It starts or connects to a REST server over a Unix socket and runs backend behavior through the normal REST client stack.

## State And Persistence Behavior
Uses temporary Unix socket/filesystem state.

## Dependencies And Integration Points
Depends on REST integration helpers, unix-capable transport support, and build tags/platform support.

## Risks And Edge Cases
Socket path length and platform support are the main risks; test is platform-specific.

## Test Signals
Covers unixtransport integration configured in http_transport.go.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry.go -->
# sources/sync-backup/restic/internal/backend/retry/backend_retry.go

## Purpose
Decorates a backend with retry, backoff, success/failure reporting, upload rewind, list de-duplication, and optional failed-load circuit breaking.

## Important APIs, Types, And Functions
Backend, New, retryNotifyErrorWithSuccess, retryAtLeastOnce, retry, Save, Load, Stat, Remove, List, Unwrap, Warmup, and WarmupWait are important.

## Control Flow
retry creates exponential backoff with feature-flag-dependent settings, reports retries/final errors, treats permanent backend errors specially, and guarantees at least one attempt. Save rewinds before each attempt and removes partial files on non-atomic backends. Load records non-permanent exhausted failures in a one-hour circuit breaker. List suppresses duplicate callbacks across retries.

## State And Persistence Behavior
State includes MaxElapsedTime, callbacks, wrapped backend, and failedLoads sync.Map. Repository persistence is delegated.

## Dependencies And Integration Points
Depends on cenkalti/backoff, internal/backend/debug/feature, context, sync, time.

## Risks And Edge Cases
Risks include incorrectly classifying permanent errors, duplicate list callbacks, deleting partial files on non-atomic backends, circuit breaker false positives, and canceled-context modification guarantees.

## Test Signals
backend_retry_test.go provides extensive targeted coverage; testing.go speeds retry timing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry_test.go -->
# sources/sync-backup/restic/internal/backend/retry/backend_retry_test.go

## Purpose
Extensively tests retry wrapper behavior for save, list, load, stat, remove, permanent errors, callbacks, and context cancellation.

## Important APIs, Types, And Functions
Tests include SaveRetry, SaveRetryAtomic, List retry/dedup/error paths, failing readers, permanent error handling, success reporting, and circuit breaker behavior.

## Control Flow
Mock backends inject transient/permanent errors and track calls while fastRetries shortens backoff. Tests assert data rewind, cleanup removal rules, callback precedence, and retry counts.

## State And Persistence Behavior
No repository persistence; state is mock callbacks, buffers, and retry wrapper maps.

## Dependencies And Integration Points
Depends on mock backend, backoff, internal/errors/restic/test, context, io, time.

## Risks And Edge Cases
Because it toggles package-level fastRetries and feature behavior, isolation is important. It targets control semantics rather than real backend I/O.

## Test Signals
This is the primary regression suite for retry correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/backend_retry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/testing.go -->
# sources/sync-backup/restic/internal/backend/retry/testing.go

## Purpose
Provides a test helper to enable fast retry timing.

## Important APIs, Types, And Functions
TestFastRetries sets the package-level fastRetries flag.

## Control Flow
Calling the helper makes retry backoff millisecond-scale for tests.

## State And Persistence Behavior
Mutates package global test state only.

## Dependencies And Integration Points
Depends on testing.

## Risks And Edge Cases
Global mutation can affect other retry tests in the same package, which is intentional for speed.

## Test Signals
Used by backend_retry_test.go.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/retry/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader.go -->
# sources/sync-backup/restic/internal/backend/rewind_reader.go

## Purpose
Defines rewindable readers used by Save so retry wrappers can replay uploads and backends can know length/hash.

## Important APIs, Types, And Functions
RewindReader, ByteReader, NewByteReader, FileReader, and NewFileReader are the API.

## Control Flow
ByteReader wraps bytes.Reader, precomputes optional hash, exposes Rewind/Length/Hash. FileReader wraps an io.ReadSeeker, records length from SeekEnd, rewinds to start, and returns a supplied hash.

## State And Persistence Behavior
State is reader position, byte buffer/file seeker, length, and hash. No repository persistence.

## Dependencies And Integration Points
Depends on bytes, hash, io, and internal/errors.

## Risks And Edge Cases
Hash may be nil when backend does not need content hash. FileReader requires seekable input and correct external hash.

## Test Signals
rewind_reader_test.go validates byte and file rewind/read semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader_test.go -->
# sources/sync-backup/restic/internal/backend/rewind_reader_test.go

## Purpose
Tests ByteReader and FileReader rewind, length, and content behavior.

## Important APIs, Types, And Functions
TestByteReader, TestFileReader, and testRewindReader are the main tests.

## Control Flow
The tests read data, rewind, reread, and compare expected bytes and lengths for in-memory and temp-file readers.

## State And Persistence Behavior
Uses temporary files for FileReader.

## Dependencies And Integration Points
Depends on backend readers, bytes/io/os, and testing helpers.

## Risks And Edge Cases
Hash behavior is lightly covered through construction rather than deep validation.

## Test Signals
Good unit signal for retry-safe upload readers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config.go -->
# sources/sync-backup/restic/internal/backend/s3/config.go

## Purpose
Parses and registers S3-compatible backend configuration and applies region environment defaults.

## Important APIs, Types, And Functions
Config, NewConfig, ParseConfig, createConfig, ApplyEnvironment, and option registration are key.

## Control Flow
ParseConfig supports s3:http(s) URL forms plus s3:// and s3: endpoint/bucket/prefix forms, cleans prefixes, and records HTTP usage. ApplyEnvironment fills Region from AWS_DEFAULT_REGION when unset.

## State And Persistence Behavior
Config stores endpoint, bucket, prefix, credentials/testing fields, storage class, restore settings, retry/listing options, and connection count.

## Dependencies And Integration Points
Depends on net/url, os, path, strings, time, internal/backend/errors/options.

## Risks And Edge Cases
Parsing assumes endpoint and bucket split semantics; empty endpoint is rejected while some bucket validation is deferred to S3 operations.

## Test Signals
config_test.go covers many URL forms and invalid endpoint cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config_test.go -->
# sources/sync-backup/restic/internal/backend/s3/config_test.go

## Purpose
Tests S3 config parsing defaults and invalid formats.

## Important APIs, Types, And Functions
newTestConfig, configTests, TestParseConfig, and TestParseError are key.

## Control Flow
Table cases verify endpoint, bucket, prefix, UseHTTP, connections, restore defaults, and cleaned prefixes.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend/test and strings/time.

## Risks And Edge Cases
Environment application and credential selection are not covered here.

## Test Signals
Good coverage for user-facing S3 repository syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/s3.go -->
# sources/sync-backup/restic/internal/backend/s3/s3.go

## Purpose
Implements the S3-compatible object storage backend using minio-go.

## Important APIs, Types, And Functions
s3 struct, NewFactory, open/getCredentials, Open/Create, IsNotExist/IsPermanentError, Properties, Save, Load/openReader, Stat, Remove, List, Delete, Warmup/requestRestore/getWarmupStatus/WarmupWait are central.

## Control Flow
open validates restore feature flag, configures MinIO client and credential chain. Create ensures bucket existence. Save PutObject writes exact bytes with optional storage class. Load uses ranged GetObject and optional length verification. List streams objects under layout prefixes. Warmup requests Glacier/Deep Archive restore and waits for restored status.

## State And Persistence Behavior
Repository state is persisted as S3 objects under bucket/prefix using DefaultLayout. Local state is client, config, and layout.

## Dependencies And Integration Points
Depends on minio-go, credentials providers, backend/layout/location/util, feature flags, backoff, http transport.

## Risks And Edge Cases
Risks include credential discovery latency/failure, anonymous-auth policy, bucket lookup style, archive class metadata availability, range truncation, list goroutine cancellation, and MinIO global MaxRetry mutation.

## Test Signals
s3_test.go covers MinIO/local and environment-backed integration; config tests cover parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/s3_test.go -->
# sources/sync-backup/restic/internal/backend/s3/s3_test.go

## Purpose
Integration-tests and benchmarks the S3 backend against MinIO or configured S3 credentials.

## Important APIs, Types, And Functions
runMinio, newMinioTestSuite, TestBackendMinio, BenchmarkBackendMinio, newS3TestSuite, TestBackendS3, and BenchmarkBackendS3 are key.

## Control Flow
Tests start a MinIO process when available, wait for TCP readiness, create randomized credentials/prefixes, and run the generic backend suite. Separate tests use RESTIC_TEST_S3_* environment variables for real S3.

## State And Persistence Behavior
Uses external processes, temporary directories, network sockets, and environment credentials.

## Dependencies And Integration Points
Depends on minio binary, backend/test Suite, location factory, options.SecretString, and internal/test.

## Risks And Edge Cases
Skipped without binaries/env vars; fixed port 9000 can conflict on shared hosts.

## Test Signals
Provides broad contract coverage for S3 persistence behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend.go -->
# sources/sync-backup/restic/internal/backend/sema/backend.go

## Purpose
Wraps a backend with connection-count limiting, parameter validation, and freeze/unfreeze coordination.

## Important APIs, Types, And Functions
NewBackend, connectionLimitedBackend, typeDependentLimit, Freeze, Unfreeze, Save, Load, Stat, Remove, and Unwrap are the API.

## Control Flow
Each operation validates handles/offset/length, skips limits for lock files, acquires a semaphore token, respects freezeLock, checks context cancellation, then delegates. Freeze blocks new non-lock operations after token acquisition.

## State And Persistence Behavior
State is semaphore tokens, freezeLock, and wrapped backend; persistence is delegated.

## Dependencies And Integration Points
Depends on context, io, sync, backoff, internal/backend/errors.

## Risks And Edge Cases
Lock-file bypass is intentional to keep lock refresh possible. Panic on invalid backend connection count happens during NewBackend.

## Test Signals
backend_test.go covers validation, concurrency limits, lock bypass, freeze behavior, and Unwrap.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend_test.go -->
# sources/sync-backup/restic/internal/backend/sema/backend_test.go

## Purpose
Tests connection-limiting backend validation, concurrency, lock-file exemptions, freeze/unfreeze, and unwrapping.

## Important APIs, Types, And Functions
Tests include parameter validation for Save/Load/Stat/Remove, concurrencyTester helpers, and freeze behavior.

## Control Flow
Mock backends block in callbacks while goroutines count how many operations enter concurrently. Tests compare against configured connection counts and lock-file unlimited behavior.

## State And Persistence Behavior
No persistence; synchronization state is in test goroutines/channels.

## Dependencies And Integration Points
Depends on mock backend, errgroup, atomics, context, and internal/test assertions.

## Risks And Edge Cases
Concurrency tests rely on small sleeps/polling but avoid precise timing for throughput.

## Test Signals
Strong signal for wrapper correctness under parallel access.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/semaphore.go -->
# sources/sync-backup/restic/internal/backend/sema/semaphore.go

## Purpose
Implements the small counting semaphore used by the connection-limited backend.

## Important APIs, Types, And Functions
semaphore type, newSemaphore, GetToken, and ReleaseToken are relevant.

## Control Flow
newSemaphore creates a buffered channel with capacity n and rejects zero. GetToken sends into the channel; ReleaseToken receives.

## State And Persistence Behavior
State is channel occupancy only.

## Dependencies And Integration Points
Depends on internal/errors for invalid count reporting.

## Risks And Edge Cases
Mispaired acquire/release can deadlock or panic; callers use defer to pair operations.

## Test Signals
Covered indirectly by sema backend tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/semaphore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config.go -->
# sources/sync-backup/restic/internal/backend/sftp/config.go

## Purpose
Parses and registers SFTP backend repository locations.

## Important APIs, Types, And Functions
Config, NewConfig, init, and ParseConfig are important.

## Control Flow
ParseConfig supports sftp://user@host[:port]/directory and sftp:user@host:directory forms, handles IPv6 URL form, splits user@domain@host, cleans paths, and rejects tilde-leading paths.

## State And Persistence Behavior
Config holds connection/subprocess parameters; no persistence here.

## Dependencies And Integration Points
Depends on net/url, path, strings, internal/errors/options.

## Risks And Edge Cases
Ambiguous colon/@ parsing is handled carefully; tilde rejection avoids server-dependent expansion surprises.

## Test Signals
config_test.go covers common, IPv6, absolute, relative, and invalid forms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/config_test.go

## Purpose
Tests SFTP config parsing and invalid URL forms.

## Important APIs, Types, And Functions
configTests, TestParseConfig, configTestsInvalid, and TestParseConfigInvalid are key.

## Control Flow
Table cases verify user, host, port, cleaned path, connection defaults, IPv6, and user names containing @.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend/test.ParseConfigTester.

## Risks And Edge Cases
Does not cover tilde rejection explicitly in the visible table.

## Test Signals
Good coverage for user-facing SFTP location syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/doc.go -->
# sources/sync-backup/restic/internal/backend/sftp/doc.go

## Purpose
Provides package documentation for the SFTP backend.

## Important APIs, Types, And Functions
No API beyond package declaration.

## Control Flow
No control flow.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
Used by Go documentation tooling.

## Risks And Edge Cases
No functional risk.

## Test Signals
No direct tests needed.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/layout_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/layout_test.go

## Purpose
Verifies SFTP can open a fixture repository using the default layout and list expected pack files.

## Important APIs, Types, And Functions
TestLayout is the only test.

## Control Flow
The test extracts a fixture, starts an sftp-server command, opens the repo, lists pack files, checks expected IDs, closes, and removes temp data.

## State And Persistence Behavior
Uses temporary filesystem state and external sftp-server process.

## Dependencies And Integration Points
Depends on sftp.Open, backend.PackFile, context, filepath, and internal/test fixtures.

## Risks And Edge Cases
Skipped when sftp-server is unavailable; process startup can be environment-sensitive.

## Test Signals
Integration signal for SFTP layout compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/layout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp.go -->
# sources/sync-backup/restic/internal/backend/sftp/sftp.go

## Purpose
Implements the SFTP backend over an ssh/sftp subprocess.

## Important APIs, Types, And Functions
SFTP, NewFactory, startClient, Open/Create/open, mkdirAllDataSubdirs/mkdirAll, buildSSHCommand, Save, Load/openReader, Stat, Remove, List, Close, Delete, Warmup/WarmupWait, and helper functions are central.

## Control Flow
startClient builds an ssh command, starts it, wires stdin/stdout to pkg/sftp, and detects posix-rename support. Create creates layout directories concurrently. Save writes a unique temp file, chmods, uses concurrent upload, validates length, closes, renames, then makes read-only. Load delegates to util.DefaultLoad and can detect too-short limited reads under BackendErrorRedesign. List walks the remote tree respecting layout subdir mode.

## State And Persistence Behavior
Repository state is remote filesystem data under DefaultLayout. Local state includes sftp client, subprocess, result channel, config, modes, and posixRename capability.

## Dependencies And Integration Points
Depends on pkg/sftp, os/exec, terminal, errgroup, backend/layout/limiter/location/util, feature flags, backoff, crypto/rand.

## Risks And Edge Cases
Risks include subprocess lifecycle, remote permission/mode support, non-atomic rename without posix extension, no-space detection via statvfs heuristics, and partial temp cleanup.

## Test Signals
sftp_test.go, sshcmd_test.go, layout tests, and generic suite cover command building, permissions, layout, and backend contract behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/sftp_test.go

## Purpose
Runs SFTP backend suite and permission-specific tests against an available sftp-server binary.

## Important APIs, Types, And Functions
findSFTPServerBinary, testConfig, newTestSuite, TestBackendSFTP, BenchmarkBackendSFTP, TestCreateSetsDirPermissions, and TestSaveSetsDirPermissions are key.

## Control Flow
Tests locate sftp-server, create temporary repos, run shared suite/benchmarks, and assert directory modes after Create and Save-created subdirectories.

## State And Persistence Behavior
Uses external subprocess and temporary filesystem state.

## Dependencies And Integration Points
Depends on backend/test Suite, sftp.NewFactory/Create, filepath/os/fs, and internal/test.

## Risks And Edge Cases
Skipped when sftp-server is missing; permission assertions assume POSIX-like behavior.

## Test Signals
Broad integration signal for SFTP backend behavior and permission handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sftp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sshcmd_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/sshcmd_test.go

## Purpose
Tests construction of ssh command/argument vectors for SFTP connections.

## Important APIs, Types, And Functions
sshcmdTests and TestBuildSSHCommand are central.

## Control Flow
Table cases cover user/host/port, extra args, custom command, IPv6, and error when command and args are both specified.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on reflect, testing, and buildSSHCommand.

## Risks And Edge Cases
Does not execute ssh; only validates deterministic argument construction.

## Test Signals
Protects command parsing and option composition used before starting the subprocess.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/sshcmd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split.go -->
# sources/sync-backup/restic/internal/backend/shell_split.go

## Purpose
Implements shell-like command string splitting for backend subprocess options.

## Important APIs, Types, And Functions
SplitShellStrings and its internal scanner/state logic are the API.

## Control Flow
The parser scans runes, handles whitespace separation, quotes, backslash escapes, and error cases for unterminated quotes or invalid escapes.

## State And Persistence Behavior
No persistent state; parsing state is local to a call.

## Dependencies And Integration Points
Depends on strings/unicode-style parsing and internal/errors.

## Risks And Edge Cases
Shell compatibility is intentionally limited; mismatches can affect sftp.command, sftp.args, rclone.program, and rclone.args.

## Test Signals
shell_split_test.go covers valid and invalid parsing cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split_test.go -->
# sources/sync-backup/restic/internal/backend/shell_split_test.go

## Purpose
Tests shell string splitting behavior for subprocess command options.

## Important APIs, Types, And Functions
TestShellSplitter and TestShellSplitterInvalid are the test entry points.

## Control Flow
Valid table cases compare parsed argument slices; invalid cases assert parser errors for malformed quoting/escaping.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend.SplitShellStrings and testing.

## Risks And Edge Cases
Coverage is parser-focused and does not execute resulting commands.

## Test Signals
Important regression signal for rclone and SFTP command option handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config.go -->
# sources/sync-backup/restic/internal/backend/swift/config.go

## Purpose
Parses, registers, and environment-populates OpenStack Swift backend configuration.

## Important APIs, Types, And Functions
Config, NewConfig, ParseConfig, ApplyEnvironment, and option registration are key.

## Control Flow
ParseConfig accepts swift:container:/prefix syntax and requires a slash-prefixed prefix. ApplyEnvironment fills unset auth, tenant/project, application credential, storage URL/token, and default container policy fields from OpenStack/Swift environment variables.

## State And Persistence Behavior
Config stores auth credentials/tokens, container/prefix, policy, and connection count; no repository persistence.

## Dependencies And Integration Points
Depends on os, strings, internal/backend/errors/options.

## Risks And Edge Cases
Many auth modes mean precedence matters: environment values only fill empty fields. SecretString fields must avoid accidental logging.

## Test Signals
config_test.go covers parsing valid and invalid repository strings; env application is not directly covered there.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config_test.go -->
# sources/sync-backup/restic/internal/backend/swift/config_test.go

## Purpose
Tests Swift config parsing and invalid repository strings.

## Important APIs, Types, And Functions
configTests, TestParseConfig, configTestsInvalid, and TestParseConfigInvalid are important.

## Control Flow
Valid cases assert container, prefix, and default connections; invalid cases ensure malformed Swift URLs are rejected.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend/test.ParseConfigTester.

## Risks And Edge Cases
Environment auth mapping is not tested in this file.

## Test Signals
Good signal for Swift repository location syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift.go -->
# sources/sync-backup/restic/internal/backend/swift/swift.go

## Purpose
Implements the OpenStack Swift object storage backend.

## Important APIs, Types, And Functions
beSwift, NewFactory, Open, IsNotExist/IsPermanentError, Properties, Hasher, Save, Load/openReader, Stat, Remove, List, Delete, Close, Warmup/WarmupWait, and path helpers are central.

## Control Flow
Open builds a swift.Connection from config, authenticates, ensures the container exists, and sets DefaultLayout over the prefix. Save uploads bytes with content length and MD5 hash. Load uses ranged ObjectOpen, Stat reads object metadata, List pages objects by layout prefix, Remove deletes objects, and Delete removes all keys under the layout.

## State And Persistence Behavior
Repository state is persisted as Swift objects in a container/prefix. Local state is authenticated connection, container, prefix, connection count, and layout.

## Dependencies And Integration Points
Depends on ncw/swift/v2, crypto/md5, backend/layout/location/util, feature flags, errors/debug.

## Risks And Edge Cases
Risks include auth mode complexity, object listing pagination, range/short-read classification, hash mismatch, and container policy behavior.

## Test Signals
swift_test.go runs integration suite when Swift environment variables are available; config tests cover parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift_test.go -->
# sources/sync-backup/restic/internal/backend/swift/swift_test.go

## Purpose
Runs the generic backend suite and benchmarks against a configured Swift endpoint.

## Important APIs, Types, And Functions
newSwiftTestSuite, TestBackendSwift, and BenchmarkBackendSwift are key.

## Control Flow
Tests read environment/config values, choose unique prefixes, construct a Swift factory, and run shared tests/benchmarks when required variables are available.

## State And Persistence Behavior
Uses remote Swift state and environment-provided credentials.

## Dependencies And Integration Points
Depends on backend/test Suite, swift.NewFactory, options, and internal/test skip helpers.

## Risks And Edge Cases
Skipped without environment; failures can reflect remote Swift service behavior.

## Test Signals
Provides integration coverage for Swift backend contract compliance.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/benchmarks.go -->
# sources/sync-backup/restic/internal/backend/test/benchmarks.go

## Purpose
Provides reusable backend benchmark methods for load and save performance.

## Important APIs, Types, And Functions
saveRandomFile, remove, BenchmarkLoadFile, BenchmarkLoadPartialFile, BenchmarkLoadPartialFileOffset, and BenchmarkSave are important.

## Control Flow
Benchmarks create/open a backend, save random pack data, repeatedly load full or partial contents into buffers, compare bytes, and remove data as needed.

## State And Persistence Behavior
Persists temporary benchmark data through the backend under test and removes it afterwards.

## Dependencies And Integration Points
Depends on backend.Backend, restic.Hash, internal/test random data, context, bytes/io.

## Risks And Edge Cases
Benchmarks may be expensive for remote backends; MinimalData in suites can reduce test sizes elsewhere but these benchmark sizes are fixed.

## Test Signals
Used by backend-specific Benchmark* entry points.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/benchmarks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/config.go -->
# sources/sync-backup/restic/internal/backend/test/config.go

## Purpose
Provides a generic helper for config parser tests.

## Important APIs, Types, And Functions
ConfigTestData and ParseConfigTester are the API.

## Control Flow
ParseConfigTester iterates table cases, calls a parser, and reflect.DeepEqual compares the result against expected config.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on fmt, reflect, testing.

## Risks And Edge Cases
Comparable generic bound is stricter than DeepEqual requires but works for current config structs.

## Test Signals
Used by local, rclone, rest, s3, sftp, swift config tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/doc.go -->
# sources/sync-backup/restic/internal/backend/test/doc.go

## Purpose
Documents the reusable backend test suite and how new backend tests/benchmarks are discovered.

## Important APIs, Types, And Functions
No runtime API beyond package documentation.

## Control Flow
Explains that Suite methods named Test* or Benchmark* are reflected and run alphabetically.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
Used by Go documentation.

## Risks And Edge Cases
No functional risk, but documentation must stay aligned with suite reflection behavior.

## Test Signals
Conceptually tied to suite.go tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/suite.go -->
# sources/sync-backup/restic/internal/backend/test/suite.go

## Purpose
Implements the generic backend contract test runner used by concrete backend tests.

## Important APIs, Types, And Functions
Suite, RunTests, testFuncs, benchmarkFuncs, RunBenchmarks, createOrError, create, open, cleanup, and close are central.

## Control Flow
RunTests obtains config, verifies create/close, reflects Test* methods, runs subtests, and deletes test data if cleanup is enabled. RunBenchmarks reflects Benchmark* methods. Helpers create/open backends through a location.Factory and wrap error handling/cleanup.

## State And Persistence Behavior
State includes Suite.Config and callbacks for config, factory, cleanup policy, delayed removal, and error handling. Repository state is created/deleted through the backend under test.

## Dependencies And Integration Points
Depends on reflection, testing, context, backend/location, internal/errors/test.

## Risks And Edge Cases
Reflection-based discovery means method signatures and names are part of the contract. Cleanup must be robust for remote backends and skipped cleanup mode.

## Test Signals
Exercised by all backend-specific tests that call RunTests or RunBenchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/suite.go -->
