# sources/test-tools/lcov/bin/genhtml lines 1-7224

## Scope and Purpose

This chunk is the front half of the `genhtml` Perl executable from LCOV. It starts with program metadata, imports, global defaults, function prototypes, and then defines the bulk of the in-memory model used to convert LCOV trace data into differential HTML report data. The line range ends in `main` while command-line and lcovrc option tables are being assembled; the actual option parsing and most HTML writer implementations continue in later lines.

The central purpose of this chunk is to build report-ready coverage summaries from current trace data, optional baseline trace data, optional unified diff data, optional source annotations, and optional callbacks. It categorizes coverpoints into LCOV differential TLAs such as `UNC`, `GNC`, `LBC`, `CBC`, `DUB`, and `DCB`; builds per-file, per-directory, per-owner, and per-age-bin summaries; loads or synthesizes source lines; and schedules file/directory/top-level report generation serially or through forked child jobs.

## Major Packages and Responsibilities

### Script Setup and Global State

- The script imports standard Perl modules for filesystem work, process state, timing, serialization, cloning, path handling, and dates: `File::Basename`, `File::Path`, `File::Spec`, `File::Temp`, `Cwd`, `DateTime`, `Date::Parse`, `Storable`, `POSIX`, and others.
- It imports LCOV-local behavior from `lcovutil`, including tool metadata, warning/error handling, parsing helpers, coverage flags, precision/rate helpers, path filtering, and callback/error constants.
- Global defaults define report thresholds, image/navigation sizes, field widths, sort modes, header modes, HTML settings, source-view behavior, differential display flags, and scheduler debugging.
- The first-line prototypes declare the HTML writer and data-processing functions that are implemented later in the file, including `gen_html`, `process_file`, `write_summary_pages`, `write_source`, `write_file_table`, and `write_function_table`.
- `main` state begins near the end of this chunk: current/base trace objects, `DiffMap`, path prefix options, report titles, output directory, baseline/diff settings, owner/date display flags, source synthesis, hierarchy/flat-view mode, HTML extension/gzip state, function alias behavior, and lcovrc/CLI option maps.

### `SummaryInfo`

`SummaryInfo` is the main aggregate data structure for top-level, directory, and file summaries. Instances are array-backed objects whose slots hold type/name/parent/path metadata plus coverage data for lines, branches, MC/DC, and functions.

Important behavior:

- Defines the differential TLA ordering, display titles, legacy mappings, default date cutpoints, owner-table truncation controls, and compact summary-table defaults.
- `_initCounts()` initializes count buckets for `found`, `hit`, and all supported TLAs.
- `noBaseline()` switches display semantics to the simplified `GNC`/`UNC` model when no baseline is available.
- `setAgeGroups()` sorts date-bin cutpoints, validates optional labels, creates default labels, and builds `ageHeaderToBin`.
- `new()` creates file, directory, or top-level records and preallocates age bins when annotation is enabled.
- `append()` merges child summaries into parent summaries, including normal count totals, per-age buckets, and per-owner buckets for each supported coverage type.
- Accessors and counters such as `get`, `get_rate`, `get_missed`, `lineCovCount`, `branchCovCount`, `mcdcCovCount`, and `functionCovCount` provide uniform summary arithmetic.
- Owner/date helpers such as `owners`, `owner_tlaCount`, `findOwnerList`, `hasOwnerInfo`, and `hasDateInfo` drive owner and age-bin detail tables.
- `removeLine()` backs out summary counts when select filtering drops a line from a source view.
- `checkCoverageCriteria()` packages summary data into callback input, including optional date and owner details, then invokes `CoverageCriteria::executeCallback`.

### Detail Callback Classes

Several small classes normalize how later HTML table code asks for coverage counts:

- `OwnerDetailCallback` returns owner-specific counts for a selected coverage type.
- `DateDetailCallback` returns age-bin-specific counts.
- `FileOrDirectoryCallback` returns total coverage data and destination links for files/directories.
- `FileOrDirectoryOwnerCallback` and `FileOrDirectoryDateCallback` provide secondary table rows grouped by owner or age bin and can enumerate matching files.
- `CovTypeSummaryCallback` adapts a `SummaryInfo` instance for branch, MC/DC, or function totals.
- `PrintCallback` tracks the current TLA, owner, age, and next navigation positions while rendering source lines.

These classes are integration glue between the data model in this chunk and the HTML writer functions defined later.

### `LineData` and `FileCoverageInfo`

`LineData` represents one logical source line across baseline/current versions. It stores old and current line numbers, line hit counts, branch data, MC/DC data, function data, and the resulting differential TLA. Deleted lines use synthetic string keys like `<<<123` and store the closest current-line leader as a negative line number.

`FileCoverageInfo` creates a per-file differential coverage map from current trace data, optional baseline trace data, and a `DiffMap`.

Key categorization behavior:

- `_categorize()` maps baseline/current hit counts to baseline TLAs: `UBC`, `GBC`, `LBC`, `CBC`, or excluded-current TLAs `EUC`/`ECC`.
- `_categorizeIfExcluded()` handles no-baseline/current-only cloning with excluded coverpoints.
- `_categorizeLineCov()` walks current line coverage, then baseline line coverage, aligns lines through `DiffMap`, marks inserted/deleted/equal lines, records deleted-line regions, and assigns line TLAs.
- `_categorizeBranchCov()` aligns branch blocks by line and code, preserving baseline/current counts in cloned branch elements. Inserted/current-only branches become `UNC`/`GNC`; deleted branches become `DUB`/`DCB`; current-only branch blocks on unchanged lines become `UIC`/`GIC`; missing current blocks on unchanged lines become `EUB`/`ECB`.
- `_categorizeMcdcCov()` performs similar logic for MC/DC expression groups and both boolean senses.
- `_categorizeFunctionCov()` aligns functions by leader line, clones function entries, stores differential function entries in `functionMap`, handles aliases, and uses known function end lines to recategorize unchanged functions with changed bodies as new-code TLAs where appropriate.
- `recategorizeTlaAsBaseline()` rewrites `UIC`/`GIC` into `UBC`/`CBC` for old files newly added to coverage, including line, branch, MC/DC, and function data.

The categorization logic is intentionally tolerant of inconsistent trace/diff data. Many inconsistencies are reported through `lcovutil::ignorable_error`, allowing configured `--ignore-errors` behavior to continue.

### `DiffMap`

`DiffMap` parses and queries unified diff data.

Important behavior:

- Stores `LINEMAP` chunks keyed by current filename, `FILEMAP` mappings from current to baseline names, captured deleted baseline lines, diff file locations, unchanged-file markers, symlink aliases, and the diff root.
- `load()` reads unified diff data and optionally scans build directories for symlink aliases that can reconcile source paths.
- `_read_udiff()` parses:
  - `Git Root: ...` records.
  - `=== file` unchanged records.
  - `--- old` and `+++ new` filename records.
  - `@@ -old,count +new,count @@` hunk headers.
  - space, `-`, `+`, and empty content lines.
- `lookup()` maps a line number from old to new or new to old.
- `type()` returns whether a line is `EQUAL`, `INSERT`, or `DELETE`, falling back to identity/equal/insert behavior when no diff was loaded.
- `recreateBaseline()` rebuilds baseline source text from current source plus deleted lines captured from the diff.
- `find_deleted_line_leader()` and `compute_deleted_lines()` map deleted baseline regions to current source anchors for source-view navigation.
- `check_version_match()` and `check_path_consistency()` compare diff paths and versions against baseline/current trace files, including basename-mismatch diagnostics and optional `elide_path_mismatch` repair.

### Source Loading and Annotation

`ReadBaselineSource` extends `ReadCurrentSource` so baseline source can be reconstructed from current source plus `DiffMap` when needed.

`SourceLine` is a line-level record containing line number, text, owner abbreviation/full name, date, age, commit id, and attached line/branch/MC/DC/function TLA data.

`SourceFile` is the per-source-file detail model used by source views and navigation:

- `_load()` resolves paths, checks optional file versions, invokes annotation callbacks when configured, falls back to file reads, and optionally synthesizes missing source content.
- `_computeAge()` computes line age in days from annotation timestamps, honoring `SOURCE_DATE_EPOCH` for reproducible report generation and warning when annotation time is in the future.
- `_synthesize()` pads missing source lines from coverage data and function end lines, optionally adding synthetic annotation metadata.
- `_bare_load()` reads real source lines into `SourceLine` records.
- The constructor loads/synthesizes lines, optionally recategorizes old newly-covered files as baseline, applies select filtering with `InInterestingRegion`, counts line/branch/MC/DC/function TLAs into `SummaryInfo`, and records owner/category line lists for navigation.
- `simplify()` drops most source-detail data after file-page generation when running in parallel and when the full serializable database is not needed.
- Navigation helpers such as `nextTlaGroup`, `nextCategoryTlaGroup`, `nextInDateBin`, `nextInOwnerBin`, `nextBranchInDateBin`, `nextMcdcInDateBin`, `nextBranchInOwnerBin`, and `nextMcdcInOwnerBin` find the next line matching category/owner/date filters.

`InInterestingRegion` supports select callbacks by expanding selected code coverpoints with contiguous matching non-code lines plus configurable context lines.

### `TestcaseTlaCount`

`TestcaseTlaCount` stores per-testcase counts for line, branch, MC/DC, or function coverage. In normal mode it records `found` and `hit`; with TLA display enabled and `SourceFile` details available, it also counts hit coverpoints by differential TLA. Function handling respects `merge_function_aliases`.

### `GenHtml` Scheduler

`GenHtml` orchestrates report computation across files, directories, and the top-level summary.

Control flow:

1. `new()` creates the top-level `SummaryInfo`, builds pending dependency records, orders files using optional profile-history predictions, creates directory records for hierarchical or legacy two-level layout, and adds file tasks to the worklist.
2. `compute()` repeatedly segments ready work, runs jobs serially or forks child workers, waits for children when parallelism or memory limits require it, and finishes when no jobs/work/pending dependencies remain.
3. `_segment_worklist()` groups ready tasks into job segments based on available parallelism and `max_tasks_per_core`, creates output directories unless HTML generation is disabled, and computes relative/base/truncated directory names.
4. `compute_one()` dispatches a single file, directory, or top-level task to `main::process_file()` or `main::write_summary_pages()`, then runs coverage criteria checks and optionally shrinks file details.
5. `merge_one()` merges completed file/directory/top summaries into their parent and clears dependency entries.
6. `_process_child()` captures child stdout/stderr, runs assigned tasks, serializes task results and lcovutil state deltas to a temp `Storable` file, and returns an exit status.
7. `_waitChild()` and `merge_child()` reap children, restore serialized results, replay output, merge summaries, update criteria/profile state, detect missing or corrupt dumps, and reschedule jobs after recoverable child failures.
8. `_reschedule()` and `_report_fail_and_reschedule()` restore task directory state and retry jobs after fork/child/serialization problems.

Persistent scheduler state is written under a `File::Temp->newdir("genhtml_XXXX", DIR => $lcovutil::tmp_dir, CLEANUP => 1)` directory with files named like `genhtml_$pid.log`, `genhtml_$pid.err`, and `dumper_$pid`.

## State and Persistence Behavior

- Most objects are array-backed Perl objects with numeric slot constants. This is compact and serialization-friendly, but makes slot ordering part of the internal ABI.
- Top, directory, and file summaries form a tree through `SummaryInfo` parent/source links. In parallel children, parent/source references are cleared before serialization to reduce dump size.
- Coverage counts are held in hashes keyed by `found`, `hit`, and TLA names. Age bins and owner bins are merged upward from file to directory to top-level summaries.
- Source details can be discarded or simplified after HTML generation to reduce memory. `buildSerializableDatabase`, `show_details`, `no_sourceview`, `frames`, and `show_tla` determine how much survives.
- Diff parsing persists deleted baseline text so baseline source can be reconstructed for source reads and deleted-code display.
- Annotation and version/profile/criteria callback effects are tracked in global lcovutil state and per-package counters; child processes serialize deltas for the parent to merge.
- Output side effects in this range are mostly scheduler temp files, output directory creation, optional empty-directory cleanup, diagnostics to stdout/stderr, and updates to global profile timing data. Actual HTML/CSS/image writing functions are mostly outside this chunk.

## Dependencies and Integration Points

- LCOV internal modules and classes: `lcovutil`, `TraceFile`, `TraceInfo`, `CountData`, `BranchLocation`, `BranchBlock`, `BranchElement`, `MCDC_Block`, `FunctionEntry`, `ReadCurrentSource`, `InOutFile`, `CoverageCriteria`, `MessageContext`, and `Capture::Tiny`. Many are defined in LCOV library files, not this script chunk.
- External callbacks: annotate callbacks, select callbacks, coverage criteria callbacks, version extraction callbacks, simplify-function callbacks, and profile-history callbacks.
- Filesystem integration: source reads, diff reads, output directory creation, symlink alias scanning, temporary directory/dump/log files, source path realpath/abs path normalization, and case-insensitive path mode.
- Process integration: `fork`, `wait`, `waitpid(WNOHANG)`, POSIX signal status, per-child stdout/stderr capture, and `Storable` serialization across fork boundaries.
- Reproducibility integration: `SOURCE_DATE_EPOCH` affects age calculations for annotation and synthetic lines.
- Later-script integration: this chunk prepares data consumed by `process_file`, `write_summary_pages`, source HTML writers, table writers, CLI parsing, and final report generation implemented after line 7224.

## Control Flow Notes

- Current trace data drives the initial file worklist. Baseline trace and diff data are optional but change TLA assignment substantially.
- No-baseline reports default to `GNC`/`UNC`; baseline reports classify unchanged, inserted, deleted, gained, lost, included, and excluded coverpoints.
- Line coverage is categorized first and establishes the `LineData` map that branch, MC/DC, and function coverage attach to.
- Source annotation is optional. Without it, owner/date bins are absent, but core line/branch/function totals still work.
- Select filtering happens after source load and before final TLA counting. Dropped lines are removed from `SummaryInfo` totals.
- Directory and top-level summaries are only scheduled after their dependencies complete.
- Parallel jobs are used only when `lcovutil::maxParallelism > 1` and there is enough work to justify fork overhead. Memory limits can force waits before scheduling more children.

## Risks and Edge Cases

- Array-backed objects are fragile: adding or reordering constants can corrupt serialized data and object interpretation.
- `LineData::curr_count()` appears to add to an undefined slot in the first-assignment branch (`$linecov->[LINE_CURRENT] += $inc`), relying on Perl's numeric undef coercion and warning behavior.
- Several comparisons mix numeric and string semantics. Deleted-line keys like `<<<123` require custom sort/compare handling and are easy to mishandle in future code.
- Diff parser support is tailored to unified diffs and custom `=== unchanged`/`Git Root` records. Nonstandard hunk headers, binary diffs, renames without expected headers, paths with unusual escaping, or filenames equal to `/dev/null` require careful testing.
- `_findChunk()` is a bespoke binary search over overlapping insert/delete/equal ranges. Boundary lines around hunks and insert/delete anchors are high-risk.
- `DiffMap::check_path_consistency()` can mutate mappings under `elide_path_mismatch`; false positives could associate coverage with the wrong same-basename file.
- Branch and MC/DC categorization assumes stable block/expression ordering between baseline and current for matching structures. Compiler or instrumentation changes can turn logical matches into apparent deletions/insertions.
- Function categorization by leader line and alias maps can be misleading when functions move, split, merge, or have unstable end-line metadata.
- Annotation callbacks must return consistent all-commit or all-no-commit data per file; mixed results are fatal.
- Future annotation timestamps relative to `SOURCE_DATE_EPOCH` or current time trigger inconsistent-data handling and collapse age to zero.
- Missing or short source files can be synthesized, which keeps report generation alive but can hide real path/configuration problems unless source/range errors are treated strictly.
- Parallel child serialization depends on `Storable` successfully dumping reduced objects. Large `SourceFile` details, circular references, callback state, or unexpected object contents can create memory pressure or serialization failures.
- Child stdout/stderr are slurped fully into memory during merge. Very verbose child output can increase parent memory use.
- `merge_child()` reschedules missing dump files and SIGKILL failures, but other child failures report parallel errors and may rely on broader `lcovutil` keep-going behavior.
- The option map includes a likely typo key, `genhtml_show_havigation`, which may be intentional compatibility or a configuration spelling bug.

## Test Signals

- Differential line coverage tests should cover no-baseline, unchanged hit/miss, gained/lost coverage, inserted hit/miss, deleted hit/miss, excluded current coverpoints, and files newly added to coverage with `treatNewFileAsBaseline`/age-base behavior.
- Branch and MC/DC tests should cover matching blocks/groups, current-only blocks, baseline-only blocks, excluded current elements, missing line coverage for branch/MC/DC lines, and unstable ordering.
- Function tests should cover aliases, merged-vs-unmerged alias reporting, known/unknown end lines, body changes with unchanged leader lines, deleted functions, inserted functions, and functions present without executable line data.
- Diff tests should exercise path stripping, `Git Root`, `=== unchanged`, `/dev/null` new/deleted files, hunk boundary lookups, deleted-line leaders, path mismatch elision, case-insensitive mode, symlink aliases, and empty diffs.
- Source loading tests should cover real readable sources, missing files with and without synthesis, files shorter than coverage ranges, CRLF stripping, version script mismatches, and baseline reconstruction from diff data.
- Annotation tests should cover valid owner/date/commit data, no-commit files, mixed commit/no-commit error handling, future timestamps, `SOURCE_DATE_EPOCH`, missing owner fields, callback exceptions, and nonzero callback exit statuses.
- Select callback tests should verify selected-code filtering, non-code contiguous expansion, context-line inclusion, and summary count removal for filtered-out lines.
- Owner/date table tests should validate age-bin boundaries, custom label mismatches, owner truncation, all-vs-missed filtering, and branch/MC/DC owner navigation.
- Scheduler tests should cover serial mode, parallel mode, dependency ordering, hierarchical and flat views, fork failure rescheduling, SIGKILL/OOM rescheduling, missing/corrupt dump files, child diagnostics replay, max-memory throttling, and empty-directory cleanup.
- Configuration tests should cover lcovrc and CLI bindings introduced in this chunk, including source view, frames, gzip, precision, coverage thresholds by type, dark mode, hierarchy/flat mode, annotation/select/simplify callbacks, date bins/labels, owner table controls, and source synthesis.

## Cross-Chunk Notes

- The prototypes at the top refer to many functions implemented after this chunk, including the main HTML writing functions and `process_file`.
- The chunk starts at executable initialization and ends while `%genhtml_options` is still being populated; actual option parsing, validation, trace loading, and final report-generation entry flow continue after line 7224.
- Many referenced LCOV data classes (`TraceFile`, `CountData`, branch/MC/DC/function structures, callback wrappers) are external to this script or defined outside this line range.
