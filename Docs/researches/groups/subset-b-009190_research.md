# subset-b-009190 grouped research

This grouped report covers the requested Syncthing GUI, blob, database interface, legacy LevelDB, and SQLite database files. Each source file section is wrapped with the required markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/syncthingController.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/syncthingController.js

## Purpose
This is the main AngularJS controller for the Syncthing web GUI. It owns top-level GUI state, authentication/login behavior, periodic refreshes, event-driven updates from the backend event stream, modal orchestration, settings editing, device and folder management, restore-version browsing, usage reporting prompts, status display helpers, and small UI utilities such as copy-to-clipboard and temporary tooltips. It also registers the `shareTemplate` directive at the end of the file.

## Important APIs, Types, And Functions
The file configures `$locationProvider` for HTML5 mode and defines `SyncthingController` with dependencies on `$scope`, `$http`, `$location`, `LocaleService`, `Events`, `$filter`, `$q`, `$compile`, `$timeout`, `$rootScope`, and `$translate`. Important private helpers include `initController`, restart expectation helpers, `refreshFolder`, `updateLocalConfig`, `refreshSystem`, `refreshCluster`, `refreshDiscoveryCache`, `refreshCompletion`, `refreshConnectionStats`, `refreshConfig`, `parseNeeded`, sharing/ignore helpers, modal helpers, and restore-version initialization. Public `$scope` APIs are broad: authentication, `saveConfig`, `saveSettings`, restart/upgrade/shutdown, folder/device edit/save/delete/pause workflows, need/failed/local-changed/remote-need views, status/class/icon/text helpers, usage-report accept/decline/preview, scan/rescan controls, advanced config editing, xattr filter editing, and utility helpers like `docsURL`, `themeName`, and `inputTypeFor`.

## Control Flow
Initialization waits for all modal templates through `$scope.modalLoaded`, then calls `initController`. If unauthenticated, it only fetches the Syncthing version header and waits for login reload. Once authenticated, it starts a 10-second refresh interval and the `Events` service. `Events.ONLINE` performs the heavy bootstrap: refreshes stats, global changes, themes, system status, discovery cache, config, cluster pending state, connections, version, usage-report prompts, and upgrade info. Event handlers incrementally update `$scope.model`, `$scope.completion`, pending device/folder maps, scan progress, folder errors, and download progress. User actions mutate `$scope.config` and persist through `PUT /config`, or call specific REST endpoints such as `/db/scan`, `/db/need`, `/folder/versions`, `/system/restart`, and `/cluster/pending/*`.

## State And Persistence
Most state lives in `$scope`: `config`, `devices`, `folders`, `model`, `completion`, connection stats, pending devices/folders, scan/download progress, ignores, current edit objects, and restore-version state. Persistence is backend-driven through Syncthing REST APIs; the controller itself also stores `metricRates` in `localStorage` and uses a `firstVisit` cookie for deferred usage-report prompting. Config editing works on temporary copies, then copies validated values back into `$scope.config` before `saveConfig`. Folder and device edits update config arrays derived from map helpers such as `folderMap`, `folderList`, `deviceMap`, and `deviceList`.

## Dependencies And Integration Points
This file integrates with many global helpers and libraries: AngularJS, jQuery, Bootstrap modals/tooltips, moment/daterangepicker, fancytree, Font Awesome classes, translation service, global `urlbase`/`authUrlbase`, global constants such as `shortIDStringLength`, and Syncthing REST/event contracts. It must stay aligned with backend endpoints, backend config JSON shapes, event names and payloads from `Events`, and GUI templates that bind these `$scope` fields.

## Risks And Test Signals
The controller has a large blast radius and many implicit contracts. Risks include stale REST endpoint assumptions, race conditions between event updates and full refreshes, modal ordering bugs, fragile DOM/plugin interactions outside Angular's digest cycle, and validation gaps before config save. Restart detection depends on timing windows, and copy-to-clipboard uses browser-dependent fallbacks. The restore-version view correctly escapes fancytree titles, which is a useful security signal for remote-controlled paths. Test signals should include GUI/e2e coverage for login/logout, online/offline/restart transitions, config saves, pending devices/folders, folder/device sharing, receive-encrypted flows, restore versions, usage-report prompts, and Angular unit tests for status helpers and parsing helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/syncthingController.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/tooltipDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/tooltipDirective.js

## Purpose
This small AngularJS directive activates Bootstrap tooltip behavior on elements carrying the `tooltip` attribute. It is an adapter between Angular templates and jQuery/Bootstrap's tooltip plugin.

## Important APIs, Control Flow, And State
The directive is registered as `tooltip` on the `syncthing.core` module, restricted to attributes, and defines only a `link` function. On link, it calls `$(element).tooltip()`. It does not define isolate scope, watchers, or controller state. All tooltip content and behavior are supplied through element attributes and Bootstrap's plugin state.

## Dependencies And Integration Points
It depends on jQuery and Bootstrap tooltip being loaded before the directive runs. It is consumed by GUI templates that use `tooltip` attributes and expect Bootstrap's `data-original-title` and tooltip lifecycle behavior.

## Risks And Test Signals
The directive does not clean up tooltips on scope destruction, which can matter if tooltipped elements are frequently created and destroyed. It also assumes Bootstrap's jQuery plugin API, so Bootstrap upgrades can break it. Test signals are simple directive tests or GUI smoke tests that verify tooltips initialize and do not throw during route/template changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/tooltipDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/uncamelFilter.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/uncamelFilter.js

## Purpose
The `uncamel` AngularJS filter converts camelCase or mixed identifier-like configuration keys into user-facing labels while preserving reserved acronyms and expanding common time suffixes.

## Important APIs, Control Flow, And State
The filter registers `uncamel` and returns a function that accepts a string. It first returns an empty string for non-string or empty input. It replaces reserved substrings such as `IDs`, `ID`, `URL`, `API`, `QUIC`, `TCP`, `LAN`, and binary units with placeholders, inserts spaces between lowercase/digit and uppercase transitions, restores placeholders with spacing, expands final suffixes `S`, `M`, `H`, and `Ms` into time units, title-cases non-reserved parts, collapses whitespace, and trims. State is function-local: `reservedStrings`, placeholder map, and counter.

## Dependencies And Integration Points
It depends only on AngularJS filter registration and modern JavaScript features such as `const`, `let`, arrow functions, and `Object.entries`. It integrates with advanced config or metadata views that need readable labels from schema keys.

## Risks And Test Signals
Ordering in `reservedStrings` matters, as longer strings must be protected before their substrings. The use of unescaped words in `RegExp(word, 'g')` is safe for the current word list but should be reconsidered if new reserved strings contain regex metacharacters. The suffix expansion is heuristic and only applies to the final space-separated part. Unit tests should cover `deviceIDs`, `apiKey`, `rescanIntervalS`, `pullerPauseS`, `QUICLAN`, and binary unit labels.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/uncamelFilter.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/uniqueFolderDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/uniqueFolderDirective.js

## Purpose
This AngularJS validation directive prevents adding a new folder with an ID that already exists in the current GUI folder map.

## Important APIs, Control Flow, And State
The directive registers `uniqueFolder`, requires `ngModel`, and prepends a parser to the model pipeline. For non-new folder editing modes, it marks the `uniqueFolder` validity key as true and does not enforce uniqueness. For new folders, it checks `scope.folders.hasOwnProperty(viewValue)` and sets validity false when the folder ID already exists. It returns the original `viewValue` unchanged.

## Dependencies And Integration Points
It depends on `scope.currentFolder._editing` and `scope.folders`, both maintained by `syncthingController.js`. It integrates with Angular form validity and folder editor templates.

## Risks And Test Signals
The directive assumes `scope.currentFolder` and `scope.folders` exist. If the parser runs before controller initialization, templates should prevent undefined access or tests will catch it. It validates only against the currently loaded local folder map; backend-side uniqueness remains the final guard. Unit tests should exercise new, existing, and defaults editing modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/uniqueFolderDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/validDeviceidDirective.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/core/validDeviceidDirective.js

## Purpose
This AngularJS validation directive validates Syncthing device IDs through the backend and also flags IDs that are already present in the current configuration.

## Important APIs, Control Flow, And State
The directive registers `validDeviceid`, requires `ngModel`, injects `$http`, and prepends a parser. On every parsed view value, it calls `GET /svc/deviceid?id=<viewValue>`. The success handler treats `!resp.error` as syntactic validity and treats uniqueness as true when the ID is invalid or absent from `scope.devices`. It sets Angular validity keys `validDeviceid` and `unique`, then returns the original view value.

## Dependencies And Integration Points
It depends on the backend `/svc/deviceid` endpoint returning an `id` and optional `error`, plus `scope.devices` from the main controller. It integrates with Angular form validation for the device editor.

## Risks And Test Signals
Validation is asynchronous but implemented inside a synchronous parser without cancellation or stale-response protection. Rapid typing can allow older HTTP responses to update validity after newer input. The raw query parameter is not encoded, so unusual input characters could produce malformed URLs; `encodeURIComponent` would be safer. Unit or e2e tests should cover valid IDs, invalid IDs, duplicate IDs, and fast input changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/core/validDeviceidDirective.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/development/logbar.js -->
# sources/sync-backup/syncthing/gui/default/syncthing/development/logbar.js

## Purpose
This development-only script intercepts console warnings and errors and increments counters in a developer top bar. It helps GUI developers see when console noise appears during manual testing.

## Important APIs, Control Flow, And State
`intercept(method, handler)` wraps `window.console[method]`, calls the handler with the method name, then forwards the original console call using `apply` when available or a joined string fallback for old IE. `handleConsoleCall(type)` looks for `#log_<type>`, marks it with `hasCount`, displays `#dev-top-bar`, and increments the element's numeric `innerHTML`. At load time, if `window.console` exists, it intercepts `error` and `warn`.

## Dependencies And Integration Points
It uses browser DOM APIs and `window.console`. It expects DOM elements with IDs such as `log_error`, `log_warn`, and `dev-top-bar` in the development GUI layout.

## Risks And Test Signals
Repeated loading would wrap console methods multiple times and overcount. The counter assumes existing numeric `innerHTML`. Since it monkey-patches global console behavior, it should remain excluded from production bundles. Manual development smoke tests can confirm counts increment and original console output still appears.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/syncthing/development/logbar.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/blob/interface.go -->
# sources/sync-backup/syncthing/internal/blob/interface.go

## Purpose
This file defines the minimal blob storage abstraction used by Syncthing internals that need upload, download, and latest-object lookup without depending on a concrete backend.

## Important APIs, Control Flow, And State
`Store` exposes `Upload(ctx, key, reader)`, `Download(ctx, key, writer)`, and `LatestKey(ctx)`. `Writer` combines `io.Writer` and `io.WriterAt`, matching download APIs that can write chunks at offsets. There is no implementation or state in this file.

## Dependencies And Integration Points
It depends only on `context` and `io`. The S3 implementation in `internal/blob/s3/s3.go` satisfies this interface. Callers can provide any backend with equivalent semantics.

## Risks And Test Signals
The interface does not specify ordering semantics for `LatestKey`, missing-key behavior, overwrite behavior, or whether implementations must honor context cancellation. Implementations should be tested against these behavioral expectations, especially concurrent multipart downloads that require `WriterAt`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/blob/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/blob/s3/s3.go -->
# sources/sync-backup/syncthing/internal/blob/s3/s3.go

## Purpose
This file implements `blob.Store` using AWS S3-compatible storage. It creates a path-style S3 session and supports upload, download, and selection of the most recently modified object key in a bucket.

## Important APIs, Control Flow, And State
`Session` stores the bucket name and AWS SDK session. `NewSession` builds the AWS session from endpoint, region, bucket, access key ID, and secret, using static credentials and `S3ForcePathStyle`. `Upload` creates an `s3manager.Uploader` and uploads the reader to the configured bucket/key. `Download` creates an `s3manager.Downloader` and writes the object into a `blob.Writer`. `LatestKey` iterates all objects via `list`, comparing `LastModified` timestamps and returning the key with the newest timestamp. `list` pages through `ListObjectsV2` using `NextContinuationToken`.

## State And Persistence
Persistent state is remote S3 bucket content. The local `Session` holds connection configuration only. `LatestKey` reads bucket listings and does not cache results.

## Dependencies And Integration Points
It depends on AWS SDK v1 packages, `internal/blob`, and S3-compatible endpoints. It intentionally uses path-style addressing, which is important for non-AWS S3-compatible services.

## Risks And Test Signals
The methods currently ignore the supplied `context.Context`, so cancellation and deadlines are not propagated to AWS operations. `LatestKey` assumes `Key` and `LastModified` are non-nil for listed objects; malformed responses could panic. Equal timestamps preserve the first listed object, which may not be deterministic across providers. Integration tests should use a real or emulated S3 endpoint to cover multipart download, pagination, empty buckets, credential failures, and latest-key selection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/blob/s3/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/counts.go -->
# sources/sync-backup/syncthing/internal/db/counts.go

## Purpose
This file defines the aggregate count structure used by database implementations and callers to summarize folder/file state.

## Important APIs, Control Flow, And State
`Counts` stores item counts by type (`Files`, `Directories`, `Symlinks`, `Deleted`), byte totals, sequence, associated device ID, and local flag bucket. `Add` returns a combined count, sums sequences, resets `DeviceID` to `protocol.EmptyDeviceID`, and ORs local flags. `TotalItems` sums all item count classes. `String` renders a diagnostic summary with decoded local flag names and the raw flag value. `Equal` compares only numeric counts and bytes, deliberately ignoring sequence, device, and flags.

## Dependencies And Integration Points
It depends on `lib/protocol` for device IDs and local flags. It is returned by the database interface and used by GUI/API model summaries, folder status logic, and validation/debug paths.

## Risks And Test Signals
`Add` summing `Sequence` is useful for aggregate arithmetic but may not represent a meaningful database sequence for mixed devices. `String` appends raw flags whenever any flag is set, including known flags, which is diagnostic rather than stable UI output. Tests should verify arithmetic, `Equal` semantics, and flag rendering for each local flag.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/counts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/interface.go -->
# sources/sync-backup/syncthing/internal/db/interface.go

## Purpose
This file defines Syncthing's database abstraction: lifecycle service, file update/query APIs, block index operations, cleanup, counts, index IDs, virtual mtimes, and a generic key-value store.

## Important APIs, Control Flow, And State
`DBService` extends `suture.Service` with asynchronous maintenance controls. `UpdateOption`, `UpdateOptions`, and `WithSkipBlockIndex` adjust update behavior. `DB` is the main contract: `Update`, `Close`, single-file lookups, global/local/needed iterators, block index maintenance, delete/drop operations, metadata queries, count queries, index ID management, mtime mapping, and embedded `KV`. `KV` provides `GetKV`, `PutKV`, `DeleteKV`, and prefix iteration. Data carriers include `BlockMapEntry`, `KeyValue`, and `FileMetadata`; `FileMetadata` has helpers for mod time, receive-only changes, directories, conflict flags, and invalid flags.

## State And Persistence
This interface describes persisted file index state, block indexes, folder/device metadata, index IDs, mtime mappings, and arbitrary KV data. Concrete implementations include SQLite and legacy migration readers.

## Dependencies And Integration Points
It depends on Go `iter`, `time`, Syncthing config pull order, protocol types, and `suture` service lifecycle. The interface is consumed by the model, scanner, puller, API, migration, metrics wrapper, and observed pending-device/folder database.

## Risks And Test Signals
Iterator APIs require callers to consume the sequence and then call the returned error function; missed error checks can hide database failures. Some iterators return lightweight `FileMetadata` while others return full `FileInfo`, which callers must not confuse. Implementations should share contract tests for missing folders, iterator early termination, sequence ordering, block index behavior, and `WithSkipBlockIndex`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/metrics.go -->
# sources/sync-backup/syncthing/internal/db/metrics.go

## Purpose
This file provides a Prometheus instrumentation wrapper for the `DB` interface, measuring current operations, total operation time, operation counts, and number of updated files.

## Important APIs, Control Flow, And State
`MetricsWrap(db DB) DB` returns `metricsDB`, which embeds the wrapped database. `account(folder, op)` increments `syncthing_db_operations_current`, records a start time, and returns a deferred closure that adds elapsed seconds, increments total operation count, and decrements current operations. Most `DB` and `KV` methods are overridden to defer `account` and delegate to `m.DB`. `Update` also adds `len(fs)` to `syncthing_db_files_updated_total`.

## Dependencies And Integration Points
It depends on Prometheus `promauto`, `config.PullOrder`, protocol types, and the local `DB` contract. It should wrap concrete databases close to construction so all consumers report consistent metrics.

## Risks And Test Signals
Iterator-returning methods measure only iterator creation, not full iteration duration. This is important when interpreting metrics for large scans. The `Update` method uses `defer metricTotalFilesUpdatedCount.WithLabelValues(folder).Add(...)`; the metric increments after the update returns regardless of success, because the defer is registered before the delegate call. Tests should confirm wrapper delegation, labels, and whether failed updates should count as updated-file attempts.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/observed.go -->
# sources/sync-backup/syncthing/internal/db/observed.go

## Purpose
This file implements storage for observed but not yet accepted devices and folders. It backs pending devices/folders shown in the GUI and API, using the generic database `KV` interface.

## Important APIs, Control Flow, And State
`ObservedDB` wraps `KV`. `ObservedFolder` stores time, label, receive-encrypted, and remote-encrypted flags and converts to/from protobuf wire types. `ObservedDevice` stores time, name, and address. `AddOrUpdatePendingDevice` writes `device/<deviceID>`, `RemovePendingDevice` deletes it, and `PendingDevices` enumerates `device/` keys, parsing device IDs and protobuf values. Folder methods use keys `folder/<deviceID>/<folderID>`; they can add/update, remove a specific folder/device pair, remove all offers for a folder, list all pending folders, or list only those for one device. Invalid entries are deleted as a side effect during enumeration.

## State And Persistence
State is persisted in the generic KV store as protobuf-encoded `dbproto.ObservedDevice` and `dbproto.ObservedFolder` values. Times are truncated to seconds when adding pending devices and stored as protobuf timestamps.

## Dependencies And Integration Points
It depends on `dbproto`, `protocol.DeviceID`, protobuf marshal/unmarshal, and `timestamppb`. It integrates with cluster pending-device/folder REST endpoints and GUI pending maps.

## Risks And Test Signals
Enumeration repairs invalid keys by deleting them, which is practical for ephemeral pending state but means read paths mutate storage. `RemovePendingFolder` scans all folder entries and deletes matching folder IDs across devices. The `mustMarshal` helper panics on marshal failure, acceptable for generated protobuf messages but still a hard failure. Tests should cover invalid key cleanup, invalid protobuf cleanup, per-device filtering, all-device removal, and JSON field compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/observed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/backend/backend.go -->
# sources/sync-backup/syncthing/internal/db/olddb/backend/backend.go

## Purpose
This file defines the legacy database backend abstraction used for read-only access to old Syncthing LevelDB databases during migration or compatibility operations.

## Important APIs, Control Flow, And State
It defines `CommitHook`, `Reader`, `Writer`, `ReadTransaction`, `WriteTransaction`, `Iterator`, and `Backend`. `Reader` supports key lookups and prefix/range iterators. `WriteTransaction` describes legacy writable transaction behavior, including `Checkpoint` and `Commit`, although the current LevelDB reader implementation is read-only. `IsClosed` and `IsNotFound` normalize sentinel errors. `releaser` wraps a close wait group with `sync.Once`, and `closeWaitGroup` prevents new operations after `CloseWait` while waiting for active snapshots to release.

## Dependencies And Integration Points
It depends on `errors` and `sync`. The LevelDB backend implements these interfaces. Legacy olddb code uses `Backend` and `ReadTransaction` to traverse old keys and reconstruct file metadata.

## Risks And Test Signals
The transaction documentation is broader than the read-only implementation in this subset, so maintainers must check concrete backend support before assuming writes exist. Correct close behavior depends on all transactions and iterators being released. Tests should cover `IsClosed`, `IsNotFound`, idempotent release, and `CloseWait` blocking until live readers finish while rejecting new readers.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_backend.go -->
# sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_backend.go

## Purpose
This file implements the legacy `backend.Backend` read API on top of goleveldb.

## Important APIs, Control Flow, And State
`leveldbBackend` holds a `*leveldb.DB`, a close wait group, and location string. `NewReadTransaction` creates a LevelDB snapshot through `newSnapshot`; snapshots acquire a releaser so `Close` can wait for them. Backend-level `Get`, `NewPrefixIterator`, and `NewRangeIterator` delegate to LevelDB. `leveldbSnapshot` exposes the same read methods against a stable snapshot and releases both snapshot and waitgroup slot in `Release`. `leveldbIterator.Error` wraps LevelDB iterator errors into backend sentinel errors.

## State And Persistence
Persistent state is the existing LevelDB database. This wrapper is read-only at the abstraction level in this repository path; it does not manage writes. Runtime state tracks live snapshots for safe close.

## Dependencies And Integration Points
It depends on `github.com/syndtr/goleveldb/leveldb`, iterators, and util ranges. It is constructed by `OpenLevelDBRO` and consumed by legacy olddb readers.

## Risks And Test Signals
Backend prefix/range iterators created directly on `leveldbBackend` are not tracked by `closeWG`, unlike snapshots, so callers should avoid closing concurrently with active direct iterators. Snapshot iterators must be released before releasing the snapshot. Tests should cover not-found/closed error mapping, snapshot consistency, range boundaries, prefix scans, and closing with live snapshots.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_open.go -->
# sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_open.go

## Purpose
This file opens legacy Syncthing LevelDB databases in read-only mode.

## Important APIs, Control Flow, And State
`OpenLevelDBRO(location)` constructs LevelDB options with `OpenFilesCacheCapacity` set to `dbMaxOpenFiles` and `ReadOnly` set to true, opens the database through `open`, and wraps it in `newLeveldbBackend`. `open` is a small seam around `leveldb.OpenFile`.

## Dependencies And Integration Points
It depends on goleveldb `leveldb` and `opt`. It integrates with olddb migration/read paths that need to inspect existing databases without modifying them.

## Risks And Test Signals
The file is intentionally small, but operational risk lies in read-only opening failing on corrupted or locked LevelDBs. The open-file cache is fixed at 100. Tests should cover opening a valid DB, missing path errors, read-only enforcement, and propagating LevelDB open errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_open.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/keyer.go -->
# sources/sync-backup/syncthing/internal/db/olddb/keyer.go

## Purpose
This file defines the legacy LevelDB key format and key construction/parsing helpers for old Syncthing database data.

## Important APIs, Control Flow, And State
The constants define prefix lengths and key type bytes for device files, global versions, block maps, statistics, virtual mtimes, folder/device indexes, index IDs, folder metadata, misc data, sequence index, need index, block lists, version vectors, and pending devices/folders. The `keyer` interface describes all key operations. `defaultKeyer` uses `smallIndex` maps for folder and device string-to-uint32 IDs. Each generated key writes a type byte and big-endian indexed IDs, hashes, sequence numbers, or names into a reused/resized byte slice. Typed key aliases expose prefix slicing helpers such as `WithoutName`, `WithoutHashAndName`, `Hash`, and `WithoutSequence`.

## State And Persistence
The key format is the persistent schema for legacy LevelDB data. Folder and device IDs are stored in small index key spaces and referenced by uint32 in compound keys. The `resize` helper allows efficient buffer reuse during scans.

## Dependencies And Integration Points
It depends on `encoding/binary` and the old `smallIndex`. Legacy transactions use it to generate range boundaries and dereference file records, block lists, versions, mtimes, and pending state.

## Risks And Test Signals
Key parsing assumes correct key lengths and will panic on malformed short keys. `smallIndex.ID` now panics for missing IDs, suitable for read-only migration when indexes must already exist but dangerous if used for writes. `DeviceFromIndexIDKey` appears to use `folderIdx.Val` instead of `deviceIdx.Val`, which is a notable correctness risk unless intentionally preserving a legacy quirk. Tests should pin exact byte layouts, range prefix helpers, round trips for all key types, malformed key handling, and the index-ID device parser behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/keyer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/lowlevel.go -->
# sources/sync-backup/syncthing/internal/db/olddb/lowlevel.go

## Purpose
This file creates the low-level legacy database wrapper around a backend and exposes folder listing plus virtual mtime iteration.

## Important APIs, Control Flow, And State
`deprecatedLowlevel` embeds `backend.Backend` and holds `folderIdx`, `deviceIdx`, and the `keyer`. `NewLowlevel` constructs small indexes for folder and device index key spaces and creates a default keyer. `ListFolders` returns sorted folder index values. `IterateMtimes` scans keys with `KeyTypeVirtualMtime`, decodes the folder ID from the key, treats the remainder as the filename, splits the value into two binary-marshaled `time.Time` values, and calls the supplied callback for each valid mapping.

## State And Persistence
State is read from the old LevelDB backend and cached in small indexes. Virtual mtime values are persisted as concatenated binary time encodings.

## Dependencies And Integration Points
It depends on `encoding/binary`, `time`, and the legacy backend. Migration code can use it to enumerate folders and mtime mappings from old databases.

## Risks And Test Signals
`IterateMtimes` silently skips unknown folder IDs and time-unmarshal failures, which keeps migration robust but can hide data loss. It assumes values split exactly into two binary time encodings. Tests should cover folder index loading, sorted `ListFolders`, valid mtime decoding, invalid values, unknown folder IDs, callback error propagation, and iterator errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/lowlevel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/set.go -->
# sources/sync-backup/syncthing/internal/db/olddb/set.go

## Purpose
This file provides a small legacy file-set abstraction for reading old database file sequences with native filename conversion.

## Important APIs, Control Flow, And State
`deprecatedFileSet` stores a folder string and low-level database reference. `Iterator` is a callback receiving `protocol.FileInfo`. `NewFileSet` constructs the wrapper. `Snapshot` opens a read-only transaction and stores the folder. `Snapshot.Release` closes the transaction. `WithHaveSequence(startSeq, fn)` iterates sequence-indexed files from the snapshot transaction and wraps the callback with `nativeFileIterator`, which converts file names through `osutil.NativeFilename` before yielding.

## State And Persistence
No new persistence is introduced; snapshots read old database state. Runtime state is the active read-only transaction.

## Dependencies And Integration Points
It depends on `osutil` and `protocol`. It integrates with olddb transaction code and migration paths that need sequence-ordered local file metadata in native path form.

## Risks And Test Signals
Callers must release snapshots. The abstraction only exposes sequence iteration in this subset. Tests should verify snapshot release, sequence start behavior, native filename conversion, early callback termination, and error propagation from the transaction.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/smallindex.go -->
# sources/sync-backup/syncthing/internal/db/olddb/smallindex.go

## Purpose
This file implements a small in-memory bidirectional index used by the legacy database reader to map persisted uint32 IDs to folder/device string values.

## Important APIs, Control Flow, And State
`smallIndex` holds a backend, key prefix, `id2val`, `val2id`, `nextID`, and mutex. `newSmallIndex` constructs maps and immediately calls `load`. `load` scans the prefix key space, decodes the uint32 ID from the key suffix, stores non-empty values in both maps, and advances `nextID` past the largest observed ID. `ID` returns an existing ID for a value or panics on missing values. `Val` returns the value for an ID. `Values` returns sorted values.

## State And Persistence
Persistent state is stored in old LevelDB index key spaces. Empty values are treated as deleted entries. Runtime state is an in-memory cache protected by a mutex.

## Dependencies And Integration Points
It depends on `encoding/binary`, `slices`, `sync`, and the old backend. `defaultKeyer` uses these indexes to encode and decode old compound keys.

## Risks And Test Signals
`ID` no longer allocates or persists missing IDs despite its older comment, and instead panics. That is appropriate for read-only migration but should be documented in callers. `load` panics on iterator creation failure and does not check `it.Error()` after iteration, so load-time iterator errors may be missed. Tests should cover deleted entries, sorted values, ID/Val round trips, missing ID panic, and iterator error behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/smallindex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/transactions.go -->
# sources/sync-backup/syncthing/internal/db/olddb/transactions.go

## Purpose
This file implements read-only legacy transactions that unmarshal old database file records and follow indirections for block lists and version vectors.

## Important APIs, Control Flow, And State
`readOnlyTransaction` embeds `backend.ReadTransaction` and carries a `keyer`. `deprecatedLowlevel.newReadOnlyTransaction` opens a backend snapshot and wraps it. `getFileByKey` and `getFileTrunc` fetch bytes by key, translate not-found to `(false, nil)`, unmarshal full or truncated file info, and fill indirect data. `unmarshalTrunc` handles `dbproto.FileInfoTruncated` or BEP `FileInfo`. `fillFileInfo` loads block lists through `BlocksHash` and version vectors through `VersionHash`. `fillTruncated` loads only version vectors. `withHaveSequence` creates sequence range keys from `startSeq` to `maxInt64`, iterates sequence entries, resolves each value as a device-file key, and calls the supplied iterator.

## State And Persistence
It reads old persisted protobuf records, indirect block-list records, and version-vector records. It does not mutate state.

## Dependencies And Integration Points
It depends on protobuf, generated BEP/dbproto types, protocol conversion helpers, and the old backend. It is used by `deprecatedFileSet` snapshots and migration code.

## Risks And Test Signals
Missing indirect block lists are wrapped in `blocksIndirectionError`, while missing top-level files are skipped. Corrupt protobuf values abort iteration. Sequence index values must point to valid file keys. Tests should cover full and truncated unmarshalling, missing/corrupt block and version indirections, range iteration boundaries, early iterator stop, and backend iterator errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/olddb/transactions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/basedb.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/basedb.go

## Purpose
This file contains shared SQLite database opening, schema migration, statement caching, template expansion, and maintenance helpers used by main and folder databases.

## Important APIs, Control Flow, And State
`baseDB` holds path metadata, an `sqlx.DB`, update checkpoint counters, a prepared-statement cache, and SQL template input values. `openBase` builds a file URI with common SQLite options, opens the DB, sets connection limits, applies pragmas, initializes `baseDB`, then uses one dedicated connection with foreign keys disabled and legacy alter table enabled to run schema and migrations inside a transaction. It filters migration scripts by schema version, reruns schema scripts after migrations, checks foreign keys when migrations ran, records `currentSchemaVersion`, commits, and optionally vacuums/optimizes. `stmt` caches prepared statements after template expansion. `runScripts` reads embedded SQL files by glob and splits statements on `\n;`. Schema version helpers persist and read migration metadata.

## State And Persistence
Persistent state includes SQLite schema, migration history, indexes/triggers from embedded SQL, and WAL/checkpoint side effects. Runtime state includes cached prepared statements protected by an RW mutex.

## Dependencies And Integration Points
It depends on `sqlx`, embedded SQL files, `build.LongVersion`, protocol flag constants used in SQL templates, logging, and SQLite driver constants from other package files. It underpins main DB and per-folder DB opening.

## Risks And Test Signals
`runScripts` depends on a repository convention that statement separators are lines beginning with semicolon; SQL files must preserve this. `stmt` caches by unexpanded template string, so template input must be stable after open. `Close` locks update and statement mutexes before closing statements and DB. Tests should cover path URI conversion on Windows/UNC paths, migration ordering, ignored script failures, foreign-key checks, statement cache concurrency, template expansion, and vacuum/checkpoint behavior after migration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/basedb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_bench_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_bench_test.go

## Purpose
This file contains performance benchmarks and long-running size/drop tests for the SQLite database implementation.

## Important APIs, Control Flow, And State
`BenchmarkUpdate` opens a temporary DB, preloads increasingly large local datasets, logs file/block throughput, and runs sub-benchmarks for inserting local files, replacing blocks, replacing same files, inserting remote files, global lookups, sequence iteration, block hash lookups, device sequence reads, remote need iteration, and local need ordering. It uses generated `protocol.FileInfo` values and reports custom `files/s` and `blocks/s` metrics. `TestBenchmarkDropAllRemote` is a slow opt-in test gated by `LONG_TEST`, fills local and remote state, and times `DropAllFiles` for a remote device. `TestBenchmarkSizeManyFilesRemotes` is another opt-in long test that simulates 100k files shared by 31 devices and logs database size.

## State And Persistence
The tests create temporary SQLite databases and folder databases, then fill them with synthetic file, block, version-vector, and device state. They close and measure on-disk directories where needed.

## Dependencies And Integration Points
It depends on the SQLite `Open` path, test data helpers such as `genFile`/`genBlocks` and `folderID` from package tests, protocol/config types, `timeutil`, `osutil.DirSize`, and random string generation.

## Risks And Test Signals
These are performance signals, not correctness assertions for normal CI. The benchmark grows the dataset up to 200k local files and can be expensive. Long tests require `LONG_TEST` and are skipped in short/default runs. They are useful for detecting update/index/query regressions, block index growth, remote-device scaling costs, and database size changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_folderdb.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_folderdb.go

## Purpose
This file implements the top-level SQLite `DB` methods that delegate folder-scoped file-index operations to lazily opened per-folder databases.

## Important APIs, Control Flow, And State
`getFolderDB(folder, create)` checks the open-folder map, reads or creates a folder database name in the main `folders` table, creates a new name from folder index plus random slug when needed, opens the folder DB, and caches it. `Update` applies `db.UpdateOption` values and delegates to `folderDB.Update`. The remaining methods delegate block index, file lookup, global/local iterators, needed-file iterators, cleanup, device lists, remote sequences, counts, index IDs, device sequences, mtime mapping, debug output, and folder/device drops to the appropriate folder DB. Missing folders usually return empty iterators, zero counts, nil slices/maps, false lookups, or nil errors. `forEachFolder` iterates all known folders and runs a callback, retaining the first error.

## State And Persistence
The main DB stores folder IDs and per-folder database filenames. Each folder DB stores file, block, sequence, count, index ID, and mtime data for that folder. Folder DBs are opened lazily and cached in `s.folderDBs` under `folderDBsMut`; creation also uses `updateLock`.

## Dependencies And Integration Points
It depends on `internal/db`, config pull ordering, protocol IDs, logging, random slugs, and `folderDB` methods implemented in other SQLite files. It is the concrete implementation of much of `db.DB`.

## Risks And Test Signals
Missing-folder behavior varies slightly by return type and includes `nil, nil` for some slices/maps; callers must tolerate that. Lazy creation means read paths should pass `create=false` to avoid accidental persistent state. Folder DB filename uniqueness depends on folder index plus random slug. Tests should cover concurrent `getFolderDB`, missing-folder read semantics, creation persistence, all delegated methods, `forEachFolder` first-error handling, and mtime/index ID behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_folderdb.go -->
