# Research Report: subset-b-008385

This grouped report covers the FoundationDB Flow tester and Go binding files assigned to `subset-b-008385`. Each file section is bounded with reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/Tester.cpp -->
# sources/storage-engines/foundationdb/bindings/flow/tester/Tester.cpp

## Purpose

`Tester.cpp` implements the executable Flow binding stack tester for FoundationDB. It reads test instructions from the database under a tuple-prefixed range, interprets them as stack-machine operations, executes Flow binding APIs, and writes/logs results back through the shared stack abstraction. Its role is cross-binding compatibility testing: the instruction vocabulary mirrors operations implemented by the Go stack tester and other language testers so that the same generated instruction stream can validate tuple encoding, transactions, range reads, atomic operations, conflicts, threading, and directory-layer integration behavior.

## Important APIs, Types, and Functions

The file registers many `InstructionFunc` implementations through `REGISTER_INSTRUCTION_FUNC`, using the dispatcher declared in `Tester.h`. Core stack instructions include `PUSH`, `DUP`, `EMPTY_STACK`, `SWAP`, `POP`, `SUB`, `CONCAT`, and `LOG_STACK`. Transaction and database instructions include `NEW_TRANSACTION`, `USE_TRANSACTION`, `ON_ERROR`, `SET`, `GET`, `COMMIT`, `RESET`, `CANCEL`, `GET_KEY`, range variants, conflict range/key operations, `ATOMIC_OP`, and API/option validation in `UNIT_TESTS`. Tuple instructions include pack/unpack/range/sort plus float and double encode/decode helpers.

`getRange` has two overloads: one for `KeyRange` and one for selector ranges. Both manually continue paged range reads until `more` is false or an explicit limit is reached, including an iterator streaming-mode progression copied from the C API. `waitForVoid`, `waitForValue`, and `getKey` normalize asynchronous results and errors into tuple-packed stack values. `startTest`, `runTest`, `getInstructions`, and `doInstructions` are the top-level execution pipeline, while `main` parses `prefix`, `api_version`, and optional cluster filename.

## Control Flow

`main` initializes platform/crash handling, selects deterministic randomness, starts `startTest`, and then runs the Flow network until stopped. `startTest` initializes global atomic-op and directory-creating-op maps, creates the Flow network, selects the requested API version, starts the network thread, opens the database, and invokes `runTest`. `runTest` fetches instruction key-values under the supplied tuple prefix, executes them in order, then waits for subthreads spawned by `START_THREAD`.

For each instruction, `doInstructions` unpacks the operation tuple, strips `_DATABASE` or `_SNAPSHOT` suffixes, chooses either a new auto-committed transaction or the named transaction from `trMap`, rejects snapshot directory operations, and dispatches by operation string. Database-suffixed mutations use `executeMutation`, which wraps the mutation in a retry loop and commits automatically. Transaction-scoped mutations run against the current transaction and leave commit timing to explicit instructions.

## State and Persistence Behavior

Persistent state lives primarily in FoundationDB: instruction streams are read from the database, mutations apply to keys passed by the generated test, and `LOG_STACK` writes stack entries to a caller-provided prefix in batches of 100. In-process state includes global `trMap`, the current transaction name, `lastVersion`, stack entries containing futures, and `DirectoryTesterData`. `START_THREAD` creates a separate `FlowTesterData` with the same database handle and independent stack/directory state, then records the future in `subThreads`.

The stack deliberately stores futures as values so instructions can test asynchronous ordering and explicit `WAIT_FUTURE`. Error results are encoded as tuple values rather than always aborting the whole tester, except for assertions and unexpected top-level errors. Directory instruction failures receive special handling: if the operation is known to create or open a directory-like object, an invalid placeholder is appended to preserve directory-list index alignment, and `DIRECTORY_ERROR` is pushed.

## Dependencies and Integration Points

The implementation depends on Flow coroutine `Future`/`Reference` APIs, `bindings/flow/fdb_flow.h`, tuple and directory binding types, `fdbrpc` network setup, deterministic random, and TLS configuration. It is built into the FoundationDB binding test infrastructure and expects a running FDB cluster or cluster file. It integrates with the Flow directory tester through shared `DirectoryTesterData` and directory instruction names, although the directory instruction bodies are defined elsewhere.

The instruction vocabulary is an integration contract with generated stack-tester workloads and other language binding testers. Atomic operation names are mapped to `FDBMutationType`, and `UNIT_TESTS` verifies API version selection and option-setting wrappers against the Flow binding surface.

## Risks

Global `trMap` and `optionInfo` are mutable process-wide state; subthreads share the transaction map without visible synchronization in this file. Several helpers use raw casts for floats, doubles, UUID formatting, and integer byte order, so strict-aliasing or alignment assumptions matter. Some stack operations silently no-op on underflow, which matches tester behavior but can hide malformed instruction streams. `getRange` carries a copied C API iterator progression with a comment noting maintenance risk if the C implementation changes. Directory error handling depends on the hard-coded `opsThatCreateDirectories` set staying aligned with registered directory operations.

## Test Signals

This file is itself a test executable. Strong signals are successful execution of generated binding stack tests across API versions, matching result logs against other language bindings, and coverage of `UNIT_TESTS`, watch/locality-equivalent operations, tuple round trips, range selector variants, and database-suffixed retry behavior. Build/test signals come from the Flow binding tester target and any suite that invokes `fdb_flow_tester prefix api_version [cluster_filename]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/Tester.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/Tester.h -->
# sources/storage-engines/foundationdb/bindings/flow/tester/Tester.h

## Purpose

`Tester.h` declares the shared data model and dispatcher support for the Flow binding stack tester. It defines stack entries, instruction metadata, directory/subspace tracking, global tester state, and the mutation retry helper used by instruction implementations. The header forms the contract between `Tester.cpp` and other tester modules such as directory instruction implementations.

## Important APIs, Types, and Functions

`StackItem` binds an instruction index to a `Future<Standalone<StringRef>>`, allowing stack values to be either immediate tuple-packed strings or pending asynchronous results. `FlowTesterStack` provides push/pop, tuple-value pushes, error tuple encoding, future-aware `waitAndPop`, duplication, and clear operations.

`InstructionData` carries execution flags (`isDatabase`, `isSnapshot`), the original packed instruction, and the selected Flow transaction. `InstructionFunc` is an `IDispatched` command dispatcher keyed by operation name. `REGISTER_INSTRUCTION_FUNC` wraps the registration macro used by concrete instruction structs.

Directory support is modeled by `DirectoryOrSubspace` and `DirectoryTesterData`. A slot can hold an `IDirectory`, a `Subspace`, both for a `DirectorySubspace`, or an invalid placeholder. `FlowTesterData` aggregates the FDB API pointer, database handle, fetched instruction range, current transaction name, stack, last version, directory state, and futures for spawned subthreads. The templated `executeMutation` helper retries database-scoped mutations on retryable errors and commits when the instruction is marked as database-level.

## Control Flow

Instruction implementations receive `Reference<FlowTesterData>` and `Reference<InstructionData>` through `InstructionFunc::call`. The dispatcher validates that the operation exists and invokes the registered callable. Stack operations can defer waiting until later by pushing futures; callers that need concrete tuple values call `waitAndPop`.

`executeMutation` loops around a caller-supplied async function. On success it commits only for `_DATABASE` instructions; on an FDB `Error`, it calls `tr->onError` for database-scoped operations and rethrows for transaction-scoped operations so explicit transaction tests can observe failures.

## State and Persistence Behavior

The header declares in-memory structures only. Persistence occurs when instruction implementations use the database or directory layer. `FlowTesterStack` preserves instruction indexes with values so logged output can map stack results back to the instruction that produced them. `DirectoryTesterData` starts with a root `DirectoryLayer` and appends results or invalid placeholders as directory instructions execute.

## Dependencies and Integration Points

The header depends on Flow reference/future infrastructure, the Flow FDB binding, tuple/subspace/directory abstractions, and `IDispatched`. It is consumed by the Flow tester executable and any companion source that registers additional instructions. Its dispatcher keys and data shapes must remain compatible with generated stack tester instruction streams.

## Risks

`FlowTesterStack::pop` returns fewer than requested items when the stack is short, leaving each instruction to decide whether to no-op. `DirectoryTesterData::directory` and `subspace` assert on invalid access rather than returning errors. `DirectoryOrSubspace` stores a raw `Subspace*` when constructed from a raw subspace, so lifetime must be owned elsewhere; directory subspaces are safe only while the referenced object remains alive. `executeMutation` retries forever until `onError` reports a non-retryable failure.

## Test Signals

Useful signals are successful compilation of all registered instruction modules and stack tester runs that exercise immediate values, futures, database-suffixed auto-commit operations, explicit transaction operations, and directory object indexing. Assertion failures in directory/subspace access usually indicate an instruction ordering or error-placeholder mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/Tester.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/CMakeLists.txt -->
# sources/storage-engines/foundationdb/bindings/go/CMakeLists.txt

## Purpose

This CMake file builds and tests the FoundationDB Go bindings inside the larger FoundationDB CMake build. It stages Go source files into a generated GOPATH layout, generates option/error binding files, compiles Go packages and the stack tester executable, and registers tests that verify generated checked-in files and gofmt cleanliness.

## Important APIs, Types, and Functions

`SRCS` lists the Go files copied into the build-local GOPATH, including binding packages, directory layer files, tests, and `go.mod`. `go_env` defines `GOPATH`, `CGO_CFLAGS`, `CGO_LDFLAGS`, and `GO111MODULE=auto`, making cgo point at the build tree’s C binding headers and libraries.

The local CMake function `build_go_package` parses `LIBRARY`, `EXECUTABLE`, `INCLUDE_TEST`, `NAME`, and `PATH`. It emits a `go install` custom command for either package archives or executables, creates an `ALL` custom target, and optionally builds a compiled Go test binary plus an `add_fdbclient_test` entry with the correct shared-library path.

Custom commands generate `src/fdb/generated.go` from `fdb.options` and `src/fdb/error_codes_generated.go` from Flow error definitions. `compare_files` tests ensure the generated build outputs match checked-in source copies.

## Control Flow

CMake first creates the GOPATH destination and a copy command for every source in `SRCS`. `copy_go_sources` materializes the staged tree. Generation targets depend on copied sources and run Go generator programs. Package targets are then declared in dependency order: `fdb_go`, `tuple_go`, `subspace_go`, `directory_go`, and `_stacktester` as `fdb_go_tester`. The final tests compare generated files and optionally run gofmt if found.

## State and Persistence Behavior

All generated and compiled artifacts are stored under `${CMAKE_CURRENT_BINARY_DIR}`. The source tree is not modified by the build; instead, generated output is compared against checked-in generated files. This gives CI a clear failure when source generators or upstream option/error definitions change without updating committed Go binding files.

## Dependencies and Integration Points

The file depends on a configured `GO_EXECUTABLE`, FoundationDB C binding target `fdb_c`, generated C binding headers, the build-tree `lib` directory, and CMake test helpers such as `add_fdbclient_test`. It integrates Go package compilation into the main FDB build graph while preserving the import path `github.com/apple/foundationdb/bindings/go/src`.

## Risks

The dependency in `build_go_package` references `${fdb_options_file}`, while the declared variable is `go_options_file`; if no variable alias exists externally, this can weaken dependency tracking. Platform mapping is hard-coded to `darwin_amd64`, `windows_amd64`, or `linux_amd64`, which may not match all Go build target names. The build uses GOPATH staging and `GO111MODULE=auto`, so behavior can vary with Go toolchain module defaults.

## Test Signals

Primary signals are successful `fdb_go`, `tuple_go`, `directory_go`, and `fdb_go_tester` targets, passing compiled Go package tests for `fdb` and `fdb/tuple`, passing generated-file compare tests, and a clean `fdb-go-fmt` test when `gofmt` is available.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/bench/int64ToBytes_bench_test.go -->
# sources/storage-engines/foundationdb/bindings/go/bench/int64ToBytes_bench_test.go

## Purpose

This benchmark compares two ways to convert an `int64` to an eight-byte little-endian representation in Go. It is a focused performance microbenchmark relevant to FoundationDB atomic integer operations and allocator counters, where byte encoding is frequent and allocation behavior matters.

## Important APIs, Types, and Functions

`Benchmark_Int64ToBytesBuffer` allocates a new `bytes.Buffer` each iteration and writes the integer via `binary.Write` with `binary.LittleEndian`. `Benchmark_Int64ToBytesPut` allocates a fixed eight-byte slice and writes with `binary.LittleEndian.PutUint64`. The package-level `result []byte` retains the last generated slice so the compiler cannot fully eliminate the work.

Both benchmarks call `b.ReportAllocs()` and `b.SetBytes(...)`, making benchmark output include allocation counts and throughput based on encoded byte length.

## Control Flow

Each benchmark loops over `b.N`, encodes `n`, updates the benchmark byte count, stores the current result in a local variable, and assigns it to the global sink after the loop. The buffer variant handles and reports a possible `binary.Write` error; the direct slice variant has no fallible operation.

## State and Persistence Behavior

There is no persistent state. Runtime state is limited to heap allocations made during the benchmark and the final assignment to `result`. The benchmark intentionally observes allocation behavior.

## Dependencies and Integration Points

The file depends only on the Go standard library packages `bytes`, `encoding/binary`, and `testing`. It is independent from the FoundationDB client runtime, but its result can inform low-level binding implementation choices where little-endian integer bytes are needed.

## Risks

The benchmark allocates a new slice even in the direct `PutUint64` path, so it compares API overhead plus one allocation rather than a fully allocation-free reusable buffer strategy. Repeated `b.SetBytes` inside the loop is unusual; it is stable here because the encoded size is constant but still adds benchmark bookkeeping overhead.

## Test Signals

Run with `go test -bench .` from the benchmark package. Expected signal is lower allocations and better throughput for the direct `PutUint64` path compared with `bytes.Buffer` plus `binary.Write`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/bench/int64ToBytes_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/godocs.js -->
# sources/storage-engines/foundationdb/bindings/go/godoc-resources/godocs.js

## Purpose

`godocs.js` is a vendored Go documentation UI helper used by generated FoundationDB Go binding documentation. It improves navigation, search placeholder behavior, table-of-contents generation, collapsible examples, playground setup, mobile menu behavior, install-instruction personalization, and optional static-analysis/callgraph overlays.

## Important APIs, Types, and Functions

The file is an immediately invoked function expression over jQuery in strict mode. Navigation helpers include `bindSearchEvents`, `generateTOC`, `bindToggle`, `bindToggleLinks`, `setupDropdownPlayground`, `setupInlinePlayground`, `fixFocus`, and `toggleHash`. `personalizeInstallInstructions` parses a `?download=` query, adjusts visible install instructions, inserts a download link, and redirects to Google storage for Go distributions.

Analysis helpers include `escapeHTML`, `makeAnchor`, `showLowFrame`, `document.hideLowFrame`, `document.onClickCallers`, `document.onClickCallees`, `document.onClickTypeInfo`, `implementsHTML`, `methodsetHTML`, `document.onClickComm`, `setupTypeInfo`, `setupCallgraphs`, `document.cgAddChildren`, and `cgAddChild`. These functions consume `document.ANALYSIS_DATA` and `document.CALLGRAPH` emitted by godoc.

## Control Flow

On document ready, the script binds UI events, generates the TOC, wires foldable sections and links, initializes playgrounds, fixes focus for keyboard navigation, initializes analysis widgets, toggles the current hash target, personalizes install instructions, and runs any functions registered in `window.initFuncs`. On window load, it scrolls the first `.selection` element into view.

Callgraph nodes are lazily expanded: `setupCallgraphs` marks roots and creates treeviews, while each generated hitarea click calls `document.cgAddChildren` once for child indices. Analysis clicks either jump directly when there is a single target or render a small lower frame with escaped HTML links.

## State and Persistence Behavior

State is browser DOM state: CSS classes, generated TOC nodes, playground setup flags, resized textareas, low-frame HTML, and callgraph tree expansion. The script mutates `window.location` for personalized downloads and `document.location` for single-target analysis navigation. It does not persist beyond the page, except where the treeview plugin may apply its own persistence if configured.

## Dependencies and Integration Points

The script depends on jQuery, the Go playground helper `playground`, treeview plugin support for callgraphs, godoc-generated DOM IDs/classes, `window.initFuncs`, `document.ANALYSIS_DATA`, and `document.CALLGRAPH`. It is a static asset for generated documentation, not part of the Go binding runtime.

## Risks

The code is old jQuery-era browser code and uses deprecated APIs such as `button.toggle(fn, fn)` and `$(window).load(...)`, which rely on the bundled jQuery version. `showLowFrame` writes `innerHTML`; most dynamic content is escaped through helper functions, but any unescaped fields such as `data.Name` should still be trusted only if generated by godoc. `personalizeInstallInstructions` can redirect the page based on the query string after regex validation.

## Test Signals

Signals are manual or browser-based: docs pages should load without JS errors, TOCs should appear, toggles and example playgrounds should work, callgraphs should expand lazily, analysis popups should escape content, mobile menu classes should toggle, and selected code should scroll into view.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/godocs.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.js -->
# sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.js

## Purpose

`jquery.js` is a minified vendored copy of jQuery v1.8.2 for the generated Go documentation resources. It provides the DOM traversal, event binding, animation, AJAX, deferred, and utility APIs consumed by `godocs.js` and the treeview plugins.

## Important APIs, Types, and Functions

Because the file is minified third-party code, the important public surface is the jQuery API exposed as `window.jQuery` and `window.$`. The bundled version includes core selection and chaining (`p.fn` in the minified body), data/cache helpers, event helpers, CSS and animation methods, AJAX transports, serialization, offset/position utilities, and AMD registration when an AMD loader with jQuery support is present.

## Control Flow

The file is a single immediately invoked function expression over `window`. It initializes support detection, defines the jQuery constructor/prototype and static helpers, registers ready/event/AJAX/animation modules, and assigns the exported symbols at the end. Consumers load it before `godocs.js`, `jquery.treeview.js`, and `jquery.treeview.edit.js`.

## State and Persistence Behavior

Runtime state is browser process state: jQuery caches, event registries, deferred queues, animation timers, AJAX global counters, and exported globals. It does not write application persistence itself, though plugins can use its data/event APIs and optional cookie plugins.

## Dependencies and Integration Points

The asset depends only on a browser `window` and `document`. It is an integration dependency for the documentation UI, especially because companion scripts rely on APIs available in jQuery 1.8.2, including older overloads that later jQuery versions removed.

## Risks

The version is old and predates many modern browser-security and compatibility expectations. It should be treated as a static documentation dependency, not reused for new application surfaces. Upgrading it can break `godocs.js` and treeview behavior that depends on removed legacy APIs. Since the source is minified, local auditing and patching are harder than for unminified assets.

## Test Signals

Documentation pages should load jQuery before dependent scripts, expose `$`/`jQuery`, and run menu, toggle, playground, and treeview interactions without browser console errors. Any dependency upgrade should be tested against the full generated Go documentation UI.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.treeview.edit.js -->
# sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.treeview.edit.js

## Purpose

This small plugin extension wraps the base jQuery treeview plugin to support dynamic branch addition and removal. In the FoundationDB Go documentation assets, it enables lazy callgraph expansion from `godocs.js` by allowing new `<li>` branches to be inserted and styled after the initial treeview setup.

## Important APIs, Types, and Functions

The file captures `$.treeview.classes` and the original `$.fn.treeview`, then replaces `$.fn.treeview` with a wrapper. When called with `settings.add`, it triggers an `add` event with the new branches. When called with `settings.remove`, it triggers `remove`. Otherwise it delegates to the original treeview initializer and binds handlers for `add` and `remove`.

The `add` handler fixes the previous sibling’s last-item classes, then calls `prepareBranches` and `applyClasses` on the new branches. The `remove` handler removes branch nodes and repairs last/collapsible/expandable classes on the previous sibling and parent.

## Control Flow

Initialization is immediate when the script loads. Later, callers use `$(tree).treeview({ add: ul })` or `{ remove: branches }`; the wrapper dispatches to events rather than rebuilding the entire tree. The add/remove event handlers rely on helper methods provided by `jquery.treeview.js`.

## State and Persistence Behavior

State consists of DOM nodes, CSS classes, hitarea nodes, and the stored toggler function on the tree element. No durable persistence is introduced here.

## Dependencies and Integration Points

It depends on jQuery, `jquery.treeview.js`, and the treeview class/helper conventions (`replaceClass`, `prepareBranches`, `applyClasses`, `data("toggler")`). `godocs.js` uses this dynamic add path for callgraph nodes.

## Risks

The plugin uses legacy jQuery APIs such as `andSelf`, which are unavailable in newer jQuery versions without migration support. The remove path has tight assumptions about tree DOM shape and class names. Loading order is critical: base treeview must run before this extension.

## Test Signals

The key signal is lazy callgraph expansion in generated docs: added children should receive hitareas, open/closed classes, and correct last-node styling. Removing branches, if used, should not leave stale hitareas or incorrect last-child visuals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.treeview.edit.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.treeview.js -->
# sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.treeview.js

## Purpose

`jquery.treeview.js` is a vendored jQuery Treeview 1.4.1 plugin used by Go documentation pages to render collapsible trees, especially package/callgraph navigation. It supplies branch preparation, hitarea creation, expand/collapse behavior, optional persistence, and tree controller links.

## Important APIs, Types, and Functions

The plugin extends `$.fn` with helper methods `swapClass`, `replaceClass`, `hoverClass`, `heightToggle`, `heightHide`, `prepareBranches`, `applyClasses`, and `treeview`. The main `treeview(settings)` method accepts options such as `collapsed`, `animated`, `unique`, `persist`, `cookieId`, `control`, `toggle`, and `prerendered`.

Internal helpers include `treeController`, which wires collapse/expand/toggle controls, `toggler`, which swaps classes and shows/hides child `<ul>` elements, `serialize`, and `deserialize` for cookie persistence. `$.treeview.classes` centralizes CSS class names used by tree markup and the edit extension.

## Control Flow

On initialization, the plugin merges settings, adapts the toggle callback, stores the toggler on the tree, adds the `treeview` class, prepares all branches, restores persistence if requested, applies classes and hitarea click handlers, optionally creates tree controls, and returns the jQuery chain. Clicking a hitarea toggles child visibility and class state; in `unique` mode it also collapses sibling branches.

## State and Persistence Behavior

State is mostly DOM/CSS state: hidden child lists, expandable/collapsible classes, hitarea classes, selected link classes, and stored jQuery data. If `persist: "cookie"` is configured, branch open/closed state is serialized to a cookie using an external `$.cookie` plugin. If `persist: "location"` is configured, the branch containing the current URL is opened and selected.

## Dependencies and Integration Points

The plugin depends on jQuery 1.x and optionally a jQuery cookie plugin for cookie persistence. `jquery.treeview.edit.js` depends on helper methods and `$.treeview.classes`. `godocs.js` uses `$(tree).treeview({ collapsed: true, animated: "fast" })` and dynamic add operations.

## Risks

The code predates modern event delegation and uses old jQuery idioms. It scans and mutates the DOM heavily, so malformed tree markup can produce incorrect classes or missing hitareas. Cookie persistence silently depends on `$.cookie` being loaded. Upgrading jQuery can break deprecated helpers used by this plugin and its edit extension.

## Test Signals

Generated documentation treeviews should show correct open/closed icons, expand/collapse smoothly with the configured animation, preserve or reveal the current location branch when requested, and support dynamic additions through the edit extension without losing last-child styling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/godoc-resources/jquery.treeview.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/_stacktester/directory.go -->
# sources/storage-engines/foundationdb/bindings/go/src/_stacktester/directory.go

## Purpose

This file adds directory-layer instructions to the Go stack tester. It translates generated `DIRECTORY_*` operations into calls against the Go `fdb/directory` and `fdb/subspace` APIs, while preserving the stack tester’s index-based object model and error behavior for cross-binding comparison.

## Important APIs, Types, and Functions

`popTuples`, `tupleToPath`, and `tuplePackStrings` bridge stack values and directory path representations. `DirectoryExtension` stores a heterogeneous list of directory and subspace objects, plus the current index and an error fallback index. `newDirectoryExtension` seeds the list with `directory.Root()`. `cwd` returns the current `directory.Directory`; `css` returns the current `subspace.Subspace`.

`processOp` is the core dispatcher for operations after the `DIRECTORY_` prefix is removed. It handles creation of subspaces/layers, `CreateOrOpen`, `Create`, `CreatePrefix`, `Open`, `Change`, error-index setup, move operations, remove variants, list/exists, key pack/unpack/range/contains, subspace opening, directory/subspace logging, and prefix stripping.

## Control Flow

`processOp` wraps execution in a `defer`/`recover` block. Any panic stores `DIRECTORY_ERROR` at the current instruction index; for create/open/move operations it also appends `nil` to keep later object indexes aligned. Each case pops arguments from the stack in the instruction-defined order, invokes the directory/subspace API, and stores either a new object in the extension list or a stack result through `sm.store`.

Remove operations are intentionally wrapped in `t.Transact`, even when the incoming transactor is already database-like, so a failed non-`IF_EXISTS` removal does not accidentally commit a directory-version key written during the attempted removal.

## State and Persistence Behavior

The extension list is in-memory object state. Persistent state is FoundationDB directory metadata, directory contents, and explicit log outputs. `LOG_SUBSPACE` writes the current subspace bytes under a tuple-suffixed key. `LOG_DIRECTORY` writes path, layer, existence, and child list under a supplied root prefix. Create/move/remove operations mutate directory metadata transactionally through the supplied transactor.

## Dependencies and Integration Points

The file depends on the Go binding `fdb`, `directory`, `subspace`, and `tuple` packages. It is invoked from `StackMachine.processInst` in `stacktester.go` for `DIRECTORY_` operations. Its behavior must remain aligned with the Flow tester and other language binding directory tests, including placeholder insertion on errors.

## Risks

The object list stores `interface{}` values and relies on type assertions, so an invalid current index panics into `DIRECTORY_ERROR`. `tupleToPath` assumes every tuple element is a string. `CHANGE` maps a nil target to `errorIndex`, so wrong error-index setup can redirect subsequent operations. `LOG_SUBSPACE` appends tuple bytes to a mutable key slice, which is acceptable for immediate use but should not be reused as immutable input afterward.

## Test Signals

Signals come from generated binding stack tests that compare directory operation outputs across languages. Important cases include layer mismatch errors, manual-prefix behavior, moving across partitions, remove versus remove-if-exists, packing/unpacking keys, subspace containment, and directory logging after both successful and failed create/open operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/_stacktester/directory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/_stacktester/stacktester.go -->
# sources/storage-engines/foundationdb/bindings/go/src/_stacktester/stacktester.go

## Purpose

`stacktester.go` is the Go binding executable stack tester. It reads generated instruction tuples from FoundationDB, interprets them against the Go binding API, and uses stack results/logging to validate that Go binding behavior matches other FoundationDB bindings. It covers transactions, read snapshots, range reads, tuple encoding, atomic operations, conflict ranges, watches, locality, API options, and directory operations delegated to `directory.go`.

## Important APIs, Types, and Functions

`StackMachine` holds the instruction prefix, current transaction name, stack, last read/committed version, spawned goroutine wait group, verbosity flag, and `DirectoryExtension`. `stackEntry` preserves the producer instruction index with each value. `waitAndPop` normalizes immediate values and FDB futures, converting ready results into plain Go values and FDB errors into encoded `ERROR` tuples.

Helpers such as `popSelector`, `popKeyRange`, `popRangeOptions`, `pushRange`, `executeMutation`, `currentTransaction`, `newTransaction`, and `switchTransaction` support the instruction interpreter. `processInst` is the large dispatcher for stack, transaction, tuple, range, conflict, atomic, unit-test, and directory operations. `Run` fetches instructions from `tuple.Tuple{prefix}` and executes them in order. `main` selects the API version, opens the database, and runs the machine.

## Control Flow

The executable expects `prefix api_version [cluster_file]`. After API selection and database open, `Run` reads all instruction key-values under the tuple prefix in a transaction and unpacks each value as an instruction tuple. For every instruction, `processInst` chooses the active transactor/read-transactor based on `_SNAPSHOT` and `_DATABASE` suffixes, then executes the opcode.

Database-suffixed mutations use `db.Transact` through `executeMutation` and push `RESULT_NOT_PRESENT`. Transaction-scoped operations use the named transaction in `trMap` and leave commit/on-error behavior explicit. `START_THREAD` spawns another `StackMachine` on a different prefix and waits at the end of `Run`.

## State and Persistence Behavior

Process state includes global `db`, global named transaction map guarded by `trMapLock`, per-machine stack, last version, and directory object list. Persistent effects are all FoundationDB operations performed by instructions: key mutations, range clears, atomic ops, log-stack writes, watch setup side effects, locality system-key reads, and directory metadata/content changes.

The stack stores FDB futures as first-class values, allowing generated tests to delay `Get`/`MustGet` until `WAIT_FUTURE` or a later pop. Errors from FDB futures are encoded as stack values where the protocol expects that, while unexpected non-FDB panics abort the process.

## Dependencies and Integration Points

The file depends on the Go binding packages `fdb` and `tuple`, standard libraries for binary encoding, reflection, synchronization, and runtime scheduling, and directory support in the sibling `directory.go`. It is built by the Go binding CMake file as `fdb_go_tester` and run by generated stack-test harnesses.

## Risks

The dispatcher is intentionally broad and type-assertion heavy; malformed instruction streams can panic or fatal. Atomic operations are invoked by reflection from transformed operation names, so method naming must stay aligned with the binding API. `WAIT_EMPTY` ignores the returned error from `db.Transact`, which may hide retry exhaustion or fatal errors. Range mode maps instruction values by adding one to the `StreamingMode`, a protocol detail that must stay aligned with generated instructions. Futures should not escape transaction lifetimes outside expected tester patterns.

## Test Signals

The executable is validated by stack tester suites. High-value signals include cross-binding result equivalence, successful tuple round trips including versionstamps and floats, watch triggering behavior, locality boundary consistency, API option calls, database retry behavior, named transaction switching, concurrent thread prefixes, and directory instruction compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/_stacktester/stacktester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/cluster.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/cluster.go

## Purpose

`cluster.go` preserves the deprecated `Cluster` API for older users of the FoundationDB Go bindings. It provides a lightweight cluster handle that can open the default database, while directing new users toward `OpenDatabase` or `OpenDefault`.

## Important APIs, Types, and Functions

`Cluster` stores a `clusterFileName`. `Cluster.OpenDatabase(dbName []byte)` calls `Open(c.clusterFileName, dbName)` and documents that the database name must be `[]byte("DB")`. Both the type and method are marked deprecated in comments.

## Control Flow

There is no complex flow. Callers holding a `Cluster` call `OpenDatabase`, which delegates to the newer `Open` helper in `fdb.go`, returning a `Database` and error.

## State and Persistence Behavior

`Cluster` is an immutable lightweight value containing only the cluster file name. It does not own a C pointer or persistent resource in this file. Actual database handles and lifecycle state are created by `Open`.

## Dependencies and Integration Points

The file depends on package-local `Open`, `Database`, and FoundationDB database naming conventions. It integrates with legacy API consumers while keeping the implementation centralized in modern open helpers.

## Risks

The API is deprecated and should not gain new behavior. The `dbName` contract is documented but not checked in this wrapper; validation is delegated to `Open`/the C API. Any removal would be a compatibility break for older binding users.

## Test Signals

Compatibility tests should confirm `Cluster.OpenDatabase([]byte("DB"))` still opens a database equivalently to the direct open helpers. New behavior should be tested through `OpenDatabase`, `OpenDefault`, and `Open` rather than this shim.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/database.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/database.go

## Purpose

`database.go` implements the Go binding `Database` handle and database-level operations. It wraps the FoundationDB C API pointer, exposes database options, creates transactions, implements retrying transactional helpers, surfaces management/status APIs, and provides locality boundary-key lookup.

## Important APIs, Types, and Functions

`Database` is a copyable concurrent-safe handle containing cache metadata and an embedded `*database` with `*C.FDBDatabase`. `DatabaseOptions` wraps database option setting through `setOpt`. `Close` removes cached handles and destroys the C database pointer. `CreateTransaction` calls `fdb_database_create_transaction`, wraps the pointer in a Go transaction, and installs a finalizer because futures can extend transaction lifetime.

Management methods include `RebootWorker`, `GetClientStatus`, and `GetMainThreadBusyness`. `retryable` is the shared retry loop used by `Transact` and `ReadTransact`; it recognizes wrapped `fdb.Error` values, calls `OnError`, and retries until success or non-retryable error. `Transact` creates one transaction, runs the user function, commits on nil error, and recovers panicked FDB errors. `ReadTransact` is the read-only equivalent without commit. `LocalityGetBoundaryKeys` reads system keyspace to expose storage-server boundary keys.

## Control Flow

Callers generally obtain a `Database`, then call `Transact` or `ReadTransact`. Each helper creates a transaction once and passes a closure to `retryable`. On retryable failure, the transaction’s `OnError` resets it for the next loop. `Transact` commits after the user callback if no error was returned; `ReadTransact` returns after the callback without commit.

Direct C API wrappers create the appropriate future wrapper, call `Get`, and translate special cases. For example, `GetClientStatus` returns `ErrAPIVersionUnset` before API selection and `ErrMultiVersionClientUnavailable` when the C future returns an empty byte slice.

## State and Persistence Behavior

`Database` owns a C database pointer until `Close`. Cached database tracking is maintained outside this file via `openDatabases`. Transactions created from the database mutate persistent FoundationDB state only when committed. `Transact` and `ReadTransact` deliberately warn callers not to return futures because transaction finalization can cancel outstanding work after the helper returns.

`LocalityGetBoundaryKeys` reads from `\xFF/keyServers/` using system-key options and strips the system prefix from returned keys. It does not mutate user data.

## Dependencies and Integration Points

The file depends on cgo and `foundationdb/fdb_c.h`, package-local transaction/future/error helpers, API version state, open database cache, and option code generation. It is the central integration point between Go callers and FDB C database handles.

## Risks

`Close` must be called exactly once and callers must avoid using the database afterward. Finalizer-based transaction destruction is subtle and depends on futures becoming unreachable. Returning futures from transaction closures can produce canceled reads and missed retry handling. `RebootWorker` comments note that immediately closing the database may prevent asynchronous reboot commands from being delivered. `LocalityGetBoundaryKeys` assumes the system key prefix length when slicing returned keys.

## Test Signals

Tests should exercise transaction retries for returned and panicked `fdb.Error`, commit errors, read-only retries, option setting, database close/cache behavior, client status with and without multi-version support, worker reboot error handling, and locality boundary key reads under system-key permissions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/database.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/allocator.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/allocator.go

## Purpose

`allocator.go` implements the Go directory layer’s high-contention allocator. It allocates short, mostly random subspace prefixes for new directories while minimizing conflicts under many concurrent creators.

## Important APIs, Types, and Functions

`highContentionAllocator` contains two subspaces: `counters` for allocation-window counters and `recent` for candidate-prefix markers. `newHCA` derives those subspaces from a parent allocator subspace. `windowSize` grows allocation windows from 64 to 1024 to 8192 as the start value increases. `allocate` is the core routine that returns `s.Sub(candidate)` for a free candidate prefix inside the current window.

`oneBytes` is the little-endian encoded increment used with FDB atomic `Add`. `allocatorMutex` serializes certain in-transaction mutation/read setup sequences inside this process.

## Control Flow

`allocate` first snapshots the highest counter key to find the current window start. It increments the current window counter with no write conflict, reads the count, and advances to a larger window if the count indicates the window is at least half full. When advancing, it clears older counter and recent marker ranges.

Once a suitable window exists, it repeatedly chooses a random candidate, writes a marker under `recent` with no write conflict, checks whether a newer window appeared, then reads the candidate marker. If the marker was absent, it adds a write conflict key and returns the candidate subspace. If a newer window appeared or the candidate was already present, it retries.

## State and Persistence Behavior

Allocator state is stored in FoundationDB under the allocator’s `counters` and `recent` subspaces. Counter increments are atomic additions; recent markers reserve candidate prefixes. Clearing older ranges bounds metadata as windows advance. The returned subspace itself is not persisted by this file; callers persist it as directory metadata.

## Dependencies and Integration Points

The allocator depends on the Go `fdb` transaction API, `subspace`, little-endian `encoding/binary`, `math/rand`, and process-local synchronization. It is used by directory layer creation code when a directory needs an automatically assigned content prefix.

## Risks

Randomness uses the package-level `math/rand` source, so deterministic seeding or concurrency behavior can affect allocation patterns. The process-local mutex only coordinates goroutines in one process; correctness still depends on FDB conflict ranges across clients. Byte decoding assumes little-endian counter values matching `oneBytes`. Bugs here can cause prefix collisions or excessive conflicts, making directory creation unsafe or slow.

## Test Signals

Useful tests create many directories concurrently and assert unique prefixes, low conflict rates, correct window advancement, bounded old metadata cleanup, and compatibility with other language directory layer allocators.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/allocator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory.go

## Purpose

`directory.go` defines the public Go directory layer interface, package-level default-root helpers, common errors, version constants, and a small move helper used by directory implementations. It is the main API surface users import for hierarchical FoundationDB subspace management.

## Important APIs, Types, and Functions

The `Directory` interface exposes `CreateOrOpen`, `Open`, `Create`, `CreatePrefix`, `Move`, `MoveTo`, `Remove`, `Exists`, `List`, `GetLayer`, and `GetPath`. Package errors include `ErrDirAlreadyExists`, `ErrDirNotExists`, and `ErrParentDirDoesNotExist`. Version constants encode directory layer metadata version `1.0.0`.

`stringsEqual` compares paths. `moveTo` prevents moving directories across partitions by checking that the new absolute path starts with the current directory layer path, then delegates to `Move` on the relative suffix. The package-level `root` is a directory layer rooted at metadata subspace `0xFE`, content subspace `AllKeys`, and no manual prefixes. Package functions such as `CreateOrOpen`, `Open`, `Create`, `Move`, `Exists`, `List`, and `Root` delegate to that root.

## Control Flow

User code either calls package-level helpers against the default root or obtains a `Directory` and invokes methods relative to that directory. The actual operation flow lives in `directory_layer.go`, `directory_subspace.go`, and partition files; this file defines the common contract and root dispatch.

## State and Persistence Behavior

The default root reserves `0xFE` for directory metadata and allocates content prefixes from the remaining keyspace. Directory operations are transactional through `fdb.Transactor` or `fdb.ReadTransactor`. `Remove` deletes directory metadata and content but cannot prevent already-open clients from writing into a removed prefix later, as documented by the interface.

## Dependencies and Integration Points

The file depends on `fdb` transaction interfaces and `subspace`. It integrates with the rest of the directory package through `NewDirectoryLayer` and implementation types found in sibling files. It is also consumed by stack testers and application code using the Go bindings.

## Risks

The default root can conflict with pre-existing application key partitioning if the database is not otherwise empty or if other data uses `0xFE`. `moveTo` slices `newAbsolutePath[:partition_len]`, so callers must supply paths at least as long as the layer path. Manual prefixes are disabled on the default root, which can surprise users expecting `CreatePrefix` to work globally. Directory removal does not revoke existing subspace handles.

## Test Signals

Tests should verify all interface operations against the default root, layer mismatch errors, parent-missing errors, create-versus-open behavior, move restrictions, recursive removal, list/exist results, root metadata isolation, and interoperability with directory layers from other bindings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory.go -->
