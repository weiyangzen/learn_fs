# Group Research: subset-b-009162

This grouped report covers the requested restic source files under `internal/fuse`, `internal/global`, `internal/migrations`, `internal/options`, and `internal/repository`. Each file section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/fuse_test.go -->
## sources/sync-backup/restic/internal/fuse/fuse_test.go

Purpose: integration and unit coverage for the Unix FUSE implementation. The tests build in-memory test repositories, create snapshots, and exercise file reads, directory attrs, UID/GID presentation, stable FUSE node caching, block counts, hard-link inode generation, symlink xattrs, and inode benchmarks.

Important APIs and helpers: `testRead` adapts `fs.HandleReader` to synthetic `fuse.ReadRequest`; `firstSnapshotID`, `loadFirstSnapshot`, and `loadTree` pull snapshot/tree data from repository fixtures. `TestFuseFile` constructs a `data.Node`, opens it through `newFile`, and validates random reads against concatenated blob contents. `TestFuseDir`, `TestTopUIDGID`, and `testTopUIDGID` validate attribute propagation from `data.Node` and mount config. `testStableLookup` verifies `treeCache` object identity until `Forget`. `TestBlocks`, `TestFileAttrNlink`, `TestInodeFromNode`, and `TestLink` cover stat details, POSIX compatibility, inode rules, and xattr lookup.

Control flow and state: tests create repository state with `repository.TestRepository` and `data.TestCreateSnapshot`, load repository indexes where needed, and then instantiate FUSE nodes directly rather than mounting a kernel filesystem. Cache-sensitive checks call `Forget` to force eviction and confirm a later lookup constructs a new node object.

Dependencies and integration points: this file exercises `bloblru`, `data`, `repository`, `restic`, `anacrolix/fuse`, `anacrolix/fuse/fs`, and restic test helpers. It reaches unexported FUSE constructors, so it is tightly coupled to the package internals.

Risks and test signals: the suite catches regressions that would break user-visible mounted filesystem behavior, especially block accounting, UID/GID choice, hard-link inode stability, and xattr forwarding. It does not mount through the OS FUSE driver, so kernel integration, permissions enforcement, and platform-specific filesystem behavior remain outside this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/fuse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/inode.go -->
## sources/sync-backup/restic/internal/fuse/inode.go

Purpose: deterministic inode generation for FUSE pseudo directories and snapshot contents on Darwin, FreeBSD, and Linux builds.

Important APIs: `inodeFromName(parent, name)` hashes a cleaned filename with its parent inode using xxhash and a fixed prime. `inodeFromNode(parent, node)` uses `(DeviceID, Inode)` for non-directory hard links so all hard-link instances share one inode; otherwise it hashes the cleaned node name with the parent inode. Both remap inode values `0` and `1` away from invalid/root-reserved values.

Control flow and state: this file is pure computation and has no persistence. It relies on `cleanupNodeName` from the FUSE directory code before hashing names, so character normalization in that helper affects inode stability.

Dependencies and integration points: imports `encoding/binary`, `github.com/cespare/xxhash/v2`, and `data.Node`. Results feed `fuse.Attr.Inode` in file, directory, symlink, other-node, and snapshot-directory paths.

Risks and test signals: collision risk is bounded by 64-bit hashing but not impossible; inode stability depends on preserving the hash algorithm and cleanup behavior. `TestInodeFromNode` covers hard-link same-inode behavior and a regression where nested repeated names could collide with ancestors. `BenchmarkInode` tracks allocation/performance expectations.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/inode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/link.go -->
## sources/sync-backup/restic/internal/fuse/link.go

Purpose: FUSE node implementation for symlinks restored from snapshot metadata.

Important APIs/types: `link` stores `root`, `forget`, `node`, and `inode`. It implements `fs.NodeForgetter`, `fs.NodeGetxattrer`, `fs.NodeListxattrer`, and `fs.NodeReadlinker`. `newLink` constructs the node. `Readlink` returns `node.LinkTarget`. `Attr` fills inode, mode, UID/GID unless `OwnerIsRoot`, access/change/mod times, link count, symlink target size, and 512-byte block count. `Listxattr` and `Getxattr` delegate to `xattr.go`; `Forget` invokes the cache eviction callback.

Control flow and state: the node is immutable after construction except that `Forget` mutates the owning `treeCache` through the callback. Attribute values are derived from the stored `data.Node`.

Dependencies and integration points: called by directory lookup code for `data.NodeTypeSymlink`. It depends on shared constants such as `blockSize` from file handling and on `nodeToXattrList`/`nodeGetXattr` for xattrs.

Risks and test signals: incorrect link target size or xattr forwarding affects tools inspecting mounted snapshots. `TestLink` validates readlink and xattr behavior; `TestBlocks` validates block count. There is no explicit guard for zero `Links`, unlike regular files, so non-POSIX link metadata should be reviewed if symlink link counts can be zero.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/link.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/other.go -->
## sources/sync-backup/restic/internal/fuse/other.go

Purpose: fallback FUSE node for non-regular, non-directory, non-symlink snapshot node types such as devices or FIFOs.

Important APIs/types: `other` stores `root`, `forget`, `node`, and `inode`. `newOther` constructs it. `Readlink` returns `node.LinkTarget`, which may matter for special node metadata. `Attr` exposes inode, mode, optional original UID/GID, timestamps, and link count. `Forget` triggers cache eviction.

Control flow and state: this is a lightweight metadata-only node. It does not implement open/read or xattrs, so the mounted representation is primarily a stat/readlink surface.

Dependencies and integration points: constructed from FUSE directory lookup when a `data.Node` does not map to file, dir, or symlink. It integrates with `Root.cfg.OwnerIsRoot` and `treeCache` forget callbacks.

Risks and test signals: behavior for special files is platform-sensitive and this file has less direct coverage than file/link/dir paths. Incorrect mode or ownership can change how tools classify restored special nodes. Coverage is indirect through FUSE tests and inode tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/root.go -->
## sources/sync-backup/restic/internal/fuse/root.go

Purpose: root object for a restic repository FUSE mount and top-level configuration.

Important APIs/types: `Config` controls ownership display, snapshot filtering, time formatting, and path templates. `Root` holds the repository, config, 64 MiB blob LRU cache, embedded `SnapshotsDir`, and mount UID/GID. `NewRoot` initializes cache, ownership defaults, path-template defaults (`ids/%i`, `snapshots/%T`, `hosts/%h/%T`, `tags/%t/%T`), and the root `SnapshotsDir`. `Root()` satisfies `fs.FS`.

Control flow and state: `NewRoot` copies the input config into `root.cfg`, but default path templates are assigned to the local `cfg` before building `SnapshotsDirStructure`; consumers should not expect `root.cfg.PathTemplates` to reflect those defaults. UID/GID default to current process owner unless `OwnerIsRoot` leaves zero values.

Dependencies and integration points: integrates `restic.Repository`, `bloblru`, `data.SnapshotFilter`, `debug`, and `anacrolix/fuse/fs`. The embedded `SnapshotsDir` handles directory listing and lookup for root paths.

Risks and test signals: root ownership and path-template defaults shape the visible mount. `TestTopUIDGID` validates owner behavior for top-level directories. Blob cache sizing is hard-coded and noted as TODO, so memory-sensitive deployments have no local control here.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/root.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/snapshots_dir.go -->
## sources/sync-backup/restic/internal/fuse/snapshots_dir.go

Purpose: FUSE directory and symlink nodes for the generated snapshot namespace.

Important APIs/types: `SnapshotsDir` stores `Root`, inode metadata, `SnapshotsDirStructure`, a prefix into the metadata tree, and a per-directory `treeCache`. `NewSnapshotsDir` constructs a pseudo directory. `Attr` returns read-only directory attrs. `ReadDirAll` refreshes snapshot metadata for the prefix, emits `.`/`..`, and converts each `MetaDirData` child to `fuse.Dirent`. `Lookup` resolves children into `snapshotLink`, snapshot root directories via `newDirFromSnapshot`, or nested `SnapshotsDir` instances. `snapshotLink` implements a read-only symlink to a generated latest target.

Control flow and state: both listing and lookup call `dirStruct.UpdatePrefix`, so repository snapshot changes are visible after `SnapshotsDirStructure` reload rules permit. Child FUSE nodes are cached by name and removed when their `Forget` callback runs.

Dependencies and integration points: depends on `SnapshotsDirStructure` for logical metadata, `inodeFromName` for stable pseudo inodes, FUSE interfaces, and `newDirFromSnapshot` in the directory implementation for actual snapshot trees. It unwraps context cancellation errors via `unwrapCtxCanceled` from `dir.go`.

Risks and test signals: the `Lookup` cache stores a node by name even though `meta` can be refreshed; stale cached nodes may persist until FUSE forgets them. Directory order is map iteration order, so callers should not rely on stable listing order. Tests cover top-level ownership, stable node objects, block count for latest links, and directory-structure generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/snapshots_dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/snapshots_dirstruct.go -->
## sources/sync-backup/restic/internal/fuse/snapshots_dirstruct.go

Purpose: constructs and refreshes the pseudo directory tree that maps snapshot metadata to user-facing paths such as IDs, timestamps, hosts, users, and tags.

Important APIs/types: `MetaDirData` represents either a pseudo directory (`names`), a snapshot mount point (`snapshot`), or a symlink (`linkTarget`). `SnapshotsDirStructure` stores root/config, a mutex-protected `entries` map, last snapshot hash, and reload timestamp. `pathsFromSn` expands `%T`, `%t`, `%i`, `%I`, `%u`, `%h` templates. `filenameFromTag`, `staticPrefix`, and `uniqueName` sanitize and stabilize generated paths. `makeDirs` builds entries, intermediate directories, static prefixes, mount points, and `latest` links. `updateSnapshots` reloads snapshots, sorts them by time and ID, hashes IDs to detect changes, loads repository index on change, and rebuilds entries. `UpdatePrefix` returns one metadata node for a prefix.

Control flow and state: reloads are throttled by `minSnapshotsReloadTime` (60 seconds). Snapshot IDs are hashed after deterministic sorting; if the hash is unchanged only `lastCheck` is updated. `makeDirs` uses a recursive `mount` closure to populate child pointers and parent directories. Latest links are updated when a snapshot time is not before the recorded latest, so equal timestamps prefer later sorted snapshots.

Dependencies and integration points: depends on `data.SnapshotFilter.FindAll`, `restic.Repository.LoadIndex`, `data.Snapshots`, SHA-256, and FUSE directory consumers. Template expansion directly defines the visible mount tree consumed by `SnapshotsDir`.

Risks and test signals: templates containing path separators in host/user/tag values can shape nested paths; tags are sanitized, but host and username replacements are not sanitized here. Snapshot changes that do not alter IDs do not rebuild metadata. Tests heavily cover template expansion, duplicate timestamp suffixes, latest-link targets, empty static directories, tag filename sanitization, and internal tree integrity.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/snapshots_dirstruct.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/snapshots_dirstruct_test.go -->
## sources/sync-backup/restic/internal/fuse/snapshots_dirstruct_test.go

Purpose: focused unit tests for the snapshot pseudo-directory generator.

Important APIs/tests: `TestPathsFromSn` validates `%i`, `%I`, `%T`, `%t`, `%u`, and `%h` expansion and time suffix behavior. `TestMakeDirs` builds multiple snapshots with shared hosts, tags, and timestamps, then asserts the complete entry map and `latest` symlink targets. `verifyEntries` compares snapshot/link maps and checks parent-child pointer integrity. `TestMakeEmptyDirs` verifies static prefixes for empty repositories. `TestFilenameFromTag` covers tag sanitization.

Control flow and state: tests avoid repository I/O by calling `makeDirs` directly on synthetic `data.Snapshot` values with fixed IDs/times. Expected maps include intermediate directories, snapshot mount points, and latest links.

Dependencies and integration points: uses `data.TestSetSnapshotID`, `restic.ParseID`, and restic test assertions. These tests are the primary specification for `SnapshotsDirStructure` output.

Risks and test signals: the complete expected maps make intentional layout changes expensive but catch subtle regressions in naming, suffix generation, and tree linking. Host and username sanitization are not tested because production code does not sanitize them.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/snapshots_dirstruct_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/tree_cache.go -->
## sources/sync-backup/restic/internal/fuse/tree_cache.go

Purpose: small concurrency-safe cache that keeps FUSE child node object identity stable until FUSE forgets the node.

Important APIs/types: `treeCache` holds `map[string]fs.Node` and a mutex. `forgetFn` is a callback type. `newTreeCache` initializes the map. `lookupOrCreate` returns an existing node or calls a factory with a forget callback that deletes the name from the cache.

Control flow and state: cache entries are protected by `sync.Mutex`; the create callback is called while the mutex is held. The injected `forgetFn` deletes exactly the name being looked up.

Dependencies and integration points: used by snapshot pseudo directories and snapshot tree directories to satisfy FUSE lookup identity expectations. FUSE node implementations call `Forget` to invoke the callback.

Risks and test signals: holding the cache lock during `create` can become a deadlock risk if a constructor synchronously calls back into the same cache, though current constructors do not. `TestStableNodeObjects` validates same-object lookup and post-forget replacement.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/tree_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/xattr.go -->
## sources/sync-backup/restic/internal/fuse/xattr.go

Purpose: shared helpers for exposing stored extended attributes through FUSE.

Important APIs: `nodeToXattrList` appends each `data.Node.ExtendedAttributes` name to a `fuse.ListxattrResponse`. `nodeGetXattr` uses `node.GetExtendedAttribute` and sets `resp.Xattr`, returning `fuse.ErrNoXattr` when absent.

Control flow and state: helpers are stateless and directly reflect metadata stored in `data.Node`. They log attribute operations for debug builds.

Dependencies and integration points: used by file, directory, and symlink FUSE nodes. Depends on `anacrolix/fuse`, `data.Node`, and restic debug logging.

Risks and test signals: response sizing is delegated to the FUSE response API. Missing xattrs must map to the platform FUSE error, which `TestLink` covers for symlinks; other node types rely on shared helper behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global.go -->
## sources/sync-backup/restic/internal/global/global.go

Purpose: central CLI-global configuration, password resolution, repository open/create workflow, backend setup, transport limiting, retry/log wrapping, and cache setup.

Important APIs/types: `Options` holds repository, password, locking, cache, transport, limiter, compression, pack size, terminal, registry, test hooks, and extended backend options. `AddFlags` binds pflag options and environment defaults. `PreRun` applies env overrides for `RESTIC_PACK_SIZE` and `RESTIC_COMPRESSION` unless CLI flags were changed, derives verbosity, parses `-o` options, and optionally resolves password. Password helpers include `resolvePassword`, `LoadPasswordFromFile`, `readPassword`, and `ReadPasswordTwice`. Repository helpers include `readRepo`, `OpenRepository`, `CreateRepository`, `hasRepositoryConfig`, `createRepositoryInstance`, `decryptRepository`, `printRepositoryInfo`, and `setupCache`. Backend helpers include `innerOpenBackend`, `parseConfig`, `setupTransport`, `createOrOpenBackend`, and `wrapBackend`.

Control flow and state: `OpenRepository` reads location, opens backend, verifies config, creates `repository.Repository`, searches keys with up to three interactive attempts, prints repository info, and optionally attaches cache. `CreateRepository` validates version, reads password twice, creates backend, initializes config/key. Backend wrapping order is logger/semaphore, inner test hook, retry, outer test hook. Cache cleanup can remove old cache directories when requested.

Dependencies and integration points: this file sits between Cobra/pflag command setup, backend registries, location parsing, retry/semaphore/logger wrappers, transport TLS/rate limiting, repository initialization/search, cache management, terminal input, and progress printers. `options.Options` feeds backend-specific configuration through reflection.

Risks and test signals: source precedence is security-sensitive: password file and command are mutually exclusive; empty passwords require explicit `--insecure-no-password`; repo and repository-file are mutually exclusive. `readPassword` documents a goroutine leak when context is cancelled during terminal read. Environment parsing fails fast for invalid pack size/compression. Tests cover repo-file reading, empty-password mode, and env-vs-flag precedence.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global_debug.go -->
## sources/sync-backup/restic/internal/global/global_debug.go

Purpose: build-tagged debug/profile support for restic CLI commands.

Important APIs/types: `RegisterProfiling` wraps a Cobra command's `PersistentPreRunE`, starts profiling, registers `cobra.OnFinalize` to stop it, and adds profiling flags. `Profiler` stores selected options and a stop handle. `ProfileOptions` defines HTTP pprof listener, memory/CPU/trace/block profile paths, and insecure KDF toggle. `ProfileOptions.AddFlags` registers debug flags. `Profiler.Start` starts optional pprof HTTP server, enforces only one active file profile, starts `pkg/profile`, and applies low-security KDF settings when requested. `Profiler.Stop` stops the active profile.

Control flow and state: profiling starts after any original pre-run logic succeeds. Stop is global via Cobra finalization instead of per-command post-run. `insecure-kdf` mutates repository test KDF settings and is available only in debug/profile builds.

Dependencies and integration points: imports `net/http/pprof` side effects, `github.com/pkg/profile`, Cobra, pflag, repository test KDF hooks, and restic errors.

Risks and test signals: starting an unauthenticated pprof listener is explicitly debug-only but still security-sensitive. Multiple profile outputs are rejected to avoid conflicting profiler modes. This file has no direct tests in the target set; behavior is build-tag dependent.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global_debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global_release.go -->
## sources/sync-backup/restic/internal/global/global_release.go

Purpose: release-build stub for profiling registration.

Important APIs: `RegisterProfiling(_ *cobra.Command, _ io.Writer)` is a no-op under `!debug && !profile` build tags.

Control flow and state: no state and no side effects. It preserves the same API as `global_debug.go` so command initialization can call `RegisterProfiling` unconditionally.

Dependencies and integration points: imports only `io` and Cobra. Selected by Go build tags in normal releases.

Risks and test signals: risk is minimal; build-tag drift between debug and release files would cause compile errors. No direct tests are needed beyond normal release builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global_release.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global_test.go -->
## sources/sync-backup/restic/internal/global/global_test.go

Purpose: unit tests for repository location reading, empty-password handling, and environment override precedence for global options.

Important tests: `TestReadRepo` covers direct repo path, repository-file reading with trimming, and missing repository-file errors. `TestReadEmptyPassword` validates `InsecureNoPassword` and conflict with supplied password. `TestPackSizeEnvParseError`, `TestPackSizeEnvApplied`, and `TestPackSizeEnvIgnoredWhenFlagSet` cover `RESTIC_PACK_SIZE`. `TestCompressionEnvParseError`, `TestCompressionEnvApplied`, and `TestCompressionEnvIgnoredWhenFlagSet` cover `RESTIC_COMPRESSION`.

Control flow and state: tests use `t.Setenv`, temporary directories, pflag flag sets, and direct calls to unexported helpers in the same package. Flag `Changed` state is used to verify CLI overrides environment values.

Dependencies and integration points: uses restic `errors.IsFatal`, test helpers, `pflag`, and OS file APIs. It validates behavior consumed by all CLI commands.

Risks and test signals: tests protect user-facing configuration precedence and fatal error clarity. They do not cover backend opening, cache cleanup, password-command stderr behavior, or interactive terminal retries.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/global/global_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/global/secondary_repo.go -->
## sources/sync-backup/restic/internal/global/secondary_repo.go

Purpose: option handling for commands that need a second/source repository, including current `from-*` flags and deprecated `repo2` flags.

Important APIs/types: `SecondaryRepoOptions` stores explicit password plus current and legacy repo, repository-file, password-file, password-command, key-hint, and insecure-no-password options. `AddFlags` registers deprecated/hidden legacy flags, current source flags, and environment defaults. `FillGlobalOpts` validates option groups, overlays selected secondary options onto a copy of global `Options`, resolves password with the appropriate env variable, prompts if needed, and returns whether current `from-*` options were used.

Control flow and state: empty options are rejected. Current and legacy groups are mutually exclusive. For current options, `--from-repo` conflicts with `--from-repository-file` and can carry `from-insecure-no-password`; for legacy `repo2`, insecure empty password remains disabled for compatibility. Explicit `SecondaryRepoOptions.Password` wins over resolving file/command/env.

Dependencies and integration points: builds on `resolvePassword` and `readPassword` from `global.go`; uses pflag for CLI integration and restic errors. Commands can pass the returned `Options` to normal repository open paths.

Risks and test signals: migration from `repo2` to `from-*` is compatibility-sensitive. Password-command execution and file reading inherit risks from global password resolution. Tests cover valid current/legacy flows, file/command password sources, no-repo failures, mutually exclusive source fields, missing password files, invalid commands, and mixed option groups.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/global/secondary_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/global/secondary_repo_test.go -->
## sources/sync-backup/restic/internal/global/secondary_repo_test.go

Purpose: table-driven validation of `SecondaryRepoOptions.FillGlobalOpts`.

Important tests: valid cases check current `Repo`, current `RepositoryFile` with password file or command, legacy `LegacyRepo`, and legacy `LegacyRepositoryFile` with legacy password file or command. Invalid cases cover no repo, repo and repository-file conflicts, password file and command conflicts, missing password file, invalid command, and mixed current/legacy groups.

Control flow and state: the test changes into a temporary directory, writes a temporary password file, and uses an existing `Options` as source values to confirm secondary settings override only the intended fields.

Dependencies and integration points: depends on OS file APIs and restic test helpers. It verifies the compatibility layer used by copy/dump/restore-style commands that need a second repository.

Risks and test signals: it catches option migration regressions but does not exercise pflag deprecation/hidden marker behavior or environment-variable initialization from `AddFlags`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/global/secondary_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/doc.go -->
## sources/sync-backup/restic/internal/migrations/doc.go

Purpose: package documentation for repository/backend migrations.

Important APIs: no executable declarations; it documents that package `migrations` contains migrations applicable to repositories and/or backends.

Control flow and state: none.

Dependencies and integration points: establishes package docs for Go tooling. The actual interfaces and registrations live in neighboring files.

Risks and test signals: minimal; documentation should remain aligned with migration scope if backend-only migrations are added.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/interface.go -->
## sources/sync-backup/restic/internal/migrations/interface.go

Purpose: defines the common migration contract.

Important APIs/types: `Migration` requires `Check(context.Context, restic.Repository) (bool, string, error)`, `RepoCheck() bool`, `Apply(context.Context, restic.Repository) error`, `Name() string`, and `Desc() string`.

Control flow and state: the interface itself is stateless; implementations decide applicability, whether repository checks are required, and how to mutate repository/backend state.

Dependencies and integration points: depends on `context` and `restic.Repository`. Command code can use this interface over the registered `All` slice.

Risks and test signals: `Apply` accepts the broad `restic.Repository` interface, but implementations may type-assert to concrete repository types, so callers must pass compatible implementations. Tests currently cover the v2 upgrade migration.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/list.go -->
## sources/sync-backup/restic/internal/migrations/list.go

Purpose: central migration registry.

Important APIs: package variable `All []Migration` stores registered migrations. `register(m Migration)` appends to it.

Control flow and state: registrations occur through `init` functions in migration implementation files. The order is Go initialization order within the package, so it should remain deterministic for files in the package but should be treated carefully when adding migrations.

Dependencies and integration points: command code enumerates `All`; `upgrade_repo_v2.go` registers itself here.

Risks and test signals: global mutable registration is simple but not concurrency-protected; registrations happen at init time before use. There are no direct registry tests in this target set.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/upgrade_repo_v2.go -->
## sources/sync-backup/restic/internal/migrations/upgrade_repo_v2.go

Purpose: migration implementation that upgrades a repository from format version 1 to version 2.

Important APIs/types: `init` registers `&UpgradeRepoV2{}`. `UpgradeRepoV2` implements `Migration`: `Name` returns `upgrade_repo_v2`; `Desc` describes the repository v2 upgrade; `Check` returns true only for repositories whose config version is exactly 1 and otherwise returns a reason; `RepoCheck` returns true; `Apply` calls `repository.UpgradeRepo`.

Control flow and state: `Apply` type-asserts `restic.Repository` to `*repository.Repository`, so it mutates only the concrete repository implementation. The persistent state change is delegated to `repository.UpgradeRepo`, which updates repository format metadata.

Dependencies and integration points: integrates migration registry, `restic.Repository.Config`, and repository upgrade code. Commands can use `Check` to report non-applicability before applying.

Risks and test signals: the concrete type assertion can panic if called with a non-standard repository implementation. The check only distinguishes version 1 from other versions and assumes future versions are already upgraded. `TestUpgradeRepoV2` covers applicability and successful apply on a v1 test repo.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/upgrade_repo_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/upgrade_repo_v2_test.go -->
## sources/sync-backup/restic/internal/migrations/upgrade_repo_v2_test.go

Purpose: smoke test for the repository v2 migration.

Important tests: `TestUpgradeRepoV2` creates a version 1 repository, verifies the initial version, checks migration applicability, and calls `Apply`.

Control flow and state: the test uses `repository.TestRepositoryWithVersion` to build mutable repository state and applies the migration against it.

Dependencies and integration points: depends on the concrete repository package and context. It verifies that the migration connects to `repository.UpgradeRepo`.

Risks and test signals: the test does not assert the post-apply version or verify command-level migration reporting. It mainly catches registration/API drift and gross upgrade failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/migrations/upgrade_repo_v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/options/options.go -->
## sources/sync-backup/restic/internal/options/options.go

Purpose: parsing, listing, namespace extraction, and reflection-based application of backend-specific `-o key=value` options.

Important APIs/types: `Options map[string]string` stores normalized options. `Register`, `List`, `appendAllOptions`, and `listOptions` support discoverable option help via struct tags. `Help` and `helpList` carry namespace/name/text and sorted ordering. `splitKeyValue` lowercases and trims keys and trims values. `Parse` accepts duplicate keys only if values match. `Extract` returns options under a namespace and strips the namespace prefix. `Apply` maps option names to struct fields tagged `option`, supporting `string`, `int`, `uint`, `bool`, and `time.Duration`.

Control flow and state: `opts` is a package-global registered option list. `Apply` reflects on a pointer to a struct and panics for duplicate tags or unsupported field types; unknown options return fatal errors with namespace-qualified names.

Dependencies and integration points: used by global backend parsing before opening/creating backends. Backend config structs must expose supported options through struct tags, and command help can list registered options.

Risks and test signals: reflection panics are possible for developer mistakes in config struct tags or unsupported types. Option parsing is intentionally permissive about missing `=` values. Tests cover parsing, duplicates, invalid keys, namespace extraction, applying typed fields, invalid conversions, listing pointer/value structs, and sorted multi-namespace help.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/options/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/options/options_test.go -->
## sources/sync-backup/restic/internal/options/options_test.go

Purpose: unit tests for the backend extended-options parser and reflector.

Important tests: `TestParseOptions` covers whitespace trimming, lowercasing, missing values, embedded equals in values, and duplicate equal values. `TestParseInvalidOptions` covers empty keys and conflicting duplicates. `TestOptionsExtract` verifies namespace filtering. `TestOptionsApply` and `TestOptionsApplyInvalid` validate typed reflection assignment and conversion errors. `TestListOptions` and `TestAppendAllOptions` check tag discovery and namespace/name sorting.

Control flow and state: tests use local structs with `option` and `help` tags. Invalid duration errors are matched by regexp to allow Go-version wording variance.

Dependencies and integration points: validates behavior used by global backend config application. No external backend is required.

Risks and test signals: tests protect accepted CLI syntax and error messages but do not cover panic paths for duplicate struct tags or unsupported field types.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/options/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/options/secret_string.go -->
## sources/sync-backup/restic/internal/options/secret_string.go

Purpose: wrapper type for strings that must be hidden in formatting/logging while still retrievable by trusted code.

Important APIs/types: `SecretString` holds a `*string`. `NewSecretString` stores a pointer to a copy of the provided string. `String` returns `**redacted**` for non-empty secrets and empty string otherwise. `GoString` wraps the redacted string in quotes for `%#v`. `Unwrap` returns the underlying secret or empty string for a nil/default value.

Control flow and state: the wrapper is immutable unless the internal pointer target is somehow modified through package internals. Default zero values are safe and render as empty.

Dependencies and integration points: used for option/config values that may appear in struct formatting. It relies on Go formatting calling `String`/`GoString`.

Risks and test signals: `Unwrap` exposes the secret by design; callers must avoid logging it. Empty secrets are not redacted, which is useful for defaults but can reveal the difference between empty and non-empty values. Tests verify formatting and struct formatting do not leak the secret.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/options/secret_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/options/secret_string_test.go -->
## sources/sync-backup/restic/internal/options/secret_string_test.go

Purpose: tests that `SecretString` redacts non-empty secrets across common formatting paths.

Important tests: `TestSecretString` checks `String`, `GoString`, `fmt.Sprint`, `%v`, `%#v`, and `Unwrap`. `TestSecretStringStruct` confirms formatted structs do not contain the secret. `TestSecretStringEmpty` validates empty-string behavior. `TestSecretStringDefault` validates zero-value safety.

Control flow and state: tests use a small struct containing a `SecretString` and helper `assertNotIn` for leak checks.

Dependencies and integration points: uses the public `options` package from an external test package, so exported behavior is tested as consumers see it.

Risks and test signals: tests cover formatting leaks but not JSON/YAML marshaling or custom reflection-based logging.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/options/secret_string_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/checker.go -->
## sources/sync-backup/restic/internal/repository/checker.go

Purpose: repository pack/index consistency checking and pack data verification.

Important APIs/types: error types model specific repository damage: `ErrIncompletePackEntry`, `ErrDuplicatePacks`, `ErrMixedPack`, `ErrPackMetadata`, and `ErrPackData`. `Checker` wraps a repository. `computePackTypes` detects packs containing mixed blob types. `LoadIndex` loads indexes with callback error collection and reports duplicate/incomplete/mixed pack hints. `Packs` compares index-derived pack sizes with backend pack files to find missing, truncated, and orphaned packs. `ReadPacks` streams selected packs concurrently and validates contents. `checkPack` retries once after cache eviction. `checkPackInner` verifies index continuity, streams pack bytes while hashing, validates blob decrypt/decompress via pack iterator, reads and parses pack header, compares content-addressed pack ID, header size, and index membership. `bufReader` reuses buffers for iterator reads.

Control flow and state: `ReadPacks` computes pack sizes from indexes, filters them, sets progress max, spawns one worker per repository connection, and feeds pack tasks from `listPacksFromIndex`. `checkPackInner` separates complete backend download failures from partial read failures; partial reads return `ErrPackData` so repair tooling can act on the pack, while full download errors remain plain errors. On any check failure, cache entries for the pack are forgotten before a retry.

Dependencies and integration points: depends on repository internals (`loadIndexWithCallback`, `idx`, `listPacksFromIndex`, `Key`, backend), `pack`, `index`, `hashing.Reader`, zstd decoder, backend handles, and progress counters. It is used by check/repair commands to classify repository health.

Risks and test signals: correctness is critical because false negatives hide corruption and false positives can prompt destructive repairs. Risks include index gaps/overlaps, stale cache data, duplicate split-pack index entries from old restic versions, context cancellation during streaming, and memory boundedness while grouping by pack. Tests cover index gaps, pack hash mismatch, complete download errors, and partial/truncated reads.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/checker_test.go -->
## sources/sync-backup/restic/internal/repository/checker_test.go

Purpose: targeted tests for repository pack verification and error classification.

Important helpers/tests: `testWrapCheckPack` creates shared buffers/zstd decoder for `checkPack`. `TestGapInBlobs` removes an indexed blob entry and expects `ErrPackData` containing gap/overlap and header-size messages. `collectErrors` and `runReadPacks` gather asynchronous checker errors. Backend wrappers `lastByteFlipBackend`, `alwaysFailBackend`, and `truncatingBackend` simulate corruption, total download failure, and partial reads. `setupChecker` writes a test snapshot, reopens through a wrapper, and loads indexes. `TestCheckPackHashMismatch`, `TestCheckPackDownloadError`, and `TestCheckPackPartialDownloadError` verify error classification.

Control flow and state: tests mutate the read path rather than on-disk fixtures when possible, allowing controlled corruption without editing repository data. Some tests use a fixed tar fixture for known pack/blob layout.

Dependencies and integration points: integrates archiver snapshot creation, backend wrapping, repository test helpers, zstd setup, and checker internals.

Risks and test signals: these tests protect repair-command behavior by ensuring total network/backend failures are not mislabeled as repairable pack corruption, while partial reads are. They do not exhaustively cover duplicate pack hints or mixed-pack detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/checker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/buffer.go -->
## sources/sync-backup/restic/internal/repository/crypto/buffer.go

Purpose: small size/buffer helpers for encrypted blob storage.

Important APIs: `NewBlobBuffer(size)` returns a slice of length `size` and capacity `size+Extension`, intended to hold plaintext and later append crypto overhead. `PlaintextLength(ciphertextSize)` subtracts `Extension`. `CiphertextLength(plaintextSize)` adds `Extension`.

Control flow and state: pure arithmetic and allocation; no validation for negative sizes or ciphertext shorter than `Extension`.

Dependencies and integration points: uses `Extension` from `crypto.go`. Repository packer and index code rely on ciphertext/plaintext length conversion for blob sizing.

Risks and test signals: callers must pass plausible non-negative sizes. Length conversion must stay in sync with the crypto construction. Coverage is indirect through crypto and repository tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/crypto.go -->
## sources/sync-backup/restic/internal/repository/crypto/crypto.go

Purpose: restic encryption and authentication primitive implementing `cipher.AEAD`-like semantics with AES-256 CTR and Poly1305-AES.

Important APIs/types: constants define AES key size, MAC key split, IV size, MAC size, and `Extension`. `ErrUnauthenticated` signals MAC failure. `Key` embeds `MACKey` and `EncryptionKey`. Random constructors `NewRandomKey` and `NewRandomNonce` panic on insufficient entropy. JSON marshal/unmarshal methods serialize key material. `Valid` methods reject all-zero key parts. Low-level helpers include `poly1305MAC`, `macKeyFromSlice`, `poly1305PrepareKey`, `poly1305Verify`, `validNonce`, and `sliceForAppend`. `Key.Seal` validates key, rejects additional data, requires valid nonce, AES-CTR encrypts plaintext, appends Poly1305 tag, and supports exact aliasing/append. `Key.Open` validates key/nonce/length, verifies MAC, then decrypts.

Control flow and state: `Seal` panics for invalid programmer inputs such as invalid key, additional data, bad nonce length, or zero nonce. `Open` returns errors for invalid key, zero nonce, short ciphertext, or authentication failure but panics for bad nonce length. The nonce is external state; callers must ensure uniqueness.

Dependencies and integration points: used by repository key handling, pack encryption/decryption, debug repair tooling, and KDF output. It imports standard crypto plus `golang.org/x/crypto/poly1305` and restic errors.

Risks and test signals: nonce reuse would break confidentiality; zero nonce is rejected but uniqueness is not enforceable here. Additional authenticated data is not supported despite the AEAD interface signature. JSON unmarshal copies whatever bytes are present into fixed arrays, so validation must be called. Tests cover Poly1305 vectors, encrypt/decrypt, tamper detection, nonce validation, aliasing and append behavior, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/crypto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/crypto_int_test.go -->
## sources/sync-backup/restic/internal/repository/crypto/crypto_int_test.go

Purpose: internal-package tests for low-level Poly1305 and deterministic crypto behavior.

Important tests/helpers: `poly1305Tests` contains published Poly1305-AES vectors. `TestPoly1305` verifies MAC generation and verification. `testValues` includes a known key/ciphertext/plaintext sample. `decodeArray16`, `decodeArray32`, and `decodeHex` build fixtures. `TestCrypto` checks encrypt/decrypt, MAC tampering, nonce tampering, ciphertext tampering, and decoding known ciphertext. `TestNonceValid` and `BenchmarkNonceValid` cover nonce validation.

Control flow and state: tests mutate ciphertext and nonce bytes in place, then restore them where needed. They call unexported crypto helpers by staying in package `crypto`.

Dependencies and integration points: validates assumptions that repository pack encryption relies on. No repository I/O is involved.

Risks and test signals: strong signal for cryptographic compatibility and tamper detection. It does not test concurrent use or nonce uniqueness policy, which must be enforced by callers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/crypto_int_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/crypto_test.go -->
## sources/sync-backup/restic/internal/repository/crypto/crypto_test.go

Purpose: external-package tests for the public crypto API and buffer aliasing behavior.

Important tests/helpers: `TestEncryptDecrypt` checks multiple plaintext sizes. `TestSmallBuffer` verifies `Seal` grows insufficient destination capacity. `TestSameBuffer` checks decrypting into the same ciphertext buffer. Helpers `encrypt`, `decryptNewSliceAndCompare`, and `decryptAndCompare` validate append semantics. `TestAppendOpen` and `TestAppendSeal` cover nil, empty, small, large, and prefixed destinations. `TestLargeEncrypt` is gated by `testLargeCrypto`. Benchmarks measure encrypt/decrypt throughput.

Control flow and state: random data and nonces are generated for each case. Tests assert prefixes remain intact when appending to destination slices.

Dependencies and integration points: imports the package as `crypto`, so only exported behavior is tested. Uses restic random/test helpers and chunker size constants for optional large cases.

Risks and test signals: append/aliasing behavior is important because repository code reuses buffers for performance. Large encryption coverage is disabled by default, so chunker-maximum-size paths rely mostly on benchmarks/manual enablement.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/crypto_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/doc.go -->
## sources/sync-backup/restic/internal/repository/crypto/doc.go

Purpose: package documentation stating that package `crypto` provides cryptographic operations needed in restic.

Important APIs: no executable declarations.

Control flow and state: none.

Dependencies and integration points: doc-only file for Go package documentation; actual implementation is in `crypto.go`, `kdf.go`, and helpers.

Risks and test signals: minimal; documentation should remain accurate as crypto responsibilities evolve.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/kdf.go -->
## sources/sync-backup/restic/internal/repository/crypto/kdf.go

Purpose: scrypt-based key derivation and salt generation for repository passwords.

Important APIs/types: `Params` stores scrypt `N`, `R`, and `P`. `DefaultKDFParams` mirrors `simple-scrypt` defaults. `Calibrate(timeout, memory)` asks `simple-scrypt` to choose parameters under runtime constraints. `KDF(p, salt, password)` validates 64-byte salt and parameter sanity, derives 64 bytes with scrypt, copies the first 32 bytes to `EncryptionKey`, and the next 32 bytes to `MACKey` as `k||r`. `NewSalt` returns 64 random bytes and panics if entropy fails.

Control flow and state: KDF is deterministic for the same password/salt/params. It performs parameter validation before expensive derivation. Salt generation is random and no persistent state is stored here.

Dependencies and integration points: used by repository key creation/search. Integrates `github.com/elithrar/simple-scrypt`, `golang.org/x/crypto/scrypt`, and crypto key layout from `crypto.go`.

Risks and test signals: security depends on calibrated parameters, adequate memory/time settings, and storing salts accurately. Salt length is strict; mismatches fail. `TestCalibrate` smoke-tests calibration but does not assert exact parameters because hardware varies.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/kdf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/kdf_test.go -->
## sources/sync-backup/restic/internal/repository/crypto/kdf_test.go

Purpose: smoke test for scrypt parameter calibration.

Important tests: `TestCalibrate` calls `Calibrate(100*time.Millisecond, 50)` and logs the returned params.

Control flow and state: hardware-dependent output is intentionally not fixed. The test only fails if calibration returns an error.

Dependencies and integration points: validates the simple-scrypt calibration path used for repository key setup.

Risks and test signals: weak signal for KDF correctness; it does not test `KDF`, salt length errors, or deterministic derived keys. It may be sensitive to very constrained CI environments if calibration fails.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/crypto/kdf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/debug.go -->
## sources/sync-backup/restic/internal/repository/debug.go

Purpose: debug-build utilities for inspecting, dumping, repairing, extracting, and reuploading repository pack/index contents.

Important APIs/types: `packDumpEntry` and `packDumpBlob` define JSON dump shapes. `writePackDumpJSON` writes indented JSON. `DumpPacks` lists pack files in parallel and dumps header blob layout. `DumpIndexes` loads every index and dumps JSON. `ExaminePackOptions` controls repair/extract/reupload behavior. `ExaminePack` loads a pack, compares content hash, inspects index entries, reads pack header, and loads blobs. `checkPackSize` compares blob offsets/header size with file size. `tryRepairWithBitflip` brute-forces one-bit or one-byte repairs with worker goroutines. `decryptUnsigned` decrypts without MAC verification. `loadBlobs` decrypts/decompresses blobs, optionally stores plaintext or reuploads. `storePlainBlob` writes plaintext blobs to local files.

Control flow and state: this file is behind the `debug` build tag. Repair search uses shared `found`/`fixed` variables and closes a `done` channel on success. Extraction writes files in the current working directory with prefixes such as `correct-`, `wrong-hash-`, `damaged-`, and `repaired-`.

Dependencies and integration points: integrates repository raw loading, pack listing, index iteration, crypto internals, zstd decompression, uploader APIs, progress printers, and OS file creation. It is intended for manual diagnostics rather than normal command paths.

Risks and test signals: debug utilities can write decrypted user data to disk and reupload blobs, so they are powerful and sensitive. The bitflip repair path is CPU-heavy and concurrency-sensitive. This target set has no direct tests for debug behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/doc.go -->
## sources/sync-backup/restic/internal/repository/doc.go

Purpose: package-level design documentation for repository storage abstractions.

Important concepts: documents `File` as backend-addressed stored data, usually content-addressed by SHA-256 of ciphertext; `Blob` as typed data/tree content identified by plaintext hash; and `Pack` as one or more encrypted blobs plus encrypted header in a backend file.

Control flow and state: no executable code.

Dependencies and integration points: this documentation explains the invariants used by pack, index, checker, crypto, and repository code.

Risks and test signals: documentation must stay aligned with repository format changes, especially around compression and index versions. No tests are attached to this doc file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/fuzz_test.go -->
## sources/sync-backup/restic/internal/repository/fuzz_test.go

Purpose: fuzz/regression test for saving and loading blobs with varied caller-provided buffer sizes.

Important APIs/tests: `FuzzSaveLoadBlob` fuzzes `blob []byte` and `buflen uint`, bounds buffer length to 64 MiB, hashes the blob, saves it through `WithBlobUploader`, then loads it into a buffer of fuzzed capacity and verifies the hash.

Control flow and state: each fuzz case creates a repository v2 test repo, saves one data blob, then loads it by handle. Oversized fuzz buffers are skipped to avoid allocator-focused tests.

Dependencies and integration points: exercises repository uploader, packer, index, crypto, and load paths. It references regression issue behavior around caller buffer sizes.

Risks and test signals: strong edge-case signal for buffer reuse and blob round trips, but expensive because each fuzz case creates a repo. It validates hash equality rather than byte-for-byte equality, which is sufficient for SHA-256 collision assumptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/reader.go -->
## sources/sync-backup/restic/internal/repository/hashing/reader.go

Purpose: `io.Reader` wrapper that feeds all bytes read into a hash.

Important APIs/types: `Reader` stores an underlying `io.Reader` and `hash.Hash`. `NewReader` constructs it. `Read` delegates to the underlying reader and writes exactly the bytes successfully read into the hash. `Sum` returns the hash sum so far.

Control flow and state: hash state advances monotonically with successful read bytes. Errors from `hash.Hash.Write` are ignored because the interface contract says they are nil.

Dependencies and integration points: used by `checker.go` while streaming pack files to compute the pack content hash without buffering the entire file.

Risks and test signals: callers must use `Sum` after all intended bytes are read. Partial reads with errors still hash the bytes returned, matching Go reader semantics. Tests cover multiple random sizes and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/reader_test.go -->
## sources/sync-backup/restic/internal/repository/hashing/reader_test.go

Purpose: validates and benchmarks `hashing.Reader`.

Important tests: `TestReader` generates random data for several sizes, computes expected SHA-256, copies through `NewReader` to discard, checks byte count and resulting hash. `BenchmarkReader` repeats the same pattern for a 4 MiB buffer.

Control flow and state: each case creates a fresh hash and reader, so accumulated state is isolated.

Dependencies and integration points: verifies behavior used by repository checker streaming hash verification.

Risks and test signals: tests cover full successful reads, not underlying readers that return data plus errors or short reads across many calls.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/writer.go -->
## sources/sync-backup/restic/internal/repository/hashing/writer.go

Purpose: `io.Writer` wrapper that forwards writes while hashing the successfully written prefix.

Important APIs/types: `Writer` stores an underlying `io.Writer` and `hash.Hash`. `NewWriter` constructs it. `Write` delegates to the underlying writer, hashes `p[:n]`, panics only if `hash.Hash.Write` violates its no-error contract, and returns the underlying result. `Sum` returns the hash of all successfully written bytes.

Control flow and state: hash state tracks the underlying writer's accepted bytes, which is important for partial writes. No synchronization is provided.

Dependencies and integration points: useful wherever repository code needs streaming content hashes during writes.

Risks and test signals: callers must handle partial write errors according to `io.Writer` semantics; the hash will already include the accepted prefix. Tests cover successful full writes and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/writer_test.go -->
## sources/sync-backup/restic/internal/repository/hashing/writer_test.go

Purpose: validates and benchmarks `hashing.Writer`.

Important tests: `TestWriter` writes random buffers of several sizes through `NewWriter(io.Discard, sha256.New())`, checks copied byte count, and compares hash with direct SHA-256. `BenchmarkWriter` measures hashing write throughput for a 4 MiB buffer.

Control flow and state: each iteration uses a fresh writer and hash.

Dependencies and integration points: protects streaming hash behavior used by repository write paths.

Risks and test signals: tests do not simulate partial writes or underlying writer errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/hashing/writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/associated_data.go -->
## sources/sync-backup/restic/internal/repository/index/associated_data.go

Purpose: memory-efficient blob-handle set/map that stores small associated values using stable offsets from a `MasterIndex`.

Important APIs/types: `associatedSetSub[T]` stores parallel `value` and `isSet` slices. `AssociatedSet[T]` stores per-blob-type arrays, overflow map, and a master index. `NewAssociatedSet` sizes arrays from `mi.stableLen` for stable finalized index entries. `Get`, `Has`, `Set`, `Insert`, and `Delete` provide map/set operations. `Intersect` and `Sub` create derived sets while preserving values from the receiver. `Len`, `All`, `Keys`, and `String` provide iteration and display.

Control flow and state: handles found in the stable part of `MasterIndex` are addressed by `blobIndex`; missing or later-added handles fall back to `overflow`. `All` yields overflow entries first and then scans `mi.Values`, skipping duplicates already in overflow.

Dependencies and integration points: designed for high-volume repository operations such as prune/check where a normal Go map of blob handles would be memory-heavy. It depends on `MasterIndex` invariants that entries in the first merged finalized index have stable positions.

Risks and test signals: if `MasterIndex` is mutated substantially after creating a set, newly indexed blobs can land in overflow and memory benefits decrease. It is not synchronized. Tests cover normal entries, overflow entries, updates/deletes, sets created before index extension, intersection/subtraction, and string formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/associated_data.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/associated_data_test.go -->
## sources/sync-backup/restic/internal/repository/index/associated_data_test.go

Purpose: tests `AssociatedSet` behavior for stable-index entries, overflow entries, and set algebra.

Important helpers/tests: `noopSaver` saves index bytes by hash. `makeFakePackedBlob` creates a blob handle and packed blob. `list` collects keys. `TestAssociatedSet` covers insert, set, update, delete, overflow handling, and `String`. `TestAssociatedSetWithExtendedIndex` verifies sets created before later master-index extension use overflow for new blobs. `TestAssociatedSetIntersectAndSub` verifies value preservation and membership for intersections and differences.

Control flow and state: tests build a `MasterIndex`, store packs, flush to finalize, and then construct associated sets. Overflow map size is asserted directly.

Dependencies and integration points: validates the stable offset contract between `AssociatedSet` and `MasterIndex`.

Risks and test signals: tests use synthetic blobs and no real repository persistence, so they focus on data-structure behavior rather than integration with prune/check commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/associated_data_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index.go -->
## sources/sync-backup/restic/internal/repository/index/index.go

Purpose: in-memory and serialized representation of restic index files mapping blob handles to pack locations.

Important APIs/types: `Index` holds per-type `indexMap`s, pack IDs, final/index IDs, creation time, and a mutex. `NewIndex`, `StorePack`, `Lookup`, `Has`, `LookupSize`, `Values`, `EachByPack`, `Packs`, `Encode`, `SaveIndex`, `Finalize`, `IDs`, `SetID`, `Dump`, `DecodeIndex`, `BlobIndex`, `Len`, and `PackBlobsHash` are the main API. `Full` and `Oversized` decide when index files should be saved/split. JSON structs `packJSON`, `blobJSON`, and `jsonIndex` define on-disk index shape.

Control flow and state: mutable indexes accept `StorePack` until finalized. Finalized indexes can be saved and assigned exactly one ID. `LookupSize` returns uncompressed length for compressed blobs or subtracts crypto overhead otherwise. `EachByPack` groups entries by pack and optionally ignores blacklisted packs only for finalized indexes. `merge` combines finalized indexes and removes exact duplicate packed blobs. `DecodeIndex` builds a finalized index from JSON and accepts older JSON with ignored `supersedes` fields.

Dependencies and integration points: central to repository load/save/check/prune/repair paths. It depends on `pack`, `crypto` length helpers, `restic` IDs/blob types, and the custom `indexMap` for memory efficiency.

Risks and test signals: panics guard impossible pack offsets over 4 GiB, storing into finalized indexes, null pack IDs, unsupported merge state, and ID assignment order. Iterator methods hold locks while yielding, so callbacks must not attempt mutation. Tests cover serialization, doc examples, size/counts, lookup/type separation, pack listing, grouping by pack, blacklist behavior, oversized thresholds, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_internal_test.go -->
## sources/sync-backup/restic/internal/repository/index/index_internal_test.go

Purpose: internal test for `Oversized` threshold logic.

Important tests: `TestIndexOversized` creates an index just below `indexMaxBlobs + pack.MaxHeaderEntries`, asserts not oversized, adds one more blob, and asserts oversized.

Control flow and state: test bypasses public `StorePack` after adding one pack ID and calls `idx.store` directly to create many entries quickly.

Dependencies and integration points: protects rewrite/splitting logic in `MasterIndex.Rewrite`, which uses `Oversized` to decide whether a full index should be rewritten.

Risks and test signals: focused threshold coverage; it does not test serialization or real rewrite behavior, which is covered in master index tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_parallel.go -->
## sources/sync-backup/restic/internal/repository/index/index_parallel.go

Purpose: parallel loader for all repository index files.

Important APIs: `ForAllIndexes(ctx, lister, repo, fn)` lists `restic.IndexFile` entries, loads each via `LoadUnpacked`, decodes with `DecodeIndex`, and invokes `fn(id, idx, err)`.

Control flow and state: worker count is `repo.Connections() + GOMAXPROCS`, reflecting mixed I/O/CPU decode cost. The callback is serialized with a mutex even though loading/decoding is parallel. Returning an error from the callback cancels/propagates through `restic.ParallelList`.

Dependencies and integration points: used by master index loading, debug index dumping, repository checker, and streaming index listing.

Risks and test signals: serialized callback prevents races in callers but can bottleneck heavy callback work. Decode errors are passed to the callback rather than immediately stopping, allowing callers like checker to collect per-index errors. Tests cover loading all expected fixture indexes and callback error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_parallel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_parallel_test.go -->
## sources/sync-backup/restic/internal/repository/index/index_parallel_test.go

Purpose: fixture-based tests for `ForAllIndexes`.

Important tests: `TestRepositoryForAllIndexes` loads a repository fixture, lists expected index IDs, then calls `ForAllIndexes` to ensure every index is decoded without error and reported. It then returns a sentinel callback error and asserts it propagates.

Control flow and state: expected IDs are gathered from repository listing, then compared with IDs observed through the parallel loader.

Dependencies and integration points: uses repository fixture loading, restic ID sets, and restic test helpers.

Risks and test signals: validates basic parallel loader correctness but not callback serialization under concurrent pressure or decode-error collection behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_parallel_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_test.go -->
## sources/sync-backup/restic/internal/repository/index/index_test.go

Purpose: comprehensive tests and benchmarks for `Index` serialization, lookup, grouping, allocation, and performance.

Important tests/helpers: `TestIndexSerialize` builds mixed compressed/uncompressed entries, encodes/decodes, verifies lookups and final IDs. `TestIndexSize` checks count and serialized size. `docExampleV1`/`docExampleV2`, `exampleTests`, and `TestIndexUnserialize` verify design-document JSON compatibility and `uncompressed_length`. `listPack` collects blobs for one pack. `createRandomIndex` and `NewRandomTestID` build large benchmark fixtures. Benchmarks cover decode, parallel decode, encode, hash lookup, allocation, and parallel allocation. `TestIndexPacks`, `TestIndexHas`, `TestMixedEachByPack`, and `TestEachByPackIgnoes` verify pack sets, type-aware membership, mixed blob grouping, and blacklist behavior.

Control flow and state: tests exercise both mutable and finalized indexes, direct JSON decode, and iterator APIs. Benchmarks use deterministic random seeds for repeatability.

Dependencies and integration points: validates on-disk compatibility and performance-critical memory layout behavior used by repository operations.

Risks and test signals: strong coverage for core index behavior. It intentionally reaches large synthetic indexes in benchmarks, but most unit tests stay moderate in size. The typo in `TestEachByPackIgnoes` is cosmetic.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/indexmap.go -->
## sources/sync-backup/restic/internal/repository/index/indexmap.go

Purpose: custom memory-efficient chained hash table for mapping blob IDs to one or more index entries.

Important APIs/types: `indexMap` stores bucket heads, entry count, a maphash seed, and a `hashedArrayTree` block allocator. `add`, `values`, `valuesWithID`, `get`, `firstIndex`, `preallocate`, `hash`, `init`, `len`, `newEntry`, and `resolve` implement map behavior. Bloom helpers `bloomCleanID`, `bloomForID`, `bloomHasID`, and `bloomInsertID` encode a small bloom filter into upper bits of entry indices on 64-bit platforms. `indexEntry` stores blob ID, next pointer, pack index, offset, length, and uncompressed length. `hashedArrayTree` allocates stable entry addresses with growing block sizes.

Control flow and state: map initialization is lazy. `add` prepends to the bucket chain and stores bloom metadata. `preallocate` grows bucket count to keep load under `maxLoad` and rethreads all entries. Entry index `0` is reserved as null, so stable indices start at 1.

Dependencies and integration points: used internally by `Index` for each blob type. The stable first index is consumed by `AssociatedSet`. `maphash` protects against crafted low-bit SHA-256 collision attacks on hash table buckets.

Risks and test signals: no deletion support by design. Bit packing depends on word size and guards overflow by panic. Hash seed handling constructs a new `maphash.Hash` per call with the stored seed. Tests cover insertion/get, iteration, duplicate IDs, stable first indices, hashed array tree allocation, and hash benchmark.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/indexmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/indexmap_test.go -->
## sources/sync-backup/restic/internal/repository/index/indexmap_test.go

Purpose: tests and benchmark for the custom `indexMap` and `hashedArrayTree`.

Important tests: `TestIndexMapBasic` inserts 400 random IDs and verifies retrieval/counts. `TestIndexMapForeach` checks empty iteration, values, and early break. `TestIndexMapForeachWithID` verifies duplicate keys with noise entries. `TestHashedArrayTree` checks allocation/ref stability. `BenchmarkIndexMapHash` measures maphash use over random IDs. `TestIndexMapFirstIndex` and `TestIndexMapFirstIndexDuplicates` verify stable first-index behavior.

Control flow and state: tests use deterministic random seeds and package-internal access to unexported structures.

Dependencies and integration points: protects the memory-efficient structure that backs all index lookup behavior and the associated data offset contract.

Risks and test signals: tests cover functional invariants but not 32-bit bloom-filter fallback or extremely large overflow limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/indexmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/master_index.go -->
## sources/sync-backup/restic/internal/repository/index/master_index.go

Purpose: aggregate index manager that combines loaded index files, tracks pending blobs, supports incremental loading, saving, rewriting, fallback save, and pack listing.

Important APIs/types: `MasterIndex` holds indexes, pending blob sizes, and a mutex. `NewMasterIndex`, `clear`, `Lookup`, `LookupSize`, `AddPending`, `IDs`, `Packs`, `Insert`, `StorePack`, `Values`, `MergeFinalIndexes`, `Load`, `Rewrite`, `SaveFallback`, `Flush`, `ListPacks`, plus internal `storePack`, `finalizeNotFinalIndexes`, `finalizeFullIndexes`, `prepareIncrementalLoad`, `saveIndex`, `saveFullIndex`, `saveFullIndex`, `blobIndex`, and `stableLen`. `MasterIndexRewriteOpts` carries progress/delete callbacks.

Control flow and state: the master starts with an empty finalized index at position 0 so merges have a stable target. Pending blobs prevent duplicate upload scheduling before a pack is stored. `StorePack` removes stored blobs from pending and appends to the current mutable index, saving full indexes as needed. `Load` memorizes index listings, skips already loaded IDs when possible, clears pending blobs, and resets fully if previously loaded IDs disappeared. `MergeFinalIndexes` preallocates and merges finalized indexes with IDs into index 0 while leaving mutable/no-ID indexes separate. `Rewrite` reloads selected old indexes, filters excluded packs and duplicate pack layouts, writes new split indexes, clears memory, then removes obsolete index files. `SaveFallback` rebuilds indexes in a bounded-concurrency fallback path. `ListPacks` scans by low nibble of pack ID to bound temporary grouping memory.

Dependencies and integration points: central to repository load, save, prune, repair-index, checker, and associated-data operations. It relies on `Index`, `PackBlobsHash`, restic list/load/save/remove interfaces, progress counters, and errgroup concurrency.

Risks and test signals: must not run concurrently with rewrite/fallback operations. Index state is cleared during rewrite and after fallback, so callers must reload as needed. Duplicate pack handling preserves old-restic split-pack repair semantics. Tests cover lookup, pending blobs, merge deduplication, saving/rewrite/fallback across repository versions, partial rewrite after pack removal, incremental load, oversized split rewrite, split-pack rewrite, duplicate full-pack rewrite, and many benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/master_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/master_index_test.go -->
## sources/sync-backup/restic/internal/repository/index/master_index_test.go

Purpose: broad behavioral and performance coverage for `MasterIndex`.

Important tests/helpers: `TestMasterIndex` covers lookup and size across multiple indexes and duplicate blob IDs. `TestMasterIndexAddPending` and `TestMasterIndexStorePackRemovesPending` cover pending state. `noopSaver` hashes saved index bytes. `TestMasterMergeFinalIndexes` verifies merge and duplicate removal. `createRandomMasterIndex` supports benchmarks for allocation, merge, lookup, iteration, and GC. `createFilledRepo`, `TestIndexSave`, and `TestIndexSavePartial` validate rewrite/save fallback against real repos and checker. `loadIndexAndCollectBlobs`, `collectBlobs`, `TestMasterIndexIncrementalLoad`, and `listPacks` cover incremental reload. `TestRewriteOversizedIndex`, `TestRewriteSplitPacks`, and `TestRewriteFullPacks` cover rewrite splitting, split pack entries, excluded packs, and duplicate full indexes.

Control flow and state: tests use both synthetic `Index` instances and full test repositories. Some tests temporarily replace package variables `index.Full` and `index.Oversized`, restoring them with defer.

Dependencies and integration points: integrates repository, data snapshot creation, checker validation, pack/crypto size helpers, progress counters, and cmp diffs.

Risks and test signals: very strong integration signal for index lifecycle, but some tests are heavier because they create real repositories and snapshots. Replacing global thresholds in tests means parallel execution must be avoided for those cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/master_index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/testing.go -->
## sources/sync-backup/restic/internal/repository/index/testing.go

Purpose: test helper for finalizing and merging a `MasterIndex`.

Important APIs: `TestMergeIndex(t, mi)` finalizes non-final indexes, assigns random IDs, calls `MergeFinalIndexes`, and returns the finalized indexes, remaining index count, and assigned ID set.

Control flow and state: mutates the provided master index by finalizing pending indexes and merging them. It uses random IDs to simulate saved index IDs without backend I/O.

Dependencies and integration points: used by master index tests and benchmarks. Depends on restic random IDs and test assertions.

Risks and test signals: helper is for tests only; it bypasses actual `SaveIndex`, so persistence errors are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index_list.go -->
## sources/sync-backup/restic/internal/repository/index_list.go

Purpose: streams blob handles directly from repository index files without building a master index.

Important APIs/types: `IndexBlob` carries either a `restic.BlobHandle` or an error. `AllIndexBlobs(ctx, lister, loader)` returns an `iter.Seq[IndexBlob]` that calls `index.ForAllIndexes`, yields each `idx.Values()` handle, supports early stop via a sentinel error, and yields loader/decode errors as `IndexBlob{Error: err}`.

Control flow and state: the iterator avoids accumulating a master index in memory. If the consumer stops early, the sentinel prevents surfacing an artificial error. Context cancellation while scanning an index is propagated through `ForAllIndexes` and yielded as an error unless it was the stop sentinel.

Dependencies and integration points: useful for commands that need a linear stream of indexed blobs. Depends on Go iterators, repository list/load interfaces, and the index package.

Risks and test signals: consumers must check `entry.Error` while iterating. Because it streams all index entries, duplicate blobs across indexes are not deduplicated here. Tests cover full streaming against a master-index baseline and early stop.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index_list_test.go -->
## sources/sync-backup/restic/internal/repository/index_list_test.go

Purpose: validates streaming index blob enumeration.

Important tests: `TestAllIndexBlobs` creates a repository, saves five data blobs, loads the master index, compares master `ListBlobs` output with `AllIndexBlobs` output. `TestAllIndexBlobsEarlyStop` saves blobs, breaks after one streamed entry, and asserts no error is yielded after early stop.

Control flow and state: tests save blobs through `WithBlobUploader`; the first test explicitly loads the master index for baseline comparison.

Dependencies and integration points: exercises repository uploader/index persistence plus direct index streaming.

Risks and test signals: tests cover happy path and early stop, not decode errors or context cancellation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index_testutil_test.go -->
## sources/sync-backup/restic/internal/repository/index_testutil_test.go

Purpose: repository-package test utility for retrieving blobs belonging to one pack from the loaded master index.

Important APIs: `BlobsInPack(repo, packID)` iterates `repo.idx.Values()`, filters entries whose pack ID matches, appends their `pack.Blob`, sorts by offset, and returns them.

Control flow and state: read-only helper over an already loaded repository index. It assumes `repo.idx` is populated by the caller.

Dependencies and integration points: used by repository tests outside this target set that need pack blob layout without duplicating index iteration logic.

Risks and test signals: if the repository index is not loaded, the helper can return incomplete results. It is test-only and has no dedicated test.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/index_testutil_test.go -->
