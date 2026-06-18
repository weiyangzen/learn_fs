<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLock.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLock.hh

Purpose: Provides a tiny RAII lock guard for `XrdSysMutex`.

APIs and control flow: `XrdOucLock(XrdSysMutex*)` stores the mutex pointer, locks it immediately, and records `isLocked`. The destructor unlocks if still marked locked. There is no public unlock/relock API, so instances are intended for stack-scoped critical sections.

State and persistence: Holds only a borrowed mutex pointer and a local locked flag. No persistent state or ownership transfer exists.

Dependencies and integration: Depends on `XrdSys/XrdSysPthread.hh`. It integrates with older XRootD code that predates or avoids standard C++ lock guards.

Risks and test signals: The class assumes a non-null mutex and is copyable by default, which could double-unlock if copied. Tests should exercise scope-exit unlock behavior, exception/early-return paths, and avoid copying in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.cc

Purpose: Implements common log configuration, including logfile selection, logging plugin loading, plugin argv construction, and optional stderr forwarding into the logging subsystem.

APIs and control flow: `XrdOucLogging::configLog()` parses `configLogInfo::logArg`. `-` leaves stderr alone, plain paths configure a logfile, and `@library[,key=value...]` loads a `XrdSysLogPInit` plugin through `XrdOucPinLoader`. It parses plugin options such as `bsz`, `cse`, and `logfn`, calls `XrdSysLogging::Configure()`, exports `XRDLOGDIR`, and, when needed, redirects `STDERR_FILENO` through a pipe serviced by `LoggingStdErr()`. `configLPIArgs()` supplies plugin argv from `XrdOucEnv`, and `varVal()` extracts delimited key values.

State and persistence: Uses namespace statics `cseLvl` and `stdErr`; the stderr router thread is persistent once started. The configured logger and plugin are external subsystem state. `XRDLOGDIR` is exported process-wide.

Dependencies and integration: Integrates with `XrdSysLogging`, `XrdSysLogPI`, `XrdOucPinLoader`, `XrdOucEnv`, `XrdOucStream`, and `XrdOucUtils::subLogfn`.

Risks and test signals: Stderr redirection changes a process-global descriptor and must be tested with plugin/no-plugin combinations. `BadHdr()` filters captured lines for CSE modes, so tests should cover malformed headers, hi-res/keepV parameters, logfile substitution, plugin failures, and buffer size bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.hh

Purpose: Declares the logging configuration facade used by servers and clients to centralize XRootD log setup.

APIs and control flow: `configLogInfo` carries the raw log argument, environment, instance name, config filename, version retention count, and high-resolution timestamp flag. `configLog()` is the public static entry point. Private helpers parse logging plugin argv and comma-delimited option values.

State and persistence: The header itself holds no instance state. Configuration effects are process-level: logger setup, plugin image lifetime, exported environment variables, and possible stderr forwarding created by the implementation.

Dependencies and integration: Forward-declares `XrdSysError` and `XrdOucEnv` so call sites can pass the active error router and environment without pulling in implementation headers.

Risks and test signals: The contract relies on `logArg` being non-null and stable during the call. Tests should validate `configLogInfo` defaults, public API compatibility for plugin users, and behavior when optional fields such as `xrdEnv`, `iName`, or `cfgFn` are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMapP2X.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMapP2X.hh

Purpose: Implements a simple path-to-value map optimized for longest-prefix matching.

APIs and control flow: The anchor/default constructor creates a head node. `Insert()` places nodes in decreasing path-length order. `Find()` looks for an exact path and can stop early because of that ordering. `Match()` returns the first stored path that prefixes a supplied pathname. Accessors expose name, path, next node, and value, while `RepName()` and `RepValu()` mutate stored metadata.

State and persistence: Each node owns duplicated `Path` and `Name` strings and stores a template value `T`. The list has no locking, persistence, or copy-control.

Dependencies and integration: Uses C string allocation and comparison from libc. It is suitable for configuration maps where longer mount or namespace prefixes must win.

Risks and test signals: Prefix matching does not enforce path-component boundaries, so `/foo` matches `/foobar`. `RepName()` checks `Path` before freeing `Name`, which is unusual but harmless for normal nodes. Tests should cover exact lookup, ordering, empty anchors, overlapping prefixes, and destruction ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMapP2X.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.cc

Purpose: Implements message-template parsing and runtime variable substitution for notification, external program, and storage-operation messages.

APIs and control flow: The constructor initializes static variable names such as `$LFN`, `$PFN`, `$USER`, `$HOST`, `$RID`, and `$CGI`. `Parse()` duplicates the message, splits it into literal and variable elements, honors escaped dollars, maps known uppercase variables to enum ids, and rejects templates with more than `maxElem` elements. `Subs()` walks the parsed elements and fills caller-provided data/length arrays. `getVal()` supplies values from `XrdOucMsubsInfo`, converting logical names through `XrdOucName2Name` when PFN/RFN values are needed and caching converted strings in the info object.

State and persistence: Parsed template text is stored in `mText`, with `mData` and `mDlen` recording fragments. Converted PFN/RFN values live in `XrdOucMsubsInfo` buffers until that info object is destroyed.

Dependencies and integration: Depends on `XrdOucEnv`, `XrdOucName2Name`, security/CMS environment keys, and POSIX open flags.

Risks and test signals: Missing values fall back to the literal variable token, which may be intentional but can hide configuration mistakes. Tests should cover escaping, custom env variables, PFN/RFN conversion failures, `$OFLAG` formatting, and the element limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.hh

Purpose: Declares the substitution engine and the per-operation data carrier used to expand `$` variables in command/message templates.

APIs and control flow: `XrdOucMsubsInfo` gathers transaction ids, environment, optional name mapper, logical and physical names, mode, flags, misc options, and buffers for lazily generated names. `XrdOucMsubs::Parse()` compiles a template and `Subs()` materializes it as arrays of data pointers and lengths.

State and persistence: `XrdOucMsubsInfo` owns only the generated `pfnbuff`, `rfnbuff`, `pfn2buff`, and `rfn2buff` allocations. `XrdOucMsubs` owns the parsed template and any duplicated unknown variable names.

Dependencies and integration: Exposes predefined environment key constants for CMS, security identity, and instance variables. Integrates with `XrdSysError`, `XrdOucEnv`, and `XrdOucName2Name`.

Risks and test signals: `maxElem` bounds template complexity and callers must size output arrays accordingly. Tests should validate destructor cleanup, mapping of each predefined variable, and behavior when `Env` or `N2N` lacks requested data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.cc

Purpose: Loads the configured logical-name to physical-name translator, either the built-in default mapper or a shared-library plugin.

APIs and control flow: `Load()` first handles the default path when `libName` is null: it compares version metadata, validates `lclRoot` as a directory, exports `XRDLCLROOT`/`XRDRMTROOT`, calls built-in `XrdOucgetName2Name()`, and stores the optional vector mapper in the environment. For plugin mode it exports `XRDN2NLIB` and `XRDN2NPARMS`, uses `XrdOucPinLoader` to resolve `XrdOucgetName2Name`, constructs the mapper, and optionally resolves `?Name2NameVec`.

State and persistence: Loader instances borrow constructor arguments. Loaded plugin images are managed by `XrdOucPinLoader`; returned mapper objects are owned by the caller. Environment exports are process-wide.

Dependencies and integration: Bridges `XrdOucName2Name`, `XrdOucPinLoader`, `XrdSysPlugin`, version metadata, and configuration environments.

Risks and test signals: Root validation and version compatibility are startup-critical. Tests should cover null library default mapping, invalid local root, plugin symbol absence, optional vector symbol, and exported environment values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.hh

Purpose: Declares the helper that instantiates name translation plugins from `oss.namelib`/proxy configuration state.

APIs and control flow: The constructor uses `XrdOucgetName2NameArgs` to capture the error route, config filename, plugin parameters, local root, and remote root. `Load()` accepts a library name, caller version, and optional environment to receive the vector translator pointer.

State and persistence: Stores borrowed pointers only; it does not own or copy configuration strings. Plugin and mapper lifetime are established by `Load()` and its dependencies.

Dependencies and integration: Includes `XrdOucName2Name.hh` for the plugin factory signature and mapper type, and forward-declares `XrdOucEnv` and `XrdVersionInfo`.

Risks and test signals: Because constructor arguments are borrowed, callers must keep them alive through `Load()`. Tests should compile third-party plugin users against this header and validate both built-in and plugin loader call signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2No2p.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2No2p.cc

Purpose: Implements a name2name plugin that maps object IDs into filesystem-safe paths, distributing short IDs across hash-derived subdirectories and segmenting long IDs.

APIs and control flow: `XrdOucN2No2p` implements `lfn2pfn()`, `lfn2rfn()`, and `pfn2lfn()`. `lfn2pfn()` optionally prefixes a local root, then delegates to `pfn2lfn()` for object-path transformation. `pfn2lfn()` leaves absolute paths untouched, replaces embedded slashes with a configurable character, creates hash fanout for IDs within the max filename length, or splits longer IDs into `oidMax`-sized path components. The exported `XrdOucgetName2Name()` parses `-slash`, `-maxfnlen`, and an object-id prefix.

State and persistence: The mapper owns `lRoot` and `oidPfx`; no on-disk state is created. Mappings are deterministic and depend on `_PC_NAME_MAX`, prefix, and replacement character.

Dependencies and integration: Uses `XrdOucTokenizer`, `XrdOucHashVal2`, `XrdSysError`, and XRootD plugin version metadata.

Risks and test signals: Option parsing uses `strtol(..., 16)` for numeric fields, so decimal-looking inputs are interpreted as hex. Tests should cover absolute paths, slash replacement, short and long IDs, buffer limits, prefix normalization, and invalid options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2No2p.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.cc

Purpose: Implements wildcard-capable name list entries and thread-safe anchor replacement logic.

APIs and control flow: The entry constructor duplicates the configured name and splits the first `*` into left and right fragments. `NameKO()` performs case-insensitive matching, while `NameOK()` performs case-sensitive matching. Both support exact, prefix-only, suffix-only, and prefix/suffix wildcard forms. `XrdOucNList_Anchor::Replace()` updates an existing equivalent wildcard entry or inserts a new one ordered by decreasing left-fragment length.

State and persistence: Each entry owns its duplicated name buffer; wildcard right fragments point into that same allocation. The anchor owns a mutex and list head but does not persist state outside memory.

Dependencies and integration: Depends on `XrdSysMutex` for anchor operations. Used by components that need dynamic allow/deny or pattern-to-flag lists.

Risks and test signals: Only the first `*` is special. Case-sensitive and case-insensitive APIs have different semantics. Tests should cover replacement ordering, wildcard edges, duplicate replacement, concurrent anchor methods, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.hh

Purpose: Declares linked-list utilities for matching names or wildcard patterns to integer flags.

APIs and control flow: `XrdOucNList` exposes flag access, next traversal, `NameOK()`, `NameKO()`, and `Set()`. `XrdOucNList_Anchor` adds mutex-protected `Insert()`, `Replace()`, `Find()`, `Pop()`, `Empty()`, and list swapping helpers.

State and persistence: Entries store a duplicated pattern split into left/right pieces plus an integer flag. The anchor owns list topology and a mutex; no serialization is provided.

Dependencies and integration: Includes pthread wrappers and platform string compatibility. It is a small infrastructure type for configuration-derived pattern lists.

Risks and test signals: `First()` returns the raw list without locking, and `Swap()` requires manual external locking. Tests should focus on caller locking discipline, pop/empty ownership, wildcard matching, and platform case-comparison behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.cc

Purpose: Implements directory indexing and optional recursive namespace traversal with stat/link collection, exclude lists, lock-file coordination, and empty-directory callbacks.

APIs and control flow: `Index()` processes queued directories one at a time, optionally locks a named file, calls `Build()`, and returns a linked list of `NSEnt` entries. `Build()` opens the directory, reads entries, skips `.`/`..`, gets stat data using `fstatat()` when available, queues child directories when recursive traversal is enabled, reads symlink targets when requested, applies return-type filters, and orders entries by option. `LockFile()` opens and write-locks the configured lock file. `setPath()` maintains a mutable path buffer with `File` pointing at the filename suffix.

State and persistence: Traversal state lives in `DList`, `DEnts`, `DPath`, lock descriptors, and copied exclude lists. No persistent state is written, but filesystem locks may block other processes.

Dependencies and integration: Uses POSIX `opendir`, `readdir`, `stat`, `lstat`, `readlink`, `fcntl` locks, `XrdOucTList`, and `XrdSysError`.

Risks and test signals: `DPath` is fixed at 1032 bytes and path construction uses `strcpy`, so long paths are risky. Tests should cover recursion, symlink handling, skipped errors, lock files, empty callbacks, excludes, entry ordering, and path length boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.hh

Purpose: Declares the namespace walker API used to enumerate filesystem directories with XRootD-specific filtering and locking options.

APIs and control flow: `NSEnt` describes returned entries with path, file component, stat data, symlink payload, length, and type. `Index()` is the iterator-like API. `CallBack::isEmpty()` can observe empty directories. Options select returned entry types, stat/link collection, sorted order, recursion, path style, and error skipping.

State and persistence: The walker owns pending directory lists, copied excludes, current directory path storage, and optional lock filename. Returned `NSEnt` lists are owned by the caller.

Dependencies and integration: Forward-declares `XrdOucTList` and `XrdSysError`; includes POSIX stat and fcntl definitions.

Risks and test signals: The API returns raw linked lists and raw pointers into owned path strings, so callers must respect object and entry lifetimes. Tests should validate option combinations, callback behavior, caller deletion of entries, and recursive `Index()` loops until end-of-traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.cc

Purpose: Provides the built-in default implementation of the name translation plugin interface.

APIs and control flow: `XrdOucN2N` implements `lfn2pfn()`, `lfn2rfn()`, `pfn2lfn()`, and `n2nVec()`. The constructor normalizes local and remote roots. `concat_fn()` prefixes a root and inserts a slash when needed. `pfn2lfn()` strips the local root when present. The exported `XrdOucgetName2Name()` creates the mapper and stores it in global `XrdOucN2NVec_P` for optional vector translation.

State and persistence: The object owns duplicated local/remote root strings and returns heap-allocated vectors from `n2nVec()` that must be recycled by the interface contract. No filesystem state is persisted.

Dependencies and integration: Used by `XrdOucN2NLoader` when no external namelib is configured. Integrates with `XrdSysError` for path-length diagnostics.

Risks and test signals: Root stripping requires `pfn[LocalRootLen] == '/'`, so exact-root PFNs are not stripped. Tests should cover null roots, trailing slash normalization, relative LFNs, buffer exhaustion, RFN prefixing, and vector recycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.hh

Purpose: Defines the public plugin contract for translating logical, physical, and remote file names in XRootD storage paths.

APIs and control flow: `XrdOucName2Name` declares pure virtual `lfn2pfn()`, `lfn2rfn()`, and `pfn2lfn()`. `XrdOucName2NameVec` declares `n2nVec()` and provides `Recycle()` for vectors of heap strings. `XrdOucgetName2NameArgs` standardizes plugin factory arguments, and the extern "C" `XrdOucgetName2Name()` entry point is the loader ABI.

State and persistence: The header defines interfaces only. Implementations decide mapping state; returned vector contents are heap-owned until `Recycle()`.

Dependencies and integration: Used by default OSS, statlib users, `XrdOucN2NLoader`, external namelib plugins, and substitution helpers.

Risks and test signals: The comments emphasize efficiency because translation is on hot metadata paths. ABI tests should compile external plugins, verify extern "C" symbol visibility, version metadata guidance, vector recycling, and errno-style return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPList.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPList.hh

Purpose: Provides a prefix path list that maps paths to flags or stores paired path/name metadata.

APIs and control flow: `XrdOucPList` stores a path, path length, attrs, and either flags or a name pointer via a union. `PathOK()` tests whether a candidate starts with the stored prefix. `Set(pd,pn)` stores path and name in one allocation. `XrdOucPListAnchor` offers longest-prefix `Find()`/`About()`, exact `Match()`, ordered `Insert()`, defaults for absolute and non-absolute paths, and list cleanup.

State and persistence: Entries own their `path` allocation; name mode stores `name` inside that allocation. The anchor holds defaults and an in-memory list only.

Dependencies and integration: Uses libc allocation and formatting. It is a configuration utility for path-prefix policies.

Risks and test signals: Prefix checks do not enforce component boundaries. The flags/name union means callers must know which constructor or setter was used. Tests should cover longest-prefix ordering, default selection, name storage, exact matching, and ownership cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.cc

Purpose: Implements checksum and iovec layout helpers for XRootD page read/write protocol messages.

APIs and control flow: `csCalc()` computes CRC32C checksums over page-sized segments, handling unaligned leading fragments. The vector overload sizes and fills a checksum vector. `csNum()` computes checksum count and optionally first/last segment lengths. `csVer()` verifies data against checksums, updates `dataInfo` past verified or failed ranges, and reports bad offset/count. `recvLayout()` validates socket bytes containing interleaved checksums and computes data/socket lengths and first/last data fragment lengths. `sendLayout()` computes the corresponding layout for outbound data.

State and persistence: All functions are stateless except for mutating caller-provided `dataInfo` and `Layout`. No persistence occurs.

Dependencies and integration: Uses `XProtocol` page size constants and `XrdOucCRC` CRC32C helpers. It sits directly in pgRead/pgWrite network and filesystem I/O paths.

Risks and test signals: Off-by-one and alignment errors can corrupt data. Tests should cover aligned and unaligned offsets, short final pages, invalid buffer sizes, zero lengths, checksum mismatch resume behavior, and maximum integer-sized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.hh

Purpose: Declares the page read/write checksum and layout utility API.

APIs and control flow: Public static methods compute checksums, count checksum slots, verify data with resumable `dataInfo`, and calculate receive/send `Layout` values. `Layout` records buffer offset, data length, socket length, first/last segment lengths, and failure reason.

State and persistence: The class has no instance state. Callers provide buffers, checksum arrays, `dataInfo`, and `Layout` structs.

Dependencies and integration: Includes `<cstdint>`, `<vector>`, and POSIX `off_t`. The implementation binds it to protocol page-size and CRC semantics.

Risks and test signals: Callers must size checksum buffers according to `csNum()` and honor `eWhy` when layout functions return zero. Tests should validate header/API assumptions for pgRead/pgWrite clients and servers, especially iovec construction from `fLen` and `lLen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinKing.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinKing.hh

Purpose: Provides a template orchestrator for post-R5 object-oriented plugin loading, including stacked plugin chains.

APIs and control flow: `Add()` records a base plugin or pushes an additional stacked plugin. `Load(Symbol)` iterates configured pins, creates an `XrdOucPinLoader` for each path, resolves an `XrdOucPinObject<T>` symbol, and calls `getInstance(parms, env, logger, previous)` so each plugin can wrap or extend the previous instance.

State and persistence: `pinVec` stores path, parameters, and loader pointers. `pinInfo` deletes its loader, whose destructor persists successfully loaded plugin images. The returned plugin instance is owned by the caller or plugin contract.

Dependencies and integration: Integrates `XrdOucPinLoader`, `XrdOucPinObject`, `XrdOucEnv`, `XrdSysError`, and caller version metadata.

Risks and test signals: `Add(push=false)` assumes the constructor-created base slot exists. Partial chain failures return null and leave prior instances to plugin-specific ownership rules. Tests should cover base replacement, stacked loading order, missing symbols, bad parameters, and loader persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinKing.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.cc

Purpose: Implements version-aware shared-library plugin loading and symbol resolution.

APIs and control flow: Constructors initialize error routing via `XrdSysError`, caller-provided buffer, or allocated buffer. `Init()` warns about version syntax in paths, computes a primary versioned library path through `XrdOucVerName::Version()`, and records an unversioned fallback when allowed. `Resolve()` validates load state, lazy-loads via `LoadLib()`, handles optional `?`/`!` symbol prefixes, and calls `XrdSysPlugin::getPlugin()`. `LoadLib()` tries the versioned library, falls back on not-found cases, and tracks bad-library state. `Unload()` drops the plugin object.

State and persistence: Owns `theLib`, `altLib`, optional error buffer, and `XrdSysPlugin`. The destructor persists loaded plugin images unless `Unload()` removed the plugin object.

Dependencies and integration: Wraps `XrdSysPlugin`, `XrdOucVerName`, XRootD version metadata, and server/client diagnostics.

Risks and test signals: Fallback behavior depends on `errno` from plugin loading. Tests should cover versioned path generation, alternate fallback, optional symbols, buffer diagnostics, global symbol mode, explicit unload, and destructor persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.hh

Purpose: Declares the standard versioned plugin loader used throughout XRootD utility and server code.

APIs and control flow: Constructors support diagnostics through an error router, caller buffer, or internal buffer. `Resolve()` loads and resolves symbols, `Global()` controls exported symbol visibility, `Export()` transfers the plugin object, `Path()` exposes the selected path, `LastMsg()` returns buffered diagnostics, and `Unload()` drops the image management object.

State and persistence: The loader owns path strings, diagnostics storage, and optionally an `XrdSysPlugin`. Deleting a loader normally persists a loaded plugin image.

Dependencies and integration: Forward-declares `XrdSysError`, `XrdSysPlugin`, and `XrdVersionInfo` to keep the public loader header light.

Risks and test signals: Callers must understand that `Export()` disables destructor management and that `Unload(true)` deletes the loader itself. Tests should check ownership transfer, optional symbol prefixes, error-buffer truncation, and compatibility with third-party plugin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinObject.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinObject.hh

Purpose: Defines the object-oriented plugin factory interface used by `XrdOucPinKing`.

APIs and control flow: Template interface `XrdOucPinObject<T>::getInstance()` receives plugin parameters, the process/config environment, logger, and an optional previous plugin instance for stacking. It returns a concrete `T*`.

State and persistence: The interface itself is stateless. Implementations in plugin shared libraries determine instance ownership and any persistent state.

Dependencies and integration: Forward-declares `XrdOucEnv` and `XrdSysLogger`. Plugin libraries export a symbol whose object derives from this template specialization.

Risks and test signals: ABI compatibility depends on template specialization, symbol naming, and matching `T`. Tests should load a sample object plugin, verify stacked `prevP` behavior, parameter passing, logger use, and null returns on initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinObject.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.cc

Purpose: Implements a public utility wrapper for computing versioned plugin library paths.

APIs and control flow: `XrdOucPinPath()` delegates to `XrdOucVerName::Version()` with `XRDPLUGIN_SOVERSION`, filling the caller buffer and setting `noAltP` to indicate whether fallback to the original path is allowed.

State and persistence: Stateless; it writes only to caller-provided output parameters.

Dependencies and integration: Integrates public plugin path users with the same version naming logic used by `XrdOucPinLoader`.

Risks and test signals: Buffer size is the main failure mode. Tests should compare output against loader path selection, include paths with and without existing version suffixes, and verify `noAltP` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.hh

Purpose: Declares `XrdOucPinPath()`, a third-party-facing helper for XRootD plugin name versioning.

APIs and control flow: The function accepts an original plugin path, output fallback flag, output buffer, and buffer length. It returns the primary path length or zero on buffer failure.

State and persistence: No owned state. The caller owns the buffer and decides whether to use the alternate original path.

Dependencies and integration: Keeps external code aligned with the same shared-library naming convention used by XRootD plugin loaders.

Risks and test signals: Callers must check a zero return and not assume the buffer is usable. Tests should compile an external-style caller and verify behavior for short buffers and normal plugin names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.cc

Purpose: Implements plugin preloading so a shared library image can be loaded and persisted before later plugin initialization.

APIs and control flow: `XrdOucPreload()` computes the versioned path with `XrdOucVerName::Version()`, writes a path-too-long message on failure, clears the error buffer, and calls `XrdSysPlugin::Preload()` on the versioned path. If `retry` is true, it also tries the original unversioned path.

State and persistence: Stateless locally. Successful `XrdSysPlugin::Preload()` persists the shared library image in process/plugin-loader state.

Dependencies and integration: Uses XRootD plugin version constants, `XrdOucVerName`, and `XrdSysPlugin`.

Risks and test signals: Error reporting depends on caller-provided buffer length. Tests should cover versioned success, retry fallback, path-too-long failure, and preservation of diagnostic text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.hh

Purpose: Declares a small public utility for preloading XRootD plugins.

APIs and control flow: `XrdOucPreload(plib, eBuff, eBlen, retry)` loads the versioned plugin path and optionally retries the original path. It returns true on success and false with diagnostics on failure.

State and persistence: The function has no caller-visible object state, but successful preloads persist plugin images process-wide.

Dependencies and integration: Used by code that wants to force plugin libraries into memory before resolving their runtime objects.

Risks and test signals: The diagnostics buffer should be at least 1 KiB per the comment. Tests should validate retry behavior, too-small buffers, and compatibility with the full `XrdOucPinLoader` path-versioning contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPrivateUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPrivateUtils.hh

Purpose: Declares private utility helpers for path checks and sensitive CGI/header sanitization.

APIs and control flow: Inline `is_subdirectory()` checks whether `subdir` starts with `dir` and either ends there, continues with `/`, or `dir` itself ends with `/`. `obfuscateAuth()` hides authorization-like values. `stripCgi()` overloads remove selected CGI keys from `std::string` and `XrdOucString`. `splitHostCgi()` separates a `host[?cgi]` target into host and CGI portions.

State and persistence: Stateless utility declarations; functions mutate only caller-provided URL/string outputs.

Dependencies and integration: Includes `XrdOucString`, STL strings, regex, unordered sets, and string views. Implementations live in `XrdOucUtils.cc`.

Risks and test signals: Security-sensitive sanitization must handle case variants and malformed URLs. Tests should cover auth obfuscation variants, CGI key removal at beginning/middle/end, empty directories in `is_subdirectory()`, trailing slashes, and targets without `?`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPrivateUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.cc

Purpose: Implements a wrapper for configured external programs or inline procedures, with one-shot run and long-lived feed modes.

APIs and control flow: `Setup()` parses a command string with `XrdOucUtils::argList()`, optionally records an inline procedure, and verifies executable access for external programs. `Run()` variants append extra args, optionally set environment through `XrdOucStream`, execute, drain output, capture the first output line, and translate wait status into negative errno-style returns. `Start()` creates a persistent stream and starts the command. `Feed()` serializes writes with a static mutex, restarts a dead process, retries failed writes once after restart, and reports errors.

State and persistence: Owns parsed argument buffer/argv, optional stream, inline procedure pointer, and error fd. Long-lived process state is managed through `XrdOucStream`.

Dependencies and integration: Uses `XrdOucStream`, `XrdOucEnv`, `XrdOucUtils`, `XrdSysError`, POSIX process/wait APIs, and Win32 compatibility.

Risks and test signals: `Feed()` uses a single static mutex across all program instances, and restart semantics can duplicate input attempts. Tests should cover setup parsing, missing executables, inline procedures, env passing, output capture trimming, signal exits, and persistent restart/feed behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.hh

Purpose: Declares the program execution helper used to run external commands or in-process command procedures.

APIs and control flow: Public methods include `Setup()`, `Run()` overloads, `RunDone()`, `Start()`, `Feed()` overloads, `getStream()`, and `isLocal()`. Private `Reset()` and `Restart()` manage parsed arguments and persistent process restart.

State and persistence: Stores optional error route, current stream, inline procedure pointer, parsed argument storage, argument count, and error fd. It owns the stream and argument buffer.

Dependencies and integration: Forward-declares `XrdSysError` and `XrdOucStream`; includes POSIX `sys/types.h`. It is a utility layer for command hooks and helpers elsewhere in XRootD.

Risks and test signals: Users must call `Setup()` before `Run()` or `Start()`, and persistent stream users must drain output. Tests should check overload consistency, destructor cleanup, copy avoidance, and behavior when commands produce large or no output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.cc

Purpose: Implements parsing and materialization of proxy/client-side XRootD configuration for caching, name translation, network mode, trace/debug, and client options.

APIs and control flow: `ClientConfig()` opens the config file, reads directives matching a prefix, dispatches to `Parse()`, captures diagnostics when `hush` is enabled, and then calls `ConfigSetup()`. `ConfigSetup()` loads cache libraries, cache context manager plugins, and name translation. `ParseCache()` builds cache parameter strings including size, pages, preread, stats, and write options. `ParseCLib()`, `ParseMLib()`, `ParseNLib()`, `ParseCio()`, `ParseINet()`, `ParseSet()`, and `ParseTrace()` validate and store directive state. `ConfigCache()`, `LoadCCM()`, and `ConfigN2N()` instantiate configured plugins through `XrdOucPinLoader` and `XrdOucN2NLoader`.

State and persistence: The object owns config strings, plugin paths/params, set-option lists, cache and name-mapper pointers, trace/debug levels, inet mode, and cache behavior flags. Environment exports and loaded plugins affect process state.

Dependencies and integration: Ties together `XrdOuca2x`, `XrdOucCache`, `XrdOucN2NLoader`, `XrdOucPinLoader`, `XrdOucStream`, `XrdOucTList`, and `XrdSysLogger`.

Risks and test signals: `SetRoot()` appears to call `strdup(lroot)` even after `lroot` is null because the assignment block is unconditional. Parser tests should cover every directive, hush diagnostics, default cachelib translation, unsupported setopts, namelib/cache interactions, plugin failures, and null-root handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.hh

Purpose: Declares the proxy/client configuration state object used to parse and apply XRootD client-side settings.

APIs and control flow: Public methods parse individual directives, perform full client config, configure loaded objects, expose cache context-manager info, and set name-translation roots. Public fields expose materialized cache, mapper, logger, environment, option list, trace/debug, retry, and name-mapping flags to integrating code.

State and persistence: Owns many heap strings for config path, roots, plugin paths, plugin params, and cache params. Holds pointers to externally integrated cache and mapper objects and a list of client option overrides.

Dependencies and integration: Includes cache context-manager declarations and forward-declares core XrdOuc/XrdSys types. It is a central handoff object between config parsing and client/proxy runtime setup.

Risks and test signals: Many fields are public for integration, so ABI and initialization defaults matter. Tests should validate constructor defaults, destructor cleanup, parse method idempotence, root-setting behavior, and consumers of `xPfn2Lfn`/`xLfn2Pfn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.cc

Purpose: Implements compact pack/unpack helpers for length-prefixed strings, numeric values, and descriptor-driven structured messages.

APIs and control flow: Static `Pack()` overloads encode strings/binary blobs into `iovec` or contiguous buffers, always adding a network-order length for data blobs. Numeric `Pack()` uses a compact inline encoding when possible. Descriptor-driven `Pack()` walks `XrdOucPupArgs`, emits typed numeric values, strings, marker/skipped iovec entries, data/total lengths, and end-fill values. `Unpack()` reads length-prefixed data or descriptor-driven typed streams, respects `PT_Fence` optional boundaries, and writes pointers or converted integers into caller structures. `eMsg()` formats diagnostics by type and optional names.

State and persistence: The object stores optional error routing and names. Pack/unpack functions mutate caller buffers, iovec arrays, and target structures but do not persist data.

Dependencies and integration: Uses network byte order conversions, platform endian helpers, `iovec`, and `XrdSysError`. It supports XRootD internal protocol serialization.

Risks and test signals: Correct alignment of target structures is the caller's responsibility. Tests should cover every descriptor type, optional fences, too-long strings, iovec overflow, buffer overrun detection, endian conversion, null strings, and mismatch diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.hh

Purpose: Declares the pack/unpack descriptor language and utility API for internal binary message serialization.

APIs and control flow: `XrdOucPupType` defines control entries, scalar types, masks, inline encoding flags, and end markers. `XrdOucPupArgs` maps a field offset, data length, name index, and type. `XrdOucPupNames` supplies diagnostic names. Macros `setPUP0`, `setPUP1`, and `setPUP2` simplify descriptor tables. `XrdOucPup` exposes static primitive pack/unpack helpers and instance descriptor-driven pack/unpack.

State and persistence: Descriptor tables are caller-owned. `XrdOucPup` stores only optional diagnostics pointers.

Dependencies and integration: Includes offsets and POSIX stat/types, forward-declares `iovec`, and works with `XrdSysError`.

Risks and test signals: `MaxLen` caps packed strings at 0x7ff in descriptor mode, and field offsets rely on C struct layout. Tests should validate descriptor macros, optional entry handling, fixed binary lengths, name diagnostics, and compatibility between packed data generated by old and new builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.hh -->
