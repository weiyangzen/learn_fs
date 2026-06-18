# sources/test-tools/lcov/lib/lcovutil.pm lines 1-8021

## Scope And Purpose

This chunk is the first and larger part of LCOV's shared Perl utility module. It defines package `lcovutil`, exports most shared command-line/configuration/error/filter helpers, and then defines the object model used to represent and manipulate LCOV trace data in memory. The covered range runs from module initialization through the beginning of `TraceFile::_filterFile`; it stops mid-filtering at line 8021, so the rest of per-line filtering, trace-file parsing, and trace-file writing belong to `subset-b-009276`.

At a high level, this code is the common runtime substrate for LCOV tools such as `lcov`, `geninfo`, and `genhtml`. It handles option and RC-file normalization, user-visible diagnostics, temporary files, optional callbacks, parallel child state merging, source-file lookup, source exclusion marker parsing, coverage filter selection, version/checksum validation, and the core in-memory representations for line, function, branch, and MC/DC coverage.

## Public Surface And Global Configuration

The module exports a large set of globals and helpers through `@EXPORT_OK`. Important exported values include tool metadata (`$tool_name`, `$tool_dir`, `$lcov_version`, `$lcov_url`), verbosity/debug state, temp directory tracking, RC parsing helpers, coverage-type booleans, filter identifiers and marker strings, file include/exclude/substitution pattern lists, error IDs, parallelism/memory knobs, callback configuration hooks, source/version/checksum controls, and color/palette maps used by report generation.

Many runtime switches are module-level global state rather than constructor-injected dependencies. Examples include `$br_coverage`, `$func_coverage`, `$mcdc_coverage`, `$case_insensitive`, `$stop_on_error`, `$treat_warning_as_error`, `$warn_once_per_file`, `$verify_checksum`, `$compute_file_version`, `$derive_function_end_line`, `$filter_blank_aggressive`, `$source_filter_lookahead`, and all filter histogram entries in `@cov_filter`. This makes initialization order important: callers are expected to run `define_errors`, `init_filters`, `parseOptions`, and related setup before loading or mutating trace data.

## Diagnostics, Errors, And Message State

`define_errors` assigns numeric IDs to all LCOV error names in `@lcovErrs`, populating `%lcovErrors`, `%ERROR_ID`, `%ERROR_NAME`, `@ignore`, `@message_count`, and `@expected_message_count`. `parse_ignore_errors` and `parse_expected_message_counts` consume comma-separated command-line/RC values and update suppression or expected-count state.

`ignorable_error` and `ignorable_warning` are the central reporting paths. They increment per-error counts, enforce `max_message_count`, record summary counters in `%message_types`, honor `--ignore-errors`, `--keep-going`/`stop_on_error`, and optionally convert warnings into errors. Fatal paths use `die_handler`; nonfatal paths use `warn_handler`. `_msg_handler` normalizes warning/error prefixes, optionally strips Perl source locations, can append stack traces when `LCOV_SHOW_LOCATION` requests developer detail, and writes to a message log under `flock` if configured.

`warn_once`, `store_deferred_message`, `merge_deferred_warnings`, and `explain_once` reduce duplicate diagnostics, especially in parallel mode. `summarize_messages` validates expected-count constraints and emits a compact summary of error, warning, and ignored message totals from the parent process.

Parallel child diagnostics are persisted through `initial_state`, `compute_update`, and `update_state`. A child records deltas for message counts, version/resolve caches, search-path use counts, pattern hit counts, callback save data, profile data, warning-once state, and explain-once state. The parent merges those deltas after child completion.

## Option And RC File Flow

`%rc_common`, `%geninfo_rc_opts`, and `%argCommon` define the shared configuration vocabulary. The code maps RC keys to scalar or array references, including filters, excludes/includes, source/build directories, callback scripts, checksum/version behavior, branch/function/MC/DC coverage toggles, message handling, parallelism, memory, color/filter behavior, and geninfo-specific knobs.

`read_config` reads `key = value` RC files, supports nested `config_file` inclusion with loop detection through `%included_config_files` and `@include_stack`, strips comments/whitespace, expands `$ENV{...}` at the start of values, rejects malformed lines, and skips unsupported keys for the current tool. Deprecated RC keys are collected as deferred diagnostics by `warnDeprecated`.

`apply_rc_params` does early pass-through parsing for `--config-file`, `--rc`, quiet/verbose/debug flags, loads user or default RC files, applies `--rc key=value` overrides, and updates language extension sets. `parseOptions` then combines shared and tool-specific `Getopt::Long` specs, handles help/version/message-log setup, merges RC-provided lists only when corresponding command-line lists are empty, creates source search paths, configures callbacks, checks callback-level/type values, initializes profiles, munges patterns, initializes parallel settings, parses expected message counts and filters, validates C++ demangling, and finally emits deferred RC diagnostics.

The option flow deliberately defers many errors until after ignore-error settings have been parsed. That is a useful behavior but also creates ordering risks: code that reports errors before `parse_ignore_errors` runs may be unavoidably fatal.

## Pattern, Filter, And Source Selection Helpers

`transform_pattern` converts shell-style file patterns into Perl regexes, respecting case-insensitive mode. `munge_file_patterns` converts include/exclude file patterns, compiles omit-line and exclude-function regexes, validates substitution expressions, validates exclusion marker regexes, and snapshots suppress-function patterns for later excessive-count suppression. `warn_file_patterns` reports unused include/exclude/substitute/omit/erase patterns and also invokes callback `finalize` methods late in a run.

Coverage filters are keyed by names such as `branch`, `brace`, `blank`, `directive`, `range`, `line`, `initializer`, `function`, `missing`, `region`, `branch_region`, `exception`, `orphan`, `mcdc`, and `trivial`. `init_filters` assigns their numeric IDs. `parse_cov_filters` enables requested filters and applies derived behavior: `line` enables brace and blank filtering; `branch` enables exception and orphan branch filtering; omit-line patterns create a synthetic `omit_lines` filter. `summarize_cov_filters` reports suppression histograms.

`skipCurrentFile` applies missing-file filtering, user exclude patterns, and include allowlists. File substitution is handled by `subst_file_name`; directory stripping by `strip_directories`; external-file detection by `is_external`.

## Callbacks, External Processes, And JSON/File IO

`configure_callback` supports two callback forms. A `.pm` callback module is loaded from its directory, instantiated with `Class->new`, and optionally registered for `save`/`restore`, `start`, and `finalize` lifecycle methods. Non-module callbacks are wrapped in `ScriptCaller`, which executes command-line scripts for version extraction, path resolution, context collection, annotation, criteria checking, name simplification, and history lookup.

`PipeHelper` owns a child pipe and normalizes close/error handling for callback scripts. `ScriptCaller` offers `call`, `pipe`, `context`, `extract_version`, `resolve`, `compare_version`, `annotate`, `check_criteria`, `select`, `simplify`, and `history`. These callbacks are integration points for source-control metadata, path resolution, report criteria, owner/date annotations, and custom coverage decisions.

`JsonSupport` dynamically selects a JSON module (`JSON::XS`, `Cpanel::JSON::XS`, `JSON::PP`, or `JSON`) unless overridden by RC. It provides `encode`, `decode`, and `load`. `InOutFile` abstracts input/output handles, stdin/stdout, gzip compression/decompression, and optional C++ demangling pipelines. `system_no_output` runs external commands through `Capture::Tiny` and controls stdout/stderr suppression or forwarding.

## Parallelism, Profiling, And Temporary State

`count_cores`, `read_proc_vmsize`, `read_system_memory`, `init_parallel_params`, and `current_process_size` implement parallelism and memory-throttle setup. The code can count Linux CPUs through `/proc/cpuinfo`, read total memory from `/proc/meminfo`, use `Memory::Process` if available, fall back to `/proc/self/stat`, and validate gzip availability when parallel intermediates are expected.

`create_temp_dir`, `append_tempdir`, and `temp_cleanup` manage temporary directories under `$tmp_dir`, with `$preserve_intermediates` disabling cleanup for debugging. `abort_handler` cleans temp dirs before exiting.

Profiling state lives in `%profileData`. `save_cmd_line` records command, tool binary path, and build directory. `merge_child_profile` merges nested profile hashes from parallel children, with special additive keys for known timing buckets. `save_profile` writes JSON profile data and, when requested for HTML output, creates HTML object wrappers for command-line and profile data.

## Version, Checksum, Dates, And Reporting Utilities

`extractFileVersion` calls a configured version callback once per source path, caches results in `%versionCache`, profiles callback time, and optionally checks file existence before invoking callbacks. `checkVersionMatch` first performs string equality, then delegates to `compare_version` if available, otherwise emits version mismatch diagnostics. `_merge_checksums` in `TraceInfo` merges per-line checksum data and reports mismatches.

`parse_w3cdtf` loads `DateTime::Format::W3CDTF` if available, otherwise parses common W3CDTF date forms into `DateTime` objects. `rate`, `get_overall_line`, `check_precision`, and `use_vanilla_color` support report summaries and coloring. `HTML_fileData` and `ValidateHTML` scan generated HTML files to find duplicate anchors, broken local links, invalid anchors, and unreferenced HTML pages.

## Coverage Criteria And Message Context

`CoverageCriteria` holds callback-driven pass/fail criteria. `executeCallback` calls a configured criteria callback with top/directory/file coverage data and records nonzero statuses or messages. `check_failUnder` converts built-in fail-under thresholds into top-level criteria failures. `summarize` prints all failed or message-bearing criteria and mirrors failures to stderr.

`MessageContext` is a small stack object. Constructing it pushes a text fragment; destruction asserts stack balance and pops it. Diagnostics call `MessageContext::context()` to append nested context such as "while loading" or "while filtering".

## Core Coverage Data Model

`MapData` is a thin hash wrapper used for checksum maps and per-testcase maps. `CountData` stores line-number-to-count data and cached found/hit totals. `append` validates numeric counts, reports non-integer, negative, or excessive counts, accumulates repeated keys, and updates found/hit counters. `union`, `intersect`, and `difference` implement tracefile merge operations for line coverage.

Branch coverage is represented by several layered types:

- `BranchElement` stores branch ID, taken count or `-`, optional expression, branch type (`VANILLA`, `EXCEPT`, `FALLTHROUGH`), exclusion state, and optional differential metadata.
- `BranchBlock` is an ordered list of branch elements with a signature string based on branch types.
- `BranchLocation` stores all branch blocks for one source line, indexed both by block order and by signature. It merges compatible blocks, clones new blocks, removes blocks, and computes found/hit totals.
- `BranchMap` tracks line-to-branch-location data and cached found/hit counts.
- `BranchData` extends `BranchMap` with block insertion, count recalculation, count consistency checks, and union/intersect/difference semantics.

MC/DC coverage has a similar model:

- `MCDC_Block` stores one line's MC/DC groups keyed by group size and validates expression compatibility.
- `MCDC_Expression` stores true/false sense counts and exclusion flags for one condition expression.
- `MCDC_Data` extends `BranchMap` with MC/DC append/creation, close-block count accumulation, recalculation, and union/intersect/difference operations.

Function coverage is represented by `FunctionEntry` and `FunctionMap`. `FunctionEntry` tracks a representative name, aliases, start/end lines, total hit count, and alias hit counts. It validates and accumulates alias counts, chooses a shorter non-lambda representative name, supports differential counts, finds line/branch/MC/DC coverpoints in its range, and removes aliases. `FunctionMap` indexes entries by start line and by alias name, detects duplicate names at different lines, reconciles mismatched end lines, counts functions/hits either per alias or merged under the function-alias filter, and implements union/intersect/difference operations.

`TraceInfo` is the per-source-file coverage container. It stores version, source location in the `.info` file, filename, checksums, line data, branch data, function data, and MC/DC data. Each coverage kind has both merged summary data and per-testcase maps. `TraceInfo::merge` selects the correct union/intersect/difference operations, checks version compatibility, merges testcase and summary data, and merges checksums.

## Source Loading And Exclusion Parsing

`ReadCurrentSource` resolves source paths through direct existence checks, source directories, substitutions, and optional resolve callbacks. `_load` reads the current source file and records its resolved path. `parseLines` scans all source lines and builds a per-line exclusion bitfield from LCOV markers and filters:

- line regions: `LCOV_EXCL_START`/`LCOV_EXCL_STOP`, `LCOV_EXCL_LINE`
- unreachable regions: `LCOV_UNREACHABLE_START`/`LCOV_UNREACHABLE_STOP`, `LCOV_UNREACHABLE_LINE`
- branch-only regions: `LCOV_EXCL_BR_START`/`LCOV_EXCL_BR_STOP`, `LCOV_EXCL_BR_LINE`
- exception-branch regions: `LCOV_EXCL_EXCEPTION_BR_START`/`LCOV_EXCL_EXCEPTION_BR_STOP`, `LCOV_EXCL_EXCEPTION_BR_LINE`
- C preprocessor directives when directive filtering is enabled
- user `omit-lines` regex matches

The parser reports overlapping, unmatched, and dangling exclusion markers. `isExcluded`, `excludeReason`, and `isOutOfRange` later use the exclusion bitfields to decide whether to suppress coverpoints, warn about out-of-range coverage data, or defer range diagnostics. Source heuristics such as `containsConditional`, `containsTrivialFunction`, `suppressCloseBrace`, `is_initializerList`, `isBlank`, and `isCharacter` support branch/brace/blank/trivial filtering. These heuristics intentionally err toward keeping coverage when uncertain.

## TraceFile Control Flow Covered In This Chunk

`TraceFile` is the top-level multi-file trace container. `load` constructs a new trace, creates a message context, reads an `.info` file through `_read_info` (defined later in the file, outside this chunk's visible implementation body), then applies filters. `new`, `serialize`, and `deserialize` create or persist the object through `Storable`.

Basic queries and mutation include `files`, `directories`, `file_exists`, `contains`, `data`, `insert`, `remove`, `comments`, and `add_comments`. `data` creates a `TraceInfo` lazily and supports case-insensitive keys and basename fallback for diff path matching. `count_totals`, `empty`, `print_summary`, `check_fail_under_criteria`, and `checkCoverageCriteria` aggregate line, branch, function, and MC/DC totals and run built-in or callback criteria.

`merge_tracefile` performs whole-trace union/intersect/difference by delegating per-file operations to `TraceInfo::merge`, removing missing files during intersection, adding new files during union, and preserving comments.

The filtering helpers visible in this chunk include:

- `_eraseFunction`, which removes line, branch, MC/DC, checksum, and function data for a function range.
- `_eraseFunctions`, which applies trivial-function and exclude-function filters, handles missing end-line cases, and reports hit functions marked unreachable.
- `_deriveFunctionEndLines`, which derives missing function end lines from sorted line coverage and neighboring function starts, propagates derived end lines to testcase function maps, records profile timing, and emits consistency diagnostics when derivation is impossible.
- `_fixFunction`, which adjusts summary and per-testcase function counts after ignored consistency errors when `fix_inconsistency` is enabled.
- `_checkConsistency`, which validates function hit state against contained line hit state, generates orphan MC/DC line data when needed, and checks branch/line consistency.
- `_filterFile`, whose beginning derives end lines, checks consistency, initializes active filter histograms, loads source for filtering, verifies source version compatibility, erases excluded/trivial functions, and then enters per-testcase filtering. This chunk stops immediately after fetching the first testcase's `CountData`.

## Branch Exception Filtering

`FilterBranchExceptions` encapsulates exception, orphan, region, and branch-region filtering. It removes exception branches and related fallthrough branches from both summary and per-testcase branch maps, updates filter histograms only on master data, removes empty branch blocks, and optionally removes orphan one-branch blocks. Its `filter` method uses `ReadCurrentSource::isExcluded` to decide whether a line is in a branch/exception/unreachable region and chooses the applicable histogram.

## State And Persistence Behavior

Most persistent runtime state is in global variables or mutable array/hash objects:

- Trace data persists in `TraceFile` -> `TraceInfo` -> `CountData`/`FunctionMap`/`BranchData`/`MCDC_Data`.
- Per-testcase data persists alongside summary data, and filters must mutate both to stay coherent.
- Pattern usage counts are stored in the last element of pattern arrays and are merged back from children.
- Message counts, suppression state, version/resolve caches, callback state, and profile state are global and explicitly merged in parallel mode.
- Temporary directories are tracked globally in `@temp_dirs`.
- Source-resolution search-path use counts persist in `SearchPath` instances and can be reported as unused options.
- Serialized tracefiles use Perl `Storable`, so object layout changes can affect compatibility with intermediates.

The code also writes optional persistent artifacts: profile JSON, profile HTML wrappers, command-line HTML wrappers, and message logs. Gzip-backed trace/intermediate IO goes through external `gzip`.

## Dependencies And Integration Points

This chunk depends on core Perl modules and several optional/external integrations: `File::Path`, `File::Basename`, `File::Temp`, `File::Spec`, `Scalar::Util`, `Cwd`, `Storable`, `Capture::Tiny`, `Module::Load::Conditional`, `Digest::MD5`, `FindBin`, `Getopt::Long`, `DateTime`, `Config`, `POSIX`, `Fcntl`, `Devel::StackTrace`, optional `Memory::Process`, optional `DateTime::Format::W3CDTF`, optional JSON modules, `gzip`, `c++filt` or a configured demangler, `/proc` on Linux, and user-supplied callback scripts/modules.

Internal integration points include the public LCOV executables that import this module, the later `TraceFile::_read_info` and write-info code in the same file, report-generation code that consumes palettes and TLA maps, callback modules implementing the documented callback methods, and merge/reconciliation code that expects union/intersect/difference behavior to preserve found/hit totals.

## Risks And Edge Cases

The main risk is global mutable state. Initialization order, child-process state merging, and repeated use in long-lived processes can affect diagnostics, filters, callbacks, pattern counts, caches, and profile data. Parallel mode adds extra hazards around callback save/restore correctness, fork failures, parent death, memory throttling, and duplicate warning suppression.

Source filtering is heuristic-heavy. Conditional detection, close-brace suppression, trivial-function detection, initializer-list filtering, and out-of-range handling can all produce false positives or false negatives for unusual C/C++ syntax, generated code, lambdas, macros, Perl branch data, or stale source/coverage version combinations.

Merge operations must preserve cached found/hit totals while mutating nested structures. Many methods clone blocks or remove elements while iterating; stale totals would corrupt summaries, fail-under criteria, and HTML report counts. The code includes `_checkCounts` and recalculation paths to catch some of this.

Callback execution and shell command construction are powerful integration surfaces. Script callbacks are invoked through shell-style command strings in several places, so paths/arguments containing spaces or shell metacharacters need careful handling by callers. Module callbacks can start child processes or maintain state; the code warns about unknown child processes and requires callback `save`/`restore` symmetry for parallel support.

Data validation intentionally turns malformed, negative, excessive, mismatched, or inconsistent coverage into LCOV diagnostics, and many diagnostics can be ignored. When ignored, the module often continues with repaired or synthetic data, such as clamping bad counts to zero, creating fake line data for branch/MC/DC consistency, or adjusting function counts.

## Test Signals

Useful tests for this chunk should exercise both normal and suppressed-error paths:

- RC and command-line parsing with config-file inclusion, deprecated keys, environment expansion, list/scalar options, `--rc` overrides, message logs, and quiet/verbose/debug interactions.
- Error handling with fatal errors, ignored errors, warning-as-error, max-message suppression, expected message-count constraints, deferred warnings, and child-state merging.
- Pattern handling for include/exclude/substitute/omit/erase patterns, invalid regexes, case-insensitive mode, unused-pattern warnings, and shell-wildcard conversion.
- Callback integration with script and module callbacks, including save/restore/start/finalize in parallel mode and callback failure diagnostics.
- JSON module selection, gzip input/output, demangle command validation, temp cleanup, profile output, and `/proc`/`Memory::Process` memory throttling fallback.
- Count, function, branch, and MC/DC data-model operations for append, remove, union, intersect, difference, duplicate/mismatched function definitions, branch signatures, excluded branches, differential metadata, and found/hit total recalculation.
- Source parsing with every LCOV exclusion marker, overlapping/unmatched regions, directive filtering, omit-line filtering, out-of-range lines, unreachable hit coverpoints, trivial functions, initializer lists, blank/brace suppression, and source version mismatches.
- TraceFile aggregation, merge_tracefile union/intersect/difference, fail-under criteria, callback criteria summaries, function end-line derivation, consistency checks, and the visible first phase of `_filterFile`.

The strongest regression signals are summary found/hit totals before and after filtering/merging, exact diagnostic types and counts, filter histogram counts, and consistency between summary data and per-testcase data after mutations.
