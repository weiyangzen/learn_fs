# subset-b-000501 Research

Grouped source-tree-aligned research for the requested BeeGFS Go CTL command files. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/create.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/create.go

- Purpose: defines `mirror create` and `mirror autocreate` for manual and automatic buddy group creation.
- Important APIs: `createBuddyGroup_Config`, `newCreateBuddyGroupCmd`, `newCreateBuddyGroupsAutomaticCmd`, `runCreateBuddyGroupCmd`, and `runCreateBuddyGroupsAutomaticCmd`.
- Control flow/state: Cobra parses alias, node type, numeric ID, primary, and secondary targets into BeeGFS entity types, then sends `pm.CreateBuddyGroupRequest` through `ctl/pkg/ctl/buddygroup.Create`; autocreate delegates to `backend.AutoCreate` and prints each created group plus warnings.
- Dependencies/integration: relies on `beegfs` parsers/proto conversion, `cmdfmt`, management protobufs, and `util.NewCtlError` for partial success.
- Risks/tests: no local tests in this file; risk is mostly destructive cluster state mutation and warning handling, especially continuing after partial automatic creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/delete.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/delete.go

- Purpose: implements hidden `mirror delete <group>` for storage buddy group removal with a dry-run default.
- Important APIs: `deleteBuddyGroup_Config`, `newDeleteBuddyGroupCmd`, and `runDeleteBuddyGroupCmd`.
- Control flow/state: parses the storage group identifier with `NewEntityIdParser`, builds `pm.DeleteBuddyGroupRequest`, and passes `Execute` from `--yes`; dry run confirms deletability, while execute prints deletion success.
- Dependencies/integration: uses management backend `ctl/pkg/ctl/buddygroup.Delete`, `beegfs.EntityIdSetFromProto`, and `cmdfmt` user-facing output.
- Risks/tests: command warns about corruption conditions but cannot verify them locally; missing group info is fatal in dry run but only a warning after execution. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/initialize.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/initialize.go

- Purpose: adds `mirror init` to initialize mirroring for the root directory.
- Important APIs: `newMirrorRootInodeCmd` and `runMirrorRootInode`.
- Control flow/state: the command is no-arg and gated by `--yes`; without confirmation it prints a dry-run warning and exits, otherwise calls `buddygroup.MirrorRootInode` and prints a restart/remount note.
- Dependencies/integration: integrates with `ctl/pkg/ctl/buddygroup` and `cmdfmt`; state change is persisted by the backend/management service, not by the CLI.
- Risks/tests: irreversible metadata state change; safety depends on user satisfying stopped-client and metadata mirror preconditions. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/initialize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/list.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/list.go

- Purpose: lists BeeGFS metadata or storage buddy groups for `mirror list`.
- Important APIs: `list_Config`, `newListCmd`, and `runListCmd`.
- Control flow/state: fetches all buddy groups with `buddygroup.GetBuddyGroups`, filters by optional node type, formats primary/secondary target IDs differently in debug mode, and prints a table.
- Dependencies/integration: uses `cmdfmt.Printomatic`, Viper `config.DebugKey`, BeeGFS entity formatting, and `ctl/pkg/ctl/buddygroup`.
- Risks/tests: output correctness depends on backend returning complete target mapping; debug and non-debug fields have separate formatting paths. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/restart.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/restart.go

- Purpose: defines `mirror resync restart <buddy-group>` as a restart variant of resync start.
- Important APIs: `newRestartCmd` reuses `startResync_config` and `runStartResyncCmd`.
- Control flow/state: parses a meta/storage buddy group, accepts `--timestamp` or `--timespan`, sets `restart: true`, and delegates execution to the shared start runner.
- Dependencies/integration: depends on `beegfs.NewEntityIdParser`, Cobra duration/int flags, and backend resync start semantics.
- Risks/tests: restart mode likely resets existing resync progress; validation for mutually exclusive timestamp/timespan is handled in shared code. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/restart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/resync.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/resync.go

- Purpose: creates the `mirror resync` command namespace.
- Important APIs: exported `NewResyncCmd`.
- Control flow/state: registers `stats`, `start`, and `restart` subcommands and performs no direct state mutation.
- Dependencies/integration: plugs the resync namespace into `buddygroup.NewCmd`; all work is delegated to sibling command files.
- Risks/tests: low logic risk; coverage is mainly command-tree integration. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/resync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/start.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/start.go

- Purpose: implements `mirror resync start <buddy-group>` for metadata or storage mirror resync.
- Important APIs: `startResync_config`, `newStartResyncCmd`, and `runStartResyncCmd`.
- Control flow/state: parses group ID, supports `--timestamp` or `--timespan`; timespan converts to Unix timestamp using current time, then calls `backend.StartResync` with a restart flag.
- Dependencies/integration: uses BeeGFS entity parsing and `ctl/pkg/ctl/buddygroup/resync`.
- Risks/tests: timestamp and timespan cannot both be set, and timespan is storage-only by help text but not visibly enforced here. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/stats.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/stats.go

- Purpose: prints resync statistics for a buddy group.
- Important APIs: `newResyncStatsCmd`, `runResyncStatsCmd`, `printMetaResults`, and `printStorageResults`.
- Control flow/state: parses a group ID, resolves the current primary with `backend.GetPrimaryTarget`, dispatches to metadata or storage stats RPC based on node type, then prints candidate, error, progress, and result counters.
- Dependencies/integration: depends on BeeMsg response types, entity parsing, and resync backend helpers.
- Risks/tests: direct `fmt` output is not table-aware; output field coverage must track protocol changes. No local tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/setalias.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/setalias.go

- Purpose: implements `mirror set-alias <buddygroup> <alias>`.
- Important APIs: `newSetAliasCmd` and `runSetAliasCmd`.
- Control flow/state: parses a meta/storage entity ID and validates alias, then calls `backend.SetAlias` and prints success.
- Dependencies/integration: integrates with management alias storage through `ctl/pkg/ctl/buddygroup`; uses common BeeGFS alias and entity parsers.
- Risks/tests: no confirmation or existence preflight here; backend must enforce uniqueness and validity. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/setalias.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/copy/copy.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/copy/copy.go

- Purpose: exposes licensed parallel copy functionality as `copy`/`cp`, wrapping `/opt/beegfs/sbin/beegfs-copy`.
- Important APIs: `NewCopyCmd`, `frontendCfg`, `copyRunner`, `copyUsingStdin`, and `readBatchFromStdin`.
- Control flow/state: validates binary presence, verifies license feature `io.beegfs.copy`, translates Go flags via `bflag`, runs the external copy binary, and optionally batches stdin paths by delimiter and batch size.
- Dependencies/integration: uses `config.ManagementClient`, `VerifyLicense`, `bflag`, stdin utilities, `os/exec`, and logger debug fields.
- Risks/tests: `copyRunner` calls `os.Exit` on external nonzero exit, bypassing normal Cobra cleanup; `copyUsingStdin` does not return errors from `copyRunner`, so batched failures can be lost. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/copy/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/debug/debug.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/debug/debug.go

- Purpose: hidden `debug <node> <command>` passthrough for node debug commands.
- Important APIs: `NewCmd` and `runGenericDebugCmd`.
- Control flow/state: parses a meta/storage node, concatenates all remaining positionals into a single command string, calls `dbg.GenericDebugCmd`, and prints the raw response.
- Dependencies/integration: uses BeeGFS entity parsing and `ctl/pkg/ctl/debug`; command list is documented in long help but execution is backend-defined.
- Risks/tests: deliberately dangerous debug surface, including cache dropping and state inspection/modification; trailing space in command assembly is benign only if backend tolerates it. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/debug/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/create.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/create.go

- Purpose: provides `entry create file` and `entry create directory` for direct BeeGFS entry creation with explicit metadata/striping settings.
- Important APIs: `newCreateCmd`, `newCreateFileCmd`, `newCreateDirCmd`, and `PrintCreateEntryResult`.
- Control flow/state: each subcommand fills `entry.CreateEntryCfg`, validates paths, calls `entry.CreateEntry`, and prints per-path status; file flags cover targets, buddy groups, pool, stripe pattern, RSTs, permissions, UID/GID, and force.
- Dependencies/integration: depends on custom flag parsers from `flags.go`, remote target flag helper, backend create APIs, and `cmdfmt`.
- Risks/tests: creation bypasses filesystem modification events per help text; defaults for UID/GID/permissions are set by flag constructors. Partial per-entry failures return a generic error after table output. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/disposal.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/disposal.go

- Purpose: implements `entry dispose-unused` for cleaning unlinked-but-open disposal files.
- Important APIs: `entryDisposalCfg`, `newEntryDisposalCmd`, and `runEntryDisposalCmd`.
- Control flow/state: calls `entry.CleanupDisposals`, consumes result and error channels, prints optional per-entry rows, and summarizes disposed versus total files.
- Dependencies/integration: uses `types.MultiError`, `beegfs.OpsErr_SUCCESS`, and backend disposal cleanup.
- Risks/tests: concurrent result/error channels require draining buffered results after errors; disposal mutates filesystem state only with `--dispose`, otherwise dry runs. No local tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/disposal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/entry.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/entry.go

- Purpose: defines the `entry` command namespace.
- Important APIs: exported `NewEntryCmd`.
- Control flow/state: creates a no-arg Cobra command and registers info, set, disposal, migrate, create, and refresh subcommands.
- Dependencies/integration: is imported by root command assembly in `root.go`; concrete behavior is in sibling files and `ctl/pkg/ctl/entry`.
- Risks/tests: command-tree integration only; no persistence or direct backend calls. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/flags.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/flags.go

- Purpose: supplies custom `pflag.Value` implementations for entry create/set configuration.
- Important APIs: `chunksizeFlag`, `poolFlag`, `stripePatternFlag`, `numTargetsFlag`, `rstCooldownFlag`, `accessControlFlag`, `dataStateFlag`, `permissionsFlag`, `userFlag`, and `groupFlag`.
- Control flow/state: parsers set pointer fields in backend configs to distinguish unchanged values from explicit values; UID/GID and permissions constructors also install defaults.
- Dependencies/integration: uses `util.ParseIntFromStr`, BeeGFS entity and enum types, OS effective UID/GID, and duration parsing.
- Risks/tests: pointer-to-pointer state is subtle; `rstCooldownFlag` does not reject negative durations, and permission parsing does not bound mode bits. No direct tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/info.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/info.go

- Purpose: implements `entry info` for table or retro details about BeeGFS entries.
- Important APIs: `entryInfoCfg`, `newEntryInfoCmd`, `runEntryInfoCmd`, `assembleRetroEntry`, and `assembleTableRow`.
- Control flow/state: selects path input method from args/stdin/recurse, streams `entry.GetEntries` results, handles verbose-detail errors as warnings, and renders either table rows or old-style vertical output.
- Dependencies/integration: uses filesystem filters, Viper debug/raw flags, `cmdfmt`, unit formatting, entry backend combined info, and logger warnings.
- Risks/tests: output has many conditionals for directories, files, mirrored metadata, RSTs, unavailable details, and verbose paths; TODO notes table verbose output is incomplete. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/migrate.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/migrate.go

- Purpose: implements `entry migrate` for moving file data away from source targets/nodes/pools to destination pools/targets/groups.
- Important APIs: `migrateCfg`, `newMigrateCmd`, and `migrateRunner`.
- Control flow/state: enforces path args and recursive `--yes`, builds `entry.MigrateCfg`, chooses path input method, streams migration results, updates `MigrateStats`, prints verbose/error rows, and returns partial success for per-entry failures.
- Dependencies/integration: uses BeeGFS entity flags, filesystem filters, background rebalancing version constants, `entry.MigrateEntries`, and CTL partial-success errors.
- Risks/tests: migration has high consistency risk, especially temp-file mode on live writable trees; recursive operations are gated but stdin bulk input is not separately confirmed. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/migrate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/refresh.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/refresh.go

- Purpose: implements `entry refresh` to synchronize BeeGFS metadata with backing filesystem state after repair or delays.
- Important APIs: local `frontendCfg`, `newRefreshEntryInfoCmd`, and `runRefreshEntryInfoCmd`.
- Control flow/state: validates paths, supports stdin delimiter and recursive `--yes`, determines path input method, calls `entry.RefreshEntriesInfo`, prints path/status/entry ID rows, and returns backend wait errors.
- Dependencies/integration: uses BeeGFS op status, path input utility, `cmdfmt`, and entry backend refresh stream.
- Risks/tests: recursive refresh can touch many entries and is gated; status output is per-entry but no partial-success wrapping is visible here. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/refresh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/set.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/set.go

- Purpose: implements `entry set` for directory stripe defaults, storage pools, RSTs, and hidden file state updates.
- Important APIs: `entrySetCfg`, `newEntrySetCmd`, `runEntrySetCmd`, and `sprintfNewEntryConfig`.
- Control flow/state: validates path args, disallows mixing `--access-flags`/`--data-state` with ordinary config flags in `PreRunE`, gates recursion with `--yes`, streams `entry.SetEntries`, and prints summary/optional per-entry updates.
- Dependencies/integration: uses custom flag types, remote target flags, filesystem filters, backend `SetEntryCfg`, reflection for summary formatting, and path input utility.
- Risks/tests: reflection output depends on backend struct field names; hidden state flags mutate regular file access/data state and have stricter allowed flag combinations. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/bundle.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/bundle.go

- Purpose: creates `health bundle <path>` support archives containing CTL command output.
- Important APIs: `supportFile`, `supportCommand`, `supportBundleContents`, `newBundleCmd`, `getGlobalConfig`, `collectSupportFiles`, `bundleSupportFiles`, and `addFileToTar`.
- Control flow/state: creates timestamped temp directory, runs configured subcommands with global flags and forced debug, writes sectioned text files, tars/gzips them, and deletes the temp directory.
- Dependencies/integration: uses Viper settings, `os.Args[0]` self-exec, tar/gzip writers, and health utility headers.
- Risks/tests: temporarily reassigns global `os.Stdout`/`os.Stderr`; command failures are embedded and ignored per section. Bundle filename uses RFC3339 colons. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/bundle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check.go

- Purpose: implements full and quick BeeGFS health checks.
- Important APIs: `Status`, `checkCfg`, `newCheckCmd`, `runHealthCheckCmd`, `checkForFallbacks`, `checkTargets`, `checkForBusyNodes`, `printBusyNodes`, `checkTLSCertificates`, `tlsCertExpirationStatus`, and `QuickChecks`.
- Control flow/state: fetches clients, targets, license, node stats, TLS peer data, and network connections; prints sections for general checks, busy nodes, targets, and connections; optionally watches and ignores failures.
- Dependencies/integration: uses procfs, target/stats/license backends, gRPC peer credentials, Viper display config, and terminal refresh utilities.
- Risks/tests: many remote/local dependencies can make failures environmental; quick checks must stay synchronized with full checks. TLS expiration logic has focused unit coverage in `check_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check_test.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check_test.go

- Purpose: unit-tests TLS certificate expiration classification used by health checks.
- Important APIs: `TestTLSCertExpirationStatus`, `TestTLSCertExpirationStatusUsesEarliestExpiry`, and `TestTLSCertExpirationStatusNoCerts`.
- Control flow/state: builds synthetic `x509.Certificate` slices around a fixed `2026-01-01` clock and asserts `Healthy`, `Degraded`, or `Critical` plus exact user-facing message text.
- Dependencies/integration: uses `stretchr/testify/assert` and the package-local `tlsCertExpirationStatus`.
- Risks/tests: good boundary coverage at 90 and 30 days, expired durations, no certs, and earliest-chain expiry. It does not cover `checkTLSCertificates` peer extraction or non-TLS transport cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/df.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/df.go

- Purpose: implements `health capacity` alias `df` for metadata and storage target capacity.
- Important APIs: `newDFCmd` and `printDF`.
- Control flow/state: gets all targets, splits meta versus storage, sorts each by target numeric ID, prints headings, and delegates table rendering to `target.PrintTargetList`.
- Dependencies/integration: depends on `ctl/pkg/ctl/target.GetTargets`, target frontend print config, and BeeGFS node type constants.
- Risks/tests: no local persistence; output ordering depends on stable numeric sort. `<=` in sort comparator is unusual because Go sort expects strict less. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/df.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/health.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/health.go

- Purpose: defines the `health` command namespace.
- Important APIs: exported `NewHealthCmd`.
- Control flow/state: creates a no-arg Cobra command and adds `check`, `network`, `capacity`, and `bundle` subcommands.
- Dependencies/integration: imported by root command and used by post-run quick-alert handling.
- Risks/tests: low logic risk; command-tree registration is the main behavior. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/net.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/net.go

- Purpose: implements `health network` alias `net` for local BeeGFS client connections.
- Important APIs: `netCfg`, `newNetCmd`, `runNetCmd`, and `printBeeGFSNet`.
- Control flow/state: loads local clients from procfs, optionally filters by configured management service, can force storage connections through df, then prints management, metadata, and storage node connection lines.
- Dependencies/integration: uses `procfs.GetBeeGFSClients`, mount filtering config, timeout flags, and shared health header utilities.
- Risks/tests: health meaning is nuanced because idle clients can show no connections; force-connections can block on unreachable storage nodes. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/net.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/utils.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/utils.go

- Purpose: shared formatting helpers for health command headings and client headers.
- Important APIs: `printHeader`, `sPrintHeader`, and `printClientHeader`.
- Control flow/state: builds repeated-character headers sized to the longest line, prints them, and formats client ID plus management/mount mapping.
- Dependencies/integration: uses `cmdfmt` for output and `procfs.Client` data from health network/check flows.
- Risks/tests: output-only helpers; multi-line header sizing is custom and not directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/common.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/common.go

- Purpose: common constants, flags, and package checks for BeeGFS Hive Index commands.
- Important APIs: `beeBinary`, `indexConfig`, package-level `path`, `commonIndexFlags`, and `checkBeeGFSConfig`.
- Control flow/state: validates external binary `/opt/beegfs/python/index/bee` and config `/etc/beegfs/index/config`; common flags translate CTL names to Hive Index CLI flags.
- Dependencies/integration: uses `bflag` and global config wrappers for mount point, worker count, and debug.
- Risks/tests: global `path` is shared by stat/stats commands and could be confusing; existence checks ignore non-ENOENT stat failures. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/create.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/create.go

- Purpose: implements `index create` by invoking the external Hive Index `bee index` command.
- Important APIs: `newGenericCreateCmd`, `newCreateCmd`, and `runPythonCreateIndex`.
- Control flow/state: performs package/config checks, gathers wrapped flags from `bflag`, prefixes `index`, starts the Python binary, wires stdout/stderr, and waits.
- Dependencies/integration: uses `os/exec`, CTL logger, `commonIndexFlags`, and Hive Index filesystem/database tools.
- Risks/tests: external process exit code is wrapped as an execution error but not propagated as exact exit status; correctness depends on installed package version. No local tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/dbupgrade.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/dbupgrade.go

- Purpose: defines a currently disabled/unused Hive Index database upgrade command.
- Important APIs: `newGenericUpgradeCmd`, `newUpgradeCmd`, and `runPythonUpgradeIndex`, retained via blank identifier assignments.
- Control flow/state: checks package config, wraps db flags, injects `-n <numWorkers>`, and runs `bee db`.
- Dependencies/integration: uses Viper worker config, `bflag`, logger, and external Hive Index database utilities.
- Risks/tests: upgrade/downgrade/delete/restore operations are persistent database mutations; the command appears intentionally not registered in `index.go`, reducing accidental exposure. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/dbupgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/find.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/find.go

- Purpose: implements `index find` by adapting many find-like flags to Hive Index `bee find`.
- Important APIs: `newGenericFindCmd`, `newFindCmd`, and `runPythonFindIndex`.
- Control flow/state: defaults path to current working directory, checks Hive Index installation/config, appends paths and wrapped predicate/action flags, adds output format `-Q` when non-table output is configured, then execs the Python binary.
- Dependencies/integration: uses `bflag`, Viper output config, and `os/exec`; annotated as allowed for all users.
- Risks/tests: large user-provided flag surface has little local validation; SQL/index semantics live in external tool. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/index.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/index.go

- Purpose: defines the `index` command namespace for BeeGFS Hive Index operations.
- Important APIs: exported `NewCmd`.
- Control flow/state: builds no-arg Cobra command and registers `create`, `ls`, `find`, `stat`, `stats`, `query`, and `rescan`; database upgrade is not registered.
- Dependencies/integration: imported by root command; behavior delegated to sibling wrappers and external Hive Index tools.
- Risks/tests: namespace depends on external package presence for most subcommands. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/ls.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/ls.go

- Purpose: implements `index ls` by invoking Hive Index `bee ls`.
- Important APIs: `newGenericLsCmd`, `newLsCmd`, and `runPythonLsIndex`.
- Control flow/state: defaults paths to cwd, validates Hive Index installation, translates many GNU-ls-like flags, appends output format when requested, and execs the external binary.
- Dependencies/integration: uses `bflag`, Viper output config, and `os/exec`; hidden `in-memory-name` and custom help flag maintain compatibility.
- Risks/tests: ordering of paths before wrapped flags may matter for external parsing; direct tests are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/query.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/query.go

- Purpose: implements `index query` for SQL queries against single-level Hive Index databases.
- Important APIs: `newGenericQueryCmd`, `newQueryCmd`, and `runPythonQueryIndex`.
- Control flow/state: validates Hive Index configuration, forwards `--db-path` and `--sql-query`, appends output format `-Q` for non-table output, and executes `bee query-index`.
- Dependencies/integration: uses external Hive Index SQL/query engine, `bflag`, Viper output config, and logger.
- Risks/tests: raw SQL is forwarded without local validation; only last statement output is documented. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/query.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/rescan.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/rescan.go

- Purpose: implements `index rescan <directory-path>` for refreshing an indexed subtree.
- Important APIs: `newGenericRescanCmd`, `newRescanCmd`, and `runPythonRescanIndex`.
- Control flow/state: defaults to cwd, validates package/config, wraps rescan flags, runs `bee rescan` for non-recursive mode or tree-summary/rescan-related external flow for recursive mode as implemented in the runner.
- Dependencies/integration: uses `bflag`, global worker/debug flags, and external Hive Index rescan tools.
- Risks/tests: persistent index updates and stale-entry deletion are delegated externally; recursive behavior can update broad database state. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/rescan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stat.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stat.go

- Purpose: implements `index stat` by invoking Hive Index `bee stat`.
- Important APIs: `newGenericStatCmd`, `newStatCmd`, and `runPythonStatIndex`.
- Control flow/state: chooses a single path argument or cwd, validates Hive Index config, appends wrapped stat flags and output format, then runs external binary with stdout/stderr inherited.
- Dependencies/integration: uses package-global `path`, `bflag`, Viper output config, and `os/exec`.
- Risks/tests: package-level mutable `path` may retain state across tests or reused command instances. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stats.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stats.go

- Purpose: implements `index stats <stat>` for Hive Index aggregate statistics.
- Important APIs: package-level `stat`, `newGenericStatsCmd`, `newStatsCmd`, and `runPythonExecStats`.
- Control flow/state: requires at least one stat argument, defaults path to cwd when needed, wraps stats flags, appends output format, and execs `bee stats`.
- Dependencies/integration: uses `bflag`, Viper output config, external Hive Index stats command, and logger.
- Risks/tests: package-level `stat`/`path` state is shared across command instances; `MarkHidden` errors only panic at command construction. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/license/license.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/license/license.go

- Purpose: implements `license`, including reload, display, license acquisition help, and URL generation.
- Important APIs: `license_Config`, `NewCmd`, `runLicenseCmd`, `printGenerateLicenseHelp`, `generateLicenseURL`, and `assembleGetArgs`.
- Control flow/state: gets/reloads license, preserves reload errors while still printing certificate data when possible, formats JSON or ASCII/table-like human output, checks expiration/violations, queries nodes for license URL parameters, and prints install guidance for missing/invalid licenses.
- Dependencies/integration: uses license and node backends, management/license protobufs, Viper/logging, URL encoding, unit formatting, and CTL error helpers.
- Risks/tests: complex error choreography around reload can confuse callers; output mixes compliance state and retrieval instructions. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/license/license.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/delete.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/delete.go

- Purpose: implements `node delete <node>` with dry-run default.
- Important APIs: `deleteNode_Config`, `newDeleteCmd`, and `runDeleteCmd`.
- Control flow/state: parses client/meta/storage node ID, calls `backend.Delete` with `Execute`, and prints dry-run or actual deletion result with metadata-specific warnings.
- Dependencies/integration: uses management protobuf `DeleteNodeRequest`, BeeGFS entity conversion, backend node delete, and `cmdfmt`.
- Risks/tests: destructive cluster membership mutation; local checks cannot prove node emptiness. Missing response identity is fatal in dry run but only warning after execute. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/list.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/list.go

- Purpose: implements `node list` with optional NIC and reachability information.
- Important APIs: `newListCmd` and `runListCmd`.
- Control flow/state: obtains management client for display port, fetches nodes, sorts by type then numeric ID, builds NIC and reachable strings, prints selected columns, and optionally returns exit code 5 when any node is unreachable.
- Dependencies/integration: uses backend `GetNodes`, Viper debug mode, `cmdfmt`, global management config, network address parsing, and CTL error codes.
- Risks/tests: management NIC port display assumes gRPC listens on the same interfaces as BeeMsg; `hasUnreachableNode` marks nodes with no reachable NIC. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/node.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/node.go

- Purpose: defines the `node` command namespace.
- Important APIs: exported `NewCmd`.
- Control flow/state: creates a no-arg Cobra command and registers `list`, `set-alias`, `delete`, and `ping`.
- Dependencies/integration: imported by root command; actual behavior is implemented in sibling files and `ctl/pkg/ctl/node`.
- Risks/tests: command-tree integration only. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/ping.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/ping.go

- Purpose: implements `node ping` through a mounted BeeGFS client module.
- Important APIs: `newPingCmd` and `runPingCmd`.
- Control flow/state: validates count, interprets args as a node type or explicit entity IDs, calls `node.PingNodes`, consumes result/error channels, prints per-ping timing plus average/median/min/max, and returns partial success when some nodes fail.
- Dependencies/integration: uses backend `PingConfig`, BeeGFS entity parsers, global worker count for parallel mode, logging, and CTL partial-success errors.
- Risks/tests: median indexing uses `cfg.Count` rather than actual successful sample count, which may panic or misreport if some pings fail within a result. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/ping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/setalias.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/setalias.go

- Purpose: implements `node set-alias node alias`.
- Important APIs: `newSetAliasCmd` and `runSetAliasCmd`.
- Control flow/state: parses management/client/meta/storage entity ID with 32-bit parser, validates alias, calls `backend.SetAlias`, and prints confirmation.
- Dependencies/integration: uses common BeeGFS parsers and node backend alias update.
- Risks/tests: no preflight confirmation or duplicate detection in the frontend; backend owns persistence and validation. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/setalias.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/assign.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/assign.go

- Purpose: implements `pool assign <pool>` for moving storage targets and buddy groups into a pool.
- Important APIs: `assignPool_Config`, `newAssignPoolCmd`, and `runAssignPoolCmd`.
- Control flow/state: requires at least targets or groups, parses each as storage entity IDs, converts to protobuf lists, calls `backend.Assign`, and prints assigned pool identity.
- Dependencies/integration: uses management protobuf `AssignPoolRequest`, BeeGFS entity conversion, and pool backend.
- Risks/tests: frontend does not check target/group current assignments or pool capacity; state mutation is persisted by management backend. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/assign.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/create.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/create.go

- Purpose: implements `pool create <alias>` for storage pool creation and optional initial assignment.
- Important APIs: `createPool_Config`, `newCreatePoolCmd`, and `runCreatePoolCmd`.
- Control flow/state: parses alias, optional numeric ID, target/group slices, creates `pm.CreatePoolRequest` with storage node type, and warns when the pool starts empty.
- Dependencies/integration: uses BeeGFS alias/entity parsers, protobuf conversions, pool backend create, and `cmdfmt`.
- Risks/tests: empty pools are allowed but can break file creation for directories assigned to them until later assignment; backend handles ID uniqueness. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/delete.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/delete.go

- Purpose: implements `pool delete <pool>` with dry-run default.
- Important APIs: `deletePool_Config`, `newDeletePoolCmd`, and `runDeletePoolCmd`.
- Control flow/state: parses storage pool ID, calls `backend.Delete` with `Execute`, prints dry-run confirmation or deletion result, and warns about directory stripe patterns that still reference the pool ID.
- Dependencies/integration: uses `pm.DeletePoolRequest`, BeeGFS entity conversion, pool backend, and `cmdfmt`.
- Risks/tests: deleting referenced pools can make file creation fail; local command cannot scan references. Missing response identity is fatal only in dry run. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/list.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/list.go

- Purpose: implements `pool list` and exported `RunListCmd` used by quota defaults listing.
- Important APIs: `newListCmd` and `RunListCmd`.
- Control flow/state: rejects page size 0, fetches pools, conditionally includes default quota limit columns, formats limits raw or human-readable, formats targets/mirrors differently in debug mode, and prints a table.
- Dependencies/integration: uses pool backend `GetStoragePools`, Viper raw/debug/page-size config, `cmdfmt`, and quota formatting utilities.
- Risks/tests: multi-line cells require paging constraints; target/group string assembly has separate debug and non-debug paths. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/pool.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/pool.go

- Purpose: defines the `pool` command namespace.
- Important APIs: exported `NewCmd`.
- Control flow/state: creates a no-arg Cobra command and registers list, set-alias, create, assign, and delete.
- Dependencies/integration: imported by root command and quota command for list-defaults behavior.
- Risks/tests: command-tree integration only. No direct tests observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/setalias.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/setalias.go

- Purpose: implements `pool set-alias <storage-pool> <alias>`.
- Important APIs: `newSetAliasCmd` and `runSetAliasCmd`.
- Control flow/state: parses storage pool entity ID, validates alias, calls `backend.SetAlias`, and prints confirmation.
- Dependencies/integration: uses BeeGFS parsers and pool backend alias persistence.
- Risks/tests: no local duplicate/existence checks; backend owns validation. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/setalias.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/quota/quota.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/quota/quota.go

- Purpose: implements quota management for pool defaults, explicit limits, and usage reporting.
- Important APIs: `NewCmd`, `newListCmd`, `newSetDefaultCmd`, `newSetLimitsCmd`, `runSetLimitsCmd`, `newListLimitsCmd`, `runListLimitsCmd`, `newListUsageCmd`, `runListUsageCmd`, `parseLimit`, `parseUserIdsInto`, `parseGroupIdsInto`, `getCurrentGroupIds`, and `idToName`.
- Control flow/state: builds quota protobuf requests, expands user/group ID ranges into individual `QuotaInfo` entries for set-limits, streams limits/usage responses, formats raw or human-readable values, and restricts arbitrary ID queries to root.
- Dependencies/integration: uses pool listing for defaults, quota backend streams, management protobuf builders, OS user/group lookup, and CTL formatting utilities.
- Risks/tests: large ID ranges can generate huge request slices; `unlimited` maps to `MaxInt64` while usage displays `-1` as unlimited. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/quota/quota.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/root.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/root.go

- Purpose: root command assembly and global lifecycle for the BeeGFS CTL binary.
- Important APIs: `Execute`, `wrapAllCommands`, `attachCustomArgsErr`, `attachPersistentPreRunE`, `attachPersistentPostRunE`, `globalPersistentPreRunE`, `globalPersistentPostRunE`, `isCommandAuthorized`, help template utilities, and `pprofStarted`.
- Control flow/state: initializes global flags/config, registers all top-level commands, wraps argument and run hooks, installs custom help wrapping, creates an interrupt-cancelled context, executes Cobra, maps errors to exit codes, starts optional pprof once, enforces worker count and authorization, and runs quick health alerts after successful commands.
- Dependencies/integration: central integration point for every command package, Viper config, signal handling, logger, health quick checks, and OS effective UID.
- Risks/tests: global post-run health checks add remote calls to most successful commands; hook wrapping must avoid duplicate root execution. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/root.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/job.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/job.go

- Purpose: implements Remote Storage Target job management: cancel, cleanup, cleanup orphaned via registered subcommand, and list.
- Important APIs: `newJobCmd`, `newCancelCmd`, `newCleanupCmd`, `updateJobRunner`, `listJobsConfig`, `newListJobsCmd`, and `runListJobsCmd`.
- Control flow/state: cancel/cleanup build `rst.UpdateJobCfg` with target state, gate recursive updates with `--yes`, stream update responses into job tables, return partial success when any update is not OK, and list jobs grouped by path/RST with table or retro verbose output.
- Dependencies/integration: uses filesystem path initialization, RST backend update/list streams, beeremote protobuf job/work states, job table helpers, Viper debug mode, and CTL partial-success errors.
- Risks/tests: recursive operations are database-prefix based, not live filesystem traversal; force cancellation deliberately ignores some backend errors to drive cleanup. No direct tests found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/job.go -->
