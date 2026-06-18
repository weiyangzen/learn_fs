# Research: subset-b-007009

This grouped report covers the requested Coda resolution, server setup, monitoring, and update-client source files. Each file section preserves its source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resutil.h -->
# sources/distributed-fs/coda/coda-src/resolution/resutil.h

Purpose: shared resolution utility declarations and constants for Coda server directory/file resolution. It defines resolution log opcodes, validation action codes, helper list element types, and cross-module function prototypes used by coordinator and subordinate resolution phases.

Important APIs/types: `he` groups remote vnode-resolution log headers by host id; `ilink` is the inconsistency-list entry containing object name, object fid components, parent fid components, and vnode type. Opcode constants distinguish original user operations (`RES_*`) from replayed resolution operations (`ResolveVice*`) while preserving older numeric compatibility. `PRINTOPCODE`, `ISNONRESOLVEOP`, and `FormFid` are macro helpers used throughout log parsing and diagnostics. Utility prototypes include status aggregation (`GetResStatus`, `ObtainResStatus`), store-id allocation, return-code reduction, bounded-byte-stream/list conversion, inconsistency serialization, object marking/creation, phase-2 object acquisition, remote remove lookup, and entry-name lookup.

Control flow and integration: this header ties together `rescoord`, `rvmrescoord`, `subresphase3`, `subresphase34`, `ruconflict`, `resfile`, and log parser code. It depends on RPC2 bounded byte streams, Coda `ViceFid`, `ViceStatus`, `ViceStoreId`, `Volume`, `Vnode`, `ResStatus`, `dlist`, and `olist` infrastructure.

State/persistence: no state is stored here, but declarations operate on persistent RVM volume/vnode state, resolution logs, and inconsistency flags. Risks include macro side effects, raw `strdup`/`free` ownership in `ilink`, and opcode compatibility requirements. Test signals are successful resolution of conflicting create/remove/rename cases, correct bounded-BS round trips, and no leaks in `CleanIncList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rsle.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rsle.cc

Purpose: implements `rsle`, the VM-resident spool-list entry that stages a directory resolution log record before it is copied into the recoverable RVM volume log. It also reconstructs remote log entries from dumped `recle` buffers and exposes helpers to extract names, child fids, and vnode types from heterogeneous log-record unions.

Important functions: constructors initialize record metadata and optional index/sequence numbers; `init(int op, va_list)` fills the operation-specific union from varargs for stores, creates, symlinks, links, mkdirs, removes, rmdirs, renames, quota changes, null records, and repair records. `CommitInRVM` ensures a vnode log exists, writes the reserved record slot with `RecovPutRecord`, appends it to the vnode log, and updates log-size histograms. `Abort` deallocates a reserved RVM slot. `InitFromRecleBuf` validates dump stamps, advances the caller buffer pointer, overlays the dumped `recle`, and points `name1`/`name2` into the variable-length payload.

Control flow and persistence: new VM entries own dynamically copied names; parsed remote entries borrow payload memory and must not free names. Commit runs inside an RVM transaction and makes records recoverable; abort releases only the reserved slot. Dependencies include `recle`, `recov_vollog`, `ops`, `srv`, `volume`, `vnode`, and resolution statistics.

Risks and tests: varargs ordering is fragile, borrowed name pointers depend on remote-log buffer lifetime, and rename target handling uses several conditional fields. Test with each opcode round-tripping through spool, dump, parse, print, extraction, commit, and abort paths, including rename-with-target and rmdir subtree records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rsle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rsle.h -->
# sources/distributed-fs/coda/coda-src/resolution/rsle.h

Purpose: declares the `rsle` VM spool-log record class used by RVM-backed directory resolution. The name means RVM spool-list entry, differentiating it from older VM-only resolution log entries.

Important APIs/types: `rsle` inherits `olink` so records can be held in Coda `olist`s. It stores an RVM log index, sequence number, `ViceStoreId`, parent directory vnode/unique pair, opcode, and a union of operation-specific record types from `ops.h` and `recle.h`. Large or variable-length names are kept as `name1` and `name2`, with `namesalloced` controlling destructor ownership. Methods include varargs initialization, RVM commit/abort, reconstruction from a dumped recoverable record buffer, and debug printing to `stdout`, `FILE *`, or fd.

Control flow and integration: producers create or initialize `rsle` instances during normal operation spooling and subordinate resolution. Coordinator/subordinate log parsing uses `InitFromRecleBuf` and then `ExtractVNTypeFromrsle`, `ExtractChildFidFromrsle`, and `ExtractNameFromrsle` to drive semantic checks.

State/persistence: the object itself is VM state; `CommitInRVM` persists into the volume log. Risks are manual ownership of names, varargs type mismatches, and union field interpretation by opcode. Test signals include clean destructor behavior for allocated names, no double-free for parsed names, and correct extraction for all supported opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rsle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ruconflict.cc -->
# sources/distributed-fs/coda/coda-src/resolution/ruconflict.cc

Purpose: detects remove/update conflicts during directory resolution. A remove/update conflict occurs when one replica removed an object while another replica updated it or its subtree in a way not represented by the remover's log.

Important functions: `RUConflict` dispatches file/symlink removes to `FileRUConf` and directory removes to recursive directory checks. `FileRUConf(rsle *, Vnode *)` extracts the deleted object's version vector from a remove log record; `FileRUConf(ViceVersionVector *, Vnode *)` treats weak equality, equality, and local-subsumed cases as non-conflicting and everything else as conflict. `NewDirRUConf` walks directory entries, skips `.`/`..`, locates child and parent VLEs, and either compares deleted-file VVs or recurses into child directories. `FindDeletedFileVV` searches a remote parent log for remove or rename-over-target records. `ChildDirRUConf` finds the deleted directory's remote log and checks that the live directory's last local log entry exists there.

Control flow and state: callers pass a VLE list of involved objects and grouped remote logs. Conflict result is stored in `RUParm::rcode` to short-circuit recursion. Persistent inputs are vnode version vectors and RVM resolution logs; this module mutates no persistent state directly.

Dependencies, risks, tests: depends on log parser `FindRemoteLog`, vnode lists, Coda directory enumeration, and version-vector comparison. Risks include assertions when expected VLE/log entries are missing and a conservative conflict when deleted directory logs are absent. Test with file remove/update, rename-over-remove, removed directory with matching/nonmatching descendant logs, empty directory recursion, and weakly equal VVs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ruconflict.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ruconflict.h -->
# sources/distributed-fs/coda/coda-src/resolution/ruconflict.h

Purpose: declares remove/update conflict detection helpers used by subordinate phase 3 semantic validation.

Important APIs/types: `RUParm` carries the recursive directory conflict walk state: `vlist` for loaded vnodes, `AllLogs` for remote logs grouped by host/object, `srvrid` for the server whose remove is being checked, `vid` for the volume id, and `rcode` as an accumulated nonzero conflict result. Public functions are `RUConflict(rsle *, dlist *, olist *, ViceFid *)`, two `FileRUConf` overloads for log-entry or explicit deleted version vector comparisons, and `NewDirRUConf` for recursive directory entry handling.

Control flow and integration: `subresphase3.cc` calls `RUConflict` from `CheckValidityResOp` for remove and rmdir compensation operations that otherwise look performable. The helper bridges `rsle` log entries, Coda VLE lists, remote parsed logs, and vnode version vectors.

State/persistence: the header owns no state. It describes analysis over persistent vnode/log state and returns a boolean-style conflict code. Risks are tight coupling to `rsle` opcode layout and `Vnode` version-vector semantics. Test signals are consistent conflict decisions from both `FileRUConf` overloads and correct propagation of `RUParm::rcode` through recursive directory enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ruconflict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rvmrescoord.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rvmrescoord.cc

Purpose: coordinator-side RVM-backed directory resolution. It first tries regular directory resolution, then runs multi-replica log collection, log distribution/compensation, inconsistency reconciliation, and final version-vector installation.

Important functions: `RecovDirResolve` orchestrates phases and updates `dirresstats`. `CoordPhase2` allocates per-server buffers, performs `FetchLogs` MRPC calls using SmartFTP VM buffers, checks return codes, and concatenates successful logs. `CoordPhase3` ships merged logs to subordinates via `ShipLogs` or `NewShipLogs`, computes the final status/VV, gathers returned inconsistency byte streams into a `dlist`, and compares returned `ViceStatus` fields. `CoordPhase34` sends the merged inconsistency list to `HandleInc`. `CoordPhase4` builds an update-set VV, calls `InstallVV`, fetches directory contents, and compares replicas. `UpdateStats` stores resolution stats in the volume log statistics object.

Control flow and state: phase 1 locking is assumed already done by `ViceResolve`. On phase failure, and when no hint fid is supplied, it broadcasts `MarkInc_OP`. Success requires phase 4 content comparison to pass. Persistent effects mostly happen on subordinates; coordinator allocates store ids and final update-set vectors.

Dependencies, risks, tests: depends on MRPC/RPC2 side effects, `res_mgrpent`, VRDB host indexing, version-vector utilities, `rescomm`, `resutil`, and RVM timing probes. Risks include buffer-size assumptions from caller-provided `sizes`, partial VSG handling, conservative inconsistency marking, and `CoordPhase34` logging errors but returning zero. Test with complete/incomplete VSGs, failed fetch/ship/install RPCs, hint-fid retry paths, nonmatching status, and directory-content mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rvmrescoord.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rvmrestiming.h -->
# sources/distributed-fs/coda/coda-src/resolution/rvmrestiming.h

Purpose: defines timing probe identifiers for RVM-backed resolution paths. It mirrors generic resolution probe ids and adds recoverable-directory-resolution phase probes.

Important APIs/types: it declares `extern int pathtiming`, `extern int probingon`, `MAXPROBES`, and the `PROBE(info, num)` macro that conditionally calls `timing_path::insert`. `RecovTimingBase` starts the RVM-specific range, covering coordinator and subordinate phase 1, phase 2, phase 3, compensation, perform operation, phase 3.5/34, and phase 4 begin/end points. It also repeats older generic directory/file resolution ids for shared instrumentation consumers.

Control flow and integration: included by coordinator and subordinate resolution phase files. Probe calls bracket RPC phases, compensation computation, semantic execution, and final install/handle-inconsistency work.

State/persistence: no persistent state; writes are to process-local timing objects such as `tpinfo`. Risks include duplicated constants with `timing.h`, macro multi-evaluation of `info`, and dependence on external synchronization because `timing_path` is not internally locked. Test signals are probe traces that show balanced begin/end ids for successful and failed resolution runs and no out-of-range ids under `MAXPROBES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rvmrestiming.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subpreres.cc -->
# sources/distributed-fs/coda/coda-src/resolution/subpreres.cc

Purpose: subordinate-side pre-resolution helpers used around repair and inconsistency cleanup. It fetches directory contents after repair and clears inconsistency flags when coordinator-supplied version vectors match.

Important functions: `RS_FetchDirContents` translates the VSG fid, obtains the directory with a read lock, packages directory data plus ACL via `Dir_n_ACL`, sends it through RPC2 SmartFTP `FILEINVM`, returns length and `ViceStatus`, then releases objects inside an RVM transaction. `RS_ClearIncon` validates the calling connection, translates the fid, gets the object with a write lock, verifies the volume lock belongs to the coordinator's remote host, compares version vectors ignoring inconsistency bits, clears the inconsistency flag, and breaks callbacks.

Control flow and persistence: both functions use `GetFsObj`/`VPutVnode`/`PutVolObj`. `RS_ClearIncon` mutates persistent vnode version-vector flags inside RVM recovery transaction boundaries when locks are released. `RS_FetchDirContents` mostly reads state but still releases handles inside a transaction.

Dependencies, risks, tests: depends on RPC2 side effects, `rvmlib`, `srv`, `volume`, `resutil`, and lock ownership. Risks include returning `EINVAL` for many setup failures, assuming side-effect buffers remain valid until transfer completes, and clearing inconsistency only under exact vector compatibility. Test with successful directory fetch, side-effect failures, coordinator mismatch, incompatible VV, and callback invalidation after clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subpreres.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subresphase2.cc -->
# sources/distributed-fs/coda/coda-src/resolution/subresphase2.cc

Purpose: subordinate side of RVM directory resolution phase 2: collect the local log for the target directory and ship it to the coordinator.

Important functions: `RS_FetchLogs` translates the fid, creates a VLE list, loads the target object with a read lock, dumps the vnode's resolution log with `DumpLog`, returns byte size and entry count, and sends the buffer through `rs_ShipLogs`. `rs_ShipLogs` configures a SmartFTP `SERVERTOCLIENT` side effect over an in-memory file and waits for local completion.

Control flow and state: the function probes `RecovSubP2Begin/End`, validates the volume id, gets the object, leaves a placeholder for phase-2 semantic checks such as verifying coordinator lock and log wrap status, dumps logs, ships them, and releases objects with `PutObjects`. It reads persistent RVM vnode logs but does not mutate them.

Dependencies, risks, tests: depends on `vlist`, `operations`, `DumpLog`, RPC2/SFTP, and timing infrastructure. Risks include unimplemented semantic checks, reliance on correct caller-provided side-effect descriptor semantics, and handling empty logs/buffers. Test with directories with no log, multiple log entries, side-effect failures, invalid fid translation, and cleanup of allocated dump buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subresphase2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subresphase3.cc -->
# sources/distributed-fs/coda/coda-src/resolution/subresphase3.cc

Purpose: subordinate side of phase 3: receive merged logs, compute compensation operations, validate semantics against local state, perform safe operations, mark irreconcilable objects inconsistent, and return an inconsistency list.

Important functions: `RS_NewShipLogs` fetches the coordinator's SmartFTP log buffer, parses remote logs, computes compensation ops with `ComputeCompOps`, preprocesses create/delete pairs into null ops, gathers and locks all needed objects with `GetResObjs`, executes `CheckSemPerformRes`, then updates directory status with `SetPhase3DirStatus`. `RS_ShipLogs` is the older wrapper without hint output. Helpers gather child/rename/subtree fids, check names and fid bindings in Coda directories, classify operations through `CheckValidityResOp`, execute via `PerformRegularCompOp` and `PerformResOp`, locate remote remove store ids, and update conflict statistics.

Control flow and persistence: compensation is sorted enough to null out matching create/delete pairs. Semantic checks return `PERFORMOP`, `NULLOP`, `MARKPARENTINC`, `MARKOBJINC`, or `CREATEINCOBJ`. Successful operations call normal server mutation helpers (`PerformCreate`, `PerformRemove`, `PerformMkdir`, `PerformRmdir`, `PerformLink`, `PerformSymlink`, `PerformSetQuota`) and spool resolution log records. `PutObjects(0, ...)` intentionally commits operations already applied even if a later phase-3 step failed. `SetPhase3DirStatus` applies the coordinator status VV, performs a COP1 update with a new store id, sets COP2 pending, updates status fields, and spools `ResolveNULL_OP`.

Dependencies, risks, tests: depends on `parselog`, `compops`, `ruconflict`, `treeremove`, vnode lists, volume indexes, RVM logs, callbacks, and conflict stats. Risks are high: many `CODA_ASSERT`s for unexpected states, partial commits on later errors, rename handling delegated elsewhere, conservative conflict marking, manual block accounting, and side-effect buffer parsing. Test with every opcode, create/delete cancellation, remove/update conflict, name/name conflict, moved-object conflict, subtree rmdir, quota conflict, hint fid generation, ENOSPC during spool, and recovery after coordinator crash with COP2 pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subresphase3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subresphase34.cc -->
# sources/distributed-fs/coda/coda-src/resolution/subresphase34.cc

Purpose: subordinate phase 3.5/34 handler that receives the coordinator's consolidated inconsistency list and ensures local replicas contain corresponding inconsistent objects or parent marks before final version-vector installation.

Important functions: `RS_HandleInc` parses an RPC2 bounded byte stream into an `ilink` list, loads required objects with `GetPhase2Objects`, creates missing phase-2 objects with `CreateResPhase2Objects`, calls `ProcessIncList`, then spools a `ResolveNULL_OP` record and returns updated status. `ProcessIncList` marks each listed object inconsistent when it exists under the expected parent, marks both actual and expected parents when parentage diverges, or marks the expected parent when the object cannot be found/created.

Control flow and persistence: this phase only runs when the inconsistency list is nonempty. It may allocate new placeholder objects, set inconsistency bits with `MarkObjInc`, and append a resolution log record to the resolved directory. Objects are returned with `PutObjects`, passing block accounting and commit semantics.

Dependencies, risks, tests: depends on `resutil` inconsistency serialization, vnode lists, `SpoolVMLogRecord`, and normal volume/vnode locking. ENOSPC while spooling the null record is explicitly ignored, which can reduce auditability. Test with object present in expected parent, object moved, missing child requiring parent mark, missing object creation, ENOSPC spooling, and returned `ViceStatus.Length` used by phase 4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/subresphase34.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/timing.cc -->
# sources/distributed-fs/coda/coda-src/resolution/timing.cc

Purpose: implements a lightweight timestamp path recorder for resolution profiling. It records probe ids with time values and prints deltas between consecutive probes and from first to last probe.

Important functions: `tvaminustvb` subtracts timeval values with microsecond borrow handling. `timing_path::timing_path` allocates initial storage, `grow_storage` doubles capacity or allocates `TIMEGROWSIZE`, `insert` records the id and either `gettimeofday` or an optional `_NSC_TIMING_` hardware counter, and `postprocess` overloads write trace output to `stdout`, a `FILE *`, or an fd.

Control flow and state: callers insert probe ids through the `PROBE` macro in `timing.h`/`rvmrestiming.h`. Storage is process-local heap memory and is not synchronized. Output uses direct `write` calls after formatting into a fixed buffer.

Dependencies, risks, tests: depends on `coda_assert`, `sys/time`, optional ioctl counter support, and C string/memory functions. Risks include no locking, unchecked initial malloc before later assertion only on grow, fixed 256-byte output buffer, and old-style external `clockFD` declaration. Test with zero entries, one entry, growth beyond initial capacity, normal timeval borrow, `_NSC_TIMING_` wrap behavior if enabled, and concurrent-probe exclusion by caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/timing.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/timing.h -->
# sources/distributed-fs/coda/coda-src/resolution/timing.h

Purpose: declares generic resolution timing probes and the `timing_path` class used by resolution profiling.

Important APIs/types: `tpe` stores a probe id plus `timeval`. `timing_path` owns a growable array of `tpe` entries with `insert` and `postprocess` methods. Global flags `pathtiming` and `probingon` enable probes, and `tpinfo`/`FileresTPinfo` are externally allocated timing paths. Probe constants cover regular directory resolution, client-side fetch/phase work, compensation operation execution, and file-resolution stages starting at `FILERESBASE`.

Control flow and integration: included by both coordinator and subordinate resolution modules. `PROBE(info, num)` conditionally records a probe and is intentionally cheap when disabled.

State/persistence: no persistent state; runtime profiling only. The underlying implementation is heap-based and unsynchronized. Risks include duplicated ids with `rvmrestiming.h`, macro argument evaluation, and accidental use from multiple LWPs without external locking. Test signals are ordered probe output around successful resolution and correct no-op behavior when either global flag is false or the timing-path pointer is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/timing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/weres.cc -->
# sources/distributed-fs/coda/coda-src/resolution/weres.cc

Purpose: subordinate handler for weakly-equal resolution. It forces a vnode's version vector forward to a coordinator-provided vector when the local vector is equal or strictly subsumed.

Important function: `RS_ForceVV` validates caller connection info, translates the VSG fid, gets the object with a write lock, verifies the volume is locked by the coordinator's host, compares local and target version vectors, applies the difference to both vnode and volume vectors when local is a subset, clears COP2 pending, optionally updates status fields from `ViceStatus`, breaks callbacks, and releases objects inside an RVM transaction.

Control flow and persistence: incompatible or dominating local vectors return `EINCOMPATIBLE`; equal vectors are effectively a no-op except possible COP2/status cleanup. Successful subset advancement mutates persistent vnode/volume version vectors and callback state.

Dependencies, risks, tests: depends on lock ownership, version-vector arithmetic (`SubVVs`, `AddVVs`), callback invalidation, RVM transaction release, and optional status propagation. Risks include strict coordinator lock requirement, updating metadata when `statusp->Date` is used as validity flag, and assertion on vnode release failures. Test equal, subset, dominating, and incomparable vectors; COP2 pending clear; coordinator mismatch; and status metadata update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/weres.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/Makefile.am -->
# sources/distributed-fs/coda/coda-src/scripts/Makefile.am

Purpose: Automake manifest for installing Coda client/server helper scripts and manpages.

Important declarations: `sbin_SCRIPTS` receives generated scripts such as `coda-client-setup`, `bldvldb.sh`, `createvol_rep`, `purgevol_rep`, `startserver`, `vice-setup`, and `vice-setup-rvm` under conditional `BUILD_CLIENT`/`BUILD_SERVER`. `dist_sbin_SCRIPTS` ships static helper scripts including `codastart`, log rotation, partial reinit, kill volumes, and setup substeps. `dist_man_MANS` lists corresponding manual pages. `EXTRA_DIST` distributes noninstalled utilities (`findparents.sh`, `volinfo.pl`, `volsizes.pl`, `pwdtopdbtool.py`). `CLEANFILES` removes generated script outputs.

Control flow/state: no runtime behavior. Build-time state is Automake's generated `Makefile.in` and configure substitution for `.in` scripts.

Dependencies/integration: integrates with top-level configure conditionals and install targets. Risks are missing helper scripts when conditionals do not match package composition, stale generated scripts in `CLEANFILES`, and static utilities distributed but not installed. Test signals are `make distcheck`, correct install contents under client-only/server-only builds, and generated scripts containing substituted paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/bldvldb.sh.in -->
# sources/distributed-fs/coda/coda-src/scripts/bldvldb.sh.in

Purpose: rebuilds the Coda VLDB from per-server volume lists. It is normally run on the SCM after replicated volume changes.

Control flow: loads `server.conf` through `codaconfedit`, defaults `vicedir` to `/vice`, changes to `$vicedir/vol/remote`, resolves command-line server aliases through `$vicedir/db/servers`, fetches each server's volume list with `volutil -h <server> getvolumelist`, atomically renames successful `.list.new` files, concatenates `*.list` into `$vicedir/vol/BigVolumeList`, then invokes `volutil makevldb`.

State/persistence: writes remote volume-list snapshots, `BigVolumeList`, and the VLDB generated by `volutil`. It reads `/vice/db/servers` and server config. No explicit locking is used.

Dependencies, risks, tests: depends on `codaconfedit`, `volutil`, reachable servers, and shell glob behavior. The loop only processes explicitly supplied servers because `"${@:-}"` expands to no words with zero args despite the comment saying all servers when argc=1/none; this should be verified against caller expectations. Regex server lookup is unanchored. Test with one server, multiple servers, failed fetch preserving old list, empty remote directory, and VLDB rebuild success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/bldvldb.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/coda-client-setup.in -->
# sources/distributed-fs/coda/coda-src/scripts/coda-client-setup.in

Purpose: initializes a Coda client installation by writing `venus.conf`, creating cache/log/runtime directories, arranging kernel module/device setup, and marking the cache for initialization.

Control flow: validates arguments differently for Cygwin and Unix, sets realm and cacheblocks via `codaconfedit`, reads generated `venus.conf`, applies default paths, creates parent directories with a custom mode-preserving `makedir`, loads the Linux `coda` kernel module and boot autoload configuration for udev systems, handles Cygwin drive mapping and private mapping config, creates the mountpoint and `NOT_REALLY_CODA`, attempts `/dev/cfs0`/`/dev/coda/0` creation via `MAKEDEV`, then touches `$cachedir/INIT`.

State/persistence: modifies `/etc/coda`-style config through `codaconfedit`, system module config (`/etc/rc.modules` or `/etc/modules`), `/dev`, mountpoint contents, Cygwin symlink `/coda`, and client cache/log/runtime directories.

Dependencies, risks, tests: requires root-like privileges, `codaconfedit`, platform tools, and correct config paths. Risks include unquoted path uses in a few places, host-specific init-system assumptions, direct edits to `/etc/modules`, and destructive Cygwin `/coda` removal. Test on Linux with existing/new directories, missing kernel device, Cygwin drive-letter validation, custom `venus.conf` paths, and idempotent rerun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/coda-client-setup.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/coda-server-logrotate -->
# sources/distributed-fs/coda/coda-src/scripts/coda-server-logrotate

Purpose: simple Coda server log rotation utility.

Control flow: loads `server.conf` through `codaconfedit`, defaults `vicedir` to `/vice`, defines `rotate` to shift suffixes `-9` through `-0` up one generation and move the active file to `-0`, rotates `$vicedir/srv/SrvLog`, `$vicedir/srv/SrvErr`, and `$vicedir/auth2/AuthLog`, then sends `SIGHUP` to codasrv/auth2 pids if pid files exist.

State/persistence: renames log files in server/auth directories and signals daemons to reopen logs. It does not compress, remove old `-10` files, or use locks.

Dependencies, risks, tests: depends on `codaconfedit`, pid files, `seq`, and daemons handling `SIGHUP`. Risks include `seq` portability, race with active log writers, stale pid-file signaling, and unbounded suffixes beyond `-10` if repeated external manipulation occurs. Test with missing logs, full suffix chain, stale pid files, and daemon reopen behavior after rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/coda-server-logrotate -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/codastart -->
# sources/distributed-fs/coda/coda-src/scripts/codastart

Purpose: minimal server startup wrapper for a configured Coda server.

Control flow: compares `/vice/hostname` with `/vice/db/scm`. On the SCM it starts `updatesrv` and `auth2`; on non-SCM servers it starts `auth2 -chk`. It then starts `updateclnt -h <scm>` and finally `startserver`.

State/persistence: directly launches daemon processes in the background except for `startserver`, which runs in the foreground of the script unless that script detaches internally. It reads fixed `/vice` files and does not consult `server.conf`.

Dependencies, risks, tests: depends on absolute `/vice` layout, `updatesrv`, `auth2`, `updateclnt`, and `startserver` in `PATH`. Risks include no error checking, no pid management, duplicate daemon starts, and fixed config path ignoring alternate `vicedir`. Test SCM/non-SCM branches, missing files, PATH setup, and repeated invocation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/codastart -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/createvol_rep.in -->
# sources/distributed-fs/coda/coda-src/scripts/createvol_rep.in

Purpose: creates a replicated Coda volume on the SCM across one to eight servers/partitions and updates VLDB/VRDB metadata.

Control flow: loads `server.conf`, requires current host to match `$vicedir/db/scm`, validates args and volume-name length, migrates old `VRList`/`maxgroupid` locations, dumps current VRDB to `VRList.new`, rejects existing replicated/nonreplicated names by querying each server's volume list, validates partitions, allocates or accepts a 0x7f-style group id, calls `volutil create_rep` for each replica, disables resolution for singly replicated volumes, rebuilds VLDB with `bldvldb.sh`, appends a padded eight-replica VRList entry, runs `volutil makevrdb`, swaps `VRList.new` into place with backup, and calls `volutil updatedb`.

State/persistence: creates actual server volumes, modifies `$vicedir/db/VRList`, `maxgroupid`, `files`, VRDB, VLDB, and temporary files under `/tmp`.

Dependencies, risks, tests: depends on `volutil`, `bldvldb.sh`, SCM identity files, server/partition listings, and shell/awk/sed parsing. Risks include no rollback after partial replica creation, unanchored regex lookups, `/tmp` predictable names, inconsistent `VRList` if `makevrdb` succeeds but moves fail, and lower/upper group id detection by prefix only. Test duplicate detection, multi-partition validation, partial create failure recovery, single-replica resolution disable, and VRList padding to eight replica slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/createvol_rep.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/findparents.sh -->
# sources/distributed-fs/coda/coda-src/scripts/findparents.sh

Purpose: quick diagnostic script to find backup volumes in `VolumeList` that appear to lack parent entries.

Control flow: prints a heading, extracts the eighth field for lines containing `backup`, strips leading `W`, loops each id, tests whether `/vice/vol/VolumeList` contains `I<id>`, and for missing parents prints selected information from matching `W<id>` lines.

State/persistence: read-only against `VolumeList`; no writes.

Dependencies, risks, tests: depends on current directory `VolumeList` for the first grep and absolute `/vice/vol/VolumeList` for subsequent checks, plus fixed field layout from Coda volume lists. Risks include inconsistent relative/absolute inputs, broad `grep backup` matching, and fragile text parsing. Test with known backup/parent pairs, missing parents, unusual names containing `backup`, and running outside `/vice/vol`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/findparents.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/partial-reinit.sh -->
# sources/distributed-fs/coda/coda-src/scripts/partial-reinit.sh

Purpose: generates a recovery script to recreate existing volumes after a partial server reinitialization and lists volumes that will not be recreated.

Control flow: prompts if `/tmp/reinit_script` already exists, removes old generated files, emits a shell script header, scans `/vice/vol/VolumeList` excluding partition, backup, and restored entries, maps each volume id to a replicated id in `/vice/db/VRList`, appends `volutil create_rep <part> <name> <repid> <volid>` lines to a temp script, builds `/tmp/not_created` for volumes absent from the generated script, warns if nonempty, then moves the temp script to `/tmp/reinit_script` and marks it executable.

State/persistence: writes `/tmp/reinit_script*` and `/tmp/not_created`; reads `/vice/vol/VolumeList` and `/vice/db/VRList`. It does not execute volume recreation.

Dependencies, risks, tests: depends on exact field positions and shell prompt behavior. Risks include predictable `/tmp` paths, grep substring false positives when mapping ids, no locking, and accidental overwrite after confirmation. Test generated commands from sample VolumeList/VRList, volumes without repid warnings, exclusion of backups/restored volumes, and pre-existing script prompt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/partial-reinit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/purgevol_rep.in -->
# sources/distributed-fs/coda/coda-src/scripts/purgevol_rep.in

Purpose: dry-run or destructive purge of a replicated volume and its replicas from Coda servers and SCM metadata.

Control flow: loads `server.conf`, requires SCM host, parses `--kill` to enable destructive mode, queries `getvolinfo` for replica/server mapping, loops replicas, obtains each server's volume list, finds volume ids with matching replica ids, and either prints or executes `volutil purge`. In kill mode it removes the replicated volume id from `dumplist`, removes the volume row from `VRList`, rebuilds VRDB with `volutil makevrdb`, and rebuilds VLDB with `bldvldb.sh`.

State/persistence: destructive mode deletes server volumes and edits `$vicedir/db/dumplist`, `VRList`, VRDB, and VLDB. Dry-run mode is read-only.

Dependencies, risks, tests: depends on `getvolinfo` output format, `volutil`, `bldvldb.sh`, and SCM config. Risks include a likely bug using `$SCM` uppercase when only `scm` is set, unanchored `grep "$REPVOLNAME"`, parsing human-readable `getvolinfo`, and no rollback after partial purge. Test dry-run output, `--kill` with controlled fixtures, uppercase `$SCM` failure, volume names that are regex prefixes, and multi-replica metadata cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/purgevol_rep.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/pwdtopdbtool.py -->
# sources/distributed-fs/coda/coda-src/scripts/pwdtopdbtool.py

Purpose: migration helper that converts legacy `/vice/db/user.coda` and `group.coda` data into commands for `pdbtool`.

Control flow: removes `/vice/db/prot_users.cdb` if present, opens a write pipe to `pdbtool`, writes default `System`, `System:Administrators`, and `System:AnyUser` identities with legacy ACL-compatible ids, reads old users as colon-separated records and emits `nui` commands, reads old groups and emits `ng`, `ci`, and `ag` commands mapping names to saved user ids, then closes the pipe.

State/persistence: deletes the protection users CDB and relies on `pdbtool` to create/update protection database state. It reads fixed `/vice/db` paths.

Dependencies, risks, tests: depends on Python 3, `pdbtool` in `PATH`, legacy file formats, and group members all appearing in `user.coda`. Risks include no error handling for missing files, unsafe pipe status ignoring, unquoted names in command language, and hardcoded owner ids. Test with sample users/groups, missing member names, existing database removal, and ACL id compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/pwdtopdbtool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/startserver.in -->
# sources/distributed-fs/coda/coda-src/scripts/startserver.in

Purpose: wrapper to rotate logs and start the Coda file server (`codasrv`) with configured RVM flags.

Control flow: ignores `SIGHUP`, loads `server.conf` when available, defaults `vicedir`, runs `coda-server-logrotate`, removes `$vicedir/srv/CRASH`, sets `-zombify` if `$vicedir/srv/ZOMBIFY` exists, derives `RVMFLAGS` from old `$vicedir/srv.conf` only when modern `server.conf` is absent, then exec-style invokes `codasrv` with passed arguments, zombify flag, and RVM flags.

State/persistence: rotates logs, removes crash marker, reads config and optional zombify marker. The daemon itself handles persistent volume/RVM state.

Dependencies, risks, tests: depends on generated `@sbindir@` paths, `coda-server-logrotate`, `codasrv`, and old/new config conventions. Risks include no explicit `exec`, word splitting in `$RVMFLAGS`, possible missing logrotate failure handling, and treating any `ZOMBIFY` file as active flag. Test with server.conf present/absent, old srv.conf `-rvm` line, marker files, forwarded args, and logrotation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/startserver.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-killvolumes -->
# sources/distributed-fs/coda/coda-src/scripts/vice-killvolumes

Purpose: destructive cleanup helper that removes Coda volume database files for a clean start.

Control flow: prompts the operator, accepts yes/default as proceed and no as abort, then removes `/vice/db/VRDB`, `/vice/db/VLDB`, `/vice/vol/RWList`, `/vice/vol/AllVolumes`, `/vice/vol/VolumeList`, and `/vice/db/VRList`, and prints confirmation.

State/persistence: permanently deletes volume database metadata files but does not remove container data or RVM data directly.

Dependencies, risks, tests: depends on fixed `/vice` layout and interactive shell. Risks are obvious destructive behavior, default proceed on empty/unrecognized input, no config-file `vicedir` support, and no backup. Test prompt handling, no branch, removal of missing files, and alternate configured `vicedir` not being honored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-killvolumes -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-rvm.in -->
# sources/distributed-fs/coda/coda-src/scripts/vice-setup-rvm.in

Purpose: interactive setup for Coda server RVM log/data areas and server configuration.

Control flow: loads `server.conf` if present, rejects existing `-rvm` line in old `srv.conf`, explains RVM tradeoffs, prompts for log file/partition and size, data file/partition and size, normalizes paths, converts data size to MB/bytes, warns before wiping, initializes the log with `rvmutl`, computes static/reserved/heap sizes and RVM start/list/chunk parameters, writes `rvm_log`, `rvm_data`, and `rvm_data_length` through `codaconfedit` or appends old-style `-rvm`, then runs `rdsinit`.

State/persistence: may wipe/init RVM log and data files or raw partitions, and writes server config. It directly creates persistent metadata storage.

Dependencies, risks, tests: requires `rvmutl`, `rdsinit`, `codaconfedit`, operator privilege, and accurate device choices. Risks include raw device destruction, unchecked arithmetic for too-small data sizes, assumptions about <=4 meaning GB, no noninteractive mode, and `set -e` terminating on unexpected command failures. Test with file-backed RVM in a temp area, unsupported sizes, existing srv.conf guard, config write path, and failed `rvmutl`/`rdsinit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-rvm.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-scm.in -->
# sources/distributed-fs/coda/coda-src/scripts/vice-setup-scm.in

Purpose: SCM-specific server setup step that initializes server identity metadata.

Control flow: loads `server.conf`, defaults `vicedir`, writes initial maximum replicated volume id `2130706432` (`0x7f000000`) to `$vicedir/db/maxgroupid`, determines the SCM hostname from exported `hn`, Linux `hostname -f`, or prompted domain plus short hostname, changes to `$vicedir/db`, prompts for a unique server id, appends `<hostname> <id>` to `servers`, and writes hostname to `$vicedir/db/scm`.

State/persistence: creates/overwrites `maxgroupid`, appends to `servers`, and writes `scm`.

Dependencies, risks, tests: depends on `codaconfedit`, hostname resolution, and interactive input. Risks include no validation that server id is numeric/range/unique despite prompt text, appending duplicates, and overwriting maxgroupid on rerun. Test fresh setup, rerun duplicate handling, non-Linux domain prompt, and correct exported `hn` propagation from `vice-setup`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-scm.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-srvdir.in -->
# sources/distributed-fs/coda/coda-src/scripts/vice-setup-srvdir.in

Purpose: interactive setup for the server container-file hierarchy and `vicetab` entry.

Control flow: loads `server.conf`, determines hostname, explains storage directory requirements, prompts for a server data directory defaulting to `/vicepa`, creates it if absent and rejects existing `FTREEDB`, touches `FTREEDB`, asks whether to add a `vicetab` entry, rejects duplicates, prompts for capacity class (`256K`, `1M`, `2M`, `16M`), and appends a matching `ftree width/depth` line with hostname and directory.

State/persistence: creates data directory, creates `FTREEDB`, and appends to `$vicedir/db/vicetab`.

Dependencies, risks, tests: depends on config, hostname, interactive shell, and ftree layout assumptions. Risks include no rollback if `vicetab` append fails after `FTREEDB`, simple `grep "$srvdir"` duplicate detection, symlink acceptance, and only four preset size classes. Test existing FTREEDB rejection, symlink data dir, each size option, duplicate vicetab entry, and no-vicetab path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-srvdir.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-user.in -->
# sources/distributed-fs/coda/coda-src/scripts/vice-setup-user.in

Purpose: initializes Coda protection/authentication data for the first administrative user.

Control flow: loads `server.conf`, enters `$vicedir/db`, prompts for a numeric uid other than 0 or 1 and username other than root/system, backs up existing `prot_users.cdb`, writes a temporary `pdbsetup` script defining `System`, the admin user, `System:Administrators`, and `System:AnyUser`, feeds it to `pdbtool`, removes the setup file, then creates `auth2.pw` from a temporary `passwd.coda` using `initpw` with restrictive umask and default password `changeme`.

State/persistence: modifies protection database and authentication password file in `$vicedir/db`.

Dependencies, risks, tests: depends on `pdbtool`, `initpw`, interactive input, and correct token/password conventions. Risks include default password, username not escaped in command file, old database backup overwritten by rerun, and minimal uid validation. Test uid validation, rejected usernames, backup behavior, restrictive `auth2.pw` permissions, and successful admin authentication after setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup-user.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup.in -->
# sources/distributed-fs/coda/coda-src/scripts/vice-setup.in

Purpose: top-level interactive Coda server setup script for SCM and non-SCM servers.

Control flow: rejects arguments, determines hostname/domain, removes existing `server.conf` after confirmation, locates `server.conf.ex`, prompts for `vicedir`, writes baseline config (`vicedir`, `rvmtruncate`, `trace`), creates standard subdirectories, asks whether this host is SCM. Non-SCM setup writes SCM hostname and update token, fetches required db files from SCM with `updatefetch`, and later runs RVM and srvdir setup. SCM setup prompts for update/auth2/volutil tokens, creates update file lists, touches empty DB placeholders, writes hostname, configures `codatunnel`, runs SCM/user/RVM/srvdir sub-scripts, optionally starts daemons, and optionally creates root volume `/`.

State/persistence: creates server config/tree, token files, update file lists, authentication/protection DBs, RVM areas, server directory, SCM metadata, and optionally starts services/creates root volume.

Dependencies, risks, tests: depends on many generated scripts and daemons (`codaconfedit`, `updatefetch`, `vice-setup-*`, `auth2`, `updatesrv`, `updateclnt`, `startserver`, `createvol_rep`). Risks include highly interactive destructive flow, token handling on terminal, partial setup across many files, direct `/etc/rc.local` edits on BSD, and no transaction/rollback. Test SCM and non-SCM paths in a sandboxed `vicedir`, failed SCM fetch, codatunnel config, sub-script failure propagation, and optional startup/root volume creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/vice-setup.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/volinfo.pl -->
# sources/distributed-fs/coda/coda-src/scripts/volinfo.pl

Purpose: Perl formatter for Coda volume-list records, printing a simple volume overview with size, name, and id.

Control flow: defines a `stripleading` helper to remove the first character from tagged fields, sets Perl output formats, reads lines from stdin, splits fixed fields, strips leading marker characters from name/size/id, converts size from hex, stores size by name in `%volsize`, and writes formatted output.

State/persistence: read-only streaming transform; `%volsize` is process-local and not used after formatting in this script.

Dependencies, risks, tests: depends on old Coda `VolumeList` field layout and Perl formats. Risks include fixed-field parsing, no validation for short/malformed lines, and formatted columns that may truncate long values. Test with representative `volutil getvolumelist` output, malformed lines, hex size conversion, and long volume names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/volinfo.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/volsizes.pl -->
# sources/distributed-fs/coda/coda-src/scripts/volsizes.pl

Purpose: Perl utility that compares sizes of replicated volume replicas using `/vice/db/VRList` and `/vice/vol/BigVolumeList`.

Control flow: reads VRList, pushes volume names into `@VOLUMENAMES`, then reads BigVolumeList, strips leading field markers, removes `.N` replica suffixes, records size for replica numbers 0, 1, and 2 when the base name matches a replicated volume, and finally prints a formatted overview marking rows with `*` when replica sizes differ.

State/persistence: read-only against fixed `/vice` files and process-local hashes for sizes.

Dependencies, risks, tests: depends on Perl, exact VRList/BigVolumeList formats, and at most first three replicas in output. Risks include a stray `shift` inside the VRList loop that mutates `@ARGV`, noisy "Adding" debug output, uninitialized-size comparisons, ignoring replicas 3-7, and hardcoded paths. Test with equal/different three-replica volumes, one/two/eight replicas, missing BigVolumeList, and names with dotted suffixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/scripts/volsizes.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/Makefile.am -->
# sources/distributed-fs/coda/coda-src/smon2/Makefile.am

Purpose: Automake build rules for server monitoring and sizing utilities.

Important declarations: under `BUILD_SERVER`, builds `getvolinfo`, `rpc2ping`, `rvmsizer`, and `smon2` as `bin_PROGRAMS`. `AM_CPPFLAGS` adds RPC2 and Coda base/vicedep include paths. Default `LDADD` links vicedep, base, and RPC2 libraries; `rvmsizer_LDADD` overrides to only link base because it scans local filesystems and does not use RPC2.

Control flow/state: build-time only; no runtime state. Integrates with top-level server conditional and generated build directories.

Dependencies, risks, tests: depends on generated `libvenusdep`, `libbase`, and RPC2 libraries. Risks include installing admin/monitoring tools in `bin` rather than `sbin` if packaging expects privileged utilities elsewhere, and missing Python scripts from build/install declarations. Test with `BUILD_SERVER` enabled/disabled, link of each target, and `make distcheck` inclusion of adjacent scripts if expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/gensrvstats.py -->
# sources/distributed-fs/coda/coda-src/smon2/gensrvstats.py

Purpose: CGI script that generates RRDTool graph images for selected Coda server statistics and emits an HTML page referencing them.

Control flow: prints an HTML header, redirects stderr to stdout, parses CGI fields `servers`, `stats`, and `period`, validates server names against hardcoded `srvmap`, maps period keys through `timemap`, optionally enables logarithmic graphing, changes to `LOGDIR`, opens an `rrdtool -` pipe, and for each requested stat/server writes a graph command using `statmap` definitions and prints an `<IMG>` tag. Exceptions render a traceback in the HTML.

State/persistence: reads `.rrd` databases from `LOGDIR`, writes graph GIFs into `IMGDIR`, and emits HTTP response content. No authentication or mutable application state beyond generated images.

Dependencies, risks, tests: depends on deprecated Python `cgi`, hardcoded hosts/paths/RRDTool version, web-server permissions, and RRD data-source names matching `smon2.c`. Server validation mitigates command injection for server names, but `stat.value` is not checked before indexing `statmap` and may raise tracebacks. Test valid multi-server graphs, invalid server/stat/period, logscale mode, missing RRDTool, and web write permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/gensrvstats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/getvolinfo.c -->
# sources/distributed-fs/coda/coda-src/smon2/getvolinfo.c

Purpose: command-line RPC2 client that queries a Coda server for `ViceGetVolumeInfo` and prints decoded volume/replica mapping details.

Important functions: `Initialize` starts LWP and RPC2 with IPv6 option and 15-second timeout. `Bind` creates an unauthenticated RPC2 binding to host/port/subsystem. `viceaddr` converts stored server addresses to dotted IPv4 text. `main` parses optional `-p port`, resolves default `codasrv/udp`, binds to `SUBSYS_SRV`, calls `ViceGetVolumeInfo`, prints volume id/type, type ids, server count, eight replica/server pairs, and VSG address, then unbinds.

State/persistence: read-only network query; no local persistent writes.

Dependencies, risks, tests: depends on RPC2/LWP, `vice.h`, service lookup, and server availability. Risks include no null check if `coda_getservbyname` fails, IPv4-only address printing despite IPv6-enabled RPC options, fixed eight replica printout regardless `ServerCount`, and open-kimono security. Test default and explicit ports, missing service entry, nonexistent volume, replicated and nonreplicated volumes, and failed bind exit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/getvolinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/rpc2ping.c -->
# sources/distributed-fs/coda/coda-src/smon2/rpc2ping.c

Purpose: simple health-check utility that verifies an RPC2 binding can be established to a Coda server.

Important functions: `Initialize` initializes LWP/RPC2 with IPv6 option and timeout; `Bind` creates an unauthenticated binding to host/port/subsystem; `main` parses optional `-p port`, otherwise uses `codasrv/udp` and `SUBSYS_SRV` numeric id, attempts bind/unbind, prints success or failure, and exits `0` on success, `2` on critical bind failure, `1` on usage error.

State/persistence: no persistent state; network-only probe.

Dependencies, risks, tests: depends on RPC2, LWP, service lookup, and DNS. It only detects bindability, not application-level server health. Risks include no check for missing service lookup, fixed subsystem id literal, and unauthenticated open binding. Test success/failure exit codes, explicit port, DNS failure, server down, and monitoring integration expecting Nagios-style critical code 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/rpc2ping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/rvmsizer.c -->
# sources/distributed-fs/coda/coda-src/smon2/rvmsizer.c

Purpose: estimates Coda RVM metadata requirements for a local file tree.

Important functions/constants: `scantree` walks roots with `fts_open` using physical, cross-device-limited traversal. It counts directories as large vnodes, files/symlinks/default entries as small vnodes, totals file and directory sizes, estimates directory pages based on padded directory entry sizes and page overhead (`DIRPAGE`, `DIRNONNAME`, `PAGELOSS`), warns if a directory would require at least 128 pages, and prints RVM estimates based on directory pages plus vnode constants (`FILERVMSIZE`, `DIRSIZE`) and the old 4% rule. `main` accepts `[-v] [--] dir`, though verbosity is parsed but unused.

State/persistence: read-only filesystem scan; no writes.

Dependencies, risks, tests: depends on Coda `coda_fts` wrappers and POSIX stat data. Risks include division by zero for empty/no-file or no-directory cases, continuing after `fts_read` errors with `errno` handling, unused verbosity, and heuristic constants that may drift from current on-disk structures. Test empty directories, large trees, unreadable directories, symlink handling, crossing filesystem boundary, and average calculations with zero small files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/rvmsizer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/smon2.c -->
# sources/distributed-fs/coda/coda-src/smon2/smon2.c

Purpose: Coda server monitor that queries `ViceGetStatistics` and emits RRDTool commands for database creation and updates.

Important functions: `RRDCreate` prints the `create <server>.rrd` command with data-source and archive definitions. `RRDUpdate` prints an `update` line using the `ViceStatistics` fields for RPC, fetch/store, CPU, VM, fault, workstation, and disk metrics. `ValidServer` resolves server names for `codasrv/udp`. `GetArgs` parses `-t` interval and `-1` one-shot mode, validates up to `MAXSRV` servers. `InitRPC` starts LWP, SFTP, and RPC2. `DoProbe` lazily binds to each server, calls `ViceGetStatistics`, and resets bindings on failure. `srvlwp` probes in a loop per server and signals the parent on exit.

State/persistence: writes RRDTool commands to stdout, intended to pipe into `rrdtool -`; stores per-server process-local connection/stat state. No direct files are written except by downstream RRDTool.

Dependencies, risks, tests: depends on RPC2/LWP/SFTP, `vice.h`, service lookup, and RRDTool command compatibility with `gensrvstats.py`. Risks include passing address of loop variable `i` into `LWP_CreateProcess`, race-prone global `SrvCount` decrement, no locking around stdout, and no service lookup null check. Test one-shot and looping modes, multiple servers, failed/recovered bindings, missing RRD creation, and RRD data-source count alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/smon2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/volusage.py -->
# sources/distributed-fs/coda/coda-src/smon2/volusage.py

Purpose: Python utility that lists per-volume usage and activity from a server's `volutil getvolumelist` output.

Control flow: parses positional `host` and optional `--volutil`, runs `volutil -h <host> getvolumelist`, splits output lines, ignores short lines, extracts volume name, usage from hex field 6, partition from field 3, and activity from hex field 11, sorts by tuple `(partition, usage, volume, activity)`, and prints tabular lines.

State/persistence: read-only subprocess query; no local writes.

Dependencies, risks, tests: depends on Python 3, `volutil`, exact volume-list field layout, and successful command exit. Risks include uncaught `CalledProcessError`, uncaught `ValueError` on malformed hex fields, and no filtering by volume type. Test with fixture output containing partitions, short/malformed lines, high usage sorting, alternate volutil path, and server command failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/smon2/volusage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/Makefile.am -->
# sources/distributed-fs/coda/coda-src/update/Makefile.am

Purpose: Automake build rules for the Coda update service programs and RPC2-generated stubs.

Important declarations: under `BUILD_SERVER`, builds `updateclnt`, `updatefetch`, and `updatesrv` as `sbin_PROGRAMS` and installs `updateclnt.8`/`updatesrv.8`. `RPC2_FILES = update.rpc2` plus `rpc2_rules.mk` generates client/server/helper sources and `update.h`. Each program has a hand-written source plus `nodist_*` generated RPC2 files. `AM_CPPFLAGS` adds RPC2, base, util, and vicedep include paths. `LDADD` links vice errors, volutil dependencies, util, base, and RPC2 libraries.

Control flow/state: build-time only. It controls generated source inclusion and link dependencies for the update protocol.

Dependencies, risks, tests: depends on RPC2 code generation and top-level build products. Risks include generated-source dependency ordering, all three programs sharing broad link dependencies, and no installed manpage for `updatefetch`. Test clean builds from generated-free tree, `make distcheck`, server-disabled builds, and relinking after `update.rpc2` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/updateclnt.cc -->
# sources/distributed-fs/coda/coda-src/update/updateclnt.cc

Purpose: long-running update client that synchronizes server database files from the SCM `updatesrv` and notifies the local Coda file server when databases change.

Important functions: `main` parses options, reads `server.conf`, obtains SCM host from `-h` or `db/scm`, ensures local `/vice` structure, detaches, installs signals, logs to `misc/UpdateClntLog`, initializes RPC/SFTP, then loops reconnecting and checking `db`. `CheckDir` fetches the `files` list, processes additions and deletion entries prefixed with `-`, and calls `CheckFile`. `CheckFile` stats local files, uses `UpdateFetch` with local mtime, receives `.UPD` via SmartFTP when newer, rotates existing file to `.BAK`, renames new file into place, chmods/utimes it, tracks remote clock skew, and returns whether updates occurred. `ReConnect` binds to `SUBSYS_UPDATE` using `db/update.tk`; `U_BindToServer` binds to the file server utility subsystem using `volutil.tk` for `VolUpdateDB`.

State/persistence: creates local `misc/db/srv/vol/spool` directories, writes pid/log files, updates database files under `db`, maintains `.BAK` backups and `.UPD` temps, and may trigger server database reload. It stores no durable cursor except file mtimes/backups.

Dependencies, risks, tests: depends on RPC2/SFTP, update RPC stubs, `codaconf`, `vice_file`, token secrets, and time synchronization. Risks include fixed-size buffers and `strcpy`/`strcat`, partial file updates around rename failure, unactioned clock skew warning, `ReadOnlyAllowed` default disabling write-protection skip, and polling forever with no backoff beyond wait interval. Test initial full sync, incremental mtime sync, deletion entries, interrupted `.UPD`, bind failure/reconnect, `VolUpdateDB` notify, signal handlers, and SCM/local clock skew.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/updateclnt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/updatefetch.cc -->
# sources/distributed-fs/coda/coda-src/update/updatefetch.cc

Purpose: one-shot client to fetch a single file from an SCM `updatesrv` using the same update RPC and token mechanism as `updateclnt`.

Important functions: `ReadConfigFile` initializes the configured `vicedir`. `ProcessArgs` requires `-h server`, `-r remote`, and `-l local`, with optional debug and port. `U_InitRPC` initializes LWP/RPC2/SFTP. `Connect` binds to `SUBSYS_UPDATE` on `codasrv-se/udp` or explicit port using `db/update.tk` and AUTHONLY/XOR. `FetchFile` opens a SmartFTP `FILEBYNAME` side effect to `LocalFileName`, calls `UpdateFetch` with time zero to force transfer, and unlinks the local file on failure. `main` creates/truncates the local file before fetching.

State/persistence: writes the requested local file and may delete it on transfer error. It reads server config and update token.

Dependencies, risks, tests: depends on RPC2/SFTP, generated update client stubs, token secret, and writable local path. Risks include truncating/creating the local destination before successful fetch, fixed-size host/filename copies, no parent-directory creation, and no atomic temp/rename behavior unlike `updateclnt`. Test successful fetch, auth failure, missing token, remote missing, local unwritable path, explicit port, and preserving existing local file on failure if behavior is changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/update/updatefetch.cc -->
