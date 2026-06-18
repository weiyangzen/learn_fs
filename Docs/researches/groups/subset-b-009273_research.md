# subset-b-009273 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/geninfo -->
# sources/test-tools/lcov/bin/geninfo

## Purpose

`geninfo` is the LCOV capture engine for GCC/gcov-style coverage artifacts. It scans one or more data/build directories for `.gcda` and `.gcno` files, runs a selected `gcov` tool, parses either classic `.gcov` text output or gcov intermediate text/JSON output, and emits LCOV `.info` trace data. It is also responsible for initial zero-coverage capture from `.gcno` files, include/exclude filtering, source-path normalization, checksum/version/comment metadata, branch/function/MC/DC collection when supported, and parallel processing of large coverage sets.

The script is a command-line tool but relies heavily on the shared `lcovutil` library for option parsing, trace-file data structures, filtering, diagnostics, profile output, and coverage criteria checks.

## Important APIs, types, and functions

- Command options are collected in `%geninfo_opts` and merged with `lcovutil::geninfo_rc_opts` through `lcovutil::parseOptions()`. Important options include `--output-filename`, `--base-directory`, `--gcov-tool`, `--initial`, `--all`, `--compat`, `--no-recursion`, `--external`/`--no-external`, `--large-file`, and inherited filter/checksum/coverage options.
- Compatibility state is represented by `%compat_value` with modes for `libtool`, `hammer`, and `split_crc`. `parse_compat_modes()` validates names and values, applies defaults, and supports delayed or automatic mode detection.
- `IntervalMonitor` reports periodic processing progress and child CPU time.
- `BuildWorkList` owns discovery of `.gcda`/`.gcno` work items. `find_files()` shells out to `find`; `add_worklist_entry()` de-duplicates files; `find_corresponding_gcno_file()` locates matching graph files beside `.gcda` files, under configured build directories, or through resolve callbacks.
- `gen_info()` builds the work list, divides it into chunks, handles serial and forked child processing, merges child `Storable` dumps, and updates profiling counters.
- `_process_one_chunk()` and `_merge_one_child()` are the parallel-processing glue. Children write temporary LCOV/Storable data under the temporary directory and parent processes merge it into `TraceFile` state.
- `process_dafile()` is the classic gcov path for a single data/graph pair. It reads `.gcno`, invokes `gcov`, resolves generated `.gcov` files back to source files, populates `TraceFile` entries, and deletes intermediates unless preservation is requested.
- `read_gcov_file()` parses classic `.gcov` content into line, branch, and function maps. It handles branch blocks, exception/fallthrough annotations, unexecuted block markers, demangling, and duplicate instance lines.
- `process_intermediate()`, `read_intermediate_text()`, `read_intermediate_json()`, `intermediate_text_to_info()`, and `intermediate_json_to_info()` implement the gcov `-i` intermediate-format path.
- `read_gcno()` and helpers (`read_gcno_word()`, `read_gcno_value()`, `read_gcno_string()`, `read_gcno_lines_record()`, `read_gcno_function_record()`) parse binary graph files to find source files, instrumented lines, and function declarations.
- Path helpers such as `solve_relative_path()`, `compute_internal_directories()`, `match_filename()`, `solve_ambiguous_match()`, `adjust_source_filenames()`, and `filter_source_files()` normalize source/build paths and enforce include/exclude/external rules.

## Control flow

At startup the tool installs LCOV warning/die handlers, forces `LC_ALL=C` so gcov output is parseable, parses command-line and rc options, validates the `gcov` executable, detects the gcov version and supported flags, decides whether intermediate format should be used, builds the final gcov command line, and normalizes data directories.

The main capture flow is:

1. Validate directories/globs and compute internal directories used by `--no-external`.
2. Create or select a temporary directory for child data and gcov intermediates.
3. Call `gen_info()` for all input directories.
4. `BuildWorkList` finds `.gcda` files for normal capture, `.gcno` files for `--initial`, or both for `--all`.
5. Work is chunked. Large files and chunk zero are handled serially; other chunks may be processed by forked children subject to `--parallel` and memory limits.
6. Each data item either creates zero-count initial coverage from graph data or executes gcov, parses generated coverage, and returns `TraceFile` data.
7. Parent and child results are merged; source filters and coverage filters are applied.
8. A single output trace is written when `--output-filename` is set. Without a single output file, per-input outputs are emitted as processing occurs.
9. Summaries, warnings, profile data, and coverage criteria status are reported before process exit.

For classic gcov output, `process_dafile()` changes into a temporary directory, invokes gcov with `-o` pointing at the object directory, reads each generated `.gcov` file, matches it against source entries from `.gcno`, and populates line/function/branch maps. For intermediate output, gcov's generated `.gcov`/JSON data is loaded directly and converted to LCOV records without reparsing source-looking text files.

## State and persistence behavior

Persistent output is LCOV `.info` data written to `--output-filename`, stdout, or generated per-file outputs depending on options. Temporary state is written under `File::Temp` or configured `--tempdir`; children serialize merge state with `Storable` and may write captured stdout/stderr logs. Temporary `.gcov` files and child info files are removed unless `--preserve`/`preserve_intermediates` is set.

In-memory state is global-heavy: `@gcov_tool`, `$gcov_version`, `$gcov_caps`, `@data_directory`, `$trace_data`, `%compat_value`, `$single_file`, `$files_created`, profile hashes in `lcovutil`, and package-level counters. Child workers inherit this state across `fork()` and return deltas to the parent.

The script also changes process state: it sets locale, changes directories while running gcov, installs signal handlers, and may follow symlinks when computing internal source directories.

## Dependencies and integration points

`geninfo` depends on core Perl modules (`File::Basename`, `File::Spec`, `File::Temp`, `File::Copy`, `File::Path`, `Cwd`, `Capture::Tiny`, `Storable`, `POSIX`, `Time::HiRes`) and on `sources/test-tools/lcov/lib/lcovutil.pm`. External integration points are the selected `gcov` executable, `find`, optional demangling/version/context/resolve scripts, source files referenced by gcov output, and the filesystem layout of build/data directories.

It is invoked directly by users and indirectly by `lcov --capture`, which passes through many options and marks the call with `--call-from-lcov`. Its output is consumed by `lcov`, `genhtml`, and other LCOV trace readers.

## Risks and edge cases

- The tool shells out to `find`, `gcov`, optional scripts, and demanglers. Quoting and unusual filenames remain a high-risk area, especially with spaces, shell metacharacters, symlinks, and Windows/MSYS paths.
- Global mutable state plus `fork()` makes parallel failures subtle. Child serialization, partial temp cleanup, parent death checks, and retry behavior must stay aligned.
- Source-path matching is inherently heuristic when gcov emits relative paths or multiple source files share the same basename. `solve_ambiguous_match()` can fail if source text is unavailable or generated content differs.
- Version-dependent gcov formats are complex. GCC 9+ text format is deliberately rejected in favor of intermediate output, while JSON/intermediate parsing has separate assumptions.
- `read_gcno()` is a hand-written binary parser. Incorrect length, endianness, artificial-function, or version handling can drop functions or misassign line coverage.
- `--initial` cannot produce branch coverage in some modes, and branch/function/MC/DC flags depend on gcov capabilities detected from `gcov --help`.
- Filtering happens in multiple phases: source file filtering, exclusion markers, coverage filters, function erasure, and external filtering. Ordering bugs can change reported totals.
- Temporary links are created when data and graph files are in different directories; interrupted runs or preserve mode can leave artifacts.

## Test signals

Useful tests include invoking `geninfo --help` and `--version`, normal capture against a tiny GCC-instrumented C/C++ fixture, `--initial` capture from `.gcno`, `--all`, `--base-directory`, `--build-directory`, `--no-external`, include/exclude filters, branch/function coverage, and gcov intermediate JSON/text paths. Regression coverage should include duplicate basenames, symlinked build directories, libtool `.libs` layouts, missing `.gcno`, empty `.gcda`, child parallel processing, `--parallel 1` versus multiple workers, and malformed gcov/gcno inputs that should produce ignorable errors. Output should be validated with `lcov --list`, `genhtml`, and checksum/coverage-criteria checks.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/geninfo -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/genpng -->
# sources/test-tools/lcov/bin/genpng

## Purpose

`genpng` creates a compact PNG overview of a source or `.gcov` file by mapping each source character to one pixel. Its primary use is visual coverage navigation: covered, uncovered, uninstrumented, highlighted, and differential categories receive different foreground/background colors.

The script can be executed as a command-line tool or loaded by another Perl script. When loaded, it exposes `genpng_process_file()` and `gen_png()`.

## Important APIs, types, and functions

- `check_and_load_module("GD")` dynamically checks for the required `GD` Perl module and exits with code 2 when unavailable.
- Command options are parsed with `Getopt::Long`: `--tab-size`, `--width`, `--output-filename`, `--dark-mode`, `--help`, and `--version`.
- `genpng_process_file($filename, $out_filename, $width, $tab_size, $dark)` reads either plain text or `.gcov` text and converts it to internal `<count>:<source>` lines.
- `gen_png($filename, $show_tla, $dark, $width, $tab_size, @source)` builds the `GD::Image`, allocates color palettes, expands tabs, maps line tags/counts through `lcovutil::pngMap`, paints pixels, and writes PNG bytes.
- Colors for differential TLA categories come from `lcovutil` hashes `%tlaColor` and `%tlaTextColor`.

## Control flow

On direct command-line execution, `genpng` loads `GD`, parses options, validates the source filename, chooses a default output name of `<source>.png`, and calls `genpng_process_file()`. For `.gcov` input, the reader recognizes common gcov line forms: uninstrumented lines, zero-count lines, and positive-count lines. For plain text, every line is treated as uninstrumented.

`gen_png()` creates an image with width equal to the requested overview width and height equal to the number of source lines, falling back to one empty line for empty inputs. For each source line it expands tabs, parses an optional tag and execution count, chooses foreground/background colors, paints each non-space character with text color and each space with background color, truncates at image width, fills the rest of the row, and writes a binary PNG.

## State and persistence behavior

There is no long-lived state. The persistent result is the output PNG file. The function keeps only local image/color variables and a one-line memory of the previous instrumented line so uninstrumented continuation lines can inherit the prior coverage color region. It reads the full source into memory before rendering.

## Dependencies and integration points

`genpng` depends on Perl `GD`, `Getopt::Long`, `File::Basename`, `Cwd`, `FindBin`, and the shared LCOV `lcovutil` module. It integrates with `.gcov` text produced by gcov and with differential coverage metadata encoded as LCOV/HTML TLA tags. Other LCOV tools can `do` or require this script and call `gen_png()` directly.

## Risks and edge cases

- Missing `GD.pm` is a hard runtime dependency failure.
- The `.gcov` parser is regex-based and supports expected gcov text forms only; unexpected spacing or newer formats may silently skip lines.
- Width is not validated for positive values in this script, so invalid or tiny widths rely on GD/runtime behavior.
- The tab expansion formula is hand-written and affects pixel alignment against genhtml source views.
- Output height equals line count, so very large source files can allocate large images.
- The function dies on unknown PNG tags unless `lcovutil::pngMap` contains them.

## Test signals

Tests should cover `--help`, `--version`, missing filename, missing GD behavior in a controlled environment, plain-text rendering, `.gcov` rendering for uninstrumented/covered/uncovered lines, dark mode, tab expansion, width truncation, empty source files, and tagged differential inputs. A basic assertion can confirm a PNG signature is written and dimensions match width by line count.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/genpng -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/get_changes.sh -->
# sources/test-tools/lcov/bin/get_changes.sh

## Purpose

`get_changes.sh` prints LCOV change-log information. It prefers live Git history from the LCOV tool directory and falls back to the packaged `../CHANGES` file when Git metadata is unavailable.

## Important APIs, types, and functions

This is a small Bash script with no functions. `TOOLDIR=$(cd $(dirname $0) >/dev/null ; pwd)` resolves the directory containing the script, `cd $TOOLDIR` moves there, and the main command attempts `git --no-pager log --no-merges --decorate=short --color=never`. If that command fails, it runs `cat "$TOOLDIR/../CHANGES" 2>/dev/null`.

## Control flow

The script resolves its directory, changes to it, invokes Git log, and exits with Git's success path if available. On Git failure, the `if ! ...; then` fallback prints the static changes file if present. There is no explicit final status normalization, so the process exit status is the status of the command executed in the selected branch.

## State and persistence behavior

The script writes only to stdout/stderr and does not create files. It changes the process working directory, but that change is confined to the script process.

## Dependencies and integration points

Runtime dependencies are Bash, `dirname`, `cd`, `pwd`, `git`, and `cat`. It integrates with a source checkout containing `.git` history and with release archives containing `sources/test-tools/lcov/CHANGES`.

## Risks and edge cases

- `$0`, `dirname $0`, and `cd $TOOLDIR` are not consistently quoted, so paths containing spaces or glob characters can break.
- If Git exists but the directory is not a repository, the fallback hides Git diagnostics and tries `../CHANGES`.
- If both Git and `../CHANGES` fail, no message is printed and the exit status comes from `cat`.
- The script assumes it should operate from the tool directory rather than the user's current working directory.

## Test signals

Tests should run it in a Git checkout, in a copied tree without `.git` but with `CHANGES`, and in a copied tree without either data source. A path-with-spaces fixture would expose the current quoting weakness.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/get_changes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/get_version.sh -->
# sources/test-tools/lcov/bin/get_version.sh

## Purpose

`get_version.sh` prints LCOV version metadata in one of three forms: version, release, or full version string. It derives metadata from Git tags when available, from a packaged `.version` file when Git metadata is unavailable, and from hard-coded fallback defaults otherwise.

## Important APIs, types, and functions

This Bash script has no functions. It computes `DIRPATH`, `TOOLDIR`, and `GITVER=$(cd "$TOOLDIR" ; git describe --tags 2>/dev/null)`. If `GITVER` is empty and `../.version` exists, it `source`s that file. If Git metadata exists, it strips a leading `v`, extracts `VERSION` from the part before the first dash, and converts the first dash in the remaining suffix into a dot for `RELEASE`. Fallbacks set `VERSION=2.5.0`, `RELEASE=beta`, and `FULL="$VERSION-$RELEASE"`.

Supported outputs are selected by the first argument: `--version`, `--release`, or `--full`.

## Control flow

The script resolves its tool directory, tries Git tag description, fills version variables from Git or `.version`, applies fallback defaults, then conditionally echoes the requested value without a trailing newline. Unknown or missing arguments produce no output; there is no usage error path.

## State and persistence behavior

The script is read-only except for shell variables. It sources `../.version`, so that file can set or override shell variables in-process. It writes selected metadata to stdout and does not write files.

## Dependencies and integration points

Dependencies are Bash, `dirname`, `cd`, `pwd`, `git`, and an optional LCOV `.version` file containing shell assignments. It is likely called by build/release/manpage tooling and by `lcovutil` version discovery paths.

## Risks and edge cases

- Sourcing `.version` executes shell code from that file, which is normal for trusted release metadata but unsafe for untrusted trees.
- `git describe --tags` behavior depends on reachable tags; shallow or tagless clones fall back to `.version` or defaults.
- The Git parsing handles a single dash-based suffix conversion for `RELEASE`; unusual tag formats may produce surprising `FULL`/`RELEASE`.
- Unknown arguments silently succeed with no output because there is no final validation.
- Output uses `echo -n`, which is common but can vary in strict portability; Bash mitigates this.

## Test signals

Tests should cover Git-tagged checkout output, no-Git `.version` output, total fallback output, and each argument selector. Additional tests should verify unknown arguments produce empty output and that tags like `v2.5-3-gHASH` produce the expected `VERSION`, `RELEASE`, and `FULL`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/get_version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/lcov -->
# sources/test-tools/lcov/bin/lcov

## Purpose

`lcov` is the main LCOV command-line wrapper. It provides a single interface for resetting counters, capturing userspace or kernel coverage, packaging raw coverage files, combining tracefiles, extracting/removing files by pattern, listing trace contents, summarizing tracefiles, and computing trace intersections or differences. It delegates raw userspace capture to `geninfo` and delegates trace parsing/aggregation/filtering to `lcovutil`.

## Important APIs, types, and functions

- `%lcov_options` defines the command surface: `--directory`, `--capture`, `--zerocounters`, `--add-tracefile`, `--extract`, `--remove`, `--list`, `--summary`, `--intersect`, `--subtract`, `--to-package`, `--from-package`, kernel directory options, and pass-through geninfo options.
- `check_options()` enforces that exactly one primary action is selected.
- `userspace_reset()` deletes `.da` and `.gcda` files under selected directories using `find`.
- `userspace_capture()` either calls `lcov_geninfo()` or creates a raw coverage package.
- `lcov_geninfo()` constructs a `geninfo` command line and passes through output, test name, base/source directories, checksum, filters, coverage modes, demangling, resolve/version/context scripts, parallel/memory/profile settings, and error-handling options.
- Kernel helpers include `setup_gkv()`, `setup_gkv_sys()`, `setup_gkv_proc()`, `kernel_reset()`, `kernel_capture_initial()`, `kernel_capture()`, `copy_gcov_dir()`, `adjust_kernel_dir()`, and `kernel_capture_from_dir()`.
- Package helpers `create_package()`, `get_package()`, `count_package_data()`, `link_data()`, and related callbacks create or consume tarballs of raw coverage data plus metadata files `.gcov_kernel_version` and `.build_directory`.
- Trace operations use `AggregateTraces`, `TraceFile`, and `TraceInfo`: `add_traces()`, `merge_traces()`, `remove_file_patterns()`, `summary()`, and `emit()`.
- `list()` prints a table of per-file and total line/function/branch/MC/DC rates, using `get_prefix()`, `shorten_filename()`, `shorten_number()`, and `shorten_rate()` for formatting.

## Control flow

Startup installs LCOV signal/error handlers, records the command line, parses rc and command-line options, normalizes compatibility/list/external options, validates mode combinations, auto-detects kernel gcov support when needed, and dispatches to exactly one action.

Dispatch behavior is action-specific:

1. `--zerocounters` resets userspace files if `--directory` is present, otherwise writes to the kernel gcov reset node.
2. `--capture` captures from a package, userspace directory, or kernel gcov tree. Userspace capture normally executes `geninfo`; package/kernel capture may copy/link raw files first.
3. `--add-tracefile` merges tracefiles, optionally emitting function mappings or pruned testcase lists.
4. `--remove` and `--extract` load one tracefile, rely on `lcovutil` pattern state to filter it, and emit the result.
5. `--list` loads one tracefile and prints a formatted coverage table.
6. `--summary` merges tracefiles and prints summary data.
7. `--intersect` and `--subtract` merge base tracefiles from positional arguments with RHS glob patterns and apply a `TraceInfo` merge operation.

After dispatch, it cleans temporary directories, restores the original working directory, prints summaries or "Done", checks coverage criteria, emits warnings/profile data, and exits non-zero on errors or failed criteria.

## State and persistence behavior

Persistent effects depend on mode. Reset mode deletes `.da`/`.gcda` files or writes kernel reset controls. Capture and trace-transform modes write LCOV `.info` output or stdout. Package mode creates `.tar.gz` archives and temporarily writes `.build_directory` and `.gcov_kernel_version` into the package root before removing them. Kernel/package capture copies raw gcov trees into temporary directories and can create symlinks from package data into build directories.

In-memory state is primarily global option variables, `$output_filename`, `$data_stdout`, `$gcov_dir`, `$gcov_gkv`, and arrays of trace patterns. Temporary directory lifecycle is managed by `lcovutil::create_temp_dir()` and `temp_cleanup()`.

## Dependencies and integration points

The script uses Perl modules `File::Find`, `File::Path`, `File::Spec`, `Cwd`, `POSIX`, `Storable`, `Time::HiRes`, `FindBin`, and `lcovutil`. External commands include `geninfo`, `find`, `tar`, `mount`, `modprobe`, and filesystem access to `/sys/kernel/debug/gcov` or `/proc/gcov` for kernel capture. It integrates with LCOV tracefiles, raw GCC coverage data, kernel gcov debugfs/procfs layouts, and release/package workflows.

## Risks and edge cases

- Many file operations shell out with interpolated paths (`find`, `tar`, `mount`, `modprobe`), so unusual filenames or untrusted package names can be risky.
- `--to-package` and `--from-package` depend on tar behavior and temporarily mutate the source/package directory with metadata marker files.
- Kernel capture requires privileges and kernel gcov support; auto-detection may mount debugfs or load modules.
- Symlink management in package capture can fail or leave links if interrupted.
- `lcov_geninfo()` mirrors many options manually. New geninfo options must be added here or `lcov --capture` behavior will diverge from direct `geninfo`.
- `--diff` is still parsed but deliberately errors as deprecated/removed.
- Listing output is width-sensitive and can truncate rates/counts to `#` when values do not fit.
- `remove_file_patterns()` relies on global extract/remove option state in `lcovutil`, so behavior is not obvious from its local argument alone.

## Test signals

Tests should cover invalid combinations, `--capture` pass-through to `geninfo`, userspace reset, package create/read, merge/add, extract/remove, list formatting, summary, intersect/subtract, stdout output, coverage criteria failures, and ignored-error behavior. Kernel paths need privileged or mocked tests for `/sys/kernel/debug/gcov`, `/proc/gcov`, reset files, and module/debugfs setup. Regression tests should compare direct `geninfo` output with `lcov --capture` output for the same fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/lcov -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/bin/llvm2lcov -->
# sources/test-tools/lcov/bin/llvm2lcov

## Purpose

`llvm2lcov` converts JSON coverage exported by `llvm-cov export -format=text` into LCOV `.info` format. It supports line coverage, function coverage, branch coverage, and LLVM MC/DC records when requested and available. It is intended for Clang/LLVM instrumentation workflows using `llvm-profdata` and `llvm-cov`, then feeding LCOV/genhtml reporting.

## Important APIs, types, and functions

- `print_usage()` documents the LLVM workflow and tool-specific options.
- `parse($testname, @json_files)` is the core converter. It loads one or more JSON files, validates the top-level `data` array, resolves source paths, skips excluded files, creates `TraceFile`/per-file entries, and fills line/function/branch/MC/DC maps.
- `JsonSupport::load()` from `lcovutil` reads JSON. `version->parse()` handles LLVM JSON version comparisons.
- `ReadCurrentSource` resolves paths and extracts source expressions for branch and MC/DC labels.
- `TraceFile`, per-file `data()`, `test()`, `testfnc()`, `testbr()`, and `testcase_mcdc()` store output coverage.
- `BranchData`, `BranchBlock`, and `BranchElement` represent branch alternatives derived from LLVM branch regions.
- `MCDC_Data` records MC/DC blocks and expressions. The script has separate paths for JSON versions before `3.0.1` and for `3.0.1` or newer because LLVM changed MC/DC record shape and file-id handling.
- Command-line parsing uses `lcovutil::parseOptions()` with `--test-name` and `--output-filename`, plus common LCOV options handled by the shared parser.

## Control flow

The command-line path parses options, defaults output to `llvm2lcov.info`, calls `parse()`, applies filters, writes the LCOV info file, prints a summary, checks coverage criteria, summarizes messages, cleans callbacks, and exits according to criteria status.

Inside `parse()`, each JSON file is loaded and each `data` entry is traversed. File records are processed first: source paths are resolved, excluded files are skipped, file versions may be attached, and LLVM segment arrays are converted into LCOV line counts by walking adjacent segment boundaries. For older MC/DC JSON, file-level `mcdc_records` are combined with `MCDCBranchRegion` branch entries and source expressions.

Function records are then processed. The converter defines functions at their first region start line, adds execution counts, optionally builds branch blocks from LLVM branch arrays, and optionally builds MC/DC expression blocks. For newer JSON versions, it handles file IDs and expansion IDs so macro/expanded regions can be attributed to useful source locations. After all files are parsed, summary maps are built by unioning testcase-specific line, branch, function, and MC/DC data into each file's aggregate maps.

## State and persistence behavior

The persistent output is a single LCOV `.info` file. The converter keeps all parsed coverage in one `TraceFile` object until writing. It reads current source files for expression extraction but does not modify them. Global LCOV filter, exclusion, coverage-mode, verbosity, criteria, and callback state comes from `lcovutil`.

## Dependencies and integration points

The script depends on Perl `version`, common file/path modules, `Capture::Tiny`, `Storable`, `POSIX`, and the shared `lcovutil` library. It integrates with LLVM JSON schema fields including `data`, `files`, `functions`, `segments`, `branches`, `regions`, `expansions`, `summary`, and `mcdc_records`. Its output is standard LCOV trace data for `lcov`, `genhtml`, and related tools.

## Risks and edge cases

- The converter assumes exact array sizes for segments, branches, and MC/DC records. Unsupported LLVM schema changes cause dies or ignorable format errors.
- Line-count derivation from segments is subtle: adjacent same-line segments, region entries, gaps, and max-count selection can affect reported counts.
- MC/DC handling differs across JSON versions and expansion/file-id combinations. Missing source files or expression extraction failures degrade expression labels to numeric indexes.
- Branch block IDs are synthetic because LLVM JSON does not provide the same block identity as gcov; multiple expressions on one line are grouped by line with generated element indexes.
- Exclusion is source-path dependent, so path resolution and substitutions must match the JSON filenames and local filesystem.
- The script imports many modules also used by `geninfo`; some are not directly used in the current converter path, increasing maintenance noise.

## Test signals

Tests should convert minimal LLVM JSON for line-only coverage, functions, branches, macro expansions, excluded files, multiple JSON inputs, and MC/DC for both pre-`3.0.1` and `3.0.1+` schema variants. Output should be validated with `lcov --list` and `genhtml`. Negative tests should cover missing files, malformed JSON, unexpected array sizes, unsupported MC/DC entry sizes, skipped source filters, and coverage criteria failures.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/bin/llvm2lcov -->
