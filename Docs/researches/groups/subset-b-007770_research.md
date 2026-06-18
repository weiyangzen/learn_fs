# Research: subset-b-007770

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/dump.c -->
# sources/distributed-fs/openafs/src/butc/dump.c

## Purpose
`dump.c` implements the tape-coordinator dump path for OpenAFS Backup: it creates BUDB dump/tape/volume records, streams volume dumps from volservers over Rx, writes volume headers/data/trailers to the configured tape module or XBSA backend, handles multi-pass retry behavior, tape changes, append mode, and XBSA dump deletion. It is the producer side for the tape format later consumed by `lwps.c`, `recoverDb.c`, and `read_tape.c`.

## Important APIs, Types, and Functions
- `struct dumpRock` is the dump worker's private state: current tape sequence/name/label, current volume index/status/start position, BUDB dump/tape entries, counters, and the active `dumpNode`.
- `calcExpirationDate()` converts backup expiration policy (`BC_REL_EXPDATE`, `BC_ABS_EXPDATE`, `BC_NO_EXPDATE`) into an absolute `Date`.
- `Bind()` caches one Rx volserver connection keyed by server address; `ListOneVolume()` wraps `AFSVolListOneVolume()` and enforces exactly one result.
- `dumpVolume()` is the file/tape dump implementation. It opens a volserver transaction, starts `StartAFSVolDump()`, writes `TC_VOLBEGINMAGIC` and `TC_VOLENDMAGIC` headers, fragments volumes across tapes when near EOT, and queues BUDB volume rows via `addVolume()`.
- `xbsaDumpVolume()` is the XBSA analogue, wrapping `xbsa_BeginTrans()`, `xbsa_WriteObjectBegin/Data/End()`, and recording a single BUDB volume fragment for each volume object.
- `dumpPass()` iterates all volumes for a retry pass, refreshes VLDB location for later passes, decides retry/omit/abort/EOT behavior, and calls `flushSavedEntries()` after each volume action.
- `Dumper()` is the asynchronous worker entry point. It owns the device latch, creates the dump row, mounts or synthesizes tape state, runs up to `maxpass`, writes final EOD, finishes tape/dump rows, logs status, frees the task node, and releases the device.
- `getDumpTape()` is the tape acquisition and safety gate. It validates labels, append eligibility, expiration, parent/latest-dump overwrite risks, rewrites labels, deletes overwritten dumps from BUDB, calls `useTape()`, and computes EOT margins.
- `makeVolumeHeader()` and `volumeHeader_hton()` define the on-tape volume header/trailer fields and byte order.
- Under `#ifdef xbsa`, `InitToServer()` switches XBSA servers and `DeleteDump()` deletes XBSA objects listed in BUDB.

## Control Flow
1. `tcprocs.c` creates a `dumpNode`, status node, and detached `Dumper`.
2. `Dumper()` takes `deviceLatch`, initializes `butm_tapeInfo` unless XBSA, allocates the data buffer, finds the previous dump, and calls `createDump()`.
3. For tape output, `getDumpTape()` prompts/mounts/labels the tape; for XBSA, `getXBSATape()` creates BUDB-compatible tape metadata.
4. Each `dumpPass()` walks remaining volumes. Pass 1 uses the supplied host/partition; later passes requery VLDB and recompute incremental dates from the parent dump.
5. `dumpVolume()` or `xbsaDumpVolume()` starts a volserver transaction, streams data through Rx, periodically updates status and checks aborts, writes a trailer, ends transport state, then queues `addVolume()`.
6. `dumpPass()` flushes saved DB entries according to the action. EOT can finish the current tape and retry on a new tape; final-pass failures can prompt retry/omit/abort.
7. `Dumper()` writes EOD, calls `finishTape()` and `finishDump()`, flushes database entries, waits for the DB watcher, logs outcome, marks status, frees the node, and releases the device.

## State and Persistence Behavior
- Persistent state is split between physical tape/XBSA objects and BUDB rows. The code deliberately writes media data first, then records volume fragments in BUDB to avoid advertising unwritten data as restorable.
- BUDB updates are queued in `savedEntries` by `useTape()`, `addVolume()`, `finishTape()`, and `finishDump()`, then moved to the DB watcher by `flushSavedEntries(action)`. Failed or partial volume entries are discarded or marked based on `action`.
- Tape labels store dump path, dump id, use count, creation/expiration, cell, and naming data. Append labels use the appended dump id, while beginning-of-tape labels can use the initial dump id.
- Runtime state lives in global knobs initialized by `tcmain.c`: `BufferSize`, `statusSize`, `maxpass`, `dump_namecheck`, `autoQuery`, `queryoperator`, `isafile`, `groupId`, and XBSA configuration.
- `lastPass` is global and affects logging to the last-pass log; `curr_fromconn` caches a volserver connection until `Bind(0)` in cleanup.

## Dependencies and Integration Points
- Volserver/Rx: `UV_Bind`, `AFSVolTransCreate`, `StartAFSVolDump`, `rx_Read`, `rx_EndCall`, and `AFSVolEndTrans`.
- VLDB/backup DB: `bc_GetEntryByID`, `bcdb_FindClone`, `bcdb_FindLatestDump`, `bcdb_CreateDump`, `bcdb_FindLastTape`, `bcdb_deleteDump`, `bcdb_MakeDumpAppended`, and the queued DB entry helpers from `dbentries.c`.
- Tape module: `butm_file_Instantiate`, `butm_Mount`, `butm_ReadLabel`, `butm_Create`, `butm_WriteFileBegin/Data/End`, `butm_WriteEOT`, `butm_remainingKSpace`, `butm_SeekEODump`.
- Operator/device support from `lwps.c`: `PromptForTape()`, `unmountTape()`, `tapeExpired()`, `ExpirationDate()`, and `databaseTape()`.
- Task/status lifecycle uses `setStatus`, `clearStatus`, `checkAbortByTaskId`, `FreeNode`, and `deviceLatch`.
- XBSA builds integrate with `butc_xbsa.h`, `butxInfo`, and BUDB dump flags such as `BUDB_DUMP_ADSM` and `BUDB_DUMP_XBSA_NSS`.

## Risks and Edge Cases
- The dump-node list in `list.c` is not locked here; correctness relies on RPC worker creation/completion not racing in unsafe ways.
- Several `strcpy()` calls copy external or DB-derived names into fixed fields; risk is bounded by AFS struct limits but still depends on upstream validation.
- EOT behavior is subtle: position `2` marks `DUMP_NORETRYEOT`, while later EOT marks retry and may finish the tape. Tests need physical/file-tape simulations for near-margin cases.
- Append mode has many safety checks, but it deletes old BUDB dumps after relabeling new media. Power loss between media and DB updates can create reconciliation work.
- XBSA error cleanup can end write objects/transactions but comments note uncertainty around partial server objects not recorded in BUDB.
- `at` style operator prompting can block indefinitely unless abort flags or callout failures are exercised.
- `curr_fromconn` is global and would be unsafe for true concurrent dump volume streams; the single device latch reduces but does not fully document that assumption.

## Test Signals
- Unit-level: `calcExpirationDate()`, `volumeHeader_hton()`, `makeVolumeHeader()`, tape-name sequence extraction interactions, and EOT margin math.
- Integration: file-tape dump of full and incremental volumes, multi-volume dump, unchanged volume handling, retry/omit/abort on final pass, and continuation across two tapes.
- Persistence: after each successful dump, verify BUDB dump/tape/volume rows match tape positions and byte counts; after failed/partial dumps, verify no restorable phantom volume rows remain.
- Safety: append to last tape, reject database tapes, reject non-expired tapes unless operator override, reject overwriting parent dump, and warn on latest-dump overwrite.
- XBSA: successful dump/delete, failed write cleanup, server-switch handling, and compatibility flags for ADSM/BUTA/NSS dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/error_macros.h -->
# sources/distributed-fs/openafs/src/butc/error_macros.h

## Purpose
`error_macros.h` centralizes the local `goto`-based error-exit idiom used throughout `butc` and declares cross-file helper functions used by dump, restore, label, scan, and RPC paths. It is intentionally small but structurally important because many functions rely on a local `code` variable and specific cleanup labels.

## Important APIs, Types, and Functions
- `ERROR_EXIT(evalue)` assigns `code = evalue` and jumps to `error_exit`.
- `ERROR_EXIT2(evalue)` assigns `code = evalue` and jumps to `error_exit2`; this supports functions with nested cleanup paths.
- `ABORT_EXIT(evalue)` assigns `code = evalue` and jumps to `abort_exit`; dump code uses this to distinguish normal cleanup from states that should mark the current volume as failed.
- Logging prototypes: `ErrorLog()`, `TapeLog()`, and `TLog()` with printf format checking.
- Task/device prototypes: `FreeNode()`, `CreateNode()`, `EnterDeviceQueue()`, `LeaveDeviceQueue()`, `ExpirationDate()`, `InitNodeList()`, `clearStatus()`, and `setStatus()`.

## Control Flow
This header does not own runtime flow itself; instead, it standardizes cleanup flow in C functions that allocate memory, hold devices, open Rx calls, start volserver or XBSA transactions, or create status nodes. Functions using these macros must define `afs_int32 code` or compatible `code` before invocation and provide the referenced label.

## State and Persistence Behavior
The macros mutate only the local `code` variable. The declared functions affect persistent and runtime state elsewhere: task-node lists, device locks, status flags, logs, and expiration lookup from BUDB.

## Dependencies and Integration Points
- Included by most `butc` implementation files and implicitly depends on AFS integer/date types and `struct dumpNode`/`struct deviceSyncNode` declarations being visible from earlier includes.
- Logging declarations are implemented in `lwps.c`.
- node/device declarations are implemented in `list.c` and `lwps.c`.
- status functions are implemented in the shared `bucoord/status.c` linked into `butc`.

## Risks and Edge Cases
- The macros silently require a local `code` variable and matching labels; misuse fails at compile time, but incorrect label choice can skip required cleanup.
- `ABORT_EXIT` is semantically overloaded: in `dump.c`, it marks current volume failure before falling through to normal error cleanup. New call sites must preserve that distinction.
- Prototypes here create broad cross-file coupling and can hide missing dedicated public headers.

## Test Signals
- Build coverage is the primary signal: all macro call sites must compile with their local labels.
- Static analysis should flag any function invoking these macros without initializing `code` or without cleanup of resources acquired before the jump.
- Behavior tests should verify abort paths mark status and cleanup differently from ordinary errors in dump/restore/scan workers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/error_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/list.c -->
# sources/distributed-fs/openafs/src/butc/list.c

## Purpose
`list.c` maintains the in-memory list of active `butc` task nodes (`struct dumpNode`). These nodes carry dump or restore parameters from the RPC stubs to asynchronous workers and are used for task id lookup.

## Important APIs, Types, and Functions
- Static globals: `headNode` dummy header, `dumpQHeader` pointer to the header, and `maxTaskID`.
- `InitNodeList(portOffset)` initializes the list and seeds task ids as `(portOffset * 1000) + 1`, giving each tape coordinator port a distinct task-id range.
- `allocTaskId()` returns and increments `maxTaskID`.
- `CreateNode()` allocates a zeroed `dumpNode`, inserts it at the list front, and assigns a new task id.
- `FreeNode(taskID)` unlinks the matching node and frees `dumpName`, `volumeSetName`, `restores`, `dumps`, and the node itself.
- `GetNthNode(index, result)` maps a zero-based list index to a task id.
- `GetNode(taskID, resultNode)` looks up a task node by id.

## Control Flow
`tcmain.c` calls `InitNodeList()` during startup. RPC handlers in `tcprocs.c` call `CreateNode()` before starting worker threads/LWPs. Worker completion paths in `dump.c` and `lwps.c` call `FreeNode()`. Lookup helpers are available to status or coordination code that needs to discover active tasks.

## State and Persistence Behavior
All state is process-local and volatile. Task ids are monotonically increasing within a process and are never reused until restart. The file does not persist anything to BUDB or tape; it owns only heap allocations for the request parameter arrays and strings that workers consume.

## Dependencies and Integration Points
- Depends on `struct dumpNode`, `struct tc_dumpDesc`, and `struct tc_restoreDesc` from AFS backup/tape headers.
- Error integration is limited to returning `TC_NODENOTFOUND` or `ENOENT`; allocation uses `opr_Assert()`.
- Called by `tcprocs.c`, `dump.c`, and `lwps.c`.

## Risks and Edge Cases
- There is no explicit lock around list insertion, removal, or traversal. In pthread builds, concurrent RPC creation/completion could race unless higher-level serialization is guaranteed elsewhere.
- `CreateNode()` asserts on allocation failure instead of returning an error, unlike many other `butc` paths.
- `FreeNode()` silently does nothing if the task id is absent; double-free attempts become no-ops after the first removal.
- `GetNode()` starts at the dummy header and could return it if asked for task id `-1`; normal callers should never request that id.

## Test Signals
- Create/free sequences should leave the list traversable and release nested arrays/strings.
- Port offset seeding should produce expected first task ids for several offsets.
- Concurrent stress under pthread builds would be valuable because no internal synchronization is present.
- Error paths in RPC handlers should verify `FreeNode()` is called after failed worker creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/lwps.c -->
# sources/distributed-fs/openafs/src/butc/lwps.c

## Purpose
`lwps.c` implements most tape-coordinator worker-side support outside the dump producer: logging, exclusive device access helpers, operator/callout prompting, tape unmounting, restore from tape or XBSA, tape labeling, label reading, tape expiration checks, and volume-header/trailer parsing. Despite the filename, it supports both LWP and pthread builds.

## Important APIs, Types, and Functions
- Logging: `PrintLogStr()`, `TapeLogStr()`, `TapeLog()`, `TLog()`, `ErrorLogStr()`, `ErrorLog()`, and `ELog()`.
- Device serialization: `EnterDeviceQueue()` and `LeaveDeviceQueue()` set `TC_DEVICEINUSE` under `deviceLatch->lock`.
- Operator interaction: `FFlushInput()`, `callOutRoutine()`, `PromptForTape()`, and `unmountTape()` support external mount/unmount scripts and console prompts with abort checks.
- Restore structures: `struct restoreParams` carries the current `dumpNode`, fragment index, mounted tape name/id, and tape info.
- Tape restore: `GetRestoreTape()`, `GetVolumeHead()`, `restoreVolume()`, `restoreVolumeData()`, `SkipTape()`, `SkipVolume()`, and `Restorer()`.
- XBSA restore: `xbsaRestoreVolume()` and `xbsaRestoreVolumeData()` read volume objects and stream them to `UV_RestoreVolume()`.
- Label management: `GetNewLabel()`, `updateTapeLabel()`, `Labeller()`, `PrintTapeLabel()`, and `ReadLabel()`.
- Format parsing: `VolHeaderToHost()`, `ReadVolHeader()`, `ExtractTrailer()`, `FindVolTrailer()`, `FindVolTrailer2()`, and `readVolumeHeader()`.
- Expiration helpers: `ExpirationDate()` consults BUDB for dump-set tape expiration; `tapeExpired()` compares that or label expiration to current time.

## Control Flow
Restore RPCs create a `dumpNode` and start `Restorer()`. `Restorer()` takes the device latch, instantiates the tape module unless XBSA, allocates buffers, iterates restore descriptors, mounts/seeks required tapes, and calls `UV_RestoreVolume()` with a callback that streams tape/XBSA data into the volserver restore call. Multi-fragment volumes advance across tape descriptors when trailers indicate continuation.

Label RPCs start `Labeller()`, which creates a new label, prompts/mounts media, validates permanent-name and expiration rules, writes the label with `butm_Create()`, and deletes obsolete BUDB dump records for overwritten labeled media. `ReadLabel()` is synchronous: it obtains the device, prompts/mounts, reads and prints the label, fills the RPC-visible `tc_tapeLabel`, and releases the device.

## State and Persistence Behavior
- Runtime globals include log file handles, `lastPass`, `debugLevel`, `autoQuery`, `globalTapeConfig`, `deviceLatch`, `globalCellName`, `BufferSize`, `dataSize`, `tapeblocks`, `bufferBlock`, and optional XBSA `butxInfo`.
- Restore writes persistent volume data through volserver calls; optional `restoretofile` also writes raw data to a local file for XBSA debugging.
- Labeling writes persistent tape labels and can delete old BUDB dump entries when overwriting labels from tape version 3 or later.
- Status nodes are updated with current volume name, kilobytes restored, wait flags, abort flags, task done, and errors.
- Logs are written to tape, error, last-pass, central log, stdout depending on debug and mode.

## Dependencies and Integration Points
- Tape module: `butm_Mount`, `butm_Dismount`, `butm_ReadLabel`, `butm_ReadFileBegin/Data/End`, `butm_Seek`, `SeekFile`, `NextFile`, `butm_Create`, and size APIs.
- Volserver restore: `UV_RestoreVolume()` consumes callbacks implemented here.
- BUDB: `bcdb_FindDumpByID`, `bcdb_FindLastTape`, `bcdb_deleteDump`, and dump flags for XBSA/BUTA compatibility.
- Process management: `spawnprocve`, `waitpid`, `kill`, `sleep`/`IOMGR_Sleep` for callout scripts.
- Shared status/list/device helpers: `checkAbortByTaskId`, `setStatus`, `clearStatus`, `FreeNode`, and `deviceLatch`.
- Tape format must match `dump.c`'s `makeVolumeHeader()`/`volumeHeader_hton()` and `read_tape.c`'s standalone parser.

## Risks and Edge Cases
- The file uses fixed-size buffers and many `strcpy()`/`sprintf()` calls for tape names, command arguments, and paths; correctness depends on AFS maximums and config validation.
- `EnterDeviceQueue()` is a write lock held across long operator prompts and media I/O; this serializes all device work and can block unrelated tasks.
- Callout scripts are killed on abort but may leave external device state inconsistent.
- Trailer detection handles alignment differences by scanning for preamble/postamble, but malformed data near the end of a block can lead to missing-trailer errors or skipped restore data.
- `VolHeaderToHost()`'s version-0 branch appears suspicious: it copies in the opposite direction (`memcpy(tapeVolHeader, hostVolHeader, ...)`) rather than into `hostVolHeader`.
- Restore failure policy skips remaining fragments of a failed volume, and `TC_SKIPTAPE` skips all volumes on that tape; operators need clear logs to understand partial restores.
- Optional `restoretofile` is global and not synchronized for multiple restores.

## Test Signals
- Tape restore with single-fragment, multi-fragment, and missing-trailer volumes.
- Header parser tests for all supported tape versions and host/tape alignment cases.
- Prompt/callout behavior for success, abort, skip-tape exit code, failing script fallback, and closecallout during unmount.
- Label update tests for unexpired tapes, permanent-label preservation, null permanent label, overwritten dump deletion, and BUDB expiration lookup.
- XBSA restore with server switch allowed/disallowed, BUTA-style object names, missing objects, and `restoretofile` enabled.
- Status polling during long restore should show current volume and byte progress, and abort requests should propagate within `BIGCHUNK` intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/lwps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/read_tape.c -->
# sources/distributed-fs/openafs/src/butc/read_tape.c

## Purpose
`read_tape.c` is a standalone command-line utility for scanning OpenAFS backup tapes and optionally restoring volume dump data to local files. It understands the low-level file tape module block format directly via `usd`, independent of the `butc` RPC service.

## Important APIs, Types, and Functions
- Globals control scan/restore behavior: `nrestore`, `nskip`, `ask`, `printlabels`, `printheaders`, `verbose`, `outfile`, `fd`, `ofd`, and `ofdIsOpen`.
- Local format mirrors `file_tm.c`: `TAPE_MAGIC`, `BLOCK_MAGIC`, `FILE_MAGIC`, `FILE_BEGIN`, `FILE_END`, `FILE_EOD`, `struct tapeLabel`, and `struct fileMark`.
- `readblock()` reads one 16 KiB tape block, treating repeated zero-length reads as hardware file marks and end-of-dump.
- `printLabel()` byte-swaps and displays `butm_tapeLabel` metadata.
- `printHeader()` byte-swaps and displays volume header/trailer metadata, identifying `TC_VOLBEGINMAGIC` and `TC_VOLENDMAGIC`.
- `openOutFile()` decides whether to restore a volume, derives an output filename, prompts unless `-noask`, opens/truncates or appends using `usd`.
- `writeData()`, `writeLastBlocks()`, and `closeOutFile()` write volume data while stripping the trailing volume trailer.
- `WorkerBee()` parses command options, opens the tape device, cycles three tape-block buffers, identifies labels/filemarks/data blocks, prints scan output, and restores selected volumes.

## Control Flow
`main()` registers command options and dispatches to `WorkerBee()`. The worker opens the tape device read-only, allocates three 16 KiB buffers, then loops until all requested skips/restores are exhausted or reads fail. Data blocks are classified by magic fields. A volume begin header opens the output file and resets trailing-block state; ordinary data blocks are delayed by up to two blocks so the final trailer can be stripped once a non-data block marks the file boundary. Filemarks and labels close any open volume output.

## State and Persistence Behavior
- The utility reads tape state but does not modify tape media or BUDB.
- It writes local restored files through `usd_Open`, `USD_WRITE`, and `USD_IOCTL_SETSIZE`. A continuation fragment appends/open-readwrite, while a new volume truncates the output file.
- `printLabel()` and `printHeader()` mutate the in-buffer structures by converting fields in place from network to host order; the same block should not be parsed again as network-order data.

## Dependencies and Integration Points
- Depends on the OpenAFS `usd` abstraction for device/file I/O and `cmd` for option parsing.
- Depends on tape/volume structures and constants from `afs/tcdata.h`.
- The format expectations align with `dump.c` volume headers/trailers and `butm` file-tape block/filemark layout.

## Risks and Edge Cases
- The code assumes data blocks have the file-tape block mark at the front and volume header data immediately after `struct blockMark`.
- Trailer stripping is heuristic: it removes all but the last 12 bytes of `struct volumeHeader` and searches for `H++NAME#`; malformed or alignment-shifted trailers can cause data loss or leave trailer bytes in output.
- `filename[100]` can overflow if volume names or `-file` are too long.
- `-noask` semantics are counterintuitive in the help text: `ask = (as->parms[5].items ? 0 : 1)`.
- `readblock()` treats more than three hardware file marks as done; unusual devices may surface different EOF behavior.
- `printHeader()` does not validate version flags or postamble before byte-swapping fields.

## Test Signals
- Scan-only against a file-tape image with labels, begin/end filemarks, EOD, and multiple volumes.
- Restore first, skip N, restore count N, and fixed `-file` behavior.
- Trailer-spanning cases where the trailer is in one block, spans two blocks, or the volume fits in a single block.
- Bad magic, short reads, repeated filemarks, and malformed headers should not crash or overwrite unintended files.
- Compare extracted files with `butc`/volserver restore stream for the same tape image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/read_tape.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/recoverDb.c -->
# sources/distributed-fs/openafs/src/butc/recoverDb.c

## Purpose
`recoverDb.c` implements `ScanDumps`, the tape-scanning worker used to inspect backup tapes and optionally reconstruct BUDB dump/tape/volume records from the media. It validates tape labels, reads volume headers/trailers, follows multi-tape and appended dump sets, and uses the same queued DB-entry path as live dumps when `addDbFlag` is set.

## Important APIs, Types, and Functions
- `struct tapeScanInfo` carries current tape label, dump label, reconstructed dump entry, initial dump id, and whether to add records to BUDB.
- `PrintDumpLabel()` and `PrintVolumeHeader()` display label/header metadata.
- `Ask()` prompts yes/no using `FFlushInput()` and a bell.
- `scanVolData()` reads one tape volume file, finds the volume trailer, returns volume header/trailer and payload byte count, and handles old tape versions that infer EOD from read errors.
- `nextTapeLabel()` increments the trailing sequence component of a tape name.
- `readDump()` scans all volumes in one dump, queues dump/tape/volume BUDB records when enabled, validates fragment continuity, handles continuation tapes, and finishes tape/dump rows.
- `readDumps()` scans a dump and then appended dumps by reading subsequent labels on version-4+ tapes.
- `getScanTape()` prompts/mounts media and validates non-null, non-database, name/id-matching tape labels.
- `ScanDumps()` is the asynchronous worker entry point.
- Name helpers: `validatePath()`, `volumesetNamePtr()`, `extractDumpName()`, `extractTapeSeq()`, and `databaseTape()`.
- `RcreateDump()` reconstructs a BUDB dump entry from the scanned tape label and volume header.

## Control Flow
`tcprocs.c` starts `ScanDumps()` with `addDbFlag`. The worker obtains the device latch, instantiates the tape module, mounts an initial scan tape, and calls `readDumps()`. `readDumps()` saves the first label as the dump label, calls `readDump()`, then checks for appended dump labels on version-4+ tapes. `readDump()` repeatedly calls `scanVolData()` for each volume, optionally creates the dump row and tape row on first valid records, queues volume rows, flushes complete volumes, follows continued volumes to the next expected tape, and finally finishes the reconstructed dump.

## State and Persistence Behavior
- Without `addDbFlag`, the worker prints scan output and uses only runtime state.
- With `addDbFlag`, it persists reconstructed BUDB dump/tape/volume entries through `RcreateDump()`, `useTape()`, `addVolume()`, `finishTape()`, `finishDump()`, and `flushSavedEntries()`.
- Fragment continuity state is held in a local `budb_volumeEntry volEntry`; incomplete fragments trigger `flushSavedEntries(DUMP_FAILED)` so partial volume rows are not committed as successful.
- `tapepos` is a file-global storing label position for tape entries.
- Scan tasks update status flags for drive wait, abort done, errors, and task done.

## Dependencies and Integration Points
- Tape APIs: `butm_file_Instantiate`, `butm_Mount`, `butm_ReadLabel`, `butm_ReadFileBegin/Data/End`, `NextFile`, and unmount handling from `lwps.c`.
- Format parsing from `lwps.c`: `ReadVolHeader()`, `FindVolTrailer()`, `FindVolTrailer2()`.
- DB queue helpers from `dbentries.c` and BUDB client calls through `bcdb_CreateDump`.
- Naming and database-tape helpers are used by both scanning and dump/restore prompt logic.
- Operator prompting and abort checks use `PromptForTape`, `Ask`, `checkAbortByTaskId`, and status helpers.

## Risks and Edge Cases
- Reconstructing DB state from media trusts tape headers for dump id, level, parent id, volume set, and clone date. Bad or forged tapes can create misleading BUDB records if allowed.
- `nextTapeLabel()` and `extractTapeSeq()` assume a final dotted numeric component; custom tape formats without that shape cannot be followed automatically.
- Old tape versions infer EOD from read errors, which can mask media damage as normal termination.
- The code accepts any initial tape when no name is supplied, but rejects database tapes and null/bad names; operator workflows need clear prompts.
- `validatePath()` only checks string shape and final component match, not full path authorization.
- Several fixed buffers and `strcpy()` calls rely on AFS max lengths.

## Test Signals
- Scan without DB add for single-tape, multi-tape, appended, and old-version tape images.
- DB add should create exactly one dump row, one row per tape, and volume rows with correct first/last fragment flags and positions.
- Corrupt or missing trailer should skip/mark incomplete volume and not commit it as successful.
- Continuation tape flow should prompt for the incremented tape name and reject mismatched label ids.
- Database-tape labels, null labels, and malformed sequence names should be rejected.
- Abort during `scanVolData()` should mark `ABORT_DONE`, unmount, wait for DB watcher, and release the device latch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/recoverDb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcmain.c -->
# sources/distributed-fs/openafs/src/butc/tcmain.c

## Purpose
`tcmain.c` is the executable entry point for the OpenAFS tape coordinator (`butc`). It parses command-line and tape configuration, initializes logs, authentication/auditing, Rx service security, VLDB/BUDB clients, global tape/XBSA settings, status and task lists, then starts the TC RPC service.

## Important APIs, Types, and Functions
- Global configuration: log paths/handles, `globalTapeConfig`, `deviceLatch`, `globalCellName`, `dump_namecheck`, `queryoperator`, `autoQuery`, `isafile`, `opencallout`, `closecallout`, `restoretofile`, `maxpass`, `groupId`, `statusSize`, `BufferSize`, `centralLogFile`, `lastLog`, `rxBind`, `butc_confdir`, and `allow_unauth`.
- `SafeATOL()` parses unsigned decimal integers with rejection of non-digits.
- `atocl()` parses sizes with B/K/M/G/T units and converts to a requested unit with rounding and 2 GiB saturation.
- `stringNowReplace()` appends a sanitized device name to log/config prefixes.
- `GetDeviceConfig()` reads `tapeconfig` entries for capacity, filemark size, device, and port offset.
- `GetConfigParams()` reads `CFG_<port>` or `CFG_<device>` and applies operational settings including mount scripts, ask/autoquery, buffer/status sizes, XBSA credentials/server/type, max pass count, group id, last/central logs.
- `tc_IsLocalRealmMatch()` integrates audit user checks with local realm matching.
- `WorkerBee()` performs nearly all process initialization and starts Rx.
- `main()` registers command syntax, initializes AFS paths, builds default backup path prefixes, handles no-argument defaults, and dispatches.

## Control Flow
`main()` defines the command interface and resolves server directory paths. `WorkerBee()` initializes error tables, parses port/debug/cell/device/auth flags, selects tape or XBSA mode, loads config, opens logs, initializes audit, optionally initializes XBSA, opens the AFS server config directory, initializes Rx on `BC_TAPEPORT + portOffset`, initializes VLDB and BUDB clients, creates the task-node list and device latch, builds Rx security objects, creates the `BUTC` service, checks BUDB permissions, initializes status, starts the DB watcher, logs startup, and donates the process to `rx_StartServer()`.

## State and Persistence Behavior
- It creates or appends operational logs (`TL_*`, `TE_*`, optional `*.lp`, and central log). If the central log is new, it writes a header and rejects central logs under `/afs/`.
- It does not itself write backup data or BUDB dump entries, but it initializes the clients and global state every worker depends on.
- `groupId` becomes the BUDB tape-set id for created dumps.
- `BufferSize` and `statusSize` shape data transfer size and progress logging frequency.
- Authentication state comes from `-localauth` or explicit `-allow_unauthenticated`; without one of these, startup refuses to continue.

## Dependencies and Integration Points
- AFS command, path, config, auth, audit, rx/rxkad, VLDB, BUDB, volserver, backup, and tape libraries.
- `tcprocs.c` provides `TC_ExecuteRequest` RPC dispatch through generated stubs and service handlers.
- `list.c`, `tcstatus.c`, `lwps.c`, `dump.c`, `recoverDb.c`, and `tcudbprocs.c` rely on globals initialized here.
- `dbWatcher` and queued DB-entry helpers are started here and used by dump/scan/save/restore DB workflows.
- XBSA builds depend on config-file-only parameters when no tapeconfig entry exists for the port.

## Risks and Edge Cases
- Configuration parsing uses fixed line buffers and simple `sscanf`; malformed or overlong lines can be rejected imprecisely.
- `PASSFILE` reads a password with `%s` into a `LINESIZE` allocation without a width specifier.
- `stringNowReplace()` mutates `deviceName` in place temporarily and assumes `storeDevice[256]` is large enough.
- `atocl()` accepts floats but uses 32-bit output and saturation, so large sizes may silently become `2147483647`.
- The secure-start behavior intentionally refuses startup unless `-localauth` or `-allow_unauthenticated` is provided; deployment tests must cover legacy scripts.
- `allow_unauth` creates only rxnull security, so firewall/topology assumptions become part of the security model.
- Many globals make multiple coordinator instances in one process impossible and complicate unit tests.

## Test Signals
- Startup with `-localauth`, with `-allow_unauthenticated`, and with neither.
- Tapeconfig parsing for old and new formats, missing entry causing XBSA mode, invalid port offsets, capacity/filemark units, and `-device` override.
- Config parsing for each supported directive, including ignored tape-only/XBSA-only directives and required XBSA parameters.
- Rx bind behavior with netinfo/netrestrict files and service creation.
- Log creation/appending, central log header creation, central log rejection under `/afs/`, and last-pass log opening.
- BUDB permission check should reject unauthenticated or unauthorized startup before accepting RPC work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcmain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcprocs.c -->
# sources/distributed-fs/openafs/src/butc/tcprocs.c

## Purpose
`tcprocs.c` implements the TC RPC service entry points that clients call to start tape-coordinator work. It performs permission checks, copies RPC/XDR arguments into process-owned heap state, creates status nodes, starts detached worker LWPs/pthreads, and audits each RPC.

## Important APIs, Types, and Functions
- `callPermitted()` allows all callers only in `allow_unauth` mode; otherwise it requires `afsconf_SuperIdentity()`.
- Copy helpers: `CopyDumpDesc()`, `CopyRestoreDesc()`, and `CopyTapeSetDesc()` translate XDR arrays/structures into local storage.
- RPC wrappers: `STC_LabelTape`, `STC_PerformDump`, `STC_PerformRestore`, `STC_ReadLabel`, `STC_RestoreDb`, `STC_SaveDb`, `STC_ScanDumps`, `STC_TCInfo`, and `STC_DeleteDump`.
- Static backend functions create workers: `SLabelTape()`, `SPerformDump()`, `SPerformRestore()`, `SReadLabel()`, `SRestoreDb()`, `SSaveDb()`, `SScanDumps()`, `STCInfo()`, and `SDeleteDump()`.
- Worker entry points are implemented elsewhere: `Labeller`, `Dumper`, `Restorer`, `restoreDbFromTape`, `saveDbToTape`, `ScanDumps`, and `DeleteDump`.

## Control Flow
Each public `STC_*` wrapper calls the corresponding static `S*` implementation and then emits an audit event with the result. Worker-starting `S*` functions check permissions and mode compatibility, allocate a task id or task node, allocate/copy request structures, create and initialize a status node with `STARTING` cleared, then start a detached pthread or LWP. On worker creation failure, they delete the status node and free the task state.

Synchronous `SReadLabel()` is the exception: it zeroes the output label, checks permissions, and calls `ReadLabel()` directly, returning no real task id.

## State and Persistence Behavior
- Creates volatile `dumpNode` and status-node state consumed by background workers.
- Does not directly write tape media or BUDB dump rows. Persistence happens in worker bodies after RPC return.
- Audit events persist through the configured audit subsystem.
- Task ids returned to clients are the handles for `tcstatus.c` polling/abort/end-status calls.

## Dependencies and Integration Points
- Requires `butc_confdir` and `allow_unauth` initialized by `tcmain.c`.
- Uses `list.c` for `CreateNode()`/`FreeNode()` and `allocTaskId()`.
- Uses shared status functions from `bucoord/status.c`.
- Integrates with `tcstatus.c` because every asynchronous task must publish a status node.
- Mode gates prevent tape-only operations when `CONF_XBSA` is true and prevent XBSA delete when not in XBSA mode.
- Uses `osi_auditU()` event constants for observability.

## Risks and Edge Cases
- Copy helpers use `strcpy()` into fixed fields; malformed oversized RPC strings could overflow if XDR layer does not enforce max lengths.
- Several allocations are not checked before copy in older-style paths, or are cleaned up by broad `ERROR_EXIT` only after partial setup.
- Status nodes are initialized while holding the status lock, but task-node list insertion is not locked here.
- RPC returns success once worker creation succeeds, not when the operation succeeds; clients must poll status.
- `ReadLabel()` allocates a task id internally for lower-level logging even though the RPC returns task id 0.
- Some comments say parameter validity "should" be verified; validation is mostly deferred to workers.

## Test Signals
- Permission matrix for authenticated superuser, non-superuser, and `-allow_unauthenticated`.
- Worker-spawn tests for every RPC should verify task id, task name, `STARTING` cleared, and cleanup on simulated spawn failure.
- Mode tests: label/readlabel/saveDB/restoreDB/scandump rejected under XBSA, delete rejected without XBSA.
- Argument-copy tests for dump arrays, restore arrays, tape sets, append flag under XBSA, and zero-length arrays.
- Audit tests should see one event per public RPC with returned code and task id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcstatus.c -->
# sources/distributed-fs/openafs/src/butc/tcstatus.c

## Purpose
`tcstatus.c` implements the TC RPC status interface: clients can poll a task, scan all active tasks, request abort, and end/delete a status node. It also provides local helper functions for worker code to check abort/status flags.

## Important APIs, Types, and Functions
- Globals: `statusHead`, `statusQueueLock`, and `cmdLineLock`; actual initialization and status-node creation/deletion are supplied by shared `bucoord/status.c`.
- Public RPC wrappers with audit: `STC_GetStatus()`, `STC_EndStatus()`, `STC_RequestAbort()`, and `STC_ScanStatus()`.
- Static implementations: `SGetStatus()`, `SEndStatus()`, `SRequestAbort()`, and `SScanStatus()`.
- Local helpers: `checkAbortByTaskId()` returns whether `ABORT_REQUEST` is set; `getStatusFlag()` tests arbitrary status flags for compatibility.

## Control Flow
Status RPCs first check `callPermitted()`. `SGetStatus()` locks the status queue, finds a task by id, copies fields into `tciStatusS`, refreshes `lastPolled`, and returns `TC_NODENOTFOUND` if absent. `SEndStatus()` finds and deletes a status node. `SRequestAbort()` sets `ABORT_REQUEST`. `SScanStatus()` returns the first or next status node depending on `TSK_STAT_FIRST`, sets `TSK_STAT_END` and `TSK_STAT_NOTFOUND` as appropriate, and annotates flags for XBSA/ADSM coordinator mode.

## State and Persistence Behavior
- State is volatile process memory only; it does not persist to BUDB or tape.
- Workers update status nodes with task names, volume names, progress bytes, failure counts, wait flags, done/error/abort flags, and DB dump id.
- `lastPolled` is refreshed on direct `GetStatus`, allowing external cleanup or clients to distinguish active polling.
- `RequestAbort` is cooperative: long-running workers must call `checkAbortByTaskId()` periodically to observe it.

## Dependencies and Integration Points
- Depends on `callPermitted()` from `tcprocs.c`, `CONF_XBSA` and `xbsaType` from the runtime configuration, and shared status/list primitives from `bucoord/status.c`.
- Worker code in `dump.c`, `lwps.c`, `recoverDb.c`, and DB save/restore paths uses `checkAbortByTaskId()` and status setters to coordinate cancellation and progress.
- Audit events expose status operations for security logging.

## Risks and Edge Cases
- `SEndStatus()` unlocks before deleting the found node; if another thread deletes or mutates it concurrently, that can race unless the shared status implementation tolerates it.
- `SScanStatus()` may end early if the set of tasks changes between calls; callers are expected to retry.
- `SScanStatus()` copies fewer fields than `SGetStatus()`; it omits `dbDumpId` and `volsFailed`, which can surprise clients.
- Abort is only checked at explicit worker polling points, so blocking tape I/O or callout scripts may delay cancellation.
- `statusHead`, `statusQueueLock`, and `cmdLineLock` are defined here to satisfy shared status code, creating a cross-module linkage contract.

## Test Signals
- Poll existing and missing task ids, verifying copied fields and `lastPolled` refresh.
- Request abort, then verify workers see `ABORT_REQUEST`, clear it, and set `ABORT_DONE` on abort completion.
- Scan status with no tasks, one task, multiple tasks, task deletion between scans, and XBSA/ADSM flag annotation.
- Permission checks should match all other TC RPCs.
- Race/stress tests around `EndStatus` while a worker exits would be valuable in pthread builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcstatus.c -->
