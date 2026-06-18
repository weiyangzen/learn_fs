# subset-b-009128 research

Grouped research report for Git LFS Git plumbing, gitattr, githistory, and core LFS scanner/filter files. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/git_test.go -->
# sources/sync-backup/git-lfs/git/git_test.go

Purpose: integration-heavy tests for the `git` package ref, branch, worktree, version, tracked-file, changed-file, remote URL, and object-ID helpers. The file uses temporary repositories from `t/cmd/util` to exercise real Git subprocess behavior rather than isolated parser logic.

Important APIs/types/functions: `Ref.Refspec`, `ParseRef`, `CurrentRef`, `Configuration.CurrentRemoteRef`, `RemoteRefNameForCurrentBranch`, `ResolveRef`, `RecentBranches`, `GetAllWorktrees`, `IsVersionAtLeast`, `GitAndRootDirs`, `GetTrackedFiles`, `LocalRefs`, `GetFilesChanged`, `ValidateRemoteURL`, `RefType.Prefix`, `RemoteURLs`, `MapRemoteURL`, `HasValidObjectIDLength`, and `IsZeroObjectID`.

Control flow: tests create commits, branches, tags, remotes, worktrees, staged files, and deleted files; then assert helper output against expected refs, paths, or booleans. Some tests gate on Git version, especially worktree behavior. Remote URL tests write local config and then query normal and push URLs.

State/persistence behavior: most cases mutate actual `.git` state: refs, packed/unpacked worktrees, config, index state, and working-tree deletion/staging. The tests verify functions see both committed and index state and do not rely only on the working tree.

Dependencies/integration: depends on the local Git binary, filesystem temp repos, `tools.CanonicalizePath`, and helper sorters for refs/worktrees/pointers. It covers behavior that other files in this group rely on, such as ref classification used by history rewriting and scanner range construction.

Risks/test signals: tests are sensitive to Git version, platform path normalization, branch default names, and real Git command behavior. Strong signals include correct ref names/SHAs, worktree pruning flags, stable file-change lists, and URL mapping. The file does not test every implementation path directly, but it establishes broad behavioral contracts for callers.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/git_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/attr.go -->
# sources/sync-backup/git-lfs/git/gitattr/attr.go

Purpose: parser for `.gitattributes` line syntax, producing typed pattern and macro lines plus attribute key/value state. It also records dominant input line ending so attribute files can be rewritten consistently elsewhere.

Important APIs/types/functions: `Line`, `PatternLine`, `MacroLine`, `Attr`, `ParseLines`, `lineEndingSplitter`, `ScanLines`, and `LineEnding`. `Attr` models true values, `-attr` false values, `key=value`, and `!attr` unspecified resets.

Control flow: `ParseLines` scans trimmed lines, skips blanks and comments, handles quoted patterns via `strconv.Unquote`, recognizes `[attr]` macro definitions, splits attributes on spaces, and constructs either `patternLine` with a `wildmatch.Wildmatch` configured for Git attributes or `macroLine`. Scanner errors and unbalanced quotes are returned.

State/persistence behavior: no durable writes. Parser state is local to the scan except line-ending counters; the returned line-ending string is `\r\n`, `\n`, or empty depending on observed input.

Dependencies/integration: depends on `github.com/git-lfs/wildmatch/v2`, Git LFS localized errors, and is consumed by `MacroProcessor`, `Tree`, and attribute file discovery in `files.go`.

Risks/test signals: syntax support is intentionally simple and space-split; quoted patterns are supported but escaped attribute values are not. Tests cover multiple attributes, comments, unset/unspecified attributes, quoted patterns, bad quotes, no-attribute lines, and macro lines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/attr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/attr_test.go -->
# sources/sync-backup/git-lfs/git/gitattr/attr_test.go

Purpose: unit tests for `.gitattributes` line parsing in `attr.go`.

Important APIs/types/functions: exercises `ParseLines`, `PatternLine`, `MacroLine`, and `Attr` values. Uses `strings.NewReader` and `testify/assert`.

Control flow: each test parses a small attribute snippet and asserts line count, concrete interface type, pattern/macro text, and ordered attributes. Negative cases assert comments are skipped and unbalanced quotes return the expected error.

State/persistence behavior: in-memory only. No filesystem or Git repository state is required.

Dependencies/integration: provides coverage for downstream consumers that assume parsed attributes preserve left-to-right order and distinguish false from unspecified state.

Risks/test signals: good coverage of common syntax, but does not cover mixed whitespace beyond spaces, line-ending detection, escaped quotes beyond `strconv.Unquote`, or malformed key/value combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/attr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/files.go -->
# sources/sync-backup/git-lfs/git/gitattr/files.go

Purpose: discovers repository, user, system, and working-tree attribute files and extracts patterns that are relevant to Git LFS tracking or locking. It can also build a `filepathfilter.Filter` from `filter=lfs` patterns.

Important APIs/types/functions: `AttributePath`, `AttributeSource`, `GetUserAttributePaths`, `GetUserAttributeFilePath`, `GetRepoAttributeFilePath`, `GetSystemAttributePaths`, `GetSystemAttributeFilePath`, `GetAttributePaths`, `AttrPathsFromReader`, `GetAttributeFilter`, and `findAttributeFiles`.

Control flow: global/system paths are resolved through Git config or `git var GIT_ATTR_SYSTEM` for Git 2.42+, repo attributes come from `$GIT_DIR/info/attributes`, and working-tree `.gitattributes` files are found through `git ls-files`. Each file is parsed, macro-expanded, filtered for `filter=lfs` and `lockable`, path-prefixed relative to the attribute file directory, and appended with source metadata.

State/persistence behavior: reads config and files only. The `MacroProcessor` is stateful across files so macros from higher-precedence sources can be reused where Git permits. `AttributeSource.LineEnding` records parsed EOL style.

Dependencies/integration: integrates with `git.NewLsFiles`, config path expansion, Git version checks, `filepathfilter`, and `Tree` scanning. Attribute-file ordering is sorted by path length descending to respect more-specific precedence when iterating.

Risks/test signals: file discovery depends on Git subprocess success and version behavior. Missing or unreadable attribute files are silently skipped in some paths, which is pragmatic but can hide configuration problems. Direct tests for this file are indirect through tree and scanner tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/macro.go -->
# sources/sync-backup/git-lfs/git/gitattr/macro.go

Purpose: expands Git attribute macros into concrete attributes while preserving the original macro attribute as Git does.

Important APIs/types/functions: `MacroProcessor`, `NewMacroProcessor`, `ProcessLines`, and `ProcessMacros`. The built-in `binary` macro expands to `-diff`, `-merge`, and `-text`.

Control flow: `ProcessLines` iterates parsed lines. Pattern lines are copied into new pattern lines with expanded attributes; macro attributes with value `true` append the macro expansion before the alias attribute, and unspecified macro attributes append unspecified versions of each macro member. Macro lines update the processor only when `readMacros` is true. `ProcessMacros` loads macro definitions without returning pattern lines.

State/persistence behavior: `MacroProcessor.macros` persists across calls and `didReadMacros` records whether macro definitions have been loaded for a tree. Macro definitions can be overridden by later processing.

Dependencies/integration: consumed by attribute file readers and `Tree.Applied` to match Git's stateful macro semantics.

Risks/test signals: statefulness is useful but requires careful call ordering. Tests cover enabled/disabled macros, unspecified macros, built-in binary, cross-call state, and macro overrides.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/macro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/macro_test.go -->
# sources/sync-backup/git-lfs/git/gitattr/macro_test.go

Purpose: tests macro expansion and macro state behavior.

Important APIs/types/functions: `ParseLines`, `NewMacroProcessor`, `ProcessLines`, and `ProcessMacros`.

Control flow: test cases parse macro definitions and pattern lines, run the processor with macros enabled or disabled, and assert expanded ordered attributes. Separate cases validate `!macro` expansion into unspecified attributes, built-in `binary`, state reuse across calls, and overriding an existing macro definition.

State/persistence behavior: intentionally verifies persistent macro state in one processor instance and override behavior through `ProcessMacros`.

Dependencies/integration: uses `testify/assert`. Supports `Tree.Applied` and `files.go` assumptions that macro expansion order is stable.

Risks/test signals: strong for macro semantics, but not for concurrency or sharing a processor across unrelated repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/macro_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/tree.go -->
# sources/sync-backup/git-lfs/git/gitattr/tree.go

Purpose: builds an in-memory tree of `.gitattributes` blobs from a Git tree and answers which attributes apply to a path, including optional system, user, and repo-info attributes.

Important APIs/types/functions: `Environment`, `Tree`, `New`, `NewFromReader`, `FindSpecialAttributes`, `linesInTree`, `Applied`, and internal `applied`.

Control flow: `New` creates a shared `MacroProcessor`, parses the current tree's `.gitattributes` blob if present, recursively descends into subtrees, and keeps only children containing attributes. `FindSpecialAttributes` loads system, user, and repo-info attribute files into sibling `Tree` nodes. `Applied` lazily processes macros, then applies system, user, in-tree, and repo-info attributes in order; recursive `applied` matches current-level patterns and descends by the first path component.

State/persistence behavior: reads Git objects and optional filesystem config files. It caches parsed child trees and macro state in memory; no writes occur.

Dependencies/integration: uses `gitobj.ObjectDatabase`, `gitattr.ParseLines`, `MacroProcessor`, and attribute path resolver functions from `files.go`. `lfs/gitscanner_tree.go` separately uses `AttrPathsFromReader` for tree scans, but this file provides the richer tree application model.

Risks/test signals: symlinked `.gitattributes` is rejected as an error. Macro processing is lazy and shared, so call order matters if tree instances are mutated. Tests cover root/subtree application, discovery, macro use, pruning irrelevant child trees, and special-attribute precedence.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/tree_test.go -->
# sources/sync-backup/git-lfs/git/gitattr/tree_test.go

Purpose: tests attribute application and tree discovery over synthetic Git object databases.

Important APIs/types/functions: `Tree.Applied`, `New`, `gitobj.FromFilesystem`, `WriteBlob`, `WriteTree`, and manual `Tree` structures using `wildmatch`.

Control flow: early tests use a hand-built tree to assert root and subtree matching. Later tests write blobs and trees to a temp object database, construct `Tree` with `New`, and verify attributes apply through direct and indirect child trees. Additional tests cover macro expansion and ordering across system/user/tree/repo attribute trees.

State/persistence behavior: uses temporary object databases but no durable repo mutation. The tests validate that irrelevant subtrees are pruned from the in-memory `children` map.

Dependencies/integration: depends on `gitobj` and `testify`. It provides regression coverage for tree-recursive discovery and precedence-sensitive macro processing.

Risks/test signals: covers many in-memory cases but not actual system/user attribute path discovery from disk; those are mostly exercised indirectly elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/gitattr/tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/identical-blobs.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/identical-blobs.git/config

Purpose: Git fixture config for a non-bare repository where two paths can reference identical blob contents. It supports rewriter tests that prove caching is keyed by path plus object ID, not only object ID.

Important APIs/types/functions: standard `[core]` keys: `repositoryformatversion = 0`, `filemode = true`, `bare = false`, `logallrefupdates = true`, `ignorecase = true`, and `precomposeunicode = true`.

Control flow: no executable logic. Git and `gitobj` consume this config when the fixture is copied to a temp directory and opened.

State/persistence behavior: declares the fixture as mutable, non-bare working repository metadata with reflog updates. Test helpers copy it before mutation so the original fixture remains unchanged.

Dependencies/integration: consumed by `DatabaseFromFixture` and `TestRewriterVisitsUniqueEntriesWithIdenticalContents`.

Risks/test signals: fixture config is minimal and platform-tuned for macOS-like case/unicode settings. If `bare` or object paths change, rewriter tests may fail to locate refs or objects.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/identical-blobs.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-annotated-tags.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-annotated-tags.git/config

Purpose: Git fixture config for a linear history containing annotated tags, used to validate tag-object rewriting during ref updates.

Important APIs/types/functions: standard `[core]` config with `bare = false`, reflog updates enabled, filemode true, and case/unicode settings.

Control flow: no logic. It lets Git commands resolve refs and tag objects in a copied fixture repository.

State/persistence behavior: non-bare repo metadata supports `git update-ref` during tests. The fixture is copied before use.

Dependencies/integration: used by `TestRefUpdaterMovesRefsWithAnnotatedTags`; the config must allow tag refs and object database access from `gitobj`.

Risks/test signals: annotated tag tests depend on this repository's tag object graph; config drift can invalidate expected SHA values.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-annotated-tags.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-tags.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-tags.git/config

Purpose: Git fixture config for a linear history with lightweight tags, used for partial migration and ref update tests.

Important APIs/types/functions: standard `[core]` keys with `bare = false`, `logallrefupdates = true`, `filemode = true`, `ignorecase = true`, and `precomposeunicode = true`.

Control flow: no code; Git reads the config when resolving tags and commit ancestry.

State/persistence behavior: copied fixture can have refs updated in temp state without touching source fixture.

Dependencies/integration: supports `TestHistoryRewriterUseOriginalParentsForPartialMigration`, `TestRefUpdaterMovesRefs`, and `TestRefUpdaterIgnoresUnovedRefs`.

Risks/test signals: expected commit/tag SHAs in tests are tightly coupled to the fixture contents and config being a normal repository.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history-with-tags.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history.git/config

Purpose: base Git fixture config for simple linear commit history used by many rewriter tests.

Important APIs/types/functions: standard `[core]` config with repository format 0, `bare = false`, filemode and reflog enabled, plus case/unicode flags.

Control flow: no executable logic. It provides Git repository identity and behavior to subprocesses and `gitobj`.

State/persistence behavior: copied to temp before tests; rewritten commits and refs are created in the copy.

Dependencies/integration: used by rewriter tests for blob rewriting, additional tree entries, callbacks, ref updates, and fixture helpers.

Risks/test signals: test expected tree and commit SHAs depend on this fixture history exactly. If config makes the repo bare or changes Git behavior, `git update-ref` and `rev-parse` assertions can break.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/linear-history.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/non-repeated-subtrees.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/non-repeated-subtrees.git/config

Purpose: fixture config for history with unique subtree content, used to test callback ordering and path filters.

Important APIs/types/functions: standard non-bare `[core]` settings with reflog updates.

Control flow: none. The config enables normal Git object/ref access.

State/persistence behavior: temp-copy mutable repository metadata. No code runs from this file.

Dependencies/integration: used by tests for filtering `subdir/*.txt` and callback sequencing across root and child trees.

Risks/test signals: expected callback counts and filter behavior depend on fixture tree shape; config must remain compatible with local Git.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/non-repeated-subtrees.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/octopus-merge.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/octopus-merge.git/config

Purpose: fixture config for an octopus merge history used to validate parent rewriting across multi-parent commits.

Important APIs/types/functions: standard `[core]` config for a non-bare repository.

Control flow: no direct logic. The rewriter reads commits/trees and writes rewritten objects in a temp copy.

State/persistence behavior: supports reflog updates and mutable refs in tests.

Dependencies/integration: used by `TestRewriterRewritesOctopusMerges`.

Risks/test signals: if fixture ancestry changes, expected parent SHAs and tree IDs in the test become invalid.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/octopus-merge.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/packed-objects.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/packed-objects.git/config

Purpose: fixture config for a bare repository with packed objects, used to prove the rewriter and object database can visit packed blobs.

Important APIs/types/functions: `[core]` sets `bare = true` while otherwise using format 0, filemode, reflog, case, and unicode settings.

Control flow: no code. The `bare = true` value changes repository layout assumptions for Git and object lookup.

State/persistence behavior: fixture is copied to temp and opened as an object database; no working tree is expected.

Dependencies/integration: used by `TestRewriterVisitsPackedObjects`.

Risks/test signals: this config differs from the other fixtures; code paths relying on a worktree must not be assumed. If bare handling regresses, packed-object scanning may fail.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/packed-objects.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/repeated-subtrees.git/config -->
# sources/sync-backup/git-lfs/git/githistory/fixtures/repeated-subtrees.git/config

Purpose: fixture config for a history with repeated subtree/object entries, used to validate rewriter caching and avoiding unnecessary revisits.

Important APIs/types/functions: standard non-bare `[core]` repository config.

Control flow: no executable behavior. Git commands and `gitobj` consume it from a temp copy.

State/persistence behavior: temp-copy repository state can be rewritten without affecting the source fixture.

Dependencies/integration: used by `TestRewriterDoesntVisitUnchangedSubtrees`.

Risks/test signals: expected visit counts depend on this fixture's repeated subtree structure and on the repo remaining non-bare.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures/repeated-subtrees.git/config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures_test.go -->
# sources/sync-backup/git-lfs/git/githistory/fixtures_test.go

Purpose: helper functions for githistory tests to copy fixture repositories, open object databases, and assert blob, commit, tree, and ref state.

Important APIs/types/functions: `DatabaseFromFixture`, `AssertBlobContents`, `AssertCommitParent`, `AssertCommitTree`, `AssertRef`, `HexDecode`, `copyToTmp`, `copyDir`, and `copyFile`.

Control flow: fixtures are recursively copied to a temp directory, opened with `gitobj.FromFilesystem`, and used by tests. Assertion helpers traverse trees path component by path component, decode SHAs, invoke `git rev-parse` for refs, and compare against expected bytes or contents.

State/persistence behavior: creates mutable temp copies under the OS temp directory and preserves file modes. No cleanup helper is present here; test temp artifacts are managed by OS/test lifecycle rather than `t.TempDir`.

Dependencies/integration: depends on `gitobj`, local `git`, `os/exec`, and `testify/assert`. It is central to `rewriter_test.go` and `ref_updater_test.go`.

Risks/test signals: recursive copy is simple and does not preserve symlink semantics specially. `AssertRef` depends on `db.Root()` and Git being able to run in that root. Helper failures call `t.Fatalf`, giving direct test failure signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/fixtures_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/ref_updater.go -->
# sources/sync-backup/git-lfs/git/githistory/ref_updater.go

Purpose: updates refs after history rewriting, including lightweight and annotated tag handling.

Important APIs/types/functions: `refUpdater`, `updateRefs`, `updateOneTag`, and `updateOneRef`.

Control flow: `updateRefs` opens `git update-ref --stdin`, optionally starts a transaction for Git 2.27+, deduplicates seen refspecs, calls `updateOneRef` for each ref, then prepares/commits and waits for the command. `updateOneRef` maps the ref SHA through `cacheFn`; for tag refs it may rewrite tag objects, recursively update inner annotated tags, and then writes NUL-delimited update commands.

State/persistence behavior: writes new tag objects to the object database and moves refs in the repository, creating reflog entries through Git. Progress is logged through `tasklog`.

Dependencies/integration: integrates with `git.UpdateRefsFromStdin`, `git.ResolveRef`, `git.Ref`, `gitobj.Tag`, Git version detection, and `Rewriter` commit cache.

Risks/test signals: annotated tag handling is subtle; missing cached objects leave refs untouched. Any command stdin/transaction formatting regression can move no refs or fail the whole update. Tests cover moving lightweight tags, annotated tags, and ignoring unmapped refs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/ref_updater.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/ref_updater_test.go -->
# sources/sync-backup/git-lfs/git/githistory/ref_updater_test.go

Purpose: tests `refUpdater` ref movement behavior for lightweight tags, annotated tags, and unmapped refs.

Important APIs/types/functions: `DatabaseFromFixture`, `AssertRef`, `refUpdater.updateRefs`, `git.Ref`, and fixed `cacheFn` closures.

Control flow: each test copies a fixture, asserts the initial tag ref, constructs a `refUpdater`, runs `updateRefs`, and asserts final ref state. Annotated tag case expects a newly written tag object SHA rather than the raw commit SHA.

State/persistence behavior: mutates refs in temp fixture copies via `git update-ref`. Object database may receive new tag objects.

Dependencies/integration: depends on local Git, fixture integrity, and SHA constants from fixture histories.

Risks/test signals: the third test name has a typo (`Unoved`) but behavior is clear. Coverage is narrow to tags and does not directly test branch refs or update-ref transaction failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/ref_updater_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/rewriter.go -->
# sources/sync-backup/git-lfs/git/githistory/rewriter.go

Purpose: rewrites Git history by applying blob and tree callbacks across selected commits, preserving topology, optionally filtering paths, writing an object map, and updating refs.

Important APIs/types/functions: `Rewriter`, `RewriteOptions`, `BlobRewriteFn`, `TreePreCallbackFn`, `TreeCallbackFn`, `WithFilter`, `WithLogger`, `NewRewriter`, `Rewrite`, `rewriteTree`, `rewriteBlob`, `commitsToMigrate`, `refsToMigrate`, `scannerOpts`, `cacheEntry`, and `cacheCommit`.

Control flow: `Rewrite` obtains commits from `git rev-list` in reverse topological order, rewrites each commit tree recursively, rewrites parent IDs through the commit cache or preserves original parents outside the migration range, writes changed commits, records object-map rows, and optionally calls `refUpdater`. `rewriteTree` pre-callbacks each tree, skips disallowed blobs and symlinks, reuses cached path/OID entries, rewrites blobs or subtrees, post-callbacks the assembled tree, and writes changed trees.

State/persistence behavior: writes new blobs, trees, commits, optional object-map files, and optionally refs/tag objects. In-memory caches map old entries and commits to rewritten values; a mutex guards those maps.

Dependencies/integration: depends on `gitobj`, `git.NewRevListScanner`, `filepathfilter`, `tasklog`, and `refUpdater`. It is a core integration point for migration commands that need to rewrite repository history.

Risks/test signals: rewriting Git history is high blast-radius. Risks include callback errors, incorrectly preserving partial migration parents, cache key mistakes for same-content different paths, symlink handling, filter semantics, and ref update failures after objects are written. Tests cover linear history, octopus merges, packed objects, repeated and identical blobs, filters with cache, tree callbacks adding entries, callback order/errors, partial migrations, ref updates, and filter identity.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/rewriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/rewriter_test.go -->
# sources/sync-backup/git-lfs/git/githistory/rewriter_test.go

Purpose: comprehensive tests for history rewriting semantics.

Important APIs/types/functions: `NewRewriter`, `Rewrite`, `RewriteOptions`, `BlobFn`, `TreePreCallbackFn`, `TreeCallbackFn`, `WithFilter`, assertion helpers, and `CallbackCall`.

Control flow: tests rewrite fixture histories with blob transforms, tree additions, filters, callback collectors, and ref updates, then assert exact tree IDs, parent IDs, blob contents, visit counts, error propagation, and filter pointer identity.

State/persistence behavior: writes new objects and refs into temp fixture copies. Some tests rely on packed-object fixtures and annotated ancestry.

Dependencies/integration: uses fixture repositories and `gitobj`; tests exact SHA outputs, so they validate deterministic object writing and commit header preservation.

Risks/test signals: excellent coverage for core rewriting, but expensive and fixture-coupled. Exact SHA assertions are strong regression signals but require updates if fixture histories or object serialization changes intentionally.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/githistory/rewriter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/ls_files.go -->
# sources/sync-backup/git-lfs/git/ls_files.go

Purpose: wraps `git ls-files -z` to collect cached and optionally untracked file paths, indexed by full path and basename.

Important APIs/types/functions: `lsFileInfo`, `LsFiles`, and `NewLsFiles`.

Control flow: builds `git ls-files -z --cached` arguments, adds `--sparse` for Git 2.35+, optional `--exclude-standard` and `--others`, runs in `workingDir`, scans stdout split on NUL, drains stderr concurrently, and waits for command completion.

State/persistence behavior: read-only query of Git index and working tree. Returned maps persist full path and basename grouping in memory.

Dependencies/integration: depends on `gitNoLFS`, `tools.SplitOnNul`, Git version checks, and is used by gitattr file discovery to locate `.gitattributes`.

Risks/test signals: large stderr is drained to prevent deadlock. Errors include stderr text. Behavior depends on Git version and current index state.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/ls_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/ls_tree_scanner.go -->
# sources/sync-backup/git-lfs/git/ls_tree_scanner.go

Purpose: parses NUL-delimited `git ls-tree` or compatible output into blob entries with OID, size, mode, and filename.

Important APIs/types/functions: `TreeBlob`, `LsTreeScanner`, `NewLsTreeScanner`, `TreeBlob`, `Scan`, `next`, and `scanNullLines`.

Control flow: scanner splits on NUL, separates metadata from filename at tab, parses mode and size, ignores non-blob entries or malformed lines by returning nil with the current scan state, and stores the current `TreeBlob`.

State/persistence behavior: in-memory stream parser only. No subprocess ownership is handled here.

Dependencies/integration: consumed by LFS tree scanners in `lfs/gitscanner_tree.go`.

Risks/test signals: `Err` always returns nil and malformed lines are skipped silently, so callers only see missing entries. Tests cover paths with spaces and non-ASCII characters plus benchmark basic parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/ls_tree_scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/ls_tree_scanner_test.go -->
# sources/sync-backup/git-lfs/git/ls_tree_scanner_test.go

Purpose: verifies and benchmarks `LsTreeScanner` parsing.

Important APIs/types/functions: `NewLsTreeScanner`, `TreeBlob`, generic scanner helper assertions, and `BenchmarkLsTreeParser`.

Control flow: feeds two NUL-delimited ls-tree records and asserts OIDs and filenames, including a filename containing spaces and a non-ASCII character. The benchmark repeatedly scans the same sample.

State/persistence behavior: in-memory only.

Dependencies/integration: supports confidence for `gitscanner_tree.go` tree-walking code.

Risks/test signals: narrow coverage; does not test malformed lines, non-blob entries, size/mode parsing failures, or scanner buffer limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/ls_tree_scanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/object_scanner.go -->
# sources/sync-backup/git-lfs/git/object_scanner.go

Purpose: object database scanner for loading arbitrary Git objects by OID, with blob contents and size exposed for pointer detection.

Important APIs/types/functions: `ObjectScanner`, `NewObjectScanner`, `NewObjectScannerFrom`, `Scan`, `Close`, `Contents`, `Sha1`, `Size`, `Type`, `Err`, `IsMissingObject`, and `missingErr`.

Control flow: `Scan` resets/close previous object, decodes the hex OID, loads it through `gitobj.ObjectDatabase`, maps no-such-object to `missingErr`, and exposes blob contents/size when the object is a blob. `Close` resets and closes the object database.

State/persistence behavior: read-only object access but owns closable object handles. Previous object resources are closed before each scan.

Dependencies/integration: used by LFS `PointerScanner` and tree scanning; depends on `GitCommonDir`, `ObjectDatabase`, and `gitobj`.

Risks/test signals: `mustDecode` ignores decode errors, so malformed OIDs may become invalid byte slices passed to `gitobj`. Accessors assume a successful scan set `s.object`. Missing object classification is available for callers.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/object_scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/refs.go -->
# sources/sync-backup/git-lfs/git/refs.go

Purpose: models a push ref update, deriving the remote destination ref from Git config and local ref when not explicitly supplied.

Important APIs/types/functions: `RefUpdate`, `NewRefUpdate`, `LocalRef`, `LocalRefCommitish`, `RemoteRef`, `defaultRemoteRef`, `TrackingRef`, `RemoteRefCommitish`, and `Env`.

Control flow: `RemoteRef` lazily computes a default using `push.default`. `simple` and empty use tracking ref only when branch remote matches target remote, otherwise current branch. `upstream`/`tracking` use branch merge config. `current` uses local ref. Unsupported modes log a warning and fall back to local ref.

State/persistence behavior: read-only access to config via `Env`. The computed remote ref is cached on the `RefUpdate`.

Dependencies/integration: used by `GitFilter.RemoteRef` to set transfer queue remote-ref metadata during smudge/download.

Risks/test signals: support is intentionally partial for push.default modes; unsupported modes silently degrade with trace logging. Tests cover default, tracking, current, and explicit refs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/refs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/refs_test.go -->
# sources/sync-backup/git-lfs/git/refs_test.go

Purpose: unit tests for `RefUpdate` remote-ref derivation and commitish behavior.

Important APIs/types/functions: `NewRefUpdate`, `ParseRef`, `LocalRefCommitish`, `RemoteRef`, `RemoteRefCommitish`, and `mapEnv`.

Control flow: table-like loops create map-backed config and assert the derived remote ref name/type for `push.default` variants. Explicit refs test SHA-vs-name commitish output.

State/persistence behavior: in-memory config only.

Dependencies/integration: validates behavior used by LFS transfer queue remote-ref selection.

Risks/test signals: does not cover unsupported push.default values or nil local refs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/refs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/rev_list_scanner.go -->
# sources/sync-backup/git-lfs/git/rev_list_scanner.go

Purpose: constructs and parses `git rev-list` scans for objects or commits across include/exclude refs, all refs, or ranges relative to remotes.

Important APIs/types/functions: `ScanningMode`, `RevListOrder`, `ScanRefsOptions`, `RevListScanner`, `NewRevListScanner`, `revListArgs`, `includeExcludeShas`, `nonZeroShas`, `Scan`, `OID`, `Name`, `Err`, and `Close`.

Control flow: argument construction adds `--objects` unless commits-only, reverse/order flags, mode-specific traversal flags and stdin content, then runs `git rev-list --stdin --`. The scanner parses each output line, extracts a leading object ID via regex, decodes it, and stores any trailing name. `Close` waits on the command and promotes ambiguous-ref warnings to errors.

State/persistence behavior: subprocess-backed read-only scan. `ScanRefsOptions.Names` can be shared across goroutines with a mutex.

Dependencies/integration: used by `githistory.Rewriter` for topological commit selection and by LFS ref scanners for object discovery.

Risks/test signals: scanner buffer is default `bufio.Scanner` size; very long path lines could be an issue. Ambiguous refs are treated as fatal only at `Close`, so callers must close. Tests cover args, close behavior, and line parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/rev_list_scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/rev_list_scanner_test.go -->
# sources/sync-backup/git-lfs/git/rev_list_scanner_test.go

Purpose: tests `revListArgs` construction and `RevListScanner` parser/close behavior.

Important APIs/types/functions: `ArgsTestCase`, `revListArgs`, `RevListScanner.Close`, `Scan`, `OID`, `Name`, and `ScanRefsOptions`.

Control flow: many cases assert expected stdin and Git args for scan modes, skip-deleted, remote ranges, skipped refs, order flags, commits-only, reverse, and unknown mode errors. Additional tests assert optional close function behavior and parsing lines with or without names.

State/persistence behavior: in-memory only; no Git subprocess is launched in these tests.

Dependencies/integration: provides contract coverage for LFS scanners and history rewriter callers that rely on exact rev-list flags.

Risks/test signals: does not test real `git rev-list` close errors, ambiguous warnings, zero SHA filtering assertions directly, or large output.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/rev_list_scanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/version.go -->
# sources/sync-backup/git-lfs/git/version.go

Purpose: caches the installed Git version and compares Git version strings for feature gates.

Important APIs/types/functions: `Version`, `IsGitVersionAtLeast`, and `IsVersionAtLeast`.

Control flow: `Version` uses `sync.Once` around `subprocess.SimpleExec("git", "version")`. `IsGitVersionAtLeast` obtains the cached version and calls `IsVersionAtLeast`. The comparison regex extracts up to major/minor/patch numbers, scales them into a comparable integer, and ignores suffixes.

State/persistence behavior: process-global cached version and error. No file writes.

Dependencies/integration: used throughout this group for feature gates such as `git ls-files --sparse`, `git var GIT_ATTR_SYSTEM`, update-ref transactions, and worktree tests.

Risks/test signals: regex uses `.` unescaped for separators, so it is permissive beyond literal dots. Versions with components above 999 can collide with scale assumptions. Tests in `git_test.go` cover common comparisons.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/attribute.go -->
# sources/sync-backup/git-lfs/lfs/attribute.go

Purpose: installs and uninstalls Git config entries for the `filter.lfs` clean/smudge/process filter, including skip-smudge variants and upgradeable historical values.

Important APIs/types/functions: `Attribute`, `FilterOptions`, `Install`, `Uninstall`, `filterAttribute`, `skipSmudgeFilterAttribute`, `normalizeKey`, `set`, and `shouldReset`.

Control flow: `FilterOptions.Install` chooses normal or skip-smudge attributes. `Attribute.Install` iterates desired properties, normalizes keys, reads the current value from local/worktree/system/file/global scope, and sets it if forced, empty, or upgradeable. Otherwise mismatched existing values produce errors. Uninstall removes the whole `filter.lfs` section from the selected scope and verifies no properties remain in `FilterOptions.Uninstall`.

State/persistence behavior: writes Git config in the chosen scope and can remove config sections. This directly changes repository/user/system filter behavior.

Dependencies/integration: depends on `git.Configuration`, localized errors, and command install/uninstall flows.

Risks/test signals: system/worktree/file writes can be destructive if scoped incorrectly. Iteration over map properties is unordered, so partial configuration is possible if a later key fails. Upgradeable values are explicit and must be maintained as command syntax changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/attribute.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/config.go -->
# sources/sync-backup/git-lfs/lfs/config.go

Purpose: centralizes fetch/prune-related Git LFS configuration with defaults.

Important APIs/types/functions: `FetchPruneConfig` and `NewFetchPruneConfig`.

Control flow: reads keys from `config.Environment`, defaults prune remote to `origin`, and fills integer/boolean fields for recent refs, recent commits, prune offsets, remote verification, and flags initialized for command overrides.

State/persistence behavior: read-only config snapshot in memory.

Dependencies/integration: used by `lfs.Environ` and fetch/prune commands to expose consistent policy.

Risks/test signals: typo in comments only (`verifiying`). Tests cover default and custom config values.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/config_test.go -->
# sources/sync-backup/git-lfs/lfs/config_test.go

Purpose: tests default and custom `FetchPruneConfig` construction.

Important APIs/types/functions: `NewFetchPruneConfig`, `config.NewFrom`, and `testify/assert`.

Control flow: one test constructs empty config and asserts defaults; another supplies Git config values and asserts parsed overrides.

State/persistence behavior: in-memory config only.

Dependencies/integration: guards environment reporting and fetch/prune behavior from silent default changes.

Risks/test signals: does not test invalid integer/boolean parsing or command-layer overrides for `PruneRecent` and `PruneForce`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/diff_index_scanner.go -->
# sources/sync-backup/git-lfs/lfs/diff_index_scanner.go

Purpose: parses `git diff-index` output into structured entries for index scanning.

Important APIs/types/functions: `DiffIndexStatus`, status constants, `String`, `Format`, `DiffIndexEntry`, `DiffIndexScanner`, `NewDiffIndexScanner`, `Scan`, `Entry`, `Err`, and internal `scan`.

Control flow: `NewDiffIndexScanner` obtains a scanner from `git.DiffIndex`. `Scan` advances a line, parses mode/sha/status/name fields, wraps parse errors, and exposes the current entry. Rename/copy destination names are taken from a third tab-separated field.

State/persistence behavior: read-only subprocess output parser. It may trigger Git index refresh depending on caller options in `git.DiffIndex`.

Dependencies/integration: used by `gitscanner_index.go` to map modified index entries to blob SHAs and filenames.

Risks/test signals: likely bug: `if score, err := strconv.Atoi(desc[4][1:]); err != nil { entry.StatusScore = score }` sets score only when parsing failed, so valid scores are dropped. Formatting panics on unsupported verbs. No direct tests in this group cover parser edge cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/diff_index_scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/extension.go -->
# sources/sync-backup/git-lfs/lfs/extension.go

Purpose: pipes clean or smudge data through configured external Git LFS extensions while tracking SHA-256 transformations.

Important APIs/types/functions: `pipeRequest`, `pipeResponse`, `pipeExtResult`, `extCommand`, and `pipeExtensions`.

Control flow: command strings are split on spaces, `%f` is replaced with the filename, subprocesses are chained, input is copied through a pipe while hashing original data, each extension stdout is hashed, output lands in a temp file, processes are waited, outputs are closed, and per-extension input/output OIDs are recorded.

State/persistence behavior: starts external processes and writes a temp file via `TempFile`. A defer kills any started processes on early return. The response owns the temp file path for later clean/smudge use.

Dependencies/integration: used by `GitFilter.Clean` and `readLocalFile` during smudge. Depends on extension config, subprocess management, SHA-256, and temp-file helpers.

Risks/test signals: command splitting is simple and does not honor shell quoting. `extcmds[0]` assumes at least one extension, which callers satisfy. Error buffering is only wired for non-last extension commands, so last-command stderr may be less informative. Extension OID verification in smudge mitigates transformation drift.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/extension.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitfilter.go -->
# sources/sync-backup/git-lfs/lfs/gitfilter.go

Purpose: small holder for Git LFS clean/smudge operations with configuration, filesystem, and clock dependencies.

Important APIs/types/functions: `GitFilter`, `NewGitFilter`, `ObjectPath`, and `RemoteRef`.

Control flow: constructor pulls filesystem from config and a real clock. `ObjectPath` delegates to the filesystem. `RemoteRef` builds a `git.RefUpdate` from current and push remote config to determine the destination ref for transfer metadata.

State/persistence behavior: no direct writes; methods expose paths and config-derived ref state.

Dependencies/integration: used by clean/smudge files and transfer queue setup.

Risks/test signals: `RemoteRef` depends on current ref and push config being initialized; nil or detached states rely on lower-level git helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitfilter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitfilter_clean.go -->
# sources/sync-backup/git-lfs/lfs/gitfilter_clean.go

Purpose: implements the Git clean filter path: convert working-file content into a Git LFS pointer and store content in a temp file for later object storage.

Important APIs/types/functions: `cleanedAsset`, `GitFilter.Clean`, `copyToTemp`, and `cleanedAsset.Teardown`.

Control flow: `Clean` loads sorted extensions; with extensions, it pipes through them, uses the final output OID and temp file size, and records pointer extensions for changed transformations. Without extensions, `copyToTemp` hashes and copies input to a temp file. `copyToTemp` first tries to decode existing pointer-like input and returns a clean-pointer error for small canonical pointer data to avoid double-cleaning.

State/persistence behavior: writes temp files and returns their names; `Teardown` removes them. Actual LFS object storage happens outside this file.

Dependencies/integration: depends on `DecodeFrom`, pointer encoding, SHA-256, temp-file helpers, extension piping, and progress callbacks.

Risks/test signals: clean-pointer detection depends on `blobSizeCutoff` and partial buffering. Callback is disabled when file size is unknown/nonpositive. Extension results influence pointer extension metadata and must align with smudge verification.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitfilter_clean.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitfilter_smudge.go -->
# sources/sync-backup/git-lfs/lfs/gitfilter_smudge.go

Purpose: implements smudge checkout/download behavior: replace an LFS pointer with local or downloaded content, applying reverse extensions when needed.

Important APIs/types/functions: `SmudgeToFile`, `Smudge`, `downloadFile`, `downloadFileFallBack`, and `readLocalFile`.

Control flow: `SmudgeToFile` removes and recreates the working file preserving mode when possible, then calls `Smudge`; download-declined errors write the pointer placeholder. `Smudge` resolves media path, links/copies from references, validates local object size, downloads if missing and allowed, optionally falls back across remotes, then streams local content. `readLocalFile` applies configured extensions in reverse priority order and verifies extension names/order/OIDs before copying to output.

State/persistence behavior: mutates working-tree files, LFS media files, and config remote selection on successful fallback. Downloads use transfer queues and may create object files.

Dependencies/integration: depends on filesystem helpers, transfer queue manifest, config remotes, `RemoteRef`, pointer extension metadata, progress callbacks, and error wrappers.

Risks/test signals: high user-visible risk: corrupt local objects are deleted on size mismatch, downloads can fail, fallback mutates selected remote, and extension mismatch aborts smudge. Placeholder writing on declined download preserves Git checkout progress.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitfilter_smudge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner.go

Purpose: public dispatcher for scanning Git history, refs, trees, index, stashes, and previous versions for LFS pointers.

Important APIs/types/functions: `GitScanner`, `GitScannerFoundPointer`, `GitScannerFoundLockable`, `GitScannerSet`, `NewGitScanner`, `NewGitScannerForPush`, all `Scan*` methods, and `firstGitScannerCallback`.

Control flow: each method resolves a callback, sets mode flags such as range-to-remote, skip-deleted, or commits-only, then delegates to specialized helpers (`scanRefsToChan`, `scanRefsByTree`, `runScanTree`, `scanUnpushed`, `logPreviousSHAs`, `scanIndex`). Performance timings are traced.

State/persistence behavior: scanner methods mutate the receiver's mode flags, remote/skipped refs, and callback fields. Scanning itself is read-only except for underlying Git commands that may refresh indexes in some paths.

Dependencies/integration: central integration point for `git/rev-list`, `git cat-file`, `git ls-tree`, log parsing, filepath filters, push lockable checks, and config environments.

Risks/test signals: receiver is stateful and not safe to reuse concurrently across scan types without resetting flags. Missing callbacks return a sentinel error. Tests in this group cover pointer scanner pieces; broader scanner behavior is covered in other files not in this work item.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatch.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatch.go

Purpose: loads Git blobs by SHA and detects whether their content is an LFS pointer.

Important APIs/types/functions: `runCatFileBatch`, `PointerScanner`, `NewPointerScanner`, `Scan`, `Pointer`, `BlobSHA`, `ContentsSha`, `Err`, `Close`, and `next`.

Control flow: `runCatFileBatch` consumes blob SHA strings, scans each with `PointerScanner`, sends decoded pointers, reports lockable non-pointers, propagates errors, waits on upstream channels, closes scanner and output channels. `PointerScanner.next` loads the object, hashes contents, buffers only blobs below `blobSizeCutoff`, decodes pointers for small blobs, and records either pointer OID or content hash.

State/persistence behavior: read-only object database access, but owns scanner resources and channels.

Dependencies/integration: built on `git.ObjectScanner`, `DecodePointer`, SHA-256, and lockable name lookup. Used by ref, index, and tree scanners.

Risks/test signals: large blobs are never pointer-decoded by design. Exact-size reads are enforced. Tests cover valid pointer interleaved with random data and large blob hash behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheck.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheck.go

Purpose: first-stage filter over Git object IDs using `git cat-file --batch-check`, passing only small blobs to pointer decoding while separately detecting large lockable blobs.

Important APIs/types/functions: `runCatFileBatchCheck`, `catFileBatchCheckScanner`, `LFSBlobOID`, `GitBlobOID`, `Scan`, `Err`, and `next`.

Control flow: a goroutine writes each upstream SHA to cat-file stdin, scans one response, sends small blob IDs to `smallRevCh`, checks lockable names for large blobs, waits on upstream, closes stdin, waits on cat-file, and closes channels. The parser expects `<hash> blob <size>`, ignores non-blobs/malformed sizes, and classifies size below cutoff as possible LFS pointer.

State/persistence behavior: read-only subprocess interaction with channels.

Dependencies/integration: used before `catFileBatch` in ref/index scanning to avoid reading large objects unnecessarily.

Risks/test signals: assumes one cat-file output line per input and does not handle process write errors directly. Tests cover malformed lines, capitalized type, invalid size, small blob, malformed extra size, and large blob classification.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheckscanner_test.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheckscanner_test.go

Purpose: unit tests for `catFileBatchCheckScanner` line parsing.

Important APIs/types/functions: `catFileBatchCheckScanner.Scan`, `LFSBlobOID`, `GitBlobOID`, and helper assertions.

Control flow: feeds representative cat-file lines and asserts whether each line yields a small LFS candidate, a large Git blob candidate, or neither.

State/persistence behavior: in-memory scanner only.

Dependencies/integration: supports the scan pipeline's first-stage object-size filter.

Risks/test signals: tests parser only, not live `git cat-file` subprocess behavior or channel closing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheckscanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_index.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_index.go

Purpose: scans changed index/worktree entries for LFS pointer blobs and reports them with filename and status metadata.

Important APIs/types/functions: `scanIndex`, `revListIndex`, `indexFile`, `indexFileMap`, `FilesFor`, and `Add`.

Control flow: builds an `indexFileMap`, runs `diff-index` once for working tree and once for cached/index changes, merges unique destination SHAs, filters small blobs with batch-check, decodes pointers with cat-file batch, expands each pointer to all filenames mapped to that blob, and calls back for paths allowed by the filter.

State/persistence behavior: read-only scanning except possible Git index interaction from `DiffIndex`. The map deduplicates SHA/name pairs and is mutex-protected for goroutines.

Dependencies/integration: depends on `DiffIndexScanner`, cat-file batch helpers, filepath filters, and `WrappedPointer` status fields.

Risks/test signals: filter callback assumes `result.Pointer` is non-nil; errors from bare pointer channel are sent as a result after pointer loop but then dereferenced in the final loop path only for pointer results. The diff-index score parsing bug can affect status score consumers, though this file stores status only.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_log.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_log.go

Purpose: scans `git log -p` output for LFS pointer additions or deletions, supporting unpushed, stashed, and previous-version scans.

Important APIs/types/functions: `LogDiffDirection`, `logLfsSearchArgs`, `scanUnpushed`, `scanStashed`, `parseScannerLogOutput`, `logPreviousSHAs`, `logScanner`, `newLogScanner`, `Scan`, `finishLastPointer`, and `setFilename`.

Control flow: Git log commands are constructed with no external diff/textconv, no color, `-G oid sha256:`, patch context, and a custom commit header. `parseScannerLogOutput` drains stderr concurrently, scans pointers, waits on the command, and calls back. `logScanner` tracks commit/file diff boundaries, collects pointer lines from either additions or deletions plus context, decodes complete pointer blocks, unquotes filenames, and applies filters.

State/persistence behavior: read-only Git log subprocess scanning. Stash scan runs two log passes for merge-parent semantics.

Dependencies/integration: depends on `git.Log`, `DecodePointer`, filepath filters, subprocess buffered command, and tracer logging.

Risks/test signals: parser is regex- and diff-format-sensitive. `setFilename` calls `s.Filter.Allows(name)` without nil guard, so callers must provide a non-nil filter or rely on wrapper defaults elsewhere. Stash scan ignores `git log` errors when no stash exists. Tests outside this listed file cover log scanner additions/deletions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_pointerscanner_test.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_pointerscanner_test.go

Purpose: tests `PointerScanner` over in-memory Git objects.

Important APIs/types/functions: `PointerScanner.Scan`, `Pointer`, `ContentsSha`, `git.NewObjectScannerFrom`, `gitobj.NewMemoryBackend`, `fakeObjectsWithRandoData`, and `writeFakeBuffer`.

Control flow: creates random non-pointer blobs and encoded pointer blobs, writes them to an in-memory object database, scans them sequentially, and asserts pointer detection only for actual pointer blobs. A separate large-blob test verifies no pointer is produced and `ContentsSha` equals the content hash.

State/persistence behavior: in-memory object database only.

Dependencies/integration: validates interaction between `PointerScanner`, `ObjectScanner`, pointer encoding/decoding, and blob size cutoff.

Risks/test signals: deterministic random source makes tests reproducible. It does not cover missing objects, object close errors, or malformed pointer errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_pointerscanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_refs.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_refs.go

Purpose: implements ref/range scanning pipeline for unique Git objects and optional per-tree scanning.

Important APIs/types/functions: `nameMap`, `lockableNameSet`, `scanRefsToChan`, `scanRefsToChanSingleIncludeExclude`, `scanRefsToChanSingleIncludeMultiExclude`, `scanRefsByTree`, and `revListShas`.

Control flow: `revListShas` runs `git.NewRevListScanner`, records object names by SHA, and streams SHA strings. `scanRefsToChan` filters small blobs with batch-check, reports lockable large blobs, decodes pointers, assigns names from the map, applies the scanner filter, and forwards pointer errors. `scanRefsByTree` scans each commit/tree SHA concurrently using `runScanTreeForPointers`.

State/persistence behavior: read-only Git scans with goroutines and channels. Name maps are mutex-protected.

Dependencies/integration: ties together `GitScanner`, rev-list scanner, cat-file batch stages, lockable callbacks, and filepath filters.

Risks/test signals: unique-object mode loses duplicate path information by design, while by-tree mode is more expensive and concurrent. Callback/filter nil handling depends on scanner initialization. Errors can arrive from multiple asynchronous stages.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_refs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_remotes.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_remotes.go

Purpose: computes remote refs to exclude or explicitly skip when scanning objects to push.

Important APIs/types/functions: `calcSkippedRefs`.

Control flow: loads cached remote branch refs and actual remote branch refs, builds a set of actual names, and returns `^<sha>` entries for cached refs still present on the remote.

State/persistence behavior: read-only remote/ref queries. Network access may occur through `git.RemoteRefs` depending on Git helper behavior.

Dependencies/integration: used by `NewGitScannerForPush` range-to-remote scans to avoid assuming deleted remote branches still protect objects.

Risks/test signals: errors from `CachedRemoteRefs` and `RemoteRefs` are ignored, resulting in empty or partial skips. Comments indicate this is a conservative strategy around remote garbage collection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_remotes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_tree.go -->
# sources/sync-backup/git-lfs/lfs/gitscanner_tree.go

Purpose: scans trees or index/listed LFS files for pointers, preserving per-path information and validating `.gitattributes` expectations.

Important APIs/types/functions: `runScanTree`, `runScanLFSFiles`, `catFileBatchTree`, `lsTreeBlobs`, `lsBlobs`, `lsFilesBlobs`, `catFileBatchTreeForPointers`, and `runScanTreeForPointers`.

Control flow: tree scans list candidate blobs via `git ls-tree` or, for Git 2.42+ LFS files, `git ls-files`, filter by size/path, decode with `PointerScanner`, and callback pointers. The pointer-validation path also reads `.gitattributes` blobs with `ObjectScanner`, constructs include/exclude filters from `gitattr.AttributePath`, records nil for non-pointers, and reports errors for files that attributes say should be LFS pointers but are plain Git blobs.

State/persistence behavior: read-only object and Git command scanning. It opens and closes object scanners and consumes channel wrappers.

Dependencies/integration: depends on `git.LsTree`, `git.LsFilesLFS`, `git.NewLsTreeScanner`, pointer scanner, object scanner, `gitattr`, and filepath filters.

Risks/test signals: by-tree validation can be expensive and must avoid deadlocks by not waiting on upstream channels after early scanner failure. Attribute macro reading is limited to top-level `.gitattributes` for macro definitions in this path. Errors are reported through callbacks for not-a-pointer cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/gitscanner_tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/hook.go -->
# sources/sync-backup/git-lfs/lfs/hook.go

Purpose: manages standard Git LFS hook scripts, including install, upgrade, and uninstall behavior.

Important APIs/types/functions: hook content constants, `Hook`, `LoadHooks`, `NewStandardHook`, `Exists`, `Path`, `Install`, `write`, `Upgrade`, `Uninstall`, and `matchesCurrent`.

Control flow: `LoadHooks` constructs pre-push, post-checkout, post-commit, and post-merge hooks with current content and upgradeable historical variants. `Install` creates the hook dir and writes or upgrades based on existence and force. `Upgrade` writes only if current contents match known upgradeable content. `Uninstall` removes only matching current/upgradeable hooks. `matchesCurrent` reads up to 1024 bytes, trims/undents, and compares.

State/persistence behavior: writes executable hook files, creates directories, and removes hooks from disk.

Dependencies/integration: depends on config-aware `tools.MkdirAll`, file IO, tracer logging, and localized errors. Used by install/uninstall commands.

Risks/test signals: protects user hooks by refusing to overwrite/delete unknown content unless forced install writes directly. The 1024-byte read limit can misclassify very large hooks. Content matching is exact after trim/undent, so small edits prevent automatic upgrade/uninstall.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/hook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/lfs.go -->
# sources/sync-backup/git-lfs/lfs/lfs.go

Purpose: package-level LFS environment reporting, tracing initialization, and reference-object linking.

Important APIs/types/functions: `Environ`, `init`, constants `gitExt`/`gitPtrPrefix`, and `LinkOrCopyFromReference`.

Control flow: `Environ` builds diagnostic/config environment lines from local paths, API transfer settings, endpoint access modes, manifest adapter names, fetch/prune config, include/exclude paths, extensions, and existing `GIT_` environment variables with overrides. `init` configures tracer defaults and maps transfer/curl trace env vars to `GIT_TRACE` when absent. `LinkOrCopyFromReference` checks whether an object already exists, then searches reference object paths and links/copies the first matching object into local media storage.

State/persistence behavior: `init` may set `GIT_TRACE` in process environment. `LinkOrCopyFromReference` can write/link local object files. `Environ` reads config and OS environment only.

Dependencies/integration: uses `config`, `lfsapi`, transfer queue manifests, filesystem helpers, and `tools.FileExistsOfSize`.

Risks/test signals: environment output can expose local paths and transfer settings. Reference linking must preserve object size correctness. Tests in `lfs_test.go` validate object enumeration through filesystem storage rather than this function directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/lfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/lfs_test.go -->
# sources/sync-backup/git-lfs/lfs/lfs_test.go

Purpose: tests current LFS object storage enumeration in temporary repositories.

Important APIs/types/functions: repository helper `NewRepo`, filesystem `EachObject`, `fs.Object`, `lfs.NewPointer`, and pointer sort helpers.

Control flow: first test asserts a new repo has no LFS objects. Second creates a commit with 20 unique files, collects expected pointers from commit helper output, enumerates object storage, converts objects to pointers, sorts both lists, and compares.

State/persistence behavior: creates temp repositories and LFS object files through test commit helpers.

Dependencies/integration: validates filesystem storage integration used by broader LFS commands.

Risks/test signals: does not directly test `Environ` or `LinkOrCopyFromReference`; it tests object presence after repository helper operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/lfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/pointer.go -->
# sources/sync-backup/git-lfs/lfs/pointer.go

Purpose: encodes and decodes Git LFS pointer files, including legacy version aliases and pointer extension metadata.

Important APIs/types/functions: `Pointer`, `PointerExtension`, `ByPriority`, `NewPointer`, `NewPointerExtension`, `Encode`, `Encoded`, `EmptyPointer`, `EncodePointer`, `DecodePointerFromBlob`, `DecodePointerFromFile`, `DecodePointer`, `DecodeFrom`, `verifyVersion`, `decodeKV`, `parseOid`, `parsePointerExtension`, `validatePointerExtensions`, and `decodeKVData`.

Control flow: encoding emits canonical version, extension lines, OID, and size, but returns an empty string for size zero. Decoding reads up to `blobSizeCutoff`, preserves a reader for the full original data on failure, rejects empty input as an empty pointer, parses ordered key/value lines, validates version aliases, OID type/hash, size, extension priority/name/OID, rejects duplicate priorities, sorts extensions, and marks canonical pointers by comparing encoded output to input.

State/persistence behavior: file/blob decoders read from disk or object streams and enforce regular-file and size-cutoff checks. No writes except through encode writer.

Dependencies/integration: central to clean/smudge filters and all scanners. Depends on Git LFS errors, filesystem empty object SHA, and `gitobj.Blob`.

Risks/test signals: parser requires strict key order except extension lines; extra lines and bad keys become not-a-pointer or bad-pointer errors. `Encoded` returning empty for zero-size pointers is an important special case. Extension key regex only allows one digit of priority, while parser later accepts nonnegative integer after splitting, so high priorities may be rejected at key validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/pointer.go -->
