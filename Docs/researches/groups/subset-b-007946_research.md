# subset-b-007946 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.hh

## Purpose

This header declares `XrdOfsConfigCP`, the OFS configuration helper for checkpoint recovery support. It is a small static-only class that exposes global checkpoint settings, parses checkpoint-related configuration, initializes the feature, and recovers checkpoint files through an internal stats accumulator.

## Important APIs, types, and functions

The public static state is the main API: `Path` names the checkpoint path, `MaxSZ` and `MaxVZ` bound checkpoint size/count behavior, and `cprErrNA`, `Enabled`, `isProxy`, and `EnForce` advertise policy and runtime mode. `Init()` performs feature initialization, and `Parse(XrdOucStream &Config)` consumes configuration tokens from the shared XRootD config stream.

The private `Stats` struct tracks recovery totals: files seen, recovered, errored, skipped, and unresolved. `Recover(const char *ckpPath, Stats &stats)` is private because callers use `Init()`/`Parse()` rather than invoking recovery directly.

## Control flow

The intended flow is configuration parse, initialization, then optional recovery. `Parse()` reads the directive body from `XrdOucStream` and updates the static fields. `Init()` checks those fields and arranges recovery or runtime enablement. `Recover()` walks the checkpoint path and updates `Stats`, with logging and final reporting expected in the implementation file outside this work item.

## State and persistence behavior

All configuration is process-global static state. The header itself owns no durable data, but it points at durable checkpoint files on disk through `Path`. Recovery mutates filesystem state indirectly by reading checkpoint records and resolving pending operations.

## Dependencies and integration points

The only direct type dependency is `XrdOucStream`; the class integrates with the larger OFS configuration parser and with checkpoint/recovery code implemented in `XrdOfsConfigCP.cc`. `isProxy` suggests behavior is sensitive to proxy mode, while `EnForce` and `cprErrNA` likely affect how strictly checkpoint failures are handled.

## Risks and test signals

The main risk is global mutable state: multiple parses or partial initialization can leave stale path or limit values. Recovery must be careful with malformed checkpoint files, missing paths, and proxy deployments. Useful tests should cover disabled configuration, invalid limits, missing checkpoint paths, recovery stats accounting, and idempotence when `Init()` is called more than once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.cc

## Purpose

This file implements `XrdOfsConfigPI`, the OFS plugin configuration and loading coordinator. It parses `ofs.*lib` directives, records default and explicit plugin paths/parameters, loads core and stacked plugins, wires plugin pointers into OFS, and preserves ABI compatibility by hiding class layout behind the factory method declared in the header.

## Important APIs, types, and functions

The constructor initializes all plugin pointers, the checksum configurator, version info, and pushability for each plugin family. `New()` performs version compatibility checking with `XrdSysPlugin::VerCmp` and returns an instance. `Parse()` dispatches directive parsing for xattr, auth, checksum, CMS, FSctl, OSS, and prepare plugins. Specialized parsers handle directive options: `ParseAtrLib()` supports `osslib` and `++`, `ParseOssLib()` supports `++`, `+cksio`, `+mmapio`, and `+xattr`, and `ParsePrpLib()` supports `++` and `+noauth`.

`Load()` is the central load sequence. It loads OSS first, then xattrs, auth, checksum, CMS, FSctl, and prepare plugins. `SetupAttr()`, `SetupAuth()`, `SetupCms()`, `SetupCtl()`, and `SetupPrp()` load primary plugins with `XrdOucPinLoader`; `AddLibAtr()`, `AddLibAut()`, `AddLibCtl()`, `AddLibOss()`, and `AddLibPrp()` layer additional `++` wrappers. `Default()`, `DefaultCS()`, `Push()`, `RepLib()`, and `SetCksRdSz()` set configuration before loading. The overloaded `Plugin()` methods return loaded plugin pointers.

## Control flow

Configuration starts by recording defaults or parsed directives into `LP[]` and `ALP[]`. `RepLib()` owns replacement semantics, parameter capture from `XrdOucStream::GetRest()`, and warnings when explicit directives override defaults. `Load()` is one-shot: subsequent calls return the cached `LoadOK`. OSS is loaded first because other plugins may depend on it, and the native OSS path can implicitly enable checksum I/O. Xattr loading either comes from OSS, an explicit xattr library, or the active default `XrdSysXAttrActive` plus optional wrappers.

Authorization loads the default object or a configured shared library and then applies auth wrappers. Checksum loading delegates to `XrdCksConfig`, optionally passing the OSS plugin for checksum I/O. CMS loading resolves `XrdCmsGetClient`. FSctl loading resolves `XrdOfsFSctl` and records stacked control plugins; `ConfigCtl()` later calls `Configure()` on the primary plugin and then the saved vector. Prepare loading resolves `XrdOfsgetPrepare` and wraps through `XrdOfsAddPrepare`.

## State and persistence behavior

State is in-memory plugin configuration: `LP[]` for primary libraries, `ALP[]` for stacked libraries, `ctlVec` for FSctl configure order, and loaded plugin pointers. `Loaded`/`LoadOK` cache the one-shot result. The file does not persist configuration, but it pins shared libraries and mutates process-global xattr behavior with `XrdSysFAttr::SetPlugin()`.

## Dependencies and integration points

This file depends on XRootD plugin/version infrastructure, `XrdOucStream`, `XrdOucPinLoader`, `XrdSysPlugin`, `XrdCksConfig`, `XrdSysFAttr`, `XrdAccAuthorize`, `XrdOss`, `XrdCmsClient`, `XrdOfsFSctl_PI`, and `XrdOfsPrepare`. It is the integration point between text configuration and runtime plugin objects used by OFS file operations, checksumming, CMS location, authorization, extended attributes, FSctl, and prepare handling.

## Risks and test signals

Plugin load order is critical; loading prepare before OSS or missing xattr routing would break downstream runtime calls. Stacked plugin ownership is mostly by pinned libraries and raw pointers, so lifetime and reconfiguration assumptions must be stable. `ConfigCtl()` configures `ctlPI` and then iterates `ctlVec`, which can include stacked plugins; tests should confirm FIFO/LIFO expectations. Parser tests should cover malformed options, `++` rejection for non-pushable libraries, default override warnings, path replacement after `PinLoader::Path()`, one-shot `Load()`, and version incompatibility in `New()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.hh

## Purpose

This header defines the ABI-facing interface for OFS plugin configuration. It intentionally exposes methods but not implementation layout to callers, and requires callers to obtain instances through `XrdOfsConfigPI::New()`.

## Important APIs, types, and functions

`TheLib` encodes plugin families and their index bits: xattr, auth, checksum, CMS, FSctl, OSS, prepare, all, max count, and `libIXMask`. Public methods configure CMS/FSctl plugins, set defaults and checksum defaults, display settings, load requested plugin families, parse a directive, retrieve loaded plugin pointers, check checksum locality/OSS checksum use, check prepare authorization, push stackable plugins, and set checksum read size.

Private helpers mirror implementation responsibilities: `AddLib*()` for stacked plugins, `Parse*()` for directive-specific grammar, `RepLib()` for replacement, and `Setup*()` for primary plugin creation. The nested `xxxLP` owns copied library path, parameters, and option strings; `ctlLP` remembers FSctl plugin configure parameters.

## Control flow

Callers create an instance with `New()`, supply defaults before or after parse, call `Parse()` as each directive is encountered, then call `Load()` once with the requested bitmask. After load, `Plugin()` overloads provide typed plugin pointers to OFS. `ConfigCtl()` is intentionally separate because FSctl plugins receive the final authorization, CMS, OSS, and SFS plugin pointers.

## State and persistence behavior

The class stores plugin path strings, parameter strings, option strings, stacked plugin vectors, loaded raw pointers, version metadata, parser stream, logger, and flags such as `ossXAttr`, `ossCksio`, `prpAuth`, `Loaded`, `LoadOK`, and `cksLcl`. The state is process-local and not durable.

## Dependencies and integration points

The header includes `XrdCmsClient.hh` and forward-declares the major XRootD plugin interfaces. It integrates with OFS configuration, `XrdSfsFileSystem`, xattr setup, authorization, checksum management, CMS client generation, OSS storage, FSctl plugins, and prepare plugins.

## Risks and test signals

The enum values combine bit masks and indexes; any new plugin type must preserve `libIXMask` and `maxXXXLib` assumptions. `xxxLP::operator=` duplicates without freeing current members, which is acceptable for construction/vector copies but risky for true reassignment. Tests should pin ABI factory behavior, enum indexing, pushability rules, `Load()` idempotence, and pointer retrieval after successful and failed plugin loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.cc

## Purpose

This file implements the OFS event receiver used for dynamic staging notifications. It creates an admin FIFO, receives external stage events, correlates them with clients waiting through callback replacement, updates balancer state, and dispatches completion callbacks.

## Important APIs, types, and functions

`Init(XrdSysError*)` creates the FIFO at `$XRDADMINPATH/ofsEvents`, exports it as `XRDOFSEVENTS`, and stores its file descriptor. `Init(XrdCmsClient*)` starts the receiver and flusher threads. `recvEvents()` reads FIFO lines and dispatches known event names. `eventStage()` parses `stage {OK|ENOENT|BAD} <path> [msg]`. `Wait4Event()` replaces the caller's error callback with `theClient`, and `Work4Event()` adds that client to the event hash or immediately sends a preposted event. `sendEvent()` invokes original callbacks with `SFS_OK` or `SFS_ERROR`.

## Control flow

Initialization is two-phase: the FIFO must exist before the CMS/balancer object is available. The receive thread attaches `msgFD` to `eventFIFO` and loops on `GetLine()`. Stage events update `OfsStats`, derive an error message, notify the balancer with `Added()` or `Removed()`, then either prepost a `theEvent` in `Events` or satisfy waiting clients. Client wait setup avoids a race by replacing callbacks before the wait response goes back to the client.

The flush thread waits on `mySem` and periodically deletes deferred clients and scrubs hash entries. Events remain in the hash for `maxLife` so clients that arrive slightly after the external event can still be resumed.

## State and persistence behavior

State is in-memory: `Events` maps path to `theEvent`, `deferQ` delays deletion of first callback clients, `runQ` prevents duplicate flusher posts, and `eventFIFO` owns the FIFO stream. The FIFO path is durable in the admin filesystem, but event records are not persisted.

## Dependencies and integration points

The file integrates with `XrdOucErrInfo` callbacks, `XrdCmsClient` balancer notifications, `XrdNetSocket` FIFO creation, `XrdOucStream`, `XrdSysThread`, `XrdSysTimer`, `OfsStats`, and OFS tracing. External stage helpers communicate by writing event lines to the exported FIFO.

## Risks and test signals

The callback/hashing logic is concurrency-sensitive. Preposted events, duplicate callbacks, deferred deletion, and destructor-triggered FIFO close should be tested under races. `BAD` and invalid statuses increment `numSeventOK`, which may be intentional legacy behavior or a stats bug. `XrdOfsScrubScan()` is currently a no-op, so hash expiry relies on `XrdOucHash` TTL semantics. Tests should cover FIFO creation failures, missing `XRDADMINPATH`, malformed event lines, balancer updates, prepost-before-wait, wait-before-event, and callback de-duplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.hh

## Purpose

This header declares `XrdOfsEvr`, the dynamic staging event receiver. It exposes initialization, event receiving/flushing, client wait registration, and callback work handling.

## Important APIs, types, and functions

`Init(XrdSysError*)` and `Init(XrdCmsClient*)` split FIFO setup from thread/balancer setup. `Wait4Event()` registers a client for a path by replacing the error callback. `Work4Event()` is invoked by the nested `theClient::Done()` callback. `flushEvents()` and `recvEvents()` are thread entry targets.

`theClient` captures the original callback, callback argument, user, path, and owning `XrdOfsEvr`. `theEvent` records the final return code, final message, whether the event happened, and the waiting client list.

## Control flow

Clients first call `Wait4Event()` while issuing a wait-style response. The nested callback then calls back into `Work4Event()` after the wait is safely sent. External event lines are received by `recvEvents()`, parsed by private handlers, and fan out to waiting clients. The flusher thread handles delayed cleanup.

## State and persistence behavior

The class owns mutex/semaphore synchronization, FIFO stream state, CMS balancer pointer, deferred client queue, run flag, file descriptor, and an `XrdOucHash<theEvent>` keyed by path. State is runtime-only; event retention is bounded by `maxLife`.

## Dependencies and integration points

The header depends on `XrdOucHash`, `XrdOucErrInfo`, `XrdSysPthread`, and `XrdOucStream`, and forward-declares logging and CMS client types. It is consumed by OFS code that needs to wait for external stage completion.

## Risks and test signals

The nested callback owns raw pointers and requires stable lifetime boundaries. `Wait4Event()` transfers callback ownership into `theClient`, so tests should verify no leaks or double callbacks across immediate event, delayed event, and cancellation/destruction paths. Header-level signals include the eight-hour max life and path-based correlation, both worth regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.cc

## Purpose

This file implements OFS event sending. It formats filesystem events into text messages, queues them through a bounded message pool, and sends them either to a FIFO/socket target or to an external collector program.

## Important APIs, types, and functions

`XrdOfsEvsFormat::Def()` initializes default message formats, while `Parse()` overrides formats from `notifymsg` text using variables such as `$TID`, `$LFN`, `$CGI`, `$FMODE`, and `$FSIZE`. `XrdOfsEvs::Notify()` formats an enabled event into an `XrdOfsEvsMsg`. `Start()` creates a FIFO target when `Target` begins with `>`, otherwise starts an `XrdOucProg`. `sendEvents()` drains the queue and sends messages through `Feed()` or `XrdOucProg::Feed()`. `getMsg()` and `retMsg()` manage small and large free lists.

## Control flow

The constructor masks enabled events, stores the target, initializes free/queue state, and defines default formats for chmod, close, create, mkdir, mv, open, rm, rmdir, trunc, and fwrite. `Notify()` validates event index, converts mode/size placeholders when needed, obtains a message block, formats text with `snprintf`, appends to the queue, and posts the sender semaphore. The sender thread serializes output so blocked collectors do not stall request threads.

`Start()` chooses output mode. FIFO mode creates an `XRDNET_FIFO` socket and writes with `write()`. Program mode prepares and starts an external program once and feeds event data to it.

## State and persistence behavior

State is runtime-only: enabled event mask, target string, queue pointers, free-list pointers, pool quotas, sender thread ID, FIFO FD, and program object. No event queue is persisted; events can be lost if the process exits or if the bounded message object pool is exhausted.

## Dependencies and integration points

The implementation uses `XrdOucProg`, `XrdOucStream`, `XrdNetSocket`, `XrdSysThread`, POSIX `write/close`, and event data from `XrdOfsEvsInfo`. OFS request paths call `Notify()` after filesystem operations selected by config.

## Risks and test signals

The queue is intentionally bounded; when exhausted, `Notify()` drops events and logs only periodically. `sendEvents()` breaks while holding `qMut` when `endIT` is set and then unlocks afterward, so destructor/thread shutdown paths are delicate. Custom format parsing has fixed buffers and manual variable scanning; tests should cover escaped dollars, brace/bracket variables, too many variables, long formats, and invalid names. Integration tests should validate FIFO and program collector modes, large `mv` messages, queue exhaustion, and disabled event masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.hh

## Purpose

This header declares the OFS event sender data model, format table, and sender class used to notify external consumers about filesystem operations.

## Important APIs, types, and functions

`XrdOfsEvsInfo` carries event arguments: trace ID, primary and secondary logical paths, CGI strings, file mode, file size, and optional environment pointers. `XrdOfsEvsFormat` stores a printf-style format, conversion flags, and argument mapping, with `Def()`, `Set()`, and `SNP()` helpers.

`XrdOfsEvs::Event` defines masks and numbered events. `Enabled()` checks an event against the enabled mask, `Notify()` queues an event, `Parse()` overrides a message format, `Start()` launches the sender, `sendEvents()` is the thread loop, and `Prog()` exposes the configured target.

## Control flow

OFS builds an `XrdOfsEvsInfo` for each operation and calls `Notify()` when `Enabled()` returns true. Static `MsgFmt[]` maps each event number to a format. The sender hides destination details behind `Start()` and `sendEvents()`.

## State and persistence behavior

The header defines bounded message sizes and queue limits, but all state lives in memory. `MsgFmt[]` is static and process-wide, so custom parse settings affect all sender instances.

## Dependencies and integration points

It depends on XRootD pthread wrappers and forward-declares environment, program, message, and logger types. It integrates with OFS operation handlers and configuration directives that enable events or override event messages.

## Risks and test signals

The event enum combines bit masks and compact indexes; adding events must update `nCount`, default format initialization, and `eName()`. Static `MsgFmt[]` is mutable global state, so tests should avoid order dependence or reset formats. Header-level tests should check mask composition, small/large message size expectations, and custom format argument ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFAttr.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFAttr.cc

## Purpose

This file implements `XrdOfs::FAttr()` and the local extended-attribute control helpers. It exposes SFS file attribute operations for delete, get, list, and set, with authorization, redirect/proxy handling, export option checks, LFN-to-PFN conversion, and buffer management for attribute results.

## Important APIs, types, and functions

`FAttr()` is the entry point. Passing `faReq == nullptr` returns support metadata through the request environment. `ctlFADel()`, `ctlFAGet()`, `ctlFALst()`, and `ctlFASet()` implement local operations through `XrdSysFAttr::Xat`. Helper functions allocate response buffers (`GetFABuff()`), fetch values into packed buffers (`GetFAVal()`), retry oversized values (`GulpFAVal()`), and mark remaining attributes as `ENOMEM` (`SetNoMem()`).

## Control flow

`FAttr()` first handles support probing, validates request type, builds an `XrdOucEnv` from path CGI and client identity, obtains export options, and optionally performs authorization/remote location. Write requests are rejected for read-only exports. Proxy servers forward the whole request to OSS with `XRDOSS_FSCTLFA`; local servers reject no-xattr exports, translate the logical path to a physical path, and dispatch to the matching `ctlFA*` method.

List flow gets all xattr names, filters by prefix, optionally explodes names into `XrdSfsFAInfo`, optionally returns value sizes/values, and frees the xattr list. Get flow allocates an initial block and fetches each named attribute, growing by additional blocks for `ERANGE`. Set flow serializes replacement-style sets under `faMutex` but does not lock when creating new attributes.

## State and persistence behavior

The file itself keeps only a local mutex. Durable state is the filesystem xattr store behind `XrdSysFAttr::Xat`, addressed by PFN. Response buffers are attached to `faCtl.fabP` for the SFS caller to return/free according to interface expectations.

## Dependencies and integration points

It integrates with OFS authorization macros, `Finder` redirection, export option lookup, `XrdOfsOss` path mapping/proxy FSctl, `XrdSysFAttr`, `XrdSfsFACtl`, and XRootD security identity. It is the local implementation of attribute operations advertised through SFS.

## Risks and test signals

The prefix length calculation uses `sizeof(faCtl.nPfx)` when the prefix is non-empty, so behavior depends on `nPfx` being a fixed char array and may not mean string length. Buffer packing for list-with-values temporarily swaps `Name` and `Value`, which needs careful tests. Proxy and local paths have different execution surfaces. Tests should cover support probing, no-xattr/read-only export failures, remote locate failures, PFN mapping failures, list prefix filtering, large value fallback, per-attribute errors, new versus replace set locking, and proxied requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFAttr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFS.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFS.cc

## Purpose

This file provides the default SFS filesystem factory for OFS. It defines the global `XrdOfsFS` pointer and exports `XrdSfsGetDefaultFileSystem()`, which initializes the standard `XrdOfs` instance and returns it to the XRootD server.

## Important APIs, types, and functions

`XrdOfs *XrdOfsFS` is the global OFS singleton pointer used throughout the OFS implementation. `XrdSfsGetDefaultFileSystem(XrdSfsFileSystem *native_fs, XrdSysLogger *lp, const char *configfn, XrdOucEnv *EnvInfo)` is the plugin entry point expected by the SFS loader.

## Control flow

The factory sets the OFS error prefix and logger, routes tracing to the same logger, then enters a static mutex. If no OFS instance exists, it points `XrdOfsFS` at a static `XrdDefaultOfsFS`, stores a duplicated config filename, and calls `Configure()`. Configuration failure returns null. Later calls return the already configured singleton.

## State and persistence behavior

State is process-global and static: the singleton pointer, static mutex, and static default filesystem object. The config filename string is copied into `XrdOfsFS->ConfigFN`. There is no durable persistence in this file.

## Dependencies and integration points

It depends on `XrdOfs`, `XrdSysError`, `XrdSysTrace`, and `XrdSysPthread`. It is the load-time bridge from XRootD's SFS plugin system into the OFS implementation and logging/tracing globals.

## Risks and test signals

The singleton pattern means failed configuration after `XrdOfsFS` is set can leave a partially initialized global for later calls. The `native_fs` argument is unused here. Tests should cover successful first load, repeated load returning the same instance, configuration failure behavior, logger/prefix setup, and thread-safety under concurrent factory calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFS.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl.cc

## Purpose

This file implements OFS filesystem control operations. It handles legacy `fsctl()` commands such as locate/statfs/statls/statxa/statcc, routes v2 FSctl requests to cache, OSS, or plugin handlers, and forwards file-scoped fctl calls to an FSctl plugin.

## Important APIs, types, and functions

`XrdOfs::fsctl()` handles version-1 commands. Supported opcodes are `SFS_FSCTL_LOCATE`, `SFS_FSCTL_STATFS`, `SFS_FSCTL_STATLS`, `SFS_FSCTL_STATXA`, and `SFS_FSCTL_STATCC`. `XrdOfs::FSctl(const int, XrdSfsFSctl&, ...)` handles v2 plugin/cache/storage operations. `XrdOfs::FSctl(XrdOfsFile&, ...)` handles file-scoped control operations.

## Control flow

Locate splits path and opaque data, authorizes unless server selection is requested, optionally asks `Finder`, stats local OSS state, chooses server/read-write markers, and returns destination interface data. Statfs/statls authorize, optionally query remote finder space, then ask OSS for physical or logical space. Statxa locates if remote, asks OSS for extended stat data, appends authorization privilege letters, and returns data. Statcc returns cluster configuration status from `Finder` or `Balancer`, defaulting to `none|`.

V2 `SFS_FSCTL_PLUGXC` routes to `FSctl_PC` after optional read authorization. `SFS_FSCTL_PLUGFS` authorizes stat access, calls OSS `FSctl(XRDOSS_FSCTLFS, ...)`, and converts returned strings into `SFS_DATA`. Other v2 commands go to `FSctl_PI` if configured. File-scoped calls also require `FSctl_PI`.

## State and persistence behavior

No state is persisted here. The file reads runtime globals and member pointers: finder/balancer location services, network interface selection, OSS plugin, authorization plugin, cache/plugin handlers, and export/security environment data.

## Dependencies and integration points

It integrates with `XrdNetIF`, OFS security macros, `XrdCmsClient`, `XrdOss`, `XrdSfsFSctl`, `XrdSfsFAttr`, `XrdSecEntity`, `XrdOucEnv`, and `XrdOfsFSctl_PI`. It is an externally visible control surface for clients, cache plugins, OSS plugins, and FSctl plugins.

## Risks and test signals

Authorization and remote routing differ per opcode, so regressions can expose data or misroute requests. `STATXA` appends privilege data after the OSS buffer and assumes sufficient message buffer slack. `SFS_FSCTL_PLUGFS` mixes URL construction with opaque argument handling. Tests should cover each opcode, authorization denied paths, finder redirects/errors, IPv4/IPv6 destination selection, read-only and privilege letters, OSS negative/positive FSctl returns, absent plugins, and plugin forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl_PI.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl_PI.hh

## Purpose

This header defines the plugin interface for customizing OFS `FSctl()` behavior. It is loaded through the `ofs.ctllib` directive and supports both file-scoped and filesystem-scoped control operations.

## Important APIs, types, and functions

`XrdOfsFSctl_PI::Plugins` passes loaded authorization, CMS, OSS, and SFS/OFS plugin pointers into `Configure()`. `Configure()` is virtual and defaults to success. Two pure virtual `FSctl()` overloads must be implemented: the legacy file version taking `cmd`, raw args, an `XrdSfsFile`, and error info; and the v2 filesystem version taking `cmd`, `XrdSfsFSctl`, and error info.

The protected `prvPI` pointer supports stacked plugins, and `eDest` gives plugins the configured logger.

## Control flow

`XrdOfsConfigPI` loads a concrete object named `XrdOfsFSctl`, sets `eDest` and `prvPI`, and later calls `Configure()` with the plugin bundle. Runtime OFS control methods call the appropriate virtual `FSctl()` overload when built-in handling does not apply.

## State and persistence behavior

The interface stores only stack linkage and logger pointer. Plugin implementations own any additional state or persistence.

## Dependencies and integration points

It forward-declares the major XRootD interfaces needed by FSctl plugins and documents the expected global instance name and optional `XrdVERSIONINFO` declaration. It integrates with `XrdOfsConfigPI`, `XrdOfs::FSctl()`, SFS file objects, and security identity.

## Risks and test signals

Plugins run inside the OFS process and receive unscreened argument strings for some commands, so interface tests should ensure authorization is performed by OFS before forwarding when required. Stacked plugins must explicitly forward through `prvPI` if desired. ABI tests should verify object name resolution, version declarations, `Configure()` ordering, and both overload contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl_PI.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.cc

## Purpose

This file implements OFS shared file-handle tracking. It deduplicates active OSS file handles by path and access mode, manages reference counts and per-handle locking, tracks POSC ownership metadata, supports delayed retirement callbacks, and provides suppressed-error wrappers for handles that must remain readable/closable after write-side failure.

## Important APIs, types, and functions

`XrdOfsHandle::Alloc()` has path-based and dummy-handle variants. `Hide()` makes existing handles unfindable by clearing key length. `Activate()` attaches a real `XrdOssDF`. `Retire()` decrements references, removes table entries, closes/deletes OSS handles, and recycles handle objects. `Retire(XrdOfsHanCB*, int)` defers retirement through an expiry thread. `PoscSet()`, `PoscGet()`, and `PoscUsr()` manage persist-on-successful-close owner state. `Suppress()` wraps the OSS handle with `XrdOfsHanOssErr`.

Supporting classes include `XrdOfsHanTab` for hash tables, `XrdOfsHanKey` for CRC32 path keys, `XrdOfsHanPsc` for POSC metadata, `XrdOfsHanXpr` for deferred retire scheduling, and dummy/error OSS classes.

## Control flow

Path allocation locks the global table, finds an existing read-only or read-write entry, increments `Links`, releases the global lock, then tries to lock the handle. If it cannot lock quickly, it rolls back the link and returns a client delay. New handles are allocated in blocks, initialized, locked, added to the table, and counted in stats.

Retire requires the handle lock on entry. If reference count reaches one, it removes the handle from the appropriate table, recycles POSC data, frees path memory, swaps in the dummy OSS object, unlocks, and closes/deletes the real OSS handle outside the global lock. Deferred retire starts a background thread, schedules an `XrdOfsHanXpr`, and later calls the callback only if the handle is still uniquely referenced and active.

## State and persistence behavior

State is in memory: static global mutex, read-only and read-write hash tables, dummy OSS object, free handle list, POSC free list, expiry queue, and counters in `OfsStats`. POSC metadata includes queue offset and creator identity but durable queue persistence is handled by `XrdOfsPoscq`, not here.

## Dependencies and integration points

It depends on `XrdOssDF`, `XrdOfsStats`, `XrdSysMutex`, `XrdSysCondVar`, timers, and POSIX time. OFS file open/close paths use handles to share OSS file descriptors and coordinate POSC cleanup. `XrdOfsHanCB` lets higher-level code receive retirement callbacks.

## Risks and test signals

The global lock, per-handle lock, and expiry condition-variable lock interact in subtle ways. Tests should stress concurrent allocate/retire, lock timeout rollback, hash expansion, hidden handles, deferred retire rescheduling, and close error propagation. `PoscSet()` admits same creator reconnects but rejects different users unless re-enabled; recovery tests should pin that behavior. The dummy/error OSS wrappers intentionally return configured errors and must still allow close/stat/read paths required by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.hh

## Purpose

This header declares private OFS handle data structures. They are used to manage shared storage-system file handles, per-path lookup, reference counts, POSC metadata, and retirement callbacks.

## Important APIs, types, and functions

`XrdOfsHanKey` stores path value, link count, CRC hash, and length, with equality based on hash, length, and string content. `XrdOfsHanTab` provides add/find/remove and hash-table expansion. `XrdOfsHandle` exposes state flags for pending sync, changed file, compression, and read-write mode; allocation and retirement APIs; POSC APIs; storage selection; suppression; usage count; and explicit locking. `XrdOfsHanCB` is the callback interface for deferred retirement.

## Control flow

Callers allocate a handle, attach an OSS object with `Activate()`, operate on `Select()`, then retire it when done. POSC callers set creator metadata while holding the handle lock and retrieve/remove it during close or recovery. Deferred retirement invokes `XrdOfsHanCB::Retired()` when the background expiry thread reaches the handle.

## State and persistence behavior

Static members maintain global tables and free lists. Per-handle state includes mutex, selected OSS object, table linkage, key, and POSC pointer. The header itself does not persist data; POSC queue offsets link it to the separate durable queue.

## Dependencies and integration points

It depends on CRC and XRootD pthread wrappers and forward-declares OSS/file callback support. It is tightly coupled to `XrdOfsHandle.cc`, OFS file open/close code, `XrdOssDF`, and POSC recovery handling.

## Risks and test signals

`XrdOfsHanKey::operator=` duplicates `Val` without freeing an existing value, so it relies on controlled initialization/recycling. `Inactive()` compares against the dummy OSS object. Tests should verify object reuse clears stale flags, path keys remain valid after hide/retire, and callback code respects the documented "handle must be locked" preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsHandle.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.cc

## Purpose

This file implements the persistent queue used for POSC pending creates. It records files that must be cleaned up or recovered if a create/write operation does not complete successfully, and reconstructs pending entries at startup.

## Important APIs, types, and functions

The constructor stores logger, OSS pointer, queue filename, file descriptor state, and sync cadence. `Add()` appends or reuses a slot for a pending create. `Commit()` marks a record committed by writing the add timestamp and removes it from the in-memory map. `Del()` optionally unlinks the file and clears the record. `Init()` opens/creates the queue and recovers valid pending records. `List()` reads queue records in read-only diagnostic mode. `ReWrite()` compacts/rebuilds the queue into a `.new` file and renames it into place.

## Control flow

`Init()` opens the queue file, truncates a new/small file to the record offset, or scans existing fixed-size records from `ReqOffs`. Records with empty LFNs, missing files, non-regular files, or non-POSC-pending modes are ignored. Valid records are returned as a linked list and then rewritten compactly, updating `pqMap` with offsets.

`Add()` checks existing file state to avoid deleting already created files. For retry/replacement cases it can return an existing verified offset. Otherwise it fills a `Request`, takes a free slot or extends `pocSZ`, writes the record, increments queue count, and updates `pqMap`. `Commit()` validates offset shape, writes current time into `addT`, and erases the map entry. `Del()` validates, optionally unlinks, clears the record's LFN field, recycles the slot, decrements count, and erases the map entry.

## State and persistence behavior

Durable state is a fixed-record queue file starting at offset 64, with each record containing add time, LFN, user, and reserved bytes. In-memory state includes queue size, pending count, map from LFN to offset, free-slot lists, file descriptor, and sync countdown. `reqWrite()` fsyncs after a configurable number of full-record writes.

## Dependencies and integration points

It depends on `XrdOss` for stat/unlink checks, `XrdSysFD_Open`, POSIX `pread/pwrite/ftruncate/fsync/rename`, and SFS mode flags such as `XRDSFS_POSCPEND`. It integrates with `XrdOfsHandle` POSC offsets and startup recovery.

## Risks and test signals

`VerOffset()` validates only offset shape, not that the offset still belongs to the supplied LFN, so callers must pass trusted offsets. `Add()` decrements `pocIQ` under a second explicit lock even though `XrdSysMutexHelper` already holds the mutex; this path warrants scrutiny for deadlock depending on mutex semantics. `ReWrite()` does not fsync the directory after rename. Tests should cover new queue creation, corrupt/short records, retry add behavior, commit/del offset validation, free-slot reuse, rewrite compaction, unlink errors, sync cadence, and recovery of only POSC-pending regular files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.hh

## Purpose

This header declares `XrdOfsPoscq`, the persistent create queue for POSC cleanup/recovery.

## Important APIs, types, and functions

`Request` is the on-disk fixed-size record containing add time, logical filename, user trace identifier, and reserved bytes. `ReqOffs` and `ReqSize` define file layout. `recEnt` is the in-memory linked-list record returned by initialization/listing, with record offset, mode, and request data.

Public methods are `Add()`, `Commit()`, `Del()`, `Init()`, static `List()`, `Num()`, and the constructor. Private helpers handle initialization failure logging, writing, rewriting, and offset verification.

## Control flow

OFS creates a queue object, calls `Init()` at startup, then uses `Add()` when a POSC create begins, `Commit()` when creation succeeds, and `Del()` when cleanup or recovery removes a pending entry.

## State and persistence behavior

The class owns a durable queue filename and FD plus in-memory maps/free-slot lists. The queue file stores durable recovery intent; `pqMap` and slot lists are rebuilt or updated at runtime.

## Dependencies and integration points

It depends on `XrdOss` for file state and unlink operations, `XrdSysError` for logging, pthread mutexes, and standard map/string. It links POSC offsets to `XrdOfsHandle` and startup recovery logic.

## Risks and test signals

The record layout uses fixed 1024-byte LFN and 288-byte user buffers, so tests should cover truncation and null termination. Offset verification is minimal. Version/sync fields (`pocSV`, `pocWS`) should be covered by tests for configured sync frequency and edge values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepGPI.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepGPI.cc

## Purpose

This file implements the generic OFS prepare plugin, `PrepGPI`. It adapts XRootD prepare, stage, evict, cancel, and query requests to an external program configured by `ofs.preplib`, with bounded worker concurrency, optional query output capture, request queuing, and optional LFN-to-PFN translation.

## Important APIs, types, and functions

Global plugin state in `XrdOfsPrepGPIReal` stores logger, OSS pointer, scheduler, program, worker pool, query limits, option flags, admitted request mask, and buffer pool. `PrepRequest` owns argument/environment vectors and copied string storage. `PrepGRun` is an `XrdJob` runner with `Run()`, `Capture()`, `makeArgs()`, `Sched()`, and `DoIt()`. `PrepGPI` implements `XrdOfsPrepare::begin()`, `cancel()`, and `query()`, plus `Assemble()`, `ApplyN2N()`, `reqFind()`, `RetErr()`, and `Xeq()`.

The exported `XrdOfsgetPrepare()` parses parameters such as `-admit`, `-cgi`, `-debug`, `-maxfiles`, `-maxquery`, `-maxreq`, `-maxresp`, `-pfn`, and `-run`, initializes `XrdOucProg`, creates worker runners, and returns a `PrepGPI`.

## Control flow

At load time, parameters come from directive data or gathered config body. The plugin requires at least one admitted request and a runnable external program. For begin requests, OFS options choose `evict`, `stage`, or `prep`; unsupported request types return `SFS_ERROR`. `Assemble()` counts paths, enforces `maxFiles`, creates `XRDPREP_TID`, optional `XRDPREP_COLOC` and `XRDPREP_NOTIFY`, maps prepare flags to command arguments, adds request id/name, and appends paths, optionally adding CGI or translating to PFN.

`Xeq()` either schedules a free `PrepGRun` on the XRootD scheduler or appends the request to a global queue. `PrepGRun::DoIt()` drains the request queue serially through the runner object. Query requests either report queued/not queued when query is unsupported, or run synchronously through a dedicated runner after passing the `qryAllow` concurrency gate and capture output into the error response.

## State and persistence behavior

All state is runtime-only. Queued `PrepRequest` objects live in memory and are lost on process exit. The external prepare program may persist request state, but this file does not. Query response buffers may come from `XrdOucBuffPool` when configured above the normal error-info maximum.

## Dependencies and integration points

It depends on `XrdOfsPrepare`, `XrdOss`, `XrdScheduler`, `XrdOucProg`, config gathering/parsing helpers, `XrdOucBuffer`, `XrdOucTList`, `XrdSfsPrep`, security identity, and XRootD tracing/version macros. It is loaded by `XrdOfsConfigPI` via `XrdOfsgetPrepare`.

## Risks and test signals

Queue linkage in `Xeq()` assigns `rP->next = PrepRequest::Last` instead of linking from the old last to the new request, which appears suspicious and should be tested with more queued requests than workers. `Assemble()` in CGI mode assumes `pargs.oinfo` is present and aligned with paths. Query gating explicitly allows spurious wakeups to exceed the limit. Tests should cover parameter validation, admitted request masks, max file enforcement, PFN translation failure, CGI path building, scheduler queuing under saturation, cancel/query fallback behavior, query timeout, response truncation, and external program failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepGPI.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepare.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepare.hh

## Purpose

This header defines the OFS prepare plugin interface. Prepare plugins customize `kXR_prepare` behavior for staging, prefetching, eviction, cancellation, and query workflows.

## Important APIs, types, and functions

`XrdOfsPrepare` is an abstract base class with pure virtual `begin()`, `cancel()`, and `query()` methods. `XrdOfsgetPrepare_t` is the factory signature for creating a prepare plugin from a shared library. `XrdOfsAddPrepare_t` is the wrapper factory signature for stacking a new prepare plugin around an existing one. Macros define the canonical argument lists for exported functions.

## Control flow

`XrdOfsConfigPI` loads a library, resolves `XrdOfsgetPrepare`, passes logger/config/parameters/SFS/OSS/environment pointers, and stores the returned object. Additional `++` prepare plugins are loaded through `XrdOfsAddPrepare`, receiving the current plugin pointer for wrapping.

## State and persistence behavior

The interface owns no state. Implementations decide whether prepare request IDs and staging state are durable or in-memory.

## Dependencies and integration points

The header forward-declares OSS, environment, error info, security identity, SFS filesystem, and `XrdSfsPrep`. It is consumed by OFS request handling, plugin config, and concrete prepare plugins such as `XrdOfsPrepGPI.cc`.

## Risks and test signals

Return-code semantics are part of the contract: `SFS_DATA` and `SFS_OK` carry request IDs differently for `begin()`, while cancel/query have narrower return sets. Plugin tests should validate exported symbol names, null factory failure, stacked wrapper behavior, and how OFS translates `SFS_STARTED`, `SFS_DATA`, and `SFS_ERROR` responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepare.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsSecurity.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsSecurity.hh

## Purpose

This header defines authorization helper macros used by OFS methods. It centralizes access checks, error reporting, and security identity propagation into opaque environments.

## Important APIs, types, and functions

`AUTHORIZE(usr, env, optype, action, pathp, edata)` checks `XrdOfsFS->Authorization` when a user is present, calls `Access()`, and on failure reports `EACCES` through `XrdOfsFS->Emsg()` before returning `SFS_ERROR` from the enclosing function. `AUTHORIZE2()` applies two authorization checks. `OOIDENTENV()` copies `SEC_USER` and `SEC_HOST` into an `XrdOucEnv`.

## Control flow

Call sites invoke these macros before sensitive filesystem operations. Failure short-circuits the caller, so the macros are not expression helpers; they assume local variables such as `epname` and compatible return types.

## State and persistence behavior

The macros do not own state. They read the global `XrdOfsFS` and its authorization plugin, and mutate an environment object in `OOIDENTENV()`.

## Dependencies and integration points

The header includes `XrdAccAuthorize.hh` and expects OFS globals, SFS return codes, errno values, and `XrdSecEntity`/`XrdOucEnv` style objects at call sites. It integrates with most user-facing OFS operations.

## Risks and test signals

Macro control flow can hide returns and variable dependencies. Tests should cover operations with no user, no authorization plugin, allowed access, denied access with extra text, and environment identity propagation. Refactors should be careful not to call `AUTHORIZE()` inside functions with incompatible return types or missing `epname`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsSecurity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.cc

## Purpose

This file implements the XML stats report formatter for OFS counters.

## Important APIs, types, and functions

`XrdOfsStats::Report(char *buff, int blen)` returns the required buffer size when `buff` is null, validates buffer length, snapshots `Data` under `sdMutex`, and formats a `<stats id="ofs">` XML fragment containing role, open counts, handle counts, replies/errors/delays, stage-event counts, and TPC counters.

## Control flow

Callers first may call `Report(nullptr, 0)` to learn a conservative buffer size. With a real buffer, the method fails with `0` if the buffer is too small, otherwise copies counters under lock and uses `sprintf()` with a fixed format.

## State and persistence behavior

The file reads in-memory counters from `XrdOfsStats::Data`. It does not persist state. Snapshotting under the mutex avoids mixed counter values while formatting outside the lock.

## Dependencies and integration points

It depends only on `cstdio` and the stats header. It integrates with XRootD monitoring/status paths that collect OFS statistics.

## Risks and test signals

The conservative `statsz` calculation should be kept large enough for role text and integer growth. XML escaping is not applied to `myRole`; role values should be controlled. Tests should cover size-only calls, too-small buffers, zero counters, non-default role, high counter values, and field ordering expected by monitoring consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.hh

## Purpose

This header declares the OFS statistics container and simple synchronized counter operations.

## Important APIs, types, and functions

`StatsData` contains counters for read/write/POSC opens, unpersisted POSC entries, handles, redirects, started operations, replies, errors, delays, stage event success/error counts, and third-party-copy grants/denials/errors/expirations. `Add()` and `Dec()` increment/decrement counters under `sdMutex`. `Report()` formats counters, and `setRole()` sets the role string reported in XML.

## Control flow

OFS operation paths update individual counters through `Add()`/`Dec()`. Monitoring code calls `Report()` to obtain a snapshot. Configuration or role setup calls `setRole()`.

## State and persistence behavior

All state is in-memory and protected by a single mutex for updates and snapshots. The constructor zeroes `Data` and defaults role to `"?"`.

## Dependencies and integration points

It depends on XRootD pthread wrappers and is referenced by event receiver, handle tracking, request handling, and stats/status reporting code.

## Risks and test signals

Because counters are plain `int`, extreme long-running servers can overflow. `setRole()` stores a raw pointer without copying, so the caller must pass stable storage. Tests should cover synchronized updates, decrement behavior, report snapshots during updates, and role pointer lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsStats.hh -->
