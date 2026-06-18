# Research: subset-b-008530

This grouped report covers the exact subset B work item `subset-b-008530`. Each section is source-tree aligned and wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/lint/lint_test.go -->
# sources/storage-engines/pebble/internal/lint/lint_test.go

## Purpose
This file defines Pebble's repository-level lint test. It is not a library lint package; it is an integration test that shells out to Go tooling, CockroachDB-specific developer tools, and grep-based source checks to enforce project style and correctness rules across `github.com/cockroachdb/pebble/...`.

## Important APIs, Types, And Functions
`TestLint` is the central test. It resolves the module root with `build.Import`, lists all packages with `go list ./...`, runs `go vet` first, and then runs several independent subtests. `dirCmd` executes a command in a directory and exposes combined output as a `stream.Filter`, treating non-zero exit codes as expected lint output rather than immediate test failure. `ignoreGoMod` filters noisy module download lines. `installTool` installs tools from `../devtools` through `go install -C`. `lintIgnore` consumes paired grep context lines and drops findings preceded by a specific ignore directive.

## Control Flow
The test skips on Windows, 386, and slow/instrumented builds. `TestGoVet` runs first and aborts the remaining lint suite if it fails, reducing noise from build failures. The rest of the subtests use `t.Parallel` where safe: `gcassert`, `staticcheck`, custom `roachvet`, grep checks for panic arguments, `fmt.Errorf`, `os.Is*`, `runtime.SetFinalizer`, raw atomics, forbidden imports, and `crlfmt`. Several checks build a `stream.Sequence` pipeline that runs a command, filters lines, and reports remaining lines as test errors.

## State, Persistence, And Side Effects
The test has no persisted application state, but it mutates the developer environment by installing lint tools into the active Go tool bin. It shells out to `git grep`, `go list`, `go vet`, and format/lint binaries, so behavior depends on the working tree, module cache, and available toolchain. The `crlfmt` subtest only reports formatting drift and logs a rewrite command; it does not modify files.

## Dependencies And Integration Points
The file depends on `github.com/ghemawat/stream` for stream processing, `testify/require`, `go/build`, `os/exec`, Pebble build tags, CockroachDB errors, and the tools declared by import path constants. It integrates with Pebble's `internal/devtools` module, the root Go module, Git, and repository-specific lint conventions like `lint:ignore PanicArgs`, `lint:ignore SetFinalizer`, and `lint:ignore RawAtomics`.

## Risks And Edge Cases
The lint suite is intentionally environment-sensitive. Missing tools, path issues, or module-cache/network problems can fail the test before source issues are evaluated. `lintIgnore` assumes `git grep -B1` emits exact pairs of directive and finding lines; changing grep context could make ignores unreliable. The forbidden import check loads packages with `UseAllFiles`, falling back for multiple-package directories, so generated/build-tag-only imports may still need care. The raw regex checks are broad and require explicit ignore directives for legitimate exceptions.

## Test Signals
This file is itself the test signal. Passing `go test ./internal/lint` indicates the repository builds under `go vet`, static analysis tools run cleanly, CockroachDB formatting is satisfied, and banned APIs/imports are absent except where ignored. Failures are line-oriented and intended to be clickable in IDEs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/lint/lint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/lsmview/data.go -->
# sources/storage-engines/pebble/internal/lsmview/data.go

## Purpose
This file defines the JSON data contract for generating an external LSM visualization. It is a small schema package used by code that wants to describe Pebble levels, tables, key boundaries, and table details in a compact form.

## Important APIs, Types, And Functions
`Data` is the root document with `Levels []Level` and `Keys []string`. `Level` names a displayed LSM level and contains `Tables []Table`. `Table` carries a string label, byte size, integer indexes into `Data.Keys` for smallest and largest keys, and a list of detail strings. The JSON tags define the public wire shape: `level_name`, `tables`, `label`, `size`, `smallest_key`, `largest_key`, and `details`.

## Control Flow
There is no executable control flow. The code is a set of Go structs whose tags are consumed by `encoding/json`, most directly by `GenerateURL` in `url.go`.

## State, Persistence, And Side Effects
The schema is immutable by convention but not enforced by the type system. State is serialized into JSON and then embedded into URL fragments by the companion encoder. The `SmallestKey` and `LargestKey` fields are indexes, not duplicated key strings, so correctness depends on callers keeping `Keys` sorted and the table indexes valid.

## Dependencies And Integration Points
The file has no imports. It integrates with `url.go`, with any Pebble code that transforms manifest/version metadata into diagram data, and with the external `raduberinde.github.io/lsmview/decode.html` viewer expected to understand this JSON shape.

## Risks And Edge Cases
The types do not validate key-index bounds, key order, level order, or whether table key spans are coherent. A caller can create a `Table` whose indexes are out of range or reversed. Because the schema is part of a URL payload contract, changing JSON field names is a compatibility risk for existing viewers and tests.

## Test Signals
Coverage comes indirectly from `url_test.go`, which constructs a `Data` value and asserts that `GenerateURL` emits the expected compressed URL. There are no data-only tests for schema validation because the schema intentionally has no validators.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/lsmview/data.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/lsmview/url.go -->
# sources/storage-engines/pebble/internal/lsmview/url.go

## Purpose
This file converts an `lsmview.Data` value into a shareable visualization URL. The payload is JSON-encoded, zlib-compressed, base64 URL-encoded, and stored in the URL fragment.

## Important APIs, Types, And Functions
`GenerateURL(data Data) (url.URL, error)` is the only exported function. It JSON-encodes the data into a buffer, compresses the JSON through a zlib writer, base64 URL-encodes the compressed bytes, closes both encoders, and returns an HTTPS URL targeting `raduberinde.github.io/lsmview/decode.html` with the encoded payload as `Fragment`.

## Control Flow
The function is linear: JSON encode, create nested encoders, stream the JSON buffer into zlib, close the zlib writer to flush the compressed stream, close the base64 encoder to flush padding/final bytes, and construct the URL. Each serialization step returns early on error. The function does not attempt to decode or validate the data after encoding.

## State, Persistence, And Side Effects
There is no durable local state. The encoded state is persisted in the URL fragment. The fragment is not sent to the server in normal HTTP requests, which keeps the full LSM payload client-side for the static viewer. The function allocates intermediate buffers proportional to the JSON and compressed payload sizes.

## Dependencies And Integration Points
The function depends on `bytes`, `compress/zlib`, `encoding/base64`, `encoding/json`, and `net/url`. Its integration boundary is the external viewer's expected fragment encoding; the test fixture locks down this encoding including the host, path, zlib stream, and base64 alphabet.

## Risks And Edge Cases
Large LSMs may produce URLs that exceed browser or sharing limits because all data lives in the fragment. `base64.URLEncoding` includes padding, so changing to raw encoding would break compatibility. The function uses `json.Encoder.Encode`, which appends a newline before compression; the test captures that exact behavior. Any change in compression level or JSON encoding can invalidate stable test vectors.

## Test Signals
`url_test.go` builds a two-level, four-table dataset and asserts the exact URL string. This gives strong regression coverage for the encoding pipeline and the viewer endpoint, but it does not test decoding, invalid data, or very large payload behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/lsmview/url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/lsmview/url_test.go -->
# sources/storage-engines/pebble/internal/lsmview/url_test.go

## Purpose
This file verifies that `GenerateURL` produces a deterministic LSM viewer URL for a representative `Data` payload.

## Important APIs, Types, And Functions
`TestGenerateURL` constructs a `Data` value with two levels, four tables, ordered boundary keys, table labels, sizes, key indexes, and details. It calls `GenerateURL`, checks that no error is returned, and compares `url.String()` against a fixed expected URL.

## Control Flow
The test is straightforward: arrange a fixture, call the encoder, trim whitespace from the expected multiline string, and assert exact equality. The fixture comments document the intended key-index relationships for human readers.

## State, Persistence, And Side Effects
The test has no durable state and does not perform network access. It only checks the local string representation of the URL. Because the expected fragment contains compressed binary data represented as base64, the test is sensitive to every byte of the encoding pipeline.

## Dependencies And Integration Points
The test depends on `strings.TrimSpace`, Go testing, and `testify/require`. It integrates with `data.go` and `url.go`, and indirectly with Go's JSON encoder, zlib implementation, base64 URL encoding, and `net/url.String`.

## Risks And Edge Cases
The exact-string assertion is useful but brittle. Semantically equivalent changes, such as a different compression level, raw base64 encoding, or JSON encoding without a trailing newline, will fail the test. The fixture does not validate viewer behavior, URL length limits, empty levels, duplicate keys, or invalid table indexes.

## Test Signals
Passing this test signals that the current URL contract for a normal multi-level LSM diagram is stable. A failure usually indicates a deliberate or accidental wire-format change that must be coordinated with the external viewer and any consumers of generated links.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/lsmview/url_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator.go -->
# sources/storage-engines/pebble/internal/manifest/annotator.go

## Purpose
This file implements the generic annotation cache used over Pebble manifest B-tree nodes. An annotator computes an aggregate value across a subtree of file metadata and caches that aggregate on the node when every contributing item reports that the value is stable.

## Important APIs, Types, And Functions
`annotator[T, M fileMetadata]` holds an annotation index, a merge function, and an item function. `annotationIdx` selects a slot in `nodeAnnotations.cachedValues`. `nodeAnnotations` stores up to `maxAnnotationsPerNode` `atomic.Value` entries per B-tree node. `Reset` clears all cached values when a node is about to mutate. `nodeAnnotation` recursively computes or returns a cached subtree aggregate.

## Control Flow
`nodeAnnotation` first checks the node's cached value for the annotator index. On a cache miss, it allocates a `T`, aggregates every item in the node, recurses into children if the node is internal, and tracks whether all item/subtree annotations were cacheable. It stores the computed pointer only if all contributors were stable. If any item is unstable, the result is returned but not cached, forcing future recomputation.

## State, Persistence, And Side Effects
Annotation state is in-memory only and attached to B-tree nodes. It is not persisted to manifests. Cache invalidation is coupled to B-tree copy-on-write mutation through `nodeAnnotations.Reset` in `mut`. Cached values are stored as pointers in `atomic.Value`, allowing concurrent readers to race benignly to compute and store equivalent results.

## Dependencies And Integration Points
The file depends only on `sync/atomic` plus manifest-local B-tree types. It is the generic substrate for `TableAnnotator` and `BlobFileAnnotator`. It relies on the `fileMetadata` abstraction implemented by `TableMetadata` and `BlobFileMetadata`.

## Risks And Edge Cases
Annotation indexes are global per annotator family and limited by `maxAnnotationsPerNode`. Reusing the same index for incompatible annotators on the same tree can return incorrect cached values. Merge functions must treat the zero value as identity and must be deterministic. Item functions must accurately report cacheability; returning true for mutable statistics would make stale node annotations possible.

## Test Signals
The direct behavior is exercised through `annotator_test.go`, which defines a count annotator and a pick-file annotator, validates level and range annotations, and benchmarks cached aggregation. Blob annotator behavior is structurally similar but not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator_blob.go -->
# sources/storage-engines/pebble/internal/manifest/annotator_blob.go

## Purpose
This file adapts the generic B-tree annotator to `BlobFileSet`, allowing callers to compute aggregate values over all blob files in a version using cached B-tree subtree annotations.

## Important APIs, Types, And Functions
`BlobFileAnnotator[T]` embeds `annotator[T, BlobFileMetadata]`. `MakeBlobFileAnnotator` builds an annotator from a `BlobFileAnnotationIdx` and `BlobFileAnnotatorFuncs`. `BlobFileAnnotatorFuncs` supplies `Merge` and `BlobFile` callbacks. `Annotation` computes the aggregate over a `BlobFileSet`. `BlobFileAnnotationIdx` and `NewBlobAnnotationIdx` provide globally unique cache slots for blob annotations.

## Control Flow
Construction wraps caller-supplied callbacks into the generic `annotator`. `Annotation` returns a zero `T` for an empty blob file set; otherwise it calls `nodeAnnotation` on the set's B-tree root and returns the computed value. `NewBlobAnnotationIdx` increments a package-global counter and panics with an assertion failure if more than `maxAnnotationsPerNode` blob annotators are allocated.

## State, Persistence, And Side Effects
Annotator indexes are process-global initialization state. Computed values are cached in B-tree nodes within `BlobFileSet` and invalidated when nodes mutate. No annotation data is persisted to the manifest; it is derived from manifest-backed blob metadata.

## Dependencies And Integration Points
The file depends on CockroachDB `errors` for assertion panics. It integrates with `BlobFileSet`, the generic B-tree, and blob-file metadata management in `blob_metadata.go`. The design mirrors table annotation in `annotator_table.go`.

## Risks And Edge Cases
The global index allocator is not synchronized and is intended for global initialization, not dynamic concurrent allocation. Exceeding four annotation slots panics. Callback correctness is critical: unstable blob-file properties must return `cacheOK=false`, and merge must be associative enough for tree-shaped aggregation to match linear aggregation.

## Test Signals
There is no direct blob annotator test in this subset. Confidence comes from the shared generic annotator tests and from `BlobFileSet` B-tree tests. Consumers adding blob annotators should add focused tests for cacheability and aggregate correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator_blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator_table.go -->
# sources/storage-engines/pebble/internal/manifest/annotator_table.go

## Purpose
This file provides cached aggregate computations over `TableMetadata` B-trees, including whole-level, multi-level, range-limited, and version-wide annotations. It is used for efficient manifest-derived decisions such as counting overlapping files or picking a best candidate file without scanning every table.

## Important APIs, Types, And Functions
`TableAnnotator[T]` embeds `annotator[T, *TableMetadata]` and adds an optional `partialOverlapFunc`. `MakeTableAnnotator` constructs one from `TableAnnotatorFuncs`. `NewTableAnnotationIdx` allocates cache slots. `accumulateRangeAnnotation` is the core range traversal. Public APIs include `LevelAnnotation`, `MultiLevelAnnotation`, `LevelRangeAnnotation`, and `VersionRangeAnnotation`. `MakePickFileAnnotator` specializes a table annotator that returns one preferred eligible file using `PickFileAnnotatorFuncs`.

## Control Flow
Whole-level annotation delegates to `nodeAnnotation`. Range annotation descends the B-tree, using key comparisons to find item and child ranges that overlap the requested `UserKeyBounds`. If a subtree is known fully inside both bounds, it reuses the cached node annotation. Boundary files can use `PartialOverlap` when only part of the file overlaps; otherwise the normal item annotation is merged. Version range annotation iterates L0 sublevel slices and levels 1+, accumulating per-slice range annotations.

## State, Persistence, And Side Effects
The file maintains a package-global `nextTableAnnotationIdx` used at initialization time. Computed annotations are transient node caches and are invalidated by B-tree mutation. No values are persisted. The API assumes caller-provided callbacks are pure relative to their cacheability flag.

## Dependencies And Integration Points
Dependencies include `sort`, CockroachDB `errors`, and Pebble `base` key bounds/comparers. Integration points include `LevelMetadata`, `LevelSlice`, `Version.L0SublevelFiles`, the copy-on-write B-tree, and compaction/manifest code that needs fast aggregate metadata.

## Risks And Edge Cases
The range traversal is sensitive to inclusive/exclusive bound semantics and to B-tree ordering. Only boundary files can use `PartialOverlap`; a missing partial callback means boundary files are counted as whole files. Index reuse or over-allocation can corrupt cache lookup or panic. Version-wide annotation must handle L0 sublevels separately because L0 is not represented as a single non-overlapping level.

## Test Signals
`annotator_test.go` validates count annotations over whole levels and ranges, including empty ranges, random bounds, and performance comparisons against `Version.Overlaps`. It also tests `MakePickFileAnnotator` by ensuring the smallest eligible file remains selected across insertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator_table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator_test.go -->
# sources/storage-engines/pebble/internal/manifest/annotator_test.go

## Purpose
This file tests the table annotation framework using concrete annotators over synthetic level metadata. It verifies cached whole-level annotation, range annotation, pick-file aggregation, and benchmark behavior.

## Important APIs, Types, And Functions
`NumFilesAnnotator` counts tables by merging `uint64` values. `makeTestVersion` creates a test `Version` with files in level 6, each covering a 10-key span. `TestNumFilesAnnotator`, `TestPickFileAggregator`, `TestNumFilesRangeAnnotationEmptyRanges`, and `TestNumFilesRangeAnnotationRandomized` are the main correctness tests. `BenchmarkNumFilesAnnotator` and `BenchmarkNumFilesRangeAnnotation` measure whole-level and range aggregation costs.

## Control Flow
The tests construct versions, mutate the underlying level B-tree through insertions/deletions, and compare annotator results with expected counts or with `Version.Overlaps`. Randomized range tests use a deterministic PCG seed. The range benchmark alternates deleting and reinserting files to exercise cache invalidation under small mutations.

## State, Persistence, And Side Effects
All state is in-memory test state. The tests directly mutate `v.Levels[6].tree`, so they exercise B-tree annotation invalidation paths. `makeTestVersion` initializes physical table backings to satisfy file metadata ref/unref expectations.

## Dependencies And Integration Points
The file depends on `math/rand/v2`, `testing`, Pebble `base`, and `testify/require`. It integrates annotation APIs with `Version`, `LevelMetadata`, B-tree mutation, user-key bounds, and overlap iteration.

## Risks And Edge Cases
The tests intentionally use annotator index `0`, which is safe in the isolated test process but demonstrates why production annotators must allocate distinct indexes. Empty-range tests delete blocks of files to cover holes and partial overlaps. Random tests cover many bounds but not custom `PartialOverlap` behavior or unstable cacheability.

## Test Signals
Passing tests signal that cached annotations update after tree edits, range pruning matches `Version.Overlaps`, and pick-file aggregation preserves the preferred file. Benchmarks provide performance signals for cached aggregation versus explicit overlap scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/annotator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/bench_test.go -->
# sources/storage-engines/pebble/internal/manifest/bench_test.go

## Purpose
This file contains an external-package benchmark for level iterator seek performance over realistic CockroachDB-style keys. It measures manifest `LevelIterator.SeekGE` behavior on a non-trivial B-tree-backed level.

## Important APIs, Types, And Functions
`BenchmarkLevelIteratorSeekGE` allocates 10,000 `manifest.TableMetadata` entries, generates random CockroachDB keys with `cockroachkvs.RandomKVs`, builds `LevelMetadata` through `manifest.MakeLevelMetadata`, creates an iterator, and repeatedly seeks keys.

## Control Flow
The benchmark creates paired keys per table, extends each table's point key bounds, initializes physical backing metadata, builds the level, resets the timer, and loops over `b.N` calls to `iter.SeekGE` using keys modulo the generated key count.

## State, Persistence, And Side Effects
State is local benchmark state. There is no persistence. The benchmark uses current time as part of random seed/config generation, so exact data distribution changes across runs, while the measured structure size remains stable.

## Dependencies And Integration Points
The file is in package `manifest_test`, so it exercises the public manifest surface rather than internal helpers. It depends on `cockroachkvs`, Pebble `base`, `manifest`, `math/rand/v2`, and `time`. It integrates manifest level metadata with CockroachDB key formatting/comparison behavior.

## Risks And Edge Cases
Because the benchmark uses time-dependent randomness, microbenchmark variance can include data-shape variance. It focuses on `SeekGE` and does not measure reverse seeks, iterator creation, deletion, copy-on-write behavior, or L0-overlap semantics. The benchmark assumes generated key pairs are suitable as smallest/largest bounds.

## Test Signals
This is a performance signal only. It is useful for detecting regressions in level iterator seek cost under realistic key distributions, but it is not a correctness test and will not fail unless setup panics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/blob_metadata.go -->
# sources/storage-engines/pebble/internal/manifest/blob_metadata.go

## Purpose
This file defines manifest metadata and live-state tracking for Pebble blob value files. It bridges stable blob file IDs referenced by sstables, physical blob files on disk, version reference counts, lookup mappings, aggregate statistics, and rewrite-candidate selection for space reclamation.

## Important APIs, Types, And Functions
`BlobReference` records a table's reference to a blob file ID, value sizes, and estimated physical size. `MakeBlobReference` validates and computes that estimate. `BlobFileMetadata` maps stable `FileID` to a reference-counted `PhysicalBlobFile`. `PhysicalBlobFile` stores file number, size, value size, creation time, refs, and optional blob properties. `BlobReferences` implements `sstable.BlobReferences`. `BlobFileSet` is a copy-on-write B-tree keyed by blob file ID with `All`, `Count`, `Lookup`, `LookupPhysical`, `clone`, `insert`, `remove`, and `release`. `CurrentBlobFileSet` tracks blob files and references in the latest version, with `Init`, `ApplyAndUpdateVersionEdit`, `Stats`, `Metadatas`, `ReplacementCandidate`, and `ReferencingTables`. Heap helpers rank rewrite candidates by live-data ratio or creation time.

## Control Flow
Blob reference construction validates non-zero and bounded value sizes in invariant builds. Physical files increment/decrement atomic refs as versions and table metadata are retained or released; refcount zero adds the file to obsolete files. `BlobFileSet.LookupPhysical` manually inlines B-tree search for read-path performance. `CurrentBlobFileSet.Init` loads blob files from a `BulkVersionEdit`, walks extant table references, computes aggregate stats, and places partially unreferenced files into either a recently-created heap or rewrite-candidate heap. `ApplyAndUpdateVersionEdit` updates the current set for new blob files, replacement blob files, new table references, deleted table references, obsolete blob-file deletions, heap membership, and aged-file promotion.

## State, Persistence, And Side Effects
Manifest persistence is represented by version edits containing blob-file additions/deletions and table blob references; this file itself mostly manages derived in-memory state. `PhysicalBlobFile.refs` and `propsValid` are atomic mutable fields. `BlobFileSet` is version-scoped copy-on-write state that preserves old versions. `CurrentBlobFileSet` is latest-version mutable state protected by the version set log lock and is explicitly not thread-safe. `ApplyAndUpdateVersionEdit` mutates the input `VersionEdit` by adding `DeletedBlobFiles` when references disappear.

## Dependencies And Integration Points
Dependencies include `container/heap`, generic iterators, maps/slices, atomics, time, CockroachDB errors/redaction, Pebble `base`, `humanize`, `invariants`, `strparse`, `sstable`, and `sstable/blob`. Integration points include manifest version edit encode/decode, `BulkVersionEdit`, table metadata blob references, obsolete-file collection, read-path blob lookup through `base.BlobFileMapping`, and compaction scheduling for blob rewrite candidates.

## Risks And Edge Cases
Reference accounting is the core risk: table moves in the same version edit must decrement temporary double-counting without deleting references, and deleted tables must use the same `*TableMetadata` identity recorded in `currentBlobFile.references`. Virtual sstables without `BackingValueSize` make rewrite eligibility unsafe and are tracked separately. Replacement blob files must be paired with a matching deleted physical file entry. Heap indexes must remain synchronized through push/remove/fix operations. `MakeBlobReference` can overflow `valueSize * phys.Size` for extreme values. Debug parsers are test-only and intentionally parse string formats rather than persisted binary records.

## Test Signals
`blob_metadata_test.go` covers debug parse round trips, datadriven `CurrentBlobFileSet` behavior, lookup correctness over 10,000 blob files, and lookup benchmarking. Broader manifest tests outside this subset cover version edit persistence and blob file invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/blob_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/blob_metadata_test.go -->
# sources/storage-engines/pebble/internal/manifest/blob_metadata_test.go

## Purpose
This file tests blob metadata parsing, latest-version blob-file tracking, blob lookup correctness, and lookup performance.

## Important APIs, Types, And Functions
`TestPhysicalBlobFile_ParseRoundTrip` and `TestBlobFileMetadata_ParseRoundTrip` verify debug string parsers. `TestCurrentBlobFileSet` drives `CurrentBlobFileSet` through datadriven commands. `TestBlobFileSet_Lookup`, `makeTestBlobFiles`, and `BenchmarkBlobFileSet_Lookup` validate and measure `BlobFileSet.Lookup`.

## Control Flow
Parse tests iterate table-driven inputs with optional whitespace, optional humanized sizes, and optional creation times. The datadriven test parses version edits, preserves `*TableMetadata` pointer identity across commands, initializes a `BulkVersionEdit`, applies version edits, and prints modified edits/current state/stats/candidates. Lookup tests build 10,000 physical blob files with some FileIDs mapping to different physical file numbers, then assert returned object file info.

## State, Persistence, And Side Effects
The tests keep mutable maps of table metadata to mimic version identity across datadriven operations. The datadriven fixture file `testdata/current_blob_file_set` is an external test dependency. Current time is simulated by a closure that advances by one second and logs timestamps, allowing deterministic age-heuristic testing.

## Dependencies And Integration Points
The file depends on `bytes`, `fmt`, `testing`, `time`, `datadriven`, Pebble `base`, and `testify/require`. It integrates debug parsers, version edit parsing, `BulkVersionEdit.Accumulate`, `CurrentBlobFileSet`, and B-tree-backed `BlobFileSet`.

## Risks And Edge Cases
Pointer identity is explicitly repaired after parsing because current blob references are keyed by `*TableMetadata`; forgetting this would make delete-reference tests invalid. Parse tests verify permissive formatting but not malformed inputs. Lookup tests cover many entries and replacement-style physical file numbers but not missing lookups or concurrent access.

## Test Signals
Passing tests signal that human debug formats round-trip, latest-version blob-file stats/rewrite state match datadriven expectations, and blob ID lookup returns the correct physical blob file at scale. The benchmark provides a read-path performance signal for manual B-tree lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/blob_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/btree.go -->
# sources/storage-engines/pebble/internal/manifest/btree.go

## Purpose
This file implements Pebble's generic copy-on-write B-tree for manifest file metadata. It stores `TableMetadata` or `BlobFileMetadata` in sorted order, supports efficient insert/delete/iteration, shares nodes across version clones, maintains file reference counts, and hosts annotation caches.

## Important APIs, Types, And Functions
`btreeCmp` and specific comparators order tables by sequence number, smallest key, or blob file ID. `fileMetadata` requires `String`, `Ref`, and `Unref`. `node` stores fixed-size items, optional child metadata, refcount, and annotations. `btree` exposes `Clone`, `Release`, `Insert`, `Delete`, `All`, `Count`, and `String`. Internal helpers include `mut`, `clone`, `decRef`, split/rebalance/merge/remove functions, and `verifyInvariants`. `iterator` plus `iterStack` implements first/last/next/prev/find/countLeft/clone/comparison traversal.

## Control Flow
Writes acquire mutable nodes through `mut`; if a node is shared, it is cloned and the old ref is decremented, preserving copy-on-write isolation. Insert splits full nodes on descent and increments item refs before insertion. Delete rebalances or merges underfull children before removal, unreferences the removed item, and collapses an empty root. Release recursively dereferences all contents. Iterators descend/ascend using a compact stack and are invalidated by tree mutation.

## State, Persistence, And Side Effects
The tree is in-memory manifest state, but it determines lifetime of persisted table backings and blob files through `Ref`/`Unref`. Node refcounts are atomic so clones can support concurrent readers and independent writers. Annotation caches live in nodes and are reset when mutable nodes are modified. Tree contents themselves are persisted elsewhere through version edits, not by this data structure.

## Dependencies And Integration Points
The file depends on `cmp`, `bytes`, `fmt`, generic `iter`, `strings`, atomics, CockroachDB errors, and Pebble invariants. It integrates with `LevelMetadata`, `LevelSlice`, `BlobFileSet`, `Version` reference management, obsolete-file tracking, and table/blob annotators.

## Risks And Edge Cases
Refcount correctness is critical: clone and mutation paths must net out item and child refs exactly or files may leak or be deleted early. `assertNoObsoleteFiles` enforces that ordinary tree mutations do not make physical files obsolete; only version release should. Iterator comparisons assume both iterators come from the same root. Writes are not safe for concurrent mutation by multiple goroutines, while reads are safe. Duplicate comparator keys return errors and would violate level invariants if ignored.

## Test Signals
`btree_test.go` covers ordered and reverse inserts/deletes, iterator traversal and clone comparison, seek behavior, duplicate insert errors, concurrent clone isolation, stack behavior, end sentinel behavior, randomized operations, and broad benchmarks. Other files exercise the same tree through level metadata and blob-file sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/btree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/btree_test.go -->
# sources/storage-engines/pebble/internal/manifest/btree_test.go

## Purpose
This file provides correctness tests, randomized tests, concurrency/clone tests, iterator tests, and benchmarks for the manifest B-tree.

## Important APIs, Types, And Functions
Test helpers include `newItem`, `cmp`, `key`, `Verify`, `verifyLeafSameDepth`, `verifyCountAllowed`, `isSorted`, `checkIter`, `perm`, and `rang`. Correctness tests include `TestBTree`, `TestIterClone`, `TestIterCmpEdgeCases`, `TestIterCmpRand`, `TestBTreeSeek`, `TestBTreeInsertDuplicateError`, `TestBTreeCloneConcurrentOperations`, `TestIterStack`, `TestIterEndSentinel`, and `TestRandomizedBTree`. Benchmarks cover insert, delete, delete/insert, clone-heavy mutation, iterator creation, seek, next, and prev.

## Control Flow
The main B-tree test inserts and deletes 768 items in sorted and reverse order, periodically verifying structural invariants and iterator order. Clone tests recursively create copy-on-write clones in goroutines, mutate subsets independently, and verify all snapshots. Randomized testing compares the tree against a map of file numbers across thousands of insert/delete/iterate operations. Benchmarks build varied tree sizes and isolate specific operations.

## State, Persistence, And Side Effects
All state is in-memory. Tests initialize physical backing metadata so deleting from the B-tree can produce obsolete table backings where expected. Concurrent clone tests intentionally exercise atomic node refs and independent mutation after cloning, then release all trees and expect each original backing to become obsolete exactly once.

## Dependencies And Integration Points
The file depends on `cmp`, `fmt`, `math/rand/v2`, reflection, slices, sync, testing, time, CockroachDB errors, Pebble `base`, build tags, and `testify/require`. It integrates B-tree internals with `LevelIterator`, `TableMetadata`, obsolete-file accounting, and build-tag-driven race/slow-test behavior.

## Risks And Edge Cases
Tests rely on unexported internals because they are in package `manifest`. Randomized tests use time seeds and log them for reproduction. Expensive full-tree verification is throttled in `TestBTree` to control runtime while still covering split/merge boundaries. Concurrency tests validate clone isolation, not arbitrary concurrent mutation of the same tree.

## Test Signals
Passing tests strongly indicate B-tree shape invariants, sorted order, subtree counts, iterator sentinels, seek logic, duplicate detection, copy-on-write behavior, and ref/unref accounting are intact. Benchmarks provide performance baselines across tree sizes and clone patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/btree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/doc.go -->
# sources/storage-engines/pebble/internal/manifest/doc.go

## Purpose
This package documentation records the correctness argument for organizing L0 into sublevels. It explains why ordering L0 files by sequence-number-derived metadata can preserve read semantics and how L0-to-base and intra-L0 compactions can safely choose triangular sets of files.

## Important APIs, Types, And Functions
There are no Go declarations beyond `package manifest`. The important content is the proof sketch: claims about file-add history, key sequence ordering, largest sequence number ordering, equivalence between simple add-order stacks and sequence-number stacks, and safety arguments for sublevel compactions.

## Control Flow
The document progresses from historical file addition order, through two core claims about overlapping keys and largest sequence numbers, to sublevel organization. It then discusses L0-to-Lbase compactions as bottom triangles and intra-L0 compactions as inverted top triangles, including the role of `earliest-unflushed-seq-num` and output-file ordering.

## State, Persistence, And Side Effects
The file has no runtime state or side effects. Its persistence role is architectural: it captures assumptions that the implementation in `l0_sublevels.go`, compaction picking, ingest/flush ordering, and sequence-number assignment rely on.

## Dependencies And Integration Points
The proof references Pebble ingest/flush behavior, memtable flush ordering, atomic ingests, commit pipeline sequencing, L0 sublevels, Lbase compactions, and historical GitHub issues. It is the design companion to `l0_sublevels.go` and to compaction picker logic that enforces triangular selection.

## Risks And Edge Cases
The proof is explicitly marked incomplete in places, especially for the hybrid real LSM where compactions remove files from L0 at arbitrary times. TODOs call out missing details for hybrid correctness and L0-to-Lbase compactions. If ingest/flush sequencing or output ordering changes, this proof must be revisited.

## Test Signals
There are no tests for the document itself. Its claims are indirectly tested by L0 sublevel tests, compaction picker tests, version/invariant checks, and read correctness tests elsewhere in Pebble.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/l0_sublevels.go -->
# sources/storage-engines/pebble/internal/manifest/l0_sublevels.go

## Purpose
This file implements Pebble's L0 sublevel organization and L0 compaction-selection machinery. It turns overlapping L0 files into non-overlapping sublevel slices, computes interval metadata for fast overlap reasoning, tracks in-progress compactions, chooses L0-to-base and intra-L0 compaction candidates, exposes flush split keys, and maintains the current organizer state across version edits.

## Important APIs, Types, And Functions
Key types include `intervalKey`, `l0FileState`, `fileInterval`, `L0Compaction`, `l0Sublevels`, `L0CompactionFiles`, `L0Organizer`, and `L0PreparedUpdate`. Construction and update functions include `newL0Sublevels`, `sortAndSweep`, `mergeIntervals`, `canUseAddL0Files`, `addL0Files`, and `addFileToSublevels`. Runtime APIs include `InitCompactingFileInfo`, `ReadAmplification`, `InUseKeyRanges`, `FlushSplitKeys`, `MaxDepthAfterOngoingCompactions`, `PickBaseCompaction`, `PickIntraL0Compaction`, `ExtendL0ForBaseCompactionTo`, `UpdateStateForStartedCompaction`, `NewL0Organizer`, `PrepareUpdate`, `PerformUpdate`, `SubLevelOf`, and `ResetForTesting`.

## Control Flow
`newL0Sublevels` builds interval boundary keys from every L0 file's smallest and largest user key, sorts/deduplicates them, assigns each file a min/max interval index, adds files in increasing L0 sequence order, sorts per-sublevel files by interval, builds `LevelSlice` B-trees, computes flush split keys, and runs invariant checks. `addL0Files` is an incremental fast path for pure additions at the top of L0: it shallow/deep copies the old state as needed, merges new interval keys into old intervals, remaps old file interval indexes, updates estimated bytes, inserts new files, rebuilds affected sublevel slices, and recomputes flush split keys.

## State, Persistence, And Side Effects
`l0Sublevels` is derived in-memory state for the current version. It stores immutable level slices plus mutable compaction counters/flags initialized under DB and manifest locks. Per-file state is indexed by L0 order and mapped by table number. Flush split keys are derived from interval byte estimates and `flushSplitBytes`. `L0Organizer` owns current L0 metadata, sublevels, and a generation counter; `PrepareUpdate` can run concurrently to precompute work, while `PerformUpdate` applies one prepared update and sets `newVersion.L0SublevelFiles`.

## Compaction Behavior
Base compaction picking scores intervals by stack depth minus compacting files, prioritizes intervals not near base-compacting ranges, skips problem spans, seeds from the lowest sublevel file in a hot interval, and grows a triangular candidate downward to preserve sequence correctness. It rejects candidates blocked by compacting Lbase files. Intra-L0 picking is used when base compaction cannot be chosen; it seeds from the highest eligible sublevel, excludes files newer than `earliestUnflushedSeqNum`, grows an inverted triangle, and may extend toward a rectangle when safe. Both paths cap candidate growth heuristically when bytes jump sharply beyond 100 MiB or exceed a 500 MiB hard threshold after a viable candidate exists.

## Dependencies And Integration Points
The file depends on `bytes`, `cmp`, `fmt`, maps/slices/sort/math/strings, CockroachDB errors, Pebble `base`, invariants, and `problemspans`. It integrates with `LevelMetadata`, `LevelSlice`, `TableMetadata` compaction flags, `Version.L0SublevelFiles`, `BulkVersionEdit`, compaction picker scheduling, flush splitting, problem-span avoidance, and the proof sketch in `doc.go`.

## Risks And Edge Cases
Inclusive largest-key handling is subtle because intervals simulate immediate successors with an `isInclusiveEndBound` flag. Incremental add remapping is complex and must update old file interval indexes, inherited interval contents, byte estimates, and affected B-trees exactly. Compaction state must be initialized under the right locks because `TableMetadata.Compacting` fields are not safe to read during sublevel construction. Candidate extension must avoid compacting files and avoid selecting files that would require unselected older/younger versions of the same keys. The `PickIntraL0Compaction` allocation currently creates a slice length equal to intervals even though skipped entries keep zero values, making zero-interval handling worth watching.

## Test Signals
This file is covered by L0 sublevel tests outside this subset, including sublevel construction, incremental add equivalence, and benchmarks noted by `rg`. In this subset, `doc.go` provides the design proof and `btree`/level metadata tests validate core structures used by `LevelSlice`. Runtime invariant checks (`Check`, `verifyLevelMetadataTransition`, occasional rebuild comparison in `PerformUpdate`) provide strong debug-mode signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/l0_sublevels.go -->
