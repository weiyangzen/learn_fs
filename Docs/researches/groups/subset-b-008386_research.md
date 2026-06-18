# subset-b-008386 FoundationDB Go/Java Binding Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_layer.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_layer.go

Purpose: implements the Go directory layer root and core operations for creating, opening, listing, moving, and deleting directory paths. `directoryLayer` binds a metadata subspace (`nodeSS`), content allocation subspace (`contentSS`), high-contention allocator, root node, manual-prefix policy, and current partition path.

Important APIs: `NewDirectoryLayer`, `CreateOrOpen`, `Create`, `CreatePrefix`, `Open`, `Exists`, `List`, `Move`, `Remove`, plus helpers `find`, `contentsOfNode`, `checkVersion`, `isPrefixFree`, `nodeContainingKey`, and recursive removal helpers. `createOrOpen` is the central state machine: check layer version, reject illegal manual prefixes/root opens, resolve existing nodes, delegate into partitions, validate layer bytes, allocate or validate prefixes, ensure parents, then persist parent `_SUBDIRS` and node `layer` keys.

State and persistence: directory metadata is stored under `nodeSS`, with root metadata at `rootNode`, child name to prefix mappings under `_SUBDIRS`, per-node layer bytes under `node/<prefix>/layer`, and directory version under root `version`. Directory contents live at the allocated prefix itself. Removing clears both metadata and the content prefix range.

Dependencies and integration: relies on `fdb.Transactor`/`ReadTransactor`, `subspace`, `tuple`, `highContentionAllocator`, and partition/subspace wrappers. Partitions are represented by layer string `partition` and create nested directory layers whose metadata is under `prefix + 0xFE`.

Risks: many helpers use `MustGet`, so asynchronous FDB errors become panics recovered only when called inside transaction helpers. Prefix allocation correctness depends on both `isRangeEmpty` and `isPrefixFree`; manual prefixes can create conflicts if policy checks drift. Recursive delete can be large and transaction-size sensitive. `find` stops at partition boundaries, so path math must remain exact.

Test signals: no direct test in this subset, but integration is exercised by directory-layer users elsewhere. Risk areas need partition delegation, move/delete recursion, incompatible directory-version, and manual-prefix conflict coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_partition.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_partition.go

Purpose: adapts a nested `directoryLayer` as a directory partition. A partition is a directory object but deliberately not a usable key subspace at its root.

Important APIs: `directoryPartition` embeds `directoryLayer` and stores `parentDirectoryLayer`. It implements subspace methods (`Sub`, `Bytes`, `Pack`, `PackWithVersionstamp`, `Unpack`, `Contains`, `FDBKey`, `FDBRangeKeys`, `FDBRangeKeySelectors`) by panicking, returns layer bytes `partition`, and routes `MoveTo`, `Remove`, and `Exists` to either the parent or nested layer via `getLayerForPath`.

Control flow: empty relative path operations refer to the partition directory in the parent layer; non-empty paths refer to the nested layer. `MoveTo` uses the common `moveTo` helper against the parent path. `Remove` and `Exists` compute partition-relative paths with `partitionSubpath`.

State and persistence: this file does not write state directly. It controls which `directoryLayer` writes metadata and content for partition-root versus partition-child operations.

Dependencies and integration: depends on `fdb`, `subspace`, `tuple`, and helpers from `directory_layer.go`. It is created by `contentsOfNode` when a node layer equals `partition`.

Risks: panic-based rejection means callers must not treat partition roots as normal subspaces. Incorrect path routing would delete/check the wrong layer. Type assertions in callers assume partition values satisfy `DirectorySubspace` but not normal subspace behavior.

Test signals: should be covered by directory partition tests: root subspace method panics, partition-child operations delegate inside partition, and root removal/existence uses the parent layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_partition.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_subspace.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_subspace.go

Purpose: represents a concrete directory that can also be used as a FoundationDB subspace for application key/value content.

Important APIs: `DirectorySubspace` composes `subspace.Subspace` and `Directory`. `directorySubspace` stores the underlying subspace, directory layer, absolute path, and layer bytes. It forwards `CreateOrOpen`, `Create`, `CreatePrefix`, `Open`, `Move`, `Remove`, `Exists`, and `List` into the owning `directoryLayer` after combining the receiver path and relative path with `partitionSubpath`. `MoveTo` delegates to common `moveTo`; `GetLayer` and `GetPath` expose metadata; `String` prints path and raw prefix.

Control flow: this file is mostly an adapter. User calls on a directory subspace are translated into absolute directory-layer paths while all key packing/range behavior comes from the embedded `subspace.Subspace`.

State and persistence: no direct writes; persistence happens in `directoryLayer`. The stored `path` and `layer` are client-side descriptors of metadata read from FDB.

Dependencies and integration: integrates directory APIs with the lower-level `subspace` package and `fdb.Printable`. Returned by `directoryLayer.contentsOfNode` for non-partition directories.

Risks: path concatenation must remain consistent with partition semantics. Because the struct embeds `subspace.Subspace`, accidental copying is cheap but shares the same raw prefix. The returned `GetPath` slice is not cloned, so external mutation could surprise callers if they retain and modify it.

Test signals: expected coverage includes string rendering, relative directory operations, movement to absolute paths, and preservation of layer bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_subspace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/node.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/node.go

Purpose: small internal representation of a directory metadata node while resolving paths.

Important APIs: `node` stores a metadata subspace, resolved path, original target path, and cached layer future. `exists` checks for non-nil subspace. `prefetchMetadata` starts the layer read. `layer` lazily reads `node.subspace.Sub("layer")`. `isInPartition` checks whether the node exists, has layer `partition`, and whether empty subpaths are included. `getPartitionSubpath` returns unresolved path suffix. `getContents` materializes the node as a `DirectorySubspace`.

Control flow: `directoryLayer.find` creates nodes as it walks child mappings. A node can stop resolution early when it does not exist or when it is a partition boundary.

State and persistence: reads only the node `layer` key. It caches the `FutureByteSlice`, not the decoded byte slice, so repeated calls share the same FDB future.

Dependencies and integration: uses `fdb.FutureByteSlice` and `subspace.Subspace`; tightly coupled to `directory_layer.go` partition and contents logic.

Risks: `isInPartition` calls `MustGet`, so FDB read errors panic. Calling `isInPartition` before `prefetchMetadata`/`layer` would dereference nil `_layer`; current callers prefetch or call layer during find. Partition suffix slicing assumes `targetPath` is at least as long as `path`.

Test signals: indirect; valuable tests would simulate missing nodes, normal nodes, partition boundaries, and layer-read errors in transactional wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/doc.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/doc.go

Purpose: package-level documentation for the Go FoundationDB binding.

Important content: describes installation requirement for the C client, `APIVersion` selection, opening databases, transaction-based reads/writes, futures, panic-based `MustGet` convenience, retry behavior in `Database.Transact`, goroutine caveats, range streaming modes, and atomic operations.

Control flow explained: basic usage calls `MustAPIVersion`, opens a database, invokes `db.Transact`, performs writes/async reads, and lets `Transact` commit/retry. Panic flow is documented: `MustGet` panics with `fdb.Error`; `Transact` recovers FDB errors for retry/final return and re-panics non-FDB values.

State and persistence: no executable state. It documents that transactions are the persistence boundary and atomic operations transform values at commit.

Dependencies and integration: documents public package semantics used by `fdb.go`, `database.go`, `transaction.go`, `futures.go`, and generated mutation methods.

Risks: documentation must track API version and current atomic operation list; stale examples can mislead users. It warns that returning futures from transaction functions is unsafe because the transaction can be finalized after `Transact` returns.

Test signals: examples in `fdb_test.go` complement these docs. `go test` examples can catch output drift, but much documented behavior requires a running FDB cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/error_codes_generated.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/error_codes_generated.go

Purpose: generated sentinel variables for FoundationDB error codes, enabling idiomatic `errors.Is` checks against `fdb.Error`.

Important APIs: declares many exported vars such as `ErrTransactionTooOld`, `ErrNotCommitted`, `ErrInvalidOption`, `ErrAPIVersionUnset`, directory errors, backup/restore errors, encryption/auth errors, and `ErrGRPCError`, each as `Error{Code: <number>}` with source descriptions.

Control flow: no runtime logic beyond variable initialization. The file is generated by `internal/gen_errors/main.go` from `flow/include/flow/error_definitions.h`.

State and persistence: process-global immutable-by-convention variables. They are vars rather than consts because `Error` is a struct, so code could mutate them accidentally.

Dependencies and integration: depends on `Error` from `errors.go` implementing `Is`. Used by callers and tests with `errors.Is(err, fdb.ErrTransactionTooOld)`. Keeps generated Go names aligned with C/Flow error macro names.

Risks: generated output must remain synchronized with the C client/server error definitions. Because these are vars, accidental reassignment in package or tests would corrupt matching. Naming quality depends on the generator initialism map. Duplicate or changed C codes could alter matching semantics.

Test signals: `errors_test.go` verifies `errors.Is` with a representative sentinel and wrapped value/pointer errors, but does not validate completeness against the header.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/error_codes_generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/errors.go

Purpose: defines the Go wrapper for low-level FoundationDB C API errors.

Important APIs: `Error{Code int}`, `Error.Error()`, and `Error.Is(target error)`. `Error()` calls `fdb_get_error` through cgo to include the C library message. `Is` matches both value and pointer `Error` targets with equal codes.

Control flow: any C API function returning nonzero `fdb_error_t` is wrapped as `Error{int(err)}` by surrounding files. Panic recovery in `panicToError` also recognizes this concrete type.

State and persistence: no persistent state. Error text is fetched from the linked C library at call time.

Dependencies and integration: cgo includes `foundationdb/fdb_c.h` with `FDB_API_VERSION 800`; generated sentinels depend on this type. `go:generate` points to `internal/gen_errors/main.go`.

Risks: `panicToError` only catches value `Error`, not `*Error`; this matches current `MustGet` panics but is a trap if future code panics pointers. `Error()` depends on the C library being loadable and initialized enough for message lookup. Code values must remain compatible with linked FoundationDB client versions.

Test signals: `errors_test.go` exercises wrapping and `errors.Is` matching for value/pointer targets and wrapped values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/errors_test.go

Purpose: tests Go error wrapping and sentinel matching semantics for `fdb.Error`.

Important tests: `TestErrorWrapping` selects API version 800, opens the default database, and passes nil, value/pointer FDB errors, wrapped FDB errors, and a custom error through `db.ReadTransact`, expecting the same error object/value to be returned. `TestErrorIs` verifies `errors.Is` against `ErrTransactionTooOld`, pointer targets, wrapped value/pointer errors, wrong codes, and unrelated errors.

Control flow: `ReadTransact` is used to confirm retryable machinery does not unwrap or replace non-retry path errors returned by the user function. `errors.Is` targets the `Error.Is` implementation directly.

State and persistence: requires a selected API version and a default database for `TestErrorWrapping`, but does not intentionally mutate data.

Dependencies and integration: depends on `fdb.go` API selection/opening, `database.go` read transaction behavior, generated `ErrTransactionTooOld`, and Go standard `errors`.

Risks: `TestErrorWrapping` requires an accessible FDB cluster/default cluster file, so it is integration-like and can fail in minimal environments. It compares interface error values directly; wrapping cases are stable because returned input should be identical, not merely equivalent.

Test signals: strong coverage for the new `errors.Is` contract; limited coverage across only one code value.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb.go

Purpose: top-level Go binding setup: API version selection, network lifecycle, database opening helpers, key types, printable byte formatting, and panic-to-error conversion.

Important APIs: `APIVersion`, `MustAPIVersion`, `IsAPIVersionSelected`, `GetAPIVersion`, network options, deprecated `StartNetwork`/`StopNetwork`, `OpenDefault`, `OpenDatabase`, `OpenWithConnectionString`, deprecated `Open`, `CreateCluster`, `KeyConvertible`, `Key`, `Printable`, and internal `executeWithRunningNetworkThread`.

Control flow: `APIVersion` validates once under `networkMutex` and calls `fdb_select_api_version_impl`. Database creation checks API selection, starts the FDB network thread lazily via `executeWithRunningNetworkThread`, calls C creation APIs, caches `OpenDatabase` handles by cluster file, and wraps C pointers in `Database`.

State and persistence: package globals track selected API version, network started/stopped state, network waitgroup, and cached open databases. Database handles own C resources; `Close` in `database.go` removes cached entries.

Dependencies and integration: cgo against `fdb_c.h`; integrates with `Database`, `Cluster`, generated error sentinels, and C network lifecycle.

Risks: API version is process-global and irreversible. Network stop is terminal. `openDatabases.Load` then create/store is not singleflight, so concurrent opens for the same new cluster file may create duplicate handles before last store wins. `panicToError` catches only concrete `Error`. C library/header version mismatch is handled but still operationally sensitive.

Test signals: `fdb_test.go` covers examples, key formatting, default open, close/cache behavior, connection string path, and some network-dependent operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_darwin.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_darwin.go

Purpose: platform-specific cgo flags for macOS builds of the Go binding.

Important content: package `fdb`; cgo `CFLAGS` adds `/usr/local/include`; cgo `LDFLAGS` adds `/usr/local/lib` and runtime path `/usr/local/lib`.

Control flow/state: no Go runtime logic, no persistence.

Dependencies and integration: affects cgo compilation/linking for files importing `C` in the same package. It assumes FoundationDB headers and `libfdb_c` are installed in Homebrew/default `/usr/local` style locations.

Risks: Apple Silicon installations often use `/opt/homebrew`, so this may not locate libraries without external flags. Runtime rpath is convenient but can mask version mismatches. It has no build tag in the file body, so platform selection relies on `_darwin.go` suffix.

Test signals: only build/link tests on Darwin validate this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_freebsd.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_freebsd.go

Purpose: platform-specific cgo flags for FreeBSD builds.

Important content: package `fdb`; `CFLAGS` uses `/usr/local/include`; `LDFLAGS` uses `/usr/local/lib`.

Control flow/state: no runtime logic and no persistent state.

Dependencies and integration: participates in cgo package compilation based on `_freebsd.go` filename. Supplies include/library search paths for the FoundationDB C client.

Risks: no rpath is set, so runtime loader configuration must find `libfdb_c`. Assumes conventional local install paths. Build failures will appear as missing headers or link libraries.

Test signals: validated by FreeBSD build/link coverage only.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_test.go

Purpose: examples and integration tests for the public Go `fdb` package.

Important tests/examples: `ExampleOpenDefault`, `TestVersionstamp`, `TestEstimatedRangeSize`, `TestReadTransactionOptions`, `ExampleTransactor`, `ExampleReadTransactor`, `ExamplePrefixRange`, `ExampleRangeIterator`, `TestKeyToString`, `ExamplePrintable`, `TestDatabaseCloseRemovesResources`, `ExampleOpenWithConnectionString`, skipped `TestGetClientStatus`, and `ExampleDatabase_GetClientStatus`.

Control flow: tests select API version 800, open default databases, demonstrate composable transactors/read transactors, create transactions, perform uncommitted example mutations/range scans, fetch versionstamp futures, read system keys with options, and verify database close removes cached handles.

State and persistence: examples intentionally avoid commits for data mutation examples. Some tests require a live FDB cluster and default or env-specified cluster configuration. `TestVersionstamp` does commit via `Transact` and writes `foo`.

Dependencies and integration: exercises `fdb.go`, `database.go`, `transaction.go`, `range.go`, `subspace`, generated options, futures, and C client integration.

Risks: tests are environment-sensitive and can mutate default database (`foo`) unless isolated. API version selection is global, so tests assume consistent version. Examples using uncommitted transactions rely on read-your-writes semantics.

Test signals: covers public examples, key formatting, close/cache semantics, versionstamp and range behavior; multi-version client status test is explicitly skipped.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_windows.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_windows.go

Purpose: Windows-specific cgo flags for the Go binding.

Important content: package `fdb`; `CFLAGS` points to `C:/Program Files/foundationdb/include`; `LDFLAGS` points to `C:/Program Files/foundationdb/bin` and links `-lfdb_c`.

Control flow/state: no runtime logic or persistence.

Dependencies and integration: selected by `_windows.go` suffix during Go builds. Supplies default FoundationDB installer paths for cgo.

Risks: assumes installation path and architecture. Spaces in paths are quoted, but custom installs need external cgo flags. Runtime DLL search must find `fdb_c.dll`.

Test signals: Windows build/link and runtime smoke tests validate this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/futures.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/futures.go

Purpose: wraps FoundationDB C futures in Go interfaces and typed future implementations.

Important APIs: `Future`, `FutureByteSlice`, `FutureKey`, `FutureNil`, `FutureKeyArray`, `FutureInt64`, `FutureStringSlice`, plus internal `future`, `newFuture`, `BlockUntilReady`, `IsReady`, `Cancel`, and C callback bridge `go_set_callback`.

Control flow: C futures are wrapped with finalizers that destroy them. Blocking uses a mutex passed to a C callback that unlocks when ready. Typed `Get` methods block, call the appropriate `fdb_future_get_*`, copy C memory into Go values, and convert C errors to `Error`. Byte/key futures use `sync.Once` to cache results; others fetch on each `Get`.

State and persistence: no database persistence. Runtime state includes C future pointers, parent db/transaction references to keep owners alive, cached values/errors, and finalizers.

Dependencies and integration: cgo links `fdb_c` and math library. Used by transaction/database/locality APIs. `runtime.KeepAlive` prevents premature finalization.

Risks: C struct layout assumptions in `stringRefToSlice` and array pointer arithmetic are ABI-sensitive. Some futures do not call `fdb_future_release_memory`, which should be checked against C API ownership rules. Finalizers make cleanup nondeterministic; explicit cancel can still leave resources until GC. Callback/mutex pattern must avoid deadlocks if future callback behavior changes.

Test signals: indirectly exercised by transaction/range/versionstamp tests; no focused future lifecycle or cancellation tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/futures.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/generated.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/generated.go

Purpose: generated public option, mutation, streaming mode, conflict range, and error predicate API surface from FoundationDB option definitions.

Important APIs: `int64ToBytes`; many `NetworkOptions`, `DatabaseOptions`, and `TransactionOptions` setters; mutation helpers on `Transaction` such as `Add`, `BitAnd`, `BitOr`, `SetVersionstampedKey`, `SetVersionstampedValue`, `ByteMin`, `CompareAndClear`; `StreamingMode`; internal `conflictRangeType`; `ErrorPredicate`.

Control flow: option setters call receiver `setOpt` with numeric option codes and encoded parameter bytes. Mutation methods call `t.atomicOp`. Integer parameters are little-endian `int64`.

State and persistence: option setters mutate FDB network/database/transaction configuration in the C client. Atomic operations are persisted only if the transaction commits. Generated enums encode C API constants.

Dependencies and integration: generated by `internal/translate_fdb_options.go`; depends on receiver types and helpers from `fdb.go`, `database.go`, and `transaction.go`.

Risks: generated code must match the C API version and option catalog. Some option semantics are version-dependent. `strings.Title` in the generator is deprecated and may produce naming quirks. Atomic operation warnings, especially append-if-fits and versionstamp offsets, need user attention.

Test signals: tests call `SetAccessSystemKeys` and versionstamp mutations indirectly; no exhaustive generated option/mutation tests here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/keyselector.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/keyselector.go

Purpose: defines Go representations of FoundationDB key selectors.

Important APIs: `Selectable`, `KeySelector`, `FDBKeySelector`, and constructors `LastLessThan`, `LastLessOrEqual`, `FirstGreaterThan`, `FirstGreaterOrEqual`.

Control flow: constructors fill the selector triple `(key, orEqual, offset)` using FoundationDB's standard selector formulas. Transactions later convert these fields into C `fdb_transaction_get_key` and range selector arguments.

State and persistence: no state or persistence. Selectors are immutable value descriptions.

Dependencies and integration: depends on `KeyConvertible`. Used by `Range`, `SelectorRange`, tuple/subspace range selector implementations, and transaction get/range APIs.

Risks: off-by-one semantics are subtle; constructor field values must exactly match FoundationDB selector definitions. Passing nil `KeyConvertible` would panic later when converting. Selector resolution can read database state and conflict depending on transaction options.

Test signals: range examples and iterator tests indirectly exercise `FirstGreaterOrEqual` and `FirstGreaterThan`; direct selector resolution tests would strengthen coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/keyselector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/range.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/range.go

Purpose: defines range abstractions and range-read iteration behavior.

Important APIs: `KeyValue`, `RangeOptions`, `Range`, `ExactRange`, `KeyRange`, `SelectorRange`, `RangeResult`, `RangeIterator`, `Strinc`, and `PrefixRange`.

Control flow: `RangeResult.Iterator` creates a `RangeIterator` around the first future. `Advance` waits for a pending batch; `Get` returns current item and triggers `fetchNextBatch` at batch boundaries. `fetchNextBatch` updates begin/end selectors based on direction, decrements remaining limit, increments iteration, and calls `doGetRange`. `GetSliceWithError` forces modes optimized for exact/want-all reads.

State and persistence: no writes. Iterator tracks transaction pointer, selectors, range options, batch future, index, errors, and snapshot flag.

Dependencies and integration: uses `Transaction.doGetRange`, key selector helpers, and C range streaming modes from generated code.

Risks: iterator is explicitly not safe for concurrent use or copying. `fetchNextBatch` assumes at least one kv when called. Prefix helpers reject empty/all-0xFF prefixes; callers must handle errors. Range reads returned from `Transact` can outlive transactions and are documented unsafe.

Test signals: `ExamplePrefixRange` and `ExampleRangeIterator` cover basic prefix and iteration behavior. Edge cases such as reverse/limit/multi-batch/errors need additional coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/range.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/snapshot.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/snapshot.go

Purpose: exposes snapshot read behavior for an existing transaction.

Important APIs: `Snapshot`, `ReadTransact`, `Cancel`, `Snapshot`, `Get`, `GetKey`, `GetRange`, `GetReadVersion`, `GetDatabase`, `GetEstimatedRangeSizeBytes`, `GetRangeSplitPoints`, and `Options`.

Control flow: `Transaction.Snapshot` wraps the same internal transaction pointer. Snapshot read methods call the transaction helpers with snapshot flag set to 1/true, while size/split/read-version operations reuse non-mutating transaction helpers. `ReadTransact` recovers `Error` panics but does not retry.

State and persistence: no independent state; shares underlying transaction state and lifetime. Snapshot reads reduce conflict creation but still use the transaction's read version and read-your-writes configuration where applicable.

Dependencies and integration: satisfies `ReadTransaction` and `ReadTransactor`; used by composable read-only functions and directory prefix checks.

Risks: canceling a snapshot cancels the underlying transaction. Snapshot isolation is weaker, making invariants harder to reason about. Options returns transaction options, so callers can change the whole transaction via a snapshot handle.

Test signals: `ExampleReadTransactor` uses `rtr.Snapshot()` composition; broader tests should cover conflict behavior and cancellation side effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace.go

Purpose: implements the Go subspace layer, a tuple-prefixed key namespace abstraction.

Important APIs: `Subspace` interface, `AllKeys`, `Sub`, `FromBytes`, methods `Sub`, `Bytes`, `Pack`, `PackWithVersionstamp`, `Unpack`, `Contains`, `FDBKey`, `FDBRangeKeys`, `FDBRangeKeySelectors`, and helper `concat`.

Control flow: constructors create raw prefixes from tuple encodings or bytes. `Pack` appends tuple packing to the raw prefix. `Unpack` checks prefix membership then tuple-unpacks the suffix. Range methods return `[prefix+0x00, prefix+0xff)` selectors, representing tuple keys strictly inside the subspace.

State and persistence: subspaces are client-side byte prefixes. They do not persist metadata; they shape keys used by transactions.

Dependencies and integration: depends on `fdb` key/range interfaces and `tuple`. Used by directory layer, tests, and application code.

Risks: `Bytes` returns the internal slice directly, unlike `FromBytes` which clones input; external mutation of returned bytes can corrupt the subspace value. `Contains` only checks raw prefix, not tuple well-formedness. `AllKeys().FDBRangeKeys()` returns `[0x00,0xff)`, excluding keys outside tuple-style range endpoints.

Test signals: `subspace_test.go` verifies `String` formatting for a representative tuple prefix.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace_test.go

Purpose: focused unit test for subspace string formatting.

Important test: `TestSubspaceString` constructs `Sub([]byte("hello"), "world", 42, 0x99)`, formats it with `fmt.Sprint`, and expects a `Subspace(rawPrefix=...)` string with FoundationDB tuple type codes rendered through `fdb.Printable`.

Control flow/state: no database access. It exercises tuple packing, subspace construction, `String`, and printable byte escaping.

Dependencies and integration: depends on `subspace.Sub`, tuple encoding, and `fdb.Printable`.

Risks: the test is narrow; it will catch formatting/encoding changes for one mixed tuple but not `Pack`, `Unpack`, range endpoints, versionstamps, or mutation-safety of returned bytes.

Test signals: good fast unit signal for developer-facing diagnostics; should be complemented by round-trip and range tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/subspace/subspace_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/transaction.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/transaction.go

Purpose: implements transaction and read transaction APIs over the FoundationDB C transaction pointer.

Important APIs: `ReadTransaction`, `Transaction`, `transaction`, `TransactionOptions`, `Transact`, `ReadTransact`, `Cancel`, `SetReadVersion`, `Snapshot`, `OnError`, `Commit`, `Watch`, `Get`, `GetRange`, `GetEstimatedRangeSizeBytes`, `GetRangeSplitPoints`, `GetReadVersion`, `Set`, `Clear`, `ClearRange`, `GetCommittedVersion`, `GetVersionstamp`, `GetApproximateSize`, `Reset`, `GetKey`, conflict range/key methods, `Options`, and `LocalityGetAddressesForKey`.

Control flow: read methods allocate typed futures around C calls; writes and atomic operations mutate the transaction immediately client-side; commit returns a future. `Transact`/`ReadTransact` on an existing transaction provide composition and panic recovery but no retry/commit. Range reads translate `Range` selectors and `RangeOptions` into C arguments.

State and persistence: `transaction` owns `*C.FDBTransaction` and parent `Database`. Mutations persist only after successful `Commit`. Conflict ranges alter commit conflict behavior. Watches outlive the transaction after commit and must be canceled if unused.

Dependencies and integration: central consumer of futures, key selectors, range abstractions, generated options/mutations, and database retry logic.

Risks: using a transaction after commit/reset/cancel can fail; concurrent `Reset`/`Cancel` is documented unsafe. `AddReadConflictKey` uses key plus `0x00`, which is not the same as `Strinc` for all logical keyspaces but matches single-key conflict convention. Returning futures outside retry functions is unsafe. C pointer lifetime depends on finalization in database code.

Test signals: `fdb_test.go` exercises read options, versionstamps, range iteration, estimated range size, and transactor composition.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/transaction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple.go

Purpose: implements FoundationDB tuple encoding/decoding for Go values with lexicographic order preservation.

Important APIs/types: `TupleElement`, `Tuple`, `UUID`, `Versionstamp`, `IncompleteVersionstamp`, `Versionstamp.Bytes`, `Tuple.Pack`, `Tuple.PackWithVersionstamp`, `HasIncompleteVersionstamp`, `Unpack`, `FDBKey`, `FDBRangeKeys`, `FDBRangeKeySelectors`, and string renderers.

Control flow: `packer.encodeTuple` dispatches by Go type, writes type codes, escapes embedded nulls in byte/string values, encodes signed/unsigned/big integers in order-preserving form, adjusts float sign bits, encodes nested tuples and versionstamps, and records the single incomplete versionstamp offset. `PackWithVersionstamp` requires selected API version, exactly one incomplete versionstamp, and appends 2- or 4-byte little-endian offset depending on API version. Decoding mirrors type codes with size/error checks.

State and persistence: no database writes. Encoded bytes become durable keys or values when used by transactions/subspaces. Versionstamp placeholders are completed by FDB commit mutations.

Dependencies and integration: uses `fdb.KeyConvertible`, `fdb.GetAPIVersion`, and `fdb.Printable`; consumed by subspace and directory layers.

Risks: panics on unsupported types and invalid vanilla incomplete versionstamps. Some decode paths index ahead and rely on well-formed lengths; malformed short integer encodings need scrutiny. `findTerminator` assumes a terminator exists and can misbehave on malformed input. API-version-dependent versionstamp offsets are subtle.

Test signals: `tuple_test.go` provides golden packing, benchmark, and string-format coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple_test.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple_test.go

Purpose: validates tuple packing stability and tuple string rendering.

Important tests: deterministic random generator setup; golden load/write helpers for `testdata/tuples.golden`; representative tuple cases covering UUIDs, strings/bytes with nulls, integers, floats, doubles, booleans, nils, nested tuples, and large byte arrays. `TestTuplePacking` compares `Tuple.Pack` output against golden bytes unless `-update` is set. `BenchmarkTuplePacking` measures packing. `TestTupleString` checks rendering of bytes, strings, nested tuples, booleans, UUIDs, and versionstamps.

Control flow/state: uses gob-encoded golden data and optional update mode that rewrites the golden file. Random input is made deterministic with a local `rand.Rand` seed for Go 1.20+ stability.

Dependencies and integration: depends on tuple encoder, stringer, `fdb.Printable`, and local testdata.

Risks: update mode can bless regressions if used casually. Golden tests validate packing but not unpack round trips or malformed decode errors in this file. Randomly generated cases are deterministic but limited.

Test signals: strong regression signal for binary compatibility of tuple keys, which is critical for persistence and cross-language compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/tuple/tuple_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/internal/gen_errors/main.go -->
# sources/storage-engines/foundationdb/bindings/go/src/internal/gen_errors/main.go

Purpose: standalone generator for `fdb/error_codes_generated.go`.

Important APIs: build-ignored `main`, `errorRe`, `initialism` map, `errorDef`, `toPascalCase`, and `tmpl`. CLI flags `-in` and `-out` select the Flow error header and output Go file.

Control flow: opens input header, scans lines for `ERROR(name, code, "description")`, converts snake names into exported Go sentinel names with initialism handling, creates output file, and executes a template that emits vars of `Error{Code: ...}` with comments and regeneration instructions.

State and persistence: reads `flow/include/flow/error_definitions.h`; writes generated Go source. No runtime package state because file is `//go:build ignore`.

Dependencies and integration: used by `go generate` directive in `errors.go`; generated output depends on `fdb.Error`.

Risks: regexp ignores macro variants, escaped quotes, multiline definitions, or comments that do not match the simple pattern. It always opens an input path, so the default `"stdin"` is not actually stdin. Output creation is not atomic, so failures can leave partial files. Initialism map omissions affect public names.

Test signals: no direct tests in subset; `errors_test.go` indirectly validates generated sentinel usability for one code.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/internal/gen_errors/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/internal/translate_fdb_options.go -->
# sources/storage-engines/foundationdb/bindings/go/src/internal/translate_fdb_options.go

Purpose: generator translating XML `fdb.options` definitions into Go option setters, mutation methods, and enum constants in `fdb/generated.go`.

Important APIs: XML structs `Option`, `Scope`, `Options`; helpers `sanitize`, `writeOptString`, `writeOptBytes`, `writeOptInt`, `writeOptNone`, `writeOpt`, `translateName`, `writeMutation`, `writeEnum`; CLI `main`.

Control flow: reads XML from stdin or `-in`, unmarshals scopes, opens stdout or `-out`, writes file header and `int64ToBytes`, then handles scopes. `*Option` scopes emit receiver methods on `NetworkOptions`, `DatabaseOptions`, or `TransactionOptions`; `MutationType` emits `Transaction` atomic methods; other scopes emit enum types/constants, with `StreamingMode` shifted by +1 so iterator is zero and `ConflictRangeType` made unexported.

State and persistence: writes generated Go source; generated setters change C client configuration at runtime and mutations affect committed transaction state.

Dependencies and integration: depends on XML schema from FoundationDB vexillographer options. Generated output relies on `setOpt`, transaction `atomicOp`, and Go doc formatting.

Risks: uses deprecated `strings.Title`; output is not atomic; output file is not deferred closed on all paths. Name translation may mishandle initialisms compared with idiomatic Go. Hidden options are omitted, so generated API changes with upstream option visibility.

Test signals: no generator tests here; generated code is partly exercised by transaction option and versionstamp tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/internal/translate_fdb_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/CMakeLists.txt -->
# sources/storage-engines/foundationdb/bindings/java/CMakeLists.txt

Purpose: CMake build graph for FoundationDB Java bindings, JNI library, Java workload library, jars, javadoc, fat jar packaging, and optional JUnit/integration tests.

Important build APIs/targets: cache toggles `RUN_JAVA_TESTS`, `RUN_JUNIT_TESTS`, `RUN_JAVA_INTEGRATION_TESTS`; source lists `JAVA_BINDING_SRCS` and `JAVA_TESTS_SRCS`; `vexillographer_compile` target `fdb_java_options`; generated `ApiVersion.java`; native targets `fdb_java` and `java_workloads`; `add_jar(fdb-java)`, `create_javadoc`, `CopyJavadoc`, `foundationdb-tests`, `fdb-java-tests`, `fat-jar`, optional `fdb-junit` and integration test targets.

Control flow: configure generated Java option/API files, choose OS/architecture packaging names, build JNI shared/object libraries, compile Java 8 sources, write OSGi-style manifest, create main jar, copy javadocs, unpack jar into a fat-jar staging dir, copy native libraries under platform-specific `lib/<os>/<arch>`, build release/snapshot fat jar and test jar, optionally download pinned JUnit jars and register ctest commands.

State and persistence: writes generated Java sources, manifest, javadocs, staged fat jar tree, native library copies, packages, and optional downloaded dependencies in build directories.

Dependencies and integration: requires Java/JNI CMake support, `fdb_c`, `fdb_java_native` generated headers, `flow`, `src/tests.cmake`, API version file, packaging target `packages`, and FoundationDB test macros.

Risks: network downloads during configure/build can fail; one `opentest4j` download lacks `EXPECTED_HASH`; sanitizer builds skip Java tests. Platform library destinations must stay aligned with runtime loader expectations. Linker version-script flags are Linux-specific with Clang 19 workaround.

Test signals: optional JUnit and integration ctest targets; integration tests require running FDB clusters and external client artifacts for multi-client paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/CMakeLists.txt -->
