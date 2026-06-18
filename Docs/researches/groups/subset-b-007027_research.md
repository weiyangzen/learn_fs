# Research: subset-b-007027

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.cc -->
# sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.cc

## Purpose
Implements `eos::mgm::QuarkConfigHandler`, the low-level QuarkDB access layer for MGM configuration hashes, configuration backups, and the configuration changelog. It translates qclient replies into `common::Status`, builds batched writes with `qclient::MultiBuilder`, and exposes synchronous read/list/tail/trim operations plus asynchronous write/changelog append operations.

## Important APIs and Functions
- `QuarkConfigHandler::QuarkConfigHandler` constructs a `qclient::QClient` from `QdbContactDetails` and creates a two-thread Folly IO executor for async continuations.
- `checkConnection` delegates to `QClient::checkConnection`.
- `checkExistence` checks `HLEN eos-config:<name>` and treats a nonzero hash length as existence.
- `listConfigurations` scans `eos-config:*` and `eos-config-backup:*` with `qclient::QScanner` and strips the storage prefixes before returning names.
- `fetchConfiguration` reads `HGETALL eos-config:<name>` and falls back to `HGETALL eos-config-backup:<name>` when the primary hash is missing or empty.
- `writeConfiguration` optionally refuses overwrite, optionally clones the old hash to a backup hash, deletes the target hash, and writes every key/value via a single qclient multi request.
- `appendChangelog` serializes `ConfigChangelogEntry` protobufs into `eos-config-changelog:default` and trims the deque to 500000 entries.
- `tailChangelog` scans the changelog deque backwards and returns serialized entries as strings.
- `trimBackups` deletes at most 200 backup hashes matching `<name>-*`.
- `FormHashKey` and `FormBackupHashKey` centralize QuarkDB key naming.

## Control Flow
Read operations are direct qclient calls followed by qclient parser validation. Write operations first validate overwrite policy with `HLEN` when needed, build an ordered multi-request, submit it through `follyExecute`, and attach a continuation that validates response cardinality and per-HSET integer results. Backup writes prepend `DEL backup` and `HCLONE current backup` before deleting and rewriting the live hash.

## State and Persistence
Persistent state lives in QuarkDB:
- live config hash: `eos-config:<name>`
- backup hash: `eos-config-backup:<name>` or timestamped `eos-config-backup:<name>-YYYYMMDDHHMMSS`
- changelog deque: `eos-config-changelog:default`

The class itself keeps only connection details, a QClient, and an executor. Backup trimming depends on scan order; there is no explicit sort by timestamp before deleting.

## Dependencies and Integration Points
Depends on qclient parsers/scanners/multi execution, Folly futures/executors, EOS `common::Status`, string helpers, logging, `QdbContactDetails`, and `ConfigChangelogEntry` protobufs. It is used by `QuarkDBConfigEngine` and the standalone `eos-config-inspect` utility.

## Risks
- `processWriteConfigurationReply` validates only HSET responses, not the `DEL`/`HCLONE` extra request results.
- `trimBackups` deletes the first scan results after prefix filtering; if scanner order is not chronological, it may remove unexpected backups.
- `fetchConfiguration` falls back to backup when the live hash is empty, so intentionally empty configs are indistinguishable from missing configs.
- `tailChangelog` scans key `eos-config-changelog`, while `appendChangelog` writes `eos-config-changelog:default`; this key mismatch is a compatibility or bug signal worth testing against the deployed deque API.
- Async writes require callers to observe the returned future; otherwise persistence errors surface only through downstream continuations or logs.

## Test Signals
Useful tests include mocked qclient replies for malformed HLEN/HGETALL/multi responses, write-with-backup request ordering, overwrite refusal, changelog key consistency, backup trim ordering, and fallback behavior for missing live configs. Integration tests need a QuarkDB instance with qclient deque/hash support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.hh -->
# sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.hh

## Purpose
Declares the MGM QuarkDB configuration storage facade. The header defines the public contract for checking QuarkDB connectivity, reading and writing named configurations, listing live and backup configs, maintaining the changelog, trimming backups, and forming canonical QuarkDB keys.

## Important APIs and Types
- `class QuarkConfigHandler : public eos::common::LogId` provides the API boundary.
- Constructor accepts `QdbContactDetails`, making the handler independent of global connection configuration.
- `common::Status` is the error carrier for synchronous operations.
- `folly::Future<common::Status>` is returned by `writeConfiguration` and `appendChangelog`, explicitly making those persistence operations asynchronous.
- Static key helpers expose the exact hash-key scheme to callers/tests.

## Control Flow and State
The header exposes no inline control flow except key helper declarations and basic method signatures. Private state is `mContactDetails`, `mQcl`, and `mExecutor`, meaning each handler owns its QClient connection and async continuation executor.

## Dependencies and Integration Points
Includes EOS namespace setup, status/logging, QuarkDB contact details, changelog protobuf, standard maps, and Folly futures. It forward declares `folly::Executor` and `qclient::QClient`, minimizing header coupling. Callers include `QuarkDBConfigEngine` and `eos-config-inspect`.

## Risks
- The API exposes asynchronous writes but has no destructor-level draining or cancellation contract in the header.
- Key helpers accept arbitrary names and do not validate characters or prefix collisions.
- `trimBackups` semantics are documented as repeated deletion batches but not as sorted or newest-preserving in the type contract.

## Test Signals
Header-level tests should focus on compile-time integration with callers, async future handling expectations, and static key helper outputs for live, backup, and timestamped backup keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.cc -->
# sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.cc

## Purpose
Implements the QuarkDB-backed `IConfigEngine` used by MGM to load, save, mutate, autosave, list, and display configuration from QuarkDB. It also implements a text changelog adapter and a background backup cleanup thread.

## Important APIs and Functions
- `QuarkDBCfgEngineChangelog::AddEntry` writes textual entries into `eos-config-changelog` and trims the deque.
- `QuarkDBCfgEngineChangelog::Tail` reads recent entries and formats epoch timestamps into local time strings.
- `QuarkDBConfigEngine::LoadConfig` resets local config, pulls a named config from QuarkDB, optionally cleans unused/deprecated entries, applies config, and records the loaded config name.
- `RemoveUnusedNodes` removes global config entries for off nodes without registered filesystems when `EOS_MGM_CONFIG_CLEANUP=1`.
- `SaveConfig` resolves the target name, checks existence if not overwriting, stores into QuarkDB, adds a changelog entry, and updates `mConfigFile`.
- `ListConfigs` delegates to `QuarkConfigHandler`.
- `CleanupThread` trims default config backups to 1000 every 30 minutes.
- `PullFromQuarkDB` replaces `sConfigDefinitions` from QuarkDB under `mMutex` and removes the `timestamp` key.
- `FilterConfig` dumps a named config to a stream.
- `AutoSave` saves only when this MGM is master, autosave is enabled, and a config name is loaded.
- `SetConfigValue` and `DeleteConfigValue` mutate `sConfigDefinitions`, publish changes to peer MGMs for local changes, update changelog, and save.
- `StoreIntoQuarkDB` filters deprecated entries and invokes async `writeConfiguration` with a timestamp backup.

## Control Flow
Loading follows `ResetConfig -> PullFromQuarkDB -> optional cleanup/save -> ApplyConfig`. Saving follows name resolution and optional existence check, then queues an async QuarkDB write and immediately records changelog/local state. Runtime config mutations update the in-memory `sConfigDefinitions` first, then publish/broadcast and persist if the change originated locally.

## State and Persistence
The engine bridges global in-memory `sConfigDefinitions` and QuarkDB hashes. It stores the current config name in `mConfigFile`, owns both a direct QClient for text changelog access and a `QuarkConfigHandler` for structured config operations, and starts an `AssistedThread` for backup cleanup. `StoreIntoQuarkDB` saves timestamped backups using local time format `YYYYMMDDHHMMSS`.

## Dependencies and Integration Points
Integrates with `IConfigEngine`, `XrdMgmOfs` globals, `FsView`, qclient, Folly, `QuarkConfigHandler`, `AssistedThread`, and the shared config map inherited from the base config engine. It uses `PublishConfigChange`/`PublishConfigDeletion` from the base class to fan out live updates.

## Risks
- `SaveConfig` reports success before the async QuarkDB write has completed; failures are logged in `checkWriteConfigurationResult` and may not propagate to the caller.
- `StoreIntoQuarkDB` holds `mMutex` while queuing async work and passes `sConfigDefinitions` by const reference to `writeConfiguration`; the handler currently copies into a multi request synchronously, but this relies on that implementation detail.
- `RemoveUnusedNodes` erases entries while iterating and checks node names by substring, which can remove unexpected entries if node names overlap.
- Cleanup behavior depends on environment variable `EOS_MGM_CONFIG_CLEANUP`; without it, stale node entries are only logged.
- Changelog format differs from protobuf changelog in `QuarkConfigHandler`, and the key naming differs from handler append behavior.

## Test Signals
Tests should exercise load/save with mocked `QuarkConfigHandler`, async write failure visibility, unused-node cleanup with overlapping node names, changelog tail parsing of malformed timestamps, autosave master gating, and config mutation broadcast/save behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.hh -->
# sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.hh

## Purpose
Declares the QuarkDB implementation of the MGM `IConfigEngine` interface and its text changelog adapter. It is the primary header tying QuarkDB storage to the generic MGM configuration engine contract.

## Important APIs and Types
- `QuarkDBCfgEngineChangelog : ICfgEngineChangelog` exposes `AddEntry` and `Tail`.
- `QuarkDBConfigEngine : IConfigEngine` overrides `LoadConfig`, `SaveConfig`, `ListConfigs`, `AutoSave`, `SetConfigValue`, `DeleteConfigValue`, and private `FilterConfig`.
- `FormatBackupTime` is an inline timestamp formatter used for backup names.
- Private helper methods cover QuarkDB store/pull, cleanup thread, unused/deprecated key removal, and config filtering.
- Private members own QDB contact details, QClient, `QuarkConfigHandler`, Folly executor, and cleanup assisted thread.

## Control Flow and State
The header makes `QuarkDBConfigEngine` a stateful engine with persistent connection objects and a background cleanup thread. The default constructor is exposed only under `IN_TEST_HARNESS`, indicating tests can instantiate without QDB wiring for isolated helper coverage.

## Dependencies and Integration Points
Depends on `IConfigEngine`, `QuarkConfigHandler`, qclient `QHash`/`AsyncHandler`/`QClient`, QuarkDB contact details, and EOS assisted threading/status primitives. It inherits base config state such as `sConfigDefinitions` through `IConfigEngine`.

## Risks
- `DeleteConfigValue` comment documents `save_config`, but the signature lacks that parameter, indicating stale API documentation.
- Inline `FormatBackupTime` uses `localtime`, which is not thread-safe and is also used by the implementation in concurrent contexts.
- Header includes several heavy qclient headers, increasing compile coupling.

## Test Signals
Compile tests should cover interface conformance. Unit tests can use `IN_TEST_HARNESS` to validate `FormatBackupTime`, `RemoveUnusedNodes`, config serialization/filtering, and private helper behavior without requiring a full engine bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/eos-config-inspect.cc -->
# sources/distributed-fs/eos/mgm/config/eos-config-inspect.cc

## Purpose
Implements a standalone CLI utility for inspecting and modifying QuarkDB-backed EOS MGM configuration. It supports exporting a legacy file config into QDB, dumping/listing configs, tailing the changelog, relocating a filesystem entry, and trimming backup configs.

## Important APIs and Functions
- `MemberValidator` validates `--members` using qclient member parsing.
- `addClusterOptions` adds required `--members` plus optional `--password` or `--password-file` to each subcommand.
- `readConfigurationFile` reads non-empty lines from a source file.
- `readAndParseConfiguration` parses legacy config text with `ConfigParsing::parseConfigurationFile`.
- `runDumpSubcommand`, `runExportSubcommand`, `runListSubcommand`, `runTailSubcommand`, and `runTrimBackupsSubcommand` directly wrap `QuarkConfigHandler`.
- `runRelocateFilesystemSubcommand` fetches the default config, finds an `fs:` entry by id, rewrites host/port with `ConfigParsing::relocateFilesystem`, and writes the updated config with a relocation backup.
- `main` defines subcommands with CLI11, reads password files, checks QDB connectivity, and dispatches to the selected subcommand.

## Control Flow
The CLI requires exactly one subcommand. Every subcommand collects cluster credentials, then after parsing `main` constructs `QdbContactDetails`, creates `QuarkConfigHandler`, checks the connection with a three-second timeout, and dispatches. Mutation commands parse and validate configuration before calling `writeConfiguration(...).get()`.

## State and Persistence
The process has no long-lived state. It reads local config files and persists changes into QuarkDB live/backup config hashes through `QuarkConfigHandler`. Relocation writes a backup name shaped like `default-YYYYMMDDHHMMSS-relocation`, which is passed to `writeConfiguration` and combined with the handler backup key scheme.

## Dependencies and Integration Points
Uses CLI11, qclient member parsing, EOS password handling, common string/config parsing helpers, `QuarkConfigHandler`, and `QdbContactDetails`. It is an operational/admin integration point rather than part of the MGM daemon runtime.

## Risks
- The `export` and `relocate-filesystem` subcommands are dangerous and rely on the operator ensuring MGM is not concurrently modifying config.
- `readConfigurationFile` drops empty lines, which may affect parsing if empty lines ever carry semantic separation.
- Relocation erases the current map iterator while iterating and returns immediately; that is safe for the found entry but would need care if extended to multiple matches.
- Backup name composition can produce names with duplicated `default-` context when combined with handler backup key construction.
- Password can be supplied on the command line, exposing it to process listings.

## Test Signals
Tests should cover CLI parsing, member validation, password file failure, export overwrite refusal, relocation of a sample fs entry, no-match relocation failure, list/dump formatting, and trim-backups exit code behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/eos-config-inspect.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionInfo.cc -->
# sources/distributed-fs/eos/mgm/convert/ConversionInfo.cc

## Purpose
Implements the compact conversion descriptor used by the MGM converter. A conversion string encodes file id, target space/group, target layout id, optional placement policy, optional app tag, and optional ctime-update marker, and maps that descriptor to a proc conversion path.

## Important APIs and Functions
- `ConversionInfo::ConversionInfo` builds the canonical conversion string from typed fields.
- `ConversionInfo::parseConversionString` parses the string form back into a `ConversionInfo` object.
- `ConversionInfo::ConversionPath` shards conversion files under `gOFS->MgmProcConversionPath/<fid % 256>/<conversion-string>`.

## Control Flow
Parsing first strips trailing `+` for ctime update, validates a 16-hex-character fid before `:`, parses `<space.group>` before `#`, extracts optional `^app_tag^`, parses the layout hex up to optional `~`, parses optional placement policy, and rejects zero/invalid fid or layout. Successful parsing constructs a new canonical object, normalizing the string.

## State and Persistence
The object is immutable except for private `mConversionString`. The conversion path points into MGM proc namespace state; the file created at that path is later used by `ConversionJob` as the temporary converted file.

## Dependencies and Integration Points
Depends on `FileId`, `LayoutId`, `GroupLocator`, EOS logging, and global `gOFS` for proc path construction. It is consumed by `ConverterEngine`, `ConversionJob`, and `ConversionTag`.

## Risks
- The constant and path use `CONVERTION_SHARD_MOD`, preserving a misspelling but making naming brittle.
- The header comment mentions `[!]` while implementation uses `+` for ctime update.
- `std::stoull`/`std::stoll` parse failures are swallowed, and invalid values collapse to zero; zero is rejected, so fid 0/layout 0 cannot be represented.
- Optional app tags are delimited by `^`; tags containing `^` cannot round-trip safely.

## Test Signals
Tests should cover valid round trips with/without group, policy, app tag, and ctime; malformed fid/layout/space/app delimiters; shard path formatting; and normalization of parsed strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionInfo.hh -->
# sources/distributed-fs/eos/mgm/convert/ConversionInfo.hh

## Purpose
Declares the conversion descriptor type and its public immutable fields. It is the shared contract for converter scheduling, job execution, CLI/tag helpers, and proc path construction.

## Important APIs and Types
- `constexpr int CONVERTION_SHARD_MOD = 256` defines conversion proc sharding.
- `struct ConversionInfo` exposes `UPDATE_CTIME`, constructor, `ToString`, `ConversionPath`, and static `parseConversionString`.
- Public const fields hold fid, target layout, target `GroupLocator`, placement policy, update-ctime flag, and app tag.

## Control Flow and State
The only inline logic is `ToString`, returning the private canonical conversion string. All semantic parsing/formatting is implemented in the `.cc`. Instances are effectively immutable after construction.

## Dependencies and Integration Points
Includes MGM namespace, `FileId`, `LayoutId`, and `FileSystem` for `GroupLocator`. `ConversionJob` takes a `ConversionInfo` by value and trusts its parsed fields.

## Risks
- Public const data fields make the type simple but lock in representation and force construction of whole new objects for any change.
- The documented format includes `[!]`, while implementation uses `+`; this can mislead callers.
- There is no escaping scheme for app tags or placement policies.

## Test Signals
Header-facing tests should verify construction from typed values, `ToString` consistency, public field values, and compile compatibility with converter and tag helper callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionJob.cc -->
# sources/distributed-fs/eos/mgm/convert/ConversionJob.cc

## Purpose
Implements execution of a file layout/location conversion. A job creates a temporary converted file via XRootD third-party copy, verifies the result and original checksum, then merges new physical locations back onto the original fid while preserving namespace identity.

## Important APIs and Functions
- `NewUrl` creates a root URL pointing at the MGM alias and manager port.
- `TpcProperties` configures XrdCl copy properties and timeout based on file size.
- `getDiskFsIdOfFile` selects a non-tape filesystem for tape GC notification.
- `ConversionJob::DoIt` orchestrates metadata lookup, destination CGI construction, TPC execution, result verification, merge, stats, tape GC notification, and callback cancellation.
- `HandleError` records status, increments failure stats, logs, stores timestamped error text, and cancels callback.
- `ConversionCGI` maps target layout/location/policy into EOS open parameters.
- `Merge` adds converted locations to the original file, asks FSTs to locally rename physical files from conversion fid to original fid, unlinks old non-tape locations, updates layout/ctime, updates quota, and resyncs new locations.

## Control Flow
`DoIt` rejects pre-cancelled jobs, marks running, reads original metadata under namespace lock, builds source and conversion destination URLs, excludes original/unlinked fsids from destination placement, runs XrdCl TPC, validates converted stripe count, re-reads the original checksum, aborts if it changed, and calls `Merge`. `Merge` first records converted locations on the original namespace object, then performs FST `local_rename` queries for each new location. On rename failure it removes newly added locations and restores quota accounting. On success it removes old non-tape locations, updates layout and optional ctime, then triggers resync for new locations.

## State and Persistence
The job mutates namespace metadata, physical FST file names, quota accounting, MGM stats, FST resync state, and optionally tape GC state. It uses the proc conversion path from `ConversionInfo` as the temporary destination. Status is held in an atomic enum and final errors in `mErrorString`.

## Dependencies and Integration Points
Heavily depends on `gOFS`, namespace locks and services, `FsView`, XrdCl copy/query APIs, EOS layout/checksum utilities, quota, tape GC, metadata prefetching, and connection pool helpers. `ConverterEngine` owns lifecycle and cleanup of the conversion proc file after the job finishes.

## Risks
- Merge spans namespace updates and remote FST renames without a single transaction; partial failure recovery removes metadata locations but cannot necessarily undo physical renames already completed.
- The original checksum comparison only detects checksum changes, not all metadata changes that could matter during conversion.
- `XrdOucErrInfo error` and `rootvid` in `DoIt` are unused after declaration.
- Callback success and failure both call `Cancel`, so callback semantics are not self-describing.
- Local rename timeout is fixed at 10 seconds, which may be fragile for slow FSTs.
- Quota removal happens before metadata retrieval in `Merge`; restoration paths exist for some failures but not every later failure.

## Test Signals
Test with fake namespace/FST services for TPC success, prepare failure, checksum drift, stripe mismatch, local rename failure after partial success, ctime update, quota restoration, tape file notification, and callback behavior. Integration tests require multi-FST EOS/XRootD setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionJob.hh -->
# sources/distributed-fs/eos/mgm/convert/ConversionJob.hh

## Purpose
Declares the conversion job execution object and its XrdCl progress/cancellation handler. It is the public surface used by `ConverterEngine` to run and monitor individual conversion tasks.

## Important APIs and Types
- `enum class ConversionJobStatus { DONE, RUNNING, PENDING, FAILED }`.
- `ConversionProgressHandler` implements `XrdCl::CopyProgressHandler` with atomic cancel/progress/bytes/start-time fields.
- `ConversionJob` exposes constructor, destructor, `DoIt`, `Cancel`, status/error/conversion/fid getters.
- Private helpers `Merge`, `HandleError`, and `ConversionCGI` encapsulate terminal handling, metadata merge, and destination parameter construction.

## Control Flow and State
The header shows lifecycle state: jobs start `PENDING`, can be cancelled through the progress handler, and transition to `RUNNING`, `DONE`, or `FAILED` in the implementation. `mFid` is expected to match `mConversionInfo.mFid`, enforced by an assert in `GetFid`.

## Dependencies and Integration Points
Includes global MGM OFS, conversion info, common file/layout/filesystem types, namespace file metadata, XrdCl copy, and `XrdOucCallBack`. The global `EOS_APP_NAME` defaults conversion app tagging.

## Risks
- `static std::string EOS_APP_NAME` in a header gives each translation unit its own mutable copy; this is not ideal for shared constants.
- `ConversionProgressHandler::JobProgress` divides by `bytesTotal` without guarding zero.
- The callback type is generic and the public contract does not clarify why terminal notification uses `Cancel`.

## Test Signals
Tests should cover progress handler cancellation/progress calculations, status transitions, fid mismatch assertions in debug builds, and compile-time compatibility with engine scheduling code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionTag.hh -->
# sources/distributed-fs/eos/mgm/convert/ConversionTag.hh

## Purpose
Provides a small static helper for producing conversion tag strings from fid, space, layout id/string, placement policy, and ctime-update choice.

## Important APIs and Types
- `ConversionTag::Get(fid, space, unsigned int layoutid, plctplcy, ctime_update)` formats the layout id as eight hex digits and delegates.
- `ConversionTag::Get(fid, space, std::string conversion, plctplcy, ctime_update)` builds `<fid16hex>:<space>#<layout><~policy><+>`.

## Control Flow and State
The helper is stateless. It prepends `~` to non-empty placement policy and appends `ConversionInfo::UPDATE_CTIME` when requested.

## Dependencies and Integration Points
Includes `XrdMgmOfs` and `ConversionInfo`, though it only needs the update marker from `ConversionInfo`. Its output is intended to be parsed by `ConversionInfo::parseConversionString`.

## Risks
- This helper does not include the scheduling group index style emitted by `ConversionInfo` constructor (`space.index`), only the caller-provided `space` string.
- No app tag support, so newer conversion strings with `^app_tag^` cannot be produced through this class.
- Fixed buffers rely on `snprintf`; overly long inputs are truncated silently.
- Header includes `XrdMgmOfs` unnecessarily, increasing compile coupling.

## Test Signals
Tests should verify layout formatting, policy separator insertion, ctime marker behavior, parser round-trip with `ConversionInfo`, and long-input truncation behavior if considered acceptable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConversionTag.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConverterEngine.cc -->
# sources/distributed-fs/eos/mgm/convert/ConverterEngine.cc

## Purpose
Implements the central converter thread that accepts conversion requests, durably records pending jobs in QuarkDB, dispatches `ConversionJob` tasks to a thread pool, handles cleanup, and persists converter configuration in the global config map.

## Important APIs and Functions
- `Start` and `Stop` manage the assisted converter thread.
- `PopulatePendingJobs` reloads QuarkDB pending jobs into the in-memory queue, using `mFidTracker` to avoid duplicate scheduling.
- `HandlePostJobRun` removes a job from running state, deletes its QuarkDB pending entry, records failures, removes the conversion proc file, notifies observers, and clears the fid tracker.
- `Convert` waits for namespace boot and mastership, reloads pending jobs, drains the in-memory queue into thread-pool tasks, and joins jobs on termination.
- `JoinAllConversionJobs` cancels running jobs and waits until they leave running/pending states.
- `ScheduleJob` validates running state, queue size, conversion string, and duplicate fid tracking, then queues in memory and writes to QuarkDB.
- `ApplyConfig`, `SetConfig`, `SerializeConfig`, and `StoreConfig` manage global converter settings.
- `QdbHelper` wraps the `eos-conversion-jobs-pending` hash with add/list/clear/remove operations.

## Control Flow
Scheduling pushes a job to the in-memory queue and then persists it to QDB. The converter thread waits for items, waits for thread-pool capacity, parses the conversion string, creates a `ConversionJob`, pushes a task that runs the job and post-run cleanup, then records it in `mJobsRunning`. On invalid persisted conversion strings, it removes the pending hash entry and tracker entry.

## State and Persistence
Durable pending jobs are stored in QuarkDB hash `eos-conversion-jobs-pending`, keyed by decimal fid and valued by conversion string. Runtime-only state includes `mPendingJobs`, `mJobsRunning`, callbacks, failure count, observer manager, thread pool, max queue size, and fid tracker entries. Converter config is persisted through `FsView::gFsView.SetGlobalConfig("converter", ...)`.

## Dependencies and Integration Points
Depends on `ConversionInfo`, `ConversionJob`, QuarkDB qclient/QHash, `FsView`, MGM master state, global fid tracker, common thread pool, observer manager, and `XrdOucCallBack`.

## Risks
- `ScheduleJob` pushes to memory before `AddPendingJob`; if QDB persistence fails, the job may run but will not survive restart.
- `QdbHelper::AddPendingJob` writes `std::cerr << "hset: ..."` from daemon code, likely unintended noisy output.
- Recovered pending jobs use `nullptr` callbacks, so restart loses callback notification.
- `Stop` joins the assisted thread before setting `mIsRunning=false`; behavior depends on `AssistedThread::join` signalling termination.
- `Convert` records the running job after pushing the task, so a very fast job can call `HandlePostJobRun` before it is inserted into `mJobsRunning`.
- `NumPendingJobs` reports in-memory queue size, not durable QDB pending count.

## Test Signals
Tests should cover scheduling persistence failure, restart reload, duplicate fid tracking, invalid conversion removal, thread-pool queue throttling, config parsing bounds, observer notifications, and the race between task execution and `mJobsRunning` insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConverterEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConverterEngine.hh -->
# sources/distributed-fs/eos/mgm/convert/ConverterEngine.hh

## Purpose
Declares the converter service API, internal QuarkDB helper, runtime queues, observer integration, and configuration surface for MGM file conversions.

## Important APIs and Types
- `JobInfoT` stores fid, conversion string, and optional callback.
- `JobStatusT` aliases `ConversionJobStatus`; `ObserverT` publishes status changes keyed by conversion string.
- Public API: `Start`, `Stop`, `ScheduleJob`, running/thread-pool/pending/failed counters, pending clear/list, observer access, config apply/set/serialize.
- `QdbHelper` owns QClient and `QHash` for the pending-job hash and exposes iterator/list/add/remove/clear helpers.
- Private thread helpers: `Convert`, `JoinAllConversionJobs`, `PopulatePendingJobs`, `HandlePostJobRun`, and `StoreConfig`.

## Control Flow and State
The constructor wires QDB helper, thread pool defaults, max queue size, and observer manager. The class keeps atomic running/failure/config counters, a concurrent pending queue, a protected running-job map, and an assisted thread.

## Dependencies and Integration Points
Depends on EOS logging, observer manager, global OFS, conversion job, namespace metadata, QuarkDB qclient/QHash, thread pool, and callbacks. Exposes `GetThreadPoolInfo` for operational inspection.

## Risks
- `NumPendingJobs` lacks `const` and exposes the in-memory queue only.
- `GetPendingJobs` returns durable QDB jobs, while `NumPendingJobs` returns memory queue size; callers may confuse the two.
- Constructor uses `std::thread::hardware_concurrency()` directly; if it returns 0, thread pool behavior depends on `ThreadPool` handling.
- The header exposes `QdbHelper::PendingJobsIterator`, coupling tests/callers to qclient iterator details.

## Test Signals
Header-level tests should validate construction with fake `QdbContactDetails`, config serialization defaults, public counter semantics, and QdbHelper hash behavior against a test QuarkDB or mock wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/convert/ConverterEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/devices/Devices.cc -->
# sources/distributed-fs/eos/mgm/devices/Devices.cc

## Purpose
Implements the MGM devices recorder thread. It periodically extracts SMART/device health information from registered filesystems, decompresses JSON payloads, stores current in-memory maps, and persists per-device records into the EOS proc namespace.

## Important APIs and Functions
- `Start` launches `Recorder`; `Stop` joins it.
- `Recorder` waits for namespace boot, only runs extraction/storage on the master MGM, and sleeps for a configured interval.
- `Extract` walks `FsView` spaces/filesystems, collects `stat.health.z64smart` and `stat.health`, decompresses SMART JSON, updates extraction timestamp, and swaps maps under mutex.
- `Store` parses each JSON payload for `serial_number`, creates or opens `<mDevicesPath>/<serial>.<fsid>`, writes `sys.smart.json` and `sys.smart.status`, and updates mtime.

## Control Flow
The recorder waits 15 seconds after namespace boot, logs with backoff, skips work on non-master nodes, then repeats `Extract` and `Store`. `Extract` uses short `FsView` read locks to collect ids and per-filesystem strings, then decompresses outside the lock. `Store` prefetches file metadata, creates missing proc files, sets birth-time on creation, and updates attributes.

## State and Persistence
Runtime state includes shared maps from fsid to JSON, fsid to space, fsid to SMART status, protected by `fsJsonMutex`, plus `lastExtraction`. Persistent state is namespace proc files named by disk serial and fsid with attributes `sys.smart.json`, `sys.smart.status`, and `sys.eos.btime` on creation.

## Dependencies and Integration Points
Uses `FsView`, global `gOFS`, namespace prefetching/view operations, JSON parsing, `SymKey::ZDeBase64`, MGM stats, assisted threading, and EOS metadata locking. `SetDevicesPath` must be called by the owning MGM setup before storage.

## Risks
- Environment override `EOS_MGM_DEVICES_PUBLISHING_INTERVAL` is parsed into `rtime` but never assigned back to `snoozetime`, so the override has no effect.
- Destructor calls `Stop`; if `Start` was never called, behavior depends on `AssistedThread::join`.
- `Store` writes attributes without an explicit namespace-wide lock in this file, relying on file locks and view APIs.
- Invalid or serial-less JSON is silently skipped after debug/error logs.
- Serial numbers become path components without obvious sanitization.

## Test Signals
Tests should cover interval environment handling, extraction with disappearing filesystems, decompression failures, JSON serial parsing, creation/update of proc files, attribute writes, master-only behavior, and Stop without Start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/devices/Devices.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/devices/Devices.hh -->
# sources/distributed-fs/eos/mgm/devices/Devices.hh

## Purpose
Declares the `Devices` service responsible for periodic device health extraction and proc namespace persistence.

## Important APIs and Types
- `Devices`, `Start`, `Stop`, and `SetDevicesPath` form the lifecycle/configuration API.
- `json_map_t`, `space_map_t`, and `smart_map_t` are shared-pointer map aliases keyed by fsid.
- Getters return current maps and extraction time.
- `Extract` is public, allowing on-demand refresh outside the background recorder.
- Private `Recorder`, `Store`, and map setters implement the background path.

## Control Flow and State
The header shows a single `AssistedThread`, device path string, mutex-protected shared maps, and atomic extraction timestamp. Getters return shared pointers under lock; callers receive a snapshot pointer, not a deep copy.

## Dependencies and Integration Points
Depends on MGM namespace, assisted threading, timing, and XRootD string types. Implementation integrates with `FsView` and namespace services.

## Risks
- The comment says "storing regulary" and there are minor typos, but the main concern is lifecycle: destructor always calls `Stop`.
- Returning shared pointers to maps means readers can mutate map contents unless they treat them as read-only; no const alias is used.
- `lastExtraction` is not initialized in the constructor.

## Test Signals
Tests should validate getter/setter thread safety, initial extraction time behavior, public `Extract` without started recorder, and immutability expectations for returned maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/devices/Devices.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainFs.cc -->
# sources/distributed-fs/eos/mgm/drain/DrainFs.cc

## Purpose
Implements draining of one filesystem: prepare the filesystem, schedule per-file `DrainTransferJob`s, monitor progress/stalls/expiry, update local drain status counters, stop jobs on cancellation, and mark final success or failure.

## Important APIs and Functions
- `DrainFs::DoIt` is the main per-filesystem drain loop.
- `GetSpaceConfiguration` reads `drainer.fs.ntx` and `drainer.tx.minrate` from space config.
- `PrepareFs` sets `kDrainPrepare`, waits service delay, reads drain period, then sets `kDraining` and initial counters.
- `UpdateFinishedJob` removes completed jobs from running state and records failures.
- `SuccessfulDrain` sets status `kDrained`, progress 100, and durable `configstatus=empty` unless MGM is shutting down.
- `FailedDrain` sets `kDrainFailed` and failed count.
- `StopJobs` cancels and waits for running transfer jobs.
- `UpdateProgress` updates counters, detects stalls/expiry, handles rerun once when files remain, and decides final state.
- `PrintJobsTable` emits running or failed transfer info.

## Control Flow
`DoIt` waits for namespace boot, exits successfully for empty filesystems, prepares the fs, streams file ids from `IFsView`, and schedules jobs while running jobs are within `mMaxJobs`. Each job is tracked in `mJobsRunning` and submitted to the shared thread pool; job completion calls back into `UpdateFinishedJob`. After each scheduling or wait interval, `UpdateProgress` can keep running, rerun, fail, or mark done. Cancellation or leftover running jobs triggers `StopJobs` and counter reset.

## State and Persistence
Runtime state includes source/target fsids, drain status, cancellation flag, max jobs, drain period, min transfer rate, running/failed job sets, total/pending counters, and progress timestamps. Persistent/durable impact is mostly through `FileSystemUpdateBatch`: local drain counters/status during operation, and durable `configstatus=empty` plus stored FS config on success.

## Dependencies and Integration Points
Uses `DrainTransferJob`, `IFsView`, `FsView`, global `gOFS`, EOS thread pool, file-system update batches, table formatting, namespace boot state, and fid tracker indirectly through jobs.

## Risks
- Scheduling condition uses `NumRunningJobs() <= mMaxJobs`, which permits one more than the configured maximum.
- Some helper declarations in the header (`MarkFsDraining`, `CollectDrainJobs`, `sRefreshTimeout`) are unused in this implementation.
- `GetSpaceConfiguration` requires a `FsView` lock per comment, but the implementation reads `mSpaceView` without taking one itself; callers must uphold that.
- Stalled drains sleep 30 seconds, slowing responsiveness to stop requests.
- Success writes durable `configstatus=empty` only when not shutting down; restart semantics depend on reapply logic elsewhere.

## Test Signals
Tests should cover empty fs success, prepare removal/stop cases, max-job boundary, failed-job rerun logic, drain expiry, stall status transitions, success durable config update, cancellation cleanup, and table rendering for running/failed jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainFs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainFs.hh -->
# sources/distributed-fs/eos/mgm/drain/DrainFs.hh

## Purpose
Declares the per-filesystem drain controller used by the central `Drainer`. It owns the future for one filesystem drain and the transfer jobs running under it.

## Important APIs and Types
- `enum class State { Done, Failed, Running, Rerun }` describes supervisor outcomes.
- Public lifecycle/status methods: constructor, destructor, `SignalStop`, `GetDrainStatus`, `GetFsId`, `DoIt`, `SetFuture`, `IsRunning`.
- `PrintJobsTable` exposes transfer job status for admin/monitoring output.
- `UpdateFinishedJob` is the completion callback used by thread-pool transfer tasks.
- Private helpers cover counter reset, space config, preparation, progress, final status, stop, and namespace boot wait.

## Control Flow and State
The class stores fs view pointer, source/target fsids, drain status, cancellation flag, max parallel jobs, drain period, min transfer rate, drain timestamps, failed/running job collections, a shared thread pool reference, future, and progress counters. `IsRunning` is future-based rather than status-based.

## Dependencies and Integration Points
Depends on EOS file-system metadata/status types, `IFsView`, common logging/RWMutex, `ThreadPool`, `DrainTransferJob`, and table formatting.

## Risks
- `mStatus` and `mDidRerun` are not atomic; access is mostly supervisor-thread local, but status can be read externally.
- `mJobsFailed` is a set of shared pointers with default pointer ordering, not ordered by fid or error.
- Unimplemented private declarations (`MarkFsDraining`, `CollectDrainJobs`) can confuse maintainers.
- `sRefreshTimeout` is declared but not meaningfully used.

## Test Signals
Tests should cover future-based `IsRunning`, `SignalStop`, job completion bookkeeping, counter reset, status reads during execution, and compile warnings for declared-but-unimplemented helpers if build flags catch them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainFs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainTransferJob.cc -->
# sources/distributed-fs/eos/mgm/drain/DrainTransferJob.cc

## Purpose
Implements a single file transfer used by drain, balance, repair, and related workflows. It selects a destination filesystem when needed, builds signed XRootD TPC source/destination URLs, executes the copy, handles ghosts/detached files, and updates metadata for zero-byte replica files.

## Important APIs and Functions
- `ContainerExists` checks whether a file parent container still exists.
- `ReportError` logs and marks the job failed.
- `DoIt` orchestrates metadata lookup, ghost/detached cleanup, destination selection, zero-size fast path, TPC preparation/execution, retry over sources, and final status.
- `GetFileInfo` prefetches file metadata and copies needed fields into `FileMdProto`.
- `BuildTpcSrc` selects a source replica or RAIN reconstruct path, builds source capability, and returns a root URL.
- `BuildTpcDst` snapshots target fs, builds destination capability and checksum parameters, and returns a root URL.
- `SelectDstFs` uses `GeoTreeEngine::placeNewReplicasOneGroup` with existing replicas/geotags and exclusions to pick a target.
- `DrainZeroSizeFile` updates namespace locations without data transfer.
- `GetInfo` formats requested monitoring tags.
- `UpdateMgmStats` maps app tag/status into MGM statistic counters.

## Control Flow
`DoIt` rejects pre-cancelled jobs, reads metadata, removes ghost or detached entries as successful cleanup, and then loops while alternate sources may be tried. If no forced target is set, it selects one. Replica zero-byte files skip TPC and directly adjust locations. Otherwise it builds source/destination URLs, prepares an XrdCl copy, runs it, and marks success on OK. Prepare/TPC failures log errors; cancellation and `EINPROGRESS` stop retrying.

## State and Persistence
The job mutates namespace replica locations for zero-size files and can trigger FST/MGM-side writes through signed TPC capabilities for non-empty files. Ghost/detached handling drops replicas. Runtime state includes source/target fsids, actual transfer source, tried sources, excluded destinations, RAIN flags, drop-source behavior, transfer progress, error string, and virtual identity for stats.

## Dependencies and Integration Points
Depends on global `gOFS`, `FsView`, `GeoTreeEngine`, `proc_fs_dropghosts`, XrdCl copy, EOS security capabilities via `SymKey`, layout helpers, string tokenization, namespace prefetching, and file metadata services. It is used by `DrainFs` and can also be configured for balance/fsck-like operations via constructor flags.

## Risks
- Error string construction in `BuildTpcDst` uses `err += caprc`, appending a character rather than decimal text.
- `DrainProgressHandler::JobProgress` divides by `bytesTotal` without zero guard.
- Detached-file handling drops all replicas when parent is missing; this is intended cleanup but high-impact if container lookup is transiently wrong.
- Source selection for replica layouts may choose source fs even if its snapshot status is unsuitable in the fallback path.
- RAIN reconstruction is attempted only once; transient failures become job failures.
- Capability construction and URL parameter correctness are security-critical and hard to unit test without integration coverage.

## Test Signals
Tests should cover ghost metadata exceptions, detached parent cleanup, destination placement failure, source retry/exclusion, RAIN reconstruct vs balance URL construction, checksum parameter padding, zero-size metadata update, cancellation, `EINPROGRESS`, and stats tag generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainTransferJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainTransferJob.hh -->
# sources/distributed-fs/eos/mgm/drain/DrainTransferJob.hh

## Purpose
Declares the per-file drain transfer job and progress handler. The class is generic enough to support drain, balance, repair-excluded RAIN reconstruction, and fsck-like replica adjustment through constructor options.

## Important APIs and Types
- `DrainProgressHandler : XrdCl::CopyProgressHandler` tracks cancellation, progress percentage, bytes transferred, and start timestamp.
- `DrainTransferJob::Status { OK, Running, Failed, Ready }`.
- Constructor parameters configure fid, source/target fsids, excluded sources/destinations, source dropping, app tag, balance mode, triggering VID, and repair-excluded behavior.
- Public methods include `DoIt`, `Cancel`, `ReportError`, `SetStatus`, `GetStatus`, `GetInfo`, `UpdateMgmStats`, `GetFileIdentifier`, and `SetMinTransferRate`.
- Under `IN_TEST_HARNESS`, internals such as `GetFileInfo`, URL builders, `SelectDstFs`, and `DrainZeroSizeFile` become public.

## Control Flow and State
The header defines state for app tag, atomic fid/fsids/status/min rate, tried source set, excluded destination vector, RAIN flags, drop-source/balance flags, progress handler, and VID. Cancellation is cooperative through XrdCl progress callbacks.

## Dependencies and Integration Points
Depends on EOS file ids, filesystem ids, namespace file metadata, protobuf file metadata, XrdCl copy process, logging, and virtual identity. `DrainFs` constructs standard drain jobs, while other subsystems can pass non-default flags.

## Risks
- `mExcludeDsts.insert(mExcludeDsts.begin(), exclude_dsts.begin(), exclude_dsts.end())` is valid but unusual and preserves set iteration order rather than caller order.
- Status is atomic, but fields like tried sources and RAIN flags are not protected; they are intended to be job-thread local.
- Progress percentage divides by total bytes in implementation without zero guard.
- Header comment says `GetInfo` returns a map, but it returns `std::list<std::string>`.

## Test Signals
Tests should use `IN_TEST_HARNESS` to validate URL construction, destination selection, zero-size handling, progress cancellation, status transitions, and info tag formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/DrainTransferJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/Drainer.cc -->
# sources/distributed-fs/eos/mgm/drain/Drainer.cc

## Purpose
Implements the central drain manager. It starts/stops the drainer thread, launches per-filesystem `DrainFs` supervisors, queues drains when a node already has too many active filesystem drains, exposes job info, reapplies drain state after mastership, and persists drainer configuration.

## Important APIs and Functions
- `Start`/`Stop` manage the assisted central thread and clear drain fid tracker state on stop.
- `StartFsDrain` validates optional target fs in same space/group, prevents duplicate/pending drains, queues when per-node limit is reached, or starts an async `DrainFs::DoIt`.
- `StopFsDrain` removes pending requests or signals an active `DrainFs` to stop.
- `GetJobsInfo` collects transfer job rows from all or one drain supervisor.
- `Drain` waits for namespace boot/mastership, reapplies drain status, periodically handles queued drains, cleans fid tracker state, and removes completed supervisors.
- `WaitForAllDrainToStop` signals and waits for all active drains before clearing maps.
- `ApplyConfig`, `SetConfig`, `SerializeConfig`, and `StoreConfig` manage global drainer settings.
- `HandleQueued` retries pending drain requests.

## Control Flow
The central thread starts only after namespace boot and mastership, then loops every five seconds. User/API calls to `StartFsDrain` either launch a new `DrainFs` with `std::async` or mark the filesystem `kDrainWait` and append to `mPending`. `HandleQueued` swaps pending requests out under lock and calls `StartFsDrain` for each. Completed futures are removed from `mDrainFs`.

## State and Persistence
Runtime state includes a map from node hostport to active `DrainFs` set, pending source/destination fsid pairs, a shared drain transfer thread pool, and max parallel fs per node. Drainer config is stored in `FsView` global config key `drainer`. Individual filesystem status persistence is handled by `DrainFs`.

## Dependencies and Integration Points
Depends on global `gOFS`, `FsView`, `IMaster`, `DrainFs`, `DrainTransferJob`, thread pool, fid tracker, string tokenization, stacktrace utilities, and table formatting. Start/stop methods assume callers hold `FsView::ViewMutex` read locks per header note.

## Risks
- `HandleQueued` holds an `FsView` read lock while calling `StartFsDrain`, whose header also expects the lock but internally may take `mDrainMutex`; lock ordering should be reviewed against other callers.
- `Stop` joins the assisted thread and then clears tracker; if called when never started, behavior depends on `AssistedThread`.
- `mCfgMutex` exists in the header but config mutation here does not use it.
- Queueing sets local drain wait status but does not persist a durable pending queue; process restart relies on filesystem drain status reapply, not `mPending`.
- `DrainMap` uses `std::set<std::shared_ptr<DrainFs>>`, ordered by pointer rather than fsid.

## Test Signals
Tests should cover same-space/group validation for forced target, duplicate and pending detection, per-node queueing, stop pending vs active drain, config parsing/persistence, completed future cleanup, master wait/reapply behavior, and `GetJobsInfo` for empty and populated drain maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/Drainer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/Drainer.hh -->
# sources/distributed-fs/eos/mgm/drain/Drainer.hh

## Purpose
Declares the central drainer service that coordinates multiple per-filesystem drains and exposes configuration and monitoring APIs.

## Important APIs and Types
- `DrainMap` maps node hostport strings to sets of active `DrainFs` supervisors.
- `DrainHdrInfo` maps display column names to internal `DrainTransferJob` info tags.
- Public API includes lifecycle (`Start`, `Stop`), drain control (`StartFsDrain`, `StopFsDrain`), thread-pool access/info, job info rendering, and config apply/set/serialize.
- Private helpers store config, run the central thread, handle queued requests, and stop all active drains.

## Control Flow and State
The header defines an assisted central thread, protected active drain map, pending queue, shared transfer thread pool, and atomic max-filesystems-per-node limit. `StartFsDrain` and `StopFsDrain` document that callers must hold the `FsView` read lock.

## Dependencies and Integration Points
Depends on MGM namespace, logging, thread pool, assisted thread, filesystem types, `DrainFs`, `DrainTransferJob`, and table formatting. The implementation integrates with `FsView`, `gOFS`, and master state.

## Risks
- `mCfgMutex` is declared but unused in the implementation.
- `DrainMap` set ordering by shared pointer can make output/order nondeterministic.
- The public `GetThreadPool` returns a mutable reference to the internal pool, which allows external code to alter behavior outside `Drainer` config paths.
- Stop/destructor lifecycle depends on `AssistedThread::join` being safe when the thread was never started.

## Test Signals
Header-level tests should validate API use with required locks, config serialization, mutable thread-pool access expectations, and drain map/pending queue behavior through public methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/drain/Drainer.hh -->
