# sources/test-tools/lcov/lib/lcovutil.pm lines 8022-10187

## Scope And Purpose

This chunk covers the tail of `TraceFile::_filterFile`, the parallel filter orchestration used by `TraceFile::applyFilters`, the `.info` reader and writer, and the `AggregateTraces` package that finds, loads, and merges tracefiles. It begins inside per-testcase source filtering and continues through module initialization.

The covered code is the late-stage normalization path for LCOV trace data. After earlier code has parsed options, built `TraceFile`/`TraceInfo` objects, loaded source files, derived function end lines, and prepared filter histograms, this chunk removes filtered function, branch, MC/DC, and line coverpoints; keeps summary and per-testcase data in sync; serializes child-process filter results; parses LCOV `.info` records into the in-memory model; writes the canonical `.info` format back out; and merges multiple input tracefiles, optionally in parallel.

## Main Control Flow

### Completing `TraceFile::_filterFile`

The chunk starts after `_filterFile` has fetched per-testcase maps from a `TraceInfo`:

- `testcount` is the current testcase's `CountData` for line records.
- `testfnccount`/`functionMap` hold function coverage for the testcase.
- `testbrcount` holds branch data, when branch coverage is enabled.
- `mcdc_count` holds testcase MC/DC data, when MC/DC coverage is enabled.
- Summary maps such as `$sumcount`, `$funcdata`, `$sumbrcount`, and `$mcdc` are shared across testcases and must be updated whenever a coverpoint is removed.

Function filtering first checks function start lines against source ranges and exclusion markers. If a function is out of range or excluded by a region/omit-line marker, the function key is removed from every testcase function map and from the summary `FunctionMap`. Unreachable regions are special: a hit function in an unreachable region reports `ERROR_UNREACHABLE` earlier in the filter path and can be retained when `$retainUnreachableCoverpointIfHit` is true.

Branch and MC/DC filtering then walks the union of testcase MC/DC lines and branch lines. It chooses one removal histogram based on out-of-range status, whole-line exclusion, branch-region exclusion, directive exclusion, omit-line exclusion, or the C branch-no-condition filter. When removal applies, the code removes both BRDA and MCDC data at that line from every testcase map and from the corresponding summary map, increments location and coverpoint counters, reports verbose filter messages, and recalculates branch counts. If the line is not otherwise removed, `FilterBranchExceptions->filter($line)` may mark/remove exception branches and orphan branch blocks.

The `mcdc_single` filter removes single-expression MC/DC blocks when there is a matching two-way branch expression on the same line. This treats such MC/DC entries as redundant with branch coverage and removes the testcase and summary MC/DC entry while incrementing the MC/DC-single filter histogram.

If `$excludeCoverpointCallback` is configured, `_filterFile` calls its `exclude($kind, $srcReader, $testCount, $sumCount)` method for `branch` and `mcdc`. Callback exceptions are reported through `ERROR_CALLBACK` but do not abort if that error is ignored.

Line filtering runs only when one of the relevant line-oriented filters is active. It skips lines that still have summary branch or testcase MC/DC data, because those lines are handled by branch/MC/DC filtering. Remaining DA lines can be removed for initializer-list ranges, out-of-range line numbers, exclusion/omit/directive markers, close-brace suppression, and blank-line suppression. Removed lines are deleted from every testcase line map, from the summary count map, and from checksum data. The function-alias filter histogram is updated at the end from the final summary function map counts.

### Parallel filtering

`TraceFile::applyFilters` computes a mask of work to perform: `DID_FILTER`, and optionally `DID_DERIVE` when function end-line derivation is enabled. It returns early when the tracefile state already includes the requested mask. Otherwise it iterates all files, removes skipped or external files, decides whether end-line derivation is needed, and builds a filter worklist for files that need source-based filters or function/trivial-function filtering.

`_processFilterWorklist` chooses serial or forked execution. Parallel mode is enabled when forced by `LCOV_FORCE_PARALLEL` or when there are more than 50 files, filter parallelism is enabled, and `$maxParallelism > 1`. It optionally honors `lcov_filter_chunk_size` as an absolute value or percentage, otherwise derives a chunk size from file count and parallelism. Work items are either single `[TraceInfo, name, actions]` entries for serial processing or chunk arrays for child processing.

For each child chunk, `_processParallelChunk` resets pattern/filter counters to per-child deltas, captures stdout/stderr with `Capture::Tiny`, calls `_filterFile` for each file in the chunk, records modified files, writes captured logs to temp files, and serializes updates, filter counters, warning state, timing state, and global child deltas through `Storable::store`.

The parent side uses `_mergeParallelChunk` to read child logs, retrieve serialized data, merge child message/profile/cache state with `lcovutil::update_state`, merge pattern and filter histogram counts, call `_updateModifiedFile` for each modified file, and record timing buckets such as `filt_undump`, `filt_merge`, `filt_queue`, and `filt_chunk`. Missing dump files or SIGKILL child exits are treated as retryable fork failures; the chunk is pushed back onto the worklist with retry counts. Other child failures are reported as parallel errors.

`_generate_end_line_message` emits a once-only GCC/gcov compatibility diagnostic when filtering had to deal with unsupported function end-line data. `_updateModifiedFile` writes the modified `TraceInfo` back into the `TraceFile` and calls that diagnostic helper if the shared state indicates unsupported end-line behavior was seen.

### Reading `.info` data

`TraceFile::_read_info($tracefile, $readSourceCallback, $verify_checksum)` parses an LCOV tracefile into the current `TraceFile`. It opens input through `InOutFile->in`, so compressed files and demangling pipelines are handled by that abstraction. It tracks current testcase, current source file, per-testcase maps, summary maps, current branch block, current MC/DC block, function index records, and whether the current file should be skipped by include/exclude/missing-file rules.

The parser recognizes:

- `TN:` testcase records, with non-word characters normalized to underscores unless testcase names are ignored globally.
- `SF:` and `KF:` source filename records, resolved through `ReadCurrentSource::resolve_path`; skipped files are logged once in `%excluded_files`.
- `VER:` source version records.
- `DA:` line coverage records, including optional checksum validation against the source file when checksums are enabled.
- Legacy `FN:` and `FNDA:` function records.
- Newer `FNL:` and `FNA:` function index/alias records.
- `BRDA:` branch records with optional type prefix `e` for exception and `f` for fallthrough, optional `U` unreachable/excluded marker, block id, branch id or expression, and taken count.
- `MCDC:` records with optional `U` marker, group size, true/false sense, count, expression index, and expression text.
- `end_of_record`, which finalizes current line/function/branch/MC/DC data into summaries and runs `TraceInfo::check_data`.

Branch parsing re-derives contiguous block IDs rather than trusting serialized IDs. It keeps one active `BranchBlock`; when the block id or source line changes, it inserts the previous block into the current testcase `BranchData` and starts a new block. Branch IDs can be arbitrary strings to support expression-oriented tools such as Verilog coverage emitters. Line number zero or negative branch records are reported as format errors but are retained if the error is ignored.

MC/DC parsing maintains one current `MCDC_Block` per line. When the line changes or the record ends, the current block is closed into summary MC/DC data and cloned into the current testcase MC/DC map. The parser preserves unreachable/excluded flags unless `$ignore_unreachable_flag` is set.

At `end_of_record`, line counts are unioned into summary counts, functions into summary function data when function coverage is enabled, branch blocks are inserted and count totals recalculated when branch coverage is enabled, MC/DC blocks are closed, and the file's internal consistency is checked. After the full file is read, empty files and empty testcase maps are removed. An empty tracefile after filtering/skipping reports `ERROR_EMPTY`.

### Writing `.info` data

`TraceFile::write_info_file($filename, $do_checksum)` opens an output handle through `InOutFile->out` and delegates to `write_info`. `write_info($handle, $verify_checksum)` emits the canonical `.info` format in stable sorted order.

For each source file and testcase, it writes `TN`, `SF`, optional `VER`, function records, branch records, MC/DC records, line records, summary count records, and `end_of_record`. The writer intentionally mirrors `_read_info`; comments in both functions warn that format changes must be kept synchronized and documented in `man/geninfo.1`.

Function output uses the newer indexed alias format. It sorts functions by start line and key, writes `FNL:<index>,<start>[,<end>]`, then writes one `FNA:<index>,<hit>,<alias>` for each alias. Function-found counts count merged functions, while function-hit counts count a function once if any alias is hit.

Branch output iterates branch lines numerically, then branch blocks in sorted/display order. It writes `BRDA:<line>,<type><U?><block>,<expr-or-id>,<taken>`. Excluded branch elements are serialized with `U` and are not included in `BRF`/`BRH` totals. MC/DC output emits two records per expression, one for true sense and one for false sense, with `U` when that sense is excluded; `MCF` counts both senses for each expression and `MCH` counts nonzero sense counts.

Line output writes DA records with optional checksums. If checksum verification is requested, existing checksum data is reused first; otherwise a `ReadCurrentSource` instance reads the current source and computes `Digest::MD5::md5_base64` for the line. `LF` and `LH` are recomputed from the testcase line map.

### Aggregate trace loading and merging

The `AggregateTraces` package is a shared utility for lcov add-trace behavior and genhtml multi-file ingestion.

`find_from_glob(@patterns)` expands input tracefile arguments. Direct files are accepted as-is. Patterns are glob-expanded, and directories are searched with `find '$dir' -name '$info_file_pattern' -type f`. Empty matches, unreadable files, and utility failures are reported through `ignorable_error`. The function returns the list of readable tracefiles to merge.

`_process_segment($total_trace, $readSourceFile, $segment)` processes a list of tracefiles sequentially inside one process. It skips missing or empty files, loads each file with `TraceFile->load($tracefile, $readSourceFile, $verify_checksum, 1)`, records parse and append profile timings, and either merges it into `$total_trace` with `TraceInfo::UNION` or, when `$function_mapping` is enabled, builds a map from unique function location to function name and tracefiles that hit it. In normal merge mode, files that improve coverage are returned as "interesting" inputs for pruning/reporting.

`merge($readSourceFile?, @tracefiles)` is the public aggregate entry point. It accepts an optional `ReadCurrentSource` or `ReadBaselineSource`; without an object it constructs `ReadCurrentSource` for backward compatibility. It temporarily disables source-based coverage filters while reading input tracefiles, because parsing source for each input is expensive and filtering is applied once after merging. It initializes parallel settings and optionally reduces `$maxParallelism` based on `$maxMemory`, current process size, and largest input file size.

If parallelism is available and there are multiple inputs or `LCOV_FORCE_PARALLEL` is set, `merge` partitions the sorted or original file list into segments, forks one child per segment up to the segment count, captures child output, serializes each child result through `Storable`, and merges child results in the parent. Child failures from missing dump files or SIGKILL are retried by pushing the segment back to the queue; other failures are reported as child/parallel errors. In sequential mode it simply calls `_process_segment` once.

After all segments are merged, `merge` removes the configured temp directory when appropriate, re-enables the previously disabled coverage filters, calls `$total_trace->applyFilters($readSourceFile)`, and returns `($total_trace, \@effective)`.

## Important APIs And Types

- `TraceFile::_filterFile($traceInfo, $source_file, $actions, $srcReader, $state)`: mutates one file's coverage data according to active filters and returns the updated `TraceInfo` plus a modified flag.
- `TraceFile::_processFilterWorklist($srcReader, $fileList)`: serial/parallel driver for file-level filtering.
- `TraceFile::_processParallelChunk(...)`: child-process filter worker; emits logs and serialized updates.
- `TraceFile::_mergeParallelChunk(...)`: parent-process merge path for child filter results.
- `TraceFile::applyFilters($srcReader?)`: public idempotent entry point for derivation and source-based filtering.
- `TraceFile::is_language($lang_expr, $filename)`: extension-based language predicate, where `$lang_expr` can be pipe-separated.
- `TraceFile::_read_info($tracefile, $readSourceCallback, $verify_checksum)`: parser for LCOV `.info` files.
- `TraceFile::write_info_file($filename, $do_checksum)` and `TraceFile::write_info($handle, $verify_checksum)`: `.info` output writers.
- `AggregateTraces::find_from_glob(@patterns)`: expands user-supplied tracefile inputs and directories.
- `AggregateTraces::_process_segment($total_trace, $readSourceFile, $segment)`: sequential parser/merger for one segment.
- `AggregateTraces::merge($readSourceFile?, @tracefiles)`: high-level multi-input merge with optional parallelism and post-merge filtering.

The main data types used here are the structures defined earlier in the same module: `TraceFile`, `TraceInfo`, `CountData`, `FunctionMap`, `FunctionEntry`, `BranchData`, `BranchBlock`, `BranchElement`, `MCDC_Data`, `MCDC_Block`, `MapData`, `ReadCurrentSource`, `ReadBaselineSource`, `FilterBranchExceptions`, `InOutFile`, and `MessageContext`.

## State And Persistence Behavior

Filtering mutates both per-testcase and summary data. Removing a function, branch, MC/DC block, or line from only one layer would leave output summaries inconsistent, so most removal paths explicitly iterate all testcase maps and then remove from the summary map. Branch removals call `updateCounts` to refresh cached found/hit totals.

Filter and pattern histograms are mutable global arrays in `@lcovutil::cov_filter`, `@exclude_function_patterns`, and `@omit_line_patterns`. Parallel filter children zero those counters, record only local deltas, serialize the deltas, and the parent adds them back. Warning counts, callback state, source-resolution caches, version caches, and profile data are also process-local in children and are reconciled through `lcovutil::compute_update`/`update_state`.

Temporary persistence uses files in a temp directory:

- Filter children write `filter_$$.log`, `filter_$$.err`, and `dumper_$$`.
- Aggregate children write `lcov_$$.log`, `lcov_$$.err`, and `dumper_$$`.
- Serialized child payloads use Perl `Storable`, so object layout and Perl-version compatibility matter for parallel intermediates.

Tracefile persistence is the LCOV `.info` text format. This chunk is both reader and writer for that format, so any new record type or field must be implemented symmetrically. Checksums are persisted in DA records when configured. Source versions are persisted in `VER:` records. Excluded/unreachable branch and MC/DC senses are persisted through `U` markers.

`TraceFile` state bits `DID_FILTER` and `DID_DERIVE` make `applyFilters` idempotent. `AggregateTraces::merge` deliberately disables filters during input parsing and applies them after all input is merged, changing when source-related diagnostics and filter histogram counts are produced.

## Dependencies And Integration Points

This chunk depends on global configuration and helpers from package `lcovutil`, including coverage enable flags, filter definitions, include/exclude patterns, warning/error reporters, profile data, memory/parallelism settings, temp-directory settings, checksum/version settings, and callback objects.

Important internal integration points include:

- `ReadCurrentSource` and `ReadBaselineSource` for source loading, exclusion markers, checksum lines, language-specific heuristics, and diff-aware baseline reconstruction.
- `FilterBranchExceptions` for exception/orphan branch removal from summary and testcase branch maps.
- `TraceInfo::get_info`, `TraceInfo::check_data`, and coverage data-model operations such as `union`, `remove`, `insertBlock`, `updateCounts`, `append_mcdc`, and `close_mcdcBlock`.
- `InOutFile` for stdin/stdout, gzip input/output, demangle pipelines, and safe file-handle ownership.
- `Capture::Tiny`, `fork`, `wait`, `POSIX::SIGKILL`, `File::Temp`, `File::Spec`, and `Storable` for parallel execution.
- `Digest::MD5` for DA checksum validation and generation.
- External `find` in `AggregateTraces::find_from_glob` when an input pattern resolves to a directory.
- User callbacks, especially `$excludeCoverpointCallback`, version callbacks used before filtering, and callback save/restore state merged from children.

The major user-facing integration is with tools that load or write `.info` files, especially `lcov` add/remove/extract flows and `genhtml` report generation. `genhtml` calls `AggregateTraces::merge`, then consumes the filtered `TraceFile` data to build summaries and source views.

## Risks And Edge Cases

The highest-risk area is keeping nested coverage maps coherent while filtering. Many operations delete from all testcase maps and the summary map, but MC/DC single-expression filtering assumes `$mcdc_count` and `$testbrcount` are defined. That path is gated by the filter flag, but tests should cover files with MC/DC enabled and no corresponding branch data to guard against undef dereferences.

Parallel filtering and aggregate merging rely on temp dump files named by child PID. Missing dump files and SIGKILL are retried, but serialization failures, child output races, stale temp dirs, or ignored parallel errors can leave partially merged state. The code also mutates global `$maxParallelism` when applying memory throttling, which can affect later work in a long-lived process.

`AggregateTraces::find_from_glob` builds a shell `find` command using single-quoted directory and filename-pattern strings. Paths or patterns containing embedded single quotes are risky. It also splits `find` stdout on whitespace, so discovered filenames containing whitespace can be broken into multiple entries.

The `.info` parser is permissive when errors are ignored. Invalid line numbers, checksum mismatches, duplicate or unknown function indexes, unexpected record formats, and malformed branch/MC/DC records may continue into the in-memory model. This is useful for "keep going" behavior but makes downstream consistency checks and writer validation important.

Parser/writer symmetry is fragile. Branch type markers, `U` exclusion markers, function alias indexes, MC/DC true/false sense records, checksum fields, and summary count records must remain compatible with external LCOV producers and older LCOV consumers. New fields need updates in `_read_info`, `write_info`, and manual documentation together.

Source filtering is source-version sensitive. `_filterFile` skips source-based filtering when the current source version differs from the tracefile's recorded version, but checksum verification and range/exclusion filtering depend on the source reader being opened to the correct current or baseline reconstruction. Misconfigured version callbacks can therefore suppress filtering or produce stale checksum diagnostics.

Global mutable state affects repeatability. Testcase name normalization, ignored testcase names, branch/function/MC/DC enable flags, omit/exclude patterns, `ignore_unreachable_flag`, `exclude_exception_branch`, and filter histograms all alter parse or filter behavior. Parallel child merging must preserve these effects without double-counting diagnostics or filter counters.

## Test Signals

Strong regression tests for this chunk should check exact `.info` round trips and summary totals:

- Filtered functions are removed from every testcase `FunctionMap` and from summary `FunctionMap`, with alias histograms reflecting final merged/alias counts.
- Out-of-range, excluded, directive, omit-line, no-conditional branch, exception branch, orphan branch, and MC/DC-single filters update the right histograms and leave branch/MC/DC found/hit totals consistent.
- Unreachable hit coverpoints produce `ERROR_UNREACHABLE` and are retained or removed according to `$retainUnreachableCoverpointIfHit`.
- Line filtering skips lines that still own branch or MC/DC data, removes DA/checksum records from all relevant maps, and handles initializer-list, close-brace, blank-line, range, directive, region, and omit filters.
- Serial and parallel `applyFilters` produce identical trace data, diagnostics, filter histograms, and profile keys for the same input corpus.
- Parallel filter and aggregate paths retry SIGKILL/missing-dump failures and report non-retryable child errors without silently losing chunks.
- `_read_info` accepts legacy `FN`/`FNDA` and indexed `FNL`/`FNA` functions, branch records with vanilla/exception/fallthrough types and expression IDs, MC/DC true/false records, version records, checksum records, comments, empty lines, and ignored summary records.
- `write_info` output can be parsed back into equivalent `TraceFile` data, including function aliases, function end lines, branch excluded flags, MC/DC excluded senses, and optional line checksums.
- Checksum verification reports missing/mismatched checksums and recomputes checksums on write when source is available.
- `AggregateTraces::merge` yields the same merged `TraceFile` sequentially and in parallel, preserves effective/interesting input lists, handles `function_mapping` mode, disables filters during parse, and applies filters once after merge.
- `find_from_glob` covers direct files, globs, directories containing `.info` files, empty matches, unreadable matches, and filenames with spaces or other shell-sensitive characters.
