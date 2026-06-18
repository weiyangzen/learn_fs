# subset-b-007950 Research

This grouped report covers the requested XRootD XrdOssArc archive-storage and XrdOssCsi checksum-sidecar files. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.hh

Purpose: declares `XrdOssArcFSMon`, the filesystem-space admission controller used by archive backup workers. It is an `XrdJob` scheduled periodically to refresh filesystem size/free counters and to release blocked backup tasks when enough space is available.

Important APIs/types: `Init(path, fVal, fsupdt)` initializes path, free-space policy, and refresh cadence; `Permit(XrdOssArcBackupTask*)` reserves bytes for a backup or queues the task; `Release(size_t)` releases reserved bytes and posts waiting task semaphores; `DoIt()` is the scheduled refresh hook; `getFSpace()` is the platform statfs wrapper. State is guarded by `rmMutex` and includes `btWaitQ`, `fs_inBkp`, `fs_inUse`, `fs_MaxUsed`, `fs_MinFree`, `fs_Free`, and `fs_Size`.

Control/state behavior: the monitor computes `fs_MaxUsed = fs_Size - fs_MinFree`, treats in-flight backups as committed bytes, and drives waiters in FIFO order after releases. Persistence is external: only live process memory is tracked; filesystem facts come from `statfs`.

Dependencies/integration: depends on `XrdJob`, `XrdSysMutex`, scheduler globals, and `XrdOssArcBackupTask` fields such as `numBytes`, `relSpace`, and `btSem`. Risks are stale accounting between refresh intervals, queued tasks that depend on correct `Release()` calls, and platform `statfs` differences. Test signals should include percentage and absolute free-space policy, queue wake-up ordering, failed statfs handling, and concurrent permit/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.cc

Purpose: implements the archive-aware file object that wraps an underlying OSS file descriptor and optionally redirects reads to a member inside a zip archive. It is the request-time bridge from XRootD open/read/write/fstat calls to archived dataset restoration.

Important APIs/functions: `Open()` classifies the path via `XrdOssArcCompose`, forwards non-archive paths to `ossDF`, stages the backing archive through `XrdOssArcStage::Stage()`, promotes archive-file opens by setting an already-open fd through `Fctl_setFD`, or constructs `XrdOssArcZipFile` for member access. `Close()`, `Fstat()`, `Read()`, and `Write()` dispatch to either the zip member or the underlying OSS file. `getErrMsg()` merges thread-local archive extended errors with lower OSS errors.

Control flow: open first determines whether the path is outside the archive namespace, invalid, the archive itself, or a member. Restore requests run under a child `XrdOssArcStopMon` shared lock so STOP/IDLE drain control can pause restores. Stage returns `EINPROGRESS` as configured wait-policy code `Config.wtpStage`; other errors are negated.

State/dependencies: owns `ossDF` and nullable `zFile`. It depends on `XrdOssArcCompose`, `Config`, `Elog`, `ecMsg`, `XrdSysFD_Open`, and libzip through `XrdOssArcZipFile`. Risks include sign normalization (`Neg()`), promotion fd ownership on `Fctl_setFD`, read-only zip semantics, and member path composition. Test signals: non-archive forwarding, archive-file open, missing member errors with extended messages, stage-in-progress mapping, and write rejection for archive members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.hh

Purpose: declares `XrdOssArcFile`, an `XrdOssWrapDF` subclass that presents archived content through the normal XRootD OSS file interface. It preserves the base OSS file contract while adding zip-member reads and archive staging in the implementation.

Important APIs/types: overrides `Open`, `Close`, `Fstat`, `getErrMsg`, `Read(buffer, offset, size)`, and `Write`. The preread overload `Read(off_t,size_t)` is a no-op returning 0. The constructor takes a thread identity and an already-created `XrdOssDF*`; the destructor owns and deletes that file object plus any active `XrdOssArcZipFile`.

Control/state behavior: `ossDF` is always present for forwarding and base-file operations. `zFile` is null for normal or whole-archive opens and non-null when a member inside an archive is open; this boolean state controls dispatch for close, stat, read, and write. Persistence remains in the underlying OSS and archive file; the wrapper holds only per-open process state.

Dependencies/integration: integrates with `XrdOssWrapper.hh` and forward-declares `XrdOssArcZipFile`, `XrdOucEnv`, and `stat`. Risks include ownership clarity for `ossDF`, no-op preread silently dropping cache hints, and write behavior differing by `zFile` state. Tests should cover lifecycle deletion, calls before/after member open, and wrapper behavior under read-only archived members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.cc

Purpose: implements asynchronous staging of archive files from a mass-storage-system buffer into the local online tier. It deduplicates concurrent staging requests for the same archive path and limits active staging jobs by `Config.maxStage`.

Important APIs/functions: `Stage(path, mssPath)` is the entry point used by archive opens. It checks the `Active` set, asks `isOnline(mssPath)` through `Config.MssComProg->Run("online", path)`, inserts a copied path into `Active`, schedules a `XrdOssArcStage` job when concurrency is available, or pushes a path into `Pending`. `DoIt()` opens the archive path to force staging, records errors with `StageError()`, drains queued paths, removes active entries through `Reset()`, then self-deletes. `isOnline()` maps `XrdOucProg` negative status conventions back to `MssRC`.

State/control: global `Active` stores `ActInfo` records keyed by path and error code; `Pending` queues path pointers owned by active records; `stageMtx` protects active state and `schedMtx` protects staging slots/queue. Persistence is in the MSS/cache state, not the process.

Dependencies/integration: uses `XrdScheduler`, `XrdOucProg`, `XrdSysFD_Open`, `Config.MssComName`, `Config.maxStage`, and tracing. Risks include pointer lifetime coupling between `Active` and `Pending`, lock ordering mistakes, `StageError()` checking an iterator after unlocking, and `Config.maxStage++` relying on `schedMtx` still being held after the loop break. Tests should simulate duplicate requests, stage failure propagation, queue draining, and online/offline/invalid MSS status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.hh

Purpose: declares the scheduled job used for archive staging. The class is intentionally small: it stores the active archive path and exposes static helpers used by the file wrapper before archive access.

Important APIs/types: `enum MssRC { isBad=-1, isFalse=0, isTrue=1 }` represents MSS online checks. `static isOnline(const char*)` wraps the configured MSS command. `static Stage(const char* path, const char* mssPath)` starts or observes staging for an archive and returns 0, `EINPROGRESS`, or an errno. `DoIt()` runs the scheduled stage operation. Private `Reset()` changes the active path and removes completed entries from the active set; `StageError()` records an error code for later callers.

Control/state behavior: object instances are scheduled jobs and self-delete in the implementation. `arcvPath` is valid only while the path is present in the global active set; this comment is important because queued work reuses path pointers from copied `ActInfo` records.

Dependencies/integration: depends on `XrdJob` and C string helpers. It is called by `XrdOssArcFile::Open()` before archive or member access. Test signals should verify idempotent return for already-active paths, status after failed staging, and safe object lifetime through pending queue transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.cc

Purpose: implements administrative stop/drain behavior for archive backup and restore work. A parent monitor watches an admin directory for a `STOP` file; child instances acquire shared locks around active operations so the parent can wait for drain and create an `IDLE` marker.

Important APIs/functions: the parent constructor opens the admin path as a directory, removes stale `IDLE`, and schedules periodic `DoIt()`. The child constructor shares the parent's `XrdSysXSLock` and locks it shared. `DoIt()` checks `STOP` with `fstatat`, takes the exclusive lock, creates `IDLE`, sleeps until `STOP` disappears, removes `IDLE`, releases the lock, and reschedules. The destructor aborts if a fully constructed parent is deleted; child destruction calls `Deactivate()`.

State/control: `admDirFD >= 0` marks the parent. The lock serializes global stop state versus per-operation shared activity. Persistence is filesystem-signaled through `STOP` and `IDLE` files in `admPath`.

Dependencies/integration: uses `XrdScheduler`, `XrdSysXSLock`, `XrdSysFD_Open`, `XrdSysTimer`, POSIX `openat/unlinkat/fstatat`, and `Elog`. Risks include indefinite sleep while STOP remains, abort-on-parent-delete behavior, constructor failure cleanup, and dependency on admin directory lifetime. Tests should cover STOP detection, IDLE creation/removal, child lock blocking, parent deletion guard, and permission errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.hh

Purpose: declares the stop monitor/job used to pause archive activity without abruptly killing workers. It supports a long-lived parent scheduler job and short-lived child guards around operations.

Important APIs/types: `DoIt()` is parent-only. `Activate()` and `Deactivate()` manage a shared lock, guarded by `RAtomic_bool isActive` to avoid duplicate lock/unlock. The parent constructor takes admin path, check interval, and success output flag. The child constructor takes a parent pointer, aliases its `xsLock`, marks itself active, and immediately locks shared. Copy/assignment are deleted.

Control/state behavior: parent owns an open admin directory and scheduled polling; children own only shared lock participation. The exclusive parent lock is acquired only in the implementation when STOP appears. Persistence is file-based via STOP/IDLE, while lock state is in process memory.

Dependencies/integration: depends on `XrdJob`, `XrdSysRAtomic`, and `XrdSysXSLock`; `XrdOssArcFile::Open()` uses child instances to wrap restore/stage decisions. Risks include parent lifetime assumptions, manual activation discipline if child instances are reused, and process abort on invalid parent destruction. Test signals: RAII child construction/destruction, repeated `Activate`/`Deactivate`, and lock contention with simulated STOP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcTrace.hh

Purpose: defines XrdOssArc trace masks and convenience macros for debug/save/all tracing. It centralizes trace access through the global `XrdOssArcGlobals::ArcTrace`.

Important APIs/macros: masks include `TRACE_All`, `TRACE_Debug`, `TRACE_Save`, and `TRACE_None`. `TraceInfo(x,y)` declares per-function `TraceEP` and `TraceID`. `TRACE(act,x)`, `TRACEI(act,x)`, `TRACING(x)`, and `DEBUG(x)` wrap `SYSTRACE` when the relevant bit is enabled. `XRDOSSARC_TRACE` can be overridden but defaults to `XrdOssArcGlobals::ArcTrace.` including the trailing member access dot.

Control/state behavior: no persistent state is declared here beyond the external trace object. Call sites must invoke `TraceInfo` before `DEBUG`/`TRACE` so `TraceEP` and `TraceID` are in scope.

Dependencies/integration: includes `XrdSysHeaders.hh` and `XrdSysTrace.hh`; used across staging, filesystem monitor, backup, and config code. Risks are macro hygiene, confusing `TRACE_All` mask excluding the low debug/save bits by value, and compile-time dependence on variable names. Tests are mostly build-time and runtime trace-level checks: verify macros compile in representative functions and that config trace settings emit or suppress expected diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.cc

Purpose: implements read-only access to a member inside a zip archive while presenting stat/read behavior needed by `XrdOssArcFile`. It converts libzip errors into negative errno values and logs archive/member-specific diagnostics.

Important APIs/functions: the constructor opens the archive path read-only, snapshots `stat`, stores the path, and converts the fd to `zip_t` with `zip_fdopen(ZIP_CHECKCONS)`. `Open(member)` closes any previous member, stores the member name, opens it with `zip_fopen`, and currently assumes seekability. `Read()` seeks if needed, reads with `zip_fread`, tracks `zOffset`, and returns EOF after short reads. `Stat()` variants copy archive `stat` then replace inode/size when libzip supplies them. `Close()` closes member state; destructor closes member/archive and frees strings. `zip2syserr()` maps libzip error codes.

State/control: mutable state includes archive pointer, subfile pointer, member name, offset, seekability, and EOF. Persistence is entirely the zip archive on disk.

Dependencies/integration: depends on libzip, `XrdSysFD_Open`, `XrdSysError`, and `XrdOucString`. Risks include assuming compressed members are seekable because older libzip lacks `zip_file_is_seekable`, EOF state reset only on seek/open, mixed sign convention in constructor `rc = -errno`, and `zip_error_fini()` ownership expectations. Tests should cover missing archive/member, stat propagation, random reads, sequential reads, compressed member behavior, and destructor cleanup after failed opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.hh

Purpose: declares a small libzip-backed file facade for archive members. It is not an OSS subclass; it is an internal helper used by `XrdOssArcFile` when the logical open targets a member inside an archive.

Important APIs/types: public methods are `Open(member)`, `Read(buff, offset, blen)`, `Stat(struct stat&)`, `Stat(member, struct stat&)`, and `Close()`. The constructor reports initialization through an `int& rc`, and the destructor closes all libzip resources. Private helpers `zipEmsg()` and overloaded `zip2syserr()` convert/log libzip errors.

State/control behavior: the class stores archive-level stat in `zFStat`, path/member strings, `zip_t*`, `zip_file_t*`, `zOffset`, `zSeek`, and `zEOF`. `zSeek` controls random-read behavior and `zEOF` suppresses repeat reads after EOF. There is no locking; instances are per-open and expected to be single-client.

Dependencies/integration: forward declares libzip structs and `stat`, keeping libzip details out of callers. Risks include constructor error reporting rather than throwing, raw pointer ownership, and no copy prevention despite owning C handles. Test signals: lifecycle under failed constructor/open, member switching, stat with and without active subfile, and correct negative errno mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Archiver -->
# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Archiver

Purpose: Python utility invoked by archive backup workers to turn staged dataset split directories into one or more uncompressed zip archives and save them into a tape/MSS buffer or via an external saver command.

Important APIs/functions: `arcDirs(dsnDir)` validates contiguous `~1`, `~2`, ... source directories. `arcZip(arcDir, arcFN)` runs `zip -r -0` from inside each split directory, creates the archive in the parent directory, and chmods it read-only. `arcSave(tapDir, arcFN)` creates the target directory and copies the archive with metadata. `Main(argv)` parses `<dsnDir> <tapDir> <arcName> [copy_cmd]`, builds per-split archive names as `<base><n>-<count>.<ext>`, and either copies locally or runs `[copy_cmd, "save", tapDir] + arcList`.

State/persistence: creates/removes archive files in the dataset arena, writes archive copies under `tapDir`, and uses read-only mode as a completion marker. Debug behavior is controlled by `XRDOSSARC_DEBUG`; value greater than `1` sets `DKeep` but the variable is not used in this script.

Dependencies/integration: depends on system `zip`, Python `shutil`, `subprocess`, and XrdOssArc backup invocation. Risks include shell command construction for `zip`, archive names needing an extension, strict contiguous split numbering, and incomplete cleanup on failures. Tests should cover one/many split dirs, missing `~1`, zip return-code mapping, external saver failures, and path/name normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Archiver -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_BkpUtils -->
# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_BkpUtils

Purpose: Python Rucio helper for archive backup orchestration. It manages metadata keys, lists closed datasets needing backup, creates symlink arenas and optional manifests, reports DID stat data, resolves which archive contains a file, and marks backup completion.

Important APIs/functions: commands include `addkey`, `list`, `qkey`, `set`, `setup`, `finish`, `stat`, and `which`. `Get_lfns()` lists and sorts dataset files, optionally preserving checksums named by `XRDOSSARC_CKSUM`. `Get_lfn2pfn()` resolves PFNs for an RSE in batches controlled by `XRDOSSARC_MAXITEMS`. `Setup()` cleans/recreates the arena, creates `~n` symlink trees via `arcSymlink()`, optionally writes a manifest, splits archives according to `XRDOSSARC_SIZE` through `arcSplit()`, and prints total files/bytes. `Which()` uses `arcIndex` metadata to map a file ordinal to an archive name. `Stat()` emits CGI-style mode/uid/gid/size/time attributes.

State/persistence: mutates Rucio metadata (`arcBackup`, `arcIndex`, configured finish key), writes arena symlinks, optional manifest files, and removes arenas on finish. It depends on Rucio clients and local filesystem reachability of PFNs.

Risks/integration: several error paths appear malformed, including `Set_Backup("arcBackup",...)` called with the wrong shape in one branch and formatting chained after `Emsg()` calls; `xeq_Finish()` removal is nested under debug logging, so non-debug cleanup may be skipped. Tests should mock Rucio clients for metadata and replica batching, verify split ordinal math, ensure arena cleanup, and exercise malformed environment values and missing PFNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_BkpUtils -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Manifest -->
# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Manifest

Purpose: Python helper that lists Rucio dataset contents in a simple line protocol for archive composition or inspection. Invocation is `XrdOssArc_Manifest ls <scope>:<dataset>`.

Important APIs/functions: `Decompose(dsn)` splits a Rucio DID into scope and name. `getClient()` constructs `DIDClient`. `do_LS()` calls `client.list_files(scope, did)` and prints each file as `scope:name`, followed by `===` as an end marker. `Main()` dispatches only the `ls` command.

State/persistence: no local persistence; all state comes from the Rucio catalog and stdout. Debug flag `XRDOSSARC_DEBUG` is parsed but not materially used beyond setting `Debug`.

Dependencies/integration: depends on `rucio.client.didclient.DIDClient` and is intended to be configured as a utility under XrdOssArc. Risks include `Decompose()` printing instead of calling `Emsg()` on invalid input, so malformed names may cause downstream unpacking errors; all Rucio exceptions are collapsed to `ENOENT` if text contains `not found` and `ECANCELED` otherwise. Test signals: valid listing order/content, invalid DID syntax, dataset not found, Rucio client construction failure, and `===` termination for consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Manifest -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_MssCom -->
# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_MssCom

Purpose: Python command adapter between XrdOssArc and a mass storage system command, defaulting to an `hsi` invocation. It reports online/offline status, saves files, and requests migration/eviction.

Important APIs/functions: `Execute(argvec)` runs the command and captures combined output. `do_Status(path)` runs `ls -X` and parses `(disk)` and `(tape)` sections into booleans. `do_Save()` creates target directories and uploads local archive files via an MSS command string. `do_Evict()` builds a `mig -P` request for paths but currently does not return or check the result. `Main()` supports `evict`, `offline`, `online`, `save`, and `status`; boolean returns are used as process exit statuses, so `online` returns 1 when on disk and 0 when not.

State/persistence: changes MSS state through save/evict commands. `MSS_CMD` and `MSS_ROOT` come from `XRDOSSARC_MSSCMD` and `XRDOSSARC_MSSROOT`, with site-specific defaults.

Dependencies/integration: `XrdOssArcStage::isOnline()` consumes the `online` exit code through `XrdOucProg`, while `XrdOssArc_Archiver` can use this script as an external saver. Risks include simplistic `split(" ")` for command templates, fragile parsing of `ls -X`, missing `result` initialization if `subprocess.run` raises before assignment, and unchecked evict failures. Tests should mock command output for disk/tape/no-data states and verify exit-code semantics expected by C++ staging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_MssCom -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Weka -->
# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Weka

Purpose: Python advisory helper to prefetch or release Weka tiered-storage data referenced by an archive manifest. Commands are `prepare <scope> <manifest>` and `dispose <scope> <manifest>`.

Important APIs/functions: `get_Manifest()` reads the first line of the manifest and parses it with `ast.literal_eval`; the expected rows include PFNs at index 1. `Wekafy(action, argv)` extracts PFNs, batches them in groups of 100, and runs either `weka fs tier fetch` or `weka fs tier release`. `Main()` dispatches `prepare` and `dispose`. Debug mode appends `-v` to Weka commands.

State/persistence: no metadata persistence, but it can change Weka tier residency. The script deliberately exits 0 from `Emsg()` even on failures because it treats Weka actions as advisory resource hints rather than correctness gates.

Dependencies/integration: depends on `weka` CLI and manifest format created by backup setup. The source uses `subprocess.run` inside `Execute()` but does not import `subprocess`, so any execution path would raise `NameError`; `get_Manifest()` references `manFN` instead of `ManFN` in one error path. Tests should cover missing import, manifest parsing, batching, advisory success semantics, and CLI argument validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Weka -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/CMakeLists.txt

Purpose: builds the XrdOssCsi OSS plugin module named `XrdOssCsi-${PLUGIN_VERSION}` and installs it under the library directory.

Important build surface: the module includes checksum-sidecar core files (`XrdOssCsi.cc/.hh`, config, CRC utilities, file/AIO, pages, unaligned pages, ranges, tagstore file, trace, and handler headers). It links privately against `XrdUtils` and `XrdServer`. The installed artifact is a `MODULE` library, matching XRootD plugin loading conventions rather than a normal shared library linked by applications.

Integration/dependencies: source list shows that the requested files are only part of the plugin; important behavior also lives in `XrdOssCsiPagesUnaligned.cc`, `XrdOssCsiRanges.cc/.hh`, and `XrdOssCsiTagstoreFile.cc/.hh`. The exported plugin entry point is implemented in `XrdOssCsi.cc` as `XrdOssAddStorageSystem2`.

Risks/test signals: build risks are missing source list updates when adding new CSI components, ABI coupling to `${PLUGIN_VERSION}`, and hidden dependency on lib/server symbols supplied by XRootD. Test signals are CMake configure/build of the module, plugin loading in an XRootD server, and installation path verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.cc

Purpose: implements the top-level checksum-sidecar OSS wrapper. It hides checksum tag files from clients, creates `XrdOssCsiFile`/`XrdOssCsiDir` handlers, coordinates data-file operations with their tag files, and exports the plugin entry point.

Important APIs/functions: `newDir()` and `newFile()` wrap successor objects unless `tident` starts with `*`. `Init()` initializes config and scheduler. Directory `Opendir/Readdir` suppress tag paths. File-system operations reject direct tag-file paths. `Create()` ensures zero-length data files get matching empty tag files. `Unlink()` removes data and tag files under the per-file map lock. `Rename()` locks old/new tag map entries, renames data, creates destination tag directories, renames/unlinks tag files, and updates `pumap_`. `Truncate()` opens a CSI file and delegates `Ftruncate()`. `StatPF()` opens the file to report checksum verification bits.

State/persistence: persistent state is the data file plus tag file tree. In-memory map entries are shared through `XrdOssCsiFile::pumap_` to serialize open-file operations. `tagOpenEnv()` clones open environment, sets tag cgroup/space, and estimates allocation size for tag files.

Risks/test signals: rename/unlink recursion when map entries are stale, tag directory creation rollback, hidden tag paths, `StatPF` open cost, and consistency under concurrent opens. Tests should cover direct tag-file denial, create/truncate/open interactions, rename over existing files, missing tag files, and scheduler fallback when no scheduler is supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.hh

Purpose: declares the public classes of the checksum-sidecar plugin: directory wrapper, file wrapper, AIO object pool, and top-level OSS handler.

Important APIs/types: `XrdOssCsiDir` wraps `Opendir/Readdir` to hide tag files. `XrdOssCsiFile` overrides normal, vector, async, and page read/write methods plus flush, fsync, fstat, truncate, and verification status. It owns a shared `puMapItem_t` containing refcount, mutex, page manager, data/tag paths, and unlink marker. Static `mapTake/mapRelease` and `pumap_` coordinate all opens by tag path. AIO lifecycle is counted by `aioInc/aioDec/aioWait`. `XrdOssCsi` extends `XrdOssHandler`, adjusts feature flags to add filesystem checksums, page read/write, and no-sendfile, and exposes `tagOpenEnv()`.

State/control: `XrdOssCsiFile` has `rdonly_`, parent OSS pointer, tident, config reference, shared page state, and AIO object store. Close waits for all AIOs before releasing page state. The map refcount is separate from `shared_ptr` lifetime and drives removal from `pumap_`.

Dependencies/integration: depends on XRootD OSS interfaces, scheduler, config, pages, and handler abstractions. Risks include refcount correctness, deadlock around AIO waiters, feature flag accuracy, and raw `const char* tident` lifetime. Tests should stress concurrent opens, close while AIOs run, readonly/write transitions, and map removal after unlink/rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.cc

Purpose: implements runtime configuration parsing for the checksum-sidecar plugin. It handles plugin parameters, reads `csi.*` directives from the XRootD config file, and reports effective settings.

Important APIs/functions: `Init()` parses space-separated plugin parameters: `nofill`, `space=<name>`, `nomissing`, `prefix=<path-or-empty>`, `nopgextend`, and `noloosewrites`. It initializes trace defaults, honors `XRDDEBUG`, calls `readConfig()`, and logs outcomes. `readConfig()` opens the config file with `XrdOucStream`, captures plugin config blocks, and dispatches `csi.` directives. `ConfigXeq()` currently supports `trace`. `xtrace()` parses `all`, `debug`, `warn`, `info`, and `off`, including negative options to clear bits.

State/persistence: mutates `XrdOssCsiConfig` booleans, tag prefix, tag-file space name, and global `OssCsiTrace.What`. No persistent files are written.

Dependencies/integration: uses `XrdOucStream`, `XrdSysError`, `XrdOssCsiTrace`, and POSIX `open`. Risks include simplistic whitespace parameter parsing, unknown parameters silently ignored, config file absence treated as defaults but open errors fatal, and trace directive limited to config-file `csi.trace`. Tests should cover every parameter combination, invalid prefix, trace add/remove semantics, config-file read errors, and default logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.hh

Purpose: declares configuration and tag-path naming rules for XrdOssCsi. `TagPath` maps client-visible data paths to hidden checksum tag paths and detects tag-file paths that should be hidden or rejected.

Important APIs/types: `TagPath::isTagFile()` detects either prefix-tree tag files or suffix-based tag files when prefix is empty. `SetPrefix()` validates empty or absolute prefix. `makeBaseDirname()` maps data directories to tag directories; `matchPrefixDir()`/`getPrefixName()` support directory listing suppression; `makeTagFilename()` maps data files to tag files. `simplePath()` normalizes slashes and leading/trailing slash behavior. `XrdOssCsiConfig` exposes `Init()`, `fillFileHole()`, `xrdtSpaceName()`, `allowMissingTags()`, `disablePgExtend()`, `disableLooseWrite()`, and public `tagParam_`.

State/control: defaults are prefix `/.xrdt`, suffix `.xrdt`, fill file holes enabled, tag space `public`, missing tags allowed, pg extension enabled, and loose writes enabled. Path mapping preserves whether the caller gave an absolute path when constructing relative tag filenames.

Risks/test signals: path normalization is central and easy to regress; prefix-empty mode changes hiding from prefix tree to suffix matching. Tests should cover absolute/relative paths, double/trailing slashes, root path, empty prefix, prefix directory listing suppression, invalid relative prefix, and tag filename creation for nested files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.cc

Purpose: defines the static zero-filled page buffer used by CRC utility routines. The implementation file contains only `XrdOssCsiCrcUtils::g_bz[XrdSys::PageSize] = {0}`.

Important APIs/state: the buffer supports zero-extension, split, and combine operations in the header. It is sized to the XRootD system page size, matching the plugin's checksum granularity.

Dependencies/integration: includes `XrdOssCsiCrcUtils.hh`, which in turn depends on `XrdOucCRC` and `XrdSysPageSize`. This file must be linked into the plugin exactly once to satisfy the static member definition.

Risks/test signals: risk is low but build-sensitive; omitting this source would produce unresolved symbols, while multiple definitions would break linkage. Runtime tests should indirectly verify zero-fill CRC operations through page extension and unaligned writes. Unit-level checks can compare `crc32c_extendwith_zero()` against direct `Calc32C` over explicit zero bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.hh

Purpose: provides CRC-32C algebra helpers for page checksum manipulation without rereading full data in every case. It assumes operations are within one `XrdSys::PageSize` page.

Important APIs/functions: `crc32c_combine(crc1, crc2, len2)` returns the CRC of data1 concatenated with data2 by advancing crc1 through zero bytes then XORing crc2. `crc32c_split1(crctot, crc2, len2)` recovers the first segment CRC by reversing through polynomial shifts. `crc32c_split2(crctot, crc1, len2)` recovers the second segment CRC. `crc32c_extendwith_zero(crc, len)` appends zero bytes. Static `g_bz` supplies zero bytes and `CrcPoly` is the reversed iSCSI polynomial.

State/control: all methods are static and assert `len <= PageSize`; they do not allocate or persist state.

Dependencies/integration: used by unaligned page update logic to combine/split partial-page CRCs. Risks include debug-only assertions for oversize lengths, subtle complement/XOR conventions tied to `XrdOucCRC::Calc32C`, and performance comments noting possible optimizations. Tests should use known CRC vectors, random split/combine round trips, zero-length cases, and page-size boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFile.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFile.cc

Purpose: implements the per-open checksum-enforcing file wrapper. It opens the data file and associated tag file, verifies reads, updates/stores checksums on writes, and keeps shared per-tag `XrdOssCsiPages` state consistent across concurrent opens.

Important APIs/functions: `pageAndFileOpen()` takes/locks the map item, opens the successor data file, and creates shared pages. `createPageUpdater()` opens or creates the tag file and wraps it with `XrdOssCsiTagstoreFile`/`XrdOssCsiPages`. `Read`, `ReadRaw`, and `ReadV` lock ranges, read data, then call `VerifyRange()`. `Write` and `WriteV` update page metadata before writing data and resync sizes on failures. `pgRead` fetches checksum vectors; `pgWrite` validates optional checksum vectors, stores them, and writes data. `Ftruncate`, `Fstat`, `Fsync`, `Flush`, and `VerificationStatus` delegate through page state.

State/control: `pumap_` maps tag paths to refcounted shared map items. `Close()` waits for AIO completion, closes page map state when last holder releases, then closes the successor. Page range locks are acquired before data operations to serialize checksum metadata and data visibility.

Risks/test signals: write metadata is updated before underlying data writes, so failure paths rely on `resyncSizes()` and range release; zero/short writes could loop if successor returns 0 during write; open with truncate while pages exist returns `-EDEADLK`; compressed files are rejected. Tests should cover aligned/unaligned reads and writes, failure injection for writes/tag opens, concurrent opens, readonly tag fallback, missing tags policy, truncation, and pgRead/pgWrite checksum modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.cc

Purpose: provides async entry points for `XrdOssCsiFile` by allocating internal AIO wrappers and scheduling staged jobs. It keeps checksum processing off the caller path while preserving range-lock and completion semantics.

Important APIs/functions: `XrdOssCsiFileAioStore::~XrdOssCsiFileAioStore()` deletes cached AIO wrappers. `XrdOssCsiFile::Read(XrdSfsAio*)`, `Write(XrdSfsAio*)`, `pgRead(XrdSfsAio*, opts)`, and `pgWrite(XrdSfsAio*, opts)` allocate `XrdOssCsiFileAio`, initialize it with the parent AIO, operation kind, and checksum options, then schedule the first job. `pgWrite` performs `pgWritePrelockCheck()` before scheduling. `Fsync(XrdSfsAio*)` waits for all active AIOs, performs synchronous `Fsync()`, and completes the callback.

State/control: AIO count is incremented by wrapper initialization and decremented during `Recycle()` in the header-defined class. The store reuses wrappers on a simple freelist.

Dependencies/integration: depends on `XrdScheduler`, `XrdSfsAio`, pages, and the AIO job implementation in the header. Risks include asynchronous object lifetime, completion callback ordering, and prelock validation needing the caller buffer to remain valid. Tests should cover async read/write completion, pg checksum return/verify, close waiting for AIO drain, wrapper reuse, and immediate errors for unopened or readonly files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.hh

Purpose: defines the internal async state machine for checksum-aware AIO operations. It wraps the caller's `XrdSfsAio`, schedules pre/post jobs, and recycles wrapper objects.

Important APIs/types: `XrdOssCsiFileAioJob` has four job states: read step 1 locks range and submits successor AIO; read step 2 finishes short pg reads and verifies/fetches checksums; write step 1 locks range, updates/stores checksums, and submits successor AIO; write step 2 completes short writes and handles failures. `XrdOssCsiFileAio` overrides `doneRead/doneWrite` to schedule step 2, copies AIO fields in `Init()`, carries a range guard and pg options, and `Recycle()` releases locks, returns to store freelist or deletes itself, then decrements parent AIO count.

State/control: each operation uses one wrapper and embedded job object. Range locks span the successor async call and post-processing. The parent AIO receives final `Result` and callback only after checksum processing.

Risks/test signals: the header contains substantial implementation, so compile dependencies are broad. Callback buffers must remain valid across both steps; short writes are completed synchronously after async completion; failures must release locks and resync sizes. Tests should inject short read/write completions, checksum mismatch, successor AIO immediate failure, pgRead short completion, and close waiting on active jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.cc

Purpose: implements the page-level checksum manager for the CSI plugin. It opens tag storage, tracks data/tag lengths, verifies reads, stores checksums for writes, supports pgRead/pgWrite checksum vectors, truncates tag state, and performs loose-write consistency repair.

Important APIs/functions: `Open()` opens tagstore and optionally allows missing tags. `TrackedSizesGet()`, `LockSetTrackedSize()`, `LockResetSizes()`, and `TrackedSizeRelease()` serialize tag/data length updates. `UpdateRange()` and `StoreRange()` update tag checksums before data writes, dispatching aligned or unaligned helpers. `VerifyRange()` and `FetchRange()` validate or return checksums after data reads. `apply_sequential_aligned_modify()` batches tag writes. `LockTrackinglen()` coordinates range locks through `XrdOssCsiRanges`. `truncate()` adjusts tag state and verifies partial pages. `pgDoCalc()` and `pgWritePrelockCheck()` support page checksum protocol. `BasicConsistencyCheck()` repairs some tag/data length mismatches in loose-write mode.

State/persistence: persistent metadata is in `XrdOssCsiTagstore`; in-memory state tracks missing tags, readonly, loose-write mode, update locks, range locks, and last-page checks. Data and tag sizes may intentionally differ after crashes or failures until repaired.

Risks/test signals: correctness depends on aligned/unaligned dispatch, range lock release on every error path, checksum convention consistency, missing-tag policy, and update-before-data-write failure recovery. Tests should cover empty/missing tag files, reads past tracked length, partial final pages, extension holes, truncation both directions, pgWrite verify/doCalc modes, loose-write repairs, and concurrent overlapping ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.hh

Purpose: declares the core page checksum manager used by `XrdOssCsiFile`. It exposes high-level range update/verify/fetch/store methods while hiding tagstore access, range locking, and aligned/unaligned page math.

Important APIs/types: `Sizes_t` is `(tag_tracked_size, data_tracked_size)`. Public methods include `Open`, `Close`, `UpdateRange`, `VerifyRange`, `FetchRange`, `StoreRange`, `LockTrackinglen`, `truncate`, `TrackedSizesGet`, `LockResetSizes`, `VerificationStatus`, `pgDoCalc`, and `pgWritePrelockCheck`. Protected helpers cover aligned and unaligned read/write paths, hole extension, pre/post partial blocks, full/max reads, and formatted diagnostics for CRC mismatches and tag/page IO errors.

State/control: owns `std::unique_ptr<XrdOssCsiTagstore>`, `XrdOssCsiRanges`, mutex/condition variables for tracking-size updates, booleans for missing tags/read-only/loose writes/config flags, file identity strings, and last-page loose-write state. `LockTrackinglen()` sets range guards that later release tracked-size update locks.

Dependencies/integration: depends on tagstore abstraction, range guard implementation, XRootD page size, and `XrdOssDF` operations. Risks include complex lock ownership between `TrackedSizesGet()` and range guards, reliance on external unaligned implementation file, and static stack buffers sized by `stsize_`. Tests should validate public methods across aligned, unaligned, missing-tag, readonly, and concurrent access paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.hh -->
