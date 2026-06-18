# subset-b-007600 research

Grouped research for the exact subset-b-007600 manifest. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/profile.go -->
# sources/distributed-fs/ipfs-kubo/profile/profile.go

Purpose: implements Kubo diagnostic profile collection into a caller-provided zip archive. The public entry point is `WriteProfiles(ctx, archive, opts)`, driven by `Options` and collector constants for goroutine stacks, pprof profiles, version metadata, binary copy, CPU/mutex/block profiles, and runtime trace.

Important APIs and control flow: `profiler.runProfile` validates collector names, filters collectors through `enabledFunc`, starts enabled collectors concurrently, buffers each result, then serializes each buffer into the zip. Sampling collectors wait for `ProfileDuration`; mutex and block collectors temporarily change global runtime profiling settings and restore them with defers.

State and persistence: no long-lived application state, but it reads the current executable, runtime pprof state, and version metadata, and writes zip members. CPU profiling, tracing, mutex fraction, and block profiling are global process resources, so concurrent callers can interfere.

Dependencies and integration: uses Go `runtime/pprof`, `runtime/trace`, `archive/zip`, Kubo version info, and `WriteAllGoroutineStacks`. Integrated with debug/profiling workflows that need a portable bundle.

Risks and test signals: unknown collector names fail early; context cancellation cancels duration-based collectors. Risks include huge binary zip entries, global runtime profile mutation, and duplicate result sends after collector errors. Tests cover enabled/disabled collectors and Windows executable naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/profile_test.go -->
# sources/distributed-fs/ipfs-kubo/profile/profile_test.go

Purpose: validates `WriteProfiles` end-to-end by creating an in-memory zip archive and checking expected profile members are present and non-empty.

Important APIs and control flow: `TestProfiler` defines a table over all collectors, OS-specific binary naming, disabled sampling profiles, disabled mutex and block profiles, and a single-collector case. Each case temporarily overrides the package-level `goos` when needed, runs `WriteProfiles`, closes the zip writer, reopens the zip, and checks file count plus non-zero file size.

State and persistence: all output is in memory through `bytes.Buffer`; the test does exercise process-level profiling collectors with very short durations, and the binary collector opens the test binary or `/proc/<pid>/exe`.

Dependencies and integration: uses `archive/zip`, `testing`, `stretchr/testify`, and package globals from `profile.go`.

Risks and test signals: coverage confirms collector gating and Windows `.exe` behavior, but does not cover unknown collector errors, context cancellation, concurrent profiler calls, zip write failures, or global profiling interference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/profile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/common/common.go -->
# sources/distributed-fs/ipfs-kubo/repo/common/common.go

Purpose: provides map utilities used by repo config code to manipulate JSON-like `map[string]any` structures without losing user-specified keys.

Important APIs and control flow: `MapGetKV` traverses dot-separated keys and returns detailed errors for missing or non-map intermediate nodes. `MapSetKV` creates missing intermediate maps and writes the final value. `MapMergeDeep` clones the left map and recursively overlays right-side map values when both sides are maps; otherwise the right value replaces.

State and persistence: functions are in-memory only, but they directly affect persisted repo config because `fsrepo.SetConfig` and `SetConfigKey` read config JSON into maps, mutate or merge, and write back.

Dependencies and integration: depends on Go `maps`, `strings`, and `fmt`; used by `repo/fsrepo` to preserve unknown config fields and protect private key values during partial updates.

Risks and test signals: dot-path keys cannot address literal dots in key names. `MapSetKV` replaces nil intermediates but errors on non-map intermediates. Tests focus on deep merge copy/override semantics; get/set edge cases rely on integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/common/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/common/common_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/common/common_test.go

Purpose: tests the deep merge behavior that repo config persistence relies on when struct-derived config values are merged back into a raw user JSON map.

Important APIs and control flow: `TestMapMergeDeepReturnsNew` checks the left input is not mutated. `TestMapMergeDeepNewKey` checks additions from the right map. `TestMapMergeDeepRecursesOnMaps` verifies nested maps are merged recursively. `TestMapMergeDeepRightNotAMap` confirms a non-map right value replaces an existing left map.

State and persistence: all data is in-memory test maps, but the asserted semantics protect persisted config files from accidental removal of keys unknown to the typed config struct.

Dependencies and integration: uses `stretchr/testify/require`; indirectly documents expectations for `fsrepo.SetConfig`.

Risks and test signals: strong signal for merge semantics, but no direct tests for `MapGetKV` or `MapSetKV`, no nil-map variants beyond clone behavior, and no type-alias map cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/common/common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/config_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/config_test.go

Purpose: validates datastore config parsing and creation for default mount, LevelDB, flatfs, and measurement wrapper specs.

Important APIs and control flow: the tests unmarshal JSON snippets into `config.Datastore` or generic spec maps, call `fsrepo.AnyDatastoreConfig`, compare `DiskSpec().String()` to expected minimal JSON, then call `Create` in a temp dir and assert the concrete datastore type. The default config test initializes and injects plugins so external datastore handlers are registered.

State and persistence: creates datastore directories under `t.TempDir`; the disk spec checks represent persistent layout identity and are used by `FSRepo.openDatastore` to reject mismatched repos.

Dependencies and integration: depends on plugin loader injection, `config`, `reflect`, and `fsrepo` datastore handlers.

Risks and test signals: strong signal that runtime-only wrapper fields such as measurement prefixes are excluded from disk specs and mount ordering is deterministic. It does not test invalid specs, duplicate handler registration, or datastore close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/datastores.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/datastores.go

Purpose: translates repo datastore spec maps into concrete datastore instances and stable on-disk identity specs.

Important APIs and control flow: `DatastoreConfig` exposes `DiskSpec` and `Create`. `AnyDatastoreConfig` dispatches by `"type"` using the package registry initialized with `mount`, `mem`, `log`, and `measure`; plugins can extend it through `AddDatastoreConfigHandler`. `MountDatastoreConfig` recursively parses child specs, sorts mountpoints descending for deterministic longest-prefix behavior, and creates a `mount.Datastore`. `log` and `measure` wrap children while returning the child disk spec.

State and persistence: `DiskSpec` JSON is stored as `datastore_spec` at repo init and compared on open to prevent using an incompatible datastore layout. Memory datastore has nil disk spec and no persistence.

Dependencies and integration: integrates with `repo.Datastore`, go-datastore mount/sync/log, go-ds-measure, and plugin-provided datastore handlers such as flatfs and levelds.

Risks and test signals: malformed specs can panic if `mountpoint` exists but is not a string. Handler registry is package-global and not synchronized after init. Tests verify disk spec canonicalization and concrete datastore construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/datastores.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/doc.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/doc.go

Purpose: package documentation sketching the intended filesystem repo layout and lock/profiling files.

Important APIs and control flow: no executable APIs. The comment documents a conceptual `.ipfs` tree with `client/`, `daemon/`, config, datastore, `repo.lock`, and version files.

State and persistence: describes persistent repo files and lock boundaries. The actual current implementation in `fsrepo.go` uses `repo.lock`, `config`, `datastore_spec`, `version`, `api`, `gateway`, `swarm.key`, keystore, and datastore directories; the doc still contains TODO roadmap text.

Dependencies and integration: package-level documentation for the `fsrepo` package.

Risks and test signals: because it is a TODO roadmap, it may be stale relative to actual files and should not be used as an authoritative layout contract without checking implementation and tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo.go

Purpose: implements Kubo's filesystem-backed `repo.Repo`, including initialization, opening, locking, config persistence, datastore/keystore creation, API/gateway address files, resource overrides, filestore integration, and close semantics.

Important APIs and control flow: `Init` writes config, datastore spec, and repo version under `packageLock`. `Open` and `OpenWithUserConfig` delegate through `repo.OnlyOne`, call `open`, acquire `repo.lock` or wait based on `IPFS_WAIT_REPO_LOCK`, validate repo version through migrations, check writability, load config/resource overrides, open datastore, open keystore, and optionally create a filestore manager. `Close` removes `api` and `gateway`, closes datastore, marks closed, and releases the lock.

State and persistence: owns files `config`, `datastore_spec`, `version`, `repo.lock`, `api`, `gateway`, `swarm.key`, `keystore`, and datastore contents. `SetAPIAddr` and `SetGatewayAddr` use temp files plus rename. `SetConfig` merges typed config into raw JSON to preserve unknown keys; `SetConfigKey` protects the private key selector.

Dependencies and integration: integrates with config serialization, fs locks, datastore handlers, metrics wrapping, migrations, libp2p resource overrides, multiaddr, and the `repo.Repo` interface.

Risks and test signals: global `packageLock` serializes broad operations and can bottleneck. `BackupConfig` returns the original name rather than the temp backup name, which is surprising. `Datastore()` after close returns a closed datastore. Version mismatch blocks open. Tests cover init idempotence, independent repos, persistence, close behavior, and same-process reference sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo_test.go

Purpose: tests core filesystem repo lifecycle properties.

Important APIs and control flow: `TestInitIdempotence` calls `Init` repeatedly. `TestCanManageReposIndependently` initializes two repos, opens both, closes/removes one while the other remains open, then closes/removes the other. `TestDatastoreGetNotAllowedAfterClose` checks datastore operations fail after repo close. `TestDatastorePersistsFromRepoToRepo` writes through one open, closes, reopens, and reads. `TestOpenMoreThanOnceInSameProcess` asserts `Open` returns the same reference through `OnlyOne` and reference-counted close releases after both closes.

State and persistence: uses temp repos, version/config/datastore files, and actual datastore writes.

Dependencies and integration: exercises `config.DefaultDatastoreConfig`, fsrepo locking, datastore persistence, and `repo.OnlyOne`.

Risks and test signals: covers major lifecycle invariants but not migration mismatch, user config files, API/gateway file writes, resource override parsing, swarm key reads, or lock wait environment behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile.go

Purpose: provides a small same-directory atomic file writer used by embedded migration backup and config rewrite helpers.

Important APIs and control flow: `New(path, mode)` creates a hidden temp file in the target directory and chmods it. `Close` closes the temp file and renames it over the target. `Abort` closes and removes the temp file, combining close and remove errors when both fail. `ReadFrom` copies a reader into the temp file.

State and persistence: writes temporary `.tmp-<base>` files next to the target, then relies on `os.Rename` atomicity on the same filesystem. It does not fsync file contents or parent directories.

Dependencies and integration: used by migration `common.WithBackup` to atomically create config backups and replacement config files.

Risks and test signals: double `Abort` returns an error because the file is gone but should not panic. On Windows, rename semantics depend on closed handles. Tests cover creation, close, abort, close failure cleanup, permissions, `ReadFrom`, and temp-file cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile_test.go

Purpose: verifies the atomic writer's file lifecycle and error handling.

Important APIs and control flow: tests cover `New`, `Close`, `Abort`, forced close/remove errors, `ReadFrom`, Unix permission preservation, repeated abort, and absence of `.tmp-*` files after repeated operations.

State and persistence: creates temp directories and real files, checking target content, target absence after abort, temp-file removal, and file modes. The tests intentionally close/remove files to trigger error paths.

Dependencies and integration: uses `os`, `filepath`, `runtime`, and `stretchr/testify`; validates behavior relied on by migration config backup and rollback.

Risks and test signals: strong coverage for expected temp-file hygiene, but no crash-simulation or fsync durability tests. Multiple aborts are allowed to error, so callers should not require idempotent nil results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/base.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/base.go

Purpose: provides the shared implementation for embedded config-only repo migrations.

Important APIs and control flow: `BaseMigration` stores from/to versions, description, and a `Convert` function. `Versions` formats `"from-to"`, `Reversible` returns true, `Apply` checks the current version, runs `WithBackup` on the repo config, writes the target version, and prints verbose progress. `Revert` checks the target version, restores the backup, and writes the original version.

State and persistence: reads and writes the repo `version` file, rewrites `config`, and leaves `config.<from>-to-<to>.bak` for rollback.

Dependencies and integration: used by embedded migrations 16-to-17 and 17-to-18 and by standalone migration command wrappers.

Risks and test signals: if version write fails after config rewrite, the repo can contain migrated config with old version and a backup; callers get an error but rollback is manual. Test helpers and migration-specific tests exercise apply/revert paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/base.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/config_helpers.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/config_helpers.go

Purpose: supplies generic JSON-map mutation helpers for embedded migration converters.

Important APIs and control flow: includes dot-path getters/setters/deleters, move/copy/rename helpers, defaults, field transforms, section creation, safe map/slice casts, merging source maps into destination maps, slice append/replace helpers, string-map cloning, and empty-slice detection.

State and persistence: operates in memory on decoded config maps; changes are later persisted by `WriteConfig` through `BaseMigration`/`WithBackup`.

Dependencies and integration: used by the 16-to-17 migration to add AutoConf, rewrite bootstrap/DNS/routing/IPNS fields, and by 17-to-18 tests and helpers. Depends on Go `maps`, `slices`, `strings`, and `fmt`.

Risks and test signals: `SetField` replaces non-map intermediates with maps, which is convenient for repair but can discard malformed user data. Equality in `EnsureFieldIs` requires comparable values. Helpers are mostly covered indirectly by migration tests rather than direct unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/config_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/migration.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/migration.go

Purpose: defines the embedded migration interface and shared options.

Important APIs and control flow: `Options` carries `Path` and `Verbose`. `Migration` requires `Versions`, `Apply`, `Revert`, and `Reversible`, giving the embedded runner a uniform way to execute or roll back migration steps.

State and persistence: no direct persistence; implementations use the options path to mutate repo files.

Dependencies and integration: implemented by `BaseMigration` and consumed by `embedded.go` registration and execution.

Risks and test signals: the interface assumes migrations can be expressed as apply/revert operations and relies on implementations to enforce version checks, locking, and backup behavior. Embedded migration tests assert registered migrations implement this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/testing_helpers.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/testing_helpers.go

Purpose: centralizes test scaffolding for embedded config migrations.

Important APIs and control flow: `RunMigrationTest` marshals a config map, invokes a `BaseMigration.Convert`, decodes output, and checks `ConfigAssertion` entries. `AssertConfigField` handles nil-missing assertions, string slices, string maps, and scalar values. `GenerateTestConfig`, `CreateTestRepo`, `AssertMigrationSuccess`, `AssertMigrationReversible`, and `compareConfigs` cover end-to-end apply/revert flows.

State and persistence: creates temp repos with `version` and `config`, writes backup files for revert tests, then reads migrated/reverted JSON.

Dependencies and integration: used by migration-specific tests, especially 17-to-18.

Risks and test signals: helper expectations mirror JSON decoder types, for example numbers become `float64`. It only supports `BaseMigration` conversions for direct conversion tests and compares maps recursively for revert fidelity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/testing_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/utils.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/utils.go

Purpose: provides version-file and JSON backup/rewrite helpers shared by embedded migrations.

Important APIs and control flow: `CheckVersion` reads and trims `version`, `WriteVersion` writes a version string, `Must` panics on supposedly unrecoverable transactional errors, `WithBackup` reads config into memory, atomically writes a backup, atomically rewrites config through a converter, and removes backup on conversion setup failure. `RevertBackup` renames backup over config. `ReadConfig` and `WriteConfig` decode and pretty-print JSON.

State and persistence: mutates repo `config`, backup config files, and `version`. Reads config fully before renaming to avoid Windows open-file rename issues.

Dependencies and integration: depends on the local `atomicfile` package and is called by `BaseMigration`.

Risks and test signals: `Must(out.Close())` can panic instead of returning an error if final rename fails. No fsync durability. Backup remains after successful migration for revert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded.go

Purpose: registers and runs migrations embedded in the Kubo binary, currently 16-to-17 and 17-to-18.

Important APIs and control flow: `embeddedMigrations` is registered into `migrationsByName` as `fs-repo-<versions>`. `RunEmbeddedMigration` looks up a name, checks reversibility, builds options, and applies or reverts. `RunEmbeddedMigrations` validates the repo path, acquires `repo.lock` once, reads current version, enforces downgrade rules, finds step names with `findMigrations`, and runs available embedded steps in sequence.

State and persistence: locks the repo, reads/writes the repo version, and lets individual migrations atomically rewrite config and backups.

Dependencies and integration: used by `RunHybridMigrations` and by `fsrepo.Open` migration guidance. Depends on `go-fs-lock` and embedded migration packages.

Risks and test signals: if a version range includes both embedded and missing steps, the current logic runs embedded ones and only errors when zero embedded migrations exist; it does not require every step be embedded. Tests verify registration and missing migration error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded_test.go

Purpose: smoke-tests embedded migration registration and error behavior.

Important APIs and control flow: `TestHasEmbeddedMigration` checks `fs-repo-16-to-17` exists and an unknown migration does not. `TestEmbeddedMigrations` verifies the embedded list is non-empty and every migration has a non-empty version string. `TestRunEmbeddedMigration` confirms a missing migration name returns an error.

State and persistence: does not create or mutate real repos; the missing-migration test passes `/tmp` but exits before path use.

Dependencies and integration: validates the map built by `embedded.go` and migration interface implementation.

Risks and test signals: coverage is shallow; it does not run successful embedded migrations, lock contention, downgrade paths, or incomplete-step ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch.go

Purpose: downloads and unpacks external migration or Kubo binaries from an IPFS distribution path.

Important APIs and control flow: `FetchBinary` determines archive and binary names, rejects existing output files, creates or uses a download directory, chooses tar.gz or zip by OS, fetches archive bytes through a `Fetcher`, writes the archive, unpacks the requested binary, chmods it executable, and returns the output path. `osWithVariant` detects Linux musl via `ldd --version`. `makeArchivePath` builds distro/version/archive paths.

State and persistence: writes downloaded archives to temp or configured `DownloadDirectory`, writes extracted binaries, and sets executable mode.

Dependencies and integration: used by legacy migration downloads in `fetchMigrations`; depends on `Fetcher`, archive unpack helpers, runtime GOOS/GOARCH, and system `ldd`.

Risks and test signals: archive bytes are fully buffered by fetchers and then copied to disk. Existing output is a hard error. Tests cover fetch success, output collisions, permission/temp errors, bad dist, missing binary, dist env, and HTTP user agent/failover paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch_test.go

Purpose: tests distribution fetcher configuration, HTTP retrieval, binary download/unpack, and `MultiFetcher` gateway failover behavior.

Important APIs and control flow: tests cover `GetDistPathEnv`, `NewHttpFetcher`, `HttpFetcher.Fetch`, `FetchBinary`, user-agent propagation, migration source failover from bad gateways, `NewMultiFetcher`, quarantine ordering, full-failure reset, exhaustion cap, concurrent fetches, success counter reset, and context cancellation.

State and persistence: writes binaries to temp dirs, manipulates `TMPDIR`, starts `httptest` gateways, and uses atomic counters for concurrency assertions.

Dependencies and integration: relies on the CAR-backed test gateway from `setup_test.go`, `GetMigrationFetcher`, and test fetcher stubs.

Risks and test signals: strong signal for gateway robustness and race-sensitive lock paths. It does not perform real network downloads and skips some permission behavior on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetcher.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetcher.go

Purpose: defines the migration `Fetcher` interface, distribution constants, size-limited reader wrapper, and `MultiFetcher` failover/circuit-breaker logic.

Important APIs and control flow: `MultiFetcher.Fetch` returns a latched exhaustion error when set, tries never-failed fetchers before quarantined fetchers, clears quarantine and failure count on success, does not penalize context cancellation, and after every fetcher fails increments a full-loop counter. After `maxMultiFetcherFullLoopFailures`, it latches `ErrMultiFetcherExhausted`.

State and persistence: `MultiFetcher` keeps session-scoped failed fetcher indexes, loop failure count, and exhausted error protected by a mutex. No disk persistence.

Dependencies and integration: used by migration download code to combine multiple HTTP gateway fetchers. `GetDistPathEnv` reads `IPFS_DIST_PATH`.

Risks and test signals: `Fetchers()` exposes the slice directly, so callers could mutate it. Exhaustion is lifetime-scoped and requires constructing a new fetcher to retry after network recovery. Tests cover quarantine, reset, cap, concurrency, success reset, and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/main.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/main.go

Purpose: standalone command wrapper for the embedded 16-to-17 repo migration.

Important APIs and control flow: parses `-path`, `-verbose`, and `-revert`; requires `-path`; builds `common.Options`; calls `mg16.Migration.Apply` or `Revert`; prints errors to stderr and exits with status 1 on failure.

State and persistence: mutates the repo at `-path` through the migration implementation, including config backup, config rewrite, and version update.

Dependencies and integration: wraps `repo/fsrepo/migrations/fs-repo-16-to-17/migration` and common migration options. Intended for manual migration scenarios even though the migration is embedded in Kubo.

Risks and test signals: no direct test file for the CLI wrapper; migration behavior is tested in the migration package. The wrapper does not acquire a repo lock itself, so lock safety depends on the migration being run through embedded runner or external operator discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration.go

Purpose: implements repo config migration from version 16 to 17, introducing AutoConf and replacing old defaults with the `"auto"` placeholder.

Important APIs and control flow: exported `Migration` is a `common.BaseMigration`. `convert` decodes JSON, calls `enableAutoConf`, `migrateBootstrap`, `migrateDNSResolvers`, `migrateDelegatedRouters`, and `migrateDelegatedPublishers`, then writes JSON. Default bootstrap peers are removed and replaced with `"auto"` while custom peers are preserved. DNS resolver defaults are converted to `"auto"` and `"."` is ensured. Empty delegated routers/publishers become `"auto"`.

State and persistence: operates on config JSON and, through `BaseMigration`, leaves a backup and updates repo version.

Dependencies and integration: depends on Kubo config constants and migration common helpers. Registered as an embedded migration.

Risks and test signals: invalid or non-slice bootstrap data is replaced by `"auto"`, which repairs but can discard malformed custom data. Default matching is exact string matching. Tests cover end-to-end apply/revert and many bootstrap/DNS/routing/IPNS/autoconf cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration_test.go

Purpose: validates 16-to-17 config conversion and reversible migration behavior.

Important APIs and control flow: helpers run conversion on JSON, assert nested map/slice values, and build minimal configs. `TestMigration` creates a temp repo, writes version 16 and config, applies migration, checks version 17 and config changes, then reverts to version 16. Additional tests cover bootstrap processing, missing sections, preservation of custom DNS/bootstrap values, delegated router rewriting, delegated publisher defaults, and existing AutoConf preservation.

State and persistence: temp repo tests write real `config`, `version`, and backup files; conversion-only tests use buffers.

Dependencies and integration: exercises `common.BaseMigration`, config constants, and helpers from the migration package.

Risks and test signals: strong coverage for expected migration semantics. It does not cover corrupt JSON beyond conversion error path, backup write failure, or lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/main.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/main.go

Purpose: standalone command wrapper for the 17-to-18 repo migration.

Important APIs and control flow: parses `-path`, `-verbose`, and `-revert`; errors when `-path` is missing; calls `mg17.Migration.Apply` or `Revert`; exits non-zero on failure.

State and persistence: delegates all persistent config/version mutation to the migration implementation.

Dependencies and integration: wraps `repo/fsrepo/migrations/fs-repo-17-to-18/migration` and common migration options for manual execution.

Risks and test signals: wrapper has no direct tests. As with the 16-to-17 wrapper, standalone execution does not itself lock the repo; the embedded runner handles locking when used in-process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration.go

Purpose: migrates deprecated `Provider` and `Reprovider` config sections into the unified `Provide` section for repo version 18.

Important APIs and control flow: exported `Migration` is a `common.BaseMigration`. `convert` decodes config, maps `Provider.Enabled` to `Provide.Enabled`, `Provider.WorkerCount` to `Provide.DHT.MaxWorkers`, `Reprovider.Strategy` to `Provide.Strategy` with `"flat"` converted to `"all"`, and `Reprovider.Interval` to `Provide.DHT.Interval`. It deletes old sections and logs guidance for non-default values and high worker counts.

State and persistence: modifies config JSON and updates version through `BaseMigration`.

Dependencies and integration: uses migration common helpers and is registered as an embedded migration.

Risks and test signals: logs include Unicode warning symbols in source output, which may be undesirable in strict ASCII terminals. Existing `Provide` content is overwritten if migrated fields exist. Non-string strategy becomes `"all"`. Tests cover missing/empty sections, preservation of unrelated sections, flat conversion, reversibility, and framework integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration_test.go

Purpose: verifies 17-to-18 conversion semantics and the common migration framework integration.

Important APIs and control flow: table-driven tests use `common.RunMigrationTest` with assertions over `Provide`, deleted `Provider`/`Reprovider`, converted `"flat"` strategy, missing sections, empty sections, and unrelated section preservation. Reversibility and `Versions`/`Reversible` behavior are checked separately.

State and persistence: conversion tests are in-memory; reversibility test creates temp repo state through common helpers and backup files.

Dependencies and integration: exercises `mg17.NewMigration`, `BaseMigration`, and common testing helpers.

Risks and test signals: good signal for config field mapping. It does not test existing `Provide` merge conflicts, non-string strategy warning behavior, high worker count logging, or write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/httpfetcher.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/httpfetcher.go

Purpose: implements HTTP gateway-based migration fetching using verifiable trustless CAR retrieval.

Important APIs and control flow: `NewHttpFetcher` normalizes distribution path, gateway, user agent, and fetch limit. `Fetch` resolves the dist path to an immutable path, requests a CAR from the gateway, and extracts the requested UnixFS file through `carStreamToFileBytes`. Mutable IPNS paths are resolved by fetching and validating IPNS records; DNSLink uses the default multiaddr DNS resolver. HTTP requests set both Accept and `?format=` hints and enforce body limits when configured.

State and persistence: no disk persistence; builds temporary in-memory datastore/blockstore/DAG service for CAR verification and extraction.

Dependencies and integration: uses Boxo blockservice, path resolver, IPNS/namesys, CAR v2, go-unixfsnode, and an HTTP client with migration-specific timeouts. Used by legacy migration download fetchers.

Risks and test signals: third-party gateway content is verified by CID path, but IPNS/DNSLink resolution depends on gateway/DNS availability. Large CARs are limited by reader but file bytes are read fully into memory. Tests cover user agent, fetch success, 404, invalid CAR failover, and gateway rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/httpfetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir.go

Purpose: resolves repo directories and reads/writes repo version files for migration code.

Important APIs and control flow: `IpfsDir` uses an explicit path or `config.PathRoot`, expands home directories, and returns the normalized repo path. `CheckIpfsDir` additionally requires the directory to exist. `RepoVersion` checks the directory then parses `version`. `WriteRepoVersion` expands the path and writes `<version>\n`. Private `repoVersion` trims and converts version text.

State and persistence: reads and writes the `version` file in the repo directory.

Dependencies and integration: used by `fsrepo.Init`, `fsrepo.Open`, legacy and embedded migration runners, and version tests.

Risks and test signals: invalid version file returns a generic error. `WriteRepoVersion` does not ensure directory existence or atomic write. Tests cover env/default path expansion, nonexistent dirs, user-specific home expansion errors, missing version, invalid data, and successful write/read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir_test.go

Purpose: tests repo path discovery and version file parsing/writing.

Important APIs and control flow: `TestRepoDir` sets fake HOME, USERPROFILE, and `IPFS_PATH`, then runs subtests for `IpfsDir`, `CheckIpfsDir`, and `RepoVersion`. Cases cover missing directory, env path, `~/.ipfs` expansion, unsupported `~user` expansion, nonexistent directory, missing version file, valid version write/read, and invalid version data.

State and persistence: creates a fake `.ipfs` directory and writes/removes version files under it.

Dependencies and integration: exercises `config.EnvDir`, `config.PathRoot`, `fsutil.ExpandHome`, and migration version helpers.

Risks and test signals: useful cross-platform signal via `USERPROFILE`; does not cover permission errors or atomicity of version writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher.go

Purpose: implements a migration fetcher that starts a temporary Kubo node and retrieves distribution files over IPFS.

Important APIs and control flow: `NewIpfsFetcher` normalizes dist path, limit, repo root, and user config. `Fetch` lazily initializes once: reads bootstrap/peering config, creates a temp repo with a generated Ed25519 identity and DHT client routing, opens it, starts an online node, then calls CoreAPI UnixFS `Get` on the parsed distribution path. Fetched paths are recorded under a mutex. `Close` stops the node and removes temp repo once.

State and persistence: creates a temp IPFS repo and node, records fetched paths in memory, and removes temp state on close.

Dependencies and integration: uses Kubo core/coreapi, libp2p DHT client, fsrepo init/open, config parsing, Boxo files/path, and migration `Fetcher`.

Risks and test signals: expensive and network-dependent; plugin loading is assumed done before temp repo init. `FetchedPaths` returns the internal slice directly. Config read errors are logged to stderr and ignored. Tests cover fetcher operation in epic mode, path parsing/config reads, and bad config handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher_test.go

Purpose: tests IPFS-based migration fetching, temporary node initialization, and config parsing.

Important APIs and control flow: setup initializes plugins. `TestIpfsFetcher` and `TestInitIpfsFetcher` are gated by an `EPIC_TEST` style skip helper for heavier network/node behavior. `TestReadIpfsConfig` writes config with bootstrap and peering entries and verifies parsed outputs. Bad bootstrap and peering config tests ensure malformed data does not crash parsing. Helpers create config files and load plugins.

State and persistence: creates temp repos/configs, may start temp Kubo nodes and fetch paths in epic tests, and validates cleanup via fetcher close behavior indirectly.

Dependencies and integration: exercises `NewIpfsFetcher`, `initTempNode`, `readIpfsConfig`, Kubo plugin setup, and migration fetcher interface.

Risks and test signals: regular test runs likely skip the most expensive network/node behavior, so coverage for live IPFS retrieval is conditional. Config parsing is intentionally forgiving and logs errors instead of failing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations.go

Purpose: orchestrates repo migrations across legacy external migration binaries and modern embedded migrations.

Important APIs and control flow: `RunMigration` validates repo/version, finds step names, downloads missing binaries, then runs each with `-path` and optional `-revert`. `ReadMigrationConfig` reads only the config `Migration` section and fills defaults. `GetMigrationFetcher` turns download sources into HTTP fetchers or a `MultiFetcher`, rejecting legacy IPFS downloads. `findMigrations` computes ordered step names and looks for binaries in `PATH`. `RunHybridMigrations` chooses pure embedded, pure external, hybrid, or reverse hybrid paths around embedded min version 16.

State and persistence: reads repo version/config, downloads binaries to temp dirs, executes external processes that mutate repos, and calls embedded migrations that lock and rewrite config/version.

Dependencies and integration: used by repo open/migration commands; depends on config, fetchers, external executable lookup, and embedded runners.

Risks and test signals: external binaries execute with inherited stdio and trust boundary depends on fetched/verifiable artifacts. Hybrid path fallback can perform network downloads for old repos. Tests cover path finding, fetch, downgrade denial, migration config defaults/errors, and fetcher source parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations_test.go

Purpose: validates migration orchestration helpers and legacy migration fetcher configuration.

Important APIs and control flow: tests cover forward and reverse `findMigrations`, fake executable discovery, concurrent `fetchMigrations` logging/output, `RunMigration` downgrade denial and reverse execution failure shape, `ReadMigrationConfig` defaults and errors, and `GetMigrationFetcher` behavior for bad schemes, HTTP sources, HTTPS alias expansion, rejected IPFS sources, nil/empty sources, and mixed sources.

State and persistence: creates fake binaries, temp repos/configs, version files, and uses the CAR-backed test gateway.

Dependencies and integration: exercises `ExeName`, `migrationName`, `FetchBinary`, config defaults, and fetcher constructors.

Risks and test signals: strong coverage for source parsing and migration step discovery. It does not fully execute successful external migrations because fake binaries are empty, and does not cover `RunHybridMigrations` matrix directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/setup_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/setup_test.go

Purpose: builds a local test distribution and trustless gateway used by migration fetch tests.

Important APIs and control flow: `TestMain` creates fake package/version/archive data, wraps it into a CAR file, starts an `httptest` gateway backed by that CAR, stores `testIpfsDist` and `testServer`, then runs tests. Helpers generate fake tar.gz/zip archives, build UnixFS recursively into CAR storage, replace CAR roots, and create a blockservice-backed gateway.

State and persistence: writes temp package trees, archive files, CAR files, and starts an HTTP server; removes CAR file on exit.

Dependencies and integration: uses Boxo gateway/blockservice, go-car v2, UnixFS builder, IPLD link systems, multihash/cid, and unpack helper functions.

Risks and test signals: provides strong local integration coverage for HTTP fetchers without external network reliance. It is test-only but complex enough that failures can obscure fetcher failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack.go

Purpose: extracts a named binary from downloaded migration archives.

Important APIs and control flow: `unpackArchive` dispatches on `tar.gz` or `zip`. `unpackTgz` opens gzip/tar, scans entries for `<root>/<name>`, and writes the matched stream. `unpackZip` scans zip entries for the same path and writes the opened file. `writeToPath` creates the output file and copies bytes.

State and persistence: reads archive files and writes extracted binaries. It does not sanitize arbitrary archive paths beyond exact match to expected root/name.

Dependencies and integration: used by `FetchBinary`; test helpers also create matching archives.

Risks and test signals: output creation is not atomic and can leave partial files on copy error. Zip file readers are not explicitly closed for the selected entry after `writeToPath`, though archive close handles resources. Tests cover bad archive types, corrupt archives, missing binary, and successful tar/zip extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack_test.go

Purpose: validates archive extraction helpers for tar.gz and zip migration packages.

Important APIs and control flow: tests assert unrecognized archive type errors, missing/corrupt archive errors, corrupt gzip/zip errors, missing binary errors, and successful extraction with expected output size. Helper functions write synthetic tar.gz and zip archives with `<root>/<file>` layout.

State and persistence: creates temp archive and output files, then checks file sizes.

Dependencies and integration: covers `unpackArchive`, `unpackTgz`, `unpackZip`, and helper archive writers used by migration fetch tests.

Risks and test signals: good coverage for happy and failure paths. It does not simulate partial copy/write failures, permission errors, or path traversal because exact expected names are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions.go

Purpose: reads and sorts distribution version lists from migration distribution sites.

Important APIs and control flow: `DistVersions` fetches `<dist>/versions`, scans lines, parses semver after trimming a leading `v`, ignores invalid lines, sorts ascending or descending, and returns `v`-prefixed versions. `LatestDistVersion` calls `DistVersions`, scans from newest to oldest, skips `-dev` always and `-rc` when `stableOnly`, and returns the first acceptable version.

State and persistence: no local persistence; fetches version file bytes through a `Fetcher`.

Dependencies and integration: used by `fetchMigrations` and `FetchBinary` selection. Depends on `blang/semver`.

Risks and test signals: invalid lines are silently ignored, and `strings.TrimLeft` removes any run of `v` characters rather than a single prefix. Tests validate non-empty sorted version lists and semver parse of latest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions_test.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions_test.go

Purpose: checks version-list fetching and latest-version selection against the local test distribution.

Important APIs and control flow: `TestDistVersions` fetches and sorts versions descending for `go-ipfs`, requiring a non-empty result. `TestLatestDistVersion` fetches the latest version, checks basic length, and validates semver after dropping the leading `v`.

State and persistence: no writes; uses the shared test server and test distribution created in `setup_test.go`.

Dependencies and integration: exercises `NewHttpFetcher`, `DistVersions`, `LatestDistVersion`, and semver parsing.

Risks and test signals: coverage is broad enough for normal version files, but does not test `stableOnly`, dev/rc filtering edge cases, invalid-line-only files, or fetcher errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/misc.go -->
# sources/distributed-fs/ipfs-kubo/repo/fsrepo/misc.go

Purpose: resolves the best-known fsrepo path for callers that need the default repo location.

Important APIs and control flow: `BestKnownPath` starts from `config.DefaultPathRoot`, overrides it with `IPFS_PATH` (`config.EnvDir`) when set, expands `~`, and returns the expanded path.

State and persistence: no file writes; reads environment and home-directory state.

Dependencies and integration: used by code that needs a repo path without opening the repo. Depends on Kubo config constants and `fsutil.ExpandHome`.

Risks and test signals: no direct test in this subset. Errors only come from home expansion. It does not check existence, initialization, or writability; callers needing those properties must use fsrepo/migration path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/fsrepo/misc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/mock.go -->
# sources/distributed-fs/ipfs-kubo/repo/mock.go

Purpose: provides a lightweight, non-thread-safe in-memory-ish implementation of `repo.Repo` for tests and components that do not need full fsrepo behavior.

Important APIs and control flow: `Mock` stores config, datastore, keystore, and file manager fields. It returns pointers or values directly for `Config`, `SetConfig`, `Datastore`, `Keystore`, `FileManager`, and nil swarm key. Unsupported methods return `errTODO`.

State and persistence: no disk persistence; delegates datastore close to the configured datastore and mutates the embedded config field directly.

Dependencies and integration: implements the `Repo` interface and integrates with components expecting a repo but not API/gateway/config-key operations.

Risks and test signals: not thread-safe, returns direct config pointer, and `Close` panics if datastore is nil. Unsupported methods are explicit TODO errors. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/onlyone.go -->
# sources/distributed-fs/ipfs-kubo/repo/onlyone.go

Purpose: ensures a repo keyed by an arbitrary comparable value is opened only once per process and shared through reference-counted wrappers.

Important APIs and control flow: `OnlyOne.Open` initializes the active map, returns an existing `ref` when present or calls the provided open function and stores a new `ref`. It increments `refs` under a mutex. `ref.Close` decrements refs, returns without closing while refs remain, and on the final close removes the entry and closes the underlying repo.

State and persistence: in-memory active map only; underlying repo controls disk persistence and locks.

Dependencies and integration: used by `fsrepo.Open` and `OpenWithUserConfig` to avoid duplicate same-process opens against the same repo path.

Risks and test signals: key must be comparable or map access panics; keys should avoid collisions across repo implementations. If a caller forgets to close, the repo remains active. fsrepo tests cover same-process double open and reference close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/onlyone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/repo.go -->
# sources/distributed-fs/ipfs-kubo/repo/repo.go

Purpose: defines the core repository abstraction for persistent Kubo node state.

Important APIs and control flow: `Repo` includes config read/write and key-level config mutation, path, user resource overrides, config backup, datastore, storage usage, keystore, filestore manager, API/gateway address writers, swarm key reading, and `io.Closer`. `Datastore` is `go-datastore.Batching` and must be thread-safe. `ErrApiNotRunning` standardizes missing API address behavior.

State and persistence: the interface represents persistent config, datastore, keystore, network address files, swarm key, and resource override data, but does not dictate backing storage.

Dependencies and integration: implemented by `fsrepo.FSRepo`, `repo.Mock`, and `repo.OnlyOne` refs; consumed by node construction and CLI components.

Risks and test signals: `Config` returns a mutable pointer with a warning that callers must clone before changes. Thread-safety expectations are implicit for datastore and implementation-specific for config mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/repo/repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/composer.go -->
# sources/distributed-fs/ipfs-kubo/routing/composer.go

Purpose: implements a `routing.Routing` facade that dispatches each routing method to a method-specific underlying router.

Important APIs and control flow: `Composer` has router fields for get/put IPNS, peer lookup, provider lookup, and provide. Methods delegate directly and log debug details. `ProvideMany` only calls the underlying provide router when it implements `ProvideManyRouter`; otherwise it returns nil. `Ready` delegates when the provide router implements `ReadyAbleRouter`, else returns true. `Bootstrap` calls all five routers and joins errors.

State and persistence: no persistence; holds router references and delegates network/datastore state to them.

Dependencies and integration: produced by `routing.Parse`; integrates with libp2p routing interfaces and routing helper optional interfaces.

Risks and test signals: nil router fields will panic if a method is called without config assignment. Bootstrap may call the same router multiple times when methods share routers. Parser tests verify shared router instances for multiple methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/composer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/delegated.go -->
# sources/distributed-fs/ipfs-kubo/routing/delegated.go

Purpose: parses custom routing configuration into HTTP, DHT, sequential, parallel, and composed routing implementations.

Important APIs and control flow: `Parse` validates method config, recursively builds named routers through `parse`, caches created routers, detects dependency loops, and assigns routers to a `Composer`. HTTP routers build a delegated routing client with response body limits, OpenTelemetry transport span names, identity, provider info, user agent, protocol filtering, streaming results, and content router batching/concurrency. DHT routers create regular, private/public, or full-routing-table DHTs based on config.

State and persistence: no direct persistence; DHT routers use the provided datastore and host, and HTTP routers may advertise provider info from dynamic addresses.

Dependencies and integration: depends on Kubo config routing structures, Boxo delegated routing clients, libp2p DHT/fullrt, validators, host, datastore, OpenCensus/OpenTelemetry, and `Composer`.

Risks and test signals: `extraHTTP` and `extraDHT` are assumed non-nil for selected router types; malformed configs can panic before type checks. `view.Register` may error on duplicate registration. Tests cover parser composition, recursive nesting, and loop detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/delegated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/delegated_test.go -->
# sources/distributed-fs/ipfs-kubo/routing/delegated_test.go

Purpose: validates custom routing parser behavior for HTTP routers and composable router graphs.

Important APIs and control flow: `TestParser` builds HTTP and sequential routers and checks methods sharing router names share router instances in the resulting `Composer`. `TestParserRecursive` builds nested sequential and parallel router graphs and expects a `Composer`. `TestParserRecursiveLoop` creates a dependency loop and checks for the loop error. `generatePeerID` creates an Ed25519 key and base64 private key for HTTP router identity.

State and persistence: no disk state; creates crypto keys and routing structs.

Dependencies and integration: exercises `Parse`, HTTP router construction, config router types, and composer assignment.

Risks and test signals: tests use dummy HTTP endpoints but do not perform network calls. They do not cover DHT routers, missing parameters, invalid keys, duplicate metric view registration, or nil extra params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/delegated_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/error.go -->
# sources/distributed-fs/ipfs-kubo/routing/error.go

Purpose: defines a typed error for missing routing configuration parameters.

Important APIs and control flow: `NewParamNeededErr` constructs `ParamNeededError` with the missing param and router type. `Error` formats a message explaining the required configuration parameter for delegated routing types.

State and persistence: none.

Dependencies and integration: used by `httpRoutingFromConfig` when the HTTP router endpoint is missing. Depends on Kubo config router type definitions.

Risks and test signals: no direct tests, but parser error paths can expose this. Message wording says "delegated routing types" generically even when a specific type is involved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/wrapper.go -->
# sources/distributed-fs/ipfs-kubo/routing/wrapper.go

Purpose: adapts delegated HTTP routing client components into libp2p routing interfaces.

Important APIs and control flow: `ProvideManyRouter` combines routing helper batch providing with `routing.Routing`. `httpRoutingWrapper` embeds content routing, peer routing, value store, and provide-many interfaces. `Bootstrap` is a no-op because HTTP delegated routers do not need peer bootstrap.

State and persistence: no state beyond embedded router implementations.

Dependencies and integration: returned by `httpRoutingFromConfig`; lets HTTP delegated routing satisfy `routing.Routing` and optional batch provide interfaces.

Risks and test signals: compile-time assertions check interface conformance. Because methods are supplied through embedding, missing embedded components would result in nil-interface panics if constructed incorrectly. Parser tests indirectly create wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/routing/wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/GNUmakefile -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/GNUmakefile

Purpose: orchestrates the legacy three-node Docker integration test.

Important APIs and control flow: `test` runs `clean` and `setup`, then `run-test-on-img.sh`. `setup` builds the IPFS image and creates tiny/random data files. `docker_ipfs_image` builds an image from the root Dockerfile. `clean` stops/removes fig services, deletes generated binaries/data/build outputs, and removes dangling Docker images.

State and persistence: creates `data/filetiny`, `data/filerand`, `bin/random`, Docker images/containers, and build logs/profiling outputs.

Dependencies and integration: relies on Docker, legacy `fig`, repository test random binary, and sibling scripts.

Risks and test signals: cleanup uses broad Docker commands that can remove exited containers and dangling images beyond the test. Uses old `fig` tooling and old Docker tag syntax in scripts. No automated unit tests for Makefile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/clean.sh -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/clean.sh

Purpose: removes exited Docker containers before the three-node test runs.

Important APIs and control flow: a single command runs `docker ps -q -a -f status=exited`, passes IDs to `docker rm -f`, and ignores failures with `|| true`.

State and persistence: mutates Docker daemon state by removing all exited containers visible to the user, not only this test's containers.

Dependencies and integration: invoked by the 3nodetest Makefile `clean` target.

Risks and test signals: broad cleanup can affect unrelated Docker workflows. With no exited containers, command substitution may produce an empty `docker rm -f` invocation, hidden by `|| true`. No tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/clean.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_logs.sh -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_logs.sh

Purpose: captures Docker logs from the three-node test containers into build artifacts.

Important APIs and control flow: defines a Perl escape-stripping command and pipes logs from bootstrap, client, data, and server containers into `./build/*.log`.

State and persistence: writes log files under `build/`.

Dependencies and integration: invoked by Makefile and `run-test-on-img.sh` after `fig up`; depends on Docker, Perl, and fixed container names.

Risks and test signals: hard-coded names couple it to fig naming. `eval $STRIP` adds shell-evaluation risk, though the string is static. Missing containers fail the corresponding pipeline unless caller ignores errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_profiling_data.sh -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_profiling_data.sh

Purpose: copies profiling artifacts from 3nodetest containers into the build directory.

Important APIs and control flow: loops over bootstrap/client/server to copy `/go/bin/ipfs` and `/go/ipfs.cpuprof`, then copies `/go/ipfs.memprof` from bootstrap and server. Client memprof is skipped because the client daemon is not terminated.

State and persistence: writes profiling files under `build/profiling_data_<container>`.

Dependencies and integration: depends on Docker and containers running with `IPFS_PROF`/debug profiling output.

Risks and test signals: hard-coded container names and paths. `docker cp` failures stop the script unless caller ignores errors; the main runner does ignore failures. No tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_profiling_data.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/Dockerfile -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/Dockerfile

Purpose: builds the bootstrap node image for the three-node integration test.

Important APIs and control flow: starts from `zaqwsx_ipfs-test-img`, initializes an IPFS repo, replaces config from the Docker build context, runs `ipfs id`, enables profiling and no-color logs, and exposes TCP/UDP swarm ports.

State and persistence: creates `/root/.ipfs` at image build time with a fixed identity/config.

Dependencies and integration: used by `fig.yml` bootstrap service and linked by client/server via environment variables.

Risks and test signals: embeds static private key material suitable only for tests. Depends on old base image tag and old config schema. No Dockerfile-specific tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/config -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/config

Purpose: static IPFS config for the 3nodetest bootstrap node.

Important APIs and control flow: JSON defines fixed identity/private key, old-style LevelDB datastore path/type, swarm/API addresses, mounts, version update policy fields, and an empty bootstrap list.

State and persistence: becomes `/root/.ipfs/config` inside the bootstrap image. The fixed identity is used by server/client bootstrap commands.

Dependencies and integration: consumed by bootstrap Dockerfile and referenced by client/server `run.sh` peer ID.

Risks and test signals: old config format uses `Datastore.Type` and `Path`, incompatible with newer fsrepo open logic unless migration/init path handles it in the test image. Static private key is test-only. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/client/Dockerfile -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/client/Dockerfile

Purpose: builds the client node image for the three-node integration test.

Important APIs and control flow: initializes an IPFS repo, installs static config, prints node identity, exposes swarm ports, enables profiling/no-color logs, and sets `/tmp/id/run.sh` as the default bash command.

State and persistence: creates a test repo with static identity and config in the image layer.

Dependencies and integration: run by `fig.yml` client service linked to bootstrap and sharing data volume.

Risks and test signals: static private key and old config schema are test-only. Runtime success depends on environment variables injected by legacy fig links and the server writing CID files to the shared volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/client/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/client/config -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/client/config

Purpose: static IPFS config for the 3nodetest client node.

Important APIs and control flow: JSON defines fixed identity/private key, API and swarm addresses, empty bootstrap list, old-style datastore, mounts, and version-check settings.

State and persistence: copied into `/root/.ipfs/config` during client image build.

Dependencies and integration: used by client Dockerfile and runtime `run.sh` which adds bootstrap dynamically.

Risks and test signals: old-style datastore config and fixed identity are only appropriate for historical integration tests. No direct validation besides the full 3nodetest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/client/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/client/run.sh -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/client/run.sh

Purpose: runs the client side of the three-node integration test, fetching files from IPFS and comparing them to shared-volume originals.

Important APIs and control flow: adds the bootstrap node from fig link env vars, starts `ipfs daemon --debug` in background, waits for `/data/idtiny`, cats the tiny CID to a file, diffs it against `/data/filetiny`, waits for `/data/idrand`, cats the random CID, checks command status, diffs against `/data/filerand`, and prints success.

State and persistence: writes fetched files in `/tmp`; reads CID marker files and original data from `/data`; starts a long-running daemon that produces profiling files.

Dependencies and integration: depends on server writing CID files, bootstrap service, shared data volume, and shell arithmetic syntax under bash.

Risks and test signals: no timeout while waiting for marker files, so failures can hang. Background daemon is not explicitly stopped, which affects memprof collection. Full test success is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/client/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/data/Dockerfile -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/data/Dockerfile

Purpose: builds a data-only container image for the three-node integration test.

Important APIs and control flow: starts from Ubuntu, adds generated `filetiny` and `filerand` into `/data`, and declares `/data` as a volume.

State and persistence: seeds the shared Docker volume with test input files.

Dependencies and integration: used by `fig.yml` as the data service, with server and client using `volumes_from`.

Risks and test signals: assumes Makefile has generated the data files before image build. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/data/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/fig.yml -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/fig.yml

Purpose: defines the legacy fig/docker-compose topology for the three-node integration test.

Important APIs and control flow: services are `data`, `bootstrap`, `server`, and `client`. Data builds a volume and sleeps. Bootstrap runs `daemon --debug --init`. Server and client build their images, link to bootstrap, share the data volume, expose swarm ports, and set debug logging.

State and persistence: creates containers, shared `/data` volume, and image builds. Server writes CID marker files that client reads.

Dependencies and integration: consumed by legacy `fig` commands in the Makefile and runner script.

Risks and test signals: uses obsolete fig syntax and link-based environment variables. Container names expected by log/profiling scripts derive from fig naming. No standalone tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/fig.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/run-test-on-img.sh -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/run-test-on-img.sh

Purpose: runs the 3nodetest stack against a supplied Docker image reference.

Important APIs and control flow: validates one argument, finds the image ID with `docker images | grep`, tags it as `zaqwsx_ipfs-test-img`, runs `fig build --no-cache`, runs `fig up --no-color` while teeing `build/fig.log`, saves logs and profiling data best-effort, then greps the log tail for `exited with code 0` as success detection.

State and persistence: mutates Docker image tags, builds containers/images, writes `build/fig.log`, logs, and profiling data.

Dependencies and integration: called by the Makefile `test` target; depends on Docker, fig, make, and fixed service behavior.

Risks and test signals: image lookup by grep can match multiple images. Success detection via tail/grep is brittle because fig may not return service exit codes. Old `docker tag -f` syntax may fail on modern Docker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/run-test-on-img.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/server/Dockerfile -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/server/Dockerfile

Purpose: builds the server node image for the three-node integration test.

Important APIs and control flow: initializes a repo, installs static config, prints identity, marks `run.sh` executable, exposes swarm ports, enables profiling/no-color logs, and runs `/tmp/test/run.sh` under bash.

State and persistence: embeds a static server repo/config in the image layer.

Dependencies and integration: used by `fig.yml` server service linked to bootstrap and sharing the data volume.

Risks and test signals: static private key and old config schema are test-only. Runtime behavior depends on fig link env vars and shared volume access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/server/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/server/config -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/server/config

Purpose: static IPFS config for the 3nodetest server node.

Important APIs and control flow: JSON defines fixed identity/private key, API and swarm addresses, empty bootstrap list, old-style datastore, mounts, and version update fields.

State and persistence: copied into `/root/.ipfs/config` in the server image; runtime script adds bootstrap dynamically and writes added CIDs to `/data`.

Dependencies and integration: used by server Dockerfile and runtime script.

Risks and test signals: fixed private key and old datastore config are suitable only for isolated tests. No direct tests beyond the full three-node flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/server/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/server/run.sh -->
# sources/distributed-fs/ipfs-kubo/test/3nodetest/server/run.sh

Purpose: runs the server side of 3nodetest by adding shared files to IPFS and publishing their CIDs through shared files.

Important APIs and control flow: adds bootstrap node from fig link env vars, starts `ipfs daemon --debug`, sleeps for startup, changes to `/tmp`, adds `/data/filetiny` and `/data/filerand`, writes CIDs via temp files renamed to `/data/idtiny` and `/data/idrand`, then sleeps for a long time so the client can retrieve data.

State and persistence: writes CID marker files to shared `/data`, creates daemon profiling output, and keeps the container alive.

Dependencies and integration: depends on bootstrap service, shared data container, IPFS CLI, and client polling.

Risks and test signals: fixed sleeps and very long final sleep make failures slow. No timeout or readiness check beyond sleep. Atomic-ish marker file rename prevents client seeing partial CID files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/3nodetest/server/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/test/Rules.mk

Purpose: includes the test subtree make rules into the repository make system.

Important APIs and control flow: includes `mk/header.mk`, sets `dir` to `test/bin`, `test/sharness`, and `test/unit` in turn and includes each `Rules.mk`, then includes `mk/footer.mk`.

State and persistence: no direct writes; participates in make target graph construction.

Dependencies and integration: relies on surrounding make variables, `mk/header.mk`, `mk/footer.mk`, and child Rules files.

Risks and test signals: simple include file with no standalone tests. Missing child files or unexpected `dir` variable behavior would break make parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/api-startup/main.go -->
# sources/distributed-fs/ipfs-kubo/test/api-startup/main.go

Purpose: utility program measuring relative startup time of Kubo API and gateway HTTP endpoints.

Important APIs and control flow: starts two goroutines polling `http://127.0.0.1:5001` and `http://127.0.0.1:8080` until each returns a response, sends the timestamp to a buffered channel, waits for both goroutines, reads both timestamps, and logs their difference.

State and persistence: no persistence; loops aggressively until endpoints respond.

Dependencies and integration: intended for test/manual startup measurement against a local daemon exposing default API and gateway ports.

Risks and test signals: no sleep, timeout, response body close, or status filtering, so it can spin hot, hang forever, and leak response bodies in the short run. It logs timing but does not assert success thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/api-startup/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bench/bench_cli_ipfs_add/main.go -->
# sources/distributed-fs/ipfs-kubo/test/bench/bench_cli_ipfs_add/main.go

Purpose: benchmark utility for measuring `ipfs add` CLI performance over generated random files.

Important APIs and control flow: `main` calls `compareResults`, which repeatedly benchmarks increasing sizes starting at 10 MB. `benchmarkAdd` uses `testing.Benchmark`; each iteration creates a temp repo via `IPFS_PATH`, runs `ipfs init`, writes deterministic random data to a temp file, optionally starts an `ipfs daemon`, times `ipfs add`, and returns the benchmark result.

State and persistence: creates temp repos and temp input files, runs external `ipfs` processes, and optionally starts/stops a daemon. Debug mode streams command output to console.

Dependencies and integration: depends on `ipfs` binary in PATH, Kubo config env var, go-test random, and Kubo unit constants.

Risks and test signals: `compareResults` loop condition grows `amount` while `amount > 0`, which depends on integer overflow to terminate and can run many sizes. Online mode is marked broken due to datastore locking. It is a benchmark, not a correctness test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bench/bench_cli_ipfs_add/main.go -->
