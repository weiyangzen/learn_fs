# Research Group subset-b-009503

This grouped report covers syzkaller subsystem entity behavior, crash/reproducer extraction, Linux MAINTAINERS-derived subsystem generation, hierarchy inference, and related tests. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/entities_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/entities_test.go

## Purpose

This test file verifies the core mutable graph behavior of `subsystem.Subsystem` from `entities.go`: parent reachability, inherited email expansion, and list filtering. It is important because later Linux subsystem generation and extraction assume parent links are acyclic, inherited mailing lists are safe to use for CC calculation, and filtered subsystem lists do not retain stale parent pointers.

## Important APIs, Types, and Functions

The tests exercise `(*Subsystem).ReachableParents`, `(*Subsystem).Emails`, and `FilterList`. Test fixtures build small in-memory `Subsystem` graphs using `Parents`, `Lists`, `Maintainers`, and `NoIndirectCc`. Assertions use `assert.ElementsMatch` where map iteration or graph traversal order is intentionally unspecified.

## Control Flow

`TestReachableParents` creates a diamond graph and confirms that both direct parents and the shared grandparent are returned once. `TestSubsystemEmails` checks that the current subsystem contributes lists and maintainers, reachable parents contribute only lists, and a parent with `NoIndirectCc` is skipped for inherited CC. `TestFilterList` removes one parent from a list and confirms both the returned list and the surviving entity's `Parents` field are updated.

## State, Dependencies, Risks, and Test Signals

The tests mutate heap-allocated `Subsystem` objects directly and rely on pointer identity. There is no persistence or I/O. Dependencies are the local `subsystem` package and `github.com/stretchr/testify/assert`. Main risks covered are duplicate traversal through shared ancestors, leaking maintainers from parents, ignoring `NoIndirectCc`, and retaining filtered-out parents. They do not cover cycle panic behavior or email deduplication, which means those remain residual risks for callers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/entities_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/extractor.go -->
# sources/test-tools/syzkaller/pkg/subsystem/extractor.go

## Purpose

`extractor.go` implements high-level subsystem inference from crash evidence. It combines path-based matches from guilty source paths and syscall-based matches from syzkaller reproducers, then applies voting and parent-pruning rules to return the most specific subsystem candidates.

## Important APIs, Types, and Functions

`Extractor` owns a `rawExtractorInterface`, allowing production use via `makeRawExtractor` and unit tests via mocks. `Crash` contains `GuiltyPath` and `SyzRepro`. Public entry points are `MakeExtractor`, `Extract`, and `TracedExtract`. Internal helpers include `readableSubsystems`, `mostVoted`, and `removeParents`.

## Control Flow

`TracedExtract` first collects all path-derived subsystems, logs each crash through `debugtracer.DebugTracer`, removes parent subsystems when children are present, and counts path votes by subsystem pointer. It then inspects reproducers. A subsystem that appears in every non-empty reproducer is treated as strong evidence. If such repro evidence is also the same as, or a child of, a path-derived subsystem, only the repro-derived child candidates are returned. With at least three reproducers, unrelated all-repro candidates may be combined with non-controversial stack candidates that clear a 66% vote share. Otherwise repro candidates add extra votes and final selection keeps subsystems at or above a 33% share, followed by parent removal.

## State, Dependencies, Risks, and Test Signals

Extractor state is read-only after construction except for the raw matcher internals. It does not persist data. Dependencies include `debugtracer`, `strings`, `math`, and the raw extractor's integration with path and syscall matching. Risks include pointer-identity vote keys, nondeterministic map iteration order, hard-coded thresholds, a typo in one trace message, and reliance on acyclic parent graphs. Tests in `extractor_test.go` cover parent shadowing, mixed repro signals, and repro-supported disambiguation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/extractor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/extractor_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/extractor_test.go

## Purpose

This file unit-tests `Extractor` without depending on real path regexes or syzkaller program parsing. It validates the policy in `TracedExtract`: direct path matching, child-over-parent preference, handling conflicting reproducers, and using reproducers to disambiguate broad guilty path matches.

## Important APIs, Types, and Functions

The test constructs `Subsystem` objects for `fs`, `ext`, `nfs`, and `mm`, with a parent hierarchy rooted at an `all` subsystem. It uses `Extractor{raw: &testRawExtractor{...}}`, where `testRawExtractor` implements `FromPath` and `FromProg`. `progSubsystems` maps byte slices to mocked subsystem results via `reflect.DeepEqual`.

## Control Flow

The table-driven `TestExtractor` runs five crash scenarios. It checks that a single path returns the path subsystem, a reproducer child shadows a parent, conflicting reproducer children fall back to the path parent, a common repro subsystem wins over an irrelevant extra repro subsystem, and a repro child can select `fs/ext` when stack paths vote for both `mm` and `fs`.

## State, Dependencies, Risks, and Test Signals

All state is in-memory test fixture data. Dependencies are `testing`, `reflect`, and `testify/assert`. The tests intentionally use `ElementsMatch` because extraction order can depend on map iteration. The test signal is strong for the extractor's threshold and parent-pruning behavior, but it does not exercise `debugtracer` output, the `cutOff >= 3` unrelated-repro branch, empty crash lists, duplicate subsystem votes from one crash, or the production `rawExtractor` parser path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/extractor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence.go

## Purpose

`coincidence.go` defines a small pair-count matrix used to infer relationships between Linux subsystems. For every file that matches one or more subsystems, callers record the matched set; the matrix then tells how often each subsystem appears and how often pairs co-occur.

## Important APIs, Types, and Functions

`CoincidenceMatrix` wraps `map[*subsystem.Subsystem]map[*subsystem.Subsystem]int`. `MakeCoincidenceMatrix` constructs an empty matrix. `Record(items ...*Subsystem)` increments all ordered pairs, including self-pairs. `Count(a)` returns the diagonal count for one subsystem. `Get(a,b)` returns a pair count. `NonEmptyPairs` iterates non-diagonal entries through a callback.

## Control Flow

`Record` performs a nested loop over the input slice and calls `inc` for every `(i,j)` pair, so recording `[A,B]` increments `A,A`, `A,B`, `B,A`, and `B,B`. `Count` delegates to `Get(a,a)`. `NonEmptyPairs` walks the nested maps and skips self-pairs before invoking the callback. Missing outer or inner map entries evaluate to zero under Go map semantics.

## State, Dependencies, Risks, and Test Signals

The matrix is mutable and keyed by subsystem pointer identity. It does not persist and is not concurrency-safe. Its main dependency is `pkg/subsystem`. Integration points are `BuildCoincidenceMatrix`, `dropSmallSubsystems`, `dropDuplicateSubsystems`, and `setParents`. Risks include duplicate items in one `Record` call inflating counts, unordered iteration, and silent zero counts for unknown subsystem pointers. `coincidence_test.go` verifies totals, pair counts, and callback enumeration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence_test.go

## Purpose

This test file validates `CoincidenceMatrix` counting semantics. It ensures the matrix correctly records self-counts as subsystem file totals and ordered pair counts as co-occurrence totals.

## Important APIs, Types, and Functions

`TestCoincidenceMatrix` uses `MakeCoincidenceMatrix`, `Record`, `Count`, `Get`, and `NonEmptyPairs`. It creates three anonymous `subsystem.Subsystem` pointers and uses `testify/assert` for equality and order-insensitive pair comparison.

## Control Flow

The test records `(a,b)` and `(b,c)`. It expects self counts of `1,2,1`, pair counts for `a-b` and `b-c`, and zero for unrelated `a-c`. It then collects all non-self pairs from `NonEmptyPairs` and checks that both directions of each observed relationship are present.

## State, Dependencies, Risks, and Test Signals

The test state is entirely in-memory. Dependencies are `testing`, `github.com/google/syzkaller/pkg/subsystem`, and `testify/assert`. It confirms the bidirectional nature of `Record` and the callback skipping diagonal entries. It does not cover duplicate subsystem pointers passed in one `Record`, nil subsystem pointers, or concurrent use, so those behaviors are left to caller discipline.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers.go

## Purpose

`maintainers.go` parses the Linux kernel `MAINTAINERS` file into raw records and converts `F`, `X`, and `N` entries into syzkaller `PathRule` regexes. It is the ingestion layer for deriving subsystem ownership from kernel metadata.

## Important APIs, Types, and Functions

`maintainersRecord` stores name, include/exclude wildcards, regexps, lists, maintainers, and trees. `parseLinuxMaintainers` scans past the header and drives `maintainersLexer.next`. `recordTitle`, `recordProperty`, and `endOfFile` model lexer outputs. `applyProperty` handles selected MAINTAINERS keys. `parseEmail` normalizes tolerant mail syntax. `ToPathRule`, `removeMatchingPatterns`, and `wildcardToRegexp` translate record patterns.

## Control Flow

Parsing skips lines until `Maintainers List`, then alternates between titles and one-letter properties. Dot-prefixed note blocks enter comment mode, and indented comment continuations are ignored. Properties before any title are errors. `F` and `X` values are stored as wildcards, `N` values are validated as regexes, `M` and `L` are parsed as email addresses, and `T` trees are retained for maintainer selection. `ToPathRule` joins include wildcards and `N` regexps with `|`, builds exclude regexps separately, and treats trailing directory patterns as recursive subtree matches.

## State, Dependencies, Risks, and Test Signals

State is local to parsing except that `removeMatchingPatterns` mutates records in place. Dependencies include `bufio.Scanner`, `net/mail`, regex, filesystem separator handling, and `subsystem.PathRule`. Risks include scanner token limits, tolerance that may hide malformed emails, regexp compilation failures for `N`, path-separator portability, and semantic divergence from `get_maintainer.pl`. Tests cover sample parsing, wildcard escaping, include/exclude behavior, directory recursion, match-everything patterns, and fuzz entry coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_fuzz.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_fuzz.go

## Purpose

`maintainers_fuzz.go` exposes the Linux MAINTAINERS parser to Go fuzzing or syzkaller's dead-code-aware fuzz harness. Its goal is robustness: arbitrary bytes should not crash the parser even when they produce parse errors internally.

## Important APIs, Types, and Functions

`Fuzz(data []byte) int` wraps `parseLinuxMaintainers(bytes.NewReader(data))` and ignores the returned records and error. `init` calls `runtime.KeepAlive(Fuzz)` to mark the function as used for dead-code checking.

## Control Flow

The fuzz entry converts input bytes into an `io.Reader`, invokes the parser, discards the result, and always returns `0`. Panics, scanner issues, regexp compilation paths, comment-state transitions, and email parsing edge cases are therefore surfaced as fuzz failures rather than handled outcomes.

## State, Dependencies, Risks, and Test Signals

There is no persistent state. Dependencies are `bytes`, `runtime`, and the parser in `maintainers.go`. The useful integration point is automated fuzz infrastructure that discovers parser panics or pathological inputs. Because the harness ignores errors, it tests crash-safety rather than parse correctness. It also does not seed structured MAINTAINERS inputs by itself, so coverage quality depends on the external fuzz corpus.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_test.go

## Purpose

This test file verifies two critical MAINTAINERS behaviors: conversion of raw `maintainersRecord` path metadata into matchable `PathRule`s, and parsing representative MAINTAINERS text into structured records.

## Important APIs, Types, and Functions

`TestRecordToPathRule` builds records and matches paths through `subsystem.MakePathMatcher`. `TestLinuxMaintainers` calls `parseLinuxMaintainers` with `maintainersSample` and compares the resulting `maintainersRecord` slice. The sample covers maintainers, lists, trees, include/exclude rules, regexps, comments, ignored property keys, and list annotations such as `(subscribers-only)`.

## Control Flow

Path-rule tests cover wildcard expansion, `?` matching, directory recursion, `N` regex inclusion, exclusion precedence, trailing slash handling, escaping literal dots, and match-everything patterns. The parser test skips the prose header, ignores note/comment blocks, collects known properties, tolerates extra mailing-list suffix text through `parseEmail`, and verifies the exact normalized records.

## State, Dependencies, Risks, and Test Signals

State is local test fixture data. Dependencies are `strings`, `testing`, the local `linux` package, `subsystem.PathMatcher`, and `testify/require`. These tests provide strong regression signals for matching semantics used by subsystem generation. They do not cover parse errors, invalid regexps, scanner length limits, platform-specific path separators beyond the implementation default, or all MAINTAINERS property keys.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/names.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/names.go

## Purpose

`names.go` assigns stable short names to generated Linux subsystems. Names are needed for bug labels, email subjects, service lookup, custom rule binding, and parent debug output.

## Important APIs, Types, and Functions

`setSubsystemNames` validates pre-existing names and fills empty names from the first mailing-list address. `validateName` constrains generated names to 2 through 16 characters. `emailToName` applies explicit `emailExceptions`, then `emailStripRe`. `buildEmailStripRe` composes prefix and suffix stripping rules from `stripPrefixes` and `stripSuffixes`.

## Control Flow

The first pass over the list rejects duplicate explicit names and records them in a map. The second pass skips already named subsystems, requires at least one list address, derives a name from the first list, validates length, rejects collisions with existing or generated names, then mutates `item.Name`. `emailToName` first checks hard-coded exceptions for renamed or overly long lists, then strips repeated prefixes like `linux-` and suffixes like `-devel`, `-dev`, `-list`, and related terms before `@`.

## State, Dependencies, Risks, and Test Signals

The function mutates the supplied subsystem list in place and persists no external data. Dependencies are `fmt`, `regexp`, `strings`, and `subsystem.Subsystem`. Integration points include `listFromRepoInner` and `applyExtraRules`, which assume all names are unique. Risks include first-list dependence, incomplete exception coverage, length constraints rejecting legitimate subsystems, and regex changes causing label churn. `names_test.go` covers general stripping, exceptions, collisions, explicit names, and missing-list failure.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/names.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/names_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/names_test.go

## Purpose

This file tests Linux subsystem name derivation from mailing lists and validates collision/error behavior in `setSubsystemNames`.

## Important APIs, Types, and Functions

`TestEmailToName` exercises `emailToName`. `subsystemTestInput` is a small fixture helper that converts input name/email pairs into `*subsystem.Subsystem`. `TestSetSubsystemNames` runs table-driven cases through `setSubsystemNames`.

## Control Flow

Email tests verify general prefix/suffix stripping, dot removal, and an exception for virtualization. Naming tests cover successful generation, duplicate generated names, missing list failure, preserving explicit names, and collisions between an explicit name and a generated name. The test then checks either expected failure or final names by list index.

## State, Dependencies, Risks, and Test Signals

All state is fixture-local and mutations occur on newly allocated subsystem objects. Dependencies are `testing` and the local `subsystem` type. The tests provide good signal for common name derivation and collision protection. They do not cover all exception-map entries, invalid email formats that fail the regex, minimum/maximum length boundaries directly, multiple lists per subsystem, or nondeterminism from future changes to list ordering upstream.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/names_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/parents.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/parents.go

## Purpose

`parents.go` infers and normalizes parent-child relationships among Linux subsystems based on file-path co-occurrence. This allows extraction to prefer specific subsystems while still inheriting broader mailing-list context.

## Important APIs, Types, and Functions

`parentTransformations` coordinates pruning and parent inference. `parentInfo` stores debug comments by parent and child pointer, with `Save` adding explanations. `setParents` infers edges from a `CoincidenceMatrix`. `dropSmallSubsystems`, `dropDuplicateSubsystems`, and `transitiveReduction` clean the generated graph.

## Control Flow

`parentTransformations` first drops subsystems with two or fewer matched files unless they have syscall rules, then drops near-duplicates. `setParents` considers each non-empty matrix pair still present in the input. If at least half of a child's files overlap a larger candidate parent and the child has fewer files, it appends the candidate to `child.Parents`, records debug text, and calls `ReachableParents` to catch loops. `transitiveReduction` removes redundant ancestor links when an intermediate parent already reaches the same ancestor.

## State, Dependencies, Risks, and Test Signals

The code mutates `Subsystem.Parents` and list membership in memory; debug info is returned to callers but not persisted here. Dependencies are the local matrix and `pkg/subsystem`. Risks include integer-threshold roughness (`2*common/childFiles`), pointer-keyed matrices, mutation accumulation if reused lists already have parents, and heuristic duplicate removal based on first list email. Tests cover small drops, duplicate/near-duplicate drops, transitive reduction, and inferred hierarchy from a synthetic filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/parents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/parents_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/parents_test.go

## Purpose

This test file validates the hierarchy-transformation heuristics used after Linux subsystem records are matched against a repository tree.

## Important APIs, Types, and Functions

Tests call `MakeCoincidenceMatrix`, `dropSmallSubsystems`, `dropDuplicateSubsystems`, `transitiveReduction`, `BuildCoincidenceMatrix`, and `setParents`. They use synthetic `subsystem.Subsystem` instances with path rules and `testing/fstest.MapFS` to avoid real kernel checkout dependencies.

## Control Flow

`TestDropSmallSubsystems` records enough files for kernel/net/fs but not legal and checks the small subsystem is removed. `TestDropDuplicateSubsystems` covers exact overlap with alphabetical-list preference, acceptable 66% overlap, and a high-overlap child that is dropped. `TestTransitiveReduction` starts with redundant ancestor links and confirms only direct edges remain. `TestSetParents` builds path matches for kernel, net, wireless, and drivers, then verifies inferred parent edges.

## State, Dependencies, Risks, and Test Signals

State is in-memory and graph mutations happen on test objects. Dependencies are `testing`, `testing/fstest`, `subsystem`, and `testify/assert`. These tests give strong signals for intended heuristics but do not cover loop creation failures, existing parent links before inference, syscall-retained small subsystems, exact threshold boundaries, nil path rules, or nondeterministic callback ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/parents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/path_coincidence.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/path_coincidence.go

## Purpose

`path_coincidence.go` walks a Linux source tree, matches relevant source files against subsystem path rules, and builds the `CoincidenceMatrix` used for duplicate pruning and parent inference.

## Important APIs, Types, and Functions

`BuildCoincidenceMatrix(root fs.FS, list []*Subsystem, excludeRe *regexp.Regexp)` is the public entry point. `matrixDebugInfo` stores matched file lists by subsystem. `includePathRe` limits scanned files to paths ending in `/` or `.c`, `.h`, or `.S`. `extractSubsystems` starts worker goroutines that apply a `subsystem.PathMatcher` to paths and emit `extracted` records.

## Control Flow

`BuildCoincidenceMatrix` creates a matcher, starts matcher workers and one result consumer, then walks the filesystem with `fs.WalkDir`. Directories and excluded paths are skipped; included files are sent to workers. The consumer records every matched subsystem set into the matrix and appends the path to debug file lists for each subsystem. After the walk, paths are closed, the consumer is awaited, and each debug file list is sorted for deterministic output.

## State, Dependencies, Risks, and Test Signals

State is local except for the returned matrix and debug info. Matching is concurrent, but matrix writes are serialized in the consumer goroutine. Dependencies include `io/fs`, `regexp`, `runtime.NumCPU`, `slices`, `sync.WaitGroup.Go`, and `subsystem.PathMatcher`. Risks include blocking if the walk exits early before closing paths, reliance on newer Go `WaitGroup.Go`, exclusion regex breadth, source-extension filtering that ignores generated or config files, and pointer-identity keys. Tests cover filtered `.git` paths, source-file counts, and pair counts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/path_coincidence.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/path_coincidence_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/path_coincidence_test.go

## Purpose

This file tests `BuildCoincidenceMatrix` using an in-memory filesystem and simple path rules. It confirms that filesystem walking, source-file filtering, matching, and pair counting cooperate correctly.

## Important APIs, Types, and Functions

`TestBuildCoincidenceMatrix` constructs `Subsystem` objects for `vfs`, `ext4`, `ntfs`, and `kernel`, each with `PathRule` include regexes. It uses `fstest.MapFS`, `BuildCoincidenceMatrix`, `CoincidenceMatrix.Count`, and `CoincidenceMatrix.Get`.

## Control Flow

The fake filesystem includes one ignored `.git` object, filesystem files under `fs/`, and a network file. The matrix is built without an exclude regex. The test expects the catch-all kernel subsystem to count all five source files, `vfs` to count the four `fs/` files, `ext4` to count one file, and pair counts to reflect nesting while unrelated children like `ext4` and `ntfs` do not co-occur.

## State, Dependencies, Risks, and Test Signals

All data is local to the test. Dependencies are `testing`, `testing/fstest`, `subsystem`, and `testify/assert`. The test confirms core matrix construction but does not inspect `matrixDebugInfo`, exclude regex behavior, `.S` and `.h` variations in detail, filesystem walk errors, or concurrent scheduling edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/path_coincidence_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/rules.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/rules.go

## Purpose

`rules.go` contains Linux-specific policy overrides layered on top of MAINTAINERS-derived data. These rules fill gaps where path metadata alone cannot produce useful syzkaller subsystem behavior.

## Important APIs, Types, and Functions

`customRules` groups six rule maps: `subsystemCalls`, `notSubsystemEmails`, `extraSubsystems`, `noReminders`, `noIndirectCc`, and `addParents`. `linuxSubsystemRules` is the production rule set used by `ListFromRepo`.

## Control Flow

The rules are consumed by `listFromRepoInner` and `linuxCtx.applyExtraRules`. `extraSubsystems` forces named subsystems from specific MAINTAINERS records before list-based grouping. `notSubsystemEmails` excludes broad or misleading mailing lists from subsystem creation. `subsystemCalls` attaches syscall/reproducer hints used by `rawExtractor.FromProg`. `noReminders` and `noIndirectCc` alter reporting and inherited CC behavior. `addParents` adds manual parent links after inferred hierarchy generation and then transitive reduction cleans redundant edges.

## State, Dependencies, Risks, and Test Signals

The file is static data plus the `customRules` type. It has no I/O and no runtime mutation by itself. Its only direct dependency is package-local integration in `subsystems.go`. Risks are staleness as Linux MAINTAINERS and syzkaller syscall names change, dangling rule keys rejected by `noDanglingRules`, inconsistent naming exceptions, and policy choices that intentionally hide broad lists or reports. `subsystems_test.go` verifies a small custom-rules instance for syscall attachment, extra subsystem extraction, and manual parent behavior; production map coverage depends on broader list-generation tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/rules.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems.go

## Purpose

`subsystems.go` is the assembly pipeline that turns a Linux repository into syzkaller `Subsystem` objects plus debug metadata. It connects MAINTAINERS parsing, custom rules, path-rule matching, hierarchy inference, naming, sorting, and service-facing metadata.

## Important APIs, Types, and Functions

`ListFromRepo(repo string)` wraps `os.DirFS` and calls `listFromRepoInner`. `linuxCtx` stores the filesystem, raw records, and optional custom rules. Key methods are `groupByList`, `groupByRules`, and `applyExtraRules`. Helpers include `noDanglingRules`, `mergeRawRecords`, `unique`, `maintainersFromRecords`, and `getMaintainers`.

## Control Flow

The pipeline opens `MAINTAINERS`, parses records, removes documentation/scripts/samples/tools/Makefile patterns, extracts forced subsystems from `extraSubsystems`, groups remaining records by list email, builds a coincidence matrix over the repo tree, applies parent transformations, assigns unique names, applies syscall/reminder/CC/manual-parent rules, and sorts subsystems and path rules deterministically. Debug output includes parent-child comments and matched file lists.

## State, Dependencies, Risks, and Test Signals

The function mutates records and subsystem objects in memory, but does not persist files. Dependencies include `io/fs`, `os.DirFS`, regex, sorting helpers, `golang.org/x/exp/maps`, MAINTAINERS parser, coincidence builder, name assignment, and `subsystem.DebugInfo`. Risks include dangling custom rules, missing MAINTAINERS records, broad pattern drops, maintainer intersection heuristics returning no maintainers, filesystem walk errors, and generated name churn. Tests cover grouping, custom syscalls and extra subsystems, path matching, inferred and manual parents.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems_test.go

## Purpose

This test file validates the end-to-end Linux subsystem generation pipeline with a synthetic MAINTAINERS file and in-memory source tree.

## Important APIs, Types, and Functions

Tests call `listFromRepoInner`, `prepareTestLinuxRepo`, `ensureParents`, `subsystem.MakePathMatcher`, and use `testRules`. The embedded `testMaintainers` fixture covers VFS, ext4, freevxfs, memory management, tmpfs, UDF, and THE REST.

## Control Flow

`TestGroupLinuxSubsystems` verifies list-based grouping, name derivation, and maintainer selection after path rules are ignored for comparison. `TestCustomCallRules` adds an extra UDF subsystem and syscall rules, then verifies syscall attachment and improved VFS maintainer selection after UDF is excluded from list grouping. `TestLinuxSubsystemPaths` builds a matcher from generated subsystems and checks expected subsystem names for representative paths. `TestLinuxSubsystemParents` verifies inferred parent links and then a custom parent override.

## State, Dependencies, Risks, and Test Signals

All repository state is modeled through `fstest.MapFS`; subsystem objects are mutated by the pipeline. Dependencies are `io/fs`, `testing`, `testing/fstest`, `subsystem`, and `testify/assert`. The tests give high-value integration coverage for generation behavior without a real kernel checkout. They do not cover production `linuxSubsystemRules`, dangling-rule failures, debug info contents, sorting stability directly, or error paths such as missing `MAINTAINERS`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/list.go -->
# sources/test-tools/syzkaller/pkg/subsystem/list.go

## Purpose

`list.go` provides a process-local registry for named subsystem lists. It decouples a fuzzing target OS from the implementation-specific subsystem list used by syzkaller services.

## Important APIs, Types, and Functions

The package-level `lists` map stores `registeredSubsystem` values containing a `[]*Subsystem` and a `revision`. `HasList` checks registration. `RegisterList` adds a new named list and panics on duplicate names. `GetList` returns the raw registered list and panics if absent. `ListService` constructs a `Service` from a registered list and revision through `MustMakeService`.

## Control Flow

Callers register lists during package initialization or setup. Later consumers check existence, retrieve the list directly, or request a service wrapper for extraction, lookup by name, and child traversal. Missing names and duplicate registration are treated as programmer errors and panic rather than returning errors.

## State, Dependencies, Risks, and Test Signals

State is global to the Go process and is not concurrency-protected. Registered lists are returned by reference, so callers can mutate shared subsystem objects and affect future lookups. There is no external persistence. Dependencies are only `fmt` and the local service/entity types. Integration points include generated Linux lists and any callers that expose subsystem extraction as a service. Risks include duplicate init registration, test pollution between packages, unsynchronized concurrent registration, and mutation of returned lists. Existing service/list tests elsewhere cover registry and service construction behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/list.go -->
