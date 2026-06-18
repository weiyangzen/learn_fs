# subset-b-009160 research

Grouped research report for the requested restic source files. Each section preserves the source path in the title and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/tests.go -->
## sources/sync-backup/restic/internal/backend/test/tests.go

Purpose: generic backend conformance tests for every `backend.Backend` implementation wired through `Suite[C]`. Important APIs include `LoadAll`, `beTest`, `store`, `testLoad`, `delayedRemove`, `delayedList`, and suite methods covering config, load, list, save, error, hash, full backend behavior, and delete. Control flow opens a backend, writes known/random pack-like data, exercises `Save`, `Load`, `Stat`, `List`, `Remove`, `Delete`, and checks backend error classifiers. State is remote/backend object state, with delayed deletion polling for eventually consistent stores. Dependencies include `backend`, `restic.ID`, `errgroup`, and restic test helpers. Integration risk is high: these tests define the contract for pagination, range reads, context cancellation, consumer error propagation, reader ownership, incomplete upload rejection, optional external hash validation, and cleanup semantics. Test signals are this file itself; failures usually indicate a backend contract regression rather than unit-only breakage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/tests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/defaults.go -->
## sources/sync-backup/restic/internal/backend/util/defaults.go

Purpose: shared default implementations for backend helpers. APIs: `DefaultLoad` adapts an `openReader` function to `Backend.Load`, always closing the `io.ReadCloser`; `DefaultDelete` removes all restic object types and config from a backend without deleting the bucket/container itself. Control flow in `DefaultLoad` opens the reader, calls the consumer, closes on both success and consumer error, and preserves the primary consumer error. `DefaultDelete` lists each file type and removes listed handles, then removes config while ignoring not-exist. State and persistence behavior are direct backend mutations. Dependencies are `context`, `io`, and `internal/backend`. Risks: `DefaultDelete` currently returns nil on list error inside the type loop, which can mask delete failures; callers rely on backend `IsNotExist` semantics for config cleanup. Tests in `defaults_test.go` cover `DefaultLoad`, but not `DefaultDelete`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/defaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/defaults_test.go -->
## sources/sync-backup/restic/internal/backend/util/defaults_test.go

Purpose: unit tests for `util.DefaultLoad`. APIs under test are the `DefaultLoad` callback contract and a local `mockReader` implementing `Read` and `Close`. Control flow validates the happy path passes handle, length, and offset to `openReader`, passes the exact reader to the consumer, and closes after success. Error cases verify producer errors skip consumer invocation and consumer errors still close the reader while returning the consumer error. State is limited to `mockReader.closed`. Dependencies include `backend.Handle`, `util.DefaultLoad`, wrapped restic errors, and internal test equality helpers. Risk coverage is narrow but important: it protects reader lifecycle and error precedence. Missing signal: there is no direct coverage for `DefaultDelete` deletion/list error behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/defaults_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/limited_reader.go -->
## sources/sync-backup/restic/internal/backend/util/limited_reader.go

Purpose: tiny adapter that combines an `io.LimitedReader` with the original `io.Closer`. APIs: `LimitedReadCloser` embeds `io.Closer` and `io.LimitedReader`; `LimitReadCloser(r, n)` returns a reader capped to `n` bytes while preserving close capability. Control flow is delegated to the embedded standard-library types. State is the mutable `LimitedReader.N`, which decreases as reads occur, plus the underlying reader state. Dependencies are only `io`. Integration points are backend range/load implementations that need to expose a bounded `io.ReadCloser`. Risks are standard wrapper risks: callers must close it, and repeated reads after `N` reaches zero return EOF without closing the source. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/limited_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/paths.go -->
## sources/sync-backup/restic/internal/backend/util/paths.go

Purpose: centralizes default permissions for file-oriented backends. APIs: `Modes{Dir, File}`, `DefaultModes` as `0700` directories and `0600` files, and `DeriveModesFromFileInfo(fi, err)` to infer group-readable/writable modes from an existing file. Control flow returns defaults on prior stat error, then adds group directory bits `0070` and file bits `0060` when the existing file has group read permission. State is not persisted here; returned modes guide later filesystem creation. Dependencies are `os.FileInfo` and `os.FileMode`. Integration points are local/SFTP-like backends that preserve repository accessibility modes. Risks: only group-read is inspected, so unusual ACLs or execute-only modes are not represented; callers must still apply umask/platform behavior. No direct tests are listed.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/util/paths.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/watchdog_roundtriper.go -->
## sources/sync-backup/restic/internal/backend/watchdog_roundtriper.go

Purpose: HTTP transport wrapper that cancels stalled uploads, response processing, or downloads. APIs: `newWatchdogRoundtripper`, `watchdogRoundtripper.RoundTrip`, `newWatchdogReadCloser`, `watchdogReadCloser.Read`, and `Close`; sentinel `errRequestTimeout`. Control flow creates a cancellable request context and timer, wraps request bodies and response bodies so each chunk of progress resets the timer, and maps context-canceled errors caused by watchdog expiry to `errRequestTimeout`. `watchdogReadCloser` reads in bounded chunks, calls `kick` after successful reads, and invokes a close callback once EOF or timeout occurs. State is per-request timer and atomic timeout flag. Dependencies include `net/http`, `context`, `io`, atomics, and time. Risks: callers must not pause long between response reads; timer reset races are subtle; timeout classification depends on context cancellation. Tests cover read chunking, canceled requests, upload, processing, and download timeout.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/watchdog_roundtriper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/watchdog_roundtriper_test.go -->
## sources/sync-backup/restic/internal/backend/watchdog_roundtriper_test.go

Purpose: validates watchdog transport timeout and progress semantics. Important tests: `TestRead`, `TestRoundtrip`, `TestCanceledRoundtrip`, `TestUploadTimeout`, `TestProcessingTimeout`, and `TestDownloadTimeout`; `slowReader` simulates stalled streams. Control flow uses local HTTP test servers and custom bodies to assert timer kicks during chunked reads, response bodies are closed on EOF, explicit context cancellation remains `context.Canceled`, and watchdog-triggered stalls become `errRequestTimeout`. State is in local counters, closed flags, server-side delayed reads/writes, and per-test contexts. Dependencies include `net/http`, `httptest`, the watchdog wrapper, and standard IO/time helpers. Risks tested are the highest-risk areas: upload stalls, server processing delays before response, and response body stalls. Remaining fragility is timing-based tests, so timeouts must balance speed with scheduler variance.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/watchdog_roundtriper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/bloblru/cache.go -->
## sources/sync-backup/restic/internal/bloblru/cache.go

Purpose: concurrent fixed-size LRU cache for blob contents, optimized by retained buffer capacity rather than slice length. APIs: `New`, private `add`, private `get`, public `GetOrCompute`, and eviction callback `evict`; `overhead` estimates per-entry memory. Control flow checks cache, coordinates concurrent cache misses through `inProgress` channels so only one goroutine computes a blob, retries cache lookup after waiting, then caches successful results. State is protected by `mu`: simplelru entries, free byte budget, max size, and in-progress miss map. Dependencies include `hashicorp/golang-lru/simplelru`, `restic.ID`, and debug logging. Integration points are dump/read paths needing blob reuse. Risks: `New(size)` panics for size too small to allow an LRU entry; memory accounting uses `cap(blob)` plus an estimate; failed computes are not cached. Tests cover eviction, oversize rejection, buffer identity, error propagation, and concurrent single-compute behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/bloblru/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/bloblru/cache_test.go -->
## sources/sync-backup/restic/internal/bloblru/cache_test.go

Purpose: unit and benchmark coverage for the blob LRU cache. APIs under test are `New`, `add`, `get`, and `GetOrCompute`, including private methods because the test is in package `bloblru`. Control flow fills the cache with slices whose length is small but capacity is large, confirming capacity-based memory accounting and LRU eviction; it then tests oversize blobs are ignored and evictions restore `free`. `TestCacheGetOrCompute` checks compute errors are returned, cached values reuse the original buffer, cached hits do not recompute, and ten concurrent callers for the same ID trigger one compute call. State observed includes cache contents, free byte budget, and in-progress coordination. Dependencies include `errgroup`, `restic.ID`, and test helpers. Risk coverage is strong for concurrency and memory accounting; benchmarks exercise repeated `add` throughput.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/bloblru/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/checker/checker.go -->
## sources/sync-backup/restic/internal/checker/checker.go

Purpose: high-level repository consistency checker layered on `repository.Checker`. APIs: `Checker`, `New`, `LoadSnapshots`, `IsFiltered`, `Structure`, `UnusedBlobs`, `ReadPacks`, and error types `Error`/`TreeError`. Control flow memorizes snapshot listing, chooses all or filtered snapshot root trees, streams trees via `data.StreamTrees`, validates node structure and referenced blob presence in the index, tracks referenced tree/data blobs when needed, and reports errors through channels. `ReadPacks` passes through for unfiltered runs or narrows pack reads to packs containing referenced blobs for filtered checks. State includes repository index view, associated blob set `blobRefs`, snapshot filter args, and `trackUnused`. Dependencies include `data`, `repository`, `restic`, `debug`, and wrapped errors. Risks: correctness relies on complete tree iteration before subtree collection, consistent index lookup, lock discipline around `blobRefs`, and filtered checks forcing unused tracking. Tests cover corrupt packs/index/data, duplicate trees, blob type confusion, and scaling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/checker/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/checker/checker_test.go -->
## sources/sync-backup/restic/internal/checker/checker_test.go

Purpose: integration tests for repository checker failure modes using tarred test repositories and synthetic backends. APIs exercised include checker construction, `LoadIndex`, `LoadSnapshots`, `Packs`, `Structure`, `UnusedBlobs`, and `ReadPacks`. Control flow extracts test repositories, mutates pack/index/data conditions, collects channel-reported errors, and asserts expected hints/errors. Helper repositories inject read errors, one-time corrupted data, duplicate load prevention, and delayed loads. State includes fixture repositories, modified backend objects, synthetic blob load behavior, and checker blob reference tracking. Dependencies span backend wrappers, repository test helpers, restic IDs, data snapshots, and checker package. Risks covered: missing packs, unreferenced packs/blobs, modified indexes and data, duplicate pack index entries, duplicate tree decode avoidance, data/tree blob type confusion, and performance scaling. Test signal is broad and high-value because it exercises repository-level behavior rather than only isolated functions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/checker/checker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/checker/testing.go -->
## sources/sync-backup/restic/internal/checker/testing.go

Purpose: reusable test helper that runs the checker end-to-end on a repository expected to be valid. API: `TestCheckRepo(t, repo)`. Control flow creates a checker with unused tracking, loads the index, fails on index errors or hints, loads all snapshots, runs pack checks, structure checks, unused blob detection, and full pack reads while reporting every channel error to the test. State is transient checker state plus repository reads; no persistence except repository access. Dependencies include `data.SnapshotFilter`, `restic.NoopCounter`, and checker repository interface. Integration point is other package tests that create repositories and want a validity assertion. Risks: helper assumes no unused blobs and no mixed-pack hints, so it is intentionally strict; callers must use repositories that are fully consistent. Test signal is indirect through callers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/checker/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/duration.go -->
## sources/sync-backup/restic/internal/data/duration.go

Purpose: parses and formats retention-policy durations with year/month/day/hour units instead of `time.Duration` nanoseconds. APIs: `Duration`, `String`, `ParseDuration`, `Set`, `Type`, `Zero`, and helper `nextNumber`. Control flow trims outer whitespace, repeatedly parses an optional negative ASCII integer followed by one unit (`y`, `m`, `d`, `h`), and stores the latest value per unit; `String` emits canonical order years, months, days, hours and omits zero fields. State is value-only. Dependencies are `strconv`, `strings`, `fmt`, and internal errors. Integration points are forget/retention flags and `ExpirePolicy`. Risks: duplicate units overwrite earlier values, only ASCII digits are accepted, inner whitespace produces errors, and months use `m` while minutes are unsupported. Tests cover positive/negative units, ordering canonicalization, invalid units, and non-ASCII digits.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/duration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/duration_test.go -->
## sources/sync-backup/restic/internal/data/duration_test.go

Purpose: validates retention duration parsing and string canonicalization. APIs under test are private `nextNumber`, public `ParseDuration`, and `Duration.String`. Control flow uses table tests for numbers followed by unit suffixes, negative numbers, missing numbers, trailing input, and full duration strings. State is only parsed `Duration` values. Dependencies include `go-cmp` for structural comparison. Integration signal: these tests pin CLI/pflag behavior used by snapshot expiration policy. Risks covered include invalid week unit, missing number, embedded unsupported unit, and non-ASCII digit bytes; they also document that input order does not control output order. Missing coverage: duplicate unit overwrite semantics and `Set`, `Type`, `Zero` are only indirectly or not covered.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/duration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/find.go -->
## sources/sync-backup/restic/internal/data/find.go

Purpose: discovers all tree and data blobs reachable from a set of root tree IDs. API: `FindUsedBlobs(ctx, repo, treeIDs, blobs, p)`. Control flow calls `StreamTrees` over root trees, inserts each tree blob into the supplied `FindBlobSet`, skips already-seen tree blobs via the filter callback, then for every file node inserts its data blob IDs. A mutex protects the shared blob set because streamed tree processing can run concurrently. State is external and mutable: the caller-provided `FindBlobSet` and progress counter. Dependencies include `restic.Loader`, `restic.FindBlobSet`, `data.StreamTrees`, and sync locking. Integration points are checker, prune, and tests needing reachability analysis. Risks: correctness depends on complete tree traversal and on skipping already-seen trees without skipping unseen data; cancellation/error propagation comes from `StreamTrees`. Tests compare golden used-blob sets and ensure seen trees are not reloaded.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/find_test.go -->
## sources/sync-backup/restic/internal/data/find_test.go

Purpose: validates used-blob reachability over synthetic repository trees. APIs under test include `FindUsedBlobs`, `TestCreateSnapshot`, `TestLoadAllSnapshots`, and `TestTreeMap`. Control flow builds one or more deterministic snapshots, calls `FindUsedBlobs`, compares the resulting set with golden files, and optionally updates goldens via `-update`. `ForbiddenRepo` asserts that already-seen tree blobs are not loaded again. State includes deterministic snapshot IDs, golden testdata sets, and caller-provided blob sets. Dependencies include repository test helpers, restic blob handles, and data package test utilities. Risks covered: multi-root traversal, duplicate/seen subtree skipping, progress over larger generated repositories, and benchmark performance. Missing signal: explicit cancellation/error path behavior is mostly inherited from `StreamTrees`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/find_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/node.go -->
## sources/sync-backup/restic/internal/data/node.go

Purpose: defines the persisted JSON representation and comparison logic for backed-up filesystem nodes. APIs/types: `Node`, `NodeType`, `ExtendedAttribute`, `GenericAttributeType`, generic attribute conversion helpers, `MarshalJSON`, `UnmarshalJSON`, `Equals`, `GetExtendedAttribute`, and unknown-attribute handlers. Control flow normalizes timestamps into JSON-safe years, escapes names manually for legacy-compatible encoding, stores invalid UTF-8 symlink targets in `linktarget_raw`, compares content/xattrs/generic attributes deeply, and maps OS-specific generic attributes via reflection. State includes the global `genericAttributesForOS` registry and `unknownGenericAttributesHandlingHistory` sync map used to warn once per unknown attribute. Dependencies include JSON, reflection, time, OS modes, debug, errors, and restic IDs. Integration points are archiver, tree serialization, restore, and cross-OS metadata handling. Risks: JSON compatibility, nil vs empty fields, reflection on pointer fields, one-time warning global state, and raw symlink bytes. Tests cover timestamp clamping and symlink serialization.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/node_test.go -->
## sources/sync-backup/restic/internal/data/node_test.go

Purpose: focused tests for node timestamp and symlink JSON behavior. APIs under test are private `fixTime` and `Node` JSON marshal/unmarshal. Control flow parses RFC3339Nano timestamps, clamps years below zero to year zero and above 9999 to 9999, then round-trips symlink targets containing valid Unicode and invalid byte sequences. `TestSymlinkSerializationFormat` checks the on-disk compatibility detail: valid UTF-8 uses `linktarget`, invalid bytes are preserved through `linktarget_raw`. State is only local node values. Dependencies include `encoding/json`, `time`, and internal test helpers. Risks covered are high-value persistence compatibility risks: Go time JSON bounds and non-UTF-8 symlink target preservation. Missing signal: broader `Node.Equals`, xattr comparison, and generic attribute reflection helpers are not covered here.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/node_windows.go -->
## sources/sync-backup/restic/internal/data/node_windows.go

Purpose: defines Windows-specific node generic attributes and conversion to the cross-platform generic attribute map. APIs: `WindowsAttributes` with pointer fields for creation time, file attributes, and security descriptor; `WindowsAttrsToGenericAttributes`. Control flow reflects over the struct with `runtime.GOOS` as key prefix and delegates to `OSAttrsToGenericAttributes`, skipping nil fields so absent Windows metadata remains absent. State is value-only; returned map is persisted in `Node.GenericAttributes`. Dependencies include `syscall.Filetime`, JSON raw messages, reflection, and runtime GOOS. Integration points are Windows archiving/restoring and cross-OS repository reads. Risks: file name lacks a Windows build tag, so types must compile cross-platform; `runtime.GOOS` controls key prefix at runtime; pointer-only field convention must be preserved. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/node_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot.go -->
## sources/sync-backup/restic/internal/data/snapshot.go

Purpose: persisted snapshot metadata and helper operations. APIs/types: `Snapshot`, `SnapshotSummary`, `NewSnapshot`, `LoadSnapshot`, `SaveSnapshot`, `ForAllSnapshots`, tag/path/hostname predicates, and `Snapshots` sort implementation. Control flow absolutizes input paths, fills current user/UID/GID when available, loads/saves JSON unpacked snapshot files, lists snapshots in parallel while serializing callback invocation with a mutex, and filters by tags, paths, and hostnames. State is persisted as JSON snapshot blobs; plaintext ID is stored only in private `id` for restore/display. Dependencies include `restic` repository interfaces, `os/user`, `filepath`, sync, and debug. Integration points are backup creation, restore selection, checker, forget policy, and CLI filters. Risks: user lookup failures are intentionally ignored, path matching requires exact absolute paths, tag removal reorders tags, and callback serialization matters for callers. Tests cover creation, tags, and JSON loading across repo versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_find.go -->
## sources/sync-backup/restic/internal/data/snapshot_find.go

Purpose: resolves snapshot selectors such as latest, explicit ID prefixes, and optional subfolders. APIs: `SnapshotFilter`, `ErrNoSnapshotFound`, `FindSnapshot`, `FindLatest`, `FindAll`, `SnapshotFindCb`, and `ErrInvalidSnapshotSyntax`. Control flow normalizes filter paths to absolute clean paths, scans snapshots for the newest matching host/tag/path/timestamp constraints, splits `id:subfolder` syntax, resolves `latest` or ID prefixes, and calls a callback for all selected snapshots. State is filter fields, including an in-place rewrite of `Paths` to absolute paths in `findLatest`. Dependencies include `ForAllSnapshots`, `restic.Find`, `FindTreeDirectory`, path/filepath, and errors. Integration points are restore, ls, forget, and checker filtered runs. Risks: `SnapshotFilter.Empty` ignores `TimestampLimit`; subfolder syntax is disallowed for `FindAll`; path normalization mutates the filter; ambiguous/not-found ID behavior depends on restic ID lookup. Tests cover latest, max timestamp, subpath, and invalid subpath usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_find_test.go -->
## sources/sync-backup/restic/internal/data/snapshot_find_test.go

Purpose: integration tests for snapshot lookup and filtering. APIs exercised are `SnapshotFilter.FindLatest`, `FindLatest` with `TimestampLimit`, latest-with-subpath resolution, and `FindAll` rejection of subfolder syntax. Control flow creates deterministic snapshots in a test repository, queries by host/path/tag/time, and asserts returned snapshot IDs and subfolder strings. State is repository snapshot metadata and generated test tree IDs. Dependencies include repository test helpers, `data.TestCreateSnapshot`, time parsing helpers, and restic IDs. Risks covered: latest selection must honor timestamp ceilings, path filters must be applied after absolute path normalization, and `latest:sub/path` must resolve both snapshot and tree subdirectory while `FindAll` must reject `snapshot:subfolder` syntax. Missing signal: ambiguous ID prefix handling is likely covered elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_find_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_group.go -->
## sources/sync-backup/restic/internal/data/snapshot_group.go

Purpose: groups snapshots by host, path set, and/or tag set for retention and listing workflows. APIs: `SnapshotGroupByOptions`, pflag-compatible `Set`/`String`/`Type`, `SnapshotGroupKey`, and `GroupSnapshots`. Control flow parses comma-separated group-by tokens (`host`, `paths`, `tags`), derives a key per snapshot with optional fields, marshals it to JSON for stable map keys, and reports whether grouping is semantically active. State is only returned maps and option values. Dependencies include JSON, strings, and internal errors. Integration points are forget policy grouping and CLI options. Risks: unknown group-by tokens error, JSON key generation can fail if struct fields become non-marshalable, tags/paths order affects grouping because slices are used as stored, and empty grouping collapses snapshots together. Tests cover option parsing and string rendering.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_group_test.go -->
## sources/sync-backup/restic/internal/data/snapshot_group_test.go

Purpose: tests group-by option parsing for snapshot grouping. API under test is `SnapshotGroupByOptions.Set` and `String`. Control flow runs table cases for empty input, valid single/multiple group fields, and invalid tokens, then compares parsed booleans and rendered output. State is only the option struct. Dependencies are the data package and internal test helpers. Integration signal is CLI-facing: it protects accepted group names and user-visible string form. Risks covered are primarily input validation and canonical display. Missing signal: `GroupSnapshots` behavior with actual snapshots, JSON key stability, and order sensitivity of tags/paths are not directly tested in this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_group_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_policy.go -->
## sources/sync-backup/restic/internal/data/snapshot_policy.go

Purpose: implements retention policy selection for keeping/removing snapshots. APIs/types: `ExpirePolicy`, `KeepReason`, `ApplyPolicy`, policy `String`, `Empty`, and bucket helpers for hourly/daily/weekly/monthly/yearly grouping. Control flow sorts snapshots newest first, computes latest non-future timestamp, evaluates tag-based keeps, within-newest duration keeps, count buckets, and within-duration buckets, then builds keep/remove lists and reasons with remaining counters. State is in-memory only but input slice is sorted in place. Dependencies include `Duration`, `Snapshots`, tags, time, sorting, reflection, and debug logging. Integration points are `forget`/retention commands and JSON output reason reporting. Risks: future snapshots are ignored for latest reference; bucket rules keep oldest when counts remain to maximize history; `-1` means keep all; in-place sort can surprise callers; exact boundary uses `After` not inclusive. Golden tests provide broad policy regression coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_policy_test.go -->
## sources/sync-backup/restic/internal/data/snapshot_policy_test.go

Purpose: golden-file and helper tests for snapshot retention policy. APIs exercised include `ExpirePolicy.Empty`, `ExpirePolicy.String`, `ApplyPolicy`, and `KeepReason` serialization. Control flow loads snapshot sets and expected keep/reason results from `testdata/policy_keep_snapshots_*`, applies many policy combinations, compares with JSON goldens, and supports `-update` regeneration. State is local snapshots with deterministic times/tags plus persisted golden files. Dependencies include `go-cmp`, JSON, filesystem testdata, and data package APIs. Risks covered are extensive: last/hourly/daily/weekly/monthly/yearly counts, keep-all sentinel, tag retention, within durations, reason counters, ordering, future/latest timestamp behavior, and policy string display. Maintenance risk is golden drift: intentional algorithm changes require updating many files with review.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_test.go -->
## sources/sync-backup/restic/internal/data/snapshot_test.go

Purpose: basic tests for snapshot construction, tag predicates, and JSON loading. APIs under test include `NewSnapshot`, `HasTags`, and `LoadSnapshot` through `testLoadJSONUnpacked`. Control flow checks new snapshots preserve provided paths/tags/host/time while filling user info opportunistically, validates tag list matching including empty-tag behavior, and loads snapshot JSON across repository versions. State includes local snapshot values and versioned test repositories. Dependencies include repository test helpers, restic IDs, and data package APIs. Risks covered are CLI-visible metadata initialization and tag matching semantics. Missing signal: path absolute conversion edge cases, `ForAllSnapshots` concurrency, `AddTags`/`RemoveTags`, and host/path filter predicates are covered elsewhere or not directly here.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tag_list.go -->
## sources/sync-backup/restic/internal/data/tag_list.go

Purpose: pflag-compatible parsing and formatting of tag filters. APIs: `TagList`, `TagLists`, `Set`, `String`, `Type`, `Flatten`, and helpers `splitTagList`. Control flow splits one comma-separated string into a tag conjunction (`TagList`), appends multiple `TagList` values to `TagLists` for disjunctions, renders comma/space-separated forms, and flattens multiple lists into a deduplicated tag list preserving first-seen order. State is mutable receiver slices. Dependencies are only `strings`. Integration points are snapshot filters, retention tag policy, and CLI flag parsing. Risks: empty strings become empty tags, no trimming beyond what split preserves, `TagLists.String` formatting is user-visible, and flatten deduplication is O(n^2) but small. Tests cover `Flatten`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tag_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tag_list_test.go -->
## sources/sync-backup/restic/internal/data/tag_list_test.go

Purpose: validates tag-list flattening. API under test is `TagLists.Flatten`. Control flow table-tests nil/empty input, one tag list, multiple lists, and duplicate tags, then compares expected flattened `TagList`. State is local slices. Dependencies are internal test equality helpers. Integration signal: this guards retention and snapshot filtering code that needs a single deduplicated tag list for display or operations. Risks covered are nil-vs-empty behavior and duplicate removal while retaining deterministic order. Missing signal: parsing (`Set`), string rendering, and empty tag semantics are tested elsewhere or remain implicit.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tag_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/testing.go -->
## sources/sync-backup/restic/internal/data/testing.go

Purpose: reusable data-package test fixtures for deterministic files, trees, snapshots, and in-memory tree maps. APIs include `TestSaveNodes`, `TestCreateSnapshot`, `TestSetSnapshotID`, `ParseDurationOrPanic`, `TestLoadAllSnapshots`, `TestTreeMap`, and `TestWritableTreeMap`. Control flow creates pseudo-random file blobs, recursively builds sorted directory trees, saves tree blobs through a repository uploader, creates snapshots at specified times/depths, and loads all snapshots sorted. State persists generated blobs/snapshots into the supplied repository or in-memory maps. Dependencies include `chunker`, `restic.BlobSaver`, `SaveTree`, `SaveSnapshot`, and test helpers. Integration points are checker, find, tree, snapshot, and benchmark tests. Risks: deterministic IDs depend on exact fake tree/file generation; helper panics/fails tests directly; in-memory maps only implement a subset of repository behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/testing_test.go -->
## sources/sync-backup/restic/internal/data/testing_test.go

Purpose: validates and benchmarks `data/testing.go` snapshot fixture generation. APIs under test are `TestCreateSnapshot` and related constants. Control flow creates a repository, generates a snapshot at a fixed timestamp and depth, then verifies expected root tree ID and snapshot ID; benchmark repeatedly creates snapshots at fixed depth. State is the test repository containing generated blobs and snapshot metadata. Dependencies include repository test helpers, restic IDs, and data fixture APIs. Risks covered: deterministic test fixture stability, which many other tests rely on for golden IDs and tree traversal expectations. Missing signal: broader fake filesystem helper edge cases are only covered indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/testing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tree.go -->
## sources/sync-backup/restic/internal/data/tree.go

Purpose: streaming JSON tree reader/writer plus ordered tree search and diff helpers. APIs/types: `TreeNodeIterator`, `NodeOrError`, `NewTreeNodeIterator`, `LoadTree`, `TreeFinder`, `TreeWriter`, `TreeJSONBuilder`, `FindTreeDirectory`, `DualTreeIterator`, and `ErrTreeNotOrdered`. Control flow decodes `{"nodes":[...]}` while skipping unknown object keys, enforces single-use iterators, writes nodes in strictly increasing name order, saves tree blobs, searches sorted trees monotonically, resolves subdirectories by repeatedly loading subtrees, and merges two sorted iterators into paired `DualTree` records. State includes streaming decoder/writer buffers and iterator cursors; persisted state is tree JSON blobs. Dependencies include JSON, `iter`, restic blob interfaces, path handling, runtime-specific Windows hint, and errors. Risks: tree order is a storage invariant; iterators are single-use; errors are emitted inside sequences; `FindTreeDirectory` requires forward slash subfolder syntax. Tests cover serialization compatibility, unknown keys, finder behavior, directory resolution, dual iteration, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tree_stream.go -->
## sources/sync-backup/restic/internal/data/tree_stream.go

Purpose: concurrently streams a forest of tree blobs, processes each tree once, and schedules discovered subtrees. APIs: `StreamTrees` plus internal `subtreesCollector`, `loadTreeWorker`, and `filterTrees`. Control flow seeds root tree IDs, runs loader workers bounded by repository connections, separates huge trees onto a special channel, calls a caller-supplied `skip` predicate for deduplication, wraps tree iterators to collect subtrees after full processing, and pushes discovered subtree jobs while preserving root indexes for progress. State includes worker channels, tracked IDs/subtrees, visited filtering held by caller, and progress counter. Dependencies include `restic.Loader`, `LoadTree`, `errgroup`, runtime worker sizing, and debug/errors. Integration points are checker structure validation and used-blob discovery. Risks: `subtreesCollector` panics if the process callback does not fully consume a tree; deadlock/cancellation correctness depends on channel closure order; huge-tree behavior affects memory/concurrency. Tests are indirect through checker/find/tree tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tree_stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tree_test.go -->
## sources/sync-backup/restic/internal/data/tree_test.go

Purpose: broad tests for node/tree serialization, tree load/save cycles, tree lookup, and dual-tree iteration. APIs exercised include `Node.MarshalJSON`, `Node.Equals`, `LoadTree`, `SaveTree`, `TreeJSONBuilder`, `TreeFinder`, `FindTreeDirectory`, and `DualTreeIterator`. Control flow creates temporary files, converts them to nodes, compares generated JSON to struct marshaling, uses in-memory tree maps for load/save round trips, runs unknown-key JSON cases, and table-tests ordered finder and two-tree merge behavior including errors and single-use panic. State includes temporary filesystem fixtures, test repositories, and in-memory blob maps. Dependencies include archiver, fs, repository, restic IDs, slices/iter, and data helpers. Risks covered are critical persistence compatibility, ordering enforcement, streaming iterator error semantics, Windows path hint behavior, and merge correctness. Benchmarks measure tree build/load performance.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/data/tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/debug.go -->
## sources/sync-backup/restic/internal/debug/debug.go

Purpose: environment-controlled debug logging infrastructure. APIs: package-level `Log` plus initialization helpers for `DEBUG_LOG`, `DEBUG_FUNCS`, and `DEBUG_FILES`. Control flow initializes before other package init functions, opens optional log file, parses comma-separated include/exclude glob filters, captures caller function/file/line and goroutine number, shortens arguments implementing `Str()`, writes to configured logger and/or stderr when filters match. State is global `opts` containing enabled flag, logger, and filter maps. Dependencies include OS environment/file IO, runtime caller/stack, path globbing, and standard log. Integration points are debug calls across restic, HTTP debug wrappers, and tests that disable logging. Risks: invalid filters or log open failures call `os.Exit`, global init reads environment once, logger file handle is not closed, and runtime caller depth must stay stable. Benchmarks cover log overhead.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/doc.go -->
## sources/sync-backup/restic/internal/debug/doc.go

Purpose: package documentation declaring the `debug` package. It contains no APIs beyond the package comment and package clause. Control flow, state, persistence, and dependencies are absent. Integration point is Go documentation tooling and package-level description for the debug logging helpers. Risks are minimal; changes here only affect docs. Test signal is none directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/log_test.go -->
## sources/sync-backup/restic/internal/debug/log_test.go

Purpose: benchmarks for debug logging call overhead and ID formatting. APIs benchmarked are `debug.Log` with static strings, `restic.ID.Str()`, and `restic.ID.String()`. Control flow repeatedly calls logging with no assertions, so measured behavior depends on environment-enabled debug state. State is benchmark-local ID values plus global debug options initialized at package load. Dependencies include `testing` and `restic.ID`. Integration signal is performance-oriented: it helps detect expensive formatting/logging regressions in hot paths. Risks: benchmarks are sensitive to debug environment variables and do not validate correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper.go -->
## sources/sync-backup/restic/internal/debug/round_tripper.go

Purpose: HTTP transport debugging utilities compiled into debug builds through wrapper files. APIs/types: `eofDetectRoundTripper`, `eofDetectReader`, `loggingRoundTripper`, `redactHeader`, `restoreHeader`, and `RoundTrip` methods. Control flow wraps responses to detect bodies closed before EOF, dumps requests/responses with `httputil`, redacts sensitive headers before dumping, restores originals afterward, and logs/stderr-writes diagnostics. State includes per-body EOF flag and temporary header maps. Dependencies include `net/http`, `httputil`, IO, OS stderr, and internal errors/logging. Integration points are backend HTTP transports under debug tags. Risks: body draining on premature close can consume remaining response bytes; redaction must keep sensitive values out of dumps; dumping bodies can affect streaming if not handled carefully. Tests cover header redaction.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper_debug.go -->
## sources/sync-backup/restic/internal/debug/round_tripper_debug.go

Purpose: debug-build implementation of `RoundTripper`. API: `RoundTripper(upstream http.RoundTripper) http.RoundTripper`. Control flow wraps the upstream transport with response body EOF detection and HTTP request/response logging, enabling diagnostics for leaking or partially consumed bodies. State is wrapper state from `round_tripper.go`; no persistence. Dependencies are `net/http` and internal debug transport types. Integration point is build-tag-controlled HTTP transport setup. Risks: debug instrumentation can alter timing and output volume; it should not be used as release behavior. Test coverage is shared through redaction tests and build-tag behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper_debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper_release.go -->
## sources/sync-backup/restic/internal/debug/round_tripper_release.go

Purpose: release-build no-op implementation of `RoundTripper`. API: `RoundTripper(upstream http.RoundTripper) http.RoundTripper`, returning `upstream` unchanged. Control flow is deliberately empty. State and persistence are absent. Dependencies are only `net/http`. Integration point is the same call sites as debug builds, allowing instrumentation to be compiled out. Risks: build tags must select the intended file; release builds will not detect undrained bodies. Tests for debug behavior do not apply in release builds except compile-time API compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper_release.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper_test.go -->
## sources/sync-backup/restic/internal/debug/round_tripper_test.go

Purpose: tests sensitive-header redaction and restoration used by HTTP debug dumps. APIs under test are `redactHeader` and `restoreHeader`. Control flow builds headers with authorization-like values, redacts them, verifies sensitive values are replaced while non-sensitive values remain, then restores originals and verifies round-trip equality. State is local `http.Header` maps and saved original values. Dependencies include `net/http` and testing helpers. Risks covered are important operational/privacy concerns: debug logging must not leak credentials and must not permanently mutate the request headers passed to the real transport. Missing signal: full dump/EOF wrapper behavior is not directly asserted.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/round_tripper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/stacktrace.go -->
## sources/sync-backup/restic/internal/debug/stacktrace.go

Purpose: returns the current goroutine stack trace as a string. API: `DumpStacktrace() string`. Control flow allocates an initial 1 KiB buffer, repeatedly calls `runtime.Stack` for the current goroutine, doubles the buffer until the stack fits, and returns the captured bytes. State is local buffer only. Dependencies are `runtime`. Integration points are panic/error diagnostics and debug logging. Risks: repeated allocation for very deep stacks, current-goroutine-only capture (`all=false`), and no truncation policy. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/stacktrace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/testing.go -->
## sources/sync-backup/restic/internal/debug/testing.go

Purpose: test helpers for controlling debug output. APIs: `TestLogToStderr` reports whether debug stderr logging is active for tests, and `TestDisableLog` disables debug logging globally. Control flow inspects global debug options and mutates `opts.isEnabled`. State is global and process-wide, so changes affect all subsequent debug logging in the test process. Dependencies include `testing`. Integration points are tests that need stable output or want to skip log-dependent assertions. Risks: disabling logging is not automatically restored and can affect parallel tests; helper is intentionally test-only by convention, not build tags.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/debug/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/acl.go -->
## sources/sync-backup/restic/internal/dump/acl.go

Purpose: converts Linux binary ACL xattrs to POSIX.1e long text format for archive dumps. APIs: private `formatLinuxACL` and `aclPermText`; constants define ACL permission and tag values. Control flow validates ACL length and version 2, iterates 8-byte entries, decodes little-endian tag/permission/id fields, emits `user`, `group`, `mask`, or `other` lines with decimal IDs and `rwx` text, and errors on unknown tags. State is local output buffer only. Dependencies are `encoding/binary`, `strconv`, and standard errors. Integration points are tar dump PAX xattrs for ACL preservation/display. Risks: supports Linux ACL binary layout only, rejects unknown versions/tags, and prints numeric IDs to avoid host name ambiguity. Tests cover valid and invalid ACL formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/acl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/acl_test.go -->
## sources/sync-backup/restic/internal/dump/acl_test.go

Purpose: verifies Linux ACL binary-to-text conversion. API under test is private `formatLinuxACL` in package `dump`. Control flow builds representative binary ACL byte slices and expected text output, then checks error cases such as wrong length, unsupported version, and unknown tag. State is local test vectors. Dependencies include testing and ACL constants from the same package. Integration signal protects tar dump metadata output because ACL text is embedded in archive headers. Risks covered include endian decoding, tag mapping, permission bit rendering, and validation. Missing signal: integration through `dumpNodeTar` PAX headers is covered by tar tests rather than this unit test.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/acl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/common.go -->
## sources/sync-backup/restic/internal/dump/common.go

Purpose: common archive dumper orchestration for tar and zip outputs. APIs: `Dumper`, `New`, `DumpTree`, `WriteNode`, private `sendTrees`, `sendNodes`, and `writeNode`. Control flow creates a 64 MiB blob LRU cache, walks selected tree nodes into a channel, dispatches to format-specific writers, recursively walks directory subtrees, filters unsupported node types, and writes file content by loading blobs concurrently while preserving output order through channels. State includes cache, format, repository loader, writer, and in-flight goroutines/channels. Dependencies include `bloblru`, `data`, `restic`, `walker`, and `errgroup`. Integration points are `restic dump` tar/zip and raw node writes. Risks: node `Path` is mutated during traversal, file blob order must be preserved despite concurrent loads, context cancellation must stop both walker and writer, and only file/dir/symlink are archived. Tests in common/tar/zip validate archive equivalence.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/common_test.go -->
## sources/sync-backup/restic/internal/dump/common_test.go

Purpose: shared dump test harness for tar and zip writers. APIs: `prepareTempdirRepoSrc`, `CheckDump`, and `WriteTest`. Control flow creates a temporary source tree using archiver test fixtures, archives it to a test repository, calls the dumper in the requested format into a buffer, and delegates archive-specific verification to a callback. State includes temporary directories, repository/backend fixtures, and in-memory dump bytes. Dependencies include archiver test helpers, repository/backend setup, and dump package APIs. Integration signal is high: tar and zip tests reuse this to verify full dump traversal from repository data to archive bytes. Risks: fixture cleanup depends on test settings; archive-specific metadata checks live in format tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/tar.go -->
## sources/sync-backup/restic/internal/dump/tar.go

Purpose: tar archive writer for dumped repository trees. APIs: `dumpTar`, `dumpNodeTar`, `tarIdentifier`, and `parseXattrs`. Control flow consumes node channel, creates tar headers for files, dirs, and symlinks, maps UID/GID into tar-compatible signed numeric fields, writes file content through `writeNode`, encodes xattrs into PAX records, and formats Linux ACL xattrs when present. State is the `tar.Writer` and per-node header data; persisted output is tar bytes. Dependencies include archive/tar, data nodes/xattrs, context, and internal ACL formatter. Integration point is `Dumper.DumpTree` with format `tar`. Risks: tar numeric field limits, path/name length behavior, xattr/ACL PAX key correctness, symlink target handling, and closing writer on errors. Tests cover writing, content comparison, and long field behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/tar_test.go -->
## sources/sync-backup/restic/internal/dump/tar_test.go

Purpose: verifies tar dump output against a source directory and edge cases. APIs exercised include shared `WriteTest`, `dumpTar`, and tar header behavior. Control flow creates a dump, reads tar entries back, compares files/directories/symlinks against the original test directory, and tests field-too-long behavior for tar metadata. State is in-memory tar bytes and temporary source repository. Dependencies include archive/tar, filesystem helpers, and dump common test harness. Risks covered: archive content fidelity, file data writes, directory/symlink representation, and tar header constraints. Missing signal: full ACL/xattr integration is partially dependent on platform/fixture availability and unit ACL tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/tar_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/zip.go -->
## sources/sync-backup/restic/internal/dump/zip.go

Purpose: zip archive writer for dumped repository trees. APIs: `dumpZip` and `dumpNodeZip`. Control flow consumes node channel, creates zip headers from node metadata, writes directories with trailing slash, writes symlinks as entries containing the link target, and streams regular file contents via `writeNode`. State is the `zip.Writer` and per-entry headers; persisted output is zip bytes. Dependencies include archive/zip, data nodes, context, and file mode metadata. Integration point is `Dumper.DumpTree` with format `zip`. Risks: zip has less metadata fidelity than tar, symlink representation is convention-based, path normalization must remain archive-safe, and writer close errors must be propagated. Tests verify archive entries and contents against a source tree.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/zip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/zip_test.go -->
## sources/sync-backup/restic/internal/dump/zip_test.go

Purpose: validates zip dump output. APIs exercised include shared `WriteTest`, `dumpZip`, `readZipFile`, and `checkZip`. Control flow writes a repository tree to an in-memory zip, opens it with `zip.NewReader`, reads each entry, and compares contents and expected entries against the original source fixture. State is temporary source data and zip buffer. Dependencies include archive/zip, bytes, filesystem helpers, and dump test harness. Risks covered: regular file content fidelity, directory entries, symlink representation, and archive readability. Missing signal: detailed permission/xattr metadata is not as rich for zip and is therefore less covered than tar.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/dump/zip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/doc.go -->
## sources/sync-backup/restic/internal/errors/doc.go

Purpose: package documentation for restic's internal error compatibility layer. It declares package `errors` and has no exported APIs beyond documentation. Control flow, state, and persistence are absent. Integration point is Go documentation and the package boundary for wrappers around standard and pkg/errors behavior. Risks are minimal; code behavior lives in `errors.go` and `fatal.go`. No direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/errors.go -->
## sources/sync-backup/restic/internal/errors/errors.go

Purpose: compatibility facade over `github.com/pkg/errors` plus selected standard-library error helpers. APIs: variables `New`, `Errorf`, `Wrap`, `Wrapf`, `WithStack`; functions `As`, `Is`, `Join`, and `Unwrap`. Control flow delegates directly to underlying packages. State and persistence are absent. Dependencies are `github.com/pkg/errors` and standard `errors`. Integration point is repository-wide error construction and matching, allowing older stack-wrapping APIs and newer `errors.Is/As/Join` use under one import path. Risks: `pkg/errors` wrapping must interoperate with standard `Is/As`; `Join` returns standard joined errors; exported vars can technically be reassigned by package users, though convention discourages it. Tests for fatal wrapping exercise some interoperability.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/fatal.go -->
## sources/sync-backup/restic/internal/errors/fatal.go

Purpose: marks errors as fatal while preserving wrapping/unwrapping behavior. APIs: private `fatalError`, public `IsFatal`, `Fatal`, and `Fatalf`. Control flow wraps an underlying error in `fatalError`, returns the underlying message from `Error`, exposes `Unwrap`, and detects fatal errors with `errors.As`. `Fatalf` formats a message and, when the last argument is an error, stores that error as the underlying cause while formatting the full message. State is per-error only. Dependencies are `fmt` and internal/standard error matching. Integration points are CLI/control-flow paths that distinguish fatal errors from ordinary retryable/reportable errors. Risks: `Fatalf` last-argument error convention is subtle; `IsFatal` follows wrapping chains, so downstream wrappers still classify fatal. Tests cover detection and wrapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/fatal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/fatal_test.go -->
## sources/sync-backup/restic/internal/errors/fatal_test.go

Purpose: validates fatal error classification and wrapping semantics. APIs under test are `Fatal`, `Fatalf`, `IsFatal`, and standard `errors.Is` interoperability through the internal facade. Control flow checks nil/nonfatal cases, direct fatal errors, formatted fatal errors, and wrapping a sentinel underlying error so both fatal classification and underlying matching work. State is local error values. Dependencies include testing and internal errors package. Risks covered: fatal marker must survive wrapping and must not hide the underlying cause. Missing signal: multi-error `Join` fatal classification is not tested here.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/errors/fatal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/features.go -->
## sources/sync-backup/restic/internal/feature/features.go

Purpose: feature-flag registry and parser with lifecycle phases. APIs/types: `FlagName`, `FlagDesc`, `FlagSet`, `New`, `SetFlags`, `Apply`, `Enabled`, `Help`, and `List`; states are stable, beta, alpha, and deprecated. Control flow initializes default enabled state by phase, applies comma-separated flag names with optional leading `!` to disable, warns for deprecated flags, errors on unknown flags, panics if queried flag or descriptor phase is invalid, and lists help metadata sorted by name. State is the mutable `FlagSet` map of flag values/descriptions. Dependencies include sorting, strings, and errors. Integration points are global feature registry and CLI feature toggles. Risks: `SetFlags` panics on invalid phases, `Enabled` panics for unregistered flags, deprecated flags default disabled, and repeated `Apply` mutates state cumulatively. Tests cover defaults, apply, invalids, panic behavior, and listing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/features.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/features_test.go -->
## sources/sync-backup/restic/internal/feature/features_test.go

Purpose: unit tests for feature flag defaults, mutation, invalid input, and help listing. APIs under test are `New`, `SetFlags`, `Apply`, `Enabled`, and `List`. Control flow builds a test flag set with stable/beta/alpha/deprecated flags, asserts default enabled values, applies enable/disable strings including multiple applications, verifies invalid flag names return errors, and asserts panic behavior for unknown queries or invalid phases. State is a local mutable `FlagSet`. Dependencies include data tables, panic helper, and testing. Risks covered include lifecycle default policy, deprecated warnings, cumulative mutation, and sorted help output. Missing signal: global registry constants are tested mostly by compile/init behavior in `registry.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/features_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/registry.go -->
## sources/sync-backup/restic/internal/feature/registry.go

Purpose: declares restic's global feature flag registry. APIs: package variable `Flag = New()` and named constants for known feature flags such as snapshot compression, safe pack operations, and upgrade repository. Control flow in `init` calls `Flag.SetFlags` with descriptors containing phase and description. State is global mutable feature flag state shared by the process. Dependencies are only the local feature package types. Integration points are CLI feature application and code paths gated by `feature.Flag.Enabled`. Risks: descriptors are applied at init, invalid phases panic, and global mutation in tests/CLI affects all callers. Test helper `TestSetFlag` exists to restore values in tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/testing.go -->
## sources/sync-backup/restic/internal/feature/testing.go

Purpose: test helper for temporarily overriding feature flag values. API: `TestSetFlag(t, f, flag, value) func()`. Control flow saves the current enabled value, sets the requested value in the flag set map, and returns a restore closure that resets the original value. State mutation is direct on `FlagSet.flags`, bypassing `Apply`. Dependencies include testing and feature package internals. Integration point is tests that need deterministic feature gating without parsing CLI strings. Risks: helper assumes the flag is registered because `Enabled` panics otherwise; restore must be called by tests, typically with `defer`; direct map access can diverge from validation semantics if internals change. Tests verify set/restore behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/testing_test.go -->
## sources/sync-backup/restic/internal/feature/testing_test.go

Purpose: validates the feature test override helper. API under test is `TestSetFlag`. Control flow creates or uses a feature flag set, records original value, sets an override, asserts `Enabled` reflects it, invokes the returned restore function, and asserts the original value returns. State is mutable feature flag map content. Dependencies include testing and feature package APIs. Risk covered is test isolation: feature overrides must be reversible to avoid leaking global state between tests. Missing signal: behavior with unknown flags is intentionally not tested because it would panic through `Enabled`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/feature/testing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/doc.go -->
## sources/sync-backup/restic/internal/filter/doc.go

Purpose: package documentation for path filtering used by backup exclude/include rules. It describes shell-style patterns and recursive `**` matching. No runtime APIs live here. Control flow, state, persistence, and dependencies are absent beyond package declaration. Integration point is Go documentation for `filter.Match`, `List`, and exclude helpers. Risks are documentation drift if pattern semantics change without updating this file. Tests for actual semantics live in filter test files.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/exclude.go -->
## sources/sync-backup/restic/internal/filter/exclude.go

Purpose: builds exclusion predicates and CLI options from explicit patterns and pattern files. APIs: `RejectByNameFunc`, `RejectByPattern`, `RejectByInsensitivePattern`, `readPatternsFromFiles`, `ExcludePatternOptions`, `Add`, `Empty`, and `CollectPatterns`. Control flow parses patterns once, returns predicate closures using `List`, lowercases patterns/items for insensitive mode, reads files via `textfile.Read`, skips comments/blank lines, validates patterns, wires pflag options for `--exclude`, `--iexclude`, `--exclude-file`, and `--iexclude-file`, and returns reject functions. State is option slices populated by flags; predicates capture parsed patterns. Dependencies include pflag, textfile, debug, internal errors, and filter matching. Integration points are backup path filtering. Risks: invalid patterns must be caught before traversal, warning callbacks handle runtime match errors, lowercase matching may be locale-insensitive only by Unicode lowercasing, and pattern-file syntax affects user workflows. Tests cover basic sensitive/insensitive rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/exclude.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/exclude_test.go -->
## sources/sync-backup/restic/internal/filter/exclude_test.go

Purpose: tests exclude predicate behavior. APIs under test are `RejectByPattern` and `RejectByInsensitivePattern`. Control flow creates predicate functions with simple patterns and a warning callback, then table-tests matching and non-matching paths for case-sensitive and case-insensitive behavior. State is predicate closures over parsed patterns. Dependencies are testing and filter package functions. Risks covered: exclusion is true on match, false otherwise, and insensitive mode lowercases both pattern and item. Missing signal: pattern-file reading, pflag option collection, invalid pattern validation, and warning behavior are covered indirectly or not here.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/exclude_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/filter.go -->
## sources/sync-backup/restic/internal/filter/filter.go

Purpose: core path pattern matching with recursive `**`, rooted patterns, and negated list rules. APIs/types: `ErrBadString`, `Pattern`, `Match`, `ChildMatch`, `ValidatePatterns`, `ParsePatterns`, `List`, `ListWithChild`, and `InvalidPatternError`. Control flow cleans and splits patterns/paths, marks simple components for fast equality, treats `**` as a variable-length directory wildcard, matches unrooted patterns at possible suffix offsets, supports rooted `/` matching, validates each component via `filepath.Match`, and evaluates pattern lists where `!` negates previous matches. State is immutable parsed pattern slices. Dependencies include filepath, strings, and internal errors. Integration points are exclude/include filtering and traversal pruning through child-match prediction. Risks: recursive wildcard expansion can be costly for long paths, negation semantics are order-sensitive, `ChildMatch` must avoid pruning paths that a later child could match, and OS filepath behavior matters. Tests are extensive for matches, child matches, invalid patterns, examples, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/filter_patterns_test.go -->
## sources/sync-backup/restic/internal/filter/filter_patterns_test.go

Purpose: validates pattern validation behavior for known valid/invalid pattern strings. API under test is `ValidatePatterns`. Control flow table-tests pattern slices and asserts whether validation returns an error. State is only local pattern data. Dependencies include testing and filter package APIs. Integration signal protects CLI exclude/include validation before traversal begins. Risks covered include malformed filepath glob components and recursive wildcard syntax accepted by restic. Missing signal: matching behavior is covered in `filter_test.go`; this file focuses only on validation acceptance/rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/filter_patterns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/filter_test.go -->
## sources/sync-backup/restic/internal/filter/filter_test.go

Purpose: comprehensive tests and benchmarks for path matching semantics. APIs exercised include `Match`, `ChildMatch`, `ParsePatterns`, `List`, `ListWithChild`, `ValidatePatterns`, and pattern-file extraction helper logic. Control flow table-tests rooted/unrooted patterns, wildcards, recursive `**`, negation lists, invalid empty strings and bad patterns, examples for documentation, tests large pattern files from compressed testdata, and benchmarks line filtering and pattern matching. State is parsed pattern lists, testdata lines, and benchmark counters. Dependencies include filepath semantics, bz2 testdata, and testing/benchmarking. Risks covered are central to backup correctness: accidentally excluding or including paths, traversal pruning decisions, negated pattern order, invalid pattern errors, and performance over large pattern sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/filter_test.go -->
