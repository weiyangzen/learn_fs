# subset-b-007939 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcRequest.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcRequest.hh

## Purpose
`XrdFrcRequest.hh` defines the fixed-size request record used by FRM/FRC transfer queues. It is a data-only ABI structure: queue code stores logical file names, request IDs, notification targets, checksum metadata, timestamps, queue linkage offsets, operation options, URL offsets, original operation code, and priority in one contiguous object.

## Important APIs, Types, And Constants
The public `XrdFrcRequest` class exposes only fields and constants. `LFN`, `User`, `ID`, `Notify`, `iName`, and `csValue` are fixed arrays intended for direct queue serialization. `This` and `Next` are integer offsets into queue storage rather than pointers, which makes the queue persistent or mmap-friendly. `Options` is a bitset using `msgFail`, `msgSucc`, `makeRW`, `Migrate`, `Purge`, and `Register`. `csType` uses the `csNone`, SHA, Adler32, MD5, and CRC constants. `Item` enumerates printable queue fields consumed by queue listing code, especially `XrdFrcUtils::MapV2I()` and `XrdFrcProxy::List()`. Queue constants map operation classes to queue IDs: stage, migrate, get, put, nil, and `outQ` as a mask.

## Control Flow And State
There is no executable control flow. The important behavior is layout stability: other queue components can read and write records by offset and decode fields by agreed constants. `LFO` and `Opaque` preserve parsing offsets within `LFN` when the logical name is a URL or includes opaque query text. `addTOD` records enqueue time and `Prty` controls priority queue placement up to `maxPrty`.

## Dependencies And Integration Points
The header has no includes and intentionally avoids dependencies. It is integrated by `XrdFrcUtils` for operation-to-queue mapping and variable-name mapping, by `XrdFrcProxy` for queue operations, and by `frm_admin query xfrq` for field selection. Since all fields are public, producer and consumer code must agree on null termination and bounds.

## Risks And Test Signals
The fixed arrays protect against dynamic allocation but create truncation and overflow risks if callers use unchecked string copies. Persistent queue compatibility depends on field ordering and sizes; changes require migration tests over existing queue files. Tests should verify operation code mappings, field listing names, URL offset semantics, priority bounds, checksum type handling, and binary layout assumptions such as `sizeof(XrdFrcRequest)` and offsets if queue files are persisted across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.cc

## Purpose
`XrdFrcTrace.cc` provides the single definition of the FRC/FRM logging and tracing globals declared in `XrdFrcTrace.hh`. It gives all FRM/FRC code a shared `Say` error channel and a shared `Trace` controller.

## Important APIs And Objects
The file defines `XrdFrc::Say` as `XrdSysError(0, "frm_")`, establishing the default log prefix used before subsystem-specific configuration adjusts it. It defines `XrdFrc::Trace` as an `XrdOucTrace` bound to `Say`, so debug/trace macros write through the same logger as normal errors.

## Control Flow, State, And Persistence
There are no functions and no persistence. The only state is process-global logging state. Runtime code modifies `Trace.What` to enable trace masks; `XrdFrmConfig::Configure()` sets `TRACE_ALL` on `-d` and exports `XRDDEBUG=1`.

## Dependencies And Integration Points
This file includes only `XrdFrcTrace.hh`. It must be linked exactly once into binaries using `XrdFrc::Say` or `XrdFrc::Trace`; otherwise consumers either fail to link or accidentally get duplicate definitions if another translation unit defines them.

## Risks And Test Signals
The primary risk is link composition: every executable using FRC trace macros needs this object or an equivalent definition. Tests are mostly build/link tests plus runtime checks that `-d` enables debug output and logger binding in `XrdFrmConfig` redirects both `Say` and `XrdLog` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.hh

## Purpose
`XrdFrcTrace.hh` centralizes trace masks and logging macros for the File Residency Manager code. It abstracts debug emission behind `NODEBUG` and binds all diagnostics to the global `XrdFrc::Say` and `XrdFrc::Trace` objects.

## Important APIs, Macros, And Types
The header declares `TRACE_ALL` and `TRACE_Debug`; `QTRACE`, `DEBUG`, `DEBUGR`, `TRACE`, `TRACER`, `TRACEX`, and `EPNAME` are active when `NODEBUG` is not defined. `DEBUGR` and `TRACER` include `Req.User`, so they are meant for request-processing contexts where a `Req` object exists. `VMSG` and `VSAY` depend on a visible `Config` object with `Verbose`, which couples the macros to FRM modules using the global config.

## Control Flow And State
Trace macros gate output on `Trace.What` bitmasks. `TRACEX` writes to `std::cerr` between `Trace.Beg()` and `Trace.End()`. When compiled with `NODEBUG`, debug/trace macros reduce to no-ops, removing both output and expression evaluation for their arguments.

## Dependencies And Integration Points
The header includes `XrdSysError.hh`, `XrdOucTrace.hh`, and, in debug builds, `XrdSysHeaders.hh` for stream support. It is widely used by XrdFrc and XrdFrm code for common diagnostics. The external globals are defined in `XrdFrcTrace.cc`.

## Risks And Test Signals
Macro coupling is the main risk: `VMSG` and `VSAY` require `Config`, while request-aware macros require `Req` and `epname` in scope. Incorrect use can become a compile-time failure or produce misleading prefixes. Tests should include debug and `NODEBUG` builds, verify `-d` trace activation, and exercise verbose-only messages in FRM config/admin commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.cc

## Purpose
`XrdFrcUtils.cc` implements shared FRC/FRM utility functions for administrator prompts, URL parsing, admin and queue path construction, request option mapping, single-instance locking, copy-time xattr updates, and timestamp changes.

## Important Functions
`Ask()` prompts on stderr/stdin and accepts prefix matches for yes/no/abort. `chkURL()` validates `scheme://host//path`-style URLs and returns the offset of the logical file path after compressing leading slashes. `makePath()` builds an instance-specific admin path through `XrdOucUtils::genPath()` and optionally creates it. `makeQDir()` derives the queue directory, resolves a `Queues/` symlink if present, optionally creates the directory, and returns a duplicated path. `MapM2O()` translates notification and processing option strings into `XrdFrcRequest::Options`. `MapR2Q()` maps operation characters to stage/migrate/get/put/nil queues and sets purge flags for `^` and `=` operations. `MapV2I()` maps user-visible queue listing variable names to `XrdFrcRequest::Item`. `Unique()` creates and write-locks a lock file with `fcntl()`. `updtCpy()` stores copy time in the `XrdFrm.Cpy` xattr. `Utime()` wraps `utime()` with EINTR retry.

## Control Flow, State, And Persistence
Most helpers are stateless, but `Unique()` intentionally leaks the successful lock file descriptor so the process retains the advisory lock until exit. `makePath()` and `makeQDir()` persist directories. `updtCpy()` persists extended attributes based on file `st_mtime + Adj`; FRM uses negative adjustment for migratable marking and zero/positive behavior for purgeable or lock-file compatibility. `Ask()` can stop workflows by returning `a`.

## Dependencies And Integration Points
The implementation depends on `XrdFrcRequest`, `XrdFrcTrace`, `XrdFrcXAttr`, `XrdOucUtils`, `XrdOucSxeq`, `XrdOucXAttr`, and POSIX filesystem APIs. Admin commands use `Ask()`, `updtCpy()`, and `Utime()` heavily. Configuration uses `makePath()`, proxy setup uses `makeQDir()`, and queue query code uses `MapV2I()`.

## Risks And Test Signals
Path helpers use fixed local buffers and `strcpy()`, so long admin paths and symlink targets are important tests. `MapR2Q()` uses `*Flags = Purge` for `^` but `*Flags |= Purge` for `=`, so callers must initialize flags and know the replacement behavior. `Ask()` accepts ambiguous prefixes by `strncmp()` with input length, so one-letter answers work but accidental prefixes also match. Tests should cover URL offset parsing, symlinked queue paths, lock contention, xattr byte order through `updtCpy()`, and option mapping for every operation character.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.hh

## Purpose
`XrdFrcUtils.hh` declares the shared static utility surface implemented in `XrdFrcUtils.cc`. It is the small common API used by FRM admin, configuration, queue, and compatibility code.

## Important APIs
`Ask`, `chkURL`, `makePath`, `makeQDir`, `MapM2O`, `MapR2Q`, `MapV2I`, `Unique`, `updtCpy`, and `Utime` are all static. The header includes `XrdFrcRequest.hh` because mapping APIs expose `XrdFrcRequest::Item` and request option constants.

## Control Flow And State
The class is not meant to hold object state; the constructor and destructor are empty and all useful methods are static. State changes occur in the implementation through filesystem locks, directory creation, xattrs, and timestamps.

## Dependencies And Integration Points
The header depends only on standard time/cstdlib and `XrdFrcRequest`. It forward-declares `XrdFrcXAttrPin`, although this declaration is not used in this header. Consumers include `XrdFrmAdmin`, `XrdFrmConfig`, `XrdFrc` queue code, and compatibility code using lock/pin files.

## Risks And Test Signals
Because this header exposes low-level behavior globally, callers rely on exact return conventions: many functions return `1/0`, while path builders return allocated strings or null. Tests should assert ownership expectations for returned paths, failures from invalid URLs and too-long paths, and that static-only usage does not require object construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXAttr.hh

## Purpose
`XrdFrcXAttr.hh` defines the extended attribute payloads used by FRM to track file residency metadata: copy time, memory mapping behavior, pinning, and PFN back-references. The classes are designed for use with the templated `XrdOucXAttr<T>` wrapper.

## Important Types
`XrdFrcXAttrCpy` stores `cpyTime` under `XrdFrm.Cpy` and converts the 64-bit value between host and network byte order. `XrdFrcXAttrMem` stores `Flags` under `XrdFrm.Mem`; flags request mmap, keep mapping, or memory lock. `XrdFrcXAttrPin` stores `pinTime` plus flags under `XrdFrm.Pin`; flags represent permanent, idle-duration, or until-time pins. `XrdFrcXAttrPfn` stores a null-terminated PFN string under `XrdFrm.Pfn` for cross-reference repair in extended-attribute cache layouts.

## Control Flow, State, And Persistence
Each class supplies the `Name()`, `sizeGet()`, `sizeSet()`, `postGet()`, and `preSet()` protocol expected by `XrdOucXAttr`. The persistent state is stored in filesystem xattrs and is portable for 64-bit time fields by network byte order conversion. `XrdFrcXAttrPfn::sizeSet()` persists only the string length plus terminator, not the full fixed buffer.

## Dependencies And Integration Points
The header depends on network byte-order helpers from `XrdSysPlatform.hh`, POSIX path sizes, and `<cstring>`. `XrdFrmAdminFiles`, `XrdFrmAdminAudit`, `XrdFrmAdminFind`, and `XrdFrcUtils::updtCpy()` use these payloads to set, read, list, repair, and delete metadata.

## Risks And Test Signals
`XrdFrcXAttrPin::sizeGet()` and `sizeSet()` return `sizeof(XrdFrcXAttrCpy)` rather than `sizeof(XrdFrcXAttrPin)`. That is a high-risk ABI bug unless intentionally relying on older oversized storage; it can cause reads/writes larger than the pin structure. `XrdFrcXAttrMem::preSet()` ignores its temp object and returns `this`, which is fine only because no byte-order conversion is needed. Tests should verify exact xattr sizes, round-trip byte order across simulated endian boundaries, expired pin deletion, PFN string truncation behavior, and compatibility with existing on-disk xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXLock.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXLock.hh

## Purpose
`XrdFrcXLock.hh` defines a minimal RAII serialization helper around `XrdOucSxeq`. It gives FRM code a shared process/file lock for critical sections rooted at an admin path.

## Important APIs
`XrdFrcXLock::Init(aPath)` creates an `XrdOucSxeq` named `.frmxeq` under the supplied path and detaches its file descriptor into the static `lkFD`. Constructing `XrdFrcXLock` calls `XrdOucSxeq::Serialize(lkFD, 0)`, and destruction calls `XrdOucSxeq::Release(lkFD)`.

## Control Flow And State
The only state is the static `lkFD`, initialized to `-1` in this header unless `__FRCXLOCK_CC__` is already defined. The class assumes `Init()` is called before any RAII object is constructed. Locking and unlocking are scoped to C++ object lifetime.

## Dependencies And Integration Points
The helper depends solely on `XrdOucSxeq`. It integrates with FRM code that needs cross-process serialization around queue/admin metadata updates. The header-local static definition avoids a separate `.cc` file but requires careful include discipline.

## Risks And Test Signals
The header defines storage for `lkFD` in every translation unit unless include guards and `__FRCXLOCK_CC__` behavior prevent duplication in the actual build model; that pattern can be fragile with modern linkers and shared libraries. Constructing before successful `Init()` serializes on `-1`. Tests should cover initialization failure, nested lock scopes, multi-process contention, and link builds with multiple consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXLock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdFrm/CMakeLists.txt

## Purpose
`XrdFrm/CMakeLists.txt` defines the build targets for the File Residency Manager library and command-line daemons. It collects common FRM implementation into a static `XrdFrm` library and builds `frm_admin`, `frm_purged`, `frm_xfrd`, and `frm_xfragent`.

## Important Targets
`XrdFrm` includes configuration, file walking, monitoring, sorting, CNS notifications, migration, request boss, transfer, transfer daemon, job, and queue sources. `frm_admin` is built from admin audit, core, files, find, main, query, and unlink sources plus the static library. `frm_purged` builds purge sources. `frm_xfrd` and `frm_xfragent` both compile `XrdFrmXfrMain.cc` and link the common library.

## Dependencies And Integration Points
All executables link `XrdFrm`, `XrdServer`, `XrdUtils`, thread libraries, extra/socket libraries, and for `frm_admin`, readline/ncurses support. If readline is present, its include directory is added privately to `frm_admin`. Install rules place all executables under `${CMAKE_INSTALL_BINDIR}`.

## Control Flow And State
This is declarative build state. The static library concentrates shared FRM behavior, while command-specific translation units provide process entry points and admin command surfaces.

## Risks And Test Signals
The listed source set for `frm_admin` does not include `XrdFrmAdminReloc.cc`, even though that file is in this subset and defines the private `XrdFrmAdmin::Reloc(char*, char*)` relocation implementation. The public `Reloc()` in `XrdFrmAdmin.cc` currently calls `Config.ossFS->Reloc()` directly, so the missing source may be dead or stale, but this deserves build-symbol and behavior verification. Tests should include clean builds with and without readline, checking that every declared admin method has a linked definition and that install rules include all expected tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.cc

## Purpose
`XrdFrmAdmin.cc` implements the main `frm_admin` command dispatcher and shared command helpers. It handles top-level admin verbs, parses common options, manages final return status, initializes transfer queue proxy access, and delegates heavy filesystem operations to companion files.

## Important Functions
Top-level commands include `Audit`, `Chksum`, `Find`, `Help`, `MakeLF`, `Mark`, `Mmap`, `Mv`, `Pin`, `Query`, `Reloc`, and `Remove`. `xeqArgs()` maps abbreviated command names to methods. `Parse()` resets `Opt`, wires either argv-array or interactive-string arguments into `XrdOucArgs`, decodes common option letters, and collects required positional arguments. `ParseKeep()`, `ParseOwner()`, `ParseSpace()`, and `ParseType()` implement shared value parsing. `ConfigProxy()` discovers existing transfer queue files and initializes `XrdFrcProxy` for `query xfrq`. `VerifyAll()` recognizes `/*` directory-wide syntax, and `VerifyMP()` checks OSS export flags before migratable/purgeable operations.

## Control Flow, State, And Persistence
`frm_admin` state lives in the singleton `XrdFrm::Admin`. Each command mutates `Opt`, counters such as `numFiles`, and `finalRC`. Filesystem persistence happens indirectly through checksum manager calls, OSS rename/reloc/unlink, xattrs, lock files, queue proxy access, and audit repair helpers. `Quit()` exits with `finalRC`.

## Dependencies And Integration Points
This file depends on `XrdFrmConfig` for path mapping, OSS access, checksum manager, queue path, instance name, and export metadata. It integrates with `XrdFrcProxy`, `XrdFrcUtils`, `XrdOucArgs`, NSS user/group lookups, and the companion admin implementation files declared in `XrdFrmAdmin.hh`.

## Risks And Test Signals
`Mmap()` calls `Parse("pin ", ...)`, so mmap parse diagnostics can incorrectly name `pin`. `Parse()` supports only two `Opt.Args` slots; commands that need more must pull additional args manually. `ParseKeep()` uses `%D`, which is locale/century-sensitive, and does not null-check `strptime()` before dereferencing `eP`. `ConfigProxy()` uses fixed buffers and queue file existence as capability discovery. Tests should cover every command abbreviation, interactive and argv modes, invalid user/group/time/checksum input, forced and prompted migratable/purgeable decisions, and queue listings with missing and present queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.hh -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.hh

## Purpose
`XrdFrmAdmin.hh` declares the `XrdFrmAdmin` command processor used by `frm_admin`. It is the central interface joining command dispatch, audit/find/query/remove/reloc helpers, option state, counters, checksum state, and transfer queue proxy state.

## Important APIs And Types
Public methods are the command entry points and argument setters. Private methods are grouped by feature: audit name/space/usage helpers, checksum listing/printing, find variants, parsing helpers, mark/mmap/pin/lock helpers, query variants, relocation helpers, unlink helpers, and verification helpers. Static help strings provide per-command usage text. The nested `Opt` struct stores command-local flags, target arguments, UID/GID, and keep-time details.

## Control Flow And State
The object is long-lived across interactive commands. `Parse()` clears `Opt` for each command, but counters and `finalRC` are explicitly managed by command implementations. `ArgV/ArgC` and `ArgS` allow the same parser to support command-line and interactive modes. `frmProxy`/`frmProxz` cache queue proxy initialization.

## Dependencies And Integration Points
The header depends on checksum data and namespace walking. It forward-declares proxy, fileset, args, and list types. `XrdFrm::Admin` is declared as a namespace-global singleton and defined in `XrdFrmAdminMain.cc`.

## Risks And Test Signals
The class is broad and stateful, so command implementations can accidentally rely on stale counters or flags if parsing paths are bypassed. The `Opt.Args[2]` fixed capacity shapes parser usage and can be a source of mistakes. Tests should exercise multiple interactive commands in one process to catch stale state, verify global singleton initialization order, and build-check that all private methods declared here are defined in the linked admin target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminAudit.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminAudit.cc

## Purpose
`XrdFrmAdminAudit.cc` implements `frm_admin audit` subcommands for consistency checking and optional repair of namespace metadata, cache-space cross references, and space usage accounting.

## Important Functions
Name audits use `AuditNames()` with `XrdFrmFiles` to detect orphaned sidecar files (`AuditNameNB`), dangling base symlinks (`AuditNameNF`), missing copy-time metadata (`AuditNameNL`), and bad/missing PFN xattrs for extended-attribute layouts (`AuditNameXA`). Space audits use `AuditSpace()` and choose AX or XA logic based on configured space entries. AX checks validate generated PFN symlinks for raw data files. XA checks validate `XrdFrm.Pfn` xattrs and symlinks. Usage audits sum file sizes and compare them with `XrdOssSpace` usage records, optionally adjusting the Admin usage bucket.

## Control Flow, State, And Persistence
The audit flow parses target space/path, walks files, increments `numProb`, `numFix`, `numFiles`, `numBytes`, and `numBLost`, and may prompt before repair unless `-force` is set. Repair actions persist by unlinking orphaned files, creating/replacing symlinks, setting PFN xattrs, setting copy-time xattrs, removing data files, and adjusting usage accounting.

## Dependencies And Integration Points
This file integrates `XrdFrmFiles`, `XrdFrcUtils`, `XrdFrcXAttrPfn`, `XrdOssPath`, `XrdOssSpace`, `XrdOucNSWalk`, and configured space lists from `XrdFrmConfig`. It relies on the admin option state set by `XrdFrmAdmin::Audit()`.

## Risks And Test Signals
Audit repair is destructive and prompt-driven, so noninteractive `-force` behavior needs careful coverage. In `AuditUsage()`, the block that converts byte differences to KB is unconditionally executed because of missing `else` braces, so the display suffix logic is misleading. `AuditSpaceXA()` may count bytes as lost when repair is declined. Tests should create synthetic spaces with missing symlinks, wrong symlinks, missing xattrs, dangling links, stale copy time, absent usage files, and verify both dry-run and fix paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminAudit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFiles.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFiles.cc

## Purpose
`XrdFrmAdminFiles.cc` implements admin operations that mark files migratable/purgeable, set or clear mmap attributes, set or clear pin attributes, and retain obsolete lock/pin sidecar-file compatibility routines.

## Important Functions
`ckAttr()` maps an LFN to PFN, stats it, and decides whether a single file or whole directory should be processed, prompting for directory-wide operations when needed. `mkMark()` sets copy-time metadata with `XrdFrcUtils::updtCpy()`. `mkMmap()` writes or deletes `XrdFrm.Mem` xattrs using flags derived from `-keep`, `-lock`, and `-off` option state. `mkPin()` writes or deletes `XrdFrm.Pin` xattrs using permanent, idle, or until-time semantics. Obsolete `mkFile()`, `mkLock()`, and `mkStat()` create sidecar `.lock` or `.pin` files with ownership and timestamp semantics.

## Control Flow, State, And Persistence
Commands process either a single PFN or a directory tree through `XrdFrmFiles`, respecting `-recursive` and `/*`. Persistent state is xattrs for modern metadata and sidecar lock/pin files for backward compatibility. Counters update `numFiles`; failures set `finalRC`.

## Dependencies And Integration Points
The file uses `XrdFrmConfig::LocalPath`, `XrdFrmFiles`, `XrdFrcUtils`, and `XrdOucXAttr` over the xattr payload classes. It depends on option parsing performed in `XrdFrmAdmin.cc` and keep-time parsing for pin behavior.

## Risks And Test Signals
The option mapping in `Mmap()` from `XrdFrmAdmin.cc` uses `lock` as option code `f` and `off` as `l`, which then arrive in generic `Opt.Fix` and `Opt.Local`; this is hard to reason about and should be covered by CLI tests. Directory prompts are safety-critical. The obsolete `mkFile()` uses fixed buffers and temporary rename logic; if still reachable via `makelf`, it needs filesystem permission, ownership, timestamp, and cleanup tests. Xattr tests should validate mmap flag combinations, pin removal when no keep is supplied, recursive traversal, and error propagation from `XrdFrmFiles`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFiles.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFind.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFind.cc

## Purpose
`XrdFrmAdminFind.cc` implements `frm_admin find` queries over local cache state: failed transfers, mmapped files, missing or stale checksums, pinned files, and unmigrated files.

## Important Functions
`FindFail()` walks transfer fail-file directories and prints paths ending in `.fail`. `FindMmap()` lists files with `XrdFrm.Mem` xattrs and reconstructs `mmap` commands. `FindNocs()` checks a requested checksum type through `XrdCksManager` and reports missing or invalid checksums. `FindPins()` lists active pin xattrs, formats permanent, idle-duration, and until-date pins, and deletes expired until-time pins. `FindUnmi()` reports files without copy time or with mtime newer than copy time.

## Control Flow, State, And Persistence
Find commands are mostly read-only tree walks using `XrdFrmFiles` or `XrdOucNSWalk`, but `FindPins()` mutates state by deleting expired pin xattrs. Each command supports multiple directory arguments after the initial target and updates counts for summary output.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig` for path mapping and checksum manager, `XrdFrmFiles` for fileset traversal, `XrdFrcXAttrMem`/`Pin`, and `XrdOucNSWalk` for fail-file discovery. It is dispatched by `XrdFrmAdmin::Find()`.

## Risks And Test Signals
`FindFail()` assigns additional args to `dirFN` in the loop condition but never assigns `lDir = dirFN`, so multiple directory arguments appear not to be processed correctly. `FindPins()` has side effects during a find operation by deleting expired xattrs. Time formatting changes pins within one week into idle-style output. Tests should cover multiple directory arguments, relocated fail-file directories via `xfrFdir`, unsupported checksum types, expired and active pins, recursive vs non-recursive scans, and checksum manager return codes including `-ESTALE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFind.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminMain.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminMain.cc

## Purpose
`XrdFrmAdminMain.cc` is the entry point for `frm_admin`. It configures the process, selects command-line or interactive mode, manages readline history, and dispatches commands to the global admin object.

## Important Objects And Functions
The file defines global `XrdFrm::Config` for the admin subsystem, global `XrdFrm::Admin`, and compatibility globals `XrdLog` and `XrdTrace` needed by linked xrootd components. If GNU readline is unavailable, it provides fallback `readline`, `add_history`, and `stifle_history` stubs. `main()` handles signal masking, logger binding, configuration, argument mode selection, interactive tokenization, and final exit.

## Control Flow And State
`main()` ignores SIGPIPE and blocks SIGPIPE/SIGCHLD before configuration. It calls `Config.Configure()`, exits with code 4 on failure, then either dispatches a single command from argv or loops over interactive commands from `frm_admin> `. Interactive commands are tokenized with `XrdOucTokenizer`; repeated identical lines are not added to history. `Admin.Quit()` exits with `finalRC`.

## Dependencies And Integration Points
This file integrates `XrdFrmConfig`, `XrdFrmAdmin`, `XrdFrcTrace`, `XrdNet` socket options, `XrdSysLogger`, optional readline, and xrootd global trace/error symbols.

## Risks And Test Signals
Fallback `readline()` returns null on empty lines, causing an empty line to quit rather than just reprompt. Interactive tokenizer behavior should be tested for quoted arguments and command abbreviations. Signal masking and logger setup are process-level behaviors. Tests should run `frm_admin -h`, invalid config, one-shot commands, and an interactive session with help, invalid command, repeated command, empty input, and quit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminMain.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminQuery.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminQuery.cc

## Purpose
`XrdFrmAdminQuery.cc` implements `frm_admin query` subcommands for path translation, cache-space listing, usage accounting, and transfer queue inspection.

## Important Functions
`QueryPfn()` maps LFNs to local PFNs through `Config.LocalPath()`. `QueryRfn()` maps LFNs to remote names through `Config.RemotePath()`. `QuerySpace()` either lists configured spaces or reports each target file's cache space using `XrdOssPath::getCname()`, optionally recursively through `XrdFrmFiles`. `QueryUsage()` prints `XrdOssSpace` usage buckets and effective usage. `QueryXfrQ()` parses queue type names, optional priority, and optional field names, initializes `XrdFrcProxy` if needed, and lists transfer queue entries.

## Control Flow, State, And Persistence
The query operations are intended to be read-only. `QueryXfrQ()` lazily initializes the transfer queue proxy and may cache failure state in `frmProxz`. Directory expansion uses `VerifyAll()` and `XrdFrmFiles`. Usage queries initialize `XrdOssSpace` and read usage records.

## Dependencies And Integration Points
The file depends on `XrdFrcProxy`, `XrdFrcRequest`, `XrdFrcUtils::MapV2I`, `XrdFrmConfig`, `XrdFrmFiles`, `XrdOssPath`, `XrdOssSpace`, and `XrdOucArgs`. It ties admin-visible variable names to queue record fields.

## Risks And Test Signals
`QuerySpace()` uses prefix matching for `-recursive` with `strncmp(lfn, "-recursive", strlen(lfn))`, so very short prefixes such as `-r` are accepted intentionally or accidentally. Queue field parsing is limited by `XrdFrcRequest::getLast`. Tests should cover no-space configuration, path mapping failures, recursive directory queries, XA/non-XA space names, unknown xfrq queue names, invalid priority, too many variables, and queues absent from `QPath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminQuery.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminReloc.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminReloc.cc

## Purpose
`XrdFrmAdminReloc.cc` contains a private implementation for relocating a file between cache spaces by allocating a target placeholder, copying data, preserving metadata, renaming into place, adjusting space accounting, and cleaning up source remnants.

## Important Functions
`Reloc(char *srcLfn, char *Space)` parses the target space, maps source and temporary target LFNs/PFNs, validates that source and target spaces differ, creates a target file via `ossFS->Create()`, copies bytes with `RelocCP()`, applies timestamps, renames target to source LFN, updates `XrdOssSpace`, and handles symlinked source remnants. `RelocCP()` first tries mmap plus segment writes, then falls back to traditional `pread()`/`pwrite()` copying. `RelocWR()` performs EINTR-safe positional writes.

## Control Flow, State, And Persistence
The operation is heavily persistent: it creates a `.anew` placeholder, copies file contents, updates mtime, renames through OSS, adjusts usage buckets, and may create or remove symlinks. A local RAII `relocRecover` object tries to unlink the target on early return. Copying proceeds in 1 MiB segments.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig`, OSS create/rename/unlink, `XrdOssSpace`, `XrdOssPath`, `XrdOucEnv`, POSIX mmap/pread/pwrite/utime, and admin parsing helpers. Notably, current `CMakeLists.txt` does not list this file in the `frm_admin` executable, and public `XrdFrmAdmin::Reloc()` in `XrdFrmAdmin.cc` delegates directly to `Config.ossFS->Reloc()`, so this implementation may be stale or unlinked.

## Risks And Test Signals
There is a likely precedence bug: `srcLsz = readlink(...) < 0` assigns a boolean rather than the link length. The lock-file timestamp branch sets a new lock path and returns `0`, apparently aborting before rename whenever a lock file exists. `relocRecover` stores `trgPfn` in a field named `Lfn` and calls `ossFS->Unlink()` without explicit PFN flags. Tests should first confirm whether this file is linked; if revived, cover symlink sources, existing lock files, copy fallback after mmap failure, partial write/read failures, usage adjustment rollback, and cleanup of `.anew` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminReloc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminUnlink.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminUnlink.cc

## Purpose
`XrdFrmAdminUnlink.cc` implements recursive and non-recursive removal for `frm_admin rm`, including OSS-backed deletion, namespace walking, cache manager notifications, and CNS notification events.

## Important Functions
`Unlink()` maps an LFN to PFN, stats it, dispatches files to `UnlinkFile()`, directories to `UnlinkDir()`, and recursive directories through `XrdOucNSWalk`. `UnlinkDir(const char*, const char*)` handles single-directory deletion or all-files deletion with confirmation. `UnlinkDir(NSEnt*&, NSEnt*&)` removes files immediately and defers directories for later removal. `UnlinkFile()` chooses raw `unlink()` for special path types and `Config.ossFS->Unlink()` for normal files, then notifies CMS and CNS.

## Control Flow, State, And Persistence
Deletion is persistent and safety-gated by `Opt.All`, `Opt.Recurse`, and `Opt.Force`. Recursive removal walks children first, remembers directories, then removes them after file deletion succeeds. Counters `numFiles`, `numDirs`, and `numProb` track results. CNS notifications are sent through `XrdFrmCns::Rm()` and `Rmd()`.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig`, `XrdFrmCns`, `XrdNetCmsNotify`, `XrdOss`, `XrdOssPath`, `XrdOucNSWalk`, and POSIX stat/unlink. It is called by `XrdFrmAdmin::Remove()`.

## Risks And Test Signals
This is destructive code, so tests should use isolated namespaces. Non-recursive directory removal special-cases a lone `DIR_LOCK`; the comparison uses `Config.lockFN` against `NSE.nP->Path`, which may be a full path rather than a basename depending on `NSWalk` behavior. CNS `Rmd()` is sometimes passed PFN and sometimes LFN with `islfn=1`; translation should be verified. Tests should cover file deletion, empty directory deletion, directory with lock file, directory with subdirectories without `-recursive`, recursive confirmation abort, echo output, CMS notification, CNS notification, and OSS failure returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminUnlink.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.cc

## Purpose
`XrdFrmCns.cc` implements optional notifications to the CNS daemon by writing event records to an `XrdCnsd.events` FIFO/file under the configured admin path.

## Important Functions
`Add()` emits create and closew events for a path, size, and mode. `Rm()`/`Rmd()` in the header call private `Del()` with file or directory delete headers. `Init(const char*, int)` presets path/mode, while `Init(myID, aPath, iName)` constructs headers and default path. Private `Init()` lazily opens the event path. `Retry()` controls auto/require/ignore behavior on FIFO errors. `Send2Cnsd()` serializes writes with `XrdOucSxeq` and writes an iovec. `setPath()` builds and validates the event path.

## Control Flow, State, And Persistence
All state is static: `cnsPath`, delete headers, fd, mode, and initialization flag. In auto/require modes, the first send lazily opens the event path. Require mode sleeps and retries on missing/not-ready daemon; auto mode logs then disables action for that send. Event records are persistent only insofar as they are written to the CNS daemon endpoint.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig` for PFN-to-LFN conversion during delete events, `XrdOucUtils::genPath()`, `XrdOucSxeq`, `XrdSysMutex`, `XrdSysTimer`, POSIX open/writev/stat, and global `Say`. Config initializes it via `frm.all.cnsd` and `ConfigPaths()`, while admin unlink and other FRM operations call `Add`, `Rm`, or `Rmd`.

## Risks And Test Signals
`Send2Cnsd()` serializes on `cnsFD`; if opening failed or fd is stale, behavior depends on retry paths. `Add()` has a fast `if (!cnsMode) return`, while `Del()` relies on callers checking mode. Require mode can block indefinitely in 10-second sleeps until CNS appears. Tests should cover ignore/auto/require modes, absent FIFO, broken pipe, PFN-to-LFN conversion failure, concurrent notifications, and event record formatting within pipe atomicity limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.hh -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.hh

## Purpose
`XrdFrmCns.hh` declares the static CNS notification facade used by FRM code. It exposes create, remove-file, remove-directory, and initialization APIs while hiding FIFO path management and write retry logic in `XrdFrmCns.cc`.

## Important APIs
`Add(tID, Path, Size, Mode)` sends create/close-write events. `Rm(Path, islfn)` and `Rmd(Path, islfn)` send file and directory removal events only when CNS mode is enabled. `cnsAuto`, `cnsIgnore`, and `cnsRequire` describe runtime mode. Two `Init()` overloads either preset path/mode from config or complete process-specific initialization with headers.

## Control Flow And State
All members and helper methods are static. Private state includes event path, delete headers, header length, initialization state, file descriptor, and mode. Header constants distinguish directory and file removal records.

## Dependencies And Integration Points
The header depends on POSIX `uio` types for vector writes. It is included by configuration and unlink/admin code. Public methods are intentionally process-global, matching a single CNS endpoint per FRM process.

## Risks And Test Signals
Because API state is static, reconfiguration and repeated `Init()` calls must be tested to ensure paths and headers are refreshed correctly. `Rm` and `Rmd` silently do nothing in ignore mode, which is expected but needs integration coverage. Tests should validate mode constants, `islfn` behavior, and that remove calls before complete initialization either initialize lazily or log a controlled failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.cc

## Purpose
`XrdFrmConfig.cc` implements configuration for FRM admin, purge, and transfer subsystems. It parses command-line options and config-file directives, sets environment/logging, loads OSS/xattr/checksum/name mapping plugins, builds admin/queue paths, configures spaces and policies, and initializes subsystem-specific runtime support.

## Important Functions
`Configure()` is the main orchestration entry. It parses options, sets `XRDINSTANCE`, `XRDHOST`, `XRDPROG`, and `XRDNAME`, configures logging/background mode, reads the config file through `ConfigProc()`, creates admin paths with `ConfigPaths()`, loads plugins through `XrdOfsConfigPI`, and dispatches to admin/purge/xfr setup. Public path helpers `LocalPath`, `LogicalPath`, and `RemotePath` wrap name2name plugins or identity mapping. `Space()` looks up configured space directories. `Stat()` chooses `StatPF` when supported. Directive handlers include `xapath`, `xcks`, `xcnsd`, `xcopy`, `xcmax`, `xdpol`, `xmon`, `xnml`, `xpol`, `xpolprog`, `xqchk`, `xsit`, `xspace`, and `xxfr`.

## Control Flow, State, And Persistence
The constructor establishes defaults for timing, queue limits, admin mode, lock names, policy, transfer commands, and subsystem identity. Config parsing mutates many persistent process fields: paths, plugin pointers, space lists, policies, transfer command templates, monitoring destinations, CNS mode, fail-file directory, and usage behavior. `ConfigPF()` writes pid files; `ConfigPaths()` creates admin directories and STOPPURGE path; `ConfigMum()` temporarily captures stderr during admin/no-log initialization.

## Dependencies And Integration Points
The implementation is deeply integrated with XRootD: `XrdOfsConfigPI`, `XrdOss`, `XrdOssSpace`, `XrdOucN2NLoader`, `XrdOucStream`, `XrdOucMsubs`, `XrdFrmCns`, `XrdFrmMonitor`, `XrdNetCmsNotify`, and global OSS export path lists. Admin commands rely on `Config` for all path, space, checksum, OSS, CMS, and queue decisions; transfer and purge daemons use the same object with different `SubSys` mode.

## Risks And Test Signals
This file is configuration-critical and uses many fixed buffers plus string mutation. `Grab()` contains `if (*Dest) {free(*Dest); Dest = 0;}` which nulls the local pointer variable rather than `*Dest`, though it later assigns `*Dest`; this is harmless for assignment but leaves a confusing pattern. `xspace()` no longer supports old non-XA spaces and returns an error for `oss.cache` without `xa`. `ConfigXeq()` ignores unknown prefixed directives with warnings but suppresses unprefixed unknowns. Tests should cover each subsystem mode, missing config, every directive parser, invalid values, plugin-load failures, background logging handoff, admin path creation, CNS modes, space wildcard expansion, policy defaults/overrides, name2name mapping, and transfer command option combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.hh

## Purpose
`XrdFrmConfig.hh` declares the configuration object shared by FRM admin, purge, migration, prestage, and transfer subsystems. It is the main runtime state container for paths, plugins, policies, transfer commands, spaces, timing knobs, and subsystem identity.

## Important APIs And Types
Public fields expose program identity, admin paths, queue paths, PID paths, MSS and transfer command state, plugin pointers, UID/GID, timing values, feature flags, path/space lists, and purge policy state. `Cmd` describes configured copy commands and option flags such as allocation, `$MDP`, stats, monitoring data, and remove-on-error. `VPInfo` stores named virtual spaces and directories. `Policy` stores free-space thresholds, hold time, external-policy flag, and space name. Public methods include `Configure`, path mapping, CTA/export checks, space lookup, and stat abstraction. `SubSys` selects admin, migrate, prestage, purge, or transfer behavior.

## Control Flow And State
`XrdFrmConfig` is stateful and generally used as the global `XrdFrm::Config`. Constructor defaults are completed by `Configure()`. Many fields are read directly by admin and daemon code rather than through accessors, so invariants are enforced mostly by configuration sequencing.

## Dependencies And Integration Points
The header depends on `XrdOssSpace.hh` and forward-declares XRootD plugin, logging, stream, name mapping, checksum, and list types. It declares private directive parsers implemented in `XrdFrmConfig.cc`. Every file in this subset that needs path mapping, OSS access, checksum support, queue paths, or space lists depends on this object.

## Risks And Test Signals
The broad public field surface makes it easy for later code to observe partially initialized state or mutate fields inconsistently. Ownership is mixed: many `char*` fields are allocated with `strdup()` and freed/replaced in parsers, while destructors intentionally do little. Tests should validate default constructor state, full `Configure()` transitions for each subsystem, null-pointer behavior when optional plugins are absent, and that direct consumers behave correctly after failed configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.hh -->
