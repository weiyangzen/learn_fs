# Research: subset-b-007008

Grouped research for Coda client repair and server resolution sources. Each section preserves its source path for reconciliation into source-tree-aligned per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.cc -->
# sources/distributed-fs/coda/coda-src/repair/repair.cc

Purpose: command-line and interactive front end for Coda conflict repair. It owns global repair session state (`allowclear`, `session`, `repair_DebugFlag`, `ConflictObj`, `cfix`) and maps parser commands to library routines from `repcmds.h`/repair I/O.

Important APIs and flow: `main` initializes Coda configuration, installs the interrupt handler, handles the special `-remove <pathname>` path, supports a batch path for object/fixfile repair, and otherwise enters `Parser_commands`. `rep_BeginRepair` calls `BeginRepair`, classifies the conflict as directory or file, and exposes only relevant commands. `rep_CompareDirs` parses fix-file, ACL, owner, and mode options into `repinfo` and calls `CompareDirs`. `rep_DoRepair` calls `DoRepair`; `rep_RemoveInc` calls `RemoveInc`, ends the session, then removes the local object with `rmdir`/`unlink`; `rep_ReplaceInc` validates a replacement regular file and calls `dorep` after ending the repair session.

State/persistence: user-visible state is process-global and single-session only. Persistent changes happen through Venus/repair library calls and filesystem removal/replacement, not directly in this file.

Dependencies/integration: depends on Coda config (`venus.conf` mountpoint), parser library, token helpers, `BeginRepair`/`EndRepair`, `repair_getfid`, `CompareDirs`, `DoRepair`, `dorep`, and POSIX file operations.

Risks/test signals: header prototype for `getcompareargs` in `repair.h` is stale relative to this implementation. Several `strncpy` calls do not guarantee termination on max-length inputs. `rep_RemoveInc`/`rep_ReplaceInc` exit with `EXIT_FAILURE` even on successful repair, which may be historical but is surprising for scripts. Test with interactive begin/end, directory compare, file replace, invalid fixfile under `/coda`, SIGINT cleanup, and `-remove` on both file and directory conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.h -->
# sources/distributed-fs/coda/coda-src/repair/repair.h

Purpose: client-only repair tool interface. It defines repair session states, declares shared globals, declares parser command handlers, and provides the initial help text shown by the repair executable.

Important APIs/types: `NOT_IN_SESSION`, `FILE_SESSION`, and `DIRECTORY_SESSION` encode the active repair mode. `ConflictObj` is the active `struct conflict *` returned by `BeginRepair`; `allowclear`, `interactive`, `repair_DebugFlag`, and `session` are shared process flags. The declared command handlers are `rep_BeginRepair`, `rep_ClearInc`, `rep_CompareDirs`, `rep_DoRepair`, `rep_EndRepair`, `rep_Exit`, `rep_Help`, `rep_RemoveInc`, and `rep_ReplaceInc`.

Control flow/integration: included by `repair.cc`, and transitively exposes declarations from `repcmds.h`. It is a thin adapter header between the command parser and Coda repair library.

State/persistence: no storage is defined here, but declarations describe singleton process state used by the repair CLI. Persistence is delegated to the lower repair library and Venus kernel/user interfaces.

Dependencies: `repcmds.h` supplies `struct conflict` and repair command APIs. The signal handler declaration references `struct sigcontext`, making this header tied to legacy platform signal ABI assumptions.

Risks/test signals: the `getcompareargs` prototype accepts many `char **` parameters, but `repair.cc` implements `getcompareargs(int,char **,char **,struct repinfo *)`; this mismatch is a compile-time/API drift risk. `interactive` is declared but not defined in `repair.cc`, so its owner must be elsewhere or dead. Compile the repair tool with warnings enabled and exercise all parser command declarations against the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/reptest.cc -->
# sources/distributed-fs/coda/coda-src/repair/reptest.cc

Purpose: small standalone test utility for repair directory-file serialization. It parses a repair description file, writes the parsed replica lists to `/tmp/xxx`, reads them back, and prints the reconstructed lines.

Important APIs/control flow: `main` calls `repair_parsefile(argv[1], &hcount, &harray)`, then `repair_putdfile("/tmp/xxx", hcount, harray)`, then `repair_getdfile("/tmp/xxx", &newhc, &newha)`. It iterates each `listhdr`, prints the `replicaId`, and prints each repair line through `repair_printline`.

State/persistence: global `harray`, `hcount`, and `repair_DebugFlag` support the repair parser/library linkage. The only persistent side effect is the fixed temporary file `/tmp/xxx`, which can collide across test runs and users.

Dependencies/integration: pulls in Coda base headers, RPC2, `vice.h`, and `repio.h`. It is not part of runtime repair flow; it is a parser/serializer smoke test for `repio` data structures.

Risks/test signals: no `argc` validation before `argv[1]`; the include line `<rpc2/rpc2.h> */` appears malformed and may only survive if this file is not regularly built. The fixed temp path is unsafe for concurrent tests. A useful test signal is round-tripping a multi-replica repair file with several operations and checking printed output equals the original semantic content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/reptest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/Makefile.am -->
# sources/distributed-fs/coda/coda-src/resolution/Makefile.am

Purpose: Automake build recipe for the Coda server resolution support library. When `BUILD_SERVER` is true it builds `libres.la` as a non-installed libtool archive.

Important contents: `libres_la_SOURCES` enumerates the resolution subsystem: communication (`rescomm.*`), coordination (`rescoord.*`, `rvmrescoord.cc`), force/runt handling (`resforce.*`), lock/util/stats files, operation logs (`ops.*`, `recle.*`, `rsle.*`, `recov_vollog.cc`), conflict handlers (`ruconflict.*`, `rename.cc`, `subresphase*`, `subpreres.cc`), worker entry points (`weres.cc`), and public umbrella `resolution.h`.

Dependencies/integration: `AM_CPPFLAGS` includes RPC2/RVM flags plus Coda base, kernel dependency, util, vicedep, directory, ACL, partition, auth, version-vector, lockqueue, and volume headers. This makes resolution a server-side integration point across storage, RPC, vnode, ACL, and recovery layers.

State/persistence: no runtime state; build-time selection via `BUILD_SERVER` controls whether the library exists.

Risks/test signals: omissions in `libres_la_SOURCES` can hide source files from build and tests. Include path order matters because both source and build directories are used for generated headers. Test by regenerating with Automake/configure and building server with `BUILD_SERVER` enabled; watch for stale header prototypes across the listed sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.cc -->
# sources/distributed-fs/coda/coda-src/resolution/compops.cc

Purpose: computes compensating operations for directory resolution by comparing local and remote resolution logs for a specific `ViceFid`.

Important APIs/control flow: exported `ComputeCompOps(olist *AllLogs, ViceFid *Fid)` extracts the local host log with `ExtractLog(ThisHostAddr, Fid)`, extracts per-remote logs, sorts logs into `arrlist`s, finds each remote log's latest common non-resolution operation with the local log, collects entries after that common point as non-local operations, merges duplicate remote entries by `ViceStoreId`, removes operations already present locally, and sorts final compensating entries by host index and sequence number. `PrintCompOps` is the exported debug printer.

State/persistence: operates on in-memory parsed logs (`he`, `remoteloglist`, `rsle`) and returns an `arrlist` of existing `rsle *` pointers; it does not own or persist log entries.

Dependencies/integration: consumes log structures from `parselog.cc`, `rsle`, `resutil` host entries, global `ThisHostAddr`, `SrvDebugLevel`, and Coda container classes.

Risks/test signals: assumes sorted store IDs and uses pointer identity to locate common points in original remote lists. If no common point exists, resolution cannot proceed. Memory ownership is mixed: arrays are freed/deleted but returned entries belong to original logs. Test with multi-host logs containing duplicate store IDs, no common point, resolution opcodes interleaved with normal opcodes, and different sequence ordering per host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.h -->
# sources/distributed-fs/coda/coda-src/resolution/compops.h

Purpose: public interface for compensating operation computation during directory resolution.

Important APIs: `ComputeCompOps(olist *, ViceFid *)` returns an `arrlist *` of compensating `rsle` entries for a vnode based on all parsed logs. `PrintCompOps(arrlist *)` emits those entries for diagnostics.

Dependencies/integration: includes `olist`, `arrlist`, and `vcrcommon` for Coda list containers and `ViceFid`. Implemented by `compops.cc` and used by log-based resolution phases to determine which remote operations need replay or conflict handling.

State/persistence: no state of its own. The returned list is an in-memory selection/order over log entries owned elsewhere.

Risks/test signals: ownership of the returned `arrlist` is implied but not documented; callers must delete the list without deleting the underlying `rsle` records unless they own the parsed log buffer. Test callers for leaks and double frees when resolution aborts early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.cc -->
# sources/distributed-fs/coda/coda-src/resolution/ops.cc

Purpose: core resolution log operation support. It initializes/prints variable log-entry payloads, spools VM `rsle` intention records, copies them to recoverable `recle` records, truncates and purges per-vnode logs, and dumps logs for shipment.

Important APIs/control flow: payload classes (`aclstore`, `ststore`, `newstore`, `create_rle`, `symlink_rle`, `link_rle`, `mkdir_rle`, `rm_rle`, `rmdir_rle`, `rename_rle`, `setquota_rle`) provide `init`/`print`. `CreateRootLog` allocates the first recoverable root log record. `CreateResLog` creates an empty per-vnode log. `SpoolVMLogRecord` filters non-directories and disabled resolution, allocates a volume-log slot, builds an `rsle`, initializes it from varargs, and appends it to a vnode list entry. `SpoolRenameLogRecord` creates source and, for cross-directory renames, target parent records. `TruncateLog`, `PurgeLog`, and `FreeVMIndices` coordinate RVM and VM bitmap cleanup. `DumpLog` serializes tree-shaped logs into a buffer.

State/persistence: works across transient VM `rsle` lists and recoverable RVM `rec_dlist`/`recle` storage. Some functions require active RVM transactions; VM bitmap freeing is intentionally deferred until commit success.

Dependencies/integration: tightly integrated with `recov_vol_log`, vnode/volume structures, `resstats`, version vectors, ACL formatting, and `operations` semantics.

Risks/test signals: varargs spooling is type-fragile. `DumpLog` buffer growth loop assigns `newmaxsize = maxsize * 2` repeatedly, which can fail to grow enough for very large child dumps. `fdopen` in print routines may affect fd buffering ownership. Test log allocation exhaustion, wraparound, recursive child logs, rename with deleted directory target, and truncation transaction rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.h -->
# sources/distributed-fs/coda/coda-src/resolution/ops.h

Purpose: exported operation-log API for the server resolution subsystem.

Important APIs: declares `SpoolVMLogRecord`, `SpoolRenameLogRecord`, `TruncateLog`, `FreeVMIndices`, `PurgeLog`, `PrintLog`, and `DumpLog`. It also exposes cross-module resolution hooks `RecovDirResolve` and `CheckAndPerformRename`.

Dependencies/integration: includes Coda containers, recoverable lists, vnode/volume list types, and resolution utility headers. Transaction annotations (`EXCLUDES_TRANSACTION`, `REQUIRES_TRANSACTION`) document RVM calling requirements and are important for static or human auditing.

State/persistence: this header defines the boundary between operation execution and recoverable resolution logging. Persistent state is in per-volume `recov_vol_log` and per-vnode `rec_dlist`s; transient state is in `dlist`/`vle` operation lists.

Risks/test signals: `SpoolVMLogRecord` uses varargs, so caller prototypes do not enforce payload shape. Any opcode addition must update `rsle`, `recle`, print/dump, and replay logic together. Tests should cover each declared opcode path plus transaction boundary misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.cc -->
# sources/distributed-fs/coda/coda-src/resolution/parselog.cc

Purpose: parses serialized remote resolution logs shipped by a coordinator into host- and vnode-indexed in-memory lists.

Important APIs/control flow: `ParseRemoteLogs` calls `ReadOpsFromBuf` to allocate an array of `rsle` records and initialize each from a dumped `recle` buffer. It then builds an `olist` of `he` host entries; within each host it groups entries into `remoteloglist` objects keyed by directory vnode/unique. `DeallocateRemoteLogs` frees host/list wrapper structures. `FindLogList` and `FindRemoteLog` retrieve a vnode-specific remote log.

State/persistence: parsed `rsle` records live in one allocated array returned via `RemoteLogEntries`; host/vnode lists hold pointers into that array. The wrapper lists are transient and must not outlive the array.

Dependencies/integration: depends on `rsle::InitFromRecleBuf`, `resutil::he`, `remoteloglist`, `ThisHostAddr`, and Coda list containers. Output is consumed by `compops.cc`, rename/RU conflict detection, and directory resolution.

Risks/test signals: assumes serialized entries are ordered by host because a host change creates a new `he` without searching for existing hosts. Corrupt buffer sizes rely on assertions, not graceful errors. Test with multi-host/multi-vnode logs, zero entries, unsorted host entries, and malformed/truncated dump buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.h -->
# sources/distributed-fs/coda/coda-src/resolution/parselog.h

Purpose: declares the remote-log grouping structures and parser helpers used by log-based directory resolution.

Important APIs/types: `remoteloglist` is an `olink` with `vnode`, `unique`, and an `olist slelist` of `rsle` pointers for one vnode at one host. `ParseRemoteLogs` parses serialized log bytes into `olist **` host grouping and `rsle **` entry storage. `DeallocateRemoteLogs`, `FindLogList`, and `FindRemoteLog` support cleanup and lookup.

State/persistence: no persistent state; represents temporary views over shipped log buffers. `remoteloglist` destructor intentionally does not assert that its list is empty.

Dependencies/integration: includes `olist` and `vcrcommon`; relies on `he` from `resutil.h` and `rsle` declarations available through included resolution headers in users.

Risks/test signals: ownership of the `RemoteLogEntries` array is not expressed in the header. Callers need a clear cleanup convention: delete the array after deallocating wrapper lists. Test cleanup under parse failure and lookup of absent remote vnode logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.cc -->
# sources/distributed-fs/coda/coda-src/resolution/recle.cc

Purpose: implements recoverable resolution log entries (`recle`) stored in RVM and their serialization/printing.

Important APIs/control flow: constructor/destructor abort because `recle` entries are allocated as raw RVM slots, not normal C++ objects. `InitFromsle` marks the fixed record and allocates a `recvarl` variable part according to opcode, copying payload from an initialized transient `rsle`. `FreeVarl` destroys the variable payload transactionally. `HasList` returns nested child logs for removed directories and rename-deleted directory targets. `GetDumpSize` and `DumpToBuf` serialize fixed and variable parts with begin/end stamps and word alignment. `print` dispatches payload-specific formatting.

State/persistence: fixed fields (`serverid`, `storeid`, `opcode`, directory fid, size, `vle`, index, seqno) live in recoverable memory; variable payloads are separate recoverable allocations. RVM range marking is explicit.

Dependencies/integration: used by `ops.cc`, `recov_vollog.cc`, `rsle` parsing, and remote log shipment. Depends on `rvmlib`, `recvarl`, opcode constants from `resutil`, and payload types declared in `recle.h` with methods implemented in `ops.cc`.

Risks/test signals: `DumpToBuf` copies `vle->vfld` even when `size == 0` and `vle == NULL`, which is risky for `ResolveNULL_OP`/`RES_Repair_OP`. Opcode additions require synchronized changes. Test dumping null-payload records, each variable payload, nested child logs, and recovery after transaction abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.h -->
# sources/distributed-fs/coda/coda-src/resolution/recle.h

Purpose: defines the recoverable log-entry wire/storage layout and variable payload structs used by Coda resolution logs.

Important APIs/types: `recle` is the fixed-length recoverable record containing server ID, store ID, opcode, directory vnode/unique, variable-size length, `recvarl *`, volume-log index, and sequence number. It exposes `InitFromsle`, `FreeVarl`, `HasList`, `GetDumpSize`, `DumpToBuf`, and print overloads. Payload classes model ACL/status stores, creates, symlinks, hard links, mkdir, remove, rmdir with child log and child LCP, rename with source/target metadata and target child log, and quota changes.

State/persistence: records and `recvarl` payloads are RVM-managed. Some payloads contain pointers to recoverable child log lists, making logs tree-shaped for directory removal/rename.

Dependencies/integration: uses `rec_dlist`, `recvarl`, vnode/version-vector types, and opcode constants from resolution utilities. `rsle` is the transient source representation.

Risks/test signals: variable-length structs use trailing `char name[1]`, so allocation sizes and string termination are critical. Pointer-bearing payloads complicate dump/purge recursion. Test payload size calculations, alignment, nested-log purge, and compatibility of serialized record stamps across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recov_vollog.cc -->
# sources/distributed-fs/coda/coda-src/resolution/recov_vollog.cc

Purpose: manages per-volume recoverable resolution log storage, including RVM allocation, transient bitmap recovery, log growth, slot allocation, salvage, and wraparound reuse.

Important APIs/control flow: `operator new/delete` allocate in RVM. The constructor initializes admin limits, index blocks, recoverable bitmap, sequence counters, wraparound cursors, and transient stats. `ResetTransients` rebuilds VM bitmap and statistics after recovery. `Grow`, `FreeBlock`, `IndexToAddr`, and `Increase_Admin_Limit` manage block-indexed storage. `AllocRecord` reserves a VM slot and sequence number; `RecovPutRecord` marks it recoverable and grows backing storage if needed; `RecovFreeRecord` frees the recoverable bit while VM cleanup is deferred. `SalvageLog` compares recovered and shadow bitmaps. `AllocViaWrapAround` reclaims old vnode log entries when no free slot is available.

State/persistence: persistent state includes record blocks, `recov_inuse`, admin limit, sequence counter, and wraparound cursor. Transient state includes `vm_inuse`, `nused`, `max_seqno`, and `vmrstats`.

Dependencies/integration: called by `ops.cc` log spooling/truncation and volume recovery. Uses RVM transactions, vnode fetch/put, lockqueue, bitmap, and stats.

Risks/test signals: VM and recoverable bitmaps intentionally differ during transactions; misuse can leak or double-free slots. Wraparound avoids root vnode and skips modified vnodes but can fail under large active transactions. Test recovery rebuild, admin growth, empty block salvage, wraparound with child logs, and ENOSPC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recov_vollog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rename.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rename.cc

Purpose: validates and replays remote rename operations during directory resolution, including conflict detection and target cleanup.

Important APIs/control flow: exported `CheckAndPerformRename` calls `CheckResolveRenameSemantics` to validate source/target parent directories, source name binding, source object existence, parent pointers, target existence expectations, target parent pointer, and target remove/update conflicts. On success it calls `CleanRenameTarget` for non-empty directory targets, replays `PerformRename`, adjusts disk usage for deleted targets, and spools a `ResolveViceRename_OP` log. On `EINCONS`, it either returns a hinted directory fid or marks/merges affected inconsistency entries.

State/persistence: mutates vnodes/directories through `PerformRename`, `TreeRmBlk` subtree removal, `MarkObjInc`, disk usage updates, and resolution log spooling. Uses in-memory `inclist`/`newinclist` for conflict propagation.

Dependencies/integration: relies on operation semantics (`CheckRenameSemantics`, `PerformRename`), directory handles, `vlist`, RU conflict helpers, `treeremove`, `resstats`, and `ops.cc` logging.

Risks/test signals: conflict outcomes depend on complete `vlist` population and correct parent pointer lookup. Hinted resolution avoids marking objects, which can change retry behavior. Test same-parent and cross-parent renames, pre-existing/deleted targets, non-empty directory overwrite, file and directory RU conflicts, and hinted resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rename.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resclient.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resclient.cc

Purpose: implements server-side RPC handlers and helpers used by the client/participant side of resolution phases, especially installing final version vectors and preparing phase-2 inconsistency objects.

Important APIs/control flow: `RS_InstallVV` translates the volume, locks the object, updates version vectors when COP2 is pending, possibly schedules log truncation, and ships directory contents/ACL back to the coordinator. `MarkObjInc` breaks callbacks and sets the inconsistency flag. `CreateObjToMarkInc` ensures an object named in an inconsistency list exists, creating or linking files/directories/symlinks as needed and spooling resolve log records. `GetPhase2Objects` builds and locks a `vlist` for a parent and all relevant child/parent fids from an inconsistency list. `CreateResPhase2Objects` iterates the list and creates missing objects. `GetNameInParent` finds a vnode's name in its parent directory.

State/persistence: mutates volume/vnode version vectors, directory entries, inode numbers, disk usage, callbacks, COP2 flags, and resolution logs under Coda locking/transaction conventions.

Dependencies/integration: integrates with RPC2 side effects, VRDB host indexes, vnode allocation, file operation semantics, `resutil` inconsistency lists, `ops.cc`, and timing probes.

Risks/test signals: complex object creation paths have many partial side effects before returning errors. Yield points exist for large lists. Test missing parent, name collision with different fid, existing deleted file relink, creating each vnode type, incomplete VSG, and successful `RS_InstallVV` truncation decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resclient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rescomm.cc

Purpose: manages resolution RPC communication state: server entries, replicated resolution groups, connection metadata, and background probing for down servers.

Important APIs/control flow: `ResCommInit` initializes global tables. `srvent` represents a server, resolves names, binds with RPC2 to `RESOLUTIONSUBSYSID`, maps RPC2 errors in `ServerError`, and resets dependent groups/connection info when down. `res_mgrpent` represents a VSG resolution group, maintains canonical host membership, creates/kills member connections, reports incomplete VSGs, and checks multicast results. `GetResMgroup`/`PutResMgroup` lease reusable groups. `conninfo` captures peer host/port/security for inbound RPC handles. `ResCheckServerLWP` periodically signals `ResCheckServerLWP_worker`, which probes down servers.

State/persistence: all state is transient process memory: global server list, resolution-group list, connection-info list, in-use/dying flags, handles, return codes, and server up/down state.

Dependencies/integration: depends on RPC2, LWP condition emulation, service lookup for `codasrv/udp`, `rescomm.private.h`, and public `resolution.h` worker declarations.

Risks/test signals: synchronization is cooperative LWP waiting on raw addresses, not modern locks. `GetHostSet` ignores individual `CreateMember` failures except via final `HowMany`. Error mapping drives retry and membership pruning. Test concurrent binds, server timeout/NAK reset, incomplete VSG detection, group reuse after failures, and connection-info cleanup on reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.h -->
# sources/distributed-fs/coda/coda-src/resolution/rescomm.h

Purpose: public communication-management interface and class declarations for the resolution subsystem.

Important APIs/types: declares group/server lifecycle functions (`GetResMgroup`, `PutResMgroup`, `ResCommInit`, `FindServer`, `GetServer`, `PutServer`), debug printers, `ViceResolve`, and `GetConnectionInfo`. `srvent` models one server and exposes connection/error/state methods. `RepResCommCtxt` holds handles, hosts, retcodes, primary host, multicast info, and dying flags. `res_mgrpent` models a resolution mgroup and exposes membership and result checks. `conninfo` stores inbound RPC peer information.

State/persistence: defines static transient tables for servers, resolution groups, and connection infos; no persistent storage.

Dependencies/integration: includes RPC2, Coda lists, `vice.h`, `res.h`, `vcrcommon.h`, `resutil.h`, and `resolution.h`. Many implementation details are friend-linked to iterators and server-check worker functions.

Risks/test signals: broad friend access and mutable arrays make invariants informal. `ALL_VSGS` is a static header variable, producing one copy per translation unit. Test all public printers and iterator filters, plus lifecycle balance for group leases and server references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.private.h -->
# sources/distributed-fs/coda/coda-src/resolution/rescomm.private.h

Purpose: private compatibility helpers for resolution communication synchronization and string normalization.

Important APIs: declares `ResProcWait(char *)` and `ResProcSignal(char *, int)`, then maps condition macros (`CONDITION_INIT`, `CONDITION_WAIT`, `CONDITION_SIGNAL`) onto LWP wait/signal functions. `TRANSLATE_TO_LOWER` lowercases a mutable C string in place.

State/persistence: no persistent state. Synchronization state is external to LWP wait addresses supplied by callers.

Dependencies/integration: included by `rescomm.cc`; assumes C linkage and C library `isupper`/`tolower` availability through the including file.

Risks/test signals: macros evaluate raw pointer addresses as condition keys and provide no mutex semantics. `TRANSLATE_TO_LOWER` passes `char` directly to ctype macros, which can be undefined for negative signed chars. Test server-name normalization with mixed case and non-ASCII bytes only if such names are expected; otherwise keep hostnames ASCII.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rescoord.cc

Purpose: coordinator-side directory resolution for simple cases: already inconsistent replicas, equal directories, weak equality, and old-logless directory resolution fallback.

Important APIs/control flow: `CompareDirContents` compares directory data and ACL blobs returned by participants, optionally dumping debug files. `ResolveInc` marks all replicas inconsistent, fetches status and contents, compares status/content, and clears inconsistency when replicas are equal. `IsWeaklyEqual` compares store IDs across version vectors. `WEResPhase1` computes a max VV and multicasts `ForceVV`; `WEResPhase2` sends COP2 update sets. `RegDirResolution` masks unavailable hosts, calls `UpdateRunts`, handles already-inconsistent groups, detects already equal vectors, handles weak equality, and reports whether log resolution is still required. `OldDirResolve` marks conflict when no log-based resolution can solve it.

State/persistence: mutates remote replicas through multicast RPCs (`MarkInc`, `ClearIncon`, `ForceVV`, `COP2`), updates timing probes, and may trigger server probing. Local state is temporary buffers and status arrays.

Dependencies/integration: uses `rescomm` groups, `resforce` runt repair, RPC2 side effects, directory/ACL comparison, and `resstats`/timing globals.

Risks/test signals: ACL equality is noted as imperfect and not fatal. Fixed maximum directory buffer sizing can be exceeded for very large directories. Test weak equality, all/some inconsistent groups, equal status with unequal directory content, incomplete VSG, and old resolution with no logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.h -->
# sources/distributed-fs/coda/coda-src/resolution/rescoord.h

Purpose: public coordinator-side directory resolution declarations.

Important APIs: `IsWeaklyEqual` tests store-id equality for version vectors. `WEResPhase1` forces a new version vector and returns success host state/status. `CompareDirContents` compares fetched directory/ACL buffers. `RegDirResolution` resolves weak equality/runt/already-equal/already-inconsistent directory cases or reports that log resolution is required.

State/persistence: no state in the header. Implementations mutate remote replicas through `res_mgrpent` RPC handles and update resolution status.

Dependencies/integration: depends on `ViceFid`, `ViceVersionVector`, `res_mgrpent`, `ViceStoreId`, `ResStatus`, and `SE_Descriptor` definitions from included users. It is included by file and directory resolution modules.

Risks/test signals: forward declarations are implicit through other headers; direct inclusion may require prior type definitions. Test compilation units that include this header alone or adjust includes if modernizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resfile.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resfile.cc

Purpose: implements replicated regular-file resolution and participant RPCs for fetching and forcing file contents.

Important APIs/control flow: `FileResolve` handles coordinator logic: record stats, mask unavailable hosts, resolve weak equality via `WEResPhase1`, detect inconsistent VVs via `IncVVGroup`, fetch the dominant file into a temp file, multicast `ForceFile` to submissive replicas, and mark all replicas inconsistent on failure. `RS_FetchFile` participant-side opens the file inode or a temporary empty inode and transfers it by SMARTFTP with `ResStatus`. `RS_ForceFile` validates coordinator lock ownership and version-vector dominance, receives replacement data, swaps inode/length/status metadata, updates volume/vnode VVs, and cleans old/new inodes around an RVM transaction. `RS_COP2` delegates to `InternalCOP2`.

State/persistence: changes file data inodes, disk usage, vnode metadata, callbacks, version vectors, and stats. Temporary files/inodes buffer transfers.

Dependencies/integration: uses RPC2 side effects, inodeops, VRDB, volume/vnode locking, `rescoord` weak equality, `resforce` runt statistics, and `resstats`.

Risks/test signals: `RS_FetchFile` tests `fd != 1` instead of `fd != -1` before close, which can leak fd 1 edge cases and close invalid fds. Force transfer length is checked by block count, not exact byte count. Test dominant/submissive VV sets, weak equality, missing inode empty transfer, coordinator lock mismatch, side-effect failure rollback, and inode cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resfile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resforce.cc

Purpose: repairs runt directory replicas by extracting directory-create/link operations from a non-runt replica and forcing them onto runt replicas.

Important APIs/control flow: `UpdateRunts` identifies runt VVs with `RuntExists`, fetches a serialized op list and ACL/status via `Res_GetForceDirOps`, temporarily removes non-runt hosts from the group, multicasts `DoForceDirOps` to runt sites, updates successful VV slots, and restores non-runt members. `RS_GetForceDirOps` enumerates a directory into `diroplink` records, serializes them in network order, returns status and ACL, and ships the op file. `RS_DoForceDirOps` validates coordinator lock and runt status, receives/parses the op file, checks semantics/disk usage, installs ACL/status, calls `ForceDir`, sets the top-level VV, and spools a null resolve record. `ForceDir` allocates vnodes and performs mkdir/create/link/symlink operations.

State/persistence: mutates runt directory replicas, ACLs, vnode metadata, directory entries, disk usage, and resolution logs. `diroplink` op files are temporary transfer artifacts.

Dependencies/integration: uses `rescomm`, `resutil`, `ops`, `operations`, `inodeops`, ACL conversion, volume locks, and SMARTFTP.

Risks/test signals: `CreateL` semantics checks currently reject an existing object even though links need an earlier `CreateF` in the same force list; ordering assumptions are important. Temporary removal of non-runt members affects group state. Test directories with files, symlinks, subdirs, hard links, insufficient space, non-runt absence, and lock-owner mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.h -->
# sources/distributed-fs/coda/coda-src/resolution/resforce.h

Purpose: public declarations for runt-directory forcing.

Important APIs/types: `dirop_t` enumerates serialized directory operations: create directory, file, symlink, or hard link. `diroplink` carries operation type, vnode/unique, and fixed-size name buffer with host/network byte-order conversion and `write`. `getdiropParm` packages a volume and operation list for directory enumeration. Exports `UpdateRunts` and `RuntExists`.

State/persistence: header declares transient operation records; persistence happens in `resforce.cc` via vnode allocation, directory operations, and log spooling.

Dependencies/integration: includes Coda `olist`; uses `DIROPNAMESIZE` from resolution utilities in practice and Coda volume/vnode types through including files.

Risks/test signals: fixed `name[DIROPNAMESIZE]` requires enforced length checks during enumeration. Serialized struct layout is compiler/ABI-dependent despite byte-order conversion. Test cross-platform compatibility if heterogeneous servers are supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resforce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/reslock.cc -->
# sources/distributed-fs/coda/coda-src/resolution/reslock.cc

Purpose: participant RPCs for coordinator-driven volume locking and initial status/log-size fetch during resolution.

Important APIs/control flow: `RS_LockAndFetch` gets connection info, translates VSG volume ID, obtains an exclusive volume lock keyed by the coordinator host, fetches the target vnode ignoring inconsistencies, returns its VV and `ResStatus`, computes a maximum log shipment size when RVM resolution is enabled, initializes timing probes for directories, then releases the volume object while retaining the volume lock. `RS_UnlockVol` validates that the caller owns the volume lock and releases it.

State/persistence: manipulates volume lock state and returns vnode status. Does not mutate object contents except timing probe state.

Dependencies/integration: depends on `conninfo`, volume/vnode locking, VRDB translation, `AllowResolution`, `V_RVMResOn`, `recov_vol_log` size, and timing globals.

Risks/test signals: logsize is estimated as `nentries * 200`, a heuristic rather than exact serialization size. Unlock rejects callers that do not match the stored IP. Test lock acquisition/release, wrong unlocker, missing connection info, disabled RVM resolution, directory timing probe initialization, and errors after volume lock acquisition to ensure locks are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/reslock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resolution.h -->
# sources/distributed-fs/coda/coda-src/resolution/resolution.h

Purpose: small public header for resolution background server-check LWP entry points.

Important APIs: declares `ResCheckServerLWP(void *)` and `ResCheckServerLWP_worker(void *)` with C linkage for use by LWP/RPC initialization code and `rescomm` server failure handling.

State/persistence: no state. Implementations in `rescomm.cc` operate on transient server tables.

Dependencies/integration: included by `rescomm.h` and any code starting or signaling the server check LWPs.

Risks/test signals: C linkage keeps callback ABI simple, but there is no ownership or lifecycle declaration for the worker threads. Test startup initializes `ResCommInit` before these workers inspect server tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resolution.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resstats.cc

Purpose: implements counters, histograms, and printing for file/directory resolution and recoverable log statistics.

Important APIs/control flow: constructors zero counter structs or initialize log sizes. `logshiphisto::add/update/print` tracks shipped log byte sizes and max entries. `conflictstats::update`, `logsize::chgsize/report/print`, `varlhisto::countalloc/countdealloc/print`, and `logstats::print` maintain log behavior metrics. `resstats::precollect/postcollect/update/print` aggregates per-volume file and directory stats. `FindResStats` searches the global `ResStatsList`.

State/persistence: `ResStatsList` is a global in-memory list. Individual `resstats` objects are attached to volume logs (`vmrstats`) and updated during resolution/log operations; they are not independently persisted here.

Dependencies/integration: included by log spooling/truncation, file resolution, directory resolution, and volume-log recovery. Uses fd-based `write` output.

Risks/test signals: `logsize` constructor does not zero buckets; callers relying on clean histograms need object memory zeroed or constructor extended. `varlhisto::countdealloc` increments free count but not bucket decrements. Test printed stats after file resolve success/conflict, directory resolve, log allocation/free, admin growth, and periodic pre/post collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.h -->
# sources/distributed-fs/coda/coda-src/resolution/resstats.h

Purpose: declares resolution statistics structures and histogram bucket macros.

Important APIs/types: `fileresstats`, `dirresstats`, and `conflictstats` count outcomes. `logshiphisto` tracks shipped log sizes and maximum entries. `logsize`, `varlhisto`, and `logstats` track recoverable log size, allocation/free counts, wraparounds, and admin growth. `resstats` aggregates these per volume and provides update/print hooks. Macros `Lsize` and `VarlHisto` expose nested log stats.

State/persistence: declares global `ResStatsList`; per-volume objects are expected to live with volume-log state.

Dependencies/integration: uses `olist` and is consumed throughout resolution and recoverable log code.

Risks/test signals: bucket macros are deeply nested and hard to audit for boundary correctness. Some counters distinguish file, directory, conflict, and log behavior but are only as accurate as call sites. Unit tests should hit bucket boundaries around powers of two and verify aggregation updates do not drop user-resolver counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resutil.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resutil.cc

Purpose: shared resolution utilities for host lookup, inbound connection registration, inconsistency marking, store-id allocation, return-code filtering, inconsistency-list serialization, status aggregation, and directory-plus-ACL packaging.

Important APIs/control flow: `FindHE` searches parsed host log entries. `RS_NewConnection` records `conninfo`. `RS_MarkInc` marks an object inconsistent under a transaction. `AllocStoreId` uses `ThisServerId` plus `startuptime + VMCounter`. `CheckRetCodes` and `CheckResRetCodes` derive surviving host sets from RPC results. `AddILE`, `BSToDlist`, `DlistToBS`, `ParseIncBSEntry`, `AllocIncBSEntry`, `CompareIlinkEntry`, and `CleanIncList` manage inconsistency lists. `ObtainResStatus` and `GetResStatus` produce status summaries. `Dir_n_ACL` copies directory bytes, ACL, and root quotas into one buffer for transfer.

State/persistence: mutates connection-info table, vnode inconsistency bits, and the global store-id counter. Other utilities operate on transient buffers/lists.

Dependencies/integration: used by parser, coordinator, client phase-2 creation, lock/fetch, and force code. Depends on RPC2, RVM, directory handles, ACL layout, volume quota metadata, and `rescomm`.

Risks/test signals: `AllocIncBSEntry` asserts on buffer overflow instead of returning an error. `CheckResRetCodes` uses `ntohl` where similar code uses `htonl`, which may affect logged addresses. `Dir_n_ACL` requires callers to `free` returned buffers. Test bounded buffer limits, duplicate inconsistency entries, host filtering for VNOVNODE, root quota packaging, and transaction cleanup on mark-inc failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resutil.cc -->
