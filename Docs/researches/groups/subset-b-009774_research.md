# subset-b-009774 research

Grouped research for rclone core fs HTTP, path, hash, listing, logging, metadata, mount-helper, backend construction, object, and open-option support files. Each section preserves the source path in its title and is wrapped for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/http.go -->
# sources/user-network-fs/rclone/fs/fshttp/http.go

## Purpose
`http.go` is rclone's shared HTTP transport and client factory. It translates global configuration into `http.Transport` settings, wraps requests for user-agent/header injection, logging, curl/debug dumps, low-level trace logging, Prometheus metrics, server-clock checks, cookie jar support, client certificate loading and hot reload, custom CA roots, proxies, HTTP/2 disabling, TCP or Unix-socket dialing, and request throttling.

## Important APIs, types, and functions
Key APIs are `LoadKeyPair`, `NewTransportCustom`, `NewTransport`, `NewClient`, `NewClientCustom`, `NewClientWithUnixSocket`, `Transport`, `SetRequestFilter`, and `RoundTrip`. `UnixSocketConfig` is an advanced config option. Helper logic includes auth scrubbing (`cleanAuths`, `cleanCurl`), server time validation, certificate expiry detection/reload, retryable-response classification for dump-on-error, and `newClientTrace` for `httptrace.ClientTrace`.

## Control flow
`NewTransportCustom` copies Go's default transport, applies rclone timeouts, proxy, TLS, CA, compression, idle-connection, HTTP/2, and custom dialer settings, then wraps it in `Transport`. Each `RoundTrip` reloads an expiring client cert if needed, applies TPS limits and configured headers, optionally filters the request, produces request/body/curl/trace dumps depending on dump flags, executes the underlying transport, dumps retryable errors/responses, records metrics, and checks the server `Date` header once per host.

## State and persistence behavior
State is process-local: a singleton transport guarded by `sync.Once`, a package cookie jar, checked-host cache, log mutex, and certificate reload mutex. Persistent state is only external file input for cert/key/CA files; no HTTP state is written except cookies in memory and logs/metrics emitted through other subsystems.

## Dependencies and integration points
This package depends on rclone `fs.ConfigInfo`, `accounting.LimitTPS`, `fs.DumpFlags`, `fs.HTTPOption`, `obscure.Reveal`, `structs.SetDefaults`, `NewDialer`, Prometheus metrics from `prometheus.go`, publicsuffix cookie jars, `http2curl`, and PKCS#8 parsing. Backends and OAuth clients call these factories to share consistent transport behavior.

## Risks and edge cases
The global `NewTransport` only reflects the first configuration until `ResetTransport` is used in tests. `LoadKeyPair` must handle encrypted PKCS#8, legacy encrypted PEM, RSA, EC, cert chains, and obscured passwords. Dumping bodies can consume or expose data if flags are wrong, so auth scrubbing is critical. Fatal errors during TLS setup terminate the process. Server-clock checks depend on trustworthy `Date` headers.

## Test signals
`http_test.go` covers auth scrubbing, curl redaction, and live client-certificate reload behavior. Wider coverage is indirect through every backend using `fshttp.NewClient*`, especially dump flags, custom headers, proxies, TLS, metrics, and Unix-socket transports.

Source-read signal: reviewed complete local file (703 lines). Types observed: `Transport`. Functions/methods observed: `ResetTransport`, `LoadKeyPair`, `NewTransportCustom`, `NewTransport`, `NewClient`, `NewClientCustom`, `NewClientWithUnixSocket`, `newTransport`, `SetRequestFilter`, `checkServerTime`, `cleanAuth`, `cleanAuths`, `cleanCurl`, `isCertificateExpired`, `reloadCertificates`, `isRetryableResponse`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/http_test.go -->
# sources/user-network-fs/rclone/fs/fshttp/http_test.go

## Purpose
`http_test.go` validates the security-sensitive and lifecycle-sensitive behavior in `fshttp/http.go`: header redaction for debug dumps/curl commands and client TLS certificate reloading when cert files change.

## Important APIs, types, and functions
The tests exercise unexported helpers `cleanAuth`, `cleanAuths`, `cleanCurl`, the package `expireWindow`, and public `NewClient`. Local helpers `createTestCert` and `writeTestCert` generate short-lived self-signed RSA client certificates, and `TestCertificates` uses `httptest.NewTLSServer` with `tls.RequestClientCert`.

## Control flow
The redaction tests run table-driven strings through the scrubbers and assert that Authorization and X-Auth-Token values are replaced with `XXXX` without removing unrelated headers. `TestCertificates` starts a TLS server, configures rclone client cert/key paths, makes one request, waits for expiry, overwrites the cert/key with a new serial number, then makes another request through the same client to prove `RoundTrip` reloads expiring certs.

## State and persistence behavior
The certificate test writes temporary cert/key files and mutates the shared config returned by `fs.GetConfig(ctx)`. It relies on the package-level certificate expiry window and the `Transport`'s in-memory TLS config being updated after file replacement.

## Dependencies and integration points
The tests depend on Go crypto/x509, `httptest`, rclone `fs.ConfigInfo`, `NewClient`, and `http2curl`. They directly protect logging behavior used by HTTP dump flags and TLS behavior used by backends requiring mutual TLS.

## Risks and edge cases
The generated certificate validity is deliberately short, so test timing can be sensitive on very slow machines. `writeTestCert` accepts a validity parameter but currently calls `createTestCert(1 * time.Second)`, so the test depends on the constant behavior. Shared config mutation must not leak badly between tests.

## Test signals
Good coverage exists for auth redaction variants, both supported sensitive headers, curl command rewriting, cert reload through real TLS handshakes, and serial-number progression at the server side.

Source-read signal: reviewed complete local file (204 lines). Functions/methods observed: `TestCleanAuth`, `TestCleanAuths`, `TestCleanCurl`, `createTestCert`, `writeTestCert`, `TestCertificates`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/http_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/prometheus.go -->
# sources/user-network-fs/rclone/fs/fshttp/prometheus.go

## Purpose
`prometheus.go` adds optional HTTP-level Prometheus instrumentation for `fshttp.Transport`. It counts responses by request host, HTTP method, and status code.

## Important APIs, types, and functions
`Metrics` contains a `StatusCode *prometheus.CounterVec`. `NewMetrics(namespace string)` creates the counter under subsystem `http` and name `status_code`. `DefaultMetrics` is a package-level hook copied into new transports. `Collectors` returns the collector set for registration. `onResponse` increments the counter and records status code `0` when there is no response.

## Control flow
Callers create metrics, register `Collectors`, and assign `DefaultMetrics` before constructing transports. `newTransport` captures the default metrics pointer. At the end of every `Transport.RoundTrip`, `t.metrics.onResponse(req, resp)` labels the observation with `req.Host`, `req.Method`, and `resp.StatusCode` or zero.

## State and persistence behavior
Metrics are in-memory Prometheus counters. `DefaultMetrics` is mutable process-global setup state; existing transports keep the pointer they were constructed with. There is no persistence beyond exporter scraping.

## Dependencies and integration points
The file depends on `github.com/prometheus/client_golang/prometheus` and integrates only through `fshttp.Transport.RoundTrip`. It is used by rclone processes that expose Prometheus metrics for backend HTTP activity.

## Risks and edge cases
Using raw `req.Host` may create high cardinality if requests span many hostnames. Nil metrics are intentionally a no-op. A nil response with an error becomes code `0`, which consumers must interpret as transport failure rather than an HTTP response.

## Test signals
There is no direct test in this subset. Indirect coverage comes from `RoundTrip` execution and any Prometheus integration tests elsewhere that register `DefaultMetrics`.

Source-read signal: reviewed complete local file (51 lines). Types observed: `Metrics`. Functions/methods observed: `NewMetrics`, `Collectors`, `onResponse`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/prometheus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fspath/fuzz.go -->
# sources/user-network-fs/rclone/fs/fspath/fuzz.go

## Purpose
`fuzz.go` is a go-fuzz harness for `fspath.Parse`. It checks parser invariants across arbitrary byte strings converted to Go strings.

## Important APIs, types, and functions
The only exported fuzz entry is `Fuzz(data []byte) int`, guarded by the `gofuzz` build tag. It calls `Parse`, then verifies whether the input was preserved as a local path or split as `ConfigString + ":" + Path`.

## Control flow
Invalid parses return `0` immediately. For local paths, the harness requires an empty config string and exact path preservation. For remote paths, it requires reconstructing the original input from config string, colon, and parsed path. Any invariant violation panics for the fuzz runner to collect.

## State and persistence behavior
The harness has no persistent state. The source comment documents corpus generation and cleanup commands that create/remove local fuzz directories outside normal builds.

## Dependencies and integration points
It depends only on the package's `Parse` function and is intended to run with the legacy `github.com/dvyukov/go-fuzz` toolchain. It complements the table tests in `path_test.go`.

## Risks and edge cases
The invariant accounts for local versus remote parsing but not every Windows slash normalization nuance, so fuzz results can differ by platform if built there. It returns zero for all cases, making it a crash/invariant harness rather than a coverage-guided accept/reject classifier.

## Test signals
The presence of this harness signals that `Parse` has historically needed broad input robustness testing beyond table cases, especially around colons, quotes, commas, Unicode, and path separators.

Source-read signal: reviewed complete local file (46 lines). Functions/methods observed: `Fuzz`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fspath/fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fspath/path.go -->
# sources/user-network-fs/rclone/fs/fspath/path.go

## Purpose
`path.go` parses and manipulates rclone filesystem paths. It distinguishes local paths from configured remotes and on-the-fly backend strings, validates remote/config names, parses comma-separated connection parameters, and supplies helpers for splitting and joining remote roots.

## Important APIs, types, and functions
Public APIs include `CheckConfigName`, `MakeConfigName`, `Parsed`, `Parse`, `SplitFs`, `Split`, and `JoinRootPath`. Important internal helpers include `checkRemoteName`, `isConfigParam`, `makeAbsolute`, regex matchers for config names, and explicit parser errors such as `errBadConfigParam`, `errQuotedValue`, and `errAfterQuote`.

## Control flow
`Parse` first treats strings without colons as local paths, then runs a state machine over config name, parameter, value, quoted value, after-quote, and done states. It supports `remote:path`, `:backend,param=value:path`, boolean params, single/double quoted params, doubled quote escaping, drive-letter detection, and slash conversion for parsed remote paths. `SplitFs` appends the remote colon back, `Split` uses `path.Split`, and `JoinRootPath` normalizes a candidate child path so it cannot climb above the root.

## State and persistence behavior
The file holds only compiled regexes and sentinel errors. It persists nothing; all parse results are returned as `Parsed` values with optional `configmap.Simple` maps.

## Dependencies and integration points
`newfs.go` calls `ParseRemote` through this package to resolve backends. Mount helpers and tests share similar quoting concepts. `JoinRootPath` is used by `fs.FullPath` and other places that reconstruct canonical `remote:path` strings. `driveletter.IsDriveLetter` handles Windows ambiguity.

## Risks and edge cases
Colons in local paths, Windows drive letters, leading `:backend` remotes, Unicode remote names, quoted parameter values, doubled quotes, empty params, and path traversal normalization are all sensitive. Remote names allow spaces internally but not leading/trailing space or leading hyphen. Parser behavior is part of rclone's user-facing CLI contract, so compatibility changes can break config strings.

## Test signals
`path_test.go` covers remote-name validation, Unicode names, on-the-fly backend params, quote escaping, local colon paths, Windows-specific slash/drive-letter cases, `SplitFs`, `Split`, `makeAbsolute`, and `JoinRootPath`. `fuzz.go` adds fuzz invariants.

Source-read signal: reviewed complete local file (356 lines). Types observed: `Parsed`. Functions/methods observed: `CheckConfigName`, `MakeConfigName`, `checkRemoteName`, `isConfigParam`, `Parse`, `SplitFs`, `Split`, `makeAbsolute`, `JoinRootPath`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fspath/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fspath/path_test.go -->
# sources/user-network-fs/rclone/fs/fspath/path_test.go

## Purpose
`path_test.go` is the main regression suite for rclone path parsing and joining. It captures the user-facing syntax contract for local paths, remotes, on-the-fly remotes, config parameters, quoting, Windows path handling, and root-safe joins.

## Important APIs, types, and functions
Tests target `CheckConfigName`, `MakeConfigName`, `checkRemoteName`, `Parse`, `SplitFs`, `Split`, `makeAbsolute`, and `JoinRootPath`. The `-make-corpus` test flag can emit parser corpus files for the go-fuzz harness.

## Control flow
Table-driven cases compare parsed structs and exact errors. Tests skip Windows-only or non-Windows-only expectations based on `runtime.GOOS`. `TestParse` optionally writes each input into `corpus/` when requested. Later tests verify recomposition properties such as `remoteName + remotePath == remote` and `parent + leaf == remote`.

## State and persistence behavior
Normal test runs have no persistent state. With `-make-corpus`, the test creates a `corpus` directory and writes sample inputs. Some cases compare `configmap.Simple` maps built by the parser.

## Dependencies and integration points
The suite depends on `configmap.Simple`, `filepath.FromSlash`, testify assertions, and the parser implementation. These tests protect `fs.NewFs`, CLI parsing, backend connection strings, and any code using `JoinRootPath` for canonical path construction.

## Risks and edge cases
The cases encode subtle behavior: a path with a slash before colon is local; `C:` is remote on non-Windows but a drive letter on Windows; quoted config values must terminate with comma or colon; `:backend` cannot accidentally become a local path; `JoinRootPath` preserves leading `//` for network paths.

## Test signals
Coverage is broad and high-signal. It includes invalid characters, leading/trailing spaces, Unicode remote names, boolean config params, empty config values, doubled quotes, empty path errors, Windows slash normalization, root-directory splitting, and path traversal cleanup.

Source-read signal: reviewed complete local file (646 lines). Functions/methods observed: `TestCheckConfigName`, `TestCheckRemoteName`, `TestParse`, `TestSplitFs`, `TestSplit`, `TestMakeAbsolute`, `TestJoinRootPath`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fspath/path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/hash/hash.go -->
# sources/user-network-fs/rclone/fs/hash/hash.go

## Purpose
`hash.go` defines rclone's hash type registry, hash-set bitmask operations, streaming hash calculators, and multihash writer. It standardizes MD5, SHA-1, Whirlpool, CRC-32, SHA-256, SHA-512, BLAKE3, XXH3-64, and XXH3-128 support for filesystem backends and operations.

## Important APIs, types, and functions
Important exports are `Type`, `Set`, `RegisterHash`, `SupportOnly`, `ErrUnsupported`, hash constants, `Supported`, `Width`, `Stream`, `StreamTypes`, `MultiHasher`, `NewMultiHasher`, `NewMultiHasherTypes`, `Equals`, and `HelpString`. `Type.Set` implements flag parsing by lowercase name or exact alias. `xxh128Hasher` adapts `xxh3.Hasher` to a 128-bit `hash.Hash`.

## Control flow
`init` registers algorithms in stable bit order. `StreamTypes` builds requested hashers, copies input through a multiwriter, and returns hex sums. `MultiHasher.Write` updates all hashers while counting bytes; `Sums`, `Sum`, and `SumString` return accumulated hashes. `fromTypes` rejects sets not contained in `Supported()`. `Set` methods perform bitwise add/overlap/subset, enumeration, first-bit selection, and population count.

## State and persistence behavior
Global registry maps and the `supported` slice are process state initialized at package load. `SupportOnly` mutates supported hashes for tests and returns the old slice. Hash calculations are in-memory and do not persist data.

## Dependencies and integration points
Backends expose supported sets through `Fs.Hashes()`, sync/check operations compare hashes with `Equals`, local/object helpers use `MultiHasher`, and CLI help/flags use `Type.Set`, `Type.String`, and `HelpString`. External hash implementations are Whirlpool, BLAKE3, and xxh3.

## Risks and edge cases
Hash `Type` values are bit positions, so registration order is compatibility-sensitive. `Type.String` panics on unknown types. `fromTypes` rejects unknown bitmasks based on current `Supported`, which tests can mutate. `Equals` treats empty hashes as matching, which is intentional for unknown hashes but dangerous if callers assume strict equality.

## Test signals
`hash_test.go` validates set operations, known digest vectors for all registered algorithms including empty input, stream and multihasher behavior, string/flag parsing, and type stability for `None`, `MD5`, and `SHA1`.

Source-read signal: reviewed complete local file (421 lines). Types observed: `Type`, `hashDefinition`, `xxh128Hasher`, `MultiHasher`, `Set`. Functions/methods observed: `RegisterHash`, `SupportOnly`, `Sum`, `Size`, `init`, `Supported`, `Width`, `Stream`, `StreamTypes`, `String`, `Set`, `Type`, `fromTypes`, `toMultiWriter`, `NewMultiHasher`, `NewMultiHasherTypes`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/hash/hash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/hash/hash_test.go -->
# sources/user-network-fs/rclone/fs/hash/hash_test.go

## Purpose
`hash_test.go` validates the hash registry, set bitmask helpers, multihash streaming, known digest outputs, flag parsing, and initial type-value stability.

## Important APIs, types, and functions
The suite exercises `hash.Set` methods, `hash.NewHashSet`, `Supported`, `NewMultiHasher`, `NewMultiHasherTypes`, `Stream`, `StreamTypes`, `Type.String`, `Type.Set`, and the `pflag.Value` interface implementation. `hashTestSet` contains canonical digest vectors for non-empty and empty byte slices.

## Control flow
Tests build sets, add/overlap/subset them, check enumeration and first-choice behavior, stream fixed buffers through `MultiHasher` or `Stream*`, and compare every returned digest to expected hex strings. Setter tests verify accepted names and aliases and rejected near-misses.

## State and persistence behavior
The tests use the package global registry but do not mutate it. No persistent state is written.

## Dependencies and integration points
The tests import rclone `fs` only for logging, `pflag` for interface checking, and testify for assertions. They protect behavior consumed by backend `Hashes()` declarations, copy/check logic, and command-line hash selection.

## Risks and edge cases
Digest vectors catch algorithm swaps, wrong xxh128 length/endian behavior, and accidental registration changes. The type stability test only asserts early values, so adding later hash types remains possible but reordering initial registrations should fail.

## Test signals
Coverage is strong for normal hash paths: empty input, multiple algorithms in one pass, single requested hash, set string formatting, parser aliases such as `SHA-1`, and rejection of unsupported spelling like `Sha-1`.

Source-read signal: reviewed complete local file (219 lines). Types observed: `hashTest`. Functions/methods observed: `TestHashSet`, `TestMultiHasher`, `TestMultiHasherTypes`, `TestHashStream`, `TestHashStreamTypes`, `TestHashSetStringer`, `TestHashStringer`, `TestHashSetter`, `TestHashTypeStability`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/hash/hash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/helpers.go -->
# sources/user-network-fs/rclone/fs/list/helpers.go

## Purpose
`helpers.go` contains small listing utilities for backend implementations. It batches `ListR` callback entries and adapts backends that implement `ListP` into the ordinary `List` style return.

## Important APIs, types, and functions
`Helper` stores a `fs.ListRCallback` and buffered `fs.DirEntries`. `NewHelper`, `Add`, `Flush`, and internal `send` implement 100-entry batching. `WithListP` calls a `fs.ListPer` backend and accumulates all paged callback entries into one `fs.DirEntries` slice.

## Control flow
Backends construct a `Helper` with their recursive-list callback, call `Add` for each entry, and call `Flush` at the end. `Add` ignores nil entries and triggers the callback when the buffer reaches 100 entries. `WithListP` appends each `ListP` callback page to a result slice while updating accounting stats.

## State and persistence behavior
State is transient per helper instance: a callback and in-memory entry buffer. There is no persistence. `WithListP` updates process accounting counters through the context's stats object.

## Dependencies and integration points
The file depends on `fs.ListRCallback`, `fs.DirEntries`, `fs.ListPer`, and `accounting.Stats`. It is used by backends implementing fast/recursive listing and by backends that expose paged listing but need a `List` adapter.

## Risks and edge cases
Callers must remember to `Flush`, or the final partial batch is lost. `WithListP` can hold all entries in memory, so it is not suitable for huge listings when a streaming callback is available. Callback errors stop processing and leave buffered state as-is.

## Test signals
`helpers_test.go` checks constructor state, nil entry handling, threshold sending at 100 entries, flush behavior, `WithListP` aggregation, and partial result return when the paged listing reports an error.

Source-read signal: reviewed complete local file (61 lines). Types observed: `Helper`. Functions/methods observed: `NewHelper`, `send`, `Add`, `Flush`, `WithListP`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/helpers_test.go -->
# sources/user-network-fs/rclone/fs/list/helpers_test.go

## Purpose
`helpers_test.go` verifies the batching semantics of `list.Helper` and the `WithListP` adapter from paged callback listing to accumulated directory entries.

## Important APIs, types, and functions
Tests target `NewHelper`, `Helper.Add`, `Helper.Flush`, and `WithListP`. `mockListPfs` implements `fs.ListPer` and emits entries in two-entry pages, optionally returning an error after a configured count.

## Control flow
Helper tests construct callbacks that record invocation, add mock objects, and assert whether buffered entries remain or callbacks fired. `WithListP` tests build 26 mock entries, run normal and error cases, and compare returned slices to the expected full or partial prefix.

## State and persistence behavior
All state is in-memory test slices and booleans. No files or remote state are used.

## Dependencies and integration points
The tests use `mockobject`, `fs.ListPer`, context, testify, and errors. They protect helper behavior used by recursive backend listing implementations and paged listing adapters.

## Risks and edge cases
The threshold is fixed at 100, so tests assert exact behavior at the boundary. The mock paging loop uses `entries[:2]` while advancing by two and assumes an even count, matching the test's 26 entries.

## Test signals
Coverage is focused and useful: constructor callback identity, ignored nil entries, callback batching, buffer clearing, final flush, page aggregation, and error propagation with partial results.

Source-read signal: reviewed complete local file (145 lines). Types observed: `mockListPfs`. Functions/methods observed: `mockCallback`, `TestNewListRHelper`, `TestListRHelperAdd`, `TestListRHelperSend`, `TestListRHelperFlush`, `ListP`, `TestListWithListP`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/list.go -->
# sources/user-network-fs/rclone/fs/list/list.go

## Purpose
`list.go` implements filtered and sorted directory listing for rclone operations. It wraps backend `List`, `ListP`, and optional `ListR` behavior with accounting, filter evaluation, directory membership validation, and stable sorting.

## Important APIs, types, and functions
Public APIs are `DirSorted` and `DirSortedFn`. Internal helpers are `listP`, `filterDir`, and `filterAndSortDir`. `DirSortedFn` uses the external-capable `Sorter` from `sorter.go` and accepts a `KeyFn` for custom ordering.

## Control flow
`DirSorted` calls `f.List`, counts entries, optionally rejects an exclude-file directory, filters entries, and stable-sorts in memory. `DirSortedFn` creates a `Sorter`, lists via `ListP` if available or `List` fallback, counts entries per callback, filters each batch, adds it to the sorter, and finally sends sorted results. `filterDir` checks object and directory filters, validates that each remote belongs directly to the listed directory, and logs ignored malformed entries.

## State and persistence behavior
The functions hold transient entry slices and sorter state. They update listing accounting counters and read filter/config state from context. They do not persist changes.

## Dependencies and integration points
Dependencies include `fs.Fs`, optional `Features().ListP`, `accounting`, `filter`, `bucket.IsAllSlashes`, and `Sorter`. This code feeds operations such as sync/copy/check that require deterministic directory listings.

## Risks and edge cases
Backends can return malformed entries, duplicate entries, entries outside the requested dir, same-as-dir entries, or nested children in non-recursive listings; this code filters/logs those. Exclude-file handling only applies when listing the starting directory. Sorting must be stable to preserve backend order for duplicates.

## Test signals
`list_test.go` covers includeAll versus filtered listing, directory-membership validation at normal and root dirs, bucket slash exceptions, and erroring on unknown `DirEntry` types. Integration tests elsewhere cover `DirSorted` through operations.

Source-read signal: reviewed complete local file (177 lines). Functions/methods observed: `DirSorted`, `listP`, `DirSortedFn`, `filterDir`, `filterAndSortDir`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/list_test.go -->
# sources/user-network-fs/rclone/fs/list/list_test.go

## Purpose
`list_test.go` validates filtering, sorting, and directory-membership checks used by `list.go`.

## Important APIs, types, and functions
Tests focus on unexported `filterAndSortDir` and the `unknownDirEntry` mock type. They indirectly exercise `filterDir` and stable sorting of `fs.DirEntries` by remote.

## Control flow
`TestFilterAndSortIncludeAll` builds mixed mock directories/objects and compares includeAll behavior against filtered object/directory predicates. `TestFilterAndSortCheckDir` and root variants feed intentionally malformed remotes to ensure only direct children remain. `TestFilterAndSortUnknown` verifies non-object/non-directory entries return an error.

## State and persistence behavior
Tests use only in-memory mock entries. No persistent state or filesystem state is touched.

## Dependencies and integration points
The suite uses `mockdir`, `mockobject`, `fs.DirEntries`, context, and testify. It protects the listing contract consumed by sync, walk, and backend wrappers.

## Risks and edge cases
The tests encode allowed double-slash/bucket-style directory exceptions and reject entries with wrong prefixes, same name as the directory, or nested children. Filter callback errors are not covered here.

## Test signals
Coverage is concise but covers the main correctness risks: stable output order, includeAll bypassing filters, filtered exclusions, root versus subdirectory validation, and unknown entry-type failures.

Source-read signal: reviewed complete local file (108 lines). Types observed: `unknownDirEntry`. Functions/methods observed: `TestFilterAndSortIncludeAll`, `TestFilterAndSortCheckDir`, `TestFilterAndSortCheckDirRoot`, `Fs`, `String`, `Remote`, `ModTime`, `Size`, `TestFilterAndSortUnknown`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/sorter.go -->
# sources/user-network-fs/rclone/fs/list/sorter.go

## Purpose
`sorter.go` provides a scalable sorter for directory entries. It sorts in memory for small lists and switches to on-disk external sorting above `--list-cutoff`, then streams sorted entries back through a `ListR`-style callback.

## Important APIs, types, and functions
Exports are `NewObjecter`, `Sorter`, `KeyFn`, `NewSorter`, `Sorter.Add`, `Sorter.Send`, `Sorter.CleanUp`, and `SortToChan`. Important internals are `entryToKey`, `keyToEntry`, `startExtSort`, `sendEntriesToExtSort`, and the `listHelper` that batches rehydration from external-sort keys.

## Control flow
`NewSorter` captures config, context cancellation, callback, and key function. `Add` appends entries until cutoff, then initializes `extsort.Strings`, sends accumulated entries as `key + NUL + remote`, and streams later additions to the sorter. `Send` either stable-sorts the in-memory slice or closes the external-sort input, reads sorted keys, recreates directory entries directly and objects via `NewObject`, batches callbacks, and returns accumulated rehydration errors. `CleanUp` cancels background work and clears memory.

## State and persistence behavior
Small sort state is in-memory. External sort state includes channels, an `extsort.StringSorter`, temporary files in OS temp or `tempDir`, cancellation state, and error aggregation. No source/destination filesystem data is mutated, but external mode reopens objects by remote.

## Dependencies and integration points
The sorter depends on `lanrat/extsort`, `errcount`, `errgroup`, rclone `fs.DirEntry`, `fs.Object`, `fs.Directory`, and config `ListCutoff`/`Checkers`. It is used by `DirSortedFn` and by `march` tests to produce sorted channels.

## Risks and edge cases
External mode only serializes remote names, so objects must still exist and be resolvable by `NewObject` during `Send`. Directory entries are reconstructed minimally with zero modtime. Keys use NUL as a separator. Temp-file initialization can fail and must return an error rather than panic. Concurrent `Add` calls are mutex-protected, but callbacks run under `Send`.

## Test signals
`sorter_test.go` validates identity and custom-key sorting, external switch thresholds, object/directory rehydration, 100k-entry boundary behavior, temp-directory failure handling for issue-style regressions, cleanup, and a large benchmark for 10 million entries.

Source-read signal: reviewed complete local file (354 lines). Types observed: `NewObjecter`, `Sorter`, `KeyFn`, `listHelper`. Functions/methods observed: `identityKeyFn`, `NewSorter`, `entryToKey`, `keyToEntry`, `sendEntriesToExtSort`, `startExtSort`, `Add`, `newListHelper`, `send`, `Add`, `Flush`, `Send`, `CleanUp`, `SortToChan`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/sorter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/sorter_test.go -->
# sources/user-network-fs/rclone/fs/list/sorter_test.go

## Purpose
`sorter_test.go` tests the in-memory and external-sort behavior of `Sorter`, including custom keys, object/directory reconstruction, cutoff boundaries, temp-file errors, and benchmark-scale throughput.

## Important APIs, types, and functions
The suite targets `NewSorter`, `Sorter.Add`, `Sorter.Send`, `Sorter.CleanUp`, `SortToChan` indirectly, and custom `KeyFn` behavior. `testFs` and `benchFs` implement the minimal `NewObjecter` interface needed to rehydrate objects in external mode.

## Control flow
Tests add unsorted mock entries, assert unsorted internal state before `Send`, then require callback order. `testSorterExt` builds maps of mixed mock objects/directories, feeds them in arbitrary order, checks whether external sorting was activated, and deletes entries from the map as callbacks arrive. The temp-file test forces external-sort initialization against an unwritable or invalid directory and expects an error.

## State and persistence behavior
Most tests use in-memory maps and mock entries. The temp-file test creates temporary filesystem paths and permission states, with cleanup on Unix. External-sort tests may create temporary files through the library when cutoff is exceeded.

## Dependencies and integration points
The tests use rclone config `ListCutoff`, mock object/dir packages, Go runtime path behavior, and OS temp/permission semantics. They protect `DirSortedFn` and `march` because both rely on deterministic sorted entry streams.

## Risks and edge cases
The external-sort path depends on re-fetching objects by remote and distinguishing directories by a trailing slash in serialized data. The test type-check assertions have a minor local bug (`gotDir`/`gotObj` are derived from `wantEntry`), but map deletion and callback order still catch many failures.

## Test signals
Coverage is strong for sorting order, case-insensitive key functions, cutoff values exactly around 100000 entries, cleanup state, and the no-panic error path when temporary file creation fails.

Source-read signal: reviewed complete local file (362 lines). Types observed: `testFs`, `benchFs`. Functions/methods observed: `TestSorter`, `TestSorterIdentity`, `TestSorterKeyFn`, `NewObject`, `String`, `keyCaseInsensitive`, `testSorterExt`, `TestSorterExt`, `TestSorterExtTempFileError`, `NewObject`, `String`, `BenchmarkSorterExt`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/list/sorter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log.go -->
# sources/user-network-fs/rclone/fs/log.go

## Purpose
`fs/log.go` defines rclone's core logging API and log levels. It maps rclone's syslog-inspired levels onto `log/slog`, provides structured log values, gates messages by configured log level, implements panic/fatal helpers, and exposes convenience functions used across the codebase.

## Important APIs, types, and functions
Exports include `LogLevel`, level constants, `LogValueItem`, `LogValue`, `LogValueHide`, `LogLevelToSlog`, `LogPrint`, `LogPrintf`, `LogLevelPrint`, `LogLevelPrintf`, `Panic`, `Panicf`, `Fatal`, `Fatalf`, `Errorf`, `Logf`, `Infof`, `Debugf`, `LogDirName`, `PrettyPrint`, and `SetLogger`. Extra slog levels include notice, critical, alert, emergency, and off.

## Control flow
Callers invoke level-specific helpers. The wrappers compare `GetConfig(context.TODO()).LogLevel` to the requested level, format text and structured attributes, add object/objectType attributes when present, and send records to the package-level slog logger. Fatal helpers also detect rc job stack frames and panic instead of exiting when invoked inside an rc job.

## State and persistence behavior
The only state is the package-level `logger`, initially `slog.Default()` and later set by `fs/log/slog.go`. Logging output persistence is controlled by handlers in `fs/log`; this file itself does not open files or sinks.

## Dependencies and integration points
This API is imported throughout rclone. `fs/log/slog.go` calls `SetLogger`; `fs/log/log.go` installs reload hooks and output sinks. `Enum` support provides CLI/config parsing for `LogLevel`.

## Risks and edge cases
Fatal functions call `os.Exit(1)` outside rc jobs, so tests and libraries must avoid them unless expected. Structured `LogValueItem` arguments are extracted only from printf args, and hidden values render empty in text but remain structured. Caller code often passes arbitrary objects, so object formatting must avoid side effects.

## Test signals
`log_test.go` covers `LogValue` rendering/hiding and `LogLevel` string/set/JSON parsing. Handler formatting, levels, concurrency, and JSON behavior are covered in `fs/log/slog_test.go`.

Source-read signal: reviewed complete local file (348 lines). Types observed: `LogLevel`, `logLevelChoices`, `LogValueItem`. Functions/methods observed: `Choices`, `Type`, `LogValue`, `LogValueHide`, `String`, `LogLevelToSlog`, `logSlog`, `logSlogWithObject`, `LogPrint`, `LogPrintf`, `LogLevelPrint`, `LogLevelPrintf`, `Panic`, `Panicf`, `panicIfRcJob`, `Fatal`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/event_log.go -->
# sources/user-network-fs/rclone/fs/log/event_log.go

## Purpose
`event_log.go` is the non-Windows stub for Windows Event Log support. It makes the logging package compile on other platforms while reporting that the feature is unsupported.

## Important APIs, types, and functions
The single function is `startWindowsEventLog(*OutputHandler) error`, compiled when `!windows`. It returns a formatted error naming `runtime.GOOS`.

## Control flow
`InitLogging` calls `startWindowsEventLog` only when `Opt.WindowsEventLogLevel` is not off. On non-Windows platforms that configuration path returns an error, and `InitLogging` fatal-exits with context.

## State and persistence behavior
There is no state and no persistence. The stub does not create event sources or outputs.

## Dependencies and integration points
The file depends on `runtime` and `fmt`, and its signature matches the Windows implementation in `event_log_windows.go`. It integrates with the common logging initialization flow.

## Risks and edge cases
The stub protects against silently accepting unsupported `--windows-event-log-level` on non-Windows platforms. The fatal behavior occurs in the caller, not here.

## Test signals
No direct test in this subset targets the stub. Platform build coverage and option handling through `InitLogging` are the main signals.

Source-read signal: reviewed complete local file (15 lines). Functions/methods observed: `startWindowsEventLog`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/event_log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/event_log_windows.go -->
# sources/user-network-fs/rclone/fs/log/event_log_windows.go

## Purpose
`event_log_windows.go` implements Windows Event Log output for rclone logging. It installs/opens the `rclone` event source and adds an extra JSON logging destination that writes records into the Windows Application/Event Log infrastructure.

## Important APIs, types, and functions
Important items are `startWindowsEventLog`, `eventLog`, constants `errorID`, `infoID`, `sourceName`, and package variable `windowsEventLog`. `eventLog` maps rclone/slog levels onto Windows Error, Warning, or Info calls.

## Control flow
When enabled, `startWindowsEventLog` attempts source registration, opens the event log, stores the handle globally, registers a close hook via `atexit`, adds `eventLog` as a JSON extra output to `OutputHandler`, and logs activation. Each event checks `Opt.WindowsEventLogLevel` and writes to the appropriate event-log severity.

## State and persistence behavior
The Windows event-log handle is process-global and closed at exit. Log entries persist in the OS event log. Handler extra-output state is modified by appending a destination.

## Dependencies and integration points
The implementation depends on `golang.org/x/sys/windows/svc/eventlog`, `windows`, `atexit`, rclone `fs` levels, and `OutputHandler.AddOutput`. It is invoked only from `InitLogging`.

## Risks and edge cases
Source installation failure is ignored deliberately because Windows has fallbacks. Open failures are fatal through the caller. The global `windowsEventLog` must be non-nil when `eventLog` runs. Level filtering uses rclone levels converted to slog severity, so misconfiguration can drop expected events.

## Test signals
No direct test is present in this subset, likely due to platform requirements. Build tags and manual Windows logging tests are needed for end-to-end confidence.

Source-read signal: reviewed complete local file (79 lines). Functions/methods observed: `startWindowsEventLog`, `eventLog`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/event_log_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/log.go -->
# sources/user-network-fs/rclone/fs/log/log.go

## Purpose
`fs/log/log.go` owns high-level logging configuration and initialization. It registers global logging options, defines log-format flags, trace/stack helpers, reload validation, file/syslog/systemd/event-log setup, JSON-log implication, and stderr redirection decisions.

## Important APIs, types, and functions
Exports are `OptionsInfo`, `Options`, `Opt`, `Trace`, `Stack`, `InitLogging`, and `Redirected`. Internal pieces include `logFormat` bit flags, `logFormatChoices`, `fnName`, `logReload`, and `fs.LogReload` assignment. Options cover log file, rotation, format, syslog, systemd, and Windows Event Log level.

## Control flow
`init` registers options and reload hook. `InitLogging` sets the process default slog logger to rclone's handler, maps standard log output to notice, opens file output or lumberjack rotation if configured, applies JSON formatting, sets initial level and format, starts syslog if requested, autodetects journald when stderr is not redirected, enables systemd output, and starts Windows event logging when configured.

## State and persistence behavior
`Opt` is global config state. `InitLogging` mutates process-wide slog defaults and the global `Handler`. File logging persists to a configured file or rotated lumberjack files. Syslog/systemd/Event Log output persists through OS logging systems. `Trace`/`Stack` only emit when debug logging is active.

## Dependencies and integration points
This file coordinates `fs` config, `OutputHandler` from `slog.go`, platform files for stderr/syslog/systemd/event logs, `lumberjack` rotation, and the CLI/global option system. It is called by CLI, librclone, and tests rather than package init to avoid import side effects.

## Risks and edge cases
`--syslog` and `--log-file` are mutually exclusive. File mode without rotation redirects stderr for panic capture; rotated mode does not redirect stderr in the same way. Journald autodetection changes formatting. `logReload` validates Windows event log level relative to main log level. Fatal setup errors exit the process.

## Test signals
Direct tests for this file are limited in the subset; `slog_test.go` covers the handler underneath and platform behavior needs integration/manual testing. The option registration is exercised by normal CLI startup.

Source-read signal: reviewed complete local file (304 lines). Types observed: `Options`, `logFormat`, `logFormatChoices`. Functions/methods observed: `init`, `Choices`, `fnName`, `Trace`, `Stack`, `logReload`, `init`, `InitLogging`, `Redirected`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/logflags/logflags.go -->
# sources/user-network-fs/rclone/fs/log/logflags/logflags.go

## Purpose
`logflags.go` bridges logging options into pflag command-line flags.

## Important APIs, types, and functions
The only public function is `AddFlags(flagSet *pflag.FlagSet)`, which calls `flags.AddFlagsFromOptions` with `log.OptionsInfo`.

## Control flow
CLI setup passes a flag set to `AddFlags`; the generic config flag helper expands every entry in `log.OptionsInfo` into command-line flags.

## State and persistence behavior
The file holds no state. It wires flags to the global logging options handled by rclone's config system.

## Dependencies and integration points
It depends on `fs/config/flags`, `fs/log`, and `spf13/pflag`. It is used by command packages that expose global logging flags.

## Risks and edge cases
All behavior depends on `log.OptionsInfo` staying accurate. If option names or types change without corresponding flag handling, CLI logging configuration can drift.

## Test signals
No direct test is present. Coverage is indirect through CLI flag parsing and global option registration tests elsewhere.

Source-read signal: reviewed complete local file (13 lines). Functions/methods observed: `AddFlags`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/logflags/logflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/redirect_stderr.go -->
# sources/user-network-fs/rclone/fs/log/redirect_stderr.go

## Purpose
`redirect_stderr.go` is the fallback stderr-redirection implementation for platforms without Unix or Windows support in the other build-tagged files.

## Important APIs, types, and functions
The single function is `redirectStderr(f *os.File)`, compiled for a narrow set of non-Windows, non-common-Unix platforms. It logs that stderr cannot be redirected.

## Control flow
When file logging without rotation is configured, `InitLogging` calls `redirectStderr`. On these platforms the function emits an error through rclone logging and leaves stderr unchanged.

## State and persistence behavior
No state is changed except the emitted log. Stderr remains connected to its original destination.

## Dependencies and integration points
The file depends on `os` and rclone `fs.Errorf`. It shares a function signature with Unix and Windows implementations selected by build tags.

## Risks and edge cases
Panic output may not be captured in the configured log file on these platforms. Because this implementation only logs an error, callers continue running with reduced crash-log capture.

## Test signals
No direct tests are present; platform build coverage verifies selection.

Source-read signal: reviewed complete local file (16 lines). Functions/methods observed: `redirectStderr`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/redirect_stderr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/redirect_stderr_unix.go -->
# sources/user-network-fs/rclone/fs/log/redirect_stderr_unix.go

## Purpose
`redirect_stderr_unix.go` redirects process stderr to the configured log file on supported Unix-like platforms so panics and runtime diagnostics are captured.

## Important APIs, types, and functions
The file implements `redirectStderr(f *os.File)`. It duplicates the original stderr file descriptor and stores it in `config.PasswordPromptOutput`, then uses `unix.Dup2` to replace stderr with the log file descriptor.

## Control flow
`InitLogging` calls this after opening a non-rotated log file. The function duplicates stderr first for password prompts, then atomically redirects file descriptor 2 to the log file. Failures call `fs.Fatalf`.

## State and persistence behavior
The process file descriptor table is mutated. `config.PasswordPromptOutput` preserves a handle to the original stderr for interactive password prompts. Runtime panic output persists to the log file afterward.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix`, `fs/config`, and core logging fatal helpers. It is selected by build tags for common Unix-like systems except Solaris, Plan 9, and JS.

## Risks and edge cases
Descriptor duplication/redirection failures are fatal. Redirecting stderr is process-wide and affects third-party libraries. Rotating log mode does not use this path, so panic capture differs by log-file configuration.

## Test signals
No direct test exists in this subset. Behavior is typically validated by platform integration tests or manual log-file crash checks.

Source-read signal: reviewed complete local file (26 lines). Functions/methods observed: `redirectStderr`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/redirect_stderr_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/redirect_stderr_windows.go -->
# sources/user-network-fs/rclone/fs/log/redirect_stderr_windows.go

## Purpose
`redirect_stderr_windows.go` implements stderr redirection for Windows by updating the process standard error handle.

## Important APIs, types, and functions
It defines DLL/procedure globals for `kernel32.dll` `SetStdHandle`, helper `setStdHandle`, and `redirectStderr(f *os.File)`.

## Control flow
`redirectStderr` calls `setStdHandle(syscall.STD_ERROR_HANDLE, syscall.Handle(f.Fd()))`. `setStdHandle` invokes the Windows API via `syscall.SyscallN` and translates zero return values into errors. Failures become fatal logging errors.

## State and persistence behavior
The process standard error handle is changed globally, so later stderr writes go to the log file. No other persistent state is maintained by this file.

## Dependencies and integration points
The file depends on Windows syscall APIs and rclone `fs.Fatalf`. It is selected by the `windows` build tag and called by `InitLogging` for non-rotated log files.

## Risks and edge cases
Handle replacement is process-wide and can affect libraries. The code does not preserve the old handle for password prompts like the Unix implementation does. API failures abort process startup.

## Test signals
No direct test is present. Windows build and manual logging/panic capture tests are needed.

Source-read signal: reviewed complete local file (40 lines). Functions/methods observed: `setStdHandle`, `redirectStderr`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/redirect_stderr_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/slog.go -->
# sources/user-network-fs/rclone/fs/log/slog.go

## Purpose
`slog.go` implements rclone's custom `log/slog` handler. It preserves rclone's historical text log format while also supporting JSON output, dynamic level changes, caller detection, extra destinations, and handler overrides for syslog/systemd/Event Log integration.

## Important APIs, types, and functions
Key exports are global `Handler`, `OutputHandler`, `NewOutputHandler`, and methods `SetOutput`, `ResetOutput`, `AddOutput`, `SetLevel`, `Enabled`, `Handle`, `WithAttrs`, and `WithGroup`. Important helpers include `defaultHandler`, `slogLevelToString`, `mapLogLevelNames`, `isLogFrame`, `getCaller`, `formatStdLogHeader`, `textLog`, and `jsonLog`.

## Control flow
`defaultHandler` creates a stderr handler and installs it into `fs.SetLogger` without changing process default slog. `Handle` snapshots format flags, builds text and/or JSON buffers depending on main and extra outputs, then writes to the override output stack or base writer and mirrors to extra destinations. Text formatting builds date/time/microsecond/UTC/file/PID/level/object prefixes. JSON formatting adds source and optional PID attributes.

## State and persistence behavior
`OutputHandler` stores writer, format flags, level variable, override stack, extra outputs, mutex, JSON buffer, and JSON handler. All mutable handler state is protected by `mu`. Persistence depends on the writer/output functions supplied by `InitLogging`.

## Dependencies and integration points
Core `fs/log.go` sends records to this handler. `log.go` mutates `Handler` during `InitLogging`; syslog/systemd/Event Log files use `SetOutput` or `AddOutput`. The handler implements `slog.Handler` for standard library compatibility.

## Risks and edge cases
Caller detection must skip rclone and standard-library logging frames, including `-trimpath` paths. `WithAttrs` and `WithGroup` intentionally ignore attrs/groups, which may surprise generic slog users. JSON and text buffers are both built when different destinations need different formats. Incorrect locking could deadlock under concurrent logging and reconfiguration.

## Test signals
`slog_test.go` covers level-name mapping, attr replacement, caller-frame skipping, text header variants, level enabling, format flag mutation, output override/reset, extra text/JSON outputs, JSON PID, handler cloning, direct text/JSON generation, concurrent reconfiguration/logging, and JSON-versus-text handling.

Source-read signal: reviewed complete local file (439 lines). Types observed: `OutputHandler`, `outputExtra`, `outputFn`. Functions/methods observed: `defaultHandler`, `slogLevelToString`, `mapLogLevelNames`, `isLogFrame`, `getCaller`, `getFormat`, `NewOutputHandler`, `SetOutput`, `ResetOutput`, `AddOutput`, `SetLevel`, `setWriter`, `setFormat`, `clearFormatFlags`, `setFormatFlags`, `Enabled`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/slog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/slog_test.go -->
# sources/user-network-fs/rclone/fs/log/slog_test.go

## Purpose
`slog_test.go` is the unit and concurrency test suite for rclone's custom slog `OutputHandler`.

## Important APIs, types, and functions
Tests cover `slogLevelToString`, `mapLogLevelNames`, `getCaller`, `isLogFrame`, `NewOutputHandler`, `formatStdLogHeader`, `Enabled`, `clearFormatFlags`, `setFormatFlags`, `SetOutput`, `ResetOutput`, `AddOutput`, `Handle`, `WithAttrs`, `WithGroup`, `textLog`, and `jsonLog`.

## Control flow
The suite uses a fixed timestamp and buffers to assert exact or prefix/suffix output. It constructs records with levels and attrs, runs handler methods, and checks text or JSON output. `TestOutputHandlerConcurrency` launches goroutines that simultaneously call `Handle`, mutate formats, mutate level, override outputs, and clone handlers, then fails on timeout to catch deadlocks.

## State and persistence behavior
All test state is in-memory buffers, fixed time values, and goroutine synchronization. No log files or OS logging systems are used.

## Dependencies and integration points
The tests use Go `log/slog`, runtime frame data, regex, time zones, and rclone `fs` slog levels. They protect the handler used by all rclone logging entry points and the platform output adapters.

## Risks and edge cases
Exact formatting expectations are sensitive to level field width, PID inclusion, UTC conversion, JSON attribute names, and caller source paths. Concurrency coverage is timeout-based, so it catches deadlocks more than subtle data races unless run with `-race`.

## Test signals
Coverage is broad and directly targets the most failure-prone handler code: mixed JSON/text destinations, output override stacks, frame skipping under trimpath, dynamic format changes, and concurrent logging/reconfiguration.

Source-read signal: reviewed complete local file (402 lines). Functions/methods observed: `TestSlogLevelToString`, `TestMapLogLevelNames`, `TestGetCaller`, `TestIsLogFrame`, `TestFormatStdLogHeader`, `TestEnabled`, `TestClearSetFormatFlags`, `TestSetResetOutput`, `TestAddOutput`, `TestAddOutputJSON`, `TestAddOutputUseJSONLog`, `TestJSONLogWithPid`, `TestWithAttrsAndGroup`, `TestTextLogAndJsonLog`, `TestOutputHandlerConcurrency`, `TestHandleFormatFlags`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/slog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/syslog.go -->
# sources/user-network-fs/rclone/fs/log/syslog.go

## Purpose
`syslog.go` is the unsupported-platform stub for syslog integration.

## Important APIs, types, and functions
The single function is `startSysLog(handler *OutputHandler) bool`, compiled for Windows, NaCl, and Plan 9. It calls `fs.Fatalf` with a platform-specific unsupported message and returns false only for compile-time completeness.

## Control flow
When `--syslog` is configured on unsupported platforms, `InitLogging` calls this stub and the process exits via fatal logging.

## State and persistence behavior
No syslog state is created and no persistence occurs beyond the fatal log/exit.

## Dependencies and integration points
It depends on `runtime` and rclone `fs.Fatalf`. The signature matches `syslog_unix.go`.

## Risks and edge cases
The explicit fatal avoids silently logging to the wrong sink when users request syslog. Library users should avoid enabling syslog on these platforms unless they expect process exit.

## Test signals
No direct tests are present. Build tags and platform CLI tests are the relevant coverage.

Source-read signal: reviewed complete local file (17 lines). Functions/methods observed: `startSysLog`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/syslog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/syslog_unix.go -->
# sources/user-network-fs/rclone/fs/log/syslog_unix.go

## Purpose
`syslog_unix.go` implements syslog output on supported Unix-like platforms.

## Important APIs, types, and functions
Important items are `syslogFacilityMap` and `startSysLog(handler *OutputHandler) bool`. The map translates facility strings such as `DAEMON`, `LOCAL0`, and `AUTHPRIV` to `syslog.Priority` values.

## Control flow
`startSysLog` validates `Opt.SyslogFacility`, opens a syslog writer with program basename, strips date/time/file/PID format flags, forces no textual level prefix, and installs a handler output function. That function maps slog/rclone levels to syslog methods such as `Emerg`, `Alert`, `Crit`, `Err`, `Warning`, `Notice`, `Info`, and `Debug`.

## State and persistence behavior
The syslog writer is captured in a closure stored as the handler output. Log records persist through the system syslog service. Handler format/output state is mutated globally.

## Dependencies and integration points
It uses Go `log/syslog`, `os.Args`, `path.Base`, rclone levels, and `OutputHandler`. `InitLogging` calls it when `Opt.UseSyslog` is set and rejects simultaneous log-file output.

## Risks and edge cases
Unknown facilities and syslog open failures are fatal. The writer is not explicitly closed here. Format mutation changes global handler behavior. Syslog availability varies by Unix platform and runtime environment.

## Test signals
No direct test is present in this subset. Manual or integration testing should cover facility validation, level mapping, and environments without a syslog daemon.

Source-read signal: reviewed complete local file (75 lines). Functions/methods observed: `startSysLog`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/syslog_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/systemd.go -->
# sources/user-network-fs/rclone/fs/log/systemd.go

## Purpose
`systemd.go` is the unsupported-platform stub for systemd journal logging.

## Important APIs, types, and functions
It implements `startSystemdLog(handler *OutputHandler) bool` and `isJournalStream() bool` for `!unix` builds. `startSystemdLog` fatal-exits when configured; `isJournalStream` returns false.

## Control flow
`InitLogging` may call `isJournalStream` for autodetection and `startSystemdLog` when systemd logging is requested. On non-Unix builds autodetection is disabled and explicit enablement is fatal.

## State and persistence behavior
There is no state and no journal output on these platforms.

## Dependencies and integration points
The stub depends on `runtime` and rclone `fs.Fatalf`. It matches the Unix implementation's API so `log.go` remains portable.

## Risks and edge cases
Explicit `--log-systemd` is not silently ignored; it terminates on unsupported platforms. This is appropriate for CLI clarity but can surprise embedded callers.

## Test signals
No direct test is present. Build coverage verifies the stub compiles.

Source-read signal: reviewed complete local file (21 lines). Functions/methods observed: `startSystemdLog`, `isJournalStream`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/systemd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/systemd_unix.go -->
# sources/user-network-fs/rclone/fs/log/systemd_unix.go

## Purpose
`systemd_unix.go` implements systemd journal output and journal-stream autodetection for Unix builds.

## Important APIs, types, and functions
Exports within the package are `startSystemdLog`, `slogLevelToSystemdPriority`, and `isJournalStream`. `slogLevelToSystemdPrefix` maps rclone/slog levels to `journal.Priority` values.

## Control flow
When enabled, `startSystemdLog` strips standard timestamp/file/PID format flags, forces no text level prefix, and replaces the handler output with a function that calls `journal.Print` using the mapped priority and formatted level/text. `isJournalStream` delegates to `journal.StderrIsJournalStream` for autodetection.

## State and persistence behavior
The handler output is redirected process-wide to journald. Log records persist according to systemd journal configuration. No local files are created by this file.

## Dependencies and integration points
It depends on `github.com/coreos/go-systemd/v22/journal`, `log/slog`, rclone levels, and `OutputHandler`. `InitLogging` calls it when `--log-systemd` is set or when stderr is detected as a journal stream and output is not redirected elsewhere.

## Risks and edge cases
Unknown slog levels default to info priority. `journal.Print` errors are ignored. Handler format mutation affects all subsequent logging. Autodetection only checks stderr and is bypassed when logs are redirected to file/syslog.

## Test signals
No direct test is present in this subset. Manual systemd-run/journalctl checks are needed for full behavior.

Source-read signal: reviewed complete local file (48 lines). Functions/methods observed: `startSystemdLog`, `slogLevelToSystemdPriority`, `isJournalStream`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log/systemd_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log_test.go -->
# sources/user-network-fs/rclone/fs/log_test.go

## Purpose
`log_test.go` tests core logging value and log-level parsing behavior from `fs/log.go`.

## Important APIs, types, and functions
The tests cover `LogValue`, `LogValueHide`, `LogValueItem.String`, `LogLevel.String`, `LogLevel.Set`, and JSON unmarshalling into `LogLevel`. Interface checks assert `LogLevel` satisfies rclone flag interfaces and `LogValueItem` satisfies `fmt.Stringer`.

## Control flow
`TestLogValue` compares visible and hidden rendering, including a value implementing `String()`. Level tests are table-driven for valid names, unknown names, numeric JSON values, invalid JSON strings, and out-of-range numbers.

## State and persistence behavior
No persistent state is used. Tests only construct values and unmarshal JSON in memory.

## Dependencies and integration points
The suite depends on `encoding/json`, `strconv`, testify, and rclone's enum/flag support. It protects CLI/config parsing for `--log-level` and structured logging argument rendering.

## Risks and edge cases
Hidden log values returning empty strings is important for text logs while still allowing structured fields elsewhere. JSON numeric parsing must reject invalid and out-of-range values rather than silently accepting bad log levels.

## Test signals
Coverage is focused on parsing and rendering; it does not test actual log emission, fatal/panic behavior, or handler integration, which are covered elsewhere or by integration tests.

Source-read signal: reviewed complete local file (95 lines). Types observed: `withString`. Functions/methods observed: `String`, `TestLogValue`, `TestLogLevelString`, `TestLogLevelSet`, `TestLogLevelUnmarshalJSON`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/logger/logger.go -->
# sources/user-network-fs/rclone/fs/logger/logger.go

## Purpose
`logger.go` provides the testscript entry point for rclone logger-related CLI tests. It builds a test executable function with all backends, commands, and plugins imported.

## Important APIs, types, and functions
The single public API is `Main()`, which delegates to `cmd.Main()`. Blank imports register `backend/all`, `cmd/all`, and `lib/plugin`.

## Control flow
`logger_test.go` registers `logger.Main` under the command name `rclone` for the `testscript` framework. When a script invokes `rclone`, control enters `cmd.Main` with the current testscript process environment.

## State and persistence behavior
This file itself stores no state. Runtime state is whatever `cmd.Main` and registered backends/commands create under testscript's temporary work directories.

## Dependencies and integration points
It integrates rclone's command package with `rogpeppe/go-internal/testscript`. The broad blank imports ensure script tests see the normal CLI command/backend registry.

## Risks and edge cases
Importing all backends/commands can increase test startup cost and pull in global init behavior. The package is test-support-oriented and should not be used as a production abstraction.

## Test signals
`logger_test.go` uses this entry point to execute scripts under `testdata/script`, giving end-to-end CLI coverage for sync/bisync logger behavior.

Source-read signal: reviewed complete local file (16 lines). Functions/methods observed: `Main`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/logger/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/logger/logger_test.go -->
# sources/user-network-fs/rclone/fs/logger/logger_test.go

## Purpose
`logger_test.go` drives CLI-level logger tests through the `testscript` framework, excluding Plan 9 via build tag.

## Important APIs, types, and functions
`TestMain` registers a synthetic `rclone` command backed by `logger.Main`. `TestLogger` calls `testscript.Run` with `Dir: "testdata/script"` and a setup hook that defines `SRC` and `DST` environment variables under `$WORK`.

## Control flow
The testscript framework runs each script file in the script directory. Scripts can call `rclone`, create files, compare outputs, and use the `SRC`/`DST` directories prepared by setup.

## State and persistence behavior
All filesystem state should live under testscript's `$WORK` temporary directory. Environment variables are set per script environment. No repository files are modified by normal runs.

## Dependencies and integration points
The test depends on `logger.Main`, `testscript`, and rclone's full CLI registry. It is an end-to-end integration point for logging behavior that is difficult to validate with unit tests alone.

## Risks and edge cases
Script outcomes depend on script contents not shown in this subset. Because it imports and runs the real CLI, failures can arise from unrelated backend/command initialization. Plan 9 is excluded, likely due to script or filesystem semantics.

## Test signals
The file signals the presence of black-box CLI regression tests for sync/bisync logger behavior, with source/destination paths isolated in temporary directories.

Source-read signal: reviewed complete local file (34 lines). Functions/methods observed: `TestMain`, `TestLogger`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/logger/logger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/march/march.go -->
# sources/user-network-fs/rclone/fs/march/march.go

## Purpose
`march.go` traverses source and destination filesystems in lock step. It is the matching engine used by sync-like operations to classify entries as source-only, destination-only, or matched, with support for filters, fast-list, no-traverse, depth limits, case-insensitive comparison, Unicode normalization, and concurrent directory processing.

## Important APIs, types, and functions
Core APIs are `March`, `Marcher`, and `March.Run`. `Marcher` callbacks are `SrcOnly`, `DstOnly`, and `Match`. Important internals include `init`, `srcOrDstKey`, `makeListDir`, `listDirJob`, `matchListings`, and `processJob`. `matchTransformFn` and `listDirFn` customize matching and listing.

## Control flow
`Run` initializes list functions and transforms, computes source/destination depth, starts checker worker goroutines, queues the root job, and waits for traversal completion. `processJob` lists source and destination directories concurrently or, in no-traverse mode, probes destination objects by name for each source object. `matchListings` merges sorted streams, skips duplicates, validates order, and dispatches callbacks. Callback return values enqueue child-directory jobs when depth allows.

## State and persistence behavior
`March` holds runtime listing functions, transforms, a semaphore limiting destination `NewObject` probes, and traversal queues. It does not directly mutate remotes; callback implementations perform sync/delete/copy behavior. It updates error counts through `fs.CountError` when listing fails.

## Dependencies and integration points
It integrates `fs.Fs`, `fs.DirEntry`, filters, `list.DirSortedFn`, `walk.NewDirTree` for fast-list/files-from no-traverse modes, `dirtree`, transform rules, `semaphore`, Unicode NFC normalization, and config fields such as `Checkers`, `UseListR`, `NoTraverse`, `MaxDepth`, `IgnoreCaseSync`, and `DeleteExcluded`.

## Risks and edge cases
Concurrency is subtle: job queue accounting, context cancellation, background no-traverse probes, and channel closure must avoid deadlocks. Duplicate handling depends on stable sorting and transformed keys. Directories sort before files by suffix. `NoCheckDest` treats destination as absent. If destination listings fail with `ErrorDirNotFound`, source items are copied anyway.

## Test signals
`march_test.go` covers source-only, identical, typical sync, no-traverse, fast-list, duplicate entries, case-insensitive matching, Unicode normalization, file-versus-directory distinctions, and local backend monkey-patched ListR behavior.

Source-read signal: reviewed complete local file (556 lines). Types observed: `matchTransformFn`, `listDirFn`, `March`, `Marcher`, `listDirJob`, `matchTask`. Functions/methods observed: `init`, `srcOrDstKey`, `srcKey`, `dstKey`, `makeListDir`, `Run`, `aborting`, `matchListings`, `processJob`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/march/march.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/march/march_test.go -->
# sources/user-network-fs/rclone/fs/march/march_test.go

## Purpose
`march_test.go` validates the lock-step traversal and matching behavior in `march.go` using local/mock filesystems and direct matching tests.

## Important APIs, types, and functions
The suite defines `marchTester`, which implements `Marcher`, and tests `March.Run`, `matchListings`, source/destination callbacks, error classification helpers, and transform-aware matching. It uses `fstest.Run`, local backend registration, `walk.ListR`, `list.NewSorter`, mock dirs/objects, and Unicode normalization.

## Control flow
`TestMarch` builds source-only, destination-only, and matched files/directories for several scenarios, configures no-traverse or fast-list, runs a `March`, and compares callback-collected entries against expected items. `TestMatchListings` constructs interleaved source/destination inputs, sorts them through `list.Sorter`, calls `matchListings`, and checks src-only, dst-only, and match outputs for duplicates, case transforms, Unicode transforms, and file/dir collisions.

## State and persistence behavior
Integration-style cases create temporary local/remote test files through `fstest.NewRun`. The tester stores callback entries and error state protected by mutexes. Fast-list tests temporarily monkey-patch local backend `ListR` and restore it.

## Dependencies and integration points
The tests exercise `march` together with `list.Sorter`, `walk.ListR`, filter config, local backend, mock object/dir packages, and rclone error classification. They reflect real sync traversal behavior more closely than isolated unit tests.

## Risks and edge cases
No-traverse matching only probes objects, not directories. Duplicate handling under transforms keeps the first stable-sorted entry. Unicode-equivalent names can collapse depending on normalization. The test comment says “swap src and dst” but repeats the same channel construction, so it mainly reruns the same assertion.

## Test signals
Coverage is strong for primary traversal modes, recursion decisions, depth behavior through directories, fast-list integration, transformed matching, duplicate skipping, and file/directory ordering semantics.

Source-read signal: reviewed complete local file (555 lines). Types observed: `marchTester`, `matchPair`. Functions/methods observed: `TestMain`, `DstOnly`, `SrcOnly`, `Match`, `processError`, `currentError`, `aborting`, `TestMarch`, `TestMatchListings`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/march/march_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/metadata.go -->
# sources/user-network-fs/rclone/fs/metadata.go

## Purpose
`metadata.go` defines rclone's generic metadata map type and helpers for reading, merging, option injection, and external metadata mapping. It standardizes how operations pass object metadata between backends.

## Important APIs, types, and functions
Exports are `Metadata`, `MetadataHelp`, `MetadataInfo`, methods `Set`, `Merge`, `MergeOptions`, `GetMetadata`, and `GetMetadataOptions`. Internal `mapItem` defines the JSON contract for mapper programs, and `metadataMapper` runs the configured external mapper command.

## Control flow
`GetMetadataOptions` returns nil unless global `Metadata` is enabled. It reads metadata from a `Metadataer` object when available, merges any `MetadataOption` open options, and optionally calls `metadataMapper`. The mapper builds a JSON object with source/destination fs identifiers, remote, size, MIME type, modtime, directory flag, optional ID, and metadata; sends it to stdin; reads JSON from stdout; and returns the output metadata.

## State and persistence behavior
Metadata maps are in-memory. The external mapper can have arbitrary side effects, but this code only starts a subprocess and passes JSON. Config controls whether metadata and mapper execution are active. Dump flags can log mapper input/output.

## Dependencies and integration points
It depends on core interfaces `DirEntry`, `Metadataer`, `IDer`, `Fs`, `OpenOption`, `MetadataOption`, `MimeType`, config `MetadataMapper`, and OS command execution. Backends use these helpers in Put/Update/Copy paths.

## Risks and edge cases
Mapper execution is synchronous and can be slow, fail, or emit invalid JSON. Metadata is merged with options after reading object metadata, so options override duplicate keys. `mapItem.IsDir` is always false in this function despite accepting `DirEntry`, which may matter for directory metadata. Error messages include stderr and stdout snippets.

## Test signals
`metadata_test.go` covers map set/merge semantics, open-option merge precedence, normal mapper transformation, mapper failure via stderr/exit, and option-overridden mapper input.

Source-read signal: reviewed complete local file (172 lines). Types observed: `Metadata`, `MetadataHelp`, `MetadataInfo`, `mapItem`. Functions/methods observed: `Set`, `Merge`, `MergeOptions`, `GetMetadata`, `metadataMapper`, `GetMetadataOptions`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/metadata_mapper_code.go -->
# sources/user-network-fs/rclone/fs/metadata_mapper_code.go

## Purpose
`metadata_mapper_code.go` is a build-ignored helper program used by `metadata_test.go` to exercise the external metadata mapper protocol.

## Important APIs, types, and functions
The program defines a generic `check` helper and `main`. It reads JSON from stdin into `map[string]any`, validates selected fields, transforms `Metadata`, and writes a JSON object containing mapped metadata.

## Control flow
`main` decodes input, requires `Metadata`, checks expected `Size`, `SrcFs`, `SrcFsType`, `DstFs`, `DstFsType`, `Remote`, `MimeType`, `ModTime`, and `IsDir`, then iterates metadata. Key `error` triggers stderr output and exit status 1; `key1` is prefixed with `two `; `key3` is dropped; `key0=cabbage` is added. Output is JSON-encoded on stdout.

## State and persistence behavior
The helper has no persistent state. It communicates only through stdin/stdout/stderr and process exit code.

## Dependencies and integration points
It is invoked by `go run metadata_mapper_code.go` from tests through `fs.MetadataMapper`. It defines the expected JSON shape produced by `metadata.go`'s mapper path.

## Risks and edge cases
The helper uses type assertions against `any` values, so mismatched JSON types panic or exit. It checks exact strings and float size representation, making it sensitive to mapper contract changes. The final `if err != nil` after encoding is stale because `err` was not reassigned from `Encode`.

## Test signals
Although not part of normal builds, it is central to `TestMetadataMapper`: successful transformation, error propagation, and metadata-option override behavior all run through this helper.

Source-read signal: reviewed complete local file (74 lines). Functions/methods observed: `check`, `main`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/metadata_mapper_code.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/metadata_test.go -->
# sources/user-network-fs/rclone/fs/metadata_test.go

## Purpose
`metadata_test.go` validates generic metadata map operations and the external metadata mapper integration.

## Important APIs, types, and functions
Tests cover `fs.Metadata.Set`, `Merge`, `MergeOptions`, `GetMetadataOptions`, `MetadataOption`, and mapper execution configured via `ci.MetadataMapper.Set("go run metadata_mapper_code.go")`. It uses `object.NewMemoryObject` and `mockfs.NewFs`.

## Control flow
Map tests run table-driven nil/empty/non-empty merge cases and option precedence. Mapper tests enable metadata in config, build a destination mock fs and memory object with metadata, then check normal mapped output, mapper error propagation when metadata includes `error`, and option merge overriding object metadata before mapping.

## State and persistence behavior
The tests create in-memory metadata and objects. Mapper tests spawn `go run`, which compiles/runs the helper process, but do not persist repository data. Config is context-local via `fs.AddConfig`.

## Dependencies and integration points
The suite depends on `metadata_mapper_code.go`, memory objects, mock fs, config parsing for `SpaceSepList`, and MIME type detection. It protects copy/upload metadata flows that rely on `GetMetadataOptions`.

## Risks and edge cases
Mapper tests assume `go` is available and that running from the package directory can find `metadata_mapper_code.go`. Exact mapper field checks make tests sensitive to source fs identity, MIME detection, and timestamp formatting.

## Test signals
Coverage is high for local metadata semantics: nil preservation, duplicate key override rules, non-metadata options ignored, external mapper success/failure, and option metadata overriding object metadata.

Source-read signal: reviewed complete local file (157 lines). Functions/methods observed: `TestMetadataSet`, `TestMetadataMerge`, `TestMetadataMergeOptions`, `TestMetadataMapper`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/mimetype.go -->
# sources/user-network-fs/rclone/fs/mimetype.go

## Purpose
`mimetype.go` provides MIME type detection helpers for rclone directory entries and augments Go's built-in extension database with common media extensions on platforms lacking a rich `mime.types`.

## Important APIs, types, and functions
Exports are `MimeTypeFromName`, `MimeType`, and `MimeTypeDirEntry`. The package `init` registers fallback MIME types for audio, image, video, and subtitle extensions when `mime.TypeByExtension` lacks them.

## Control flow
At init, each comma-separated extension is registered only if Go has no type for it. `MimeTypeFromName` checks `path.Ext` and returns `application/octet-stream` unless the result contains `/`. `MimeType` prefers an object's `MimeTyper` implementation when non-empty, then falls back to filename. `MimeTypeDirEntry` returns `inode/directory` for directories and delegates to `MimeType` for objects.

## State and persistence behavior
The process-global MIME extension table is mutated during package init. No files are read or written by this code.

## Dependencies and integration points
It depends on Go `mime`, `path`, and rclone interfaces `DirEntry`, `Object`, `Directory`, and `MimeTyper`. Metadata mapping and backend uploads use these helpers to infer content type.

## Risks and edge cases
MIME type registration is global and can affect other packages in-process. Extension matching is filename-based and not content-sniffing. If a `MimeTyper` returns an invalid but non-empty type, this helper trusts it.

## Test signals
No direct test is in this subset. Metadata mapper tests indirectly assert `file.txt` produces `text/plain; charset=utf-8`.

Source-read signal: reviewed complete local file (81 lines). Functions/methods observed: `init`, `MimeTypeFromName`, `MimeType`, `MimeTypeDirEntry`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/mimetype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/mount_helper.go -->
# sources/user-network-fs/rclone/fs/mount_helper.go

## Purpose
`mount_helper.go` converts Linux/Unix mount-helper invocation syntax into normal rclone command-line arguments. It lets rclone run as `mount.rclone` or `rclonefs` and parse `-o` option strings from `/bin/mount`, fusermount, or systemd mount units.

## Important APIs, types, and functions
Exports are `PassDaemonArgsAsEnviron` and `IsMountHelper`. Internal core functions are `convertMountHelperArgs` and `parseHelperOptionString`. Constants define ignored standard mount options and valid option-name characters; sentinel errors describe parser failures.

## Control flow
Package init detects mount-helper executable names early and rewrites `os.Args` unless already daemonized. `convertMountHelperArgs` scans original args, accepts `-o`/`--opt`, verbosity flags, and help, rejects other flags, parses option strings, ignores standard mount/systemd options, sets `env.NAME=value` environment variables, handles `command`, `args2env`, verbosity, `daemon`, `verbose`, and `ro`, converts remaining options to `--kebab-case` flags, defaults mount commands to `--daemon`, and returns `[argv0, command, ...]`.

## State and persistence behavior
It may mutate `os.Args`, environment variables, and `PassDaemonArgsAsEnviron`. It persists nothing to disk. `IsDaemon` integration avoids repeated conversion in daemon children.

## Dependencies and integration points
It integrates with rclone mount command startup, daemonization, config password prompt behavior, and OS mount helpers. The option parser borrows state-machine ideas from `fspath.Parse` but accepts mount-specific `env.` and `x-systemd.` prefixes.

## Risks and edge cases
This runs very early before normal configuration. Quoted option parsing, doubled quotes, dangling `-o`, unsupported flags, empty command names, and environment syntax are sensitive. `args2env` is a security feature to hide daemon args from process listings. Standard mount options must be ignored without swallowing meaningful rclone flags.

## Test signals
`mount_helper_test.go` covers empty conversion, quoted env values containing spaces/semicolons/commas, `ro`, ignored options, verbosity count, `args2env`, and default daemon insertion.

Source-read signal: reviewed complete local file (283 lines). Functions/methods observed: `init`, `IsMountHelper`, `convertMountHelperArgs`, `parseHelperOptionString`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/mount_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/mount_helper_test.go -->
# sources/user-network-fs/rclone/fs/mount_helper_test.go

## Purpose
`mount_helper_test.go` verifies representative mount-helper argument conversion and environment handling.

## Important APIs, types, and functions
The test targets unexported `convertMountHelperArgs` and indirectly `parseHelperOptionString`. It checks output args and environment side effects.

## Control flow
`TestMountHelperArgs` defines normal cases, prepends a fake executable name, calls conversion, compares the command/flags after argv0, and checks any expected environment variable assignment.

## State and persistence behavior
The test may set environment variables such as `HTTPS_PROXY` in the process environment. It does not restore them in the shown code, so test isolation relies on chosen names and process lifetime.

## Dependencies and integration points
It uses `os.Getenv`, string splitting, and testify. The covered behavior protects rclone invocation through `/bin/mount` and systemd mount option strings.

## Risks and edge cases
Coverage is narrow relative to the parser: many error paths, quote failures, command override, explicit daemon handling, and unsupported flags are not exercised. The first normal case with no args confirms default `mount --daemon` behavior.

## Test signals
The positive case is high value because it combines `x-systemd` ignore, verbosity option, quoted env value with embedded separators, read-only alias, ignored mount options, and args-to-env mode.

Source-read signal: reviewed complete local file (53 lines). Types observed: `testCase`. Functions/methods observed: `TestMountHelperArgs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/mount_helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/newfs.go -->
# sources/user-network-fs/rclone/fs/newfs.go

## Purpose
`newfs.go` constructs rclone filesystem backends from user paths. It parses remote strings, resolves backend registry entries and config maps, applies per-backend/global override parameters, tracks hashed config suffixes for remotes with extra connection-string config, and provides canonical config-string helpers.

## Important APIs, types, and functions
Exports include `WithRCRequest`, `IsRCRequest`, `NewFs`, `ConfigFs`, `ParseRemote`, `ConfigString`, `FullPath`, `ConfigStringFull`, and `TemporaryLocalFs`. Internal state includes `overriddenConfig` guarded by `overriddenConfigMu`, and `addConfigToContext` for `global.`/`override.` keys.

## Control flow
`NewFs` warns if a bare path matches a config section, calls `ConfigFs`, detects options overridden by connection-string config, computes a short base64 MD5 suffix like `{S_NHG}` when needed, stores suffix-to-config mapping, applies config overrides to context/global config, calls the backend `NewFs`, and registers reverse lookup when construction succeeds or returns `ErrorIsFile`. `ParseRemote` uses `fspath.Parse`, chooses local when no config name exists, reads configured remote type, or handles `:backend`.

## State and persistence behavior
The overridden-config suffix map is process-global and used later by `ConfigStringFull`. `global.` config overrides can mutate the process-wide background config unless the context is marked as an rc request. `TemporaryLocalFs` creates and removes a temp path before constructing a local fs there.

## Dependencies and integration points
This file integrates `fspath`, the backend registry (`Find`, `RegInfo.NewFs`), config maps/struct assignment, reverse fs registry helpers, global config options, and object path helpers. Every rclone command that opens a remote flows through this code.

## Risks and edge cases
Suffix generation must avoid collisions while producing filesystem-safe names for caches. `global.` options from normal contexts mutate global config, but rc requests must avoid cross-request leakage. Local paths can be confused with remote names, especially one-character names on Windows. `ConfigStringFull` depends on the in-memory suffix map being present.

## Test signals
`newfs_test.go` checks mock backend creation, suffix stability for equivalent extra params, canonical config strings, and global override mutation. `newfs_internal_test.go` checks override/global context behavior and rc isolation.

Source-read signal: reviewed complete local file (246 lines). Types observed: `rcRequestKeyType`. Functions/methods observed: `WithRCRequest`, `IsRCRequest`, `NewFs`, `addConfigToContext`, `ConfigFs`, `ParseRemote`, `configString`, `ConfigString`, `FullPath`, `ConfigStringFull`, `TemporaryLocalFs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/newfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/newfs_internal_test.go -->
# sources/user-network-fs/rclone/fs/newfs_internal_test.go

## Purpose
`newfs_internal_test.go` tests the internal `addConfigToContext` behavior for connection-string `override.` and `global.` config keys.

## Important APIs, types, and functions
Tests target `addConfigToContext`, `WithRCRequest`, and `GetConfig` behavior for context-local and global config mutation. `configmap.Simple` supplies synthetic keys such as `override.user_agent` and `global.user_agent`.

## Control flow
The suite covers no-change, override-only, global-only, and global-from-rc cases. It compares whether the returned context is the original or a new one, checks user-agent values on the returned context, and verifies whether the process-wide config was or was not mutated.

## State and persistence behavior
Tests mutate the global config's `UserAgent` for global-only cases and restore it with `defer`. Context-local config is created via `AddConfig`.

## Dependencies and integration points
It depends on rclone config option metadata, `configstruct.Set`, and rc request marking. It protects `NewFs` behavior for remote-control requests and ordinary CLI backend startup.

## Risks and edge cases
Global config leakage is the main risk: rc requests must not change process-wide settings, while CLI global overrides intentionally do. Tests only cover `user_agent`, so type conversion issues for other options rely on shared configstruct tests.

## Test signals
The tests provide direct regression coverage for context identity, override scoping, global mutation, and rc isolation.

Source-read signal: reviewed complete local file (77 lines). Functions/methods observed: `TestAddConfigToContext_NoChanges`, `TestAddConfigToContext_OverrideOnly`, `TestAddConfigToContext_GlobalOnly`, `TestAddConfigToContext_GlobalFromRC`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/newfs_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/newfs_test.go -->
# sources/user-network-fs/rclone/fs/newfs_test.go

## Purpose
`newfs_test.go` validates public backend construction and canonical config-string behavior through the mock filesystem backend.

## Important APIs, types, and functions
The test exercises `fs.NewFs`, `ConfigString`, `ConfigStringFull`, `GetConfig`, and mock backend registration. It temporarily replaces `fs.Registry` to isolate registry state.

## Control flow
The test registers `mockfs`, creates a plain on-the-fly mock remote, creates equivalent remotes with extra `potato` config in boolean and quoted forms, verifies the hashed suffix name and full canonical config string, then creates a remote with `global.user_agent` and checks global config mutation without suffixing.

## State and persistence behavior
The test mutates global backend registry and global config user agent, restoring both with defers. It also populates the process-global overridden-config suffix map as part of `NewFs`.

## Dependencies and integration points
It depends on `fstest/mockfs`, backend registry behavior, config option override detection, fspath parsing, and config-string reconstruction.

## Risks and edge cases
The expected suffix `{S_NHG}` is tied to the hash/canonicalization of `potato='true'`; changing canonical option formatting will break this test. Global config restoration is manual.

## Test signals
Coverage confirms basic `:backend:path` creation, suffixing for extra config, equivalence of implicit boolean and quoted true, `ConfigStringFull` reversibility, and global override application.

Source-read signal: reviewed complete local file (62 lines). Functions/methods observed: `TestNewFs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/newfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/object/object.go -->
# sources/user-network-fs/rclone/fs/object/object.go

## Purpose
`object.go` defines lightweight object implementations used by tests and internal operations: immutable `StaticObjectInfo`, an in-memory `MemoryFs`, and mutable `MemoryObject`.

## Important APIs, types, and functions
Exports include `StaticObjectInfo`, `NewStaticObjectInfo`, `WithMetadata`, `WithMimeType`, `MemoryFs`, `MemoryObject`, `NewMemoryObject`, `SetFs`, `Content`, `Open`, `Update`, and interface methods for `fs.ObjectInfo`, `fs.Object`, `fs.Metadataer`, and `fs.MimeTyper`.

## Control flow
`NewStaticObjectInfo` stores caller-provided metadata and, if hashes are nil but an fs is supplied, creates empty hash entries for every supported hash type. `MemoryFs.Put` creates a `MemoryObject` and calls `Update`. `MemoryObject.Open` interprets `RangeOption` and `SeekOption`, clamps negative offsets, and returns an `io.NopCloser` over a slice. `Update` reuses the existing buffer when known size fits capacity, otherwise reads all content; it also updates modtime.

## State and persistence behavior
All object content, metadata, MIME type, and modtime live in memory. `MemoryFs` is a package-level value but has no backing store or directory tree. No data persists across process lifetime.

## Dependencies and integration points
The package depends on core `fs` interfaces, `hash.MultiHasher`, open options, and standard I/O. It is widely useful for unit tests, metadata mapper tests, and operations needing synthetic `ObjectInfo`.

## Risks and edge cases
`MemoryObject.Open` silently logs unsupported mandatory options rather than returning an error. Negative ranges and limits are simplified. `Update` with unknown size reads all input into memory. `MemoryFs` reports all hashes supported but has no object lookup store.

## Test signals
`object_test.go` covers static object properties/hash behavior, memory fs basics, Put, in-memory hashing, range/seek open behavior, modtime updates, buffer reuse/non-reuse, streaming unknown-size update, zero-length update, and unsupported remove.

Source-read signal: reviewed complete local file (349 lines). Types observed: `StaticObjectInfo`, `memoryFs`, `MemoryObject`. Functions/methods observed: `NewStaticObjectInfo`, `WithMetadata`, `WithMimeType`, `Fs`, `Remote`, `String`, `ModTime`, `Size`, `Storable`, `Hash`, `Metadata`, `MimeType`, `Name`, `Root`, `String`, `Precision`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/object/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/object/object_test.go -->
# sources/user-network-fs/rclone/fs/object/object_test.go

## Purpose
`object_test.go` validates the behavior of the synthetic object helpers in `fs/object/object.go`.

## Important APIs, types, and functions
Tests cover `NewStaticObjectInfo`, `StaticObjectInfo.Hash`, `MemoryFs` methods, `MemoryFs.Put`, `NewMemoryObject`, `WithMimeType`, `Content`, `Hash`, `SetModTime`, `Open`, `Update`, and `Remove`.

## Control flow
`TestStaticObject` checks default fs/hashes and explicit hash maps. `TestMemoryFs` checks fs metadata methods, unsupported list/object/mkdir/rmdir behavior, and Put creating hashable content. `TestMemoryObject` reads full and partial content through range/seek options, updates content with known sizes that do and do not fit existing capacity, tests unknown-size streaming and zero-size update, and confirms remove errors.

## State and persistence behavior
All state is in-memory byte slices and timestamps. Tests deliberately keep an old content slice to assert buffer reuse or replacement behavior.

## Dependencies and integration points
The tests use rclone `fs` open options and hash constants, plus standard `bytes`/`io`. They protect helpers used across many other tests, so regressions can cascade.

## Risks and edge cases
Range behavior around negative starts, overly large ends, and seek offsets is simplified but important for callers using memory objects as test doubles. Buffer reuse assertions depend on slice capacity and content mutation details.

## Test signals
Coverage is broad for the intended fake-object semantics: object info, hash support/unsupported errors, memory fs put, range and seek reads, modtime changes, efficient update reuse, unknown size handling, zero-length content, and unsupported deletion.

Source-read signal: reviewed complete local file (196 lines). Functions/methods observed: `TestStaticObject`, `TestMemoryFs`, `TestMemoryObject`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/object/object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/open_options.go -->
# sources/user-network-fs/rclone/fs/open_options.go

## Purpose
`open_options.go` defines rclone's generic open/read options. These options let callers request HTTP ranges, seek offsets, extra HTTP headers, hash calculation limits, metadata injection, no-op placeholders, and preferred chunks.

## Important APIs, types, and functions
Core exports are `OpenOption`, `RangeOption`, `ParseRangeOption`, `RangeOption.Decode`, `FixRangeOption`, `SeekOption`, `ParseHeaders`, `MustParseHeaders`, `HTTPOption`, `HashesOption`, `NullOption`, `MetadataOption`, `MetadataAsOpenOptions`, `ChunkOption`, `OpenOptionAddHeaders`, `OpenOptionHeaders`, and `OpenOptionAddHTTPHeaders`.

## Control flow
Options expose `Header`, `String`, and `Mandatory`. `RangeOption.Header` renders RFC 7233 byte ranges; `ParseRangeOption` accepts only a single `bytes=` range; `Decode` converts inclusive ranges into offset/limit. `FixRangeOption` normalizes suffix ranges and seeks into absolute ranges when size is known, caps end offsets, and replaces ranges on zero-size files with `NullOption`. Header helpers collect non-empty option headers into maps or `http.Header`.

## State and persistence behavior
Options are plain values/slices. `FixRangeOption` mutates the supplied slice in place and may replace option objects. `MetadataAsOpenOptions` reads context config and returns metadata-set options.

## Dependencies and integration points
Backends inspect open options in `Object.Open` and upload/update methods. HTTP backends use header helpers. Local hashing uses `HashesOption`; metadata copy paths use `MetadataOption`; multipart/upload code can use `ChunkOption`.

## Risks and edge cases
Range end is inclusive, while `Decode` returns a count. `FixRangeOption` cannot normalize unknown-size objects. Suffix ranges with `End` greater than size can produce negative starts before later capping if callers pass unusual data. Multiple HTTP ranges are explicitly unsupported. `MustParseHeaders` fatal-exits on bad user input.

## Test signals
`open_options_test.go` covers range parsing errors and variants, decode math, string/header/mandatory methods for all option types, range fixing for zero/unknown/known sizes, seek conversion, and map/header construction.

Source-read signal: reviewed complete local file (368 lines). Types observed: `OpenOption`, `RangeOption`, `SeekOption`, `HTTPOption`, `HashesOption`, `NullOption`, `MetadataOption`, `ChunkOption`. Functions/methods observed: `Header`, `ParseRangeOption`, `String`, `Mandatory`, `Decode`, `FixRangeOption`, `Header`, `String`, `Mandatory`, `ParseHeaders`, `MustParseHeaders`, `Header`, `String`, `Mandatory`, `Header`, `String`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/open_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/open_options_test.go -->
# sources/user-network-fs/rclone/fs/open_options_test.go

## Purpose
`open_options_test.go` validates parsing, rendering, normalization, and header extraction for rclone open options.

## Important APIs, types, and functions
Tests cover `ParseRangeOption`, `RangeOption.Decode`, `RangeOption`, `SeekOption`, `HTTPOption`, `HashesOption`, `NullOption`, `MetadataOption`, `FixRangeOption`, `OpenOptionAddHeaders`, `OpenOptionHeaders`, and `OpenOptionAddHTTPHeaders`.

## Control flow
Range parser tests feed valid and invalid `Range` header strings. Decode tests compare offset/limit math. Option tests assert interface compliance, `String`, `Header`, and `Mandatory` values. Fix tests mutate option slices under different object sizes. Header tests collect a mixed option list into string maps and `http.Header`.

## State and persistence behavior
Tests use in-memory option slices and maps. No external state is touched.

## Dependencies and integration points
The suite depends on Go `http.Header`, rclone `hash.Set`, and testify. It protects every backend that translates open options into HTTP headers or range reads.

## Risks and edge cases
The tests capture important boundary behavior: unsupported multiple ranges, whitespace, open-ended and suffix ranges, zero-size replacement with `NullOption`, unknown-size no-op normalization, and canonical capitalization in `http.Header`.

## Test signals
Coverage is strong for all option implementations present in the file. It does not cover `ParseHeaders`, `MustParseHeaders`, `MetadataAsOpenOptions`, or `ChunkOption`, which remain residual gaps.

Source-read signal: reviewed complete local file (290 lines). Functions/methods observed: `TestParseRangeOption`, `TestRangeOptionDecode`, `TestRangeOption`, `TestSeekOption`, `TestHTTPOption`, `TestHashesOption`, `TestNullOption`, `TestMetadataOption`, `TestFixRangeOptions`, `TestOpenOptionAddHeaders`, `TestOpenOptionHeaders`, `TestOpenOptionAddHTTPHeaders`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/open_options_test.go -->
