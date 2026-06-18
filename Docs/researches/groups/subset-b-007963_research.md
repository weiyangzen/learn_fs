# subset-b-007963 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssConfig.cc

## Purpose

`XrdPssConfig.cc` performs startup configuration for the XRootD proxy storage service. It parses `pss.*`, `oss.defaults`, and `all.export` directives, initializes POSIX client settings, origin/forwarding proxy state, cache/N2N settings, persona mapping, reproxy support, permit rules, and exported environment variables used by downstream xrootd client code.

## Important APIs, Types, And Functions

- Static `XrdPssSys` members store global proxy configuration: `ConfigFN`, `myHost`, `myName`, `XPList`, `Police`, `ManList`, `fileOrgn`, `protName`, `hdrData`, `Streams`, `Workers`, trace flags, DCA/reproxy/persona booleans.
- `XrdPssSys::Configure(cfn, envP)` is the top-level initializer. It creates an `XrdOucPsx`, sets default `XrdPosixConfig` options, calls `ConfigProc()`, validates origin state, configures identity mapping, finalizes the POSIX client config, allocates `XrdPosixXrootd`, sets session-id support, registers accepted protocols, and exports `XRDXROOTD_PROXY`, `XRDXROOTD_ORIGIN`, and `XRDXROOTD_PROXYURL`.
- `ConfigProc()` opens and scans the config file with `XrdOucStream`, captures relevant directives, dispatches through `ConfigXeq()`, and finalizes export defaults.
- `ConfigXeq()` maps directives to parser methods. Some are delegated to `XrdOucPsx` (`namelib`, `cache`, `cachelib`, `inetmode`, `setopt`, `trace`), while local handlers cover `config`, `dca`, `defaults`, `export`, `origin`, `permit`, `persona`, `hostarena`, `localroot`, and `reproxy`.
- `ConfigMapID()` builds an `XrdSecsssID` mapper and enables URL identity mapping when persona mode requires client ID propagation.
- Directive parsers include `xconf()`, `xdca()`, `xdef()`, `xexp()`, `xorig()`, `xperm()`, and `xpers()`.

## Control Flow

Startup begins by collecting environment and instance identity, exporting `XRDXROOTD_NOPOSC=1`, creating `psxConfig`, applying debug/IP/event-loop defaults, and parsing the config file. After parsing, `Configure()` rejects configurations without an origin unless running as a forwarding proxy, re-exports cache stream state from `envP`, initializes persona mapping if requested, handles local roots, disables LFN-to-PFN mapping in forwarding mode, advertises cache/reproxy features, opens the TPC reproxy directory if enabled, finalizes `XrdOucPsx`, and installs it into `XrdPosixConfig`.

Origin parsing is central. `xorig()` supports local filesystem origins, regular host/port origins, protocol URLs, and forwarding-proxy syntax beginning with `=`. Forwarding syntax can restrict allowed protocols via `XrdPssUtils::Vectorize()` and `valProt()`. URL origins normalize `xroot` to `root` protocol names where needed and use protocol-specific default ports when omitted.

## State And Persistence

This file mutates process-wide static state. Configuration does not persist to disk beyond exported environment variables and the open `rpFD` directory descriptor for reproxy metadata. `ManList`, `fileOrgn`, `hdrData`, protocol vectors, permit lists, and POSIX config environment survive for the process lifetime. Several strings are heap-allocated with `strdup()` and intentionally live for the plugin lifetime.

## Dependencies And Integration Points

The file depends on `XrdOucPsx`, `XrdPosixConfig`, `XrdPosixXrootd`, `XrdPosixXrootdPath`, `XrdOucExport`, `XrdNetSecurity`, `XrdNetUtils`, `XrdSecsssID`, `XrdPssUrlInfo`, and `XrdPssUtils`. It integrates with the larger proxy implementation through global variables in the `XrdProxy` namespace, `XrdPssSys` feature flags, exported environment consumed by the xrootd client, and security persona mapping used later by URL generation.

## Risks And Edge Cases

- Configuration is global and order-sensitive; repeated `origin` directives replace `ManList` or `fileOrgn`.
- `xdca()` appears to check `"off"` against the current token before reading the recheck value, so `dca recheck off` may not behave as the comment implies.
- The domain check in `xorig()` compares `protName` to both `"http://"` and `"https://"` with `&&`, which can never be true; only hostname-without-dot can set `DirlistDflt`.
- Memory ownership is manual and mostly process-lifetime; early error returns after partial allocation can leave state set.
- Persona mapping is explicitly rejected for caching proxies and strict forwarding proxies; configuration tests need to cover those failures because enforcement happens only at startup.
- `ConfigProc()` dispatches `oss.defaults` and `all.export` using `var+4`, relying on those strings aligning with local handler names.

## Test Signals

Useful tests should parse origin forms for local paths, `root://`, `xroot://`, `http://`, `https://`, forwarding-only `=`, forwarding protocol lists, omitted ports, service-name ports, malformed URLs, and trailing `+`. Persona tests should cover client/server, verify/noverify, strict/nonstrict, cache rejection, and forwarding rejection. Reproxy tests need TPC env presence and directory-open failure. Export/default tests should assert `XPList`, object ID enablement, and the exported `XRDXROOTD_*` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssTrace.hh

## Purpose

`XrdPssTrace.hh` defines the trace mask constants and debug macros for the proxy storage service. It gives PSS code a small wrapper over `XrdSysTrace` with a single debug bit and compile-time no-debug behavior.

## Important APIs, Types, And Functions

- `TRACEPSS_ALL` and `TRACEPSS_Debug` define the available PSS trace masks.
- `QTRACE(act)`, `TRACING(x)`, `DEBUGON`, `DEBUG(tid,y)`, and `EPNAME(x)` expand to `SysTrace` checks and `SYSTRACE` calls when `NODEBUG` is not defined.
- Under `NODEBUG`, tracing checks become false/no-op macros.

## Control Flow

There is no runtime control flow beyond macro expansion. Callers set `SysTrace.What` elsewhere, notably from `XrdPssConfig.cc` when `XRDDEBUG` or `pss.debug` is configured.

## State And Persistence

The header owns no state. It assumes an accessible `SysTrace` object and per-function `epname` string when debug macros are used.

## Dependencies And Integration Points

The non-`NODEBUG` path includes `XrdSys/XrdSysTrace.hh` and integrates with PSS files that use `EPNAME` and `DEBUG` for diagnostics. Configuration enables the mask.

## Risks And Edge Cases

- The `NODEBUG` `DEBUG` macro has a different parameter shape than the active macro, which can expose compile issues if used with two arguments in no-debug builds.
- Only one debug flag is defined, so adding more detailed categories requires coordinated changes to config parsing and this header.

## Test Signals

Build coverage should include debug and no-debug configurations. Runtime signal is visible `SysTrace` output after enabling `pss.debug` or `XRDDEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.cc

## Purpose

`XrdPssUrlInfo.cc` implements request URL metadata handling for PSS. It carries the target path, client CGI, proxy-added CGI, trace identity, and optional compact identity string used when constructing upstream URLs.

## Important APIs, Types, And Functions

- Static `XrdPssUrlInfo::MapID` toggles whether `setID()` uses the security entity unique ID instead of parsing the trace identifier.
- Local `copyCGI()` copies client CGI while stripping `xrd.*` and `xrdcl.*` keys that can interfere with xrootd upstreams.
- The constructor captures user CGI from `XrdOucEnv`, extracts `XrdSecEntity::ueid` and `tident`, falls back to `"unk.0:0@host"`, and builds optional `pss.tid=<tident>` suffix CGI.
- `addCGI(prot, buff, blen)` appends query text appropriate for the upstream protocol. For xroot-family protocols it strips sensitive xroot CGI keys and includes proxy suffix CGI; for other protocols it forwards only the client CGI.
- `Extend(cgi, cgiln)` appends additional suffix CGI with an ampersand separator.
- `setID(tid)` creates a compact ID from either the security entity ID or the file descriptor portion of a trace identity.

## Control Flow

Construction prepares immutable per-request metadata. When the proxy builds an upstream URL, `addCGI()` first determines whether the target protocol is xroot-family via `XrdPssUtils::is4Xrootd()`. If no CGI is needed, it emits an empty suffix. Otherwise it adds `?`, filters or copies user CGI, and appends proxy suffixes only for xroot-family targets. `setID()` is called when the upstream URL needs an identity prefix; it prefers mapped entity IDs when configured, otherwise parses `pid:fd@host` from `tident`.

## State And Persistence

State is per `XrdPssUrlInfo` instance except for static `MapID`. The object stores borrowed pointers to path, user CGI, and trace identity, plus local fixed-size buffers for ID and suffix CGI. If a session ID is obtained through `setID(XrdOucSid*)`, the destructor releases it.

## Dependencies And Integration Points

The implementation uses `XrdOucEnv`, `XrdOucSid`, `XrdSecEntity`, and `XrdPssUtils`. It is configured by `XrdPssConfig.cc` through `setMapID(true)` when client persona mapping is active and is used by proxy request paths that construct upstream URLs and preserve request identity.

## Risks And Edge Cases

- `CgiSfx` is fixed at 512 bytes; long trace identifiers or extra CGI can be rejected.
- `addCGI()` must be called with a large enough buffer; it returns false instead of truncating.
- `copyCGI()` strips only CGI keys beginning at component boundaries; unusual encoding or capitalization is not normalized.
- Borrowed `XrdOucEnv` strings and path pointers must remain valid for the request lifetime.
- `setID()` depends on trace identifier format and silently produces an empty ID on unexpected format or length.

## Test Signals

Tests should cover no CGI, user CGI only, suffix CGI only, xroot and non-xroot protocols, stripping `xrd.*` and `xrdcl.*`, buffer exhaustion, `Extend()` separator behavior, mapped entity IDs, trace-ID parsing, and session-ID release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.hh

## Purpose

`XrdPssUrlInfo.hh` declares the per-request URL helper used by PSS to expose path, CGI suffix construction, trace identity, and optional session/entity ID generation.

## Important APIs, Types, And Functions

- Constructor `XrdPssUrlInfo(XrdOucEnv*, const char*, const char*, bool, bool)` captures request environment data and extra CGI policy.
- `addCGI()`, `Extend()`, `hasCGI()`, `thePath()`, `Tident()`, and `getID()` are the primary URL-building accessors.
- `setID(const char*)` derives an ID from trace or entity state.
- `setID(XrdOucSid*)` obtains a session ID and formats `p<sid>@`.
- Static `setMapID(bool)` selects security-entity ID mapping behavior.

## Control Flow

The header exposes a two-step use pattern: construct from request environment, optionally extend CGI and set an ID, then ask `addCGI()` for a protocol-appropriate suffix. Destructor cleanup only matters for session IDs acquired from `XrdOucSid`.

## State And Persistence

State is request-local and stored in fixed buffers plus borrowed pointers. `MapID` is process-global. `idVal` tracks a borrowed session ID lease when used.

## Dependencies And Integration Points

The header forward-declares `XrdOucEnv` but directly uses `XrdOucSid` types without including its header, relying on include order from users. It integrates with PSS URL generation and persona mapping.

## Risks And Edge Cases

- Missing direct declarations for `XrdOucSid` make the header fragile unless included after a header defining it.
- Fixed-size `theID[13]` and `CgiSfx[512]` impose silent formatting limits enforced in the implementation.
- Destructor behavior depends on `theID` beginning with `p` to release a session ID.

## Test Signals

Compile tests should include this header in isolation or document required include order. Runtime tests should validate ID lifetime and suffix construction through the public API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.cc

## Purpose

`XrdPssUtils.cc` implements small protocol and string helpers used by PSS configuration and URL handling.

## Important APIs, Types, And Functions

- Static protocol table recognizes `https://`, `http://`, `roots://`, `root://`, `xroots://`, `xroot://`, `pelican://`, and `s3://`.
- `getDomain(hName)` returns the substring after the first dot, or the whole hostname when no dot exists.
- `is4Xrootd(pname)` detects root/xroot-family protocol names.
- `valProt(pname, plen, adj)` validates a protocol prefix and returns the canonical table entry while reporting matched length.
- `Vectorize(str, vec, sep)` splits a mutable string in-place on a separator and rejects empty components.

## Control Flow

Callers pass raw strings. `valProt()` scans the table in order and can match shortened entries by subtracting `adj` from the required prefix length; `xorig()` uses this for forwarding protocol lists that omit URL punctuation. `Vectorize()` repeatedly replaces separators with NUL bytes and stores pointers into the original buffer.

## State And Persistence

Only static immutable protocol metadata is stored. `Vectorize()` mutates caller-owned memory and returns borrowed pointers into that buffer.

## Dependencies And Integration Points

The file depends on C string routines and is used by `XrdPssConfig.cc` for origin and forwarding protocol validation and by `XrdPssUrlInfo.cc` for CGI behavior.

## Risks And Edge Cases

- `Vectorize()` rejects trailing separators and empty elements but leaves the input partially modified on failure.
- `getDomain()` is a simple first-dot split and does not handle FQDN trailing dots, public suffixes, or null input.
- `valProt()` with `adj` can match abbreviated prefixes; callers must choose `adj` carefully.

## Test Signals

Tests should cover all supported protocol prefixes, unsupported strings, `xroot` vs non-xroot classification, forwarding lists with empty/trailing components, and hostnames with/without dots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.hh

## Purpose

`XrdPssUtils.hh` declares shared PSS helper functions and the inline forwarding-path test macro.

## Important APIs, Types, And Functions

- `XrdPssUtils::getDomain()`, `is4Xrootd()`, `valProt()`, and `Vectorize()` are stateless static helpers.
- `IS_FWDPATH(x)` detects path-encoded root/xroot forwarding forms such as `/root:/` and `/xroot:/`.

## Control Flow

The declared helpers are called by config and URL code. `IS_FWDPATH` is a raw macro that reads fixed offsets from its argument and should only be used on strings known to be long enough and slash-prefixed.

## State And Persistence

No state is declared in the header.

## Dependencies And Integration Points

The header includes `<vector>` and is included by PSS config and URL code. The macro encodes PSS forwarding semantics shared with path handling outside this subset.

## Risks And Edge Cases

- `IS_FWDPATH` performs unchecked pointer arithmetic and prefix reads.
- `Vectorize()` returns pointers into mutable caller storage, which the header comment documents but callers must honor.

## Test Signals

Compile tests should include the header in PSS users. Behavior tests should cover the macro on valid forwarding paths and ensure callers do not pass too-short strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdRmc/CMakeLists.txt

## Purpose

This CMake fragment adds the RMC memory-cache implementation sources and headers to the `XrdUtils` target.

## Important APIs, Types, And Functions

- `target_sources(XrdUtils PRIVATE ...)` registers `XrdRmc.cc`, `XrdRmcData.cc`, `XrdRmcReal.cc`, and their headers plus `XrdRmcSlot.hh`.

## Control Flow

CMake evaluates this fragment during the main build and compiles RMC directly into `XrdUtils`; it does not create a separate plugin or library target.

## State And Persistence

The file has no runtime state. Build-state effect is that RMC symbols become part of `XrdUtils`.

## Dependencies And Integration Points

It depends on a parent build defining `XrdUtils`. RMC then integrates with any component linking `XrdUtils` and using `XrdOucCache`.

## Risks And Edge Cases

- Because headers are listed as private target sources, install/export behavior depends on the broader project rules.
- Any source added to RMC must be added here or it will not compile into `XrdUtils`.

## Test Signals

Build signal is successful compilation of `XrdUtils` with RMC enabled. Link tests should verify `XrdRmc::Create` is available to consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.cc -->
# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.cc

## Purpose

`XrdRmc.cc` provides the public factory for the remanufactured memory cache.

## Important APIs, Types, And Functions

- `XrdRmc::Create(Parms&, XrdOucCacheIO::aprParms*)` constructs `XrdRmcReal`, deletes it on initialization failure, sets `errno`, and returns it as `XrdOucCache*`.

## Control Flow

The factory delegates all parameter validation and allocation to `XrdRmcReal`. The `rc` out parameter from the constructor determines success.

## State And Persistence

No static state is maintained here. Returned cache lifetime is owned by the caller through the `XrdOucCache` interface.

## Dependencies And Integration Points

It depends on `XrdRmc.hh` and `XrdRmcReal.hh`. It is the stable API entrypoint for users that do not need to know the concrete `XrdRmcReal` type.

## Risks And Edge Cases

- Constructor failure uses a partially constructed object plus `rc`; destructor behavior must be safe on failed initialization.
- `errno` is the only detailed error channel.

## Test Signals

Tests should create caches with default parameters, impossible allocation sizes, invalid page/cache sizes, and optional preread parameters, checking returned pointer and `errno`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.hh -->
# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.hh

## Purpose

`XrdRmc.hh` declares the public memory-cache facade and parameter contract for a general `XrdOucCache` implementation over arbitrary `XrdOucCacheIO` sources.

## Important APIs, Types, And Functions

- `struct XrdRmc::Parms` defines `CacheSize`, `PageSize`, `Max2Cache`, `MaxFiles`, `Options`, `minPages`, and reserved fields.
- Option bits include `isServer`, `isStructured`, `canPreRead`, `logStats`, `Serialized`, `ioMTSafe`, and `Debug`.
- `XrdRmc::Create()` is the sole public factory.

## Control Flow

Consumers fill `Parms`, optionally provide automatic-preread parameters, call `Create()`, then attach `XrdOucCacheIO` objects through the returned cache. The detailed behavior described in comments maps to `XrdRmcReal` and `XrdRmcData`.

## State And Persistence

The header declares no static state. Cache state lives in the implementation returned by `Create()`.

## Dependencies And Integration Points

It includes `XrdOuc/XrdOucCache.hh` and is used by callers that want an in-memory, write-through, optionally structured/preread cache.

## Risks And Edge Cases

- Comments mention a maximum page size and write-in behavior, but the observed implementation mostly normalizes page size and currently uses write-through writes.
- Option semantics require careful caller coordination for `Serialized` and `ioMTSafe`; incorrect flags can create unnecessary locking or unsafe sharing.

## Test Signals

API tests should verify default parameter construction, option bit combinations, structured-file optimization, preread enablement, and write-through behavior via the `XrdOucCache` interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.cc -->
# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.cc

## Purpose

`XrdRmcData.cc` implements the `XrdOucCacheIO` wrapper used for each attached I/O object in the RMC cache. It performs cached reads, write-through updates, truncation, detach cleanup, per-file statistics, and manual/automatic preread scheduling.

## Important APIs, Types, And Functions

- Constructor maps attach options (`optFIS`, `optRW`) into local flags, copies cache geometry, initializes preread queues, configures automatic preread parameters, and sets read/preread/write locks based on cache thread-safety options.
- `Detach()` waits for prereads to stop, serializes detach, asks `XrdRmcReal` to detach the underlying object, merges stats, optionally logs them, and deletes itself.
- `Read(Buff, Offs, rLen)` handles both preread requests (`Buff == nullptr`) and normal cached reads, including bypass for reads larger than `maxCache`.
- Private `Read(Now, Buff, Offs, rLen)` implements the large-read bypass path, mixing cache hits with direct I/O for misses.
- `Write()` writes through to the underlying object first, then updates cached pages that are already present.
- `Trunc()` invalidates cached pages from the truncation point and delegates the real truncate.
- `Preread()`, `Preread(Offs, rLen, Opts)`, `Preread(aprParms&)`, `QueuePR()`, and `setAPR()` implement asynchronous and automatic preread behavior.

## Control Flow

Normal reads validate bounds, optionally remember recent reads for automatic preread suppression, then fetch page buffers through `Cache->Get()`. Hits copy from cached pages; misses cause `XrdRmcReal` to read a segment from the underlying object. Each page is released through `Cache->Ref()`, with structured-file accounting when enabled. After a successful read, automatic preread can enqueue the next segment range.

Large reads over `maxCache` avoid filling the cache. That path cancels overlapping prereads, copies any existing cache hits, accumulates contiguous cache misses into direct `ioObj->Read()` calls, and records pass-through statistics. Writes are strictly write-through: failure to write the underlying object aborts cache updates.

Preread requests are stored in an eight-entry ring. The preread worker calls `Preread()`, consumes queued ranges, faults pages into the cache with `isNew` and optionally `isSUSE`, and updates preread stats. Detach coordinates with active prereads through `prStop` and semaphores.

## State And Persistence

All state is per attached file wrapper: statistics, read/write lock, underlying `ioObj`, virtual file number `VNum`, cache geometry, flags, recent-read ring, preread queue, automatic preread tuning, and active/stop markers. Cache contents live in `XrdRmcReal` memory, not this object. No state is persisted to disk.

## Dependencies And Integration Points

The class depends on `XrdRmcReal`, `XrdOucCacheIO`, `XrdOucCacheStats`, `XrdSysXSLock`, `XrdSysMutex`, and `XrdSysSemaphore`. It is created by `XrdRmcReal::Attach()` and deleted after successful detach.

## Risks And Edge Cases

- `Preread(long long Offs, int rLen, int Opts)` has a condition that returns when the request appears valid, meaning only invalid-looking requests fall through to `QueuePR()`; this is suspicious and should be tested.
- Detach comments acknowledge that failed detach can leak the wrapper because it will not retry.
- Cache locking depends on caller-supplied `Serialized` and `ioMTSafe` options; incorrect flags can cause over-serialization or races.
- Large-read path mixes direct I/O and cache hits; partial direct reads return the accumulated destination length, so EOF and short reads require careful validation.
- Fixed preread queue depth discards or skips older entries under pressure.

## Test Signals

Tests should cover small cached reads, repeated hits, reads larger than `maxCache`, read overflow and negative offsets, `Buff == nullptr` preread requests, automatic preread enable/disable based on performance, write-through update of existing cached pages, read-only write rejection, truncation invalidation, detach with active prereads, and structured-file single-use behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.hh -->
# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.hh

## Purpose

`XrdRmcData.hh` declares the per-I/O-object cache wrapper that presents `XrdOucCacheIO` methods while routing reads, writes, truncation, and prereads through `XrdRmcReal`.

## Important APIs, Types, And Functions

- Public overrides include `Detach()`, `FSize()`, `Path()`, `Preread()`, `Preread(aprParms&)`, `Preread(Offs, rLen, Opts)`, `Read()`, `Sync()`, `Trunc()`, and `Write()`.
- Static `setAPR()` normalizes automatic preread parameters.
- Private `MrSw` RAII helper manages optional multiple-reader/single-writer locks.
- Private fields store stats, locks, cache pointer, underlying I/O pointer, virtual segment namespace, geometry, flags, and preread queue/ring state.

## Control Flow

The declaration shows that `XrdRmcData` is constructed only by `XrdRmcReal` and self-deletes through `Detach()`. Public `Sync()` is a no-op because the implementation is write-through.

## State And Persistence

Per-instance state covers file statistics and preread scheduling. There is no persistent storage; `Statistics` is merged into the parent cache at detach.

## Dependencies And Integration Points

It includes `XrdOucCache.hh`, `XrdRmcReal.hh`, `XrdSysPthread.hh`, and `XrdSysXSLock.hh`. It is a friend-level collaborator of `XrdRmcReal` through the parent class interfaces.

## Risks And Edge Cases

- Destructor is private and empty, so lifetime must follow the `Detach()` protocol.
- `Sync()` always returns success, which is correct for write-through but could surprise callers expecting underlying sync behavior.
- Many preread constants are fixed in the class, making tuning impossible without code changes.

## Test Signals

Compile tests should treat it as an `XrdOucCacheIO`. Runtime tests should verify caller-visible `Path`, `FSize`, `Sync`, and lifecycle semantics through `XrdRmcReal::Attach()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcData.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.cc -->
# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.cc

## Purpose

`XrdRmcReal.cc` implements the actual shared memory cache behind RMC. It owns page memory, slot metadata, file attachment tracking, hash tables, LRU lists, preread worker threads, and cache page fault/ref/update/truncation operations.

## Important APIs, Types, And Functions

- Constructor normalizes parameters, allocates anonymous `mmap` memory for data plus a hash table, allocates `XrdRmcSlot` metadata, initializes page LRU, file-slot free lists, and optional preread threads.
- Destructor waits for attached files to detach, stops preread threads, deletes slots, and unmaps cache memory.
- `Attach(ioP, Opts)` maps an `XrdOucCacheIO` to a file slot and returns an `XrdRmcData` wrapper, reusing one wrapper for duplicate attachments.
- `Detach(ioP)` drops an I/O attachment, releases all page slots owned by the file when the final reference disappears, and signals destructor waiters.
- `Get(ioP, lAddr, rAmt, noIO)` is the central page lookup/fault method. It handles hits, in-transit waits, free-slot selection, owner/hash removal, underlying reads, waiter wakeup, and slot initialization.
- `Ref()`, `Upd()`, and `Trunc()` release references, update cached writes, and invalidate cached pages.
- `PreRead()` worker loop and `PreRead(prTask*)` queue preread work.
- `ioAdd()`, `ioDel()`, `ioEnt()`, and `ioLookup()` track attached underlying I/O objects.

## Control Flow

Initialization computes a power-of-two segment size, segment count, maximum cached read size, and file-slot capacity. The page data area is anonymous memory; slots `1..SegCnt-1` form the LRU pool, while slots from `SegCnt` onward track attached file objects. Preread threads wait on `prReady`.

`Get()` first checks the hash bucket for a logical address. If a slot is in transit, the caller waits on a stack semaphore linked into the slot wait queue. On a miss with an I/O object, the least-recent free slot is pulled, detached from prior ownership/hash state, marked in transit, and filled by reading from the underlying object without holding the cache mutex. Waiters are posted before the caller returns the buffer. `Ref()` later marks consumption, adjusts single-use/LRU behavior, and indicates EOF state to sequential readers.

Deletion is cooperative. The destructor blocks on `AZero` until `Attached` reaches zero; preread worker shutdown is then coordinated with `prStop` and semaphore chaining.

## State And Persistence

All cache state is in process memory: `Base` mmap data, `Slash` content hash, `Slots`, file hash table `hTab`, free file-slot list, attach counts, LRU/owner lists, debug flags, and preread queue/thread counters. There is no durable persistence.

## Dependencies And Integration Points

It depends on POSIX `mmap/munmap`, pthread-style XRootD thread helpers, `XrdRmcData`, `XrdRmcSlot`, and `XrdOucCache`. It is created only through `XrdRmc::Create()` and serves `XrdRmcData` wrappers.

## Risks And Edge Cases

- Destructor calls `delete Slots` for an array allocated with `new[]`, which is a correctness risk.
- `munmap()` uses only `SegSize * SegCnt`, while allocation included `SegCnt * sizeof(int)` for the hash table, potentially leaving the trailing mapping length inconsistent.
- `ioEnt()` hashes pointer bytes through a union with four shorts, which is pointer-size sensitive and dated.
- In-transit waiter logic depends on stack semaphore lifetime and precise wakeup ordering under the cache mutex.
- Failed I/O frees the slot and wakes waiters, which then detect changed contents as `-EIO`.
- Cache capacity/lifetime behavior relies on `XrdRmcSlot` list invariants; list corruption would be hard to diagnose.

## Test Signals

Tests should cover parameter normalization, allocation failure, attach/detach reference counting, duplicate attachment reuse, cache hit/miss/fault behavior, simultaneous readers of the same missing page, read error propagation, LRU eviction, truncation invalidation, write update, preread thread shutdown, and destructor with live attachments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.hh -->
# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.hh

## Purpose

`XrdRmcReal.hh` declares the concrete `XrdOucCache` implementation used by RMC and exposes internals needed by `XrdRmcData`.

## Important APIs, Types, And Functions

- Public `Attach()`, constructor, destructor, and worker `PreRead()` implement the `XrdOucCache` lifecycle.
- Private cache operations include `Detach()`, `Get()`, `Ref()`, `Trunc()`, `Upd()`, `PreRead(prTask*)`, and I/O tracking helpers.
- Constants `Shift`, `Strip`, and `MaxFO` encode the logical address format: high bits identify the attached file namespace and low bits identify file offsets.
- Fields hold cache geometry, slot arrays, hash tables, file-slot free list, debug/log flags, attach deletion semaphores, and preread queue state.

## Control Flow

The header establishes `XrdRmcData` as a friend and collaborator. Data wrappers call private methods to fault pages, release references, and enqueue prereads while the cache controls global memory and slot ownership.

## State And Persistence

The class owns all process-memory cache state. It has no persistence contract beyond the lifetime of the `XrdRmcReal` object.

## Dependencies And Integration Points

It includes `XrdRmc.hh`, `XrdRmcSlot.hh`, and `XrdSysPthread.hh`, and implements the `XrdOucCache` API from `XrdRmc.hh`.

## Risks And Edge Cases

- The logical address format limits file offset range to `MaxFO`.
- The private hash/list machinery is not encapsulated behind standard containers, so callers must not bypass the `XrdRmcData` protocol.
- Preread task nodes are embedded in `XrdRmcData`; queue validity depends on wrapper lifetime coordination.

## Test Signals

Header-level tests should compile the class through `XrdRmc::Create()` and exercise behavior via the public `XrdOucCache` API. Concurrency tests should stress `Get`, `Ref`, and preread queue interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcSlot.hh -->
# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcSlot.hh

## Purpose

`XrdRmcSlot.hh` defines the compact metadata node used for both cached page slots and attached-file slots in the RMC cache.

## Important APIs, Types, And Functions

- `File()` initializes a file-tracking slot.
- `Find()` scans a hash chain by logical address.
- `Hide()` removes a page slot from a hash bucket and marks it empty.
- `Init()` initializes the page-slot LRU list.
- `Pull()` and `Push()` manipulate LRU list membership.
- `Owner()` overloads remove or attach a page slot to a file-owner list.
- `reRef()` and `unRef()` move slots between referenced and free/LRU positions.
- `SlotState` union holds either an I/O wait queue, `XrdRmcData*`, LRU links, or in-use count depending on slot role.
- Count flags include `lenMask`, `isShort`, `inTrans`, `isSUSE`, and `isNew`.

## Control Flow

The slot is intentionally low-level. `XrdRmcReal` chooses how to interpret union fields based on whether a slot represents page data or a file anchor. LRU and owner operations are intrusive list updates over integer indexes into the slot array.

## State And Persistence

Each slot stores either `Contents` or `Key`, a union status field, owner links, hash link, and count/flags. State is volatile in process memory.

## Dependencies And Integration Points

It forward-declares `XrdRmcData`, `XrdOucCacheIO`, and `XrdSysSemaphore`. The entire RMC implementation depends on the invariants maintained by this class.

## Risks And Edge Cases

- Union fields are role-dependent; accidental use of the wrong interpretation corrupts cache state.
- Inline list operations have minimal validation and assume sentinel/index invariants.
- Count combines length, flags, transit state, and reference accounting in one integer, increasing the chance of mask mistakes.

## Test Signals

Unit tests for slot list operations should initialize small arrays, push/pull/re-reference/unreference slots, manipulate owner lists, and verify hash-chain removal. Integration cache tests are also needed because slot bugs manifest as cache corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcSlot.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/CMakeLists.txt

## Purpose

This CMake fragment conditionally builds and installs the `XrdAccSciTokens` authorization plugin when SciTokens support is enabled and `SciTokensCpp` is available.

## Important APIs, Types, And Functions

- Clears `BUILD_SCITOKENS` cache state, returns early unless `ENABLE_SCITOKENS` is set.
- Uses `find_package(SciTokensCpp REQUIRED)` when `FORCE_ENABLED` is set, otherwise optional discovery.
- Defines module target `XrdAccSciTokens-${PLUGIN_VERSION}` from access, helper, and monitoring sources.
- Links against `XrdUtils`, `XrdServer`, `${SCITOKENS_CPP_LIBRARIES}`, thread libs, and dl libs.
- Adds include directories for vendored `inih`, `picojson`, and SciTokens headers.
- Defines `HAVE_SCITOKEN_CONFIG_SET_STR` when available and installs the module.

## Control Flow

Build flow is feature-gated. If SciTokens support is disabled or package discovery fails in non-forced mode, no plugin target is added. Successful discovery makes `BUILD_SCITOKENS` true and compiles the module.

## State And Persistence

The only persistent build state is the internal CMake cache variable `BUILD_SCITOKENS` and the installed shared module.

## Dependencies And Integration Points

This integrates with the project plugin build, SciTokens C++ library, XRootD server/utils targets, vendored INI/JSON parsers, and optional compile-time SciTokens configuration API availability.

## Risks And Edge Cases

- Optional discovery silently skips the plugin, so CI must assert `BUILD_SCITOKENS` when coverage is expected.
- Compile definitions and include variable names must match the `SciTokensCpp` package module.
- Runtime config behavior differs depending on `HAVE_SCITOKEN_CONFIG_SET_STR`.

## Test Signals

Build tests should cover disabled, optional-missing, forced-missing, and found SciTokens configurations. Runtime packaging should verify the module installs under `${CMAKE_INSTALL_LIBDIR}` and loads as `libXrdAccSciTokens`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensAccess.cc -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensAccess.cc

## Purpose

`XrdSciTokensAccess.cc` implements the SciTokens-based `XrdAccAuthorize` plugin. It validates JWT/SciToken credentials, generates XRootD access rules from token scopes, maps token claims/groups to request names and security-entity attributes, supports chained authorization, exposes a helper validation API, periodically reconfigures issuer/audience policy, and emits optional token monitoring records.

## Important APIs, Types, And Functions

- Local enums `LogMask`, `IssuerAuthz`, and `AuthzBehavior` define logging, issuer authorization strategies, and behavior for missing/invalid token authorization.
- Helpers include `monotonic_time()`, `AddPriv()`, `OpToName()`, `AccessRuleStr()`, `IsSafeUsername()`, `MakeCanonical()`, and `ParseCanonicalPaths()`.
- `MapRule` matches subject, username, path prefix, and group to a result username.
- `IssuerConfig` holds parsed issuer policy: issuer name/url, base/restricted paths, subject mapping behavior, authorization strategy, default user, username/groups claims, and map rules.
- `OverrideINIReader` customizes INI parsing so later duplicate keys override earlier values.
- `XrdAccRules` stores cached parsed token result: expiry, username, token subject, issuer, map rules, groups, authz strategy, and access rules. `apply()` checks operation/path authorization.
- `XrdAccSciTokens` inherits `XrdAccAuthorize`, `XrdSciTokensHelper`, and `XrdSciTokensMon`.
- Public plugin methods include `Access()`, `IssuerList()`, `Validate()`, `Audit()`, `Test()`, and `GetConfigFile()`.
- Private methods include `OnMissing()`, `GenerateAcls()`, `Config()`, `ParseMapfile()`, `Reconfig()`, and `Check()`.
- C plugin exports are `XrdAccAuthorizeObjAdd`, `XrdAccAuthorizeObject`, and `XrdAccAuthorizeObject2`; global symbols `accSciTokens` and `SciTokensHelper` expose singleton/plugin helper state.

## Control Flow

Plugin construction initializes locks, logging, and configuration. `Config()` reads `XRDCONFIGFN` to gather `scitokens.trace`, wires TLS CA settings from the xrootd TLS context when possible, configures key-cache location from `XDG_CACHE_HOME` or `XRDADMINPATH`, then calls `Reconfig()`.

`Access()` extracts a request token from `env["authz"]`, stripping `Bearer%20`, or from ZTN session credentials. Missing token handling delegates to `OnMissing()`. Present tokens are looked up in a 60-second cache keyed by token string; expired or absent entries call `GenerateAcls()`. A successful parsed token becomes an `XrdAccRules` object cached until token expiration or the plugin cap.

Authorization then builds a temporary `XrdSecEntity` carrying issuer in `vorg`, groups in `grps`, and selected attributes. Scope success immediately grants the operation via `AddPriv()`. Mapping or group success can instead chain to the next authorization plugin. When scope or mapping supplies a username, the code writes `request.name` to both the original and temporary entity attribute APIs. It also writes `token.subject` to the original entity. Successful scoped I/O operations can emit token monitoring through `Mon_Report()`.

`GenerateAcls()` first rejects strings that do not look like JWTs. It deserializes with configured valid issuers, checks expiration, creates a SciTokens enforcer with configured audiences, generates ACLs, retrieves issuer config, parses groups/subject/username claim, validates username safety, expands map rules over base paths, applies restricted-path clipping, and maps SciTokens authz strings such as `read`, `create`, `modify`, `write`, `storage.stage`, and `storage.poll` to XRootD operations.

`Reconfig()` parses `/etc/xrootd/scitokens.cfg` by default or `config=<path>` from plugin parameters. It reads global audiences, `audience_json`, `onmissing`, issuer sections, optional JSON map files, base/restricted paths, username/group claims, default user, and authorization strategies, then swaps the config under a write lock. `Check()` opportunistically cleans expired token cache entries and re-runs `Reconfig()` every 60 seconds.

## State And Persistence

The plugin is a process singleton. Runtime state includes config read/write lock, audience and issuer vectors plus C-string arrays passed to SciTokens, parsed-token cache `m_map`, mutexes, chain pointer, parameters, next cleanup time, authz behavior, and config filename. Token cache is in memory only. The SciTokens key cache may persist under `XDG_CACHE_HOME` or `${XRDADMINPATH}/.cache` depending on library support.

## Dependencies And Integration Points

The file depends on XRootD authorization interfaces, `XrdOucEnv`, `XrdOucGatherConf`, `XrdSecEntity`/attributes, TLS context, `INIReader`, `picojson`, `scitokens-cpp`, and monitoring helper classes. It integrates with HTTP via `http.header2cgi Authorization authz`, with chained authorization plugins, with ZTN credentials, with `XrdSecEntityAttr` for request attributes, and with external issuer JWKS discovery through SciTokens.

## Risks And Edge Cases

- `Access()` assumes `Entity` is non-null later even though token extraction checks it conditionally; callers must supply an entity.
- The expression checking ZTN NUL termination indexes `Entity->creds[Entity->credslen]`, which is one byte past a buffer of length `credslen` unless the contract includes an extra NUL.
- Token cache keys are raw token strings and grow until cleanup; high token cardinality can increase memory between checks.
- `IssuerList()` and `Validate()` take config locks but expose C-string arrays derived from vectors; config swaps must preserve array validity during library calls.
- `new_secentity.eaAPI` relies on default construction; cleanup frees only selected C strings, not all copied entity fields because most are borrowed.
- Mapfile parsing accepts `"ignore"` only when it is a string value because non-string handling ignores keys outside a fixed set; boolean ignore may not work.
- `onmissing=allow` is intentionally permissive and should be treated as high-risk config.
- Username claim safety is checked, but default users and mapfile results are not validated by `IsSafeUsername()`.

## Test Signals

Unit tests should cover canonical path normalization, restricted-path clipping, authz string to operation mapping, safe username rejection, JSON mapfile parsing, duplicate INI override behavior, audience and audience_json parsing, authorization strategy parsing, and `onmissing` behavior. Integration tests should run with valid/expired/wrong-issuer/wrong-audience/no-audience tokens; scope-only, group-only, mapping-only, and chained authorization modes; ZTN token credentials; reconfiguration after file changes; and token monitoring output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensAccess.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensHelper.hh -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensHelper.hh

## Purpose

`XrdSciTokensHelper.hh` declares a helper API exported by the SciTokens authorization plugin so other components can list configured issuers and validate tokens without performing file-operation authorization.

## Important APIs, Types, And Functions

- `struct ValidIssuer` contains `issuer_name` and `issuer_url`.
- `using Issuers = std::vector<ValidIssuer>` is the issuer list return type.
- Pure virtual `IssuerList()` returns configured valid issuers.
- Pure virtual `Validate(token, emsg, expT, entP)` validates token signature/issuer/audience and optionally returns expiration and fills an `XrdSecEntity` with identifying claims.
- Global symbol `SciTokensHelper` is described as the way to find an initialized implementation.

## Control Flow

Callers obtain the plugin-provided instance after the authorization plugin is loaded, then use the virtual API. The implementation in `XrdSciTokensAccess.cc` delegates to `scitoken_deserialize()` and issuer config state.

## State And Persistence

The interface owns no state. Implementations expose plugin runtime state.

## Dependencies And Integration Points

It depends on STL strings/vectors and forward-declares `XrdSecEntity`. It is implemented by `XrdAccSciTokens` and can be used by other XRootD modules needing token validation.

## Risks And Edge Cases

- The helper exists only after plugin load and successful initialization; callers must handle a null global.
- Documentation says issuer list changes only at initialization, but the implementation can reconfigure periodically, so callers should not assume permanent immutability.

## Test Signals

Tests should load the plugin, confirm `SciTokensHelper` is non-null, validate known good/bad tokens, check expiration return, and compare issuer list before and after reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.cc -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.cc

## Purpose

`XrdSciTokensMon.cc` formats and emits security-monitoring token records for successful SciTokens-authenticated I/O.

## Important APIs, Types, And Functions

- `XrdSciTokensMon::Mon_Report(Entity, subject, username)` formats `s`, `n`, `o`, `r`, and `g` fields into a buffer and sends it to `Entity.secMon->Report(XrdSecMonitor::TokenInfo, buff)`.

## Control Flow

The method is called from `XrdAccSciTokens::Access()` after scoped authorization grants an I/O operation and `Mon_isIO()` indicates the operation should be monitored. It no-ops if `Entity.secMon` is null.

## State And Persistence

There is no local state. Monitoring records go to the configured `XrdSecMonitor` sink and are not persisted here.

## Dependencies And Integration Points

It depends on `XrdSciTokensMon.hh`, `XrdSecEntity`, and `XrdSecMonitor`. It integrates with the security monitoring channel and SciTokens authorization.

## Risks And Edge Cases

- Formatting uses a fixed 2048-byte stack buffer and truncates groups to 1024 characters.
- Field values are inserted without escaping in query-string-like format, so special characters in subject, username, issuer, role, or groups may affect downstream parsing.

## Test Signals

Tests should use a fake monitor to verify emission on configured entities, no-op without `secMon`, truncation behavior, and parsing of records containing empty issuer/role/group values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.hh -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.hh

## Purpose

`XrdSciTokensMon.hh` declares the small monitoring mixin used by the SciTokens authorization plugin.

## Important APIs, Types, And Functions

- `Mon_isIO(oper)` returns true for read, update, create, and exclusive create operations.
- `Mon_Report(Entity, subject, username)` emits token monitoring data.

## Control Flow

`XrdAccSciTokens` calls `Mon_isIO()` after successful scope-based authorization and calls `Mon_Report()` only for monitored I/O operations.

## State And Persistence

The class owns no state.

## Dependencies And Integration Points

It includes `XrdAcc/XrdAccAuthorize.hh` for `Access_Operation` and forward-uses `XrdSecEntity` through the implementation. It is a base class of `XrdAccSciTokens`.

## Risks And Edge Cases

- The monitored operation set is hard-coded; mkdir, rename, delete, stage, and poll are not reported by this helper.
- The header typo in its comment/name banner has no runtime effect.

## Test Signals

Unit tests should assert `Mon_isIO()` truth table for every `Access_Operation` and verify the implementation is called only for those operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/configs/scitokens.cfg -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/configs/scitokens.cfg

## Purpose

This is a sample SciTokens plugin configuration showing global audience syntax and two issuer sections.

## Important APIs, Types, And Functions

- Commented `[Global]` examples show `audience` and `audience_json`.
- `[Issuer OSG-Connect]` sets issuer `https://scitokens.org/osg-connect`, `base_path=/stash`, and `map_subject=True`.
- `[Issuer CMS]` sets issuer `https://scitokens.org/cms`, `base_path=/user/cms`, and `map_subject=False`.

## Control Flow

When used as the plugin config, `Reconfig()` parses issuer sections and maps token scopes under each base path. The OSG issuer maps token subject to local username; CMS does not.

## State And Persistence

It is static configuration text. Runtime state is created by `XrdSciTokensAccess.cc` when parsed.

## Dependencies And Integration Points

It follows the INI syntax consumed by `OverrideINIReader` and the keys recognized by `XrdAccSciTokens::Reconfig()`.

## Risks And Edge Cases

- The global audience examples are commented, so tokens with an `aud` claim may be rejected depending on SciTokens library semantics when no audience is configured.
- `map_subject=True` assumes subjects are safe local usernames; newer code validates explicit username claims, but subject/default mapping policy still needs operator care.

## Test Signals

Config tests should parse this file and verify both issuers appear, base paths canonicalize, and sample tokens for each issuer map according to `map_subject`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/configs/scitokens.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/override.conf -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/override.conf

## Purpose

This systemd drop-in injects an environment variable for the xrootd HTTP test service.

## Important APIs, Types, And Functions

- `[Service] Environment=REQUESTS_CA_BUNDLE=/localhost.crt` tells Python/request clients or related tooling to trust the self-signed localhost certificate during tests.

## Control Flow

`test_inside_docker.sh` copies this file into `/etc/systemd/system/xrootd@http.service.d/override.conf`, reloads systemd, and restarts the service.

## State And Persistence

The file persists as a systemd override inside the test container until removed.

## Dependencies And Integration Points

It integrates with the test-generated `localhost.crt`, systemd service environment, and SciTokens HTTPS/JWKS discovery.

## Risks And Edge Cases

- It assumes the certificate exists at `/localhost.crt`; the setup script copies certs under `/etc/ssl` but also generates in the working directory, so path assumptions matter.
- This is test-only and should not be installed in production.

## Test Signals

Test signal is successful HTTPS access to localhost issuer metadata without CA verification failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/override.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-aud.cfg -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-aud.cfg

## Purpose

This test SciTokens config requires a single accepted audience for the localhost issuer.

## Important APIs, Types, And Functions

- `[Global] audience = testing.com`
- `[Issuer localhost] issuer = https://localhost`
- `base_path = /`

## Control Flow

The integration test installs this config, restarts xrootd, then expects tokens with `aud=testing.com` to succeed and tokens without an audience to fail.

## State And Persistence

It is copied to `/etc/xrootd/scitokens.cfg` during tests and parsed into plugin runtime state.

## Dependencies And Integration Points

Consumed by `XrdAccSciTokens::Reconfig()` and SciTokens enforcer audience checking.

## Risks And Edge Cases

- Issuer URL must match the token issuer exactly, including scheme and host.
- The base path `/` grants scope-derived paths across the exported namespace for matching token scopes.

## Test Signals

Expected signal is pass for a valid localhost token with `aud=testing.com`, fail for no-audience and wrong-audience variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-aud.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-multi-aud.cfg -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-multi-aud.cfg

## Purpose

This test config accepts two audience values for the localhost issuer.

## Important APIs, Types, And Functions

- `[Global] audience = testing.com, https://another.com`
- `[Issuer localhost] issuer = https://localhost`
- `base_path = /`

## Control Flow

The integration test copies this config, restarts xrootd, then verifies either configured audience succeeds while no audience and wrong audience fail.

## State And Persistence

It is static test config parsed into runtime audience vector state.

## Dependencies And Integration Points

It exercises comma/space splitting in `XrdAccSciTokens::Reconfig()` and SciTokens enforcer audience validation.

## Risks And Edge Cases

- Audience parsing splits on comma and space, so values containing spaces require `audience_json` instead.
- The URL audience includes `https://`; exact token claim matching is required.

## Test Signals

Expected test signals are successful reads for `testing.com` and `https://another.com`, and failures for absent or `wrong.com` audiences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-multi-aud.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-no-aud.cfg -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-no-aud.cfg

## Purpose

This test config defines a localhost issuer without configuring a global audience.

## Important APIs, Types, And Functions

- `[Issuer localhost] issuer = https://localhost`
- `base_path = /`

## Control Flow

The integration test expects a token without `aud` to succeed and a token carrying `aud=testing.com` to fail when this config is installed.

## State And Persistence

It is copied to `/etc/xrootd/scitokens.cfg` during tests.

## Dependencies And Integration Points

It exercises `XrdAccSciTokens::Reconfig()` behavior when `m_audiences_array` contains only the null terminator.

## Risks And Edge Cases

- Audience-less acceptance depends on SciTokens library behavior with an empty audience list.
- This config is intentionally minimal and broadly maps scopes under `/`.

## Test Signals

Expected signal is successful read with no `aud` claim and failure when an audience claim is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/scitokens-no-aud.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/xrootd-http.cfg -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/xrootd-http.cfg

## Purpose

This test xrootd configuration starts a standalone data server exporting `/tmp`, enables HTTP on port 8080, and loads the SciTokens authorization plugin.

## Important APIs, Types, And Functions

- `all.export /tmp`, `all.adminpath /var/spool/xrootd`, and `all.pidpath /run/xrootd` configure the standalone server.
- `xrd.protocol XrdHttp:8080 /usr/lib64/libXrdHttp-4.so` loads HTTP.
- `http.header2cgi Authorization authz` maps the HTTP `Authorization` header into request CGI key `authz`.
- `ofs.authorize` enables authorization.
- `ofs.authlib libXrdAccSciTokens.so` loads the SciTokens plugin.
- `xrd.trace all` enables broad tracing for the test.

## Control Flow

`test_inside_docker.sh` installs this as `/etc/xrootd/xrootd-http.cfg`, starts `xrootd@http.service`, then HTTP requests with bearer tokens are checked by the SciTokens plugin before reading `/tmp/random.txt`.

## State And Persistence

The config produces runtime server state under admin/pid paths and serves files from `/tmp`.

## Dependencies And Integration Points

It depends on the HTTP plugin path used by the CentOS test packages, SciTokens authlib installation, systemd socket/service environment, and header-to-CGI integration expected by `XrdSciTokensAccess.cc`.

## Risks And Edge Cases

- Hard-coded `/usr/lib64/libXrdHttp-4.so` is distribution/version-specific.
- `xrd.trace all` is noisy and test-oriented.
- Exporting `/tmp` is appropriate for tests but not a production policy.

## Test Signals

Passing signal is an HTTP GET to `/tmp/random.txt` with a valid token returning the generated file contents while invalid audience cases fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/config/xrootd-http.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/create-pubkey.py -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/create-pubkey.py

## Purpose

`create-pubkey.py` is a Python 2 integration-test helper that creates a SciToken signed by `private.pem`, optionally adds an audience claim, sends it to the local xrootd HTTP endpoint, and prints the fetched file contents.

## Important APIs, Types, And Functions

- Uses `argparse` for optional `--aud` and required JWKS public-key path.
- Loads `private.pem` with `cryptography` serialization.
- Reads the JWKS file to extract the first key's `kid`.
- Creates `scitokens.SciToken(key=private_key, key_id=key_id)`, sets `scope = "read:/"`, optionally sets `aud`, serializes with issuer `https://localhost`, and sends `Authorization: Bearer <token>` to `http://localhost:8080/tmp/random.txt` via `urllib2`.

## Control Flow

The script is invoked by `test_inside_docker.sh` after Apache serves JWKS and xrootd serves `/tmp`. Its stdout is compared with a generated random file value. A nonzero exception path is used by shell `if python ...; then exit 1` checks to assert expected failures.

## State And Persistence

It reads `private.pem` and the JWKS file, makes a network request, and writes only stdout/stderr.

## Dependencies And Integration Points

It depends on Python 2 modules `urllib2`, `scitokens`, `cryptography`, and `json`. It integrates with generated test keys, the local issuer metadata served by Apache, and xrootd HTTP authorization.

## Risks And Edge Cases

- Python 2 dependency is obsolete and environment-sensitive.
- It assumes `private.pem` is in the current working directory.
- It always requests `read:/` and one fixed URL, so it does not exercise write or path-restricted scopes.
- It extracts only the first JWKS key ID.

## Test Signals

Successful execution prints the contents of `/tmp/random.txt`. Expected failure cases include wrong/missing audience under audience-requiring configs and audience-present tokens under no-audience config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/create-pubkey.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/openssl-selfsigned.conf -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/openssl-selfsigned.conf

## Purpose

This OpenSSL config creates a self-signed localhost certificate for the SciTokens integration test HTTPS issuer.

## Important APIs, Types, And Functions

- `[req]` sets 2048-bit default key, `localhost.key`, distinguished-name section, request extensions, and x509 extensions.
- `[localhost]` supplies subject defaults for US/Nebraska/Lincoln/SciTokens/Development/commonName localhost.
- `[req_ext]` and `[v3_ca]` use `subjectAltName = @alt_names`.
- `[alt_names]` contains `DNS.1 = localhost` and `DNS.2 = 127.0.0.1`.

## Control Flow

`test_inside_docker.sh` passes this file to `openssl req -x509 -nodes -days 365 -newkey rsa:2048 ...` to generate `localhost.key` and `localhost.crt`.

## State And Persistence

The config itself is static. Generated key/cert files persist in the test container and are copied into `/etc/ssl`.

## Dependencies And Integration Points

It integrates with Apache TLS config, SciTokens issuer discovery over HTTPS, and the system trust bundle update in the test script.

## Risks And Edge Cases

- `DNS.2 = 127.0.0.1` uses a DNS SAN for an IP literal rather than an IP SAN, which some TLS stacks may reject.
- Certificate values are test-only and not suitable for production.

## Test Signals

OpenSSL generation should succeed, Apache should restart with the certificate, and SciTokens/JWKS discovery should validate against the updated trust bundle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/openssl-selfsigned.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/setup_tests.sh -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/setup_tests.sh

## Purpose

`setup_tests.sh` starts a privileged CentOS 7 Docker container and runs the SciTokens integration test script inside it.

## Important APIs, Types, And Functions

- Checks `OS_VERSION=7`.
- Runs `docker run --privileged --detach --tty --interactive --env container=docker --volume /sys/fs/cgroup:/sys/fs/cgroup --volume $(pwd):/xrootd-scitokens:rw centos:centos${OS_VERSION} /usr/sbin/init`.
- Finds the container ID from `docker ps | grep centos | awk '{print $1}'`.
- Executes `/xrootd-scitokens/test/test_inside_docker.sh ${OS_VERSION}` inside the container.

## Control Flow

The script is an outer harness. It starts systemd-capable Docker, prints logs, runs the inner setup/test script, and lists containers. Stop/remove commands are commented out.

## State And Persistence

It creates a privileged Docker container and bind-mounts the repository read-write. Because cleanup is commented, containers may remain after the run.

## Dependencies And Integration Points

It depends on Docker, CentOS 7 images, systemd-in-container support, and the inner test script. It assumes the current directory is the xrootd-scitokens source root expected by paths in the container.

## Risks And Edge Cases

- Privileged Docker with `/sys/fs/cgroup` mount has high host impact and may not work in restricted CI.
- Container selection via `grep centos` can pick the wrong container.
- No cleanup by default can leak containers and disk.
- Only `OS_VERSION=7` is supported; other values silently do nothing.

## Test Signals

Successful run prints the inner script completion marker and exits zero. Failure signals include Docker startup failure, package install failure, RPM build failure, service restart failure, or token request mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/setup_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/test_inside_docker.sh -->
# sources/distributed-fs/xrootd/src/XrdSciTokens/test/test_inside_docker.sh

## Purpose

`test_inside_docker.sh` provisions a CentOS container, builds and installs the xrootd-scitokens RPM, configures a local HTTPS issuer and xrootd HTTP server, then validates SciTokens audience behavior with real HTTP reads.

## Important APIs, Types, And Functions

- Installs EPEL, build tools, OSG repositories, `xrootd-server-devel`, `scitokens-cpp-devel`, `httpd`, `mod_ssl`, `xrootd-server`, and `python2-scitokens`.
- Builds RPM from `rpm/xrootd-scitokens.spec` using `git archive` and `rpmbuild`.
- Generates SciTokens keys with `scitokens-admin-create-key`, serves JWKS and OIDC discovery from Apache, and creates a self-signed certificate with `openssl-selfsigned.conf`.
- Installs xrootd and SciTokens configs, restarts `xrootd@http.service`, writes random data to `/tmp/random.txt`, and invokes `create-pubkey.py`.
- Exercises no-audience, single-audience, multi-audience, missing-audience, and wrong-audience scenarios.

## Control Flow

The script first prepares package repositories and build dependencies, builds the source RPM/binary RPM, installs it, configures Apache TLS/JWKS discovery, configures xrootd HTTP authorization, starts services, and then runs a sequence of token request assertions. For success cases, Python output must exactly equal the generated random string. For failure cases, the Python command must fail or the script exits with failure.

## State And Persistence

It mutates the container extensively: yum cache/repos/packages, `/tmp/rpmbuild`, `/etc/httpd`, `/var/www/html`, `/etc/ssl`, `/etc/xrootd`, systemd drop-ins, services, generated keys/certs, and `/tmp/random.txt`.

## Dependencies And Integration Points

It depends on external RPM repositories, network access, systemd, Apache, OpenSSL, SciTokens admin tooling, Python 2 client libraries, xrootd packages, and the local repository layout. It integrates the SciTokens plugin through `ofs.authlib` and HTTP authorization header mapping.

## Risks And Edge Cases

- Network and repository availability dominate reliability.
- `cat /dev/urandom | ... | head` can trigger pipefail-style issues if shell options change, though current script uses `-xe` not `pipefail`.
- The script assumes x86_64 RPM output and CentOS/OSG package names.
- It modifies global CA bundle and service configs inside the container.
- Audience expectations depend on SciTokens library semantics and exact issuer URL handling.

## Test Signals

The key test signal is exact content match for valid token cases and command failure for invalid audience cases. Additional signals are successful RPM build/install, Apache restart, xrootd restart, JWKS discovery availability, and service logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSciTokens/test/test_inside_docker.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSec/CMakeLists.txt

## Purpose

This CMake fragment builds XRootD security support into `XrdUtils` and creates the loadable security plugin modules.

## Important APIs, Types, And Functions

- Defines module target names `XrdSec-${PLUGIN_VERSION}` and `XrdSecProt-${PLUGIN_VERSION}`.
- Adds entity, attribute, extra, load-security, and monitor sources to `XrdUtils`.
- Builds `${XrdSec}` module from client/server protocol manager, interfaces, trace, entity pin, and transport-layer sources.
- Builds `${XrdSecProt}` module from protector sources.
- Links `${XrdSec}` to `XrdUtils`; links `${XrdSecProt}` to `XrdUtils` and `OpenSSL::Crypto`.
- Adds both modules to the `plugins` dependency target and installs them.

## Control Flow

CMake compiles base entity support into the utility library and plugin-facing security protocol machinery into modules. Install rules place module shared libraries in the configured library directory.

## State And Persistence

Build outputs are the two plugin modules plus `XrdUtils` object content. No runtime state is in the CMake file.

## Dependencies And Integration Points

It depends on parent targets `XrdUtils`, `plugins`, `OpenSSL::Crypto`, and `${PLUGIN_VERSION}`. It is foundational for security protocol loading and for other modules such as SciTokens that include `XrdSecEntity`.

## Risks And Edge Cases

- Splitting entity classes into `XrdUtils` means ABI changes affect many consumers.
- Module names are versioned; runtime config must reference the correct installed names or symlinks.
- Missing source additions here can cause runtime plugin symbols to be absent.

## Test Signals

Build tests should verify both modules are produced and installed. Runtime tests should load security protocols and confirm `XrdSecGetProtocol` resolves from the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecAttr.hh

## Purpose

`XrdSecAttr.hh` defines the base class for typed extension objects attached to an `XrdSecEntity`.

## Important APIs, Types, And Functions

- `XrdSecAttr(const void *dSig)` stores a unique signature pointer for the derived attribute type.
- Virtual `Delete()` defaults to `delete this` and can be overridden for custom deletion.
- Destructor is protected, forcing deletion through `Delete()`.
- `XrdSecEntityAttr` is a friend so it can inspect `Signature`.

## Control Flow

Derived classes choose a stable unique signature, instantiate attributes, and add them through `XrdSecEntityAttr::Add(XrdSecAttr&)`. Retrieval uses the same signature pointer and downcasts by convention.

## State And Persistence

Each attribute stores only its signature in the base. Derived objects carry their own state and are deleted when the entity extra state resets or is destroyed.

## Dependencies And Integration Points

It forward-declares `XrdSecEntity` and integrates with `XrdSecEntityAttr` and `XrdSecEntityXtra`.

## Risks And Edge Cases

- Signature uniqueness is a convention, not enforced globally.
- Attribute objects are stored by pointer; callers must not stack-allocate attributes whose lifetime is shorter than the entity.
- Custom `Delete()` implementations must be correct to avoid leaks.

## Test Signals

Tests should add a custom derived attribute, reject duplicate signatures, retrieve it by signature, and verify deletion during entity reset/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecClient.cc -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecClient.cc

## Purpose

`XrdSecClient.cc` exposes the client-side security protocol selection entrypoint and a no-authentication fallback protocol.

## Important APIs, Types, And Functions

- Local `XrdSecProtNone` implements `XrdSecProtocol` with no-op `Authenticate()`, empty credentials from `getCredentials()`, and no deletion because it is static.
- Exported `extern "C" XrdSecGetProtocol(hostname, endPoint, parms, einfo)` returns `ProtNone` when the server requests no security, otherwise asks static `XrdSecPManager` to load/select a supported protocol.
- Static `DebugON` is driven by `XrdSecDEBUG`.
- Static `XrdSecPManager` is constructed with proxy flags from `XrdSecPROXY` and `XrdSecPROXYCREDS`.

## Control Flow

Client code calls `XrdSecGetProtocol()` with server parameters. If `parms` is empty, the static no-auth protocol is returned. Otherwise the protocol manager locates a matching security plugin. Failure sets `ENOPROTOOPT` in `einfo` or logs to stderr.

## State And Persistence

The fallback protocol and protocol manager are static process-lifetime objects. Debug/proxy behavior is captured on first function call from environment variables.

## Dependencies And Integration Points

It depends on `XrdSecPManager`, `XrdSecInterface`, `XrdNetAddrInfo`, and `XrdOucErrInfo`. It is loaded from the client-facing security module and is influenced by PSS setting `XrdSecPROXY=1`.

## Risks And Edge Cases

- Environment variables are read once due to static initialization inside the function.
- `XrdSecProtNone::Delete()` intentionally does nothing; consumers must not expect ownership.
- Debug output can include raw security tokens in stderr when enabled.

## Test Signals

Tests should call with empty parameters and expect the no-auth protocol, call with unsupported parameters and expect `ENOPROTOOPT`, and verify proxy/debug environment behavior before first call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.cc -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.cc

## Purpose

`XrdSecEntity.cc` implements construction, reset, and diagnostic display for the connection security entity object.

## Important APIs, Types, And Functions

- Constructor allocates `eaAPI` as a new `XrdSecEntityXtra` and calls `Init()`.
- Destructor deletes `eaAPI->entXtra`, which owns key-value and object attributes.
- `Init(spV)` zeroes protocol/extractor arrays, optionally copies the protocol name, and resets all public fields to null/zero.
- `Reset(spV)` reinitializes fields and clears extra attributes.
- `Display(mDest)` logs protocol, identity fields, credential length, unique ID, uid/gid, and all key-value attributes through a local `AttrCB`.

## Control Flow

Security protocol implementations fill public fields after construction. `Reset()` is used to reuse an entity object, clearing attribute state as well as scalar/pointer fields. `Display()` is diagnostic and iterates attributes under the attribute API.

## State And Persistence

The entity stores many public raw pointers but does not free most of them in `Reset()` or destructor; the security protocol object remains responsible for public member ownership. Extra attributes are owned by `XrdSecEntityXtra` and are deleted on reset/destruction.

## Dependencies And Integration Points

It depends on `XrdSecEntityXtra`, `XrdSecEntityAttr`, and `XrdSysError`. It is used across authentication, authorization, monitoring, PSS URL identity, and SciTokens attribute decoration.

## Risks And Edge Cases

- Public pointer ownership is external and easy to misuse; resetting without freeing protocol-owned fields can leak if the owner does not handle them.
- Destructor deletes `eaAPI->entXtra`; because `XrdSecEntityXtra` inherits `XrdSecEntityAttr`, this relies on the self-referential API layout.
- `Display()` logs sensitive fields such as names, groups, credentials length, and attributes; debug use should be controlled.

## Test Signals

Tests should construct with protocol names, reset with/without protocol, add attributes then reset, verify display includes attributes, and run leak checks with derived attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.hh -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.hh

## Purpose

`XrdSecEntity.hh` declares the core identity object returned by XRootD security authentication and consumed by authorization, monitoring, and protocol layers.

## Important APIs, Types, And Functions

- Public identity fields include auth protocol `prot`, extractor `prox`, `name`, `host`, `vorg`, `role`, `grps`, `caps`, `endorsements`, `moninfo`, raw `creds`, `credslen`, `ueid`, `addrInfo`, `tident`, `pident`, uid/gid, and security monitor pointer.
- `eaAPI` exposes mutable extra attributes through `XrdSecEntityAttr`.
- `Display()`, `Reset()`, constructor, and destructor manage diagnostics and initialization.
- Aliases `XrdSecClientName` and `XrdSecServerName` map to `XrdSecEntity`.

## Control Flow

Authentication protocols populate this object for a connection. Authorization plugins generally receive it as const but can still mutate logical request attributes through `eaAPI`. The object persists for the connection lifetime.

## State And Persistence

State is in memory and connection-scoped. The destructor intentionally does not delete public member pointers; protocol owners must free them. Extra attributes are owned by the entity implementation.

## Dependencies And Integration Points

It forward-declares network address, attributes, monitor, and logging classes. It is included by SciTokens, PSS URL code, security protocol implementations, and monitoring.

## Risks And Edge Cases

- Raw public fields make ownership and const-correctness subtle.
- `host` may be a DNS name or IP based on DNR settings; code needing real hostnames should use `addrInfo`.
- Columnar tuple semantics for `vorg`, `role`, and `grps` must be preserved by producers.

## Test Signals

Tests should verify initialization defaults, protocol truncation behavior, attribute API availability, reset semantics, and integration with authorization plugins that write request attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.cc -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.cc

## Purpose

`XrdSecEntityAttr.cc` implements thread-safe storage and lookup of typed and key-value attributes attached to an `XrdSecEntity`.

## Important APIs, Types, And Functions

- `Add(XrdSecAttr&)` adds a typed attribute object if no existing object has the same signature.
- `Add(key, val, replace)` adds or optionally replaces a string key-value attribute.
- `Get(sigkey)` returns a typed attribute by signature.
- `Get(key, val)` returns a key-value attribute.
- `Keys()` returns all key-value keys.
- `List(attrCB)` iterates key-values through callback actions `Next`, `Stop`, and `Delete`.

## Control Flow

Every method locks `entXtra->xMutex`. Typed attributes are stored in a vector and compared by signature. Key-values are stored in a map. `List()` calls the callback while holding the mutex, records requested deletions, sends an end marker if iteration was not stopped, and then erases requested keys.

## State And Persistence

The implementation mutates `XrdSecEntityXtra::attrVec` and `attrMap`, both scoped to one entity. No persistent storage exists.

## Dependencies And Integration Points

It depends on `XrdSecAttr`, `XrdSecEntityXtra`, and `XrdSysMutexHelper`. SciTokens uses the key-value API for `request.name` and `token.subject`.

## Risks And Edge Cases

- Callback code must not call `Add()` or `Get()` during `List()` because the mutex is held and the header warns this deadlocks.
- `List()` stores `c_str()` pointers for later deletion; because the map is not modified until after iteration, this is safe but delicate.
- Typed attributes are non-owning until `XrdSecEntityXtra::Reset()` deletes them; callers must allocate accordingly.

## Test Signals

Tests should cover duplicate typed attribute rejection, key add/replace/no-replace, missing gets, key enumeration, callback stop/delete behavior, and concurrent attribute access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.hh

## Purpose

`XrdSecEntityAttr.hh` declares the mutable extra-attribute API for `XrdSecEntity` and the callback interface for listing key-value attributes.

## Important APIs, Types, And Functions

- `XrdSecEntityAttr` exposes typed-object `Add()`/`Get()`, key-value `Add()`/`Get()`, `Keys()`, and `List()`.
- `XrdSecEntityAttrCB` defines callback actions `Delete`, `Stop`, and `Next`, and pure virtual `Attr(key, val)`.
- Private `entXtra` points to the implementation storage object.

## Control Flow

Authorization and security plugins use this API to attach extra logical identity data even when they receive a const `XrdSecEntity*`. Listing is callback-driven and may request deletion.

## State And Persistence

The API object references entity-owned `XrdSecEntityXtra` state. Attribute state is connection-scoped.

## Dependencies And Integration Points

It uses STL strings/vectors and forward-declares `XrdSecAttr` and `XrdSecEntityXtra`. It is embedded in `XrdSecEntity` as `eaAPI`.

## Risks And Edge Cases

- The callback contract forbids reentrant attribute API calls to avoid deadlock.
- The API is mutable through a pointer on otherwise const entities, so authorization code must coordinate naming and replacement semantics.
- Key names are unconstrained strings; collisions between plugins are possible.

## Test Signals

Compile tests should exercise typed and string attribute APIs from const-entity contexts. Runtime tests should verify callback end marker behavior and replacement rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityPin.hh -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityPin.hh

## Purpose

`XrdSecEntityPin.hh` declares the post-authentication entity processing plugin interface.

## Important APIs, Types, And Functions

- Pure virtual `Process(XrdSecEntity &entity, XrdOucErrInfo &einfo)` inspects or decorates an authenticated entity and can fail authentication by returning false with error information.
- Comments describe stacking behavior and loading through `XrdOucPinObject<XrdSecEntityPin>` with file-level object `SecEntityPin`.

## Control Flow

After a security protocol authenticates an entity, configured post-processing plugins can be called to add attributes or reject the entity. Stacked plugins should generally be called and their result returned unless the current plugin rejects.

## State And Persistence

The interface owns no state. Implementations may attach state to `XrdSecEntity` attributes or internal plugin objects.

## Dependencies And Integration Points

It forward-declares `XrdOucErrInfo` and `XrdSecEntity` and integrates with XRootD plugin loading/versioning via `XrdOucPinObject` and `XrdVERSIONINFO`.

## Risks And Edge Cases

- A failing plugin causes the framework to try another authentication protocol if available, so rejection semantics affect protocol negotiation.
- Stacked plugin ordering and error propagation must be designed carefully.

## Test Signals

Plugin tests should load a concrete entity pin, verify successful decoration, verify failure messages in `XrdOucErrInfo`, and cover stacked plugin pass-through behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityPin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.cc -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.cc

## Purpose

`XrdSecEntityXtra.cc` implements cleanup for the entity extra-attribute storage.

## Important APIs, Types, And Functions

- `XrdSecEntityXtra::Reset()` locks the extra-state mutex, clears the key-value map, calls `Delete()` on every typed attribute object, and clears the vector.

## Control Flow

`Reset()` is called by `XrdSecEntity::Reset()` and by `XrdSecEntityXtra` destructor. It first discards string attributes, then deletes object attributes through their virtual deletion hook.

## State And Persistence

It clears entity-scoped `attrMap` and `attrVec`. No persistence exists.

## Dependencies And Integration Points

It depends on `XrdSecAttr` and `XrdSecEntityXtra.hh`. It is the cleanup path for all users of `XrdSecEntityAttr`.

## Risks And Edge Cases

- `Delete()` runs while holding `xMutex`; custom attribute deletion code must not call back into the same entity attribute API.
- Attribute object ownership transfers to the entity after successful `Add(XrdSecAttr&)`.

## Test Signals

Tests should add typed attributes with observable `Delete()`, call reset/destructor, and assert each object is deleted once and maps/vectors are empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.hh -->
# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.hh

## Purpose

`XrdSecEntityXtra.hh` defines the concrete storage backing the `XrdSecEntityAttr` API.

## Important APIs, Types, And Functions

- `XrdSecEntityXtra` inherits `XrdSecEntityAttr` and passes `this` to the base constructor.
- Public fields include mutex `xMutex`, typed attribute vector `attrVec`, and string attribute map `attrMap`.
- `Reset()` clears all stored attributes.
- Destructor calls `Reset()`.

## Control Flow

`XrdSecEntity` allocates `XrdSecEntityXtra` and exposes it through the base API pointer `eaAPI`. API methods lock and mutate this concrete storage.

## State And Persistence

State is per entity and in memory only.

## Dependencies And Integration Points

It includes maps/vectors, `XrdSecEntityAttr.hh`, and XRootD pthread mutex helpers. It is tightly coupled to `XrdSecEntity` construction and destruction.

## Risks And Edge Cases

- Public storage fields are accessible to implementation files but should not be modified by arbitrary consumers.
- Inheritance plus self pointer means object layout/lifetime is subtle; `eaAPI->entXtra` is the owning concrete object.

## Test Signals

Tests should verify base API methods correctly mutate this storage and destructor cleanup is idempotent after explicit `Reset()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityXtra.hh -->
