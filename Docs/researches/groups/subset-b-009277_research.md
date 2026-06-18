# Research group subset-b-009277

This grouped report covers the requested lcov support scripts and test harness files. Each source file has its own marked section for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/P4version.pm -->
# sources/test-tools/lcov/scripts/P4version.pm

Purpose: Perl version-script callback for lcov/genhtml merges in Perforce workspaces. It maps source paths to Perforce depot revisions and returns stable version strings so coverage data from different source revisions is rejected before line numbers are merged.

Important APIs: package `P4version` exports `new`, `extract_version`, and `compare_version`. `new($script, @args)` parses `--md5`, `--allow-missing`, `--local-edit`, `--prefix`, and an optional depot root. `extract_version($filename)` returns a depot revision, an edited marker with mtime or md5, an md5/mtime fallback, or an empty string for allowed missing files. `compare_version` currently performs exact string inequality.

Control flow and state: construction shells out to `p4 have`, `p4 where`, and `p4 opened`, building an in-memory hash keyed by trimmed path, absolute path, and depot path. Local `add/edit/integrate/delete` states rewrite the stored version when `--local-edit` is allowed.

Dependencies and integration: uses `annotateutil` for modification time and md5, plus `lcovutil::ignorable_error` without an explicit `use lcovutil`, relying on caller environment. It is selected by `tests/common.mak` as `VERSION_SCRIPT` when the test tree is not a git checkout.

Risks and test signals: external `p4` output is parsed with strict regexes and many `die` paths, so Perforce localization, spaces, or changed output formats can break it. Command strings interpolate paths without shell quoting. Tests that run P4-backed coverage or version matching through `common.mak` are the main signals; most local developer runs probably exercise the git version path instead.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/P4version.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/analyzeInfoFiles -->
# sources/test-tools/lcov/scripts/analyzeInfoFiles

Purpose: diagnostic Perl utility that compares multiple lcov `.info` traces for source-file presence, source version agreement, and per-line code/non-code consistency. It is intended for debugging inconsistent capture results from supposedly identical code bases.

Important APIs/types: defines internal `Region` objects with `start`, `finish`, `size`, `consistent`, `in`, `out`, `buildCodeKey`, and `print`; and `FileData` objects with `name`, `traces`, `regions`, `regionsBySize`, `totalRegionSize`, `print`, and `checkLineCoverageConsistency`. The executable interface accepts `--include`, `--exclude`, `--substitute`, `--keep-going`, `--drop`, `--all`, `--compact`, `--sort`, and `--verbose`.

Control flow and state: arguments are expanded from `.info` filenames or list files, then each `TraceFile->load` result is indexed by source path. For each source, the script checks version string equality across traces, detects missing source files, optionally drops missing files, then scans line numbers to group contiguous regions where info files disagree about whether a line is code. Global variables in package `main` carry options and file-index mappings into `Region`/`FileData`.

Dependencies and integration: loads `lcovutil` from adjacent lib paths and uses `TraceFile`, `TraceInfo->sum`, `keylist`, `value`, and lcov include/exclude/substitution pattern handling.

Risks and test signals: uses smartmatch (`~~`), shell `wc -l`, and source-file existence to set scan bounds. Missing files fall back to largest observed line number. It can produce false confidence if version callbacks are absent. Tests are indirect through generated `.info` fixtures, lcov merge/consistency tests, and manual diagnostic use.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/analyzeInfoFiles -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/annotateutil.pm -->
# sources/test-tools/lcov/scripts/annotateutil.pm

Purpose: shared support module for annotation and version callbacks. It provides common output formatting, mtime/md5 helpers, fallback annotation for files outside a repository, and a cache-aware `AnnotateBase` superclass used by git and Perforce annotators.

Important APIs/types: package `annotateutil` exports `get_modify_time`, `compute_md5`, `call_annotate`, and `call_get_version`. Package `AnnotateBase` exposes `new`, `printlog`, `resolve_cache_dir`, `find_in_cache`, `store_in_cache`, `verify_annotation`, and `annotate`; subclasses implement `annotate_callback`.

Control flow and state: `call_annotate` constructs the callback class, invokes `annotate`, and emits pipe-delimited `cl|abbrev;full|when|text` records. `AnnotateBase::annotate` first checks a Storable cache keyed by source path and validated against `lcovutil::extractFileVersion`; on miss it delegates to `annotate_callback`, falls back to filesystem ownership/mtime if undef, optionally verifies text, and stores cache data.

Dependencies and integration: uses `POSIX`, `Cwd`, `Fcntl`, `File::Path`, `File::Spec`, `File::Basename`, `Storable`, and many `lcovutil` globals/functions provided by callback host scripts. `gitblame.pm` and `p4annotate.pm` inherit from it.

Risks and test signals: `compute_md5` shells out with an unquoted filename. Cache correctness depends on a configured version callback unless version errors are ignored. `verify_annotation` compares chomped lines without CR stripping on local file reads, while annotators often strip CR. Tests exercising `--annotate-script`, `--cache`, `--verify`, and version mismatch handling provide coverage signals.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/annotateutil.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/batchGitVersion.pm -->
# sources/test-tools/lcov/scripts/batchGitVersion.pm

Purpose: optimized git version-script callback that builds a repository-wide blob SHA database once, including submodules, and answers repeated `extract_version` calls from memory.

Important APIs: package `batchGitVersion` exports `new`, `extract_version`, `compare_version`, and `usage`. Options include `--md5`, `--allow-missing`, `--repo`, `--prepend`, repeated `--prefix`, `--token`, and verbose flags. Standalone execution delegates to `annotateutil::call_get_version`.

Control flow and state: `new` runs `git ls-tree -r --full-tree HEAD` in the main repo, records blob shas by path, tracks submodule commit entries, then runs `git submodule foreach` and stores submodule blob shas under composed paths. Prefixes are normalized with trailing slashes and used by `extract_version` to strip build-root path prefixes before hash lookup. Unknown existing files fall back to mtime plus optional md5.

Dependencies and integration: uses `annotateutil` for time/md5, `Getopt::Long`, `File::Spec`, and shell git commands. The returned version string is `"BLOB <sha>"` unless `--token` changes the token for backward compatibility.

Risks and test signals: the module explicitly does not detect local edits, so dirty working trees may compare equal. A regex for nested submodule commit lines appears narrow and may not match all `git ls-tree` formats. Shell command construction lacks quoting for repo paths. Tests should compare callback behavior against `gitversion.pm`, submodule fixtures, prefix/prepend behavior, and missing-file paths.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/batchGitVersion.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/context.pm -->
# sources/test-tools/lcov/scripts/context.pm

Purpose: example lcov/geninfo/genhtml `--context-script` callback that returns environment metadata for infrastructure debugging and optionally appends that metadata to lcov comments.

Important APIs: package `context` exports `new`. `new($script, @args)` accepts `--comment`. `context()` returns a hash containing `user`, `perl_version`, `perl`, and optionally `PERL5LIB`.

Control flow and state: construction validates arguments and creates a small blessed array. If `--comment` is present, it immediately calls `context` and pushes `key: value` strings into global `@lcovutil::comments`. The `context` method shells out to `whoami` and `which perl`, then chomps values.

Dependencies and integration: depends on `lcovutil` for comment storage and on the callback protocol that calls `$callback->context()` near tool completion. It is not used by the test Makefiles directly but is a sample support script shipped with lcov.

Risks and test signals: shelling out makes output platform-dependent and can fail in minimal containers. The constructor only accepts bare `--comment`; future option extensions need to preserve callback invocation semantics. Test signals are callback loading tests and any lcov/genhtml run configured with `--context-script context.pm,--comment`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/context.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/criteria -->
# sources/test-tools/lcov/scripts/criteria

Purpose: thin executable wrapper for the `criteria.pm` genhtml criteria callback. It decodes the JSON coverage summary argument and exits according to the callback result.

Important APIs: the script imports `criteria::new`, `lcovutil`, and `JsonSupport::decode`. Its command-line contract is `name type json-string [--signoff]` although the module supports additional coverage-type flags.

Control flow and state: it constructs `criteria->new($0, @ARGV)`, then parses `--signoff` again with `GetOptions`, pops the JSON string, decodes it, calls `$obj->check_criteria(@ARGV, $db)`, prints all returned messages, and exits with the status.

Dependencies and integration: lib paths are set relative to the script and support-scripts install location. This wrapper is used when callback invocation prefers an external process rather than loading `criteria.pm` directly.

Risks and test signals: parsing options both in `criteria->new` and again in the wrapper can consume or validate arguments unexpectedly, especially for module-only options. The script assumes `JsonSupport` is provided by `lcovutil`. Tests should exercise external `--criteria-script path/criteria` usage, failing JSON summaries, and `--signoff` suppress behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/criteria -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/criteria.pm -->
# sources/test-tools/lcov/scripts/criteria.pm

Purpose: reusable criteria callback implementing a simple quality gate: at selected hierarchy levels, the sum of uncovered/lost categories `UNC + LBC + UIC` must be zero for selected coverage types.

Important APIs: package `criteria` exports `new`. `new($script, @args)` accepts `--signoff`, `--function`, `--branch`, and `--mcdc`. `check_criteria($name, $type, $db)` returns `(status, messages)`.

Control flow and state: constructor builds a list of coverage types starting with `line` and appending selected `function`, `MC/DC`, and `branch`. `check_criteria` only evaluates when `$type eq 'top'`; it iterates configured types present in the decoded JSON map, sums `UNC`, `LBC`, and `UIC`, emits messages for non-zero sums, and suppresses nonzero exit status if signoff is enabled.

Dependencies and integration: designed for genhtml `--criteria-script`, either loaded as a Perl module or via the wrapper. Input schema follows lcov criteria-script JSON summaries.

Risks and test signals: coverage type name `MC/DC` must match the host JSON exactly, while threshold-like callbacks elsewhere use `mcdc`. The code ignores non-top levels by design. Tests should cover top-level line-only failure/success, optional branch/function/MC/DC checks, missing keys, and signoff mode.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/criteria.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/get_signature -->
# sources/test-tools/lcov/scripts/get_signature

Purpose: standalone sample version-script that uses an md5 checksum as the file version identifier and compares versions by exact string equality.

Important APIs: command modes are `get_signature [--allow-missing] filename` and `get_signature --compare old_version new_version filename`. It prints the checksum or an empty line for allowed missing files, and exits nonzero when comparison strings differ.

Control flow and state: argument parsing validates mode arity. In compare mode no filesystem access is needed. In extraction mode the script checks existence, canonicalizes the path with `abs_path`, runs `md5sum`, captures the first token, prints it, and exits with the `md5sum` status.

Dependencies and integration: depends on `Getopt::Long`, `Cwd`, POSIX import that is unused, and the external `md5sum` program. It is a process-based callback compatible with lcov `--version-script`.

Risks and test signals: command substitution does not quote the path, so filenames containing shell metacharacters or spaces are unsafe. `md5sum` is not portable to all platforms. Tests should include compare mode, missing-file behavior, and checksum matching on simple files; security-sensitive callers should prefer a Perl digest library.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/get_signature -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/getp4version -->
# sources/test-tools/lcov/scripts/getp4version

Purpose: older standalone Perforce version-script sample for lcov merge verification. It returns a P4 revision or fallback mtime/md5 signature for one filename.

Important APIs: modes are `getp4version [--md5] [--allow-missing] filename` and `getp4version --compare old_version new_version filename`. It supports special md5 comparison for non-P4 version strings.

Control flow and state: extraction canonicalizes the file, probes `p4 files` for repository membership, reads `p4 have` for a revision, checks `p4 opened` for local edits, appends mtime and optional md5 when needed, and prints the version string. Compare mode returns exact inequality except for md5 fallback strings where both sides have md5 tails.

Dependencies and integration: uses `annotateutil::get_modify_time` and `compute_md5`, plus external `p4`, `grep`, and shell redirection. It is a direct executable alternative to the module-oriented `P4version.pm`.

Risks and test signals: `p4 files $pathname` and other shell strings interpolate filenames without quoting. The script only handles edit local state in `p4 opened`, unlike `P4version.pm` which also considers add/delete/integrate. Test signals are P4 callback tests, missing file tests, local edit behavior, and md5 compare paths.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/getp4version -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitblame -->
# sources/test-tools/lcov/scripts/gitblame

Purpose: executable wrapper for `gitblame.pm` that formats git blame output for diffcov/lcov annotation callback use.

Important APIs: accepts `gitblame.pm` options such as `--p4`, `--prefix`, `--abbrev`, `--cache`, `--verify`, `--log`, optional domain, and pathname. It imports `gitblame::new` and `annotateutil::call_annotate`.

Control flow and state: if the final argument looks like a file or a non-option path, it calls `call_annotate('gitblame', $0, @ARGV)`, which constructs the class and prints annotation rows. Otherwise it only constructs `gitblame->new` to validate options/help.

Dependencies and integration: adds its own directory to `@INC`, so the module can be used from the source tree or installed support-scripts directory. It is the process callback sibling of the loadable module.

Risks and test signals: the path heuristic treats a final option-like string as constructor-only, so unusual filenames beginning with `-` need `--`-style handling elsewhere. Tests should verify wrapper/module parity, option validation, and actual annotation output via git fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitblame -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitblame.pm -->
# sources/test-tools/lcov/scripts/gitblame.pm

Purpose: loadable git annotation callback that runs `git blame -e` and converts results into the lcov/diffcov annotation tuple format, with optional cache, verification, P4 changelist mapping, and owner abbreviation.

Important APIs: package `gitblame` inherits `AnnotateBase`. `new` accepts `--p4`, `--prefix`, repeated `--abbrev`, `--cache`, `--verify`, `--log`, optional internal domain, and pathname. `annotate_callback($file, $version)` returns `[status, lines, version]` or undef to fall back to filesystem annotation.

Control flow and state: construction extends the base object with P4 mapping, abbreviation regexps, and prefix. Annotation validates readability, changes to the file directory, checks git repository membership with `git rev-parse` and `git ls-files`, then parses `git blame -e`. It normalizes owners, abbreviates by configured substitution regexps, rewrites timestamps to ISO-with-zone format, and optionally maps commits to git-p4 changelists via `git show -s`.

Dependencies and integration: depends on `annotateutil.pm`, `AnnotateBase`, git CLI, `File::Basename`, `File::Spec`, and `lcovutil` through the base class.

Risks and test signals: command strings are unquoted and basename-only blame can be ambiguous with odd filenames. Abbreviation regexps are `eval`ed. Git blame output parsing is strict and may fail on unusual author/date formatting. Test signals include annotate-cache tests, `--verify`, domain abbreviation, git-p4 commit messages, and non-repo fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitblame.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitdiff -->
# sources/test-tools/lcov/scripts/gitdiff

Purpose: extracts a unified diff between two git revisions, optionally filtered by include/exclude regexps, and optionally emits placeholder entries for unchanged files so downstream diffcov/genhtml code can disambiguate basenames.

Important APIs: command usage accepts optional `[dir] base_SHA current_SHA` plus `--repo`, `--prefix`, `--include`, `--exclude`, `--no-unchanged`, `-b/--blank`, and `--verbose`.

Control flow and state: include/exclude options are comma-expanded. The script runs `git diff` in the realpath of `--repo`, rewrites `a/` and `b/` path prefixes to the configured prefix, tracks files seen in diff headers, and prints only included file hunks. Unless `--no-unchanged` is set, it then runs `git ls-tree -r --name-only` for the current SHA and emits synthetic `diff --git` plus `===` markers for included files not in the diff.

Dependencies and integration: uses git CLI, `Getopt::Long`, and `Cwd::realpath`. It is a diff-file generator for lcov/genhtml differential coverage.

Risks and test signals: include/exclude regexps run against git-style paths after partial prefix manipulation; path normalization can produce absolute repo-prefixed synthetic paths unlike raw diff headers. Shell command interpolation is unquoted. Tests should cover changed, deleted, added, unchanged, whitespace-ignored, include/exclude, and prefix modes.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitdiff -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitversion -->
# sources/test-tools/lcov/scripts/gitversion

Purpose: executable wrapper for `gitversion.pm`, providing process-based lcov `--version-script` behavior.

Important APIs: accepts `--compare old_version new_version filename` or extraction flags `--md5`, `--p4`, `--prefix`, `--allow-missing`, and `--help`. It imports `gitversion::new` and `usage`.

Control flow and state: the wrapper constructs `gitversion->new($0, @ARGV)`, then parses the same options to determine whether this invocation is comparison or extraction. Compare mode exits with `$class->compare_version(@ARGV)`. Extraction prints `$class->extract_version(@ARGV)` and exits zero.

Dependencies and integration: adds the script directory to `@INC` and delegates all substantive behavior to `gitversion.pm`. Used as a standalone callback where loading the module directly is not configured.

Risks and test signals: double option parsing can be brittle and `usage($help)` passes a boolean to a function expecting an executable path. Still, the module constructor does most validation. Tests should exercise wrapper compare/extract parity with `gitversion.pm`, help handling, missing files, md5 fallback, and local-change mode.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitversion -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitversion.pm -->
# sources/test-tools/lcov/scripts/gitversion.pm

Purpose: git version-script callback that reports the last commit affecting a file, optionally mapped to a git-p4 changelist, with optional dirty-file detection.

Important APIs: package `gitversion` exports `new`, `extract_version`, `compare_version`, and `usage`. Options include `--md5`, `--p4`, `--prefix`, `--allow-missing`, and `--local-change`.

Control flow and state: `extract_version` applies prefix to relative names, checks existence, resolves absolute path, and runs git commands from the containing directory. If the directory is in a git repo and `git log --no-abbrev --oneline -1 <file>` returns a commit, it emits `SHA <commit>` or scans `git show -s` for a `git-p4` changelist and emits `CL <id>`. With `--local-change`, non-empty `git diff <file>` appends edited mtime and optional md5. Non-git files fall back to mtime and optional md5.

Dependencies and integration: uses `annotateutil` helpers and git CLI. `tests/common.mak` selects it as the default `VERSION_SCRIPT` in git checkouts.

Risks and test signals: commands interpolate paths without quoting and use basename from the file directory. Untracked files in git worktrees fall through to mtime. Compare md5 logic is subtle and only applies for fallback/edited strings. Tests include lcov merge version checks, git dirty-file behavior, git-p4 mapping, and wrapper parity.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/gitversion.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/history.pm -->
# sources/test-tools/lcov/scripts/history.pm

Purpose: load-balancing history callback for lcov/geninfo/genhtml. It reads prior `--profile` JSON files and predicts per-file execution time so parallel schedulers can start historically expensive work first.

Important APIs: package `history` exports `new`; callback method `history($name)` returns a predicted time or undef. Helper `appendElements($predicted, $in, $sub)` accumulates totals and counts for averaging.

Control flow and state: construction inspects `lcovutil::tool_name` to decide required profile keys (`file` for genhtml, `file` and `find` for geninfo/lcov capture), expands glob arguments, loads JSON through `JsonSupport::load`, validates required keys, and ignores invalid/empty inputs via `lcovutil::ignorable_error`. With multiple profiles, it averages values. For geninfo, it strips capture-directory prefixes using directories from the `find` profile key before merging file costs.

Dependencies and integration: depends on `lcovutil`, `Time::HiRes`, and profile data schemas emitted by lcov tools. It stores callback processing time in `%lcovutil::profileData`.

Risks and test signals: profile schema drift or tool-name mismatch causes ignored history. Regex construction from directory names is not escaped. Multiple data files are averaged equally regardless of recency. Test signals include profile generation, `--history-script` scheduling tests, invalid JSON handling, and lcov/geninfo/genhtml-specific key validation.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/history.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/p4annotate -->
# sources/test-tools/lcov/scripts/p4annotate

Purpose: executable wrapper for `p4annotate.pm`, turning Perforce annotation data into lcov/diffcov callback output.

Important APIs: accepts module options such as `--log`, `--cache`, `--verify`, and a filename. It imports `p4annotate::new` and `annotateutil::call_annotate`.

Control flow and state: mirrors the `gitblame` wrapper. If the last argument is an existing file or non-option path, it calls `call_annotate('p4annotate', $0, @ARGV)` to print annotation records. Otherwise it constructs the module object, primarily for option validation or help.

Dependencies and integration: sets `@INC` to the support-scripts directory and delegates to `p4annotate.pm`. In non-git test environments, `tests/common.mak` points `ANNOTATE_SCRIPT` at `p4annotate.pm,--verify`, not necessarily this wrapper, but the wrapper remains compatible with process callback use.

Risks and test signals: same last-argument heuristic issue as `gitblame`. Test coverage should verify wrapper/module parity, environment validation, and annotation formatting in Perforce workspaces.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/p4annotate -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/p4annotate.pm -->
# sources/test-tools/lcov/scripts/p4annotate.pm

Purpose: loadable Perforce annotation callback with cache/log/verify support. It runs `p4 annotate`, merges local edits from `p4 diff`, and returns per-line owner/date/changelist metadata.

Important APIs: package `p4annotate` inherits `AnnotateBase`. `new($script, @args)` accepts `--verify`, `--log`, `--cache`, and `--help`, and validates `P4USER`, `P4PORT`, and `P4CLIENT`. `annotate_callback($pathname, $computed_version)` returns `[status, lines, version]` or undef for filesystem fallback.

Control flow and state: symlink paths are resolved manually. If `p4 files` confirms repository membership, the module reads `p4 have` for revision, checks `p4 opened` for local edit/integrate, parses `p4 diff` normal diff output into `%localAdd` and `%localDelete`, then streams `p4 annotate -Iucq` and interleaves local additions/deletions with depot annotation lines. Local additions are attributed to `P4USER` and file mtime.

Dependencies and integration: depends on `annotateutil`, `AnnotateBase`, Perforce CLI, and callback host globals through the base class.

Risks and test signals: Perforce output parsing is strict and assumes normal diff format. Timezone is hard-coded to `-05:00` for P4 dates. Shell command paths are unquoted. Local delete/add line tracking can die on unexpected diff shape. Tests should cover plain annotate, local edit merge, cache/verify, symlink resolution, and non-repo fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/p4annotate.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/p4udiff -->
# sources/test-tools/lcov/scripts/p4udiff

Purpose: generates a unified diff between two Perforce changelists, labels, or a baseline and current sandbox state, including optional unchanged-file markers for differential coverage.

Important APIs/types: internal `P4File` parses `p4 files`/`p4 opened` descriptions and exposes `path`, `name`, `rev`, `action`, `changelist`, and `type`. `P4FileList` stores included non-binary files with `append`, `files`, `get`, `remove`, and `include_me`. CLI usage is `p4udiff [--include/--exclude] [-b] [--no-unchanged] sandbox_directory base current`.

Control flow and state: the script maps sandbox to depot path with `p4 where`, builds baseline and current file lists, adjusts current state for `sandbox` by querying `p4 opened`, computes a union with presence states, streams `p4 diff -du`, rewrites depot paths to sandbox paths, filters hunks, then emits synthetic sections for unchanged, deleted, and added files using `p4 print` or local file content.

Dependencies and integration: depends on P4 CLI, `DateTime` import, regex include/exclude filters, and unified diff conventions consumed by lcov/genhtml differential reports.

Risks and test signals: command strings are often unquoted, `p4 where` parsing assumes three whitespace-separated fields, and binary files are dropped. The `-b` flag is parsed but not incorporated into the diff command. Tests require Perforce fixtures for changed/deleted/added/sandbox cases and should validate unchanged suppression.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/p4udiff -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/select.pm -->
# sources/test-tools/lcov/scripts/select.pm

Purpose: genhtml `--select-script` callback that decides whether a line or coverpoint is interesting enough to include, based on differential TLA category, commit/changelist, owner regexp, or age range.

Important APIs: package `select` exports `new`. Options are `--range`, `--owner`, `--tla`, `--sha`/`--cl`, and `--separator`. Runtime methods are `select($lineData, $annotateData, $filename, $lineNo)`, `save`, `restore`, and `finalize`.

Control flow and state: constructor splits list arguments, validates regexps and TLA names against `%lcovutil::tlaColor`, validates numeric ranges, and checks that annotation/diff/baseline prerequisites exist for selected criteria. The object stores criteria arrays, match counters, plaintext labels, and total seen coverpoints. `select` first matches coverage TLA, then annotation age, commit prefix regex, and owner full-name regex; any match returns true and increments criterion counters. `finalize` reports match counts.

Dependencies and integration: depends on `lcovutil`, `SourceFile::annotateScript`, `@main::base_filenames`, and `$main::diff_filename` provided by genhtml. Annotation data must provide `age`, `commit`, and `full_name`; line data must provide `tla`, `type`.

Risks and test signals: age matching uses equality against provided range objects rather than checking min/max bounds, which is suspicious. Regexps are user supplied. Tests should cover TLA-only, owner/SHA with annotation enabled, prerequisite warnings, save/restore aggregation, and final count output.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/select.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/simplify.pm -->
# sources/test-tools/lcov/scripts/simplify.pm

Purpose: genhtml `--simplify-script` callback that rewrites displayed function names using ordered substitution regexps. It affects function detail presentation only, not stored coverage identities.

Important APIs: package `simplify` exports `new`. Options are mutually exclusive `--file regexp_file_name` or repeated `--re regexp`, with optional `--separator`. Methods are `simplify($name)`, `start`, `save`, `restore`, and `finalize`.

Control flow and state: constructor loads regexps from a file or command line, validates patterns through `lcovutil::verify_regexp_patterns`, expects substitution form `s<sep>pattern<sep>replacement<sep>g`, precompiles pattern components, and stores a per-pattern match count. `simplify` applies every substitution in order and increments the pattern count when it changes the name. `start/save/restore/finalize` support parallel callback aggregation and unused-pattern warnings.

Dependencies and integration: depends on `lcovutil` for regex validation and `warn_pattern_list`. Invoked by genhtml while rendering function tables.

Risks and test signals: the parser only accepts global substitutions with exactly three split fields, so escaped separators or flags other than `g` are unsupported. Replacement strings are used literally in Perl substitution context. Tests should verify file and inline patterns, separator handling, invalid patterns, parallel save/restore, and warning output for unused rules.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/simplify.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/spreadsheet.py -->
# sources/test-tools/lcov/scripts/spreadsheet.py

Purpose: converts lcov/geninfo/genhtml profile JSON files into an Excel workbook for performance analysis, including per-tool worksheets, optional summary sheets, statistics, and conditional highlighting of outliers.

Important APIs/types: executable Python script using class `GenerateSpreadsheet(excelFile, files, args)`. CLI options include `-o`, `--threshold`, `--low`, `--high`, `-v/--verbose`, `--show-filter`, and profile JSON filenames. Internally, nested helpers insert conditional formats, statistics rows, data sections, and per-tool layouts.

Control flow and state: the constructor opens an `xlsxwriter.Workbook`, creates a summary sheet when multiple files are present, loads each JSON, identifies the tool from `data['config']['tool']` (with `lcov --call-from-lcov` treated as geninfo), creates a sanitized worksheet name, writes config and total rows, then dispatches profile-specific table generation for lcov segments, geninfo chunks/files/filter phases, genhtml scopes, or generic fallback keys. Summary formulas link back to individual worksheets.

Dependencies and integration: depends on `xlsxwriter`, JSON profile schemas emitted by lcov tools, and is wired into `tests/common.mak` as `SPREADSHEET_TOOL`; top-level test `Makefile` uses it in the `excel` target.

Risks and test signals: global threshold CLI options are parsed but not assigned back to module globals. Many broad `except` blocks skip corrupt data silently. Worksheet names may collide after truncation but have retry logic. Tests should run the `excel` target against generated JSON profiles and inspect workbook creation rather than full cell fidelity.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/spreadsheet.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/threshold.pm -->
# sources/test-tools/lcov/scripts/threshold.pm

Purpose: criteria callback that enforces minimum coverage percentages for selected coverage types at any callback level, typically top or file.

Important APIs: package `threshold` exports `new`. Options include `--signoff`, `--line`, `--branch`, `--mcdc`, and `--function`. `check_criteria($name, $type, $db)` returns `(status, messages)`.

Control flow and state: constructor builds a hash of configured thresholds, requires at least one, and validates every value as numeric in `(0,100]`. `check_criteria` iterates configured keys present in the JSON DB, skips zero-found entries, computes `100 * hit / found`, and records a failure message when actual coverage is below the threshold. `--signoff` suppresses failing status while still returning messages.

Dependencies and integration: uses `Getopt::Long` and `Scalar::Util::looks_like_number`; input schema is the lcov criteria-script JSON summary.

Risks and test signals: missing coverage keys are ignored, which may be desirable for disabled coverage but can hide misconfiguration. The usage text mentions `--suppress` in comments while the implementation uses `--signoff`. Tests should cover threshold boundaries, missing/zero found counts, multiple coverage types, and signoff behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/threshold.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/scripts/unreach.pm -->
# sources/test-tools/lcov/scripts/unreach.pm

Purpose: genhtml/lcov `--unreachable-script` callback that excludes branch and MC/DC coverpoints marked unreachable by source comments.

Important APIs: package `unreach` exposes `new`, `exclude($type, $reader, $testdata, $summary)`, `exclude_branch`, `exclude_cond`, `start`, `save`, `restore`, and `finalize`. Options are `--branch`, `--mcdc`, or neither to use enabled coverage modes.

Control flow and state: constructor validates options and creates regex/count pairs for branch comments `LCOV_UNREACHABLE_BRANCH` and MC/DC comments `LCOV_UNREACHABLE_COND`. `exclude` scans source lines from a reader for matching annotations, parses semicolon-separated exclusion specs, updates summary and per-test maps, and decrements found/hit counters when a coverpoint is newly excluded. `start/save/restore/finalize` reset and aggregate exclusion counts.

Dependencies and integration: depends on `lcovutil` coverage flags and error reporting, `BranchMap` indexes, branch data objects with `getBlock/getElement/set_excluded`, and MC/DC data objects with group/expression APIs.

Risks and test signals: parser error messages mix branch and MC/DC wording. Index validation is delegated to underlying objects and dies on invalid specs. Counter decrements must stay in sync with map layouts. Tests should include branch-only, MC/DC-only, combined comments, invalid ids, multiple testdata maps, and finalize count output.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/scripts/unreach.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/Makefile -->
# sources/test-tools/lcov/tests/Makefile

Purpose: top-level LCOV test Makefile that composes common test rules, runs all major test suites, and optionally builds coverage and performance reports from the test run.

Important targets/state: exports `COVER_DB`, `PYCOV_DB`, and `HTML_RPT` when `COVERAGE=1`; defines `all: check report`; includes `common.mak`; sets `TESTS := genhtml lcov llvm2lcov py2lcov perl2lcov xml2lcov`; defines `excel`, `info`, `report`, and `clean`.

Control flow and persistence: `excel` converts all JSON profiles to `report.xlsx`. `info` merges Devel::Cover databases, optionally emits per-test coverage info, converts Perl and Python coverage data to lcov info files, and preserves per-test artifacts when configured. `report` runs genhtml over produced info files with branch, annotation, version, and filter options. `clean` removes generated info/log/count/gcov/report/coverage artifacts and generated source.

Dependencies and integration: relies on variables and tools from `common.mak`, including `PERL2LCOV_TOOL`, `PY2LCOV_TOOL`, `GENHTML_TOOL`, `ANNOTATE_SCRIPT`, `VERSION_SCRIPT`, and `SPREADSHEET_TOOL`.

Risks and test signals: coverage targets are shell-heavy and assume Devel::Cover, Python coverage, and lcov converters are installed. Globs are intentionally tolerant. The main signal is `make check`; coverage reporting is an optional deeper signal with more environmental dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/check_counts -->
# sources/test-tools/lcov/tests/bin/check_counts

Purpose: small Perl assertion helper that compares expected coverage counts against lcov/genhtml textual summary output.

Important APIs: executable usage is `check_counts <counts_file> <output_file>`. Helper `do_cmp($title, $a, $b)` prints equality/mismatch and returns a mismatch bit.

Control flow and state: reads the output file and extracts the latest matches for `N of M lines`, `functions`, and `branches`. It then reads the first line of the counts file as six integers: line hit/found, function hit/found, branch hit/found. It compares each pair, ORs mismatch bits into `$rc`, prints comparison details, and exits `$rc`.

Dependencies and integration: relies on summary wording emitted by lcov/genhtml tests and count fixtures generated by `mkinfo`. The `$LCOV` environment variable is read but not used.

Risks and test signals: parsing is fragile to output text changes and only captures integer summaries. It cannot distinguish multiple summaries except by last match. It is itself a test helper; failures identify summary/count drift in generated coverage tests.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/check_counts -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/checkdeps -->
# sources/test-tools/lcov/tests/bin/checkdeps

Purpose: Perl dependency preflight helper for test scripts. It scans shebang Perl files for simple `use Module;` directives and verifies that required modules can be loaded.

Important APIs: executable `checkdeps <perl-file1> ...`. Helper `check_file($file)` returns nonzero if required modules are missing; `main` aggregates across all paths.

Control flow and state: for each file, it reads the first line and only scans files whose shebang mentions Perl. It then scans later lines matching `use <module> ...;`, skips repository-local modules such as `lcovutil`, `annotateutil`, `gitversion`, `gitblame`, `getp4version`, and `p4annotate`, and runs `eval("require $module")`. Missing modules emit warnings and set return code.

Dependencies and integration: invoked by `common.mak` `checkdeps` over lcov binaries and test helpers before running tests.

Risks and test signals: only catches straightforward static `use` lines and can mis-handle import arguments or conditional dependencies. `eval` with module text parsed from source is acceptable in trusted test code but not general-purpose safe. Test signal is early failure when a developer machine lacks required Perl modules.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/checkdeps -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/cleantests.py -->
# sources/test-tools/lcov/tests/bin/cleantests.py

Purpose: Python cleanup utility for LCOV tests, replacing shell cleanup logic. It removes generated top-level artifacts and recursively runs `make clean` in selected test directories.

Important APIs: CLI accepts positional tests and `-s/--silent`. Functions are `parse_args`, `find_topdir`, `clean_test(base_dir, test_name)`, and `main`.

Control flow and persistence: `find_topdir` prefers current directory with `common.mak`, then `TOPDIR`, then upward search. `main` uses the current directory as the base for requested tests, removes `test.log`, `test.counts`, `test.time`, `test.log.d`, coverage directories, and top-level `*.info`/`*.counts`, then cleans explicit tests or default suite directories. `clean_test` skips `.sh`/`.pl` scripts and runs `make -C <dir> clean -s` for directories with Makefiles, ignoring failures.

Dependencies and integration: called by `common.mak` `clean_subdirs` and top-level Makefiles. Uses Python stdlib `argparse`, `pathlib`, `shutil`, and `subprocess`.

Risks and test signals: broad ignored exceptions can hide cleanup failures. It deletes generated artifacts under discovered topdir, so incorrect `TOPDIR` would be harmful. Tests are practical: run `make clean` after generating fixtures and verify expected artifacts disappear without deleting source tests.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/cleantests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/common.py -->
# sources/test-tools/lcov/tests/bin/common.py

Purpose: shared Python utilities for the newer Python test runner and worker modules.

Important APIs/types: constants for ANSI colors, `timestamp()`, `detail(key, value)`, `marker()`, `find_topdir()`, `get_parallel_default()`, and class `TestResult`.

Control flow and state: color constants depend on `sys.stdout.isatty()`. `detail` formats fixed-width key/value log lines compatible with shell helpers. `find_topdir` uses `TOPDIR` if valid, otherwise searches upward for either `tests/bin` or `bin` plus `common.mak`. `get_parallel_default` caps multiprocessing CPU count at 8. `TestResult` stores name, result, exit code, duration, memory, log file, coverage directory, and optional error text.

Dependencies and integration: imported by `runtests.py`; a similarly named dataclass exists in `test_worker.py`, so consumers must be clear which class is returned.

Risks and test signals: duplicated `TestResult` definitions can diverge. `detail` truncation math assumes short keys; long keys reduce dot padding. Test signals are successful runner initialization, correctly formatted logs, and topdir discovery from both top-level and subdirectory invocations.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/mkinfo -->
# sources/test-tools/lcov/tests/bin/mkinfo

Purpose: deterministic-ish fixture generator for fake lcov coverage data and optional source trees. It creates full, target, partial, and zero coverage `.info`/`.counts` files used by LCOV regression tests.

Important APIs: configuration helpers `read_config`, `apply_config`, `get_value`, `get_int`, `get_list`; generation helpers for filenames, lines, functions, branch distributions, source structures, hits, filters, splitting, and writing; `main` handles CLI `mkinfo <config_file> [-o output_dir] [--seed seed] [section.key=value...]`.

Control flow and persistence: after parsing config and seeding `rand`, it generates a random source model with files, instrumented lines, functions, and branches; optionally writes blank source files under `-o`; creates random full hit data; writes `full.info/counts`; reduces hits to target coverage and writes `target`; splits hits into complementary `part1`/`part2`; zeroes all hits and writes `zero`. Count files summarize aggregate hit/found totals for validation.

Dependencies and integration: invoked by `common.mak` `prepare` to create `ZEROINFO`, `FULLINFO`, `TARGETINFO`, `PART1INFO`, and `PART2INFO`. Uses Perl stdlib `Getopt::Long`, `Cwd`, `File::Path`, `File::Basename`, and `Data::Dumper`.

Risks and test signals: random generation can create odd edge cases, controlled by `--seed`. Branch hit sanitization encodes lcov rule that untaken blocks use `-`. Tests depend heavily on output consistency; `check_counts` and downstream lcov/genhtml tests are the main validators.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/mkinfo -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/runtests.py -->
# sources/test-tools/lcov/tests/bin/runtests.py

Purpose: Python LCOV test driver with serial or parallel execution, replacing shell runner behavior while preserving Makefile compatibility and log/count outputs.

Important APIs/types: CLI parser supports positional tests, `-j/--parallel`, `--coverage`, `--script-args`, `--keep-logs`, `--keep-going`, `--list`, `--timeout`, `--silent`, and `--debug`. Class `TestRunner` implements setup, test discovery, parallel execution, log merge, coverage merge, summary, cleanup, and `run`.

Control flow and persistence: setup creates `test.log.d`, optional `cover_db.d`, initializes `test.log`, and runs `testsuite_init`. Discovery parses `TESTS` variables from Makefiles, recurses into subdirectories, or accepts explicit tests. `run_all_tests` uses `ThreadPoolExecutor` and `test_worker.run_test_worker`. Results are merged into `test.log`, `test.counts` is written, Python coverage files are combined, and `testsuite_exit` is run in cleanup.

Dependencies and integration: called by `common.mak` `check`. Imports `common.py` and `test_worker.py`; runs shell scripts in test directories and lcov tool binaries from the surrounding tree.

Risks and test signals: `--keep-going` is parsed but not used to stop/continue behavior; all submitted tests run regardless. Coverage merge handles Python coverage but only records a note for Devel::Cover. Makefile parsing is simple and may miss complex variables. Test signal is `make check`, with `--list`, `-j`, and coverage modes as focused checks.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/runtests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/test_run -->
# sources/test-tools/lcov/tests/bin/test_run

Purpose: legacy Bash helper that runs one test script, records command output, timing, memory, result status, and failure excerpts in the shared test log.

Important APIs: usage `test_run <testname> <cmdline> [--script-args args] [--coverage db]`. It sources `bin/common` for logging functions and uses environment variables such as `TOPDIR`, `LOGFILE`, `COUNTFILE`, and `TIMEFILE`.

Control flow and persistence: parses options, configures Perl Devel::Cover wrapping for `.pl` scripts when coverage is requested, probes GNU `time -v`, announces the test, appends command/output headers to `LOGFILE`, runs the script through `bash -c`, captures pipeline status, parses timing output, scans for unexpected `uninitialized`, records result and metrics to `COUNTFILE`, prints skip reasons or failure excerpts, and exits with the test status.

Dependencies and integration: used by shell-based tests and compatible with `testsuite_init/exit`. Depends on Bash, `time`, `stat`, `tail`, `grep`, and helper functions from `bin/common`.

Risks and test signals: command construction via `bash -c "$INVOKE_COVER $SCRIPT $OPTS"` is quoting-sensitive. Pipeline status handling assumes Bash. The helper itself is validated indirectly by every shell test that uses it.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/test_run -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/test_skip -->
# sources/test-tools/lcov/tests/bin/test_skip

Purpose: Bash helper to mark one test case as skipped and record a reason.

Important APIs: usage `test_skip <testname> <reason>`. It sources `bin/common`, sets `TESTNAME` and `REASON`, calls `t_announce` and `t_skip`, writes the reason to `LOGFILE`, and prints it indented to stdout.

Control flow and state: `TOPDIR` is discovered relative to the script. Empty reason text becomes `<no reason given>`. The script does not explicitly write to `COUNTFILE`; that behavior is likely encapsulated by `t_skip` from `bin/common`.

Dependencies and integration: used by tests that need to skip based on missing tools or unsupported environments. It relies on shell helper functions and shared log variables from `bin/common`.

Risks and test signals: reason text is unescaped shell text but only echoed/logged. If `bin/common` is missing or `TOPDIR` discovery fails, skip reporting fails. Test signal is suite summaries showing skipped counts and reasons.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/test_skip -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/test_worker.py -->
# sources/test-tools/lcov/tests/bin/test_worker.py

Purpose: worker module for `runtests.py`, executing one test in a subprocess with isolated log and optional coverage environment, then returning a structured result.

Important APIs/types: dataclass `TestResult` mirrors fields used by the runner. Function `run_test_worker(test_name, test_path, log_dir, topdir, coverage_dir, script_args, timeout, coverage_mode, debug=False)` is the ThreadPoolExecutor target.

Control flow and persistence: the worker builds a per-test log path, constructs an environment with `TOPDIR`, `TESTDIR`, `LCOV_HOME`, tool paths, lcov convenience variables, info/count paths, and coverage variables. In coverage mode it creates a per-test coverage subdir and wraps `.pl` with Devel::Cover or `.py` with `coverage run`; shell scripts receive `--coverage`. It runs the command with timeout, writes stdout/stderr and final metadata to the log, measures duration and child RSS via `resource`, and returns `TestResult`.

Dependencies and integration: imported by `runtests.py`; depends on external lcov tool binaries, Python coverage, Perl Devel::Cover, and test scripts honoring common environment conventions.

Risks and test signals: shell scripts receive `--coverage` twice in one branch, which may affect scripts with strict parsing. `result` only distinguishes pass/fail; exit code 2 is not treated as skip unlike legacy `test_run`. Resource usage is process-global for children and can be noisy in threaded execution. Tests should cover pass/fail/timeout, coverage wrapping, and skip semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/test_worker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/testsuite_exit -->
# sources/test-tools/lcov/tests/bin/testsuite_exit

Purpose: legacy Bash suite finalizer that aggregates `test.counts`, appends final details to `test.log`, prints a colored summary, and sets the suite exit status.

Important APIs: no arguments. It sources `bin/common`, reads `COUNTFILE`, and uses `t_marker`, `t_detail`, and color variables.

Control flow and persistence: appends `end_time` to `COUNTFILE`, initializes success/failure/skipped/time/memory counters, parses count lines for `start_time`, `end_time`, `pass`, `fail`, `skip`, `elapsed`, and `resident`, redirects stdout/stderr to `LOGFILE` while preserving fd 3 for console summary, writes final log details, prints total/pass/fail/skip plus optional aggregate time/memory, and exits 1 if any failures occurred.

Dependencies and integration: called by shell test flows and by `runtests.py.cleanup()` for compatibility, although the Python runner also writes its own summary.

Risks and test signals: numeric aggregation uses Bash `let` and assumes well-formed count lines. It ignores killed/timeout statuses unless encoded as failures. Test signal is the final suite summary and nonzero exit on failure.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/testsuite_exit -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/testsuite_init -->
# sources/test-tools/lcov/tests/bin/testsuite_init

Purpose: legacy Bash suite initializer that creates the count file, starts the main log, and records tool/system details.

Important APIs: no arguments. It sources `bin/common`, writes `start_time` to `COUNTFILE`, redirects stdout/stderr to `LOGFILE`, and calls helper logging functions.

Control flow and persistence: discovers `TOPDIR`, prints “Starting tests”, initializes `COUNTFILE`, logs timestamp, `lcov --version`, `gcov --version`, and platform-specific CPU/memory information from `/proc`, `sysctl`, `vm_stat`, or fallback text. This prepares the shared files consumed by `test_run` and `testsuite_exit`.

Dependencies and integration: used by legacy shell runner paths and invoked by Python `runtests.py` setup for compatibility. Depends on lcov/gcov on PATH and platform commands.

Risks and test signals: missing `lcov`/`gcov` versions are logged but not explicitly fatal. Large `/proc/cpuinfo` and `/proc/meminfo` dumps can make logs noisy. Test signal is presence of initialized `test.counts` and a header section in `test.log`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/bin/testsuite_init -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/common.mak -->
# sources/test-tools/lcov/tests/common.mak

Purpose: shared Makefile fragment for all LCOV tests. It discovers repository paths, exports common tool commands, prepares generated `.info` fixtures, dispatches tests through `runtests.py`, and defines common cleanup.

Important variables/targets: computes `TOPDIR`, `TESTDIR`, `ROOT_DIR`, `BINDIR`, `SCRIPTDIR`, `TESTBINDIR`, `IS_GIT`, `IS_P4`, `ANNOTATE_SCRIPT`, `VERSION_SCRIPT`, coverage wrappers, fixture paths, `LCOV`, `GENHTML`, `OPTS`, and `TESTS`. Targets include `check`, `checkdeps`, `prepare`, generated `$(INFOFILES) $(COUNTFILES)`, `clean`, `clean_echo`, and `clean_subdirs`.

Control flow and state: included Makefiles define `TESTS`, then `check` calls `$(TOPDIR)/bin/runtests.py $(TESTS) $(OPTS)`. On first include only (`_ONCE` guard), `check` depends on dependency checks and fixture generation through `mkinfo`. Tool paths and language are exported for child tests. Cleanup delegates to `cleantests.py`.

Dependencies and integration: central integration point for lcov binaries, support scripts, Python/Perl coverage, generated fixture data, and subdirectory Makefiles.

Risks and test signals: git/P4 detection controls annotation/version callback selection, so environment changes affect test behavior. The `_ONCE` guard prevents repeated preparation in recursive includes. Makefile variable overrides like `TESTS` are filtered from sub-makes. Main signal is every `make check` under this tree.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/common.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/Makefile -->
# sources/test-tools/lcov/tests/genhtml/Makefile

Purpose: genhtml-specific test suite Makefile that includes common LCOV test infrastructure and enumerates genhtml test scripts.

Important variables/targets: includes `../common.mak`, sets `TESTS := full.sh zero.sh demangle.sh relative lambda exception simple filter function insensitive synthesize errs`, and records disabled legacy scripts in `DISABLED`. Overrides `clean` to remove genhtml local artifacts after common cleanup.

Control flow and persistence: when `make check` runs in this directory, `common.mak` dispatches the listed test scripts/directories through `runtests.py`. `clean` runs common `clean_echo` and `clean_subdirs`, then removes `*.log`, `out_*`, and `*.tmp`.

Dependencies and integration: relies entirely on common variables such as `GENHTML`, fixture info files, test helper binaries, and generated sources. The listed tests exercise genhtml rendering, demangling, relative paths, exception handling, filters, function views, case insensitivity, synthetic source, and error paths.

Risks and test signals: disabled tests are retained as documentation but not executed. The Makefile is intentionally small; failures usually indicate test script behavior or common infrastructure issues rather than this file. Signals are per-test results from the genhtml suite and cleanup artifact removal.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/Makefile -->
