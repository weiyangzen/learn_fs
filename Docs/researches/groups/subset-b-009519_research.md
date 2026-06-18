# subset-b-009519 Research Group

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/testdata/src/lintertest/lintertest.go -->
# sources/test-tools/syzkaller/tools/syz-linter/testdata/src/lintertest/lintertest.go

## Purpose
This file is analyzer testdata for `tools/syz-linter`. It deliberately mixes accepted idioms and lines annotated with `// want "..."` diagnostics so Go analysis tests can verify linter rules against concrete source constructs.

## Important APIs, types, and functions
- Package `lintertest` imports standard packages plus `pkg/tool` only to exercise analyzer recognition of real APIs.
- `stringComparison`, `flagDefinitions`, `logErrorMessages`, `testMessages`, `varDecls`, `minmax`, `loopvar`, `anyInterface`, `contextArgs*`, `sliceClones`, `sortUsage`, `rangeOverIntegers`, `whileStyleLoops`, `mapKeysExtraction`, `stringsCut`, and declaration-spacing examples are fixtures rather than reusable APIs.
- `Foo`, `MissingEmptyLineStruct`, grouped types, and `StructLayout` provide type references for argument grouping and struct literal layout checks.

## Control flow
Execution is unimportant; the linter test runner parses the file and compares emitted diagnostics against `want` comments. Functions include trivial branches, loops, and calls only to trigger AST patterns such as `len(str)==0`, manual min/max updates, duplicated range variables, integer `for` loops, and manual key extraction plus sorting.

## State and persistence behavior
No persistent state is created. Local variables and maps exist only to make syntactically valid examples. The file's durable state is the source text itself: diagnostic comments are the assertion data consumed by analyzer tests.

## Dependencies and integration points
The file integrates with Go analysis test harness conventions where `// want` marks expected messages. Imports of `flag`, `fmt`, `log`, `sort`, `strings`, `testing`, `context`, and `tool` intentionally create call sites for specific syzkaller linter rules.

## Risks and edge cases
Because this is negative testdata, many lines intentionally violate repository style and should not be mechanically formatted into "better" code. Changes to diagnostic wording or Go version idioms can break tests even when behavior is unchanged. Several examples rely on subtle syntactic shape, such as grouped single-line functions, multi-line struct literals, and `sort.Slice` predicate patterns.

## Test signals
Strong direct test signal: each `want` comment states an expected analyzer diagnostic. The file covers both positive and negative cases for comments, logging, flag naming, context argument placement, modern library replacements, declaration spacing, and struct literal layout.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/testdata/src/lintertest/lintertest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-lore/query_lkml.go -->
# sources/test-tools/syzkaller/tools/syz-lore/query_lkml.go

## Purpose
`syz-lore` parses LKML/lore archive directories, extracts syzbot-related email threads, and saves them either as JSON discussion files or through the syzkaller dashboard API.

## Important APIs, types, and functions
- Flags configure own emails/domains, output directory, dashboard endpoint/client/key, and verbose logging.
- `main` validates archive arguments, calls `processArchives`, converts `lore.Thread` objects to `dashapi.Discussion`, and persists each discussion.
- `saveDiscussion` lazily creates a global `dashapi.Dashboard`, writes JSON files named by `hash.String(d.ID)`, and/or calls `Dashboard.SaveDiscussion`.
- `processArchives` concurrently reads LKML repositories through `vcs.NewLKMLRepo` and `lore.ReadArchive`, parses messages with `lore.Parse`, groups them with `lore.Threads`, and filters to threads with syzbot bug IDs.

## Control flow
Archive paths are read by errgroup jobs that enqueue `lore.EmailReader` values on a channel. A worker pool sized to `runtime.NumCPU()` consumes that channel, reads raw messages, parses them, strips body/patch payloads, and appends metadata under a mutex. After archive readers finish, the channel closes, parsing errors are counted and skipped, and grouped threads are filtered before returning.

## State and persistence behavior
State is mostly in memory: `repoEmails`, skipped parse count, and the global dashboard client. Persistent side effects are JSON discussion files under `-out_dir` and remote dashboard writes when dashboard flags are set. Email body and patch content are cleared before storing to reduce output size and sensitivity.

## Dependencies and integration points
The tool depends on `pkg/email/lore` for archive parsing/threading, `pkg/vcs` for LKML archive access, `dashboard/dashapi` for persistence, `pkg/hash` for stable filenames, and `pkg/tool` for initialization/fatal errors. It integrates with syzbot dashboard discussion ingestion.

## Risks and edge cases
The goroutine closure over `path` relies on Go range semantics; older Go versions would risk capturing the wrong path. `strings.Split("", ",")` yields a single empty string for unset email/domain flags, so downstream parsing must tolerate empty identifiers. Broken LKML messages are silently skipped except for a count, which is pragmatic but can hide archive quality regressions. Dashboard and JSON writes are sequential after concurrent parsing.

## Test signals
No local tests in this file. Behavioral confidence comes from `lore` and `dashapi` package tests and from manual runs over real archives. Useful test cases would include malformed email handling, filtering threads without bug IDs, JSON output naming, and simultaneous dashboard plus local output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-lore/query_lkml.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-make/make.go -->
# sources/test-tools/syzkaller/tools/syz-make/make.go

## Purpose
`syz-make` prints shell `export` assignments used by syzkaller Makefiles to derive native/cross build variables and a conservative parallelism setting.

## Important APIs, types, and functions
- `main` calls `impl`, prints `SYZERROR` and exits nonzero on failure, otherwise emits each `Var` as `export NAME=value\n`.
- `Var` is the simple name/value output model.
- `impl` resolves `HOSTOS`, `HOSTARCH`, `TARGETOS`, `TARGETARCH`, and `TARGETVMARCH` from environment variables with runtime fallbacks, validates `targets.Get`, and derives compiler/linker flags from `sys/targets`.
- `or` is the environment fallback helper.

## Control flow
The tool computes host/target defaults, looks up target metadata, starts parallelism at CPU count, then reduces it for CI, OpenBSD, and low-memory hosts. The memory limiter keeps `NCORES*NCORES <= memoryGiB` to account for nested Make and Go build parallelism.

## State and persistence behavior
No files are read or written. Output is stdout shell text intended to be evaluated by Make/shell. The only process state read is environment variables, OS/architecture, CPU count, and memory size.

## Dependencies and integration points
`pkg/osutil.SystemMemorySize` supplies RAM size. `sys/targets` supplies compiler names, flags, executable suffixes, broken compiler markers, and build OS. The Makefile consumes the emitted variables.

## Risks and edge cases
Values are printed without shell escaping, so target metadata and environment-derived values are expected to be safe tokens. `NATIVEBUILDOS` is emitted twice with the same value. If system memory cannot be determined, CPU parallelism may still be too aggressive on memory-constrained systems. CI and OpenBSD intentionally force single Make parallelism.

## Test signals
No direct tests here. Good validation includes running under representative env var combinations, unknown target pairs, CI/OpenBSD paths, and low-memory hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-make/make.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-minconfig/minconfig.go -->
# sources/test-tools/syzkaller/tools/syz-minconfig/minconfig.go

## Purpose
`syz-minconfig` is a manual helper for checking kernel config minimization. It minimizes a full config relative to a base config while preserving a predicate that specified config symbols remain enabled.

## Important APIs, types, and functions
- Flags specify kernel source directory, base config, full config, comma-separated config symbols, and target arch.
- `main` parses Linux Kconfig with `kconfig.Parse`, loads base/full configs with `kconfig.ParseConfig`, defines the predicate, creates a `debugtracer.GenericTracer`, runs `kconf.Minimize`, and writes the serialized minimized config.

## Control flow
After argument parsing, the tool loads the target Kconfig tree from `<sourcedir>/Kconfig`. The predicate iterates `strings.SplitSeq(*flagConfigs, ",")` and returns false if any requested symbol is `kconfig.No`. `Minimize` drives the search and logs trace output to stdout before the final serialized config is also written to stdout.

## State and persistence behavior
The tool reads Kconfig and config files. It writes only stdout and has no persistent output file flag. The minimization predicate is stateless apart from requested config symbol names.

## Dependencies and integration points
It integrates with `pkg/kconfig` minimization logic, `pkg/debugtracer` for trace logging, `pkg/tool` for failures, and `sys/targets` for Linux target metadata.

## Risks and edge cases
No explicit flag validation means empty paths or unknown architecture can fail inside `kconfig.Parse`. Trace and final config share stdout, which is useful manually but awkward for scripts that expect only config content. Empty config names from a trailing comma are not filtered.

## Test signals
No direct tests. The underlying minimizer should be covered in `pkg/kconfig`; this wrapper is best tested with a tiny synthetic Kconfig tree and known base/full configs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-minconfig/minconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-mutate/mutate.go -->
# sources/test-tools/syzkaller/tools/syz-mutate/mutate.go

## Purpose
`syz-mutate` generates a random syzkaller program or mutates an input program, optionally using comparison hints for a specific call.

## Important APIs, types, and functions
- Flags select OS/arch, seed, target program length, enabled syscall list, corpus file, hint call/src/cmp values, and strict deserialization.
- `main` loads the `prog.Target`, resolves enabled syscalls with `mgrconfig.ParseEnabledSyscalls`, reads corpus with `db.ReadCorpus`, builds a choice table, and either `Generate`s or mutates a `prog.Prog`.
- Hint mode builds a `prog.CompMap` and uses `Prog.MutateWithHints` to print every hinted mutation.

## Control flow
If `-enable` is set, syscall names are parsed and transitive requirements are applied through `target.TransitivelyEnabledCalls`, with disabled calls logged to stderr. Seed defaults to current nanoseconds unless specified. With no positional argument, a fresh program is generated. With an input file, it is deserialized under strict or non-strict mode, then either hint-mutated or generally mutated.

## State and persistence behavior
The tool reads an optional corpus DB and optional input program. It writes generated programs to stdout and diagnostics to stderr. No files are modified.

## Dependencies and integration points
It uses `prog` core generation/mutation APIs, `pkg/db` corpus loading, `pkg/mgrconfig` syscall selection, and the blank `sys` import to register target descriptions.

## Risks and edge cases
Randomness is reproducible only when `-seed` is specified. Empty corpus path behavior depends on `db.ReadCorpus`. Hint mode prints multiple programs and returns without printing the final original/mutated program. Type correctness and call availability are delegated to `prog` APIs.

## Test signals
No direct tests. Useful checks are fixed-seed golden generation, strict vs non-strict parse failures, enabled syscall filtering, and hint mutation output count/shape.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-mutate/mutate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-old-env -->
# sources/test-tools/syzkaller/tools/syz-old-env

## Purpose
`syz-old-env` is a Bash wrapper for running syzkaller development commands inside the older `gcr.io/syzkaller/old-env` Docker image, or a locally built equivalent when `SYZ_ENV_BUILD` is set.

## Important APIs, types, and functions
- It builds `COMMAND`, `BUILDARGS`, and `DOCKERARGS` from proxy environment variables, command arguments, CI mode, rootless Docker detection, and `SOURCEDIR=...` rewrites.
- `SCRIPT_DIR` locates the syzkaller checkout relative to the script.
- It selects image `old-env` when invoked as `syz-old-env`, otherwise `env`, sharing implementation with the newer wrapper naming.

## Control flow
The script translates each CLI argument into a container command. `SOURCEDIR=/path` is special-cased into a bind mount at `/syzkaller/kernel` plus a rewritten command argument. Non-CI runs add `-it`. It then builds or pulls the image and runs Docker with syzkaller source, cache, Docker socket, Go env, CI/GitHub env, and user mapping.

## State and persistence behavior
It can pull or build Docker images, mount the host syzkaller tree read/write, mount `$HOME/.cache`, mount the Docker socket, and run commands that create files as the host user when possible. It does not persist wrapper-local state.

## Dependencies and integration points
Requires Docker, the syzkaller Docker image definitions under `tools/docker`, and host permissions for Docker. It is intended to wrap Make targets such as format, presubmit, and extract.

## Risks and edge cases
The `[ -n $http_proxy ]` style tests are unquoted and can misbehave for unset or whitespace-containing values. Array-like expansions use variables initialized as strings, relying on Bash behavior. Passing the Docker socket into the container is powerful and should be treated as host-level access. Rootless detection controls file ownership behavior.

## Test signals
No automated tests. Manual validation should cover rootless and rootful Docker, CI vs interactive mode, proxy propagation, `SOURCEDIR` mounting, and local image build mode.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-old-env -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-prog2c/prog2c.go -->
# sources/test-tools/syzkaller/tools/syz-prog2c/prog2c.go

## Purpose
`syz-prog2c` converts a serialized syzkaller program into generated C source, optionally builds it, and supports toggling csource execution features.

## Important APIs, types, and functions
- Flags select target OS/arch, input `-prog`, build mode, threading/repetition/process count/slowdown, sandbox settings, segv/tmpdir/trace/leak, feature enable/disable flags, strict parsing, and optional `vmlinux` for kfuzztest dynamic targets.
- `main` parses feature flags with `csource.ParseFeaturesFlags`, loads target metadata, optionally activates kfuzz targets, deserializes the program, creates `csource.Options`, calls `csource.Write` and `csource.Format`, writes source to stdout, and optionally calls `csource.Build`.

## Control flow
The tool requires `-prog`; usage also prints available feature flags. Program parsing defaults to non-strict unless `-strict` is set. Feature booleans from `ParseFeaturesFlags` are mapped field-by-field into `csource.Options`, with `CallComments` always true. Build mode creates a temporary binary through `csource.Build`, removes it, and reports success on stderr.

## State and persistence behavior
It reads the input program and optional vmlinux. It writes C source to stdout. In build mode it creates and removes a binary from the csource build path. It otherwise has no persistent state.

## Dependencies and integration points
Integrates `prog` serialization, `pkg/csource` C emission/building, `pkg/kfuzztest` dynamic target activation, and blank `sys` imports for target registration. Generated C is used for standalone reproducer workflows.

## Risks and edge cases
Feature flag names must match `csource` feature keys; missing or renamed features would panic through map access only if absent entries are not returned. Build success depends on host compiler/toolchain and target support. Non-strict parsing is permissive by default, which helps old programs but can hide malformed input.

## Test signals
No direct tests. Existing csource/prog tests cover most behavior. Wrapper tests should verify required `-prog`, strict parse failures, feature mapping, kfuzz activation failures, and build cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-prog2c/prog2c.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-query-subsystems/generator.go -->
# sources/test-tools/syzkaller/tools/syz-query-subsystems/generator.go

## Purpose
This file renders a queried subsystem hierarchy into a generated Go source file under `pkg/subsystem/lists`, preserving subsystem metadata and parent relationships in code.

## Important APIs, types, and functions
- `generateSubsystemsFile` assigns stable variable names, builds `templateVars`, serializes supported fields, includes commit/version/debug parent comments, executes `fileTemplate`, and formats the result with `go/format`.
- `getVarName` lowercases names, removes non-word and leading non-alphanumeric runs via `makeVarRegexp`, and prefixes identifiers that start with digits.
- `hierarchyList` builds a parent-to-children map and emits indented comment lines for roots and descendants.
- Template types `templateSubsystem`, `parentInfo`, and `templateVars` define the rendering model.

## Control flow
The generator first maps every `*subsystem.Subsystem` pointer to a variable name so parent references can point to variables instead of serialized nested structs. It then iterates the list, sorts parent references by generated name, conditionally includes non-empty lists/maintainers/syscalls and booleans, and emits initialization code that registers the generated list with a date-based version.

## State and persistence behavior
The function itself is pure aside from deterministic formatting and sorting mutations of `entry.Maintainers` in place. It returns generated bytes; writing to disk is handled by `query_subsystems.go`.

## Dependencies and integration points
Uses `pkg/serializer` to produce Go literals, `pkg/subsystem` data structures, and `pkg/vcs.Commit` metadata. The generated file calls `RegisterList` in package `lists` and imports `pkg/subsystem` with a dot import.

## Risks and edge cases
Generated variable names are not checked for duplicates, so similarly normalized subsystem names could produce invalid or ambiguous code. The hierarchy walk has no cycle guard; it assumes upstream subsystem parent data is acyclic. `debugInfo.ParentChildComment[p][entry]` assumes debug maps are populated. Sorting maintainers mutates input objects.

## Test signals
No direct tests. Effective tests would feed synthetic subsystem graphs with parents, duplicate-normalized names, numeric names, maintainer/list toggles, and compare formatted output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-query-subsystems/generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-query-subsystems/query_subsystems.go -->
# sources/test-tools/syzkaller/tools/syz-query-subsystems/query_subsystems.go

## Purpose
`syz-query-subsystems` queries Linux subsystem definitions from a kernel repository and saves them as a generated syzkaller subsystem list in another syzkaller checkout.

## Important APIs, types, and functions
- Flags specify OS, kernel repo, syzkaller repo, list name, optional subsystem filter, email/list inclusion, and debug output.
- `main` validates inputs, calls `linux.ListFromRepo`, optionally prints debug info, post-processes the list, creates `pkg/subsystem/lists`, gets kernel HEAD commit metadata, generates code, and writes `<name>.go`.
- `printDebugInfo`, `postProcessList`, `prepareFilter`, and `determineCommitInfo` support debug, filtering, email stripping, and VCS metadata.

## Control flow
Only Linux is accepted. Repository paths and generated list names are validated before expensive querying. Filtering is exact by subsystem `Name`, then `-emails=false` clears maintainer/list fields from every item. Commit info is fetched with `vcs.NewRepo(... OptPrecious, OptDontSandbox)` and `repo.Commit(vcs.HEAD)`.

## State and persistence behavior
Reads kernel and syzkaller repositories. Writes one generated Go file under the target syzkaller repository. Does not alter the kernel repository beyond VCS inspection; `OptPrecious` and `OptDontSandbox` indicate careful direct repo handling.

## Dependencies and integration points
Depends on `pkg/subsystem/linux` for Linux extraction, `pkg/subsystem` filtering, `pkg/vcs` for commit metadata, and the local generator in `generator.go`. Integrates with syzkaller's `pkg/subsystem/lists` registry.

## Risks and edge cases
The exact-name filter does not trim subsystem names from the data side. Invalid regex strings in skip logic do not apply here, but invalid list names fail early. Current implementation supports only Linux; other OS values are hard failures. Generated output can fail if generator creates duplicate identifiers.

## Test signals
No direct tests. Useful coverage includes validation failures, filter behavior, email stripping, debug printing, and generated file path/content checks against a small fake repo abstraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-query-subsystems/query_subsystems.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-reporter/reporter.go -->
# sources/test-tools/syzkaller/tools/syz-reporter/reporter.go

## Purpose
`syz-reporter` builds an HTML crash summary for a syzkaller manager workdir and opens it in a browser. It is intended for inspecting crash/reproducer results, especially after `syz-crush` style runs.

## Important APIs, types, and functions
- `UISummaryData`, `UICrashType`, and `UICrash` are template view models.
- `main` loads a manager config, creates a temporary HTML filename, renders `httpSummary`, writes it, and starts `xdg-open`.
- `httpSummary` collects crashes, counts crash types and crash types with reproducers, and executes `summaryTemplate`.
- `collectCrashes` lists `workdir/crashes`, calls `readCrash`, and sorts by lowercase description.
- `readCrash` reads crash metadata including description, log indices, tags/prog reproducers, cause/fix commits, and cause config data.
- `trimNewLines` removes trailing newline bytes.

## Control flow
The crash directory is scanned by 40-character crash IDs. Each crash type's description is required; missing/empty descriptions skip the entry. File names drive classification: `logN` adds a crash record, `tag*` and `*prog` add reproducers, `cause.commit`, `fix.commit`, and `kconfig.CauseConfigFile` populate metadata. The template renders sortable columns.

## State and persistence behavior
Reads manager config and workdir crash files. Writes a temporary `.html` file and launches a browser. It does not modify crash data. The temporary file is not removed by the process after opening.

## Dependencies and integration points
Uses `pkg/mgrconfig`, `pkg/osutil`, `pkg/kconfig`, and `pkg/html/pages`. It expects the manager crash store on disk but does not reuse `manager.CrashStore` yet.

## Risks and edge cases
In `main`, `if httpSummary(buf, cfg) != nil { log.Fatalf("%v", err) }` logs the wrong `err` variable instead of the render error. Crash log contents are not loaded into `UICrash` despite fields existing. Reproducer map iteration order is nondeterministic in the template. Cause config lists longer than ten are collapsed to `...`.

## Test signals
No direct tests. Good tests would construct temporary crash directories and assert rendered counts, metadata extraction, sorting, malformed ID skipping, and the error variable bug.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-reporter/reporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-repro/repro.go -->
# sources/test-tools/syzkaller/tools/syz-repro/repro.go

## Purpose
`syz-repro` runs syzkaller's reproduction pipeline against an execution log using a manager configuration and VM pool, writing found syz/C reproducers and optional title/strace artifacts.

## Important APIs, types, and functions
- Flags configure manager config, VM count override, debug VM output, syz repro path, C repro path, title path, and strace output path.
- `main` loads config/log data, creates VM pool and reporter, reserves dispatcher instances, runs `repro.Run`, prints timings and results, writes outputs, optionally runs strace, and drives `pool.Loop`.
- `recordTitle`, `recordCRepro`, and `recordStraceResult` persist specific result artifacts.

## Control flow
The tool prepends `-vv=10` to args before flag parsing for verbose logging. Reproduction runs in a goroutine with a cancelable context; the VM dispatcher loop runs on the main goroutine until the reproduction completes and cancels context. If a result exists, the serialized syz program is printed and written. C generation uses `csource.Write` and formatting. Strace mode invokes `repro.RunStrace` on the resulting repro.

## State and persistence behavior
Reads manager config and execution log. Uses external VMs through `vm.Create`/dispatcher. Writes repro program, C repro, title, and strace output files depending on flags and result. Handles interrupts by shutting down VM infrastructure.

## Dependencies and integration points
Integrates `pkg/repro`, `pkg/report`, `pkg/mgrconfig`, `pkg/flatrpc` feature flags, `pkg/csource`, `vm` pools, and `pkg/osutil`. Used both standalone and by `syz-testbed` repro benchmarking.

## Risks and edge cases
The default output files in the current directory may be overwritten. The strace result success message says "C file saved" even for strace output. A nil result silently produces no artifact beyond failure logs. VM count override can exceed practical host capacity if misused. The dispatcher/cancel flow relies on `repro.Run` returning and deferring `done()`.

## Test signals
No direct tests in this file. Most logic depends on integration tests around `pkg/repro` and VM backends. Wrapper tests can cover argument validation and artifact writers with fake results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-repro/repro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-reproducers.sh -->
# sources/test-tools/syzkaller/tools/syz-reproducers.sh

## Purpose
This Bash helper downloads exported C reproducers from syzkaller storage, extracts them, compiles them in parallel, and reports how many built successfully.

## Important APIs, types, and functions
- The script accepts one required target directory argument.
- It uses `wget`, `tar`, `find`, `xargs`, `grep`, `gcc`, and `wc`.
- The compile pipeline checks each `.c` file for `__NR_mmap2` and adds `-m32` when present, then builds statically with pthreads into `<target>/bin/<filename>`.

## Control flow
The script validates the target directory argument, creates it, downloads `upstream.tar.gz`, extracts and removes the archive, creates `bin`, compiles all `export/bugs/**/*.c` files with `xargs -P 128`, counts successful compilations by echoing `1`, counts total reproducers, and prints both totals.

## State and persistence behavior
Creates or reuses the target directory, downloads a remote archive, extracts an `export` tree, creates `bin`, and writes compiled binaries. It removes only the downloaded archive, not extracted sources or binaries.

## Dependencies and integration points
Depends on syz-db-export artifact layout and public Google Cloud Storage. Integrates with local C toolchains and can be used to prepare a corpus of standalone reproducer binaries.

## Risks and edge cases
No `set -euo pipefail`, so partial failures can continue. Parallelism is hard-coded to 128 and may overwhelm hosts. `grep "__NR_mmap2"` may print matched lines into build logs unless quiet mode is used. Static `-m32` builds require 32-bit libraries/toolchain support. File basenames may collide across directories.

## Test signals
No tests. Manual validation should cover download failure, extraction failure, no `.c` files, compile failures, 32-bit reproducers, and duplicate basenames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-reproducers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-showprio/showprio.go -->
# sources/test-tools/syzkaller/tools/syz-showprio/showprio.go

## Purpose
`syz-showprio` prints a table of syzkaller call-to-call priority values for a specified set of enabled syscalls.

## Important APIs, types, and functions
- Flags select OS/arch, comma-separated enabled calls, and optional corpus file.
- `main` loads target metadata, validates enabled syscalls through `mgrconfig.ParseEnabledSyscalls`, reads corpus, computes priorities with `target.CalculatePriorities`, and calls `showPriorities`.
- `showPriorities` indexes the priority matrix by syscall IDs and prints rows/columns for the requested call names.
- `printLine` prints fixed-width pipe-delimited cells.

## Control flow
The tool fails if `-enable` is empty or invalid. It does not use the parsed syscall IDs directly; it relies on the original names to index `target.SyscallMap`. Corpus-derived priorities are computed for the whole target, then a selected submatrix is printed.

## State and persistence behavior
Reads an optional corpus DB and writes only stdout/stderr. No persistent files are modified.

## Dependencies and integration points
Uses `prog` target priority calculation, `pkg/db` corpus loading, and `pkg/mgrconfig` syscall validation. It is a diagnostic companion for fuzzing choice table behavior.

## Risks and edge cases
Aliases or patterns accepted by `ParseEnabledSyscalls` may not be valid direct keys in `target.SyscallMap`, since `showPriorities` uses the raw `enabled` strings. Empty corpus behavior depends on `db.ReadCorpus`. Output is human-readable rather than CSV/TSV.

## Test signals
No direct tests. Tests should validate a small known target/corpus matrix, invalid syscall names, and behavior with syscall aliases/patterns.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-showprio/showprio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-symbolize/symbolize.go -->
# sources/test-tools/syzkaller/tools/syz-symbolize/symbolize.go

## Purpose
`syz-symbolize` symbolizes kernel crash logs and can save parsed crashes in syzkaller crash-store format.

## Important APIs, types, and functions
- Flags configure target OS/arch, kernel object/source directories, output crash directory, or a partial manager config.
- `main` builds/loads a partial manager config, completes kernel dirs, creates a `report.Reporter`, reads the input log, parses all reports, symbolizes them, prints metadata and reports, and optionally calls `saveCrash`.
- `saveCrash` hashes the report title to create a crash directory and writes `description`, `log`, and optional `report` files.

## Control flow
If `report.ParseAll` finds no structured reports, the whole input is wrapped in `report.Report` and symbolized in place, then printed. Otherwise each parsed report can be saved before symbolization, then symbolized and printed with title, corruption/suppression status, and maintainer recipients.

## State and persistence behavior
Reads config or flag-derived kernel paths and one log file. Writes symbolized output to stdout. With `-outdir`, creates crash directories and files named by title hash.

## Dependencies and integration points
Integrates with `pkg/report` parsing/symbolization, `pkg/mgrconfig` partial config loading, `pkg/vcs` maintainer recipient formatting, and `pkg/hash`/`pkg/osutil` for crash persistence.

## Risks and edge cases
Saving occurs before symbolization, so saved `report` content may be unsymbolized while stdout is symbolized. Hashing only the title groups same-title crashes. If no report is parsed, `-outdir` is ignored. Maintainer extraction depends on reporter/kernel source availability.

## Test signals
No direct tests here. Useful cases include no parsed report fallback, multiple reports in one log, outdir crash-store layout, config vs flag path config, and symbolization failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-symbolize/symbolize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/checkout.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/checkout.go

## Purpose
This file models a checked-out syzkaller variant in `syz-testbed`, tracks its running/completed instances, lazily creates its crash reporter, and performs initial repository checkout/build.

## Important APIs, types, and functions
- `Checkout` holds path/name, manager config JSON, running instance map, completed results, last run timestamp, cached reporter, and mutex.
- `GetReporter` parses partial manager config and lazily constructs `report.Reporter`.
- `AddRunning`, `ArchiveInstance`, `GetRunningResults`, and `GetCompletedResults` synchronize access to instance/result state.
- `TestbedContext.NewCheckout` creates a checkout directory, polls a syzkaller repo/branch, and builds binaries with `syz_instance.MakeBin`.

## Control flow
New checkout creation refuses to reuse an existing path, checks out the configured repo/branch via `vcs.NewSyzkallerRepo(...).Poll`, then runs the syzkaller build with a one-hour timeout. Instance lifecycle methods update `Running` and `Completed` under lock; archiving fetches the instance result before removing it from `Running`.

## State and persistence behavior
Persistent side effects include creating `workdir/checkouts/<name>`, cloning/updating source, and building binaries. Runtime state is held in memory and guarded by `Checkout.mu`. Completed results are not restored from disk on restart.

## Dependencies and integration points
Uses `pkg/vcs`, `pkg/instance.MakeBin`, `pkg/mgrconfig`, `pkg/report`, `pkg/osutil`, and local `Instance`/`RunResult` abstractions. `SyzReproInput.QueryTitle` depends on `GetReporter`.

## Risks and edge cases
Existing checkout paths are fatal to a new testbed run, so restart/resume is not supported. `GetRunningResults` ignores fetch errors, which avoids transient failures but can hide broken instances in live stats. Lazy reporter creation calls `tool.Failf`, terminating the process from a getter on config/report errors.

## Test signals
No direct tests. Tests should cover state transitions, result cloning, existing path refusal, build failure propagation, and reporter caching.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/checkout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/html.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/html.go

## Purpose
This file implements the live HTTP dashboard for `syz-testbed`, rendering summary/stat tables and graph images from current testbed state.

## Important APIs, types, and functions
- `setupHTTPServer` installs handlers for `/`, `/graph`, and `/favicon.ico` and serves with gzip compression.
- `getCurrentStatView` selects requested, first non-empty, or first available stat view.
- `httpGraph` materializes averaged bench files, invokes external `syz-benchcmp`, and writes generated graph output.
- UI structs `uiTable`, `uiTableType`, `uiStatView`, and `uiMainPage` carry data to templates.
- `getTableTypes`, `genSimpleTableController`, `httpMainStatsTable`, `httpMain`, and `executeTemplate` generate table views.
- Embedded templates are loaded from `templates/*.html` through `pages.CreateFromFS`.

## Control flow
The main page selects an active view and table type from query parameters, builds URL callbacks for table/view navigation, generates the active table, and executes `testbed.html`. Stats table links can set `base_column` and `align` parameters, causing `Table.SetRelativeValues` and aligned stats generation. Graph requests create temp dirs/files, save average benches, run `benchcmp -all -over ... -out ...`, and stream the output.

## State and persistence behavior
The server reads live in-memory checkout state via `GetStatViews`. Graph requests create temporary files/directories and remove them with defers. No persistent dashboard state is stored by this file.

## Dependencies and integration points
Uses Go `net/http`, embedded templates, `gorilla/handlers` compression, `pkg/html/pages`, `pkg/osutil`, and local stats/table generation. Depends on `ctx.Target.SupportsHTMLView` to present target-appropriate tables.

## Risks and edge cases
`setupHTTPServer` is always called even if `ctx.Config.HTTP` is empty; listen behavior depends on config validation/defaults. In `httpMain`, an unknown table key writes `fmt.Sprintf("%s", err)` where `err` may be nil, producing a confusing response. `httpGraph` shells out to an external benchcmp path for every request and can be expensive. Template map iteration can make table-type link order nondeterministic.

## Test signals
No direct tests. Useful tests include view/table query selection, invalid view/table handling, relative-value links, graph failure paths, and template execution over empty/non-empty stats.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/html.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/instance.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/instance.go

## Purpose
This file defines executable testbed instances and the concrete `syz-manager`/`syz-repro` instance setup, execution, stopping, and result extraction logic.

## Important APIs, types, and functions
- `Instance` interface requires `Run`, `Stop`, `FetchResult`, and `Uptime`.
- `InstanceCommon` stores process command, args, log path, start/stop timestamps, and stop channel; its `Run`, `Stop`, and `Uptime` implement shared process lifecycle behavior.
- `SyzManagerInstance` embeds `InstanceCommon`/`SyzkallerInfo`, adds runtime, and fetches bug/bench results.
- `SetupSyzkallerInstance` creates workdir/config/bench paths and patches manager config JSON.
- `SyzManagerTarget.newSyzManagerInstance` creates a configured `syz-manager` run folder and command.
- `SyzReproInstance` and `SyzReproTarget.newSyzReproInstance` copy an execution log and run `syz-repro` with output/title paths.

## Control flow
`InstanceCommon.Run` creates a gracious command, redirects stdout/stderr to a log file if configured, starts the process, and waits for completion or stop signal. Stop sends interrupt, waits up to one minute, then kills. Manager instances wrap common run with a `time.After(RunTime)` timeout. Repro instances run until `syz-repro` exits and derive success from produced files and title matching.

## State and persistence behavior
Each instance creates a `run-<uniq>` folder under a checkout, with workdir, manager config, bench file, log, and repro-specific artifacts. Runtime timestamps are in memory. `FetchResult` reads crash stores, bench files, and output files to produce result structs.

## Dependencies and integration points
Uses `pkg/config` for JSON patching, `pkg/osutil` for process/file helpers, local `collectBugs`/`readBenches`, and built syzkaller binaries in each checkout. It is invoked by target strategies in `targets.go` and slots in `testbed.go`.

## Risks and edge cases
`cmd.Start()` error is ignored before `cmd.Wait`, which can make startup failures less clear. Log files are created but not explicitly closed in `Run`. `SyzReproInstance.FetchResult` treats a different reproduced title as failure, which is correct for benchmarking but can discard evidence of another bug. Manager run timeout uses `time.After`, so very long runtimes allocate a timer per instance.

## Test signals
No direct tests. Good tests would fake commands to cover graceful stop, kill-after-timeout, log creation failures, title mismatch, and generated manager/repro config paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/instance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/stats.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/stats.go

## Purpose
This file defines result models and table/bench generation for `syz-testbed` manager and repro experiments.

## Important APIs, types, and functions
- Data types: `BugInfo`, `RunResult`, `SyzManagerResult`, `SyzReproResult`, `StatRecord`, `RunResultGroup`, and `StatView`.
- Collection helpers: `collectBugs`, `readBenches`, and `groupSamples`.
- Bug summaries/tables: `summarizeBugs`, `GenerateBugTable`, `GenerateBugCountsTable`.
- Type filters: `SyzManagerResults`, `SyzReproResults`.
- Stat alignment/averaging: `AvgStatRecords`, `minResultLength`, `groupNthRecord`, `groupLastRecord`, `StatsTable`, `AlignedStatsTable`, `InstanceStatsTable`.
- Repro tables: `GenerateReproSuccessTable`, `GenerateCReproSuccessTable`, `GenerateReproDurationTable`, `GenerateReproAttemptsTable`.
- Persistence helpers: `SaveAvgBenchFile`, `SaveAvgBenches`, `IsEmpty`.

## Control flow
Manager stats collect crash titles/log paths and JSON bench records. Group-level methods filter result unions by concrete result type. For aligned stats, each group contributes the latest sample at or above the minimum common value of an alignment field, usually uptime. Repro tables aggregate by input title, counting success ratios, C repro ratios, durations, or every attempt row.

## State and persistence behavior
Reads crash stores and bench files. Writes averaged bench files under caller-provided directories. All summary tables are in-memory until saved by target or HTTP code.

## Dependencies and integration points
Uses `pkg/manager.ReadCrashStore` for bug lists and `pkg/stat/sample` for median, outlier removal, and statistical samples. Tables are consumed by `targets.go`, `html.go`, and CSV persistence.

## Risks and edge cases
`readBenches` ignores JSON decode errors inside the stream, potentially hiding corrupt records. `minResultLength` assumes there is at least one manager result when `len(group.Results) > 0`; mixed or repro-only groups can panic if used with manager stats. `GenerateBugCountsTable` divides by `len(group.Results)` for found bugs, but empty groups do not set cells. The duration table comment incorrectly mentions C repro share.

## Test signals
No direct tests in this file. It has indirect coverage from table tests only. High-value tests would cover malformed bench JSON, mixed result groups, stat alignment missing fields, repro aggregation, and bench downsampling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/table.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/table.go

## Purpose
This file provides the generic named-row/named-column table abstraction used by `syz-testbed` CSV and HTML reports, plus cell types for values, ratios, and booleans.

## Important APIs, types, and functions
- `Table` stores top-left header, ordered column headers, and a row/column cell map.
- `ValueCell` wraps a statistical sample, median value, optional percent change, and optional p-value.
- `RatioCell` and `BoolCell` provide displayable aggregate cells.
- Core methods include `NewTable`, `Get`, `Set`, `AddColumn`, `AddRow`, `SortedRows`, `ToStrings`, `SaveAsCsv`, `SetRelativeValues`, and `GetFooterValue`.

## Control flow
Tables preserve column insertion order while rows are sorted alphabetically on rendering. `SetRelativeValues` iterates rows, finds a base `ValueCell`, computes percent changes for other `ValueCell`s, removes outliers, and tries a U-test for p-values. Footer generation computes averages for homogeneous ratio/value columns or yes counts for boolean columns.

## State and persistence behavior
The table is in-memory until `SaveAsCsv` creates/truncates a CSV file. `SetRelativeValues` mutates existing `ValueCell` objects by filling `PercentChange` and `PValue` pointers.

## Dependencies and integration points
Uses `pkg/stat/sample` for medians, outlier removal, and U-test; `golang.org/x/exp/maps` plus `slices` for row sorting. HTML templates call table methods directly.

## Risks and edge cases
`AddRow` panics on length mismatch, which is acceptable for internal construction but not user input. `SortedRows` calls `maps.Keys(t.Cells)` and may need nil handling depending on library behavior, though `ToStrings` checks nil before calling it. `GetFooterValue` divides value averages by a count that is incremented as float; it returns a ratio over `len(t.Cells)` for bools, including rows with nil cells if any slipped through the homogeneous case.

## Test signals
`table_test.go` directly tests `SetRelativeValues` for a base column, percent change, nil base cells, and unchanged base cell extras. Additional tests should cover footer values, CSV output ordering, AddRow panic, and mixed cell columns.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/table_test.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/table_test.go

## Purpose
This file tests relative value calculation for the `Table` abstraction used in syz-testbed stats displays.

## Important APIs, types, and functions
- `TestRelativeValues` constructs a two-column table with `ValueCell`s backed by `sample.Sample`, calls `SetRelativeValues("A")`, and asserts computed/omitted percent changes.
- Uses `testify/assert` for no-error and delta/nil assertions.

## Control flow
The test creates row1 with base A=2 and comparison B=3, row2 with only B=1, then verifies B in row1 receives about +50%, A receives no percent change, missing row2/A remains nil, and row2/B does not get a percent change because the base column is missing.

## State and persistence behavior
No files or persistent state. It mutates the in-memory table as production code would.

## Dependencies and integration points
Depends on local `NewTable`, `NewValueCell`, and `SetRelativeValues`, plus `pkg/stat/sample`. It is the direct regression test for the relative comparison behavior used by the HTML stats table.

## Risks and edge cases
Coverage is narrow: it does not assert p-values, wrong base cell types, outlier removal, zero base values, CSV rendering, footer aggregation, or panic behavior.

## Test signals
Strong for the basic percent-change path and missing-base guard. Remaining table behavior still needs separate coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/targets.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/targets.go

## Purpose
This file defines `syz-testbed` target strategies for benchmarking `syz-manager` performance and `syz-repro` reproduction success.

## Important APIs, types, and functions
- `TestbedTarget` interface abstracts job creation, stat persistence, and supported HTML tables.
- `targetConstructors` builds either `SyzManagerTarget` or `SyzReproTarget` from config.
- `SyzManagerTarget.NewJob`, `SupportsHTMLView`, and `SaveStatView` implement round-robin manager benchmarking and CSV/bench output.
- `SyzReproTarget`, `SyzReproInput`, `QueryTitle`, `NewJob`, `SupportsHTMLView`, and `SaveStatView` implement crash-log selection and repro benchmarking.

## Control flow
Manager jobs choose checkouts round-robin and assign monotonically increasing instance IDs. Repro target construction collects input logs either by walking a directory or sampling crash logs from a workdir while honoring skip regexps and `CrashesPerBug`. Repro jobs choose checkouts round-robin, lazily parse input titles per checkout, skip unparsable logs, and choose the least-run available input for that checkout.

## State and persistence behavior
Targets keep in-memory counters, input run counts, skip flags, and duplicate-title map under mutexes. `SaveStatView` writes target-specific CSV files and averaged bench files under caller-provided stats directories.

## Dependencies and integration points
Uses local instance constructors, stats/table methods, `collectBugs`, `pkg/osutil`, and `pkg/tool`. Repro inputs depend on checkout-specific reporters because parsing may vary with target config.

## Risks and edge cases
Repro target uses `regexp.MustCompile` for skip patterns, so invalid regexps panic during construction. Random sampling seeds from `time.Now().Nanosecond()`, limiting randomness entropy. `SyzManagerTarget.NewJob` assumes `checkouts` is non-empty. Repro title deduplication is global and mutable across checkouts, so display names depend on discovery order.

## Test signals
No direct tests. Useful tests include round-robin assignment, repro input sampling/skipping, duplicate title naming, least-run selection, invalid input handling, and stat file generation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/targets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/testbed.go -->
# sources/test-tools/syzkaller/tools/syz-testbed/testbed.go

## Purpose
`syz-testbed` orchestrates checkout/build/run/collect loops for comparing syzkaller variants or benchmarking repro behavior over time.

## Important APIs, types, and functions
- Config types: `TestbedConfig`, `DurationConfig`, `CheckoutConfig`, `ReproTestConfig`, and runtime `TestbedContext`.
- `main` loads defaults plus JSON config, validates it, starts HTTP/stats goroutines, creates checkouts, and enters the slot loop.
- `MakeMgrConfig` merges base and per-checkout manager config and forces manager HTTP to `:0`.
- `GetStatViews`, `TestbedStatsTable`, and `SaveStats` derive completed/all views and persist stats.
- `Slot` repeatedly creates target jobs, runs instances, stops/archives them, and reports errors.
- `Loop` runs `MaxInstances` slots until interrupt or any slot error.
- `DurationConfig` JSON marshaling and config validation helpers support config parsing.

## Control flow
After config validation, every checkout is cloned and built before slots start. Each slot repeatedly asks the target for a new job, marks it running, runs it in a goroutine, waits for stop or completion, archives normal results, and starts another. The top-level loop closes all slots on interrupt or first error and waits for every slot to report.

## State and persistence behavior
Persistent state lives under the configured workdir: checkouts, run folders, stats CSVs, averaged bench files, and testbed summary CSV. Runtime counters and checkout lists live in memory. Periodic `SaveStats` runs every 90 seconds and is serialized by `ctx.mu`.

## Dependencies and integration points
Uses `pkg/config`, `pkg/osutil`, `pkg/tool`, `pkg/vcs`, target strategies, checkout/instance/stats/table code, and optional `syz-benchcmp` path. HTTP setup is delegated to `html.go`.

## Risks and edge cases
The HTTP goroutine starts even when HTTP config is empty. `Loop` expects every slot to send an error after `stopAll` closes; a slot blocked in job creation or shutdown can hang shutdown. Existing checkout directories prevent restart. `SaveStats` periodically reads live instance outputs, which can race with files being written but uses fetch errors defensively in some paths.

## Test signals
No direct tests. High-value integration tests would use fake targets/instances to cover slot lifecycle, config validation, stats saving, interrupt shutdown, and error propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbed/testbed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbuild/testbuild.go -->
# sources/test-tools/syzkaller/tools/syz-testbuild/testbuild.go

## Purpose
`syz-testbuild` validates that a kernel config and syzkaller bisection environment can build and boot the current kernel plus previous release tags, protecting bisection workflows from config/toolchain regressions.

## Important APIs, types, and functions
- Flags configure target OS/arch, kernel checkout, config/sysctl/cmdline/userspace/bisect binaries, built syzkaller path, sandbox settings, compiler/linker choices.
- Constants `vmType=qemu` and `numTests=5` define the VM backend and boot/test repetitions.
- `main` requires root, constructs a temporary manager config and `instance.Env`, discovers previous release tags through `vcs.Bisecter`, reads kernel config, tests HEAD and each tag.
- `test` builds the commit-specific bisection environment, cleans/builds kernel, runs VM tests, logs verdicts, and saves failure output.
- `saveLog` writes non-empty failure logs as `<hash>.<idx>` in the current directory.

## Control flow
The tool disables syzkaller sandboxing, creates a temp workdir, completes manager config, opens a VCS repo/bisecter, gets HEAD and previous release tags, then iterates. Each commit obtains compiler/config from `EnvForCommit`, cleans/builds the kernel, and either records build failure output or runs five VM tests. Verdicts are collapsed when all runs match.

## State and persistence behavior
It mutates the supplied kernel checkout by switching commits and cleaning/building in tree. It creates and removes a temporary syzkaller workdir. It writes failure logs in the current working directory and relies on root privileges for image creation.

## Dependencies and integration points
Integrates `pkg/vcs` bisection APIs, `pkg/instance` build/test environment, `pkg/mgrconfig`, QEMU VM configuration, and syzkaller build artifacts. Intended for dashboard/kernel config maintenance.

## Risks and edge cases
The tool is destructive to the kernel checkout state and must run as root. It assumes `repo` implements `vcs.Bisecter` with a direct type assertion. `errors.AsType` use depends on local errors helper API. Saved log filenames use commit hash and run index in the current directory, which can collide across runs. Userspace/toolchain paths are not explicitly validated before build.

## Test signals
No direct tests. Real value is integration testing with throwaway kernel checkouts. Unit seams could fake `instance.Env` and `vcs.Bisecter` to test verdict classification and log saving.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-testbuild/testbuild.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/intermediate_types.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/intermediate_types.go

## Purpose
This file defines the intermediate representation used by `syz-trace2syz` while converting parsed strace lines into syzkaller programs.

## Important APIs, types, and functions
- `TraceTree` stores per-PID traces, parent-child relationships, and root PID; `NewTraceTree` initializes maps; `add` inserts calls and records clone children.
- `Trace` is an ordered syscall list; `Trace.add` appends normal calls or merges resumed calls into the last paused call.
- `IrType` is the interface implemented by parsed argument types.
- `Syscall` stores call name, args, PID, return value, and paused/resumed flags; `NewSyscall` and `String` construct/display it.
- `GroupType`, `Constant`, and `BufferType` model aggregate arguments, evaluated numeric constants, and string/identifier buffers.

## Control flow
`TraceTree.add` sets the first seen PID as root, creates a trace lazily, delegates insertion to `Trace.add`, and records `clone` return values as children when the call is not paused. `Trace.add` merges resumed syscall fragments by appending args, clearing paused, and replacing return value on the last call.

## State and persistence behavior
All state is in-memory parser IR. There is no file or external state. The parent tree and traces persist only for downstream trace-to-program generation.

## Dependencies and integration points
Used by parser grammar actions in `strace.y`/`strace.go`, line parsing in `parser.go`, and prog generation packages. `Constant.Val` and `BufferType.Val` are consumed by call selection and argument generation.

## Risks and edge cases
`Trace.add` assumes a resumed fragment always follows an existing paused call for that PID; malformed traces can panic on an empty call list. Clone child detection assumes clone return value is the child PID and does not filter failed clone returns. Root PID is first parsed PID, not necessarily process-tree root in arbitrary trace ordering.

## Test signals
`parser_test.go` covers root PID, clone tree creation, resumed calls, expression constants, and group types, giving direct coverage of these IR operations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/intermediate_types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/lex.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/lex.go

## Purpose
This generated Ragel lexer tokenizes one strace line for the yacc parser used by `syz-trace2syz`.

## Important APIs, types, and functions
- Constants such as `strace_start`, `strace_error`, `strace_en_comment`, and `strace_en_main` define generated state-machine entry points.
- `Stracelexer` stores parse result, input data, current/end positions, current state, token start/end, and action marker.
- `newStraceLexer` initializes lexer state for a byte slice.
- `Lex` is the large generated state machine that fills `StraceSymType` fields and returns tokens like `INT`, `UINT`, `DOUBLE`, `NULL`, `IDENTIFIER`, operators, string literals, and resumed/unfinished markers.
- `Error` prints parser errors.
- `ParseString` decodes `\x`-escaped quoted string data through `encoding/hex`, falling back to stripped text on decode failure.

## Control flow
`Lex` advances through generated states from `strace_start`, recognizing numeric forms with `strconv`, buffers/identifiers/dates/MAC/IP-like tokens, punctuation and operators required by `strace.y`, and comment-like sections. It returns one token per call to the yacc parser, preserving semantic values in `out`.

## State and persistence behavior
The lexer mutates only its in-memory cursor and semantic output. Parsed syscall result is stored in `Stracelexer.result` by grammar actions, not directly by lexer tokens. There is no persistent state.

## Dependencies and integration points
Generated from `straceLex.rl` and paired with `strace.go`/`strace.y`. Uses `StraceSymType` token fields, parser token constants, `pkg/log` for failed string decoding, and standard parsing/hex helpers.

## Risks and edge cases
This is generated code and should usually be modified through its Ragel source. `Error` prints to stdout, which can pollute tool output. `ParseString` strips all `\x` and quote substrings before hex decoding, so non-hex escaped strings degrade to a stripped representation. Large generated switch logic is hard to review manually.

## Test signals
Parser tests exercise lexer behavior indirectly for strings, constants, resumed calls, groups, and PIDs. More direct lexer tests would cover escaped strings, dates/MAC/IP tokens, malformed strings, and unusual strace comments.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/lex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser.go

## Purpose
This file provides the public byte-slice parsing loop for strace data, producing a `TraceTree` from generated lexer/parser components.

## Important APIs, types, and functions
- `parseSyscall` creates a `Stracelexer` for the current scanner line, calls `StraceParse`, and returns parser status plus parsed syscall.
- `shouldSkip` filters known non-syscall strace noise such as `ERESTART`, signal lines, and ptrace errors.
- `ParseData` scans input line by line, parses calls, inserts them into a `TraceTree`, and returns nil for empty traces.

## Control flow
`ParseData` creates a scanner with a 64 MiB max token buffer, skips known noisy lines, logs each scanned call at verbosity 4, parses the scanner's current bytes, fails on parse errors or nil calls, and accumulates calls in tree order. Scanner errors are returned after the loop.

## State and persistence behavior
All state is in-memory. The function does not read from or write to files; callers provide raw data.

## Dependencies and integration points
Uses generated `newStraceLexer` and `StraceParse`, local IR types, and `pkg/log`. It is the parser entry point consumed by syz-trace2syz conversion logic and parser tests.

## Risks and edge cases
Line-by-line parsing cannot handle syscall records split in ways other than the supported `<unfinished ...>`/`<... resumed>` format. `shouldSkip` is substring-based and may skip unusual legitimate lines containing those markers. Any parse failure aborts the whole input rather than collecting partial traces.

## Test signals
`parser_test.go` directly exercises `ParseData` for basic calls, return values, paused/resumed syscalls, PIDs, clone process trees, expressions, and group arguments.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser_test.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser_test.go

## Purpose
This file tests strace parsing into the intermediate trace tree for `syz-trace2syz`.

## Important APIs, types, and functions
- `TestParseLoopBasic` covers ordinary calls, hex/negative/question returns, unfinished/resumed calls, flags, grouped args, arithmetic, and arrows.
- `TestEvaluateExpressions` validates numeric constant parsing/evaluation for hex, decimal, octal, bitwise, shifts, arithmetic, parentheses, and underflow semantics.
- `TestParseLoopPid`, `TestParseLoop1Child`, `TestParseLoop2Childs`, and `TestParseLoop1Grandchild` validate PID parsing and clone-derived process tree relationships.
- `TestParseGroupType` validates bracket/brace group parsing.

## Control flow
Each test builds small inline strace snippets, calls `ParseData`, and inspects `RootPid`, trace lengths, call names, constant values, `Ptree`, or argument dynamic types.

## State and persistence behavior
No persistent state. The blank `sys` import registers syzkaller descriptions for any downstream parser/prog interactions needed by the package.

## Dependencies and integration points
Directly tests `parser.ParseData` and IR types from the same package. It indirectly validates generated lexer/parser code.

## Risks and edge cases
Tests use `t.Fatal` inside loops without including the test string in many failure messages, which can slow diagnosis. Coverage is focused on accepted examples; malformed lines, scanner overlong lines, escaped string decoding, and resumed-without-paused panics are not covered.

## Test signals
Strong regression signal for core parser behavior, especially expression evaluation and process-tree construction. Missing negative/error-path tests are the main gap.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.go

## Purpose
This generated goyacc parser implements the `strace.y` grammar for converting lexer tokens into `Syscall` and `IrType` values.

## Important APIs, types, and functions
- `StraceSymType` is the semantic value union for token data, integers, constants, buffer/group types, type slices, and syscall results.
- Token constants mirror `strace.y` declarations.
- Parser tables (`StraceAct`, `StracePact`, `StraceR1`, `StraceR2`, etc.) drive generated parsing.
- `StraceLexer`, `StraceParser`, `StraceParserImpl`, `StraceNewParser`, `StraceParse`, `StraceTokname`, `StraceStatname`, `StraceErrorMessage`, and `Stracelex1` form the parser API.
- The large reduction switch contains grammar actions from `strace.y`, constructing `NewSyscall`, `Constant`, `GroupType`, and `BufferType` values.

## Control flow
`StraceParse` creates a parser and calls `Parse`. The parser repeatedly shifts lexer tokens, reduces grammar productions, and writes the parsed syscall into `Stracelex.(*Stracelexer).result`. Productions cover unfinished and resumed syscalls, optional PIDs, numeric/question/flag returns, argument lists, parenthetical suffixes, constants, groups, field assignments, and buffers.

## State and persistence behavior
Parser state is stack-local plus the receiver's lookahead fields. The parsed result is stored in the lexer object. There is no persistent state. Debug verbosity is controlled by package globals `StraceDebug` and `StraceErrorVerbose`.

## Dependencies and integration points
Generated from `strace.y`; should be regenerated rather than manually edited. It depends on local IR constructors and is invoked by `parser.go`. It is paired with the Ragel-generated lexer in `lex.go`.

## Risks and edge cases
Manual edits will be overwritten by generation. Parser actions type-assert the lexer to `*Stracelexer`, so alternate lexer implementations must still use that concrete type or actions panic. Error messages are generic unless verbose mode is enabled. Resumed call merging assumptions live in `Trace.add`, not this parser.

## Test signals
`parser_test.go` exercises this generated parser indirectly. The authoritative grammar source `strace.y` is easier to review for intended behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.y -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.y

## Purpose
This goyacc grammar is the authoritative source for the generated strace parser used by `syz-trace2syz`.

## Important APIs, types, and functions
- `%union` defines semantic fields for strings, integers, constants, IR values, type slices, groups, buffers, and syscalls.
- Tokens describe strace literals, identifiers, flags, date/time/MAC/IP-like strings, numeric values, punctuation, operators, `UNFINISHED`, `RESUMED`, and null/question values.
- `syscall` productions create `NewSyscall` values for normal, paused, resumed, question-return, flagged-error, parenthetical-return, and PID-prefixed forms.
- `constant` productions evaluate arithmetic/bitwise expressions at parse time.
- `group_type`, `field_type`, and `buf_type` map strace aggregates and named fields to IR values.

## Control flow
A parsed line starts at `syscall`. Grammar actions assign `Stracelexer.result` as soon as a complete syscall form is recognized. Resumed fragments are represented as temporary calls with `Resumed=true`; later `Trace.add` merges them into the previous paused call. Field forms generally keep the right-hand value, except arrows keep the left-hand value.

## State and persistence behavior
No persistent state. Grammar actions mutate only the current parser semantic value and concrete lexer result. Constants are folded into `parser.Constant` during parsing.

## Dependencies and integration points
Consumes tokens from `lex.go` and constructs IR types from `intermediate_types.go`. Regeneration produces `strace.go`. `parser.go` calls the generated parser per input line.

## Risks and edge cases
The grammar accepts a pragmatic subset of strace, so unsupported output forms abort parsing. Some tokens, such as signal/date/MAC/IP forms, are tokenized but not all are semantically used in every context. Arithmetic uses unsigned `Constant`, so negative/underflow behavior is intentional but surprising. Concrete lexer type assertions in actions constrain parser reuse.

## Test signals
`parser_test.go` covers many productions, including paused/resumed calls, return variants, expression folding, groups, and PIDs. More grammar-level coverage is needed for strings, field assignments, signals, MAC/IP/date tokens, and parse errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.y -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector.go

## Purpose
This file selects the best syzkaller syscall description variant for a parsed strace syscall when multiple descriptions share a call name or when `open`-family calls need special mapping.

## Important APIs, types, and functions
- `discriminatorArgs` lists syscall argument positions used to distinguish variants by constants, flags, resources, or strings.
- `openDiscriminatorArgs` lists filename argument indexes for `open`, `openat`, and `syz_open_dev`.
- `callSelector` interface exposes `Select`.
- `newSelectors` returns default and open selectors sharing `selectorCommon`.
- `selectorCommon.matchFilename` compares syzkaller string patterns with strace paths, allowing `#` to match digits and returning a device ID.
- `callSet` caches non-automatic target syscalls by call name.
- `openCallSelector.Select` and `matchOpen` specialize open/openat/syz_open_dev matching and argument rewrites.
- `defaultCallSelector.Select` and `matchCall` score variant matches using target argument types and return-cache resource tracking.

## Control flow
Selectors are tried by callers in the returned order. The default selector considers only calls listed in `discriminatorArgs` and chooses the highest positive score. The open selector checks every open-family target variant; when an `open` strace call matches `openat`, it prepends `AT_FDCWD`, and when it matches `syz_open_dev`, it may insert the extracted device ID.

## State and persistence behavior
State is in-memory: target pointer, return cache, and call-set cache. Selectors may mutate the parsed syscall's `Args` slice when translating `open` to `openat` or `syz_open_dev`.

## Dependencies and integration points
Depends on `prog.Target` syscall metadata, parser IR types, and a package-local `returnCache` abstraction for resource arguments. It is part of the trace-to-program generation pipeline.

## Risks and edge cases
`openCallSelector.matchOpen` type-asserts the strace filename arg to `*parser.BufferType`; malformed/non-string args can panic. `matchFilename` concatenates all digits matched by multiple `#` placeholders into one number, which is tested but may be surprising. Selector order means default selection is attempted before open selection; caller behavior determines whether later selectors can override nil only. Scores are heuristic and may choose wrong variants for ambiguous flags/resources.

## Test signals
`call_selector_test.go` covers filename matching, including `#` digit extraction and NUL trimming. There is no direct test for variant scoring, open argument rewrites, resource matching, or panic cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector_test.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector_test.go

## Purpose
This file tests the filename-pattern matching helper used by trace-to-program syscall selection.

## Important APIs, types, and functions
- `TestMatchFilename` constructs a bare `selectorCommon` and tests `matchFilename` over exact paths, `#` digit placeholders, NUL-terminated syzkaller strings, length mismatches, and mismatched characters.

## Control flow
Each table row passes two byte slices to `matchFilename` and verifies both the boolean match and extracted device ID. Multiple `#` placeholders accumulate digits into one decimal ID.

## State and persistence behavior
No persistent state. The selector has no target or return cache because `matchFilename` is self-contained.

## Dependencies and integration points
Tests `selectorCommon.matchFilename`, which is used by both open-family and default pointer-buffer matching in `call_selector.go`.

## Risks and edge cases
Coverage does not include non-ASCII paths, more complex NUL placement, empty-equal paths, or invalid digit extraction overflow. It also does not test callers that mutate syscall args after a match.

## Test signals
Good focused signal for the pattern matcher's intended behavior. Broader call selection remains undertested.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector_test.go -->
