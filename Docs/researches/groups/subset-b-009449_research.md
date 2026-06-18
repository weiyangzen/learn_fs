# subset-b-009449 grouped source research

This grouped report covers the requested source files in manifest order. Each section is bounded by file research markers so it can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/bisect_test.go -->
# sources/test-tools/syzkaller/pkg/bisect/bisect_test.go

Purpose: End-to-end and unit tests for syzkaller kernel bisection logic. The file builds a synthetic git history, injects simulated build/test outcomes, and verifies cause/fix bisection behavior across flaky crashes, broken revisions, equivalent binaries, merge topology, and cross-tree operation.

Important APIs/types/functions: `testEnv` implements the builder/tester surface consumed by `runImpl`, with `BuildKernel`, `CleanKernel`, `BuildSyzkaller`, and `Test`. `createTestRepo` constructs tagged release history and special merge graphs for regression scenarios. `testBisection`, `checkBisectionResult`, `BisectionTest`, `bisectionTests`, `TestBisectionResults`, `TestBisectVerdict`, `TestMostFrequentReport`, and `TestPickReleaseTags` define the core test matrix.

Control flow: `TestBisectionResults` reuses temporary repositories through a channel, validates each `BisectionTest`, creates or reuses the synthetic repo, and runs `testBisection`. `testEnv.Test` determines crash/good/infra/boot results from the current repo HEAD title, baseline config, introduced/fix commit lookup, and optional injected crash types. `testBisection` runs `runImpl` once and usually reruns with a fake hash to verify title-based commit recovery.

State and persistence behavior: Tests persist a real temporary git repository with tags, branches, and merges. The simulated kernel build stores the last config in `testEnv.config` and returns image signatures derived from commit/config hash, with configurable same-binary ranges. There is no production persistence beyond temp dirs.

Dependencies/integration points: Exercises `pkg/vcs`, `pkg/instance`, `pkg/build`, `pkg/mgrconfig`, `pkg/report/crash`, and `debugtracer.TestTracer`. It depends on test OS/arch targets and the production bisection package internals.

Risks: The test relies on commit titles being parseable integers and on git bisection/tag behavior. Parallel tests share repo directories through a cache, so a checkout leak could contaminate later cases. The synthetic environment compresses many real failure modes into deterministic ranges, which is useful but can miss timing, remote build, or flaky infrastructure subtleties.

Test signals: The file itself is the test signal. It covers successful cause/fix bisection, non-repro errors, inconclusive sets, all-release failures, HEAD failures, syz-fatal/lost-connection handling, cross-tree fixes, confidence for flaky repros, verdict thresholds, report preference, and release tag sampling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/bisect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/minimize/slice.go -->
# sources/test-tools/syzkaller/pkg/bisect/minimize/slice.go

Purpose: Generic slice minimization helper for finding a small subsequence that still satisfies a predicate. It is intended for expensive bisection predicates and tries to reduce predicate calls while preserving element order.

Important APIs/types/functions: `Config[T]` carries `Pred`, `MaxSteps`, `MaxChunks`, and `Logf`. `Slice` minimizes all elements. `SliceWithFixed` keeps fixed elements while minimizing only free indices. `sliceCtx`, `arrayChunk`, `ErrTooManyChunks`, `bisect`, `splitChunks`, `initialSplit`, `predRun`, `done`, `elements`, `chunkInfo`, `mergeChunks`, `mergeRawChunks`, and `splitChunk` implement the algorithm.

Control flow: `Slice` starts with one chunk and calls `bisect`. The first split may divide into three or `MaxSteps` chunks, then later passes split surviving chunks in two. For every candidate sub-chunk, `predRun` tests whether the remainder still satisfies `Pred`; if yes, the candidate is dropped. Chunks that cannot be split further become final. `SliceWithFixed` maps original indices into free/fixed sets, runs `Slice` on free indices, then merges fixed elements back in original order.

State and persistence behavior: State is in-memory only: current chunk list and predicate run count. `MaxSteps` is a soft budget that makes future predicates behave as false, returning an intermediate result. `MaxChunks` returns `ErrTooManyChunks` plus the current valid but not fully minimized result.

Dependencies/integration points: Uses only Go standard library packages. It is reusable across bisection/minimization callers that can express success as `Pred([]T)`.

Risks: Correctness assumes a monotonic predicate: if a set satisfies `Pred`, supersets also satisfy it. Non-monotonic predicates may produce misleading minima. `SliceWithFixed` returns `nil, err` on minimization errors, losing the intermediate free result except for `ErrTooManyChunks` currently propagated as an error. `MaxSteps` can intentionally stop before true minimality.

Test signals: Covered by `slice_test.go`, including zero/full minimization, fixed elements, randomized subset preservation, and benchmark behavior under a predicate-call limit.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/minimize/slice.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/minimize/slice_test.go -->
# sources/test-tools/syzkaller/pkg/bisect/minimize/slice_test.go

Purpose: Tests and benchmarks for the generic slice minimizer.

Important APIs/types/functions: `TestBisectSliceToZero`, `TestBisectSliceFull`, `TestBisectSliceWithFixed`, `TestBisectRandomSlice`, `BenchmarkSplits`, and `runMinimize`.

Control flow: The deterministic tests build integer arrays and predicates for no-needed-elements, all-needed-elements, and fixed-element cases. The randomized test selects a random subset of non-zero guilty elements and asserts the minimizer returns exactly those elements while keeping predicate calls below a logarithmic bound. The benchmark measures remaining elements after a fixed number of predicate calls.

State and persistence behavior: Uses in-memory arrays and randomized sources from `testutil.RandSource` or wall-clock benchmark seed. No file or external persistence.

Dependencies/integration points: Integrates with `pkg/testutil` for iteration/randomness and `testify/assert` for assertions.

Risks: Benchmark randomness from `time.Now().UnixNano()` makes exact performance numbers non-reproducible. The randomized test validates monotonic predicates but not adversarial non-monotonic behavior, which the minimizer does not promise to support.

Test signals: Strong coverage for basic behavior, fixed element preservation, output minimality for generated monotonic predicates, and rough predicate-call complexity.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/minimize/slice_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/clangtool/clangtool.go -->
# sources/test-tools/syzkaller/pkg/clangtool/clangtool.go

Purpose: Go-side runner for compiled-in clang tools. It loads a kernel `compile_commands.json`, invokes the current test/tool binary in a special environment for each source file, merges JSON output, verifies source locations, and caches final output.

Important APIs/types/functions: `Config`, generic `OutputDataPtr[T]`, `Run`, `Verifier`, `NewVerifier`, `Verifier.Error`, `Verifier.Filename`, `Verifier.LineRange`, `runTool`, `loadCompileCommands`, and `SortAndDedupSlice`.

Control flow: `Run` first attempts to read `CacheFile`. On cache miss it loads compile commands, starts `runtime.NumCPU()` workers, calls `runTool` for each file, merges each output via `OutputPtr.Merge`, finalizes, verifies all recorded files/ranges, and writes the cache. `runTool` executes `os.Args[0]` with clang-tool flags and `SYZ_RUN_CLANGTOOL=<tool>`, parses JSON, and normalizes emitted paths relative to the kernel source tree.

State and persistence behavior: Persistent state is the optional JSON cache file. `Verifier` caches file line counts in memory, using `-1` for missing files. `loadCompileCommands` shuffles command order intentionally to catch nondeterministic merge behavior.

Dependencies/integration points: Uses `pkg/osutil` for JSON/file helpers. Output types must implement merge/source/finalize hooks, which `codesearch.Database` does. The C++ clang tool is expected to intercept execution when `SYZ_RUN_CLANGTOOL` is set; otherwise `init` panics to signal missing compiled-in tool support.

Risks: Cache reads bypass verification of freshness or tool/schema version unless the caller encodes it in `CacheFile`. `SortAndDedupSlice` deduplicates by marshaled JSON SHA-256, so equality depends on stable JSON representation. Running one process per compile command can be expensive on huge databases, though workers bound concurrency to CPU count.

Test signals: Used by `clangtool/tooltest` and `codesearch` tests. Error wrapping includes stderr for failed tool invocations, and verifier failures detect stale or bogus locations before downstream consumers use them.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/clangtool/clangtool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/clangtool/tooltest/tooltest.go -->
# sources/test-tools/syzkaller/pkg/clangtool/tooltest/tooltest.go

Purpose: Test harness for clangtool-backed packages. It creates per-fixture compile databases, runs a compiled-in clang tool, compares JSON output with golden files, and can load all golden outputs into a merged tool database.

Important APIs/types/functions: `FlagUpdate`, `TestClangTool`, `LoadOutput`, `ForEachTestFile`, `forEachTestFile`, `CompareGoldenFile`, and `CompareGoldenData`.

Control flow: `TestClangTool` skips non-Linux hosts, iterates `testdata/*.c`, writes a temporary `compile_commands.json` with `-DKBUILD_BASENAME`, runs `clangtool.Run`, marshals output, and compares to `<file>.json`. `LoadOutput` reads existing golden JSON for all fixture files, merges and finalizes them with a verifier.

State and persistence behavior: Temporary build dirs hold compile databases and cache files. Golden files are read from the source tree; when `-update` is set, `CompareGoldenData` overwrites the golden file.

Dependencies/integration points: Wraps `pkg/clangtool`, `pkg/osutil`, `pkg/testutil`, `sys/targets`, and `testify/require`. It expects fixture C files under a local `testdata` directory.

Risks: `forEachTestFile` ignores dotfiles and only selects `.c` files, so hidden fixtures need explicit separate tests. `-update` can rewrite goldens, so reviewers need to inspect golden diffs. The harness requires Linux because clang tools are only tested there.

Test signals: Provides reusable golden comparison for `codesearch` and any future clang tool output type implementing `OutputDataPtr`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/clangtool/tooltest/tooltest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/codesearch.go -->
# sources/test-tools/syzkaller/pkg/codesearch/codesearch.go

Purpose: Query layer over a source-code entity database for syzkaller's codesearch tool and LLM-facing workflows. It exposes commands for source tree navigation, bounded file reading, definitions, comments, references, and struct/union layouts.

Important APIs/types/functions: `Index`, `Command`, `Commands`, `IsSourceFile`, `NewIndex`, `NewTestIndex`, `Index.Command`, `Entity`, `FileIndex`, `EntityInfo`, `DefinitionComment`, `DefinitionSource`, `ReferenceInfo`, `FindReferences`, `findDefinition`, `GetStructLayout`, `formatSource`, `formatSourceFile`, `escaping`, `dirIndex`, `DirIndex`, and `ReadFile`.

Control flow: Commands validate argument counts through `Index.Command`, call helper methods, and format human-readable output. `FileIndex` first calls `ReadFile` to distinguish empty definition sets from missing files. `definitionSource` resolves an entity by context-aware name lookup and formats either body or comment range. `FindReferences` resolves target definitions, filters by source prefix and reference kind/entity kind/static visibility, optionally formats bounded context snippets, and enforces an output limit while still reporting total count.

State and persistence behavior: `Index` holds an in-memory `Database` loaded from JSON and a list of source directories. There is no mutation after construction. Source reads are bounded: `ReadFile` clamps line count to 1..100, and `FindReferences` clamps context lines to 10000.

Dependencies/integration points: Uses `codesearch.Database` records produced by clangtool, `tooltest.LoadOutput` for tests, `aflow.BadCallError` for user-facing bad tool calls, and `osutil` for filesystem helpers. It supports both source and generated/build directories through `srcDirs`.

Risks: `escaping` rejects cleaned paths containing `..`, which is conservative but string-based. `FindReferences` has a TODO for static symbol ambiguity across files. `GetStructLayout` treats a byte offset as matching a field when `targetBits <= offset+size`, so exact end-boundary semantics should be reviewed for off-by-one expectations. Command output is plain text and part of golden tests.

Test signals: `codesearch_test.go` runs every query fixture and ensures every registered command is covered. Golden fixtures exercise directory listing, reading, definitions, comments, references, and struct layouts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/codesearch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/codesearch_test.go -->
# sources/test-tools/syzkaller/pkg/codesearch/codesearch_test.go

Purpose: Golden tests for the codesearch clang extraction and query command layer.

Important APIs/types/functions: `TestClangTool`, `TestCommands`, and `testCommand`.

Control flow: `TestClangTool` delegates to `tooltest.TestClangTool[Database]` with the compiled codesearch clang tool. `TestCommands` loads a merged test index from `testdata`, finds `query*` fixture files, and runs each query. `testCommand` parses the first line into command plus arguments, executes `Index.Command`, converts expected bad-call errors into output text, and compares the result against the whole fixture file.

State and persistence behavior: Uses fixture files and golden `.json` databases. The `covered` map tracks which commands were exercised and fails if any command lacks a query fixture.

Dependencies/integration points: Integrates `clangtool/tooltest`, `osutil`, and the C++ tool package imported as `tools/clang/codesearch`.

Risks: The first-line parser only supports whitespace-separated args with simple surrounding quotes, not escaped spaces or complex shell syntax. Golden output tightly couples user-facing command text to tests.

Test signals: Provides full command registry coverage and validates clang database output against expected JSON for all test C files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/codesearch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/database.go -->
# sources/test-tools/syzkaller/pkg/codesearch/database.go

Purpose: Defines the JSON schema and merge/finalization behavior for codesearch entity databases emitted by clangtool.

Important APIs/types/functions: `Database`, `Definition`, `FieldInfo`, `Reference`, `LineRange`, `EntityKind`, `RefKind`, custom `String`/`MarshalJSON`/`UnmarshalJSON` methods, `DatabaseFormatHash`, `Database.Merge`, `Database.Finalize`, `Database.SetSourceFile`, and `intern`.

Control flow: Each clangtool output is merged by unique key `<kind>-<name>-<body file>`. New definitions are verified for body/comment line ranges, string fields are interned, and duplicate keys are ignored. `Finalize` collects merge-cache values into `Definitions`, sorts by the remembered stable key, and clears merge caches. `SetSourceFile` normalizes paths and marks static definitions as non-static if their body is in a different `.c` file than the compile unit.

State and persistence behavior: The public persisted state is JSON `definitions`. `mergeCache`, `reverseCache`, and `stringCache` are transient merge-time structures. `DatabaseFormatHash` hashes the generated JSON schema plus a semantic version string for cache invalidation by callers.

Dependencies/integration points: Implements the `clangtool.OutputDataPtr` contract. Uses `jsonschema.For[Database]` and `pkg/hash` to derive the format hash, and `clangtool.Verifier` to reject invalid source ranges during merge.

Risks: `EntityKind.String` and `RefKind.String` index directly into name arrays; invalid enum values could panic if constructed outside JSON parsing expectations. Duplicate definition identity ignores type/signature and line span, so conflicting definitions with same kind/name/file collapse silently. The comment above `SetSourceFile` has a typo but not behavioral impact.

Test signals: Validated indirectly by clangtool golden JSON, command tests, path verifier checks, and merge/finalize behavior in `tooltest.LoadOutput`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/database.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c

Purpose: C fixture for testing extraction of global variables, static file-local variables, macro-defined globals, and a simple function.

Important APIs/types/functions: Defines `DEFINE_VAR`, `DEFINE_STATIC_VAR`, `macro_var`, `static_macro_var`, `global_var`, `local_to_file_var`, and `some_function`.

Control flow: There is no runtime control flow beyond `some_function` assigning and discarding a local variable. The fixture exists to drive clang AST/database extraction.

State and persistence behavior: Declares initialized globals and statics in source form only. The resulting persisted state is represented in `global_vars.c.json`.

Dependencies/integration points: Consumed by `tooltest.TestClangTool` and codesearch golden tests. It validates that macro expansions and static attributes are reflected in the database.

Risks: Very small fixture; changes to line numbers or macro shape require updating the golden JSON.

Test signals: Expected definitions are captured in `global_vars.c.json`, including `is_static` on static variables.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c.json -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c.json

Purpose: Golden codesearch database for `global_vars.c`.

Important APIs/types/functions: Contains definitions for `some_function`, `global_var`, `local_to_file_var`, `macro_var`, and `static_macro_var`, with kinds, types, body line ranges, and static markers.

Control flow: This is static JSON data read by golden tests; it has no executable flow.

State and persistence behavior: Persists expected clangtool output for this fixture. It is source-of-truth for regression comparison unless regenerated with `-update`.

Dependencies/integration points: Loaded by `tooltest.LoadOutput` and compared by `tooltest.TestClangTool`.

Risks: Golden line ranges are sensitive to fixture edits. It intentionally omits the local variable inside `some_function`, so extractor changes that include locals would require semantic review.

Test signals: Confirms global-variable extraction, static tracking, and macro-defined variable extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/.slub.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/.slub.c

Purpose: Hidden empty C-like fixture under `testdata/mm` for directory filtering behavior.

Important APIs/types/functions: None; the file has zero lines.

Control flow: None.

State and persistence behavior: The file's existence and hidden basename are the relevant state. `dirIndex` skips entries whose names start with `.`.

Dependencies/integration points: Used by codesearch directory listing behavior to ensure hidden files are not exposed.

Risks: Empty hidden fixtures can be missed by test harnesses that glob only visible `.c` files, which is intentional here.

Test signals: Supports `dir-index` expectations for ignoring dot-prefixed source files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/.slub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c

Purpose: Small nested-directory C fixture for cross-directory reference search.

Important APIs/types/functions: Declares `int refs2();` and defines `ref_in_mm`, which calls `refs2`.

Control flow: `ref_in_mm` performs a single call to an externally defined `refs2`.

State and persistence behavior: No runtime state. Expected extracted state lives in `mm/refs.c.json`.

Dependencies/integration points: Tests `FindReferences` with source prefixes and nested paths such as `mm/refs.c`.

Risks: The declaration signature differs from the full definition in root `refs.c`, which is useful for extraction but can expose compiler warning sensitivity.

Test signals: Golden JSON records one function definition with a call reference to `refs2`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c.json -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c.json

Purpose: Golden codesearch output for nested fixture `mm/refs.c`.

Important APIs/types/functions: Contains definition `ref_in_mm` with body range `mm/refs.c:3-6` and one `calls` reference to function `refs2` on line 5.

Control flow: Static JSON only.

State and persistence behavior: Persisted expected entity/reference data for tests.

Dependencies/integration points: Loaded and merged into the test `Database`, then used by reference query fixtures.

Risks: Path normalization must keep the `mm/` prefix; otherwise reference source filtering can break.

Test signals: Confirms nested source path handling and references to entities defined in another file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c

Purpose: Two-line fixture used for `read-file` and directory listing tests.

Important APIs/types/functions: No C symbols; contains comments/text only.

Control flow: None.

State and persistence behavior: Source text is the state. It intentionally produces an empty codesearch JSON database.

Dependencies/integration points: Used by `ReadFile` tests to verify line formatting and nested file access.

Risks: Because it defines no entities, `FileIndex` should distinguish "file exists with no definitions" from missing file by reading the file first.

Test signals: Paired with empty `slub.c.json` and read-file golden queries.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c.json -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c.json

Purpose: Empty golden database for `mm/slub.c`, which has no extractable definitions.

Important APIs/types/functions: No definitions.

Control flow: Static JSON data only.

State and persistence behavior: Persists the expected empty clangtool result as `{}`.

Dependencies/integration points: Compared by clangtool golden tests and merged by `tooltest.LoadOutput`.

Risks: Empty JSON still needs to deserialize into a valid `Database`. If the tool starts emitting comments/macros for this fixture, this golden will change.

Test signals: Confirms the extractor can produce and consumers can accept empty database output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.h -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.h

Purpose: Empty header fixture in a nested source directory.

Important APIs/types/functions: None; zero lines.

Control flow: None.

State and persistence behavior: Its presence validates that `IsSourceFile`/`DirIndex` include `.h` files even when they have no contents.

Dependencies/integration points: Directory indexing and source-file filtering tests.

Risks: Empty headers are not consumed by clangtool's `.c` fixture walker, so behavior is limited to directory/source navigation.

Test signals: Supports directory listing expectations for header files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c

Purpose: C fixture for function references, address-taking, repeated references, struct fields, global arrays, and initializer references.

Important APIs/types/functions: Defines `refs0`, `refs1`, `refs2`, `refs3`, `long_func_with_ref`, `struct global_ops`, `global_init_target`, and global variable `my_global_ops`.

Control flow: `refs3` calls `refs2(refs1, refs0())` and takes the address of `refs2`. `long_func_with_ref` repeatedly calls `refs0`, `refs1`, and `refs2`. `my_global_ops` initializes function pointer field `prep` with `global_init_target`.

State and persistence behavior: Source definitions and initializer references are persisted in `refs.c.json`. No runtime persistence.

Dependencies/integration points: Exercises `FindReferences` output limits/context snippets, function address taking, global variable references, and struct field layout.

Risks: Repeated references intentionally stress output limits; changing line counts or adding references alters golden query expectations.

Test signals: Golden JSON includes body ranges, comments, refs, field layout for `global_ops`, and references from `my_global_ops`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c.json -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c.json

Purpose: Golden codesearch database for `refs.c`.

Important APIs/types/functions: Defines functions `global_init_target`, `long_func_with_ref`, `refs0`, `refs1`, `refs2`, `refs3`, struct `global_ops`, and global variable `my_global_ops`. Records call and takes-address references plus field layout for `global_ops.prep`.

Control flow: Static expected JSON.

State and persistence behavior: Persists expected reference and definition metadata for tests.

Dependencies/integration points: Used by `FindReferences`, `DefinitionSource`, `DefinitionComment`, and `GetStructLayout` query tests.

Risks: This golden has many line-sensitive references; source edits require synchronized fixture updates. It is also important for distinguishing `calls` from `takes-address-of`.

Test signals: Strong reference-search signal, including repeated references and global initializer references.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c

Purpose: Main C fixture for codesearch entity extraction across source/header boundaries, comments, duplicate names, typedef/union/struct usage, field reads/writes, static inline header calls, and compile database loading.

Important APIs/types/functions: Includes `source0.h`; defines `struct_in_c_file`, `open`, `close`, `function_with_comment_in_header`, `func_accepting_a_struct`, `function_with_quotes_in_type`, `field_refs`, and `reference_to_header_static`.

Control flow: Functions are simple, but each is structured to create specific AST references: function calls to duplicate-name symbols, casts through typedefs/unions, field reads/writes/address-taking, and a call to a static inline header function. A preprocessor guard fails compilation if `KBUILD_BASENAME` was not supplied by the test compile database.

State and persistence behavior: No runtime state; source and expected extraction are persisted through `source0.c.json`.

Dependencies/integration points: Depends on `source0.h`. Used by clangtool tests, file-index, definition/comment, reference, struct-layout, and compile_commands correctness tests.

Risks: The function named `open` can collide with common libc names conceptually, but this is intentional for extractor context. Line ranges and comments are golden-sensitive.

Test signals: Broadest C fixture in this set, validating definitions from included headers, type references, field references, comment extraction, static inline handling, and `-DKBUILD_BASENAME`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c.json -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c.json

Purpose: Golden database for `source0.c` plus included `source0.h` entities.

Important APIs/types/functions: Captures functions `close`, `field_refs`, `func_accepting_a_struct`, `func_in_header`, `function_with_comment_in_header`, `function_with_quotes_in_type`, `open`, `reference_to_header_static`; structs `another_struct`, `some_struct`, `some_struct_with_a_comment`, `struct_in_c_file`; union `some_union`; enum `some_enum`; typedefs `another_struct_t`, `some_enum_t`, `some_struct_t`, and `typedefed_struct_t`.

Control flow: Static JSON only, but references encode calls, type uses, field reads/writes, and field address-taking from the C source.

State and persistence behavior: Persists expected clangtool output, including body/comment ranges, static flags, field offsets/sizes, and references.

Dependencies/integration points: Used by all codesearch command tests and merged test database creation.

Risks: Large golden file is sensitive to clang AST extraction changes, target ABI field layout, and fixture line edits. It also tests quoted attributes in type strings.

Test signals: High-value fixture for entity lookup, struct layout, comment lookup, context-aware duplicate symbol resolution, and field reference classification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.h -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.h

Purpose: Header fixture included by `source0.c` to test extraction of comments, static inline functions, structs, typedefs, unions, enums, and duplicated function names across files.

Important APIs/types/functions: Declares `function_with_comment_in_header`, `same_name_in_several_files`, static inline `func_in_header`, `struct some_struct`, typedef `some_struct_t`, `struct some_struct_with_a_comment`, anonymous/ named struct typedefs, `union some_union`, `enum some_enum`, and `some_enum_t`.

Control flow: Only `func_in_header` has executable code, returning 0. Most content drives type/entity extraction.

State and persistence behavior: Source declarations are reflected in `source0.c.json` because the header is included by the compiled C fixture.

Dependencies/integration points: Included by `source0.c`; used for definition lookup and struct layout queries.

Risks: Header definitions are extracted through a compile unit, so changes to inclusion or compile database can affect visibility. Static inline functions in headers have special visibility rules in `findDefinition`.

Test signals: Validates header comments, type definitions, field offsets, union layout, enum/typedef extraction, and header-static function calls.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c

Purpose: Duplicate-name C fixture defining a static version of `same_name_in_several_files`.

Important APIs/types/functions: Static function `same_name_in_several_files`.

Control flow: Empty function body with an explanatory comment.

State and persistence behavior: Expected database state lives in `source1.c.json`, with `is_static: true`.

Dependencies/integration points: Tests context-aware definition resolution and static visibility in `codesearch.findDefinition` and `FindReferences`.

Risks: Static duplicate-name behavior is explicitly subtle; queries from other files should not resolve to this definition except through weak fallback rules.

Test signals: Golden JSON confirms static function extraction and comment range.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c.json -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c.json

Purpose: Golden database for `source1.c`.

Important APIs/types/functions: One static function definition, `same_name_in_several_files`, with body and comment ranges.

Control flow: Static JSON.

State and persistence behavior: Persists expected static duplicate-symbol metadata.

Dependencies/integration points: Merged into the codesearch test database to test duplicate symbol lookup against `source2.c` and `source0.h`.

Risks: Static flag correctness matters for reference filtering. Line edits require golden updates.

Test signals: Confirms extraction of static function and comment in a duplicate-name scenario.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c

Purpose: Duplicate-name C fixture defining a non-static `same_name_in_several_files`.

Important APIs/types/functions: Function `same_name_in_several_files`.

Control flow: Empty function body with an explanatory comment.

State and persistence behavior: Expected extracted state is in `source2.c.json`.

Dependencies/integration points: Used with `source1.c` and `source0.h` to test global versus static duplicate resolution.

Risks: Non-static duplicate resolution is weak-match fallback in `findDefinition`; fixture edits can alter query expectations.

Test signals: Golden JSON records a non-static duplicate-name function and comment range.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c.json -->
# sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c.json

Purpose: Golden database for `source2.c`.

Important APIs/types/functions: One non-static function definition, `same_name_in_several_files`, with body and comment ranges.

Control flow: Static JSON.

State and persistence behavior: Persists expected duplicate global symbol metadata.

Dependencies/integration points: Merged into codesearch tests to check context-aware lookup against the static same-name function.

Risks: Golden line ranges are sensitive to comments/source edits.

Test signals: Confirms non-static duplicate symbol extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/attrs.go -->
# sources/test-tools/syzkaller/pkg/compiler/attrs.go

Purpose: Defines syzlang attribute descriptors and parsing metadata for structs, unions, fields, and syscalls.

Important APIs/types/functions: `attrDescAttrType`, `attrDesc`, predefined descriptors such as `attrPacked`, `attrVarlen`, `attrSize`, `attrAlign`, `attrIn`, `attrOut`, `attrInOut`, `attrOutOverlay`, `attrIf`, maps `structAttrs`, `unionAttrs`, `structFieldAttrs`, `unionFieldAttrs`, `callAttrs`, and helpers `initCallAttrs`, `structOrUnionAttrs`, `structOrUnionFieldAttrs`, `makeAttrs`.

Control flow: Package init reflects over `prog.SyscallAttrs` to create syscall attribute descriptors. Additional init-time checks are attached for `size` and `align` attributes. The compiler later consumes these descriptors through `parseAttrs` and related checks/generation.

State and persistence behavior: Global immutable descriptor maps form compiler state. No persistence.

Dependencies/integration points: Depends on `pkg/ast` and `prog`. Attribute descriptors are used by `check.go`, `consts.go`, and `gen.go` to validate and generate syscall/type metadata.

Risks: Reflecting `prog.SyscallAttrs` means adding a new unsupported field kind will panic at init. Attribute name conversion relies on `prog.CppName`, so renames can affect source syntax.

Test signals: Covered indirectly by compiler testdata, attribute validation errors, and generation tests for syscall/field attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/attrs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/check.go -->
# sources/test-tools/syzkaller/pkg/compiler/check.go

Purpose: Semantic validation engine for syzlang ASTs. It performs phased checks before and after constants are patched, including names, type arguments, field paths, resource usability, recursion, varlen placement, attributes, and unused declarations.

Important APIs/types/functions: `typecheck`, `check`, `checkComments`, `checkDirectives`, `checkNames`, `checkFlags`, `checkFields`, `checkTypedefs`, `checkTypes`, `checkTypeValues`, `checkAttributeValues`, `checkFieldPaths`, `CollectUnused`, `CollectUnusedConsts`, `collectUnused`, `collectUsed`, `checkConstructors`, `checkRecursion`, `checkStruct`, `checkCall`, `checkType`, `replaceTypedef`, `instantiate`, `checkTypeArg`, `checkVarlens`, and `checkDupConsts`.

Control flow: `typecheck` handles syntax-adjacent semantics and basic type validity. `check` runs after constants are available and validates values, attributes, unused nodes, recursive layouts, constructor/input reachability, varlen rules, and const/flag conflicts. Typedef handling can instantiate template structs into synthetic AST nodes. Field-path validation resolves `len`, `bytesize`, `offsetof`, and `value(...)` paths through syscall arguments, parents, structs, and nested fields.

State and persistence behavior: Mutates compiler in-memory maps (`resources`, `typedefs`, `structs`, flags, used maps, generated template structs, errors/warnings). No disk persistence. Unsupported/broken typedef state prevents duplicate exponential errors.

Dependencies/integration points: Central to `Compile` in `compiler.go`; uses `ast`, `prog`, and `targets`. `CollectUnused` APIs are exported for other tooling.

Risks: Complex recursive traversal must avoid infinite loops through optional pointers, varlen arrays, templates, and parent paths. Field path checks intentionally limit `parent` depth. `checkDupConsts` is disabled due to false positives. Some TODOs mention incomplete transitive unsupported pruning.

Test signals: Extensive coverage through compiler `errors*.txt`, `warnings.txt`, `all.txt`, fuzz seeds, `CollectUnused` tests, flag flattening tests, and full sys description compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/compiler.go -->
# sources/test-tools/syzkaller/pkg/compiler/compiler.go

Purpose: Top-level syzlang compiler orchestration. It converts parsed AST descriptions and constants into `prog` resources, syscalls, and types.

Important APIs/types/functions: `Prog`, `createCompiler`, `Compile`, `compiler`, `error`, `warning`, `filterArch`, `structIsVarlen`, `parseIntAttrs`, `parseAttrs`, `parseAttrExprArg`, `parseAttrIntArg`, `parseAttrStringArg`, `getTypeDesc`, `getArgsBase`, `derefPointers`, `foreachType`, `foreachSubType`, `removeOpt`, `parseIntType`, `flattenFlags`, `flattenIntFlags`, `flattenStrFlags`, and `recurFlattenFlags`.

Control flow: `Compile` clones the AST, prepends built-ins, filters nodes by file metadata/target arch, typechecks, flattens nested flags, either extracts constants or assigns syscall numbers, patches constants, runs full semantic checks, generates syscalls/resources/types, lays out types, and emits warnings. If any phase records errors, compilation stops.

State and persistence behavior: All compiler state is in-memory. Returned `Prog.Unsupported` persists unsupported syscall/flag information to callers. If `consts == nil`, `Prog.fileConsts` is used internally by `ExtractConsts`.

Dependencies/integration points: Integrates `pkg/ast`, `prog`, and `sys/targets`. Called by sysgen, extraction tooling, tests, and fuzzing. It relies on helpers defined across `attrs.go`, `check.go`, `consts.go`, `gen.go`, `meta.go`, and `types.go`.

Risks: Phase ordering is critical; later checks assume type argument counts are valid. `structIsVarlen` caches before fully traversing recursive structures to avoid hangs. Flag flattening has a hard cap of 100000 values.

Test signals: Exercised by full target compilation in `compiler_test.go`, canned testdata, const extraction tests, and fuzzing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/compiler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/compiler_test.go -->
# sources/test-tools/syzkaller/pkg/compiler/compiler_test.go

Purpose: Core test suite for the syzlang compiler.

Important APIs/types/functions: `TestCompileAll`, `TestData`, `TestAutoConsts`, `TestFuzz`, `TestAlign`, `TestCollectUnusedError`, `TestCollectUnused`, `TestFlattenFlags`, and `TestSquashablePtr`.

Control flow: `TestCompileAll` parses every `sys/<os>/*.txt`, loads const files, and compiles for every target arch. `TestData` runs phase-specific canned inputs and expected errors/warnings. Other tests cover auto const files, fuzz regression seeds, recursive alignment, unused collection, nested flag flattening, and pointer squashing decisions.

State and persistence behavior: Reads sys descriptions, const files, and testdata. With `-update`, it can rewrite formatted `all.txt`. Otherwise no persistent writes.

Dependencies/integration points: Exercises `ast`, `serializer`, `prog`, `targets`, `DeserializeConstFile`, `ExtractConsts`, `FabricateSyscallConsts`, `Compile`, and `CollectUnused`.

Risks: `TestCompileAll` is broad and can be costly because it spans all OS/arch descriptions. The formatting update flag can rewrite source testdata. Some assertions inspect generated `prog.Type` details, so serializer/type layout changes can require updates.

Test signals: Very strong integration signal for parser, const extraction, semantic checking, code generation, target-specific constants, warnings, and regression fuzz seeds.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/compiler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/const_file.go -->
# sources/test-tools/syzkaller/pkg/compiler/const_file.go

Purpose: Serializer/deserializer for syzkaller `.const` files containing per-architecture constant values and undefined constants.

Important APIs/types/functions: `ConstFile`, `constVal`, `undefined`, `NewConstFile`, `AddArch`, `addConst`, `Arch`, `ExistsAny`, `Serialize`, `DeserializeConstFile`, `deserializeFile`, `parseConst`, and `parseOldConst`.

Control flow: `AddArch` records declared constants and undefined names for an arch. `Serialize` sorts arches/constants, chooses a default value when repeated across arches, and emits compact arch-specific overrides or `???`. `DeserializeConstFile` expands a glob, supports old per-arch filename format, detects weak `auto.txt.const`, and parses new compact lines.

State and persistence behavior: In-memory maps track arches and constant values/weak flags. Serialized text is persistent state used by sysgen and compiler tests. Weak values can be replaced on mismatch rather than erroring.

Dependencies/integration points: Used by compiler tests and sys description compilation to load constants. Error reporting uses `ast.ErrorHandler`.

Risks: `parseConst` assumes an `arches =` header for new format. Duplicate/mismatched non-weak values fail. Old-format support depends on `_([a-z0-9]+).const` filename matching and is marked temporary.

Test signals: `const_file_test.go` validates serialization, deserialization, undefined handling, defaults, per-arch values, and old-format compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/const_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/const_file_test.go -->
# sources/test-tools/syzkaller/pkg/compiler/const_file_test.go

Purpose: Unit tests for `.const` file serialization and deserialization.

Important APIs/types/functions: `TestConstFile`.

Control flow: The test builds three architecture constant maps with all-different, all-same, partially undefined, and fully undefined constants. It serializes them, compares exact text, checks `ExistsAny`, deserializes the new format from a temp file, and deserializes old per-arch files from a temp dir.

State and persistence behavior: Writes temporary const files only. Expected serialized string is embedded in the test.

Dependencies/integration points: Tests `NewConstFile`, `AddArch`, `Serialize`, `DeserializeConstFile`, `Arch`, and `ExistsAny`.

Risks: Exact output formatting is part of the contract; changes to compaction/order require updating the expected string.

Test signals: Strong coverage for const file compatibility and undefined/default encoding.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/const_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/consts.go -->
# sources/test-tools/syzkaller/pkg/compiler/consts.go

Purpose: Constant extraction and constant patching for syzlang ASTs.

Important APIs/types/functions: `ConstInfo`, `Const`, `ExtractConsts`, `FabricateSyscallConsts`, `constContext`, `extractConsts`, `foreachFieldAttrConst`, `extractTypeConsts`, `addConst`, `constInfo`, `convertConstInfo`, `assignSyscallNumbers`, `patchConsts`, `patchIntConst`, `patchTypeConst`, and `patchConst`.

Control flow: Extraction walks AST integer nodes, directives, defines, syscall numbers, syscall attrs, struct attrs, field conditions, and type arguments. Template instantiation context propagates constants used by template structs to files that instantiate them. Patching copies caller constants, adds built-ins like `PTR_SIZE`, assigns syscall numbers, replaces identifiers with values, removes unsupported flag values, and marks syscalls/declarations unsupported when constants are missing.

State and persistence behavior: Extraction returns per-file `ConstInfo` for external const generation. Patching mutates the cloned AST in memory and records unsupported declarations plus warnings. No direct disk writes.

Dependencies/integration points: Called by `Compile` and `ExtractConsts`; works with `ConstFile` and target syscall-number policy. Uses AST metadata to preserve include/incdir/define associations.

Risks: Missing constants are patched with value 1 to avoid cascading bad ranges, which can hide transitive issues until warnings are reviewed. TODOs note that unsupported dependency pruning is incomplete. Field attribute const extraction currently handles expression attrs only.

Test signals: `consts_test.go`, compiler canned `consts.txt` and `consts_errors.txt`, and full compile tests validate extraction, defines/includes/incdirs, syscall const fabrication, and missing-const handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/consts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/consts_test.go -->
# sources/test-tools/syzkaller/pkg/compiler/consts_test.go

Purpose: Tests for syzlang constant extraction and const extraction diagnostics.

Important APIs/types/functions: `TestExtractConsts` and `TestConstErrors`.

Control flow: `TestExtractConsts` parses `testdata/consts.txt`, extracts constants for Linux/amd64, and compares expected constant names, includes, incdirs, and defines. `TestConstErrors` parses `consts_errors.txt`, runs extraction, and checks expected diagnostics through `ast.ErrorMatcher`.

State and persistence behavior: Reads testdata only. No writes.

Dependencies/integration points: Exercises `ast.Parse`, `ExtractConsts`, target metadata, and compiler error handling.

Risks: Expected const list is explicit and must be updated with fixture changes. Diagnostics are phase-sensitive.

Test signals: Validates const discovery in syscall numbers, type arguments, defines, includes, incdirs, and error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/consts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/fuzz.go -->
# sources/test-tools/syzkaller/pkg/compiler/fuzz.go

Purpose: Go fuzz entrypoint for the syzlang compiler.

Important APIs/types/functions: `Fuzz`, `fuzzTarget`, and `fuzzConsts`.

Control flow: `Fuzz` parses arbitrary bytes with a no-op error handler. If parsing succeeds, it compiles the description against a test target and small constant map. It returns 1 only when compilation succeeds.

State and persistence behavior: No persistence. Uses package-level test target and const map.

Dependencies/integration points: Integrates `pkg/ast`, `Compile`, and `targets.Get` for `TestOS/TestArch64`.

Risks: Fuzz constants are intentionally small and may not cover all const-sensitive compiler branches. The no-op error handler suppresses diagnostics by design.

Test signals: Called by `TestFuzz` with regression seeds and suitable for external fuzzing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/gen.go -->
# sources/test-tools/syzkaller/pkg/compiler/gen.go

Purpose: Generates `prog` resources, syscalls, types, layouts, fields, padding, and expressions from checked syzlang ASTs.

Important APIs/types/functions: `sizeUnassigned`, `genResources`, `genResource`, `collectCallArgSizes`, `getCallName`, `genSyscalls`, `genSyscall`, `typeProxy`, `generateTypes`, `layoutTypes`, `layoutType`, `layoutArray`, `layoutUnion`, `layoutStruct`, `layoutStructFields`, `finalizeStructFields`, bitfield helpers, `genPad`, `genFieldArray`, `genFieldDir`, `genField`, `wrapConditionalField`, `genType`, `genExpression`, `genValue`, `genCommon`, `genIntCommon`, `genIntArray`, and `genStrArray`.

Control flow: Resource generation follows base-resource chains. Syscall generation first computes consistent syscall argument sizes across variants, generates calls, then marks pointer elements squashable after all recursive types exist. Type generation replaces concrete types in syscalls with deterministic `prog.Ref` indices. Layout recursively computes array/struct/union sizes, alignment, padding, overlays, and bitfields. Conditional fields are wrapped as anonymous unions with a `void` alternative.

State and persistence behavior: Mutates generated `prog.Type` objects, compiler `structTypes`, and synthetic conditional wrapper entries in memory. No disk persistence.

Dependencies/integration points: Uses `prog`, `serializer`, checked compiler state, type descriptors from `types.go`, and attributes from `attrs.go`. Output feeds syzkaller program generation/mutation.

Risks: Layout logic is dense and architecture-sensitive. Bitfield offset/unit-size handling has panic guards for unexpected states. `collectCallArgSizes` must keep syscall variants ABI-compatible. Conditional wrapping rewrites value paths by prepending parent references, which is easy to regress.

Test signals: Covered by compiler all-target tests, canned data, alignment tests, flatten flag tests, and squashable pointer tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/meta.go -->
# sources/test-tools/syzkaller/pkg/compiler/meta.go

Purpose: Handles syzlang file-level metadata such as automatic descriptions, no-extract markers, and supported architectures.

Important APIs/types/functions: `Meta`, `Meta.SupportsArch`, `FileList`, `compiler.fileMeta`, `compiler.fileList`, `metaTypes`, `metaAutomatic`, `metaNoExtract`, `metaArches`, and `metaArch`.

Control flow: `FileList` selects any target for an OS and delegates to a compiler to parse metadata. `fileList` scans AST nodes by basename, validates meta node types through `checkTypeImpl`, and sets `Automatic`, `NoExtract`, or `Arches`. `fileMeta` lazily builds and caches the map. `filterArch` in `compiler.go` consumes `SupportsArch`.

State and persistence behavior: Metadata is stored in the compiler's in-memory `fileMetas` map. No disk persistence.

Dependencies/integration points: Depends on `ast` and `targets`. Used by compiler filtering, syscall generation (`Automatic` attr), const collection, and unused-const collection.

Risks: Metadata is keyed by `filepath.Base(pos.File)`, so files with the same basename in different dirs could collide if descriptions include paths that are not unique by base. `FileList` returns nil for unknown OS.

Test signals: Covered indirectly by compiler testdata and full sys description compilation across arches.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/meta.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/types.go -->
# sources/test-tools/syzkaller/pkg/compiler/types.go

Purpose: Built-in syzlang type descriptor table. It defines validation, const checks, varlen/zero-size predicates, and generation for all core syzlang types.

Important APIs/types/functions: `typeDesc`, `typeArg`, `namedArg`, kind constants, descriptors `typeInt`, `typePtr`, `typeVoid`, `typeArray`, `typeLen`, `typeConst`, `typeFlags`, `typeVMA`, `typeCsum`, `typeProc`, `typeText`, `typeString`, `typeFmt`, `typeCompressedImage`, `typeResource`, `typeStruct`, `typeTypedef`, helper functions `generateFlagsType`, `getIntAlignment`, `isSquashableElem`, `constOverflowsBase`, `isBitmask`, `genStrings`, `stringSize`, `genDir`, built-in descriptor globals, and `builtinDefs`.

Control flow: `init` registers descriptor names into `builtinTypes` and parses `builtinDefs`. Each descriptor supplies custom checks and `Gen` logic consumed by `check.go` and `gen.go`. `typeStruct` and `typeResource` use init-time closures to break initialization cycles. Arrays can become buffer types, strings compute static or varlen sizes, integer arguments can become const/flags/range types, and resources derive base format from their root base type.

State and persistence behavior: Global built-in descriptor maps and parsed built-in AST are package state. Generated `prog.Type` instances are in-memory only.

Dependencies/integration points: Central to `Compile`; integrates with `ast`, `prog`, and target ABI settings such as pointer size/int64 alignment.

Risks: Descriptor checks are the compiler's ABI contract; small changes can affect all syscall descriptions. Some special cases are target- or legacy-driven, such as `xdp_mmap_offsets` and built-in ANY layouts known by `prog/any.go`. Invalid descriptor registration panics during init.

Test signals: Covered broadly by all compiler tests, type-specific error testdata, fuzz seeds, squashable pointer checks, and full target compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/compiler/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/config/config.go -->
# sources/test-tools/syzkaller/pkg/config/config.go

Purpose: Small JSON config load/save helper with support for line comments starting with `#` and strict unknown-field rejection.

Important APIs/types/functions: `LoadFile`, `LoadData`, and `SaveFile`.

Control flow: `LoadFile` rejects empty filenames, reads file bytes, and delegates to `LoadData`. `LoadData` strips comment lines with a regexp, decodes JSON with `DisallowUnknownFields`, and wraps parse errors. `SaveFile` marshals indented JSON and writes via `osutil.WriteFile`.

State and persistence behavior: Reads and writes config files. No internal persistent state.

Dependencies/integration points: Used by syzkaller components that load manager/tool configs. Depends on standard JSON and `pkg/osutil`.

Risks: The comment stripper removes full lines beginning with optional whitespace and `#`; it does not support inline comments. Strict unknown fields are good for config hygiene but can break users with stale/extra fields.

Test signals: No direct tests in this file, but config merge tests cover adjacent package behavior; downstream config-loading tests likely exercise it.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/config/merge.go -->
# sources/test-tools/syzkaller/pkg/config/merge.go

Purpose: Recursive JSON object merge and patch helpers for syzkaller configs, especially when raw JSON subdocuments should be merged rather than replaced wholesale.

Important APIs/types/functions: `MergeJSONs`, `PatchJSON`, `parseFragment`, and `mergeRecursive`.

Control flow: `MergeJSONs` parses both JSON fragments and marshals the recursive merge result. `PatchJSON` parses the left JSON and merges a Go map patch. `parseFragment` treats empty input as nil. `mergeRecursive` returns the non-nil side when one side is nil, replaces non-map values with the right side, and recursively merges `map[string]any` values.

State and persistence behavior: Stateless pure byte/map transformation. Output JSON is compact marshaled JSON.

Dependencies/integration points: Used when layering config fragments or applying structured patches.

Risks: Arrays and scalar values are replaced, not merged. Number types become `float64` through `encoding/json` generic unmarshalling. Map iteration is normalized by `json.Marshal` for deterministic key order in tests.

Test signals: `merge_test.go` covers shallow merge, nested merge, empty-right preservation, and map patch replacement/creation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/config/merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/config/merge_test.go -->
# sources/test-tools/syzkaller/pkg/config/merge_test.go

Purpose: Unit tests for recursive JSON merge and patch helpers.

Important APIs/types/functions: `TestMergeJSONs` and `TestPatchJSON`.

Control flow: Each table-driven test calls `config.MergeJSONs` or `config.PatchJSON`, expects no error, and compares compact JSON bytes exactly.

State and persistence behavior: In-memory only.

Dependencies/integration points: Exercises public `pkg/config` merge APIs from an external `config_test` package.

Risks: Exact byte comparisons rely on deterministic marshal ordering. Tests do not cover invalid JSON, arrays, null patches, or number type nuances.

Test signals: Confirms recursive object merging, right-side scalar replacement, empty fragment handling, and map patch insertion.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/config/merge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/corpus.go -->
# sources/test-tools/syzkaller/pkg/corpus/corpus.go

Purpose: Thread-safe in-memory corpus of syzkaller programs, aggregate signal/coverage, update notifications, statistics, and focus-area program lists.

Important APIs/types/functions: `Corpus`, `focusAreaState`, `FocusArea`, `NewCorpus`, `NewMonitoredCorpus`, `NewFocusedCorpus`, `ItemUpdate`, `Item`, `Item.StringCall`, `NewInput`, `NewItemEvent`, `Corpus.Save`, `applyFocusAreas`, `Signal`, `Items`, `Item`, `CallCover`, `ProgsPerArea`, and `Cover`.

Control flow: Constructors initialize maps, weighted program lists, focus areas, and stats. `Save` serializes and hashes a program, locks the corpus, either merges signal/coverage into an existing immutable-copy `Item` or creates a new one, applies focus areas based on coverage deltas, updates aggregate signal/coverage, and optionally sends a non-blocking/context-aware `NewItemEvent`.

State and persistence behavior: Corpus state is in memory behind `sync.RWMutex`: program map, aggregate signal, coverage, program lists, focus area lists, and stats. It emits serialized program bytes in update events but does not write files itself. `Item` objects are treated as immutable and replaced on updates.

Dependencies/integration points: Integrates `cover`, `signal`, `stat`, `hash`, and `prog`. Used by fuzzing components to save interesting programs and choose future mutation seeds.

Risks: `applyFocusAreas` initializes `item.areas` only inside the `nil` branch and immediately records one area; if an item later matches additional areas after `areas` is non-nil, that area is not recorded in `item.areas`, which can affect minimization repopulation. `Save` caps `Updates` at 32 to bound memory, losing later per-call update history.

Test signals: `corpus_test.go` covers basic save/update events, coverage delta reporting, stats, minimization call, and concurrent save/choose operations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/corpus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/corpus_test.go -->
# sources/test-tools/syzkaller/pkg/corpus/corpus_test.go

Purpose: Tests for corpus save/update, coverage aggregation, stats, and concurrent access.

Important APIs/types/functions: `TestCorpusOperation`, `TestCorpusCoverage`, `TestCorpusSaveConcurrency`, `generateInput`, `generateRangedInput`, and `getTarget`.

Control flow: Tests generate programs for the test target, save them to monitored or plain corpus instances, read update events, check `Exists` and `NewCover`, query items and stats, call `Minimize`, and run concurrent goroutines that save and choose programs.

State and persistence behavior: Uses in-memory corpus state and channels. No disk writes.

Dependencies/integration points: Exercises `prog.Target.Generate`, signal creation, corpus APIs, and target lookup.

Risks: `TestCorpusSaveConcurrency` starts goroutines but does not wait for them, so it is more of a race/smoke trigger than deterministic completion test. Running with the race detector would add value.

Test signals: Covers event semantics, aggregate signal/coverage stats, item lookup, minimization entrypoint, and basic concurrent lock safety.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/corpus_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/minimize.go -->
# sources/test-tools/syzkaller/pkg/corpus/minimize.go

Purpose: Reduces the corpus to a smaller set of programs that preserves aggregate signal, with preference for simpler/non-squashed programs.

Important APIs/types/functions: `Corpus.Minimize`.

Control flow: Under corpus write lock, it builds `signal.Context` entries for all items, stable-sorts them to prefer items without squashed `any` arguments and then fewer calls, clears `progsMap` and all program lists, runs `signal.Minimize`, and repopulates maps/lists for retained items and their focus areas.

State and persistence behavior: Mutates in-memory corpus state destructively under lock. It does not recompute aggregate `signal` or `cover`, so those remain frontier totals, not minimized item sums.

Dependencies/integration points: Depends on `pkg/signal.Minimize` and `ProgramsList.saveProgram`.

Risks: The `cover bool` parameter is currently unused, which may surprise callers expecting coverage-aware minimization. Rebuilding focus area lists relies on each `Item.areas` map being complete.

Test signals: Invoked by `TestCorpusOperation`; deeper minimization correctness depends on `pkg/signal` tests and priority tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/minimize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/prio.go -->
# sources/test-tools/syzkaller/pkg/corpus/prio.go

Purpose: Weighted random selection of corpus programs, including optional focus-area weighted selection.

Important APIs/types/functions: `ProgramsList`, `chooseProgram`, `saveProgram`, `Corpus.ChooseProgram`, and `Corpus.Programs`.

Control flow: `saveProgram` assigns priority equal to signal size, falling back to 1, and appends cumulative priority. `chooseProgram` samples an integer from cumulative priority and binary-searches `accPrios`. `ChooseProgram` optionally picks a non-empty focus area by configured weights and samples within it, otherwise samples the whole corpus.

State and persistence behavior: `ProgramsList` stores in-memory program slices and cumulative priorities. `ChooseProgram` reads under corpus lock.

Dependencies/integration points: Used by fuzzing mutation scheduling. Depends on `signal.Signal`, `prog.Prog`, and caller-provided `rand.Rand`.

Risks: `chooseProgram` calls `Int63n(pl.sumPrios + 1)`, making zero a possible value and slightly biasing the first program because `accPrios[0] >= 0` is always true. Focus-area selection loop assigns `randArea` whenever `val >= currSum`, effectively ending with the last area whose prefix is below `val`; this works for positive weights but should be reviewed for zero/negative weights.

Test signals: `prio_test.go` statistically checks whole-corpus priority distribution and focus-area weight distribution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/prio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/prio_test.go -->
# sources/test-tools/syzkaller/pkg/corpus/prio_test.go

Purpose: Statistical tests for program selection priorities and focus-area weights.

Important APIs/types/functions: `TestChooseProgram` and `TestFocusAreas`.

Control flow: `TestChooseProgram` builds 1000 inputs with varying signal sizes, samples 1000 choices, and checks observed counts against expected priority probabilities within an epsilon. `TestFocusAreas` creates three weighted focus areas, fills each with programs covering selected PCs, samples 10000 choices, and asserts counts near 10/30/60 percent.

State and persistence behavior: In-memory corpus and random sources only.

Dependencies/integration points: Uses helper generators from `corpus_test.go`, `prog` targets, and `testify/assert`.

Risks: Statistical tests can be flaky if tolerances are too tight or RNG behavior changes. The whole-corpus test includes zero-signal cases mapped to priority 1 but records expected priority as `len(signal)`, which is worth reviewing against `saveProgram` fallback behavior.

Test signals: Provides distribution-level confidence for selection algorithms and focus-area weighting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/corpus/prio_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/backend.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/backend.go

Purpose: Public coverage backend facade and shared data model for symbolization/coverage mapping across ELF, Mach-O, and gVisor backends.

Important APIs/types/functions: `Impl`, `CompileUnit`, `Symbol`, `ObjectUnit`, `Frame`, `Range`, `SecRange`, `LineEnd`, `Make`, and `GetPCBase`.

Control flow: `Make` derives kernel dirs, target, module object paths, and VM type from manager config. It requires a kernel object directory, dispatches to `makeMachO` for Darwin, `makeGvisor` for gVisor, and otherwise `makeELF`, optionally passing Android split-build path delimiters. `GetPCBase` returns Linux PC base only for non-gVisor/non-Starnix Linux targets; otherwise 0.

State and persistence behavior: `Impl` holds in-memory compile units, symbols, frames, callback points, precise coverage flag, and a `Symbolize` function. No direct persistence in this file.

Dependencies/integration points: Integrates `mgrconfig`, `vminfo.KernelModule`, and `targets`. Other backend files implement ELF, DWARF, Mach-O, module discovery, and PC helpers.

Risks: Missing `KernelDirs().Obj` fails early. Backend selection is target/VM sensitive; new VM types may need explicit handling in both `Make` and `GetPCBase`. Android delimiter handling is hard-coded to known Pixel path markers.

Test signals: This file is mostly integration glue; backend-specific tests live in adjacent files such as ELF tests, while higher-level coverage flows exercise `Make`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/backend.go -->
