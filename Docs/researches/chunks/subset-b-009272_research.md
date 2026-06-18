# sources/test-tools/lcov/bin/genhtml lines 7225-14230

## Scope

This chunk covers the second half of the `genhtml` script. It starts in the top-level command-line option table and includes option normalization, trace ingestion orchestration, output asset creation, all major HTML renderer helpers, source-code view rendering, owner/date/differential navigation tables, function table generation, and late utility routines. Earlier packages in the same file define the data objects consumed here, including `SummaryInfo`, `FileOrDirectoryCallback`, `FileOrDirectoryOwnerCallback`, `FileOrDirectoryDateCallback`, `FileCoverageInfo`, `SourceFile`, `PrintCallback`, and `GenHtml`.

## Purpose

The covered code is the report-generation backend for lcov trace data. It turns parsed command-line and rc options into global rendering state, merges current and optional baseline traces, applies optional unified diff data, builds source and summary objects, and writes a tree of HTML, CSS, PNG, gzip, frameset, description, source, directory, file, owner/date, and function pages.

This chunk is especially responsible for the user-visible report layout:

- Top-level option behavior for differential coverage, owner/date bins, source annotations, source view suppression, frames, dark mode, table sorting, gzip output, function aliases, and HTML validation.
- Per-file processing that combines current trace data, optional baseline data, diff metadata, source annotation data, and coverage category maps into `SourceFile` and `SummaryInfo` structures.
- HTML table writers for directory/file rows, per-testcase detail rows, source-line rows, header summaries, owner summaries, date summaries, and function summaries.
- Static report assets such as `gcov.css`, color bar PNGs, sort icons, `.htaccess`, `cmd_line`, `profile.html`, and optional serialized coverage data.

## Main Control Flow

### Option normalization and top-level execution

Lines 7225-7638 are still executable top-level script code. After registering options in `%genhtml_options`, the script calls `lcovutil::parseOptions()` and exits on option parsing failure. The subsequent normalization step resolves global flags before any trace parsing:

- `--suppress-aliases` and the function-alias filter force `$merge_function_aliases`.
- `--serialize` enables `$buildSerializableDatabase`.
- `--no-html` implies `$no_sourceview`.
- Coverage threshold defaults cascade from generic `hi_limit`/`med_limit` to line, function, branch, and MC/DC thresholds.
- Rc-provided lists are copied into active lists for date bins, date labels, annotate scripts, select scripts, and function simplification scripts when the command line did not override them.
- External callbacks are configured through `lcovutil::configure_callback()` for source annotation, selection, and function-name simplification.
- `stop_on_error = 0` implicitly enables synthetic missing source files.
- `--flat` and `--hierarchical` are rejected together.
- Differential-navigation mode (`$show_tla`) is enabled for baseline or diff reports, while "legacy labels" are used for non-differential navigation.
- Annotation scripts imply date-bin reporting. Owner and date-bin options are rejected without annotation support.
- Supplying only one side of baseline/diff input produces a warning but still enables differential report mode.
- Dark mode rewrites TLA background/text color maps from the normal palette to the dark palette.

The script expands trace filename globs, computes default titles, resolves baseline files and dates, canonicalizes the CSS path, reads prolog/epilog templates, disables incompatible `--frames`/`--no-sourceview`, parses prefix options, constructs file/function sort lists, optionally loads `genpng`, creates the output directory, optionally saves copies of input trace/diff files, writes `cmd_line`, and finally calls `gen_html()` inside `eval`.

After `gen_html()` returns, the script records overall profile timing, reports unused include/exclude/source-directory patterns, evaluates coverage criteria, optionally serializes the top-level `SummaryInfo` tree with `Storable::store`, cleans callbacks, writes profile output, optionally validates HTML, converts accumulated ignorable errors into a nonzero exit code, and exits.

### `gen_html()`

`gen_html()` is the main report workflow:

1. Creates `ReadCurrentSource` and merges all current `.info` inputs through `AggregateTraces::merge()`.
2. Loads unified diff data, if provided, before baseline parsing so baseline source can be mapped through the diff.
3. Merges baseline trace inputs through `ReadBaselineSource` when present, or creates an empty `TraceFile` when a diff is provided without baseline data.
4. Checks path consistency across diff, baseline, and current trace data.
5. Determines filename prefixes automatically with `get_prefix()` unless `--no-prefix` or explicit prefixes were used.
6. Reads and filters optional testcase descriptions with `read_testfile()` and `remove_unused_descriptions()`.
7. Quotes callback-script arguments that contain spaces for display/debug consistency.
8. Writes CSS/PNG assets unless `--no-html`, and writes `.htaccess` for gzip output.
9. Instantiates `GenHtml->new($current_data)`, which drives the recursive directory/file processing defined earlier in the file but calls renderer functions in this chunk.
10. Verifies annotation scripts found at least one controlled file when annotation was requested.
11. Writes `descriptions.<ext>` when testcase descriptions exist.
12. Prints overall line/function/branch/MC/DC rates with `print_overall_rate()`.

The function returns the top-level `SummaryInfo` object from `GenHtml`.

### `process_file()`

`process_file($fileSummary, $parent_dir_summary, $trunc_dir, $rel_dir, $filename)` is the per-source-file bridge between trace data and page generation. It:

- Applies configured directory prefixes for display names.
- Pulls line, function, branch, and MC/DC trace structures from the current `TraceInfo` object.
- Populates the per-file `SummaryInfo` counts.
- Resolves baseline filename mappings through `$diff_data->baseline_file_name()` and fetches baseline data from `$base_data`.
- Constructs `FileCoverageInfo`, which categorizes line/function/branch/MC/DC data into differential TLA buckets.
- Builds a `SourceFile`, which also updates file summary counts, date bins, owner bins, and "new file as baseline" category conversions.
- Skips empty files.
- Temporarily attaches the parent directory summary to the file summary so HTML callbacks can build directory links.
- Writes the source view unless `--no-sourceview`.
- Builds function proportion maps for line, branch, and MC/DC coverage per function when `--show-proportion` is enabled.
- Writes one or more function pages when function coverage is enabled and the file has visible functions.
- Writes frame support files and overview PNGs when `--frames` is enabled.
- Returns per-testcase line/function/branch/MC/DC data to the caller so directory pages can show detail rows.

This function is the central integration point for `TraceFile`, `TraceInfo`, `FileCoverageInfo`, `SourceFile`, and the HTML writers.

### Directory, file, and summary pages

`write_summary_pages()` removes empty children from a `SummaryInfo`, drops empty directories from the output tree, emits optional console TLA summaries, decides whether owner/date bin pages are needed, and builds a list of directory page calls for every requested sort and detail permutation. It creates:

- Default `index.<ext>` pages.
- Sort variants for line/function/branch/MC/DC coverage.
- Detail variants when `--show-details` and per-testcase data are available.
- Date and owner bin summary pages when annotation/owner options are enabled.

`write_dir_page()` creates the concrete HTML page, writes a standard header, emits the file table when sources exist, or writes an empty-coverpoints message when a selected subset has no coverpoints.

`write_file_table()` writes the full directory/file table. It supports three primary keys:

- `name`: standard file or directory rows.
- `owner`: rows grouped by owner, with files/directories shown beneath each owner.
- `date`: rows grouped by age bin, with files/directories shown beneath each bin.

It also supports two secondary detail modes when primary key is `name`:

- `-owner`: expand owner rows underneath each file/directory.
- `-date`: expand age-bin rows underneath each file/directory.

The table writer dynamically includes line, MC/DC, branch, and function columns depending on enabled coverage types and actual data. It suppresses function columns for owner grouping because function ownership is not associated. It can show per-testcase detail rows by computing affecting tests with `get_affecting_tests()`.

## Important APIs and Functions

### User-facing and setup helpers

- `print_usage(*HANDLE)`: emits the CLI usage text for common, operation, and HTML-output options.
- `print_overall_rate($trace, $ln_do, $fn_do, $br_do, $mcdc_do, $summary)`: prints source-file count and aggregate rates. In TLA mode, it also prints nonzero TLA counts by coverage type.
- `compute_title($patterns, $info_files)`: chooses a title from a single file, a single glob/pattern, or the number of expanded coverage DB files.
- `parse_dir_prefix(@prefixes)`: splits command-line prefix entries by `lcovutil::split_char` and appends them to `@dir_prefix`.
- `apply_prefix($filename, @prefixes)`: removes the first matching configured prefix from a path, returning `root` when the whole filename equals the prefix.
- `get_prefix($min_dir, @filename_list)` and `shorten_prefix($path)`: choose a prefix that minimizes displayed path lengths while preserving at least the requested number of parent directories.
- `get_relative_base_path($subdirectory)`: computes `../` path segments for CSS/image links from nested output directories.

### Input and text processing

- `read_testfile($desc_filename)`: parses testcase description files with `TN:` and `TD:` records, sanitizes testcase names to word characters, and reports format/empty-file errors through `lcovutil::ignorable_error()`.
- `remove_unused_descriptions()`: removes descriptions whose test names are not present in `%current_data`.
- `escape_html($string)`: escapes `&`, `<`, `>`, and `"`, optionally expands tabs into spaces, and converts newlines to `<br>`.
- `escape_id($name)`: normalizes HTML anchor IDs to HTML 4.01-compatible characters.
- `get_date_string($time)`: formats timestamps as `yyyy-mm-dd hh:mm:ss`, using `SOURCE_DATE_EPOCH` when no explicit time is provided.
- `simplify_function_name($name)`: invokes the configured simplification callback and reports callback failures as ignorable callback errors.

### File creation and static assets

- `html_create(*HANDLE, $filename)`: opens an output HTML file under `$output_directory`, lowercasing the full path on case-insensitive platforms. With `--html-gzip`, it opens a pipe to `gzip -c > $filename`.
- `write_png_files()`: writes embedded PNG byte arrays for coverage bar colors (`ruby.png`, `amber.png`, `emerald.png`, `snow.png`), `glass.png`, and `updown.png` when table sorting is active.
- `write_htaccess_file()`: writes `.htaccess` with gzip HTML encoding.
- `write_css_file()`: either copies a user CSS file or writes generated `gcov.css`. The generated CSS defines page layout, header tables, file tables, owner/date rows, source lines, function rows, legends, TLA classes, and dark-mode/normal palette substitutions.
- `get_html_prolog($file)` and `get_html_epilog($file)`: read user templates or provide default HTML 4.01 Transitional wrappers with `@pagetitle@` and `@basedir@` substitutions.

### Generic HTML layout

- `write_html(*HANDLE, $html_code)`: strips one leading tab from every line and writes to the HTML handle.
- `write_html_prolog(*HANDLE, $base_dir, $pagetitle)`: substitutes title and base path in the configured prolog.
- `write_header_prolog()`, `write_header_line()`, and `write_header_epilog()`: build the shared title/header table.
- `write_html_epilog(*HANDLE, $base_dir, $break_frames?)`: writes footer/version text and the configured epilog. It adds `target="_parent"` when the page can be embedded in frames.
- `write_frameset()`, `write_overview()`, and `write_overview_line()`: create frameset and overview image-map pages for source views.

### Header and summary table builders

- `write_header(*HANDLE, $callback_type, $ctrl, $trunc_name, $rel_filename, $summary, $fileDetail, $differentialFunctionMap)`: builds the standard page header for directory, file, source, testcase-description, and function pages. It constructs breadcrumb/navigation links, test/baseline labels and dates, optional command/profile links, legends, active TLA column lists, line/function/branch/MC/DC summary rows, date-bin summaries, and owner summaries. It returns a map from coverage type to the active nonzero TLA columns used by file tables.
- `build_html_path($path, $key, $bin_type, $isFile, $isAbsolute)`: builds clickable hierarchical breadcrumbs.
- `buildHeaderSummaryTableRow()`: creates TLA count cells for a coverage type, linking nonzero counts to first source locations when a `SourceFile` is available.
- `buildDateSummaryTable()`: creates date-bin rows for line/function/branch/MC/DC coverage, including links to detail pages or source anchors.
- `buildOwnerSummaryTable()`: creates owner-bin rows, optionally filtering owners without uncovered code unless `--show-owners all` is active.
- `max($a, $b)`: small row-count helper.

### File and testcase tables

- `write_file_table_prolog()`: writes multi-row table headers, including optional owner/date bin columns and sortable subcolumn headings.
- `write_file_table_entry()`: writes a primary or secondary row for a file, directory, owner, or date bin. It builds links to source pages, directory pages, bin summary anchors, and first TLA locations; computes bar graphs and rate classes; writes found/hit/missed and TLA counts; and adds footnote markers for elided rows.
- `write_file_table_detail_entry()`: writes per-testcase detail rows beneath a file/directory row.
- `write_file_table_epilog()`: closes the file table.
- `get_sort_code()`, `get_file_code()`, `get_line_code()`, `get_func_code()`, `get_br_code()`, and `get_mcdc_code()`: build sortable column heading labels and links.
- `get_bar_graph_code($base_dir, $found, $hit)`: renders a 100-pixel coverage bar with color chosen by line-coverage thresholds.
- `classify_rate($found, $hit, $med, $hi)`: returns low/medium/high rate bucket indexes.
- `get_affecting_tests()`: returns testcase-level line/function/branch/MC/DC totals only for tests with nonzero line hits.

### Source-line rendering

- `write_source($srcfile, $count_data, $checkdata, $fileCovInfo, $funcdata, $sumbrcount, $mcdc_summary)`: writes a source view for one file and returns compact per-line data for `gen_png()`. It suppresses branch/MC/DC columns when no data exists, creates a `PrintCallback`, applies optional `--select-script` region elision, validates source checksums, and delegates each visible line to `write_source_line()`.
- `write_source_prolog()` and `write_source_epilog()`: open and close the source view table and fixed-width source `<pre>`.
- `write_source_line()`: renders one source line with optional age, owner, line number, branch symbols, MC/DC symbols, TLA label, hit count, source text, annotation tooltip, deleted-line marker, and next-navigation anchors. It also emits continuation rows when branch/MC/DC text exceeds the fixed field width.
- `format_count($count, $width)`: right-aligns counts and switches to a compact `>N*10^E` notation for values that do not fit.
- `fmt_centered($width, $text)`: centers source heading labels.

### Branch and MC/DC rendering

- `get_block_list($branch_or_mcdc_data)`: groups branch locations or MC/DC expressions into display blocks. Branch data becomes `[block, branch, record, length, open, close]`; MC/DC data is expanded into true and false senses per expression.
- `get_block_len($block)`: sums display widths for a branch/MC/DC block.
- `distribute_blocks($blocks, $field_width)`: wraps blocks over one or more fixed-width lines while trying to keep groups together.
- `get_branch_html($brdata, $cbdata)`: converts branch records into colored symbols: `+` for taken, `-` for not taken, `#` for not executed, and `x` for excluded. In differential mode it uses TLA classes and links to the next branch group with the same TLA.
- `get_mcdc_html($mcdc_data, $cbdata)`: converts MC/DC expressions into colored true/false sensitization symbols: `T`/`F` for sensitized, `t`/`f` for not sensitized, `-` for dropped, and `x` for excluded. Differential mode mirrors branch TLA navigation.

### Function pages

- `write_function_page()`: chooses output filenames for function tables by sort mode, writes the shared header, and calls `write_function_table()`.
- `funcview_get_label()`: returns function table headings with sort links for function name, hit count, unexercised lines, unexercised branches, or unexercised MC/DC expressions.
- `funcview_get_sorted()`: sorts function names alphabetically, by hit count, or by descending missed line/branch/MC/DC counts.
- `write_function_table()`: writes rows for function leader entries and optional alias rows. It hides deleted functions (`DUB`, `DCB`), applies function-name simplification, links functions back to source anchors, displays differential TLA labels, and optionally shows per-function line/branch/MC/DC rates.

## State and Persistence Behavior

This chunk relies on global mutable script state rather than passing an explicit context object. Important globals include:

- Input and title state: `@info_filenames`, `@base_filenames`, `$diff_filename`, `$test_title`, `$baseline_title`, `$current_date`, `$baseline_date`, `$age_basefile`.
- Output behavior: `$output_directory`, `$html_ext`, `$html_gzip`, `$html_prolog`, `$html_epilog`, `$css_filename`, `$no_html`, `$no_sourceview`, `$frames`, `$flat`, `$hierarchical`, `$sort_tables`, `$validateHTML`.
- Coverage thresholds and labels: `$ln_med_limit`, `$ln_hi_limit`, `$fn_med_limit`, `$fn_hi_limit`, `$br_med_limit`, `$br_hi_limit`, `$mcdc_med_limit`, `$mcdc_hi_limit`, `@rate_name`, `@rate_png`, `$show_tla`, `$use_legacyLabels`, `$show_hitTotalCol`, `$opt_missed`.
- Differential and annotation state: `$diff_data`, `$base_data`, `$current_data`, `@SourceFile::annotateScript`, `$show_dateBins`, `$show_ownerBins`, `$show_nonCodeOwners`, `$show_zeroTlaColumns`, `@datebins`, `@SummaryInfo::ageGroupHeader`.
- Path/rendering state: `@dir_prefix`, `@opt_dir_prefix`, `@fileview_prefixes`, `@fileview_sortlist`, `@funcview_sortlist`, `$tab_size`, `$charset`, `$footer`, `$legend`.
- Description and profile state: `%test_description`, `$lcovutil::profileData`, `$lcovutil::profile`.

Persistent side effects are all report artifacts under `$output_directory`:

- `cmd_line` is always written before `gen_html()`.
- `gcov.css`, color/sort PNGs, and optional `.htaccess` are written unless HTML is suppressed where applicable.
- `index*.html` and nested directory `index*.html` pages are generated for default, detail, sorted, owner, and date views.
- Per-file source pages use `<basename>.gcov.<ext>`.
- Per-file function pages use `<basename>.func.<ext>`, `<basename>.func-c.<ext>`, `<basename>.func-l.<ext>`, `<basename>.func-b.<ext>`, and `<basename>.func-m.<ext>` depending on sort/data availability.
- Frame mode adds `<basename>.gcov.png`, `<basename>.gcov.frameset.<ext>`, and `<basename>.gcov.overview.<ext>`.
- Test descriptions are written to `descriptions.<ext>`.
- `profile.html` and profile data are saved through `lcovutil::save_profile()`.
- Optional `--serialize` writes a `Storable` dump to the configured serialization path.
- Optional `--save` copies baseline, diff, and current trace inputs into the output directory.

## Dependencies and Integration Points

The chunk integrates with many packages defined elsewhere in `genhtml` and lcov support modules:

- `lcovutil`: option parsing, rc/profile state, logging, ignorable warnings/errors, palette maps, rate formatting helpers, coverage filters, path separators, callback configuration/cleanup, HTML validation trigger support, and profile saving.
- `AggregateTraces`: glob expansion and merging of trace files.
- `TraceFile`/`TraceInfo`: current and baseline coverage records.
- `ReadCurrentSource` and `ReadBaselineSource`: source lookup and checksum/source loading behavior.
- `FileCoverageInfo`: differential classification maps for lines, branches, MC/DC, and functions.
- `SourceFile`: annotated source lines, owner/date metadata, navigation lookups, and source-detail state.
- `SummaryInfo`: hierarchical coverage totals, TLA count accessors, owner/date aggregation, active age bins, sorting, and parent/child summary relationships.
- `FileOrDirectoryCallback`, `FileOrDirectoryOwnerCallback`, and `FileOrDirectoryDateCallback`: table row adapters that supply totals, callbacks, secondary rows, and file/directory links.
- `PrintCallback`: stateful helper for source-line rendering and next-link suppression.
- `CoverageCriteria`: optional post-generation criteria checks.
- `ValidateHTML`: optional output validation.
- `Date::Parse`, `DateTime`, `Time::HiRes`, `Storable`, `File::Spec`, `File::Basename`, `File::Path`, `File::Copy`, `Digest::MD5`, and external `gzip`/`cp` commands.
- `genpng`: loaded dynamically for frame overview PNG generation.

Callback integration is significant. Annotation, selection, version, resolve, criteria, and function-simplification scripts can alter which source lines are loaded, which regions are visible, how owners/dates are shown, how criteria affect exit status, and how function names appear.

## Risks and Edge Cases

- `html_create()` uses a shell pipeline string for gzip output: `gzip -c > $filename`. Filenames are derived from output paths, but shell interpretation still makes quoting and metacharacter safety important.
- `write_css_file()` shells out to `cp` for user CSS copying. It passes arguments as a list, which avoids shell interpolation, but failures only report `$!`, which may not describe nonzero exit status accurately.
- HTML is mostly hand-assembled. `escape_html()` is applied in many user/source-facing paths, but not uniformly for every constructed string. Callback output, custom prolog/epilog/footer, `--rc desc_html`, and some labels are intentionally trusted, so XSS/content-injection behavior depends on trusted input.
- A typo calls `lcovutil::ignorable_eror()` in the owner/date source-line path for undefined owner/age metadata. If that path is reached, it may fail with an undefined subroutine instead of reporting an ignorable error.
- The generated CSS includes `foreground-color` for `span.lineNumWithDelete`, which is not a valid CSS property; expected behavior likely meant `color`.
- Global state makes option interactions fragile. For example, `--no-html` changes source-view behavior, `--frames` is disabled by `--no-sourceview`, owner/date tables require annotation scripts, and TLA output mode changes hit-total columns and labels.
- `get_prefix()` is heuristic and uses resolved/absolute paths, so unusual path mappings, symlinks, or mixed absolute/relative trace paths can produce surprising display prefixes.
- Source selection elision in `write_source()` resets callback state across gaps and emits synthetic elision lines. Navigation correctness depends on `InInterestingRegion`, `PrintCallback`, and `SourceFile` next-location methods staying in sync.
- The branch and MC/DC formatting code relies on fixed field widths and handwritten display lengths. HTML tags are later stripped for continuation alignment, which is brittle when markup changes.
- Date/owner navigation assumes owner and age metadata exist for project code lines when annotation is enabled. Missing metadata can affect source rendering and table anchors.
- Function pages suppress deleted functions and optionally aliases. Merging/suppressing aliases changes table contents and sort results, which can confuse comparisons unless documented to users.
- `write_file_table()` has many combinations of primary key, bin type, detail view, flat/hierarchical mode, and source-view suppression. Link generation is the highest-risk area for regressions.
- MC/DC summary styling in `write_header()` uses branch thresholds (`$br_med_limit`, `$br_hi_limit`) for one header row path rather than MC/DC-specific thresholds, which may be intentional legacy behavior or a threshold bug.

## Test Signals

Useful validation signals for this chunk include:

- Run `genhtml` on a simple line-only trace and verify `index.<ext>`, `gcov.css`, PNG assets, `cmd_line`, and per-file source pages are created.
- Run with `--function-coverage`, `--branch-coverage`, and `--mcdc-coverage` traces to verify dynamic columns, source-line branch/MC/DC glyphs, and function pages.
- Run with `--baseline-file` and `--diff-file` to exercise TLA categories, differential colors, first/next navigation links, deleted-line markers, and hidden deleted functions.
- Run with `--annotate-script`, `--show-owners`, and `--date-bins` to verify owner/date header tables, source owner/date columns, owner/date detail pages, truncation behavior, and non-project file handling.
- Run `--show-details` with testcase descriptions to verify `descriptions.<ext>`, per-testcase detail rows, and description anchors.
- Run `--flat`, `--hierarchical`, and default layout separately to validate relative links and breadcrumbs.
- Run `--no-sourceview`, `--no-html`, and `--frames` combinations to ensure incompatible options are disabled or skipped as expected.
- Run `--html-gzip` and verify compressed HTML output plus `.htaccess`.
- Run `--dark-mode`, `--simplified-colors`, and default palettes to verify generated CSS classes and PNG bar assets.
- Run `--sort`/`--no-sort` and inspect generated sort pages and `updown.png` references.
- Run with `--serialize` and a coverage criteria script to confirm serialized top-level data and final exit status behavior.

## Chunk Boundary Notes

The chunk invokes several classes and methods whose definitions are outside this line range, notably `GenHtml->new`, `SummaryInfo` aggregation methods, `SourceFile` navigation methods, `FileCoverageInfo` categorization, and callback adapter classes. This research therefore describes their integration contracts as observed from calls in lines 7225-14230, not their internal implementations.
