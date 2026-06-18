# subset-b-007767 Research

Grouped research for OpenAFS backup coordinator (`bucoord`) command/configuration/runtime files and the backup database build recipe. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/commands.c -->
# sources/distributed-fs/openafs/src/bucoord/commands.c

## Purpose
Implements most user-visible `backup` command handlers and shared command utilities for the OpenAFS Backup Coordinator. It expands volume sets through VLDB queries, schedules and starts dump/restore work, manages jobs, talks to tape coordinators for tape/database actions, queries and deletes backup database records, parses dates/ports/sizes, and reports dump/volume metadata to users.

## Important APIs, Types, And Functions
Main command entry points are `bc_DumpCmd`, `bc_VolRestoreCmd`, `bc_DiskRestoreCmd`, `bc_VolsetRestoreCmd`, `bc_QuitCmd`, `bc_JobsCmd`, `bc_KillCmd`, `bc_GetTapeStatusCmd`, `bc_LabelTapeCmd`, `bc_ReadLabelCmd`, `bc_ScanDumpsCmd`, `bc_dblookupCmd`, `bc_dbVerifyCmd`, `bc_deleteDumpCmd`, `bc_saveDbCmd`, `bc_restoreDbCmd`, `bc_dumpInfoCmd`, and `bc_SetExpCmd`. Volume expansion is handled by `bc_EvalVolumeSet`, `EvalVolumeSet2`, and fallback `EvalVolumeSet1`; `getSPEntries` and `randSPEntries` group matched volumes by server/partition and randomize processing order. Utility APIs include `bc_SafeATOI`, `bc_FloatATOI`, `bc_CopyString`, `concatParams`, `compactDateString`, `compactTimeString`, `getPortOffset`, and `bc_ParseExpiration`. Local structures include `serversort`, `partitionsort`, `dumpedVol`, `volumeLink`, and `tapeLink`.

## Control Flow
Dump execution first refreshes dump schedules, volume sets, and tape hosts, validates mutually exclusive options, optionally queues a scheduled dump as a status node, optionally records a load file for `main.c` recursion, then locates the selected volume set and dump schedule. For incremental dumps it walks parent dump schedule nodes, calls `bcdb_FindLatestDump` and `bcdb_FindDumpByID` to find a complete parent chain, expands the volume set through VLDB, records previous clone times via `bcdb_FindClone`, and starts the asynchronous worker with `bc_StartDmpRst(..., bc_Dumper, ...)`. Restore handlers build `bc_volumeDump` lists from explicit volume names, evaluated volume sets, partitions, or input files, normalize destination server/partition/extension/port options, and start `bc_Restorer`.

Tape and database commands refresh tape hosts, connect indirectly through `dump.c`, and issue butc or BUDB operations. `deleteDump` optionally asks an XBSA-capable tape coordinator to delete remote objects, waits for the task, then removes BUDB dump records. `dumpInfo` gathers dump, tape, and volume entries from BUDB and formats either compact or detailed output. Job commands inspect or mutate the shared status queue: `jobs` prints active and scheduled work, `kill` sets `ABORT_REQUEST`, `quit` refuses to exit until jobs are aborted or done.

## State And Persistence
The file uses global `bc_globalConfig`, `bc_dumpTasks`, `cstruct` VLDB client, `whoami`, `loadFile`, `dontExecute`, `lastTaskCode`, `tokenExpires`, and `dispatchLock`. Persistent effects happen through BUDB (`bcdb_*`, `ubik_BUDB_*`) and tape coordinator RPCs (`TC_*`) rather than local files. Scheduled dumps live only in memory as status queue nodes with `scheduledDump` and reconstructed `cmdLine`. Dry-run mode prints volume/restore/delete plans and avoids work submission.

## Dependencies And Integration Points
Depends on OpenAFS command parsing, com_err, BUDB client stubs, butc/tape coordinator RPCs, VLDB/volser APIs, ktime parsing, rx/ubik, status queue helpers, configuration refresh functions from `tape_hosts.c`, `vol_sets.c`, and `dump_sched.c`, job launcher functions from `dump.c`, restore logic from `restore.c`, and volume clone-time helpers from `volstub.c`. It is registered from `main.c` as the implementation of most `backup` subcommands.

## Risks And Test Signals
Key risks are long manual linked-list flows with partial cleanup on errors, fixed-size string buffers around dump names/tape names/volume names, legacy non-cryptographic randomization of volume order, mixed error conventions (`-1`, errno, com_err codes), and concurrency interactions between status queue operations, dispatch recursion, and LWP dump tasks. Volume expansion has two VLDB implementations with fallback on `RXGEN_OPCODE`, so compatibility with older VLDB servers matters. Test signals include `backup dump -n`, scheduled `dump -at`, `dump -file` recursion limits, volume-set expansion with RW/BK/RO matches, parent incremental selection with missing dumps, restore dry-run output, job/kill behavior, dump deletion with `-dbonly`, `-force`, and `-dryrun`, database verification, dumpinfo output, and authenticated/unauthenticated tape coordinator operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/commands.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/config.c -->
# sources/distributed-fs/openafs/src/bucoord/config.c

## Purpose
Provides the in-memory backup coordinator configuration root and small helpers for opening files under that root and maintaining tape-host lists. It initializes `bc_globalConfig` and supplies the host add/delete primitives used by tape-host command and persistence code.

## Important APIs, Types, And Functions
Exports `bc_globalConfig`, `bc_open`, `bc_InitConfig`, `bc_AddTapeHost`, and `bc_DeleteTapeHost`. Private helpers `HostAdd` and `HostDelete` operate on `struct bc_hostEntry` singly linked lists, resolving host names to `sockaddr_in` and storing a tape coordinator port offset.

## Control Flow
`bc_InitConfig` allocates a zeroed `struct bc_config`, stores the configuration path, and makes it globally visible. `bc_open` constructs `aconfig->path/aname[aext]` into a fixed local buffer and calls `fopen`. `HostAdd` verifies the host through `gethostbyname`, rejects any existing entry with the same port offset, appends a new host record, and copies the resolved address. `HostDelete` finds an exact host-name and port-offset match, unlinks it, and frees its name and record.

## State And Persistence
`bc_InitConfig` initializes only in-memory state; persistent text configuration is loaded later through BUDB text APIs in other modules. `bc_open` can read or write local files below the configured path, but the current file does not itself save host entries. Host records live in `bc_globalConfig->tapeHosts` until refreshed, saved, or cleared by `tape_hosts.c`.

## Dependencies And Integration Points
Depends on `bc.h` for `struct bc_config` and `struct bc_hostEntry`, libc allocation/string/file APIs, and resolver APIs. The host-list primitives are called by `tape_hosts.c`; `bc_InitConfig` is invoked by `main.c` during `backupInit`.

## Risks And Test Signals
`bc_open` uses unbounded `strcpy`/`strcat` into a 256-byte path buffer. `HostAdd` checks duplicate port offsets only, so two names for the same host with different offsets are allowed while any two hosts sharing one offset are rejected. `gethostbyname` is IPv4-only and legacy. Test signals are initialization with a valid backup directory, add/delete/list host flows, duplicate port offset handling, invalid host handling, and long path/name robustness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dlq.c -->
# sources/distributed-fs/openafs/src/bucoord/dlq.c

## Purpose
Implements a minimal intrusive doubly linked queue used by backup coordinator status management. Queue heads are sentinel `dlqlinkT` records and entries embed the same link fields, allowing status nodes and other structures to be linked without wrapper allocation.

## Important APIs, Types, And Functions
The public queue operations are `dlqInit`, `dlqEmpty`, `dlqLinkf`, `dlqLinkb`, `dlqMoveb`, `dlqUnlinkb`, `dlqUnlinkf`, `dlqUnlink`, `dlqFront`, `dlqCount`, and `dlqTraverseQueue`. `DLQ_ASSERT_HEAD` validates sentinel nodes by checking `dlq_type == DLQ_HEAD`.

## Control Flow
Initialization points head `next` and `prev` at itself and marks it as `DLQ_HEAD`. Link operations splice entries at the front or back. `dlqMoveb` appends all entries from one queue to another and resets the source head to empty. Unlink operations remove first, last, or a specific entry and either self-link or null the removed entry’s pointers. Traversal walks from head to head, optionally calling one function on each entry’s `dlq_structPtr` and another on the link itself.

## State And Persistence
All state is in caller-owned memory; there is no persistence or allocation. The implementation mutates embedded link pointers directly and has no internal locking, so callers must provide synchronization.

## Dependencies And Integration Points
Depends on queue link definitions from `bc.h`/`afs/bubasics.h`. `status.c`, `bc_status.c`, and `commands.c` use it for the global status queue and temporary job listing queues.

## Risks And Test Signals
Invalid queue heads or attempts to unlink a head call `printf` and `exit(1)`, which is harsh for library-style code. Link functions do not verify whether an entry is already linked. There is no thread safety without external locks. Test signals include empty queue behavior, front/back insertion order, moving non-empty and empty queues, unlink first/last/specific nodes, traversal while freeing nodes, and misuse assertions in debug or fault-injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dlq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dsstub.c -->
# sources/distributed-fs/openafs/src/bucoord/dsstub.c

## Purpose
Provides a local flat-file stub for backup dump/tape metadata scanning. It names and opens local `T<tapename>.db` and `D<dumpid>.db` files under the server backup directory, parses dump headers and volume records, finds clone times, and recursively deletes local dump files by parent-child relationships.

## Important APIs, Types, And Functions
Important functions are `OpenTape`, `tailCompPtr`, `ScanDumpHdr`, `ScanTapeVolume`, and `ScanVolClone`. Private helpers `TapeName`, `DumpName`, `OpenDump`, `ScanForChildren`, and `DeleteDump` construct paths, open files, and remove dump trees.

## Control Flow
`TapeName` and `DumpName` allocate canonical local metadata paths with `asprintf`. `OpenTape` and `OpenDump` open those files in caller-specified modes. `ScanDumpHdr` reads the first dump line, parses magic, version, dump name, dump path, parent id, incremental time, create time, and level, then validates magic/version. `ScanTapeVolume` reads one volume-record line and distinguishes success, EOF, and parse/error. `ScanVolClone` scans records until it finds a matching volume name. `DeleteDump` unlinks the dump file and then calls `ScanForChildren`, which scans the backup directory for dump files whose header parent matches the deleted id.

## State And Persistence
State is persistent local metadata in `AFSDIR_SERVER_BACKUP_DIRPATH`, with a text format described in comments. Functions allocate path strings transiently and leave file lifecycle mostly to callers. Deletion removes local dump files and recursively removes child dump metadata.

## Dependencies And Integration Points
Depends on OpenAFS directory constants, BUDB/bubasics/volser headers for constants and types, standard directory and file APIs, and `bc.h`. `tailCompPtr` is reused by display and command code to print the final component of dump schedule paths.

## Risks And Test Signals
The parser uses fixed-size line buffers and whitespace-delimited fields, so names with whitespace cannot be represented and long lines are truncated. Several `sscanf` calls cast `afs_int32 *` to `long int *`, which is ABI-sensitive. Recursive deletion is based on scanning live directory contents and ignores unreadable child headers. Test signals include parsing valid/invalid magic/version headers, EOF and malformed volume lines, clone lookup hits/misses, local tape/dump open failures, child dump recursive deletion, and long-name boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dsstub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dsvs.c -->
# sources/distributed-fs/openafs/src/bucoord/dsvs.c

## Purpose
Maintains core in-memory abstractions for volume sets and dump schedules independent of their BUDB text persistence. It parses host and partition selectors, creates/deletes volume sets and entries, creates/deletes dump schedule nodes, and rebuilds the dump schedule tree from pathname-style schedule names.

## Important APIs, Types, And Functions
Volume-set APIs include `bc_GetPartitionID`, `bc_ParseHost`, `bc_CreateVolumeSet`, `bc_AddVolumeItem`, `bc_DeleteVolumeItem`, `bc_DeleteVolumeSet`, `bc_FindVolumeSet`, and `FreeVolumeSet`. Dump-schedule APIs include `bc_CreateDumpSchedule`, `bc_DeleteDumpSchedule`, `bc_DeleteDumpScheduleAddr`, `bc_FindDumpSchedule`, `bc_ProcessDumpSchedule`, and `FindDump`. Private helpers free `struct bc_volumeEntry` lists.

## Control Flow
Partition parsing accepts `.*` as wildcard `-1`, numeric strings, single-letter partition names, and `vicep`/`/vicep` names. Host parsing first accepts dotted IPv4 strings, then wildcard `.*`, then DNS names via `gethostbyname`. Volume-set creation rejects duplicates and prepends temporary sets while appending persistent sets. Entry creation appends to the selected set after duplicating selector strings and resolving host/partition fields. Dump schedule creation uses `FindDump` to validate path parents and reject duplicates, prepends a new node, stores expiration metadata, and rebuilds the tree. Schedule deletion recursively removes children then rebuilds parent/child/sibling links.

## State And Persistence
All state is in `struct bc_config`: `vset` is a linked list of `bc_volumeSet` objects with `bc_volumeEntry` children, and `dsched` is a flat linked list with derived tree pointers (`parent`, `firstChild`, `nextSibling`). This file does not write persistence; `vol_sets.c` and `dump_sched.c` serialize these lists into BUDB text blocks.

## Dependencies And Integration Points
Depends on `bc.h`, `bucoord_internal.h`, resolver/socket APIs, `opr_Assert`, and backup error constants. It is the shared model layer used by command handlers and by text parse/save modules.

## Risks And Test Signals
IPv4 dotted parsing does not range-check octets before bit shifting. `bc_ParseHost` byte-order handling differs between dotted names and `gethostbyname`, which deserves interoperability tests. `FindDump` is strict about leading slash and can return confusing errors for trailing slashes. `bc_ProcessDumpSchedule` exits the process if an existing schedule path cannot be found. Test signals include wildcard partition/host entries, all partition name forms, invalid dump path syntax, duplicate set/schedule rejection, temporary volume set ordering and non-persistence, recursive schedule deletion, and tree rebuild correctness for multi-level paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dsvs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dump.c -->
# sources/distributed-fs/openafs/src/bucoord/dump.c

## Purpose
Runs dump/restore helper jobs and tape coordinator operations for the backup coordinator. It owns the global dump-task slots, launches asynchronous LWP worker processes, packages volume dumps into butc RPC structures, connects to tape coordinators, and exposes label/read/scan helpers.

## Important APIs, Types, And Functions
Global state is `bc_dumpTasks[BC_MAXSIMDUMPS]`. Main functions are `bc_Dumper`, `bc_StartDmpRst`, `bc_DmpRstStart`, `freeDumpTaskVolumeList`, `bc_LabelTape`, `bc_ReadLabel`, `bc_ScanDumps`, `bc_GetConn`, `CheckTCVersion`, and `ConnectButc`. The central data type is `struct bc_dumpTask`, populated by `bc_StartDmpRst` and consumed by `bc_Dumper` or `bc_Restorer`.

## Control Flow
`bc_StartDmpRst` finds a free task slot, copies command state into it, records destination/parent/level/port/expiration/append/dry-run fields, and creates an LWP helper process. `bc_DmpRstStart` calls the selected worker function, records `lastTaskCode` on failure, frees volume lists and copied strings, releases the port array, and clears `BC_DI_INUSE`. `bc_Dumper` connects to the selected butc, converts each `bc_volumeDump` into a `tc_dumpDesc`, constructs dump/tape naming fields, calls `TC_PerformDump`, and creates a status node for monitoring. Label, read-label, and scan-dumps helpers perform similar butc RPC submission and status setup.

## State And Persistence
The file maintains transient task slot state and status queue nodes. Persistent effects are delegated to tape coordinator operations and later BUDB updates performed by butc. `bc_GetConn` caches the chosen RX security class and index in static variables, so authentication mode is effectively fixed after the first tape coordinator connection.

## Dependencies And Integration Points
Depends on LWP, RX, OpenAFS auth/cell config, butc RPC stubs, TC status constants, `status.c`, `commands.c` utilities, and `tape_hosts.c` configuration state. `commands.c` calls `bc_StartDmpRst` for dump and restore commands, and `restore.c` supplies `bc_Restorer`.

## Risks And Test Signals
Task slots are scanned and marked without an explicit lock, so concurrent command dispatch can race if multiple LWPs enter start logic. Several string copies into RPC fields assume earlier command validation. `bc_LabelTape` and other error paths can return without destroying RX connections. Static security caching in `bc_GetConn` may surprise mixed `-localauth`/`-nobutcauth` sessions. Test signals include slot exhaustion, LWP creation failure cleanup, dump RPC request contents, status node creation, tape coordinator version mismatch, authenticated/null/fallback butc connections, label/read/scantape flows, and cleanup after worker completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dump_sched.c -->
# sources/distributed-fs/openafs/src/bucoord/dump_sched.c

## Purpose
Implements `backup` commands and BUDB text-block synchronization for dump schedules. It adds, deletes, lists, parses, saves, updates, and modifies expiration metadata for schedule nodes represented by `struct bc_dumpSchedule`.

## Important APIs, Types, And Functions
Command handlers are `bc_AddDumpCmd`, `bc_DeleteDumpCmd`, `bc_ListDumpScheduleCmd`, and `bc_SetExpCmd`. Persistence helpers are `bc_ParseDumpSchedule`, `bc_SaveDumpSchedule`, and `bc_UpdateDumpSchedule`. `ListDumpSchedule` recursively prints a schedule tree with expiration details.

## Control Flow
Mutating commands lock `TB_DUMPSCHEDULE`, refresh the local schedule from BUDB, modify the in-memory tree through `dsvs.c` helpers, save the text block back to BUDB, and unlock. Listing refreshes the schedule and prints only root nodes, recursively visiting children. Parsing validates a magic/version header, then reads `dump-name period expDate expType` lines into the flat schedule list; after update, `bc_ProcessDumpSchedule` rebuilds the tree. Saving truncates the local temp stream, writes the header and all schedule records, calls `bcdb_SaveTextFile`, increments the local version, and updates text size.

## State And Persistence
State is `bc_globalConfig->dsched` plus `bc_globalConfig->configText[TB_DUMPSCHEDULE]`. Persistent storage is BUDB configuration text, protected by BUDB text locks. The `period` field is currently serialized as `"any"` and not used in the in-memory creation path; expiration fields are preserved.

## Dependencies And Integration Points
Depends on ktime conversion, BUDB client text locking/versioning from `ubik_db_if.c`, dump-schedule model helpers from `dsvs.c`, error macros, com_err, and global `udbHandle`. The schedule data drives `commands.c` dump parent selection and expiration propagation into `dump.c`.

## Risks And Test Signals
Several early returns after failed refresh skip the `error_exit` unlock path if the lock was already acquired. Clearing obsolete schedule entries frees only the schedule node and leaks `name`. The parser rejects any malformed line and has fixed-size field buffers. Test signals include add/delete/set expiration with lock/unlock verification, stale version refresh, empty schedule text, invalid magic/version, malformed lines, tree listing indentation, relative and absolute expiration formatting, and save failure behavior that leaves session-local changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/dump_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/error_macros.h -->
# sources/distributed-fs/openafs/src/bucoord/error_macros.h

## Purpose
Defines local structured-error macros for backup coordinator C files. The macros set a function-local `code` variable and jump to a conventional cleanup label.

## Important APIs, Types, And Functions
`ERROR(evalue)` assigns `code = evalue` and jumps to `error_exit`. `ABORT(evalue)` assigns `code = evalue` and jumps to `abort_exit`. Both undefine previous definitions before redefining.

## Control Flow
Files that include this header must declare a compatible `code` variable and provide the corresponding label. The macros centralize early-exit cleanup in functions with many allocation, lock, RPC, or file failure points.

## State And Persistence
The header stores no state. It influences cleanup behavior in callers and therefore affects lock release, stream cleanup, allocated-memory release, and RPC connection teardown.

## Dependencies And Integration Points
It is included by the command, dump schedule, volume set, tape host, dump, restore, and BUDB interface modules. It depends only on C `goto` label conventions.

## Risks And Test Signals
The macro contract is implicit: missing `code`, `error_exit`, or `abort_exit` labels cause compile failures, while using the macro in a scope where `code` has a different type can produce subtle behavior. Early direct `return`s in files using these macros are a risk because they bypass the intended cleanup labels. Compile coverage and fault-injection paths that verify locks/connections are released are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/error_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/main.c -->
# sources/distributed-fs/openafs/src/bucoord/main.c

## Purpose
Defines the `backup` program entrypoint. It initializes error tables, RX/LWP, VLDB and BUDB clients, backup configuration, and status monitoring; registers all command syntaxes; dispatches one-shot, interactive, and load-file commands; and waits for background jobs before non-interactive exit.

## Important APIs, Types, And Functions
Important functions are `InitErrTabs`, `bc_HandleMisc`, `bc_InitTextConfig`, `backupInit`, `MyBeforeProc`, `doDispatch`, `bc_interactCmd`, `add_std_args`, and `main`. Global process state includes `localauth`, `interact`, `nobutcauth`, `tcell`, `tokenExpires`, `whoami`, `bcInit`, `DefaultConfDir`, `dispatchLock`, and `lineBuffer`.

## Control Flow
`main` initializes locks and error tables, decides whether to enter interactive mode, registers a `cmd` before-proc, then builds syntaxes for dump, restore, configuration, tape, database, and status commands. `MyBeforeProc` lazily performs full initialization on the first real command, capturing standard auth arguments from command parameter slots. `backupInit` creates `bc_globalConfig`, initializes LWP and RX, sets RX dead time, initializes VLDB and BUDB clients, initializes status locks/queue, and starts the status watcher LWP. `doDispatch` serializes `cmd_Dispatch` with `dispatchLock`, handles `dump -file` by opening the requested command file, echoes lines, skips blanks/comments, parses lines, and recursively dispatches them up to `MAXRECURSION`. Non-interactive mode waits for jobs through `bc_WaitForNoJobs`; interactive mode reads lines with `LWP_GetLine` until EOF.

## State And Persistence
Most state is process-global and transient. `bc_InitTextConfig` initializes BUDB text handles for tape hosts, volume sets, and dump schedules with version `-1` and temp file name slots; actual text content is fetched lazily by update functions. Persistent changes are made by command handlers through BUDB and butc, not by `main.c` directly.

## Dependencies And Integration Points
Depends on OpenAFS `cmd`, RX, LWP, auth/cell config, VLDB, BUDB, butm/butc/butx error tables, status watcher from `bc_status.c`, model/config functions, and every command handler declared in `bucoord_internal.h`. The command parameter indexes used by `add_std_args` and `MyBeforeProc` must remain aligned.

## Risks And Test Signals
Command registration relies on hard-coded parameter indexes for common auth flags, which can break if syntaxes shift. `doDispatch` uses global `loadFile`/`dontExecute` for recursive load-file handling and serializes all dispatches to avoid parser corruption. Interactive startup can defer initialization until after help/apropos-like commands. Test signals include `backup -help` without full init, non-interactive standard auth parsing, interactive prompt dispatch, load-file recursion cutoff, blank/comment handling, command-line-too-long handling, job wait exit status, and status watcher startup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/restore.c -->
# sources/distributed-fs/openafs/src/bucoord/restore.c

## Purpose
Implements restore-job planning and execution. It maps requested volumes to BUDB dump lineages, builds an ordered tape/volume-fragment restore plan, supports dry-run output, and submits grouped restore RPCs to tape coordinators with correct full/incremental sequencing.

## Important APIs, Types, And Functions
Exported functions are `BackupName` and `bc_Restorer`; local helpers are `StripBackup`, `extractTapeSeq`, and `viceName`. Internal planning structures are `dumpinfo`, `volinfo`, `bc_tapeList`, and `bc_tapeItem`, representing dump chains, target volumes, tapes, and ordered restore fragments.

## Control Flow
`bc_Restorer` receives a `bc_dumpTask` slot. For each requested volume it finds the most recent matching dump before the requested date, or a caller-specified dump id, also trying `.backup` names when appropriate. It builds a dump list sorted from newer to older, attaches requested volume targets, then walks each dump’s parent chain back to the full dump. For each volume and each dump level from full to latest incremental, it calls `bcdb_FindVolumes`, sorts returned fragments into a global tape list by dump/tape sequence and tape position, and records restore server/partition and first/last dump flags. Dry-run mode prints either human-readable restore plans or file format suitable for `volsetrestore`. Execution mode converts tape items to `tc_restoreDesc` entries and submits contiguous batches to butc, choosing port offsets by dump level when multiple ports are supplied and waiting for each restore pass to finish before starting the next.

## State And Persistence
The restore plan is entirely in-memory and freed before return. Persistent effects are delegated to butc/volserver restore operations. Destination server/partition can be global for all restored volumes, or per-volume from input/evaluated volume metadata. The task’s `newExt`, `oldFlag`, `fromDate`, `parentDumpID`, `portOffset`, and `dontExecute` fields shape restore behavior.

## Dependencies And Integration Points
Depends on BUDB lookup wrappers in `ubik_db_if.c`, butc restore RPCs, RX connection helpers from `dump.c`, status queue helpers, command-populated `bc_dumpTask` structures, and OpenAFS volume/tape constants. `commands.c` prepares restore tasks and `dump.c` launches this function via `bc_StartDmpRst`.

## Risks And Test Signals
The planning logic is complex and allocation-heavy, with many linked-list insertion cases for appended dumps, fragmented volumes, and multi-level incrementals. Fixed-size volume-name buffers and extension concatenation need boundary coverage. The `viceName` alphabet string appears to omit `g`, which can affect dry-run partition formatting. The dynamic `dlevels` resize path must preserve existing chain data. Test signals include restoring explicit volumes, `.backup` fallback, `-usedump`, full plus incremental chains, fragmented volumes across tapes, appended dump ordering, multi-port restore level routing, dry-run `volsetrestore` output, abort/error status handling while waiting, and cleanup on BUDB or butc failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/server.c -->
# sources/distributed-fs/openafs/src/bucoord/server.c

## Purpose
Implements the backup coordinator’s small incoming RX service callback for printing messages sent by other components.

## Important APIs, Types, And Functions
The only function is `SBC_Print(struct rx_call *acall, afs_int32 acode, afs_int32 aflags, char *amessage)`.

## Control Flow
`SBC_Print` obtains the RX connection and peer from the call, prints the peer host address, message string, and code to stdout, and returns success. The `aflags` argument is currently unused.

## State And Persistence
No state is stored and nothing is persisted. The only side effect is console output.

## Dependencies And Integration Points
Depends on RX call/connection/peer APIs. It is part of the backup coordinator service surface for incoming message-port notifications.

## Risks And Test Signals
There is no validation of `amessage`, no formatting of flags, and no authentication or filtering in this function itself. Test signals are successful RX callback dispatch, correct peer host display, safe behavior with empty messages, and build coverage with generated service stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/status.c -->
# sources/distributed-fs/openafs/src/bucoord/status.c

## Purpose
Provides shared status-queue primitives for backup coordinator tasks. It initializes locks, creates/finds/deletes status nodes, and sets or clears task status flags under the queue lock.

## Important APIs, Types, And Functions
Public functions are `initStatus`, `lock_Status`, `unlock_Status`, `lock_cmdLine`, `unlock_cmdLine`, `clearStatus`, `createStatusNode`, `deleteStatusNode`, `findStatus`, and `setStatus`. It operates on external globals `statusHead`, `statusQueueLock`, and `cmdLineLock`.

## Control Flow
`initStatus` initializes the queue sentinel and locks. `createStatusNode` allocates a zeroed status object, links it at the back of `statusHead`, marks it `STARTING`, and returns it for caller population. `findStatus` linearly scans the queue by `taskId`. `setStatus` and `clearStatus` lock, find the node, update flags, and unlock. `deleteStatusNode` unlinks and frees a status node and its optional `cmdLine`.

## State And Persistence
State is transient in-memory status records linked through an intrusive `dlq` queue. There is no persistence. The queue is protected by `statusQueueLock`; command-line string access can be protected separately with `cmdLineLock`.

## Dependencies And Integration Points
Depends on `dlq.c`, OpenAFS lock primitives, `bc.h` status types, and com_err/command headers. Dump, restore, tape, database, job, kill, and status watcher code all coordinate through these helpers.

## Risks And Test Signals
`findStatus` does not lock internally, so callers must know whether they already hold the queue lock; some code intentionally does. `deleteStatusNode` assumes the node is currently linked and not concurrently observed. Test signals include create/find/set/clear/delete under lock, deleting nodes with `cmdLine`, concurrent status watcher updates, kill/abort flag propagation, and scheduled dump queue behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/tape_hosts.c -->
# sources/distributed-fs/openafs/src/bucoord/tape_hosts.c

## Purpose
Implements tape-host command handlers and BUDB text-block persistence. It adds, deletes, lists, parses, saves, and refreshes the tape coordinator host list stored in `bc_globalConfig->tapeHosts`.

## Important APIs, Types, And Functions
Command handlers are `bc_AddHostCmd`, `bc_DeleteHostCmd`, and `bc_ListHostsCmd`. Support functions are `bc_ClearHosts`, `bc_ParseHosts`, `bc_SaveHosts`, and `bc_UpdateHosts`.

## Control Flow
Add/delete commands lock `TB_TAPEHOSTS`, refresh the local list from BUDB, parse the optional port offset, call `bc_AddTapeHost` or `bc_DeleteTapeHost`, save the text block back through `bc_SaveHosts`, and unlock. Listing refreshes and prints every host/offset pair. Parsing rewinds the text stream, reads `hostname port` lines, resolves host names, allocates `bc_hostEntry` nodes, and replaces the global host list. Saving truncates the stream, writes one line per host, calls `bcdb_SaveTextFile`, increments local version, and updates size. Updating compares BUDB text version, locks if needed, opens a temp stream, downloads text, fetches version, parses, and unlocks if it acquired the lock.

## State And Persistence
The in-memory tape host list mirrors BUDB configuration text type `TB_TAPEHOSTS`. Persistent writes require a BUDB text lock. On Unix, downloaded text streams are temporary unlinked files managed by `ubik_db_if.c`.

## Dependencies And Integration Points
Depends on `config.c` host add/delete helpers, BUDB text locking/versioning, OpenAFS command/com_err APIs, and `bc_globalConfig`. `dump.c` uses the resulting host list to connect to butc by port offset.

## Risks And Test Signals
`bc_ParseHosts` does not validate `sscanf` return count and can reuse previous `port` values on malformed lines. Resolver failures still create entries with zero address, later producing `BC_NOHOSTENTRY`. Some refresh error returns bypass unlock paths. Duplicate prevention happens in `config.c` by port offset, not by hostname. Test signals include add/delete/list with default and nonzero offsets, malformed text lines, unresolved host entries, stale version refresh, save failure session-only warning, lock contention, and butc connection lookup by offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/tape_hosts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/ubik_db_if.c -->
# sources/distributed-fs/openafs/src/bucoord/ubik_db_if.c

## Purpose
Wraps BUDB and VLDB Ubik/RX client interactions for the backup coordinator. It provides typed helper functions for backup database records, text configuration locking/get/save/versioning, BUDB/VLDB client initialization, single-server Ubik iteration, local test initialization, and temporary text-file management.

## Important APIs, Types, And Functions
Global state is `struct udbHandleS udbHandle`. BUDB wrappers include `bcdb_AddVolume`, `bcdb_AddVolumes`, `bcdb_CreateDump`, `bcdb_deleteDump`, `bcdb_listDumps`, `bcdb_DeleteVDP`, `bcdb_FindClone`, `bcdb_FindDump`, `bcdb_FindDumpByID`, `bcdb_FindLatestDump`, `bcdb_FindTape`, `bcdb_FindTapeSeq`, `bcdb_FindVolumes`, `bcdb_LookupVolume`, `bcdb_FinishDump`, `bcdb_FinishTape`, `bcdb_UseTape`, `bcdb_FindLastTape`, and `bcdb_MakeDumpAppended`. Text APIs are `bcdb_GetTextFile`, `bcdb_SaveTextFile`, `bc_LockText`, `bc_UnlockText`, `bc_CheckTextVersion`, `bc_openTextFile`, and `bc_closeTextFile`. Initialization APIs are `vldbClientInit`, `udbClientInit`, and test-only `udbLocalInit`. Specialized wrappers are `ubik_Call_SingleServer_BUDB_GetVolumes` and `ubik_Call_SingleServer_BUDB_DumpDB`.

## Control Flow
Most record functions are thin delegates to `ubik_BUDB_*`, adding list setup, result count checks, and allocated-result cleanup. `bcdb_FindDumpByID`, `bcdb_FindTape`, and `bcdb_FindTapeSeq` use list-returning BUDB RPCs and require exactly one result. Text download requires an existing lock and open temp stream, then repeatedly calls `ubik_BUDB_GetText` in 1024-byte chunks until `nextOffset == -1`, writes chunks locally, and refreshes the text version. Text save rewinds the stream, computes size, sends either a zero-length complete marker or chunked `ubik_BUDB_SaveText` calls, marking the final chunk complete. Locking loops on `BUDB_LOCKED`/`BUDB_SELFLOCKED`, printing every 30 seconds, and stores the returned lock handle.

`vldbClientInit` and `udbClientInit` choose client or server config directories from auth flags, resolve cell/server information, choose RX security objects with fallback null security, build RX connections, initialize Ubik clients, and for BUDB fetch an instance id with a short-deadtime first pass. `ubik_Call_SingleServer` selects a working server for a call series, sticks to it while `UF_SINGLESERVER` remains active, and clears state on failure or `UF_END_SINGLESERVER`.

## State And Persistence
Persistent data is the BUDB database and BUDB text configuration. Runtime state includes `udbHandle` security object/index, server RX connections, Ubik client pointer, instance id, text lock handles in each `udbClientTextT`, temp streams, and static `uServer` single-server call state. Temporary text files are created under `gettmpdir()`, unlinked immediately on Unix, and explicitly removed on NT.

## Dependencies And Integration Points
Depends on OpenAFS auth/cellconfig, RX, Ubik, VLDB, volser, BUDB generated client stubs, `afsconf_PickClientSecObj`, and `bc.h` text/config types. Configuration modules call the text APIs; command, dump, and restore modules call the BUDB record APIs; `main.c` calls the initialization routines.

## Risks And Test Signals
The thin wrappers inherit BUDB RPC semantics and often collapse multi-result or end-of-list cases into local error conventions. `bcdb_FindVolumes` points XDR output directly at caller storage, so RPC stub expectations must match. Text locking can wait indefinitely with one-second sleeps. Temp file error paths must close streams and preserve lock cleanup by callers. `ubik_Call_SingleServer` stores one static selected server, so concurrent single-server series would interfere. Test signals include authenticated, localauth, noauth, and fallback-null initialization; no-cell and too-many-server warnings; text lock contention and timeout sizing; chunked get/save including empty text; version mismatch detection; exact-one dump/tape lookup; BUDB list length consistency; single-server iteration cleanup; and local test initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/ubik_db_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/vol_sets.c -->
# sources/distributed-fs/openafs/src/bucoord/vol_sets.c

## Purpose
Implements volume-set command handlers and BUDB text-block synchronization. It creates/deletes/lists volume sets, adds/deletes volume entries, parses the stored text format, saves persistent sets, and refreshes in-memory state on BUDB version changes.

## Important APIs, Types, And Functions
Command handlers are `bc_AddVolSetCmd`, `bc_DeleteVolSetCmd`, `bc_AddVolEntryCmd`, `bc_DeleteVolEntryCmd`, and `bc_ListVolSetCmd`. Persistence/support functions are `bc_ClearVolumeSets`, `bc_ParseVolumeSet`, `bc_SaveVolumeSet`, and `bc_UpdateVolumeSet`; `ListVolSet` formats one set.

## Control Flow
Command handlers refresh the current volume-set text, lock `TB_VOLUMESET` for persistent sets, perform model mutations through `dsvs.c`, save when needed, and unlock. Temporary volume sets skip locking and saving. Parsing reads a repeated text format of `volumeset <name>`, one or more `<server> <partition> <volume-regexp>` lines, and `end`, allocating linked `bc_volumeSet` and `bc_volumeEntry` records. Saving truncates the stream and writes all non-temporary sets in the same format before sending it to BUDB. Updating checks text version, locks if stale, clears only non-temporary existing sets, downloads text into a temp stream, fetches the server version, parses, and optionally unlocks.

## State And Persistence
State is `bc_globalConfig->vset` and text handle `configText[TB_VOLUMESET]`. Persistent volume sets are stored in BUDB text. Temporary sets live only in memory and are preserved across refreshes by `bc_ClearVolumeSets`.

## Dependencies And Integration Points
Depends on BUDB text helpers from `ubik_db_if.c`, model helpers from `dsvs.c`, command/com_err APIs, and `bc_globalConfig`. `commands.c` uses the resulting volume sets to evaluate dumps/restores.

## Risks And Test Signals
`bc_AddVolEntryCmd` reports an uninitialized/old `code` if a set is missing before `ERROR(code)`. Several refresh failure paths return without unlocking when they already hold the lock. Parser errors can leak partially allocated structures, and host-parse failures are logged but do not stop entry creation until partition parsing. Fixed-size `%255s` parsing disallows whitespace and truncates long fields. Test signals include persistent and temporary set lifecycle, entry add/delete by 1-based index, malformed text with missing `end`, stale version refresh preserving temporary sets, save failure session-only behavior, wildcard host/partition entries, invalid regex strings surfaced later by volume evaluation, and listing selected/all sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/vol_sets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/volstub.c -->
# sources/distributed-fs/openafs/src/bucoord/volstub.c

## Purpose
Provides small VLDB/volserver helper wrappers used by backup commands. It looks up VLDB entries by volume id and determines the timestamp to record for a volume image.

## Important APIs, Types, And Functions
Exports `bc_GetEntryByID` and `volImageTime`. `bc_GetEntryByID` wraps `ubik_VL_GetEntryByID`. `volImageTime` uses `UV_ListOneVolume` for non-RW volumes and interprets `struct volintInfo`.

## Control Flow
`bc_GetEntryByID` directly delegates to VLDB. `volImageTime` returns current time for RW volumes. For RO/BK or unknown requested types it asks the volserver for one volume’s info; RW results again use current time, RO/BK results use `creationDate`, and unknown types return an error after logging.

## State And Persistence
No state is stored and nothing is persisted. The returned clone/image time is written into caller-owned fields such as `bc_volumeDump.cloneDate`.

## Dependencies And Integration Points
Depends on VLDB Ubik stubs, volser/UV helpers, `volintInfo`, and com_err. `commands.c` calls `volImageTime` during dry-run incremental dump checks to warn when a volume timestamp did not change.

## Risks And Test Signals
`UV_ListOneVolume` allocation ownership is not released in this function, which may leak depending on API contract. Returning success with clone date `0` on query failure intentionally lets dump planning continue with a warning. Test signals include RW current-time behavior, backup/readonly creation-date behavior, volserver query failure warning, unknown volume type failure, and VLDB lookup by id/type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/volstub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/Makefile.in -->
# sources/distributed-fs/openafs/src/budb/Makefile.in

## Purpose
Defines the Autoconf make rules for building and installing the OpenAFS backup database client library, generated BUDB RPC/error headers, generated RX stubs, and the `budb_server`/`buserver` binary.

## Important APIs, Types, And Functions
Key variables are `INCLS`, `LIBS`, `COMMON_OBJS`, and `SERVER_OBJS`. Major targets are `all`, `generated`, `${TOP_LIBDIR}/libbudb.a`, installed headers under `${TOP_INCDIR}/afs`, `budb_errs.[ch]`, generated `budb.cs.c`, `budb.ss.c`, `budb.xdr.c`, `budb.h`, `libbudb.a`, `budb_server`, `install`, `dest`, and `clean`.

## Control Flow
The default target builds the static client library, installs generated headers into the object include tree, and links `budb_server`. Error table sources come from `budb_errs.et` via `COMPILE_ET_*`. RPC sources and headers come from `budb.rg` via `RXGEN` in client, server, xdr, and header modes. `libbudb.a` archives the error object, client stub, XDR object, struct operations, and component version object. `budb_server` links server/common objects with OpenAFS libraries in top-level-defined order. Install and dest targets copy libraries, headers, and the server binary to packaging/staging locations.

## State And Persistence
Build outputs are generated `.c/.h`, object files, `libbudb.a`, and `budb_server`. Installation persists artifacts under configured lib/include/server-libexec directories or legacy `${DEST}` staging paths. `clean` removes generated stubs, generated headers, archive, objects, core, server binary, and component version file.

## Dependencies And Integration Points
Depends on top object configuration includes, `Makefile.lwp`, RXGEN, compile_et, top-level library layout, generated `AFS_component_version_number.c`, BUDB source files, and many OpenAFS libraries (`libbubasics`, audit, prot, kauth, ubik, auth, rxkad, sys, rx, lwp, cmd, com_err, util, opr, crypto helpers). The generated headers are consumed by `bucoord` and other backup components.

## Risks And Test Signals
Library ordering is manually encoded and can break link resolution. Generated-file dependencies must be correct for parallel builds. The `all` target expects generated headers and library installation into `${TOP_INCDIR}`/`${TOP_LIBDIR}` before downstream consumers build. Test signals include clean-tree parallel `make generated`, `make all`, relink after touching `budb.rg` and `budb_errs.et`, install/dest staging, and `make clean` removing generated outputs without removing source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/Makefile.in -->
