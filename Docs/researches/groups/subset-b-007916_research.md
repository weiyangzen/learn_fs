# subset-b-007916 grouped research

This grouped report covers the XRootD application utilities, the BWM SFS plugin, and the Ceph buffer/readv helpers assigned to `subset-b-007916`. Each source file is documented in its own marked section for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMpxStats.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdMpxStats.cc

Purpose: implements the `mpxstats` UDP listener utility. It receives XML statistics datagrams on a configured UDP port and writes them to stdout either as raw XML or after conversion through `XrdMpxXml` into CGI/flat text formats.

Important APIs/types/functions: namespace globals `XrdMpx::Logger`, `Say`, `Opts`, and `statsQ`; `XrdMpxOut::statsBuff` holds source address, data length, and an 8190-byte payload; `XrdMpxOut::getBuff`, `Add`, and `Run` implement a small producer/consumer queue; `mainOutput` is the thread trampoline; `main` parses `-d`, `-f`, `-p`, and `-s`.

Control flow: `main` validates the port, blocks SIGPIPE/SIGCHLD, sets XrdSys thread stack size, opens a UDP server socket with `XrdNetSocket`, optionally creates an `XrdMpxXml`, starts one output thread, and then loops forever calling `recvfrom`. Received buffers are queued to `XrdMpxOut::Run`, which formats with sender host when `-s` is set and writes all bytes to stdout with EINTR retry.

State and persistence: all state is in memory. The output queue keeps input and free buffer linked lists under `XrdSysMutex` and wakes the consumer via `XrdSysSemaphore`; no data is persisted beyond stdout.

Dependencies and integration points: depends on XRootD networking (`XrdNetSocket`, `XrdNetAddr`), system threading/semaphores, and `XrdMpxXml`. It is an external utility consuming statistics multicast/unicast streams emitted by XRootD servers or collectors.

Risks: `fromLen` is initialized with `sizeof(sbP->From)` while `sbP` is null; this works only because `sizeof` is compile-time but is visually fragile. The write loop subtracts `rc` without handling `write` returning `-1` for non-EINTR errors, which can corrupt pointer/length arithmetic. Output buffer sizing assumes formatted output fits `sizeof(statsBuff)*2`.

Test signals: exercise option parsing, invalid port handling, raw/XML/flat/CGI output, sender host resolution, EINTR write retry, and high-rate UDP receive with queue reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMpxStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.cc

Purpose: converts XRootD `<statistics>` XML streams into compact CGI, flat key/value, or human text output for `mpxstats` and `xrdqstats`.

Important APIs/types/functions: file-local `vnMap` maps dotted XML variable names to text labels and marks time fields with `~`; `XrdMpxVar` maintains a dotted element stack with `Push`, `Pop`, `Reset`, and `Var`; `XrdMpxXml::Format` performs parsing and formatting; `Add` emits one variable/value pair; `getVars` parses XML-style attributes from the tokenizer; `xmlErr` reports malformed streams.

Control flow: `Format` first rewrites the input buffer in place to make tokens line-oriented, validates that the first record starts with `<statistics`, extracts header attributes (`tod`, `ver`, `src`, `tos`, `pgm`, `ins`, `pid`), appends an optional host, then walks tokens until `/statistics`. Opening tags push stack names, `stats id="..."` pushes the id value, closing tags pop, and text tokens are emitted under the current dotted path. Tail attribute `toe` is appended when present.

State and persistence: conversion state is transient. `Format` mutates its input buffer by replacing delimiters with whitespace/newlines and trimming quotes, so callers must not expect the original XML to remain intact. No persistent storage is used.

Dependencies and integration points: uses `XrdOucTokenizer`; called by XrdApps utilities that query or receive stats. The text-label map hardcodes XRootD statistic schema knowledge.

Risks: parsing is token-based rather than XML-compliant, so unusual whitespace, escaping, nested text, or larger messages can misparse. Output uses unbounded `strcpy` into caller-provided buffers. `XrdMpxVar::Push` can partially modify `vEnd` before detecting some fence failures. Text time conversion uses `localtime`, which is not thread-safe.

Test signals: compare XML-to-flat/CGI/text conversion for representative stats payloads, malformed XML, deep nesting, zero suppression, quoted values, time fields, and unknown variable names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.hh

Purpose: declares the lightweight statistics XML formatter used by XRootD command-line stats tools.

Important APIs/types/functions: `XrdMpxXml::fmtType` selects `fmtCGI`, `fmtFlat`, `fmtText`, or `fmtXML`; the constructor derives separator/suffix behavior and enables human variable-name translation for text; public `Format(const char *Host, char *ibuff, char *obuff)` converts one mutable input XML buffer into the provided output buffer.

Control flow: callers instantiate only when they need non-XML output. `Format` delegates to private helpers `Add`, `getVars`, and `xmlErr`; headers and stack logic live in the `.cc`.

State and persistence: each object stores format flags (`fType`, `vSep`, `vSfx`, `Debug`, `noZed`, `doV2T`). There is no persistent state, but `Debug` and `noZed` affect every conversion through the object.

Dependencies and integration points: forward-declares `XrdOucTokenizer` and is included by `XrdMpxStats.cc` and `XrdQStats.cc`. It is not a general XML API; it is coupled to the XRootD statistics XML shape.

Risks: the constructor parameter name `nz` is used both as no-zero suppression and, in one caller, as debug-only context; users must understand the exact signature. `fmtXML` is declared but the converter object is normally not created for XML passthrough. `Format` has no output length parameter.

Test signals: compile-time coverage of all enum values, constructor behavior for separator/suffix, zero suppression in text mode, and callers passing mutable buffers of sufficient size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdPinls.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdPinls.cc

Purpose: implements `xrdpinls`, a utility that prints plugin version requirements derived from generated/version macros.

Important APIs/types/functions: `Display` formats one directive-to-plugin rule using `XrdVersionPlugin` fields; `main` materializes `XrdVERSIONPLUGINRULES` and `XrdVERSIONPLUGINMAPD2P`, maps plugin creator names to rules, maps configuration directives to rules, and prints sorted directive results.

Control flow: all plugin rules are indexed by `pName`, then directive mappings are walked to find matching plugin entries. The directive map is ordered lexicographically by `cmp_str`, so output is sorted by directive name. `Display` classifies `vProcess` as Untested, Optional, Required, or Unknown and renders the minimum major/minor version.

State and persistence: no persistent state. All maps are local to `main`, and output goes to stdout.

Dependencies and integration points: depends on `XrdVersionPlugin.hh`, which supplies the generated rule arrays. It is a diagnostic companion for XRootD plugin ABI/version policy.

Risks: the condition `itV != dRules.end()` compares an iterator from `vRules` against `dRules.end()`, which is undefined/wrong; it should compare against `vRules.end()`. That can lead to invalid dereference or incorrect missing-rule detection. The program ignores command-line arguments even though syntax says no options.

Test signals: build and run against current version macro tables, check required/optional/untested formatting, and add a regression for missing plugin rules to catch the iterator-container bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdPinls.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdPrep.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdPrep.cc

Purpose: implements `xrdprep`, an XrdCl-based command-line client for prepare, cancel, and query requests against an XRootD server.

Important APIs/types/functions: `GetNum` validates numeric options; `Usage` prints supported command modes; `main` parses options and invokes `XrdCl::FileSystem::Prepare` or `Query(QueryCode::Prepare, ...)`. It uses `PrepareFlags` for Evict, Stage, Colocate, Fresh, WriteMode, and Cancel.

Control flow: options are parsed first, then an optional keyword (`cancel`, `query`, `prepare`) determines whether a handle is required or paths are required. The target is converted to `root://host[:port]`. Paths come from remaining arguments plus optional `-f` input file lines. Cancel/query build a newline-separated query buffer; prepare passes the vector directly with priority.

State and persistence: no local persistence. It may read a path list file and exports `XRD_LOGLEVEL` when debug is requested. Server-side prepare state is external to this utility.

Dependencies and integration points: integrates with `XrdCl::FileSystem`, `XrdCl::Buffer`, `XrdOucEnv`, and XRootD server prepare/query protocol. Error messages are normalized from `XRootDStatus`.

Risks: `Target` is a fixed 512-byte buffer populated by `strcpy`/`strcat`; long host arguments can overflow. Total query buffer size is computed from string sizes and newlines, but empty `fList` with query/cancel may produce odd buffer behavior. Option validity is tied to `lastOpt`, so mixed command ordering needs coverage.

Test signals: prepare with paths, prepare from `-f`, cancel/query with handle and optional path filters, invalid numbers, invalid command/option combinations, long host rejection, server error response formatting, and debug environment mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdPrep.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdQStats.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdQStats.cc

Purpose: implements `xrdqstats`, a client-side stats query utility that asks an XRootD server for selected statistic categories and prints XML or converted text/flat/CGI output.

Important APIs/types/functions: `Fatal` reports failed `XRootDStatus`; `Usage` documents options; `main` parses `-f`, `-i`, `-n`, `-s`, `-z`, constructs an `XrdCl::URL`, creates a `FileSystem`, performs `Query(QueryCode::Stats, ...)`, and formats with `XrdMpxXml`.

Control flow: statistics letters default to `bldpsu`; `c` is normalized to `l`. Count/interval rules make one-shot default, repeated default every 10 seconds when `-n` is given, and endless looping when only `-i` is given. Each loop queries the server, writes raw XML for `fmtXML`, or converts through `XrdMpxXml::Format` and writes with EINTR retry.

State and persistence: maintains only local loop counters and buffers. No persistence; repeated operation depends entirely on remote server stats.

Dependencies and integration points: uses XrdCl URL/FileSystem/Buffer/XRootDResponses and shares formatter code with `mpxstats`.

Risks: the write loop has the same non-EINTR write error handling gap as `mpxstats`. `obuff` is fixed at 65536 with no bounds contract from `Format`. `-d` is accepted but not listed in usage options except via `valOpts`; debug only affects formatter behavior.

Test signals: all format modes, zero suppression in text mode, stats letter validation, count/interval matrix, invalid URL handling, xrootd error response extraction, and repeated query behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdQStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdWait41.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdWait41.cc

Purpose: implements `wait41`, a synchronization utility that waits until it can acquire the first write lock among a set of files or files inside provided directories.

Important APIs/types/functions: `XrdW41Gate` owns static mutex/semaphore/gate flag and exposes `Serialize` plus `Wait41`; `XrdW41Dirs::Expand` expands one directory into regular-file paths; `XrdWait41::GateWait` is the thread trampoline; `main` builds the file list and waits.

Control flow: `main` blocks SIGPIPE/SIGCHLD, sets thread stack size, turns regular file args into `XrdOucTList` nodes, expands directory args, and fails with `BAD` if there is nothing to wait on. `Wait41` opens each file, starts one thread per file, and each thread performs blocking `fcntl(F_SETLKW)` write lock. The first successful lock sets `gateOpen` and wakes the main waiter, which prints `OK`.

State and persistence: creates/open files with `O_CREAT|O_RDWR` mode `0644` and keeps the winning descriptor open until process exit. The utility then waits for stdin read before exiting, preserving the lock while its parent keeps the pipe open.

Dependencies and integration points: uses POSIX `stat`, `opendir`, `fcntl` locks, XRootD list/thread/semaphore wrappers, and error text helpers. Likely used by scripts needing “wait for first resource” behavior.

Risks: one thread per path can be expensive for large directories. `Expand` uses a fixed 1024-byte path buffer and `strcpy`, risking overflow. The process intentionally waits on stdin after success, so unattended use can hang unless the caller closes stdin.

Test signals: regular file success, directory expansion, nonexistent path warnings, all-open failures, early success before all threads launch, lock release on process exit, and large-directory/thread pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdWait41.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/Xrdadler32.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/Xrdadler32.cc

Purpose: implements `xrdadler32`, computing or retrieving Adler-32 checksums for stdin, local files, virtual-mapped paths, and `root://` URLs.

Important APIs/types/functions: `fSetXattrAdler32` writes checksum metadata using XRootD checksum xattrs and removes old native attrs; `fGetXattrAdler32` has native and XRootD xattr variants; `getchksum` asks a remote server for `xroot.cksum`; `main` selects local versus remote path behavior and computes with zlib `adler32`.

Control flow: `main` handles `-h`, converts arguments through `XrdPosixXrootPath` when possible, uses local open/stat/read for non-root paths or stdin, consults cached xattrs before reading local files, stores new xattrs after computing, and for remote files first tries server checksum metadata. If absent, it opens through `XrdPosixXrootd` and reads until file size is covered.

State and persistence: can persist local checksum metadata in XRootD checksum xattr format and removes the older `user.checksum.adler32` attr after migration. Remote state is read-only.

Dependencies and integration points: depends on zlib, XrdPosix path/IO wrappers, XrdCks checksum xattr types, and platform xattr APIs.

Risks: fixed path/checksum buffers use `strcpy`; long URLs or paths can overflow. Native xattr reader assumes `attr_val[8]` exists even if fewer than 9 bytes are returned. Remote fallback has a comment for an XrdClEC regression and bounds read length against stat size. `getchksum` returns `char`, which is too narrow for checksum length/error semantics.

Test signals: stdin checksum, local cache hit/miss/stale mtime, xattr migration, root URL server-checksum success/failure, virtual mount translation, remote read fallback, and permission/access errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/Xrdadler32.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdBwm/CMakeLists.txt

Purpose: defines the XrdBwm plugin build target.

Important APIs/types/functions: sets module target name `XrdBwm-${PLUGIN_VERSION}`; includes implementation, headers, policy, logger, handle, config, and trace files; links against `XrdServer`, `XrdUtils`, and thread libraries; installs the module into `${CMAKE_INSTALL_LIBDIR}`.

Control flow: CMake only. There are no conditional branches in this file; the parent build controls whether this directory is included.

State and persistence: no runtime state. Build output is a loadable module rather than a linked executable.

Dependencies and integration points: integrates with XRootD plugin naming/versioning conventions and server module loading. The included source list shows BWM is self-contained except for XRootD server/util dependencies and optional runtime-loaded auth/policy libraries.

Risks: because headers are listed as sources, IDE visibility is improved but behavior depends on CMake treating them as non-compilation units. Missing source entries would break plugin features at link time; no tests are declared here.

Test signals: configure/build with plugin version set, verify produced module name, link dependencies, install destination, and server-side load of `XrdSfsGetFileSystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.cc -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.cc

Purpose: implements the BWM SFS filesystem plugin that grants bandwidth/resource “visas” through pseudo-file opens and `fctl(SFS_FCTL_STATV)`.

Important APIs/types/functions: global `BwmEroute`, `BwmTrace`, and singleton `XrdBwmFS`; exported `XrdSfsGetFileSystem`; `XrdBwmDirectory` methods all reject directory operations; `XrdBwmFile::open`, `close`, `fctl`, read/write/stat/sync/truncate methods; `XrdBwm` filesystem operations mostly return unsupported; `Emsg` and `Stall` centralize error/delay responses.

Control flow: plugin construction discovers host/domain and advertise address, creates a dummy handle, and initializes defaults. On plugin load, `Configure` runs. File open requires read/write mode, optional authorization, opaque `bwm.src` and `bwm.dst`, and an LFN embedded after the pseudo prefix. Direction is inferred by matching source/destination host against the local domain, then an `XrdBwmHandle` is allocated. `fctl(SFS_FCTL_STATV)` activates scheduling and returns visa data or async start. `close` retires the handle.

State and persistence: singleton plugin state includes host/domain strings, authorization/policy/logger pointers, locate response, and an open/close mutex. Per-file state is the current `XrdBwmHandle`; no disk namespace is implemented. The policy/logger hold runtime queues and event state.

Dependencies and integration points: integrates with XrdSfs plugin API, XrdAcc authorization, XrdBwmHandle/policy/logger, XrdOucEnv opaque parsing, XrdNet host discovery, and XrdSec identity.

Risks: almost every namespace operation is unsupported, so clients must use the intended pseudo-file/fctl flow. Domain matching with suffix checks can misclassify unusual hostnames. Fixed strings and global singleton design limit reconfiguration. `stat` fabricates block-device-like mode.

Test signals: plugin load/configure, open with missing opaque keys, authorization denial, incoming/outgoing direction inference, `STATV` immediate/queued/failure cases, close cancellation/release, and unsupported method errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.hh -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.hh

Purpose: declares the BWM SFS plugin object model: directory shim, file shim, filesystem singleton, and configuration/runtime fields.

Important APIs/types/functions: `XrdBwmDirectory` derives `XrdSfsDirectory`; `XrdBwmFile` derives `XrdSfsFile` and exposes open/close/fctl/read/write/sync/stat/truncate/CX methods; `XrdBwm` derives `XrdSfsFileSystem`, creates file/directory objects, exposes core SFS operations, `Configure`, config parsing helpers, authorization/policy/logger pointers, and static `dummyHandle`.

Control flow: this header defines the contracts implemented by `XrdBwm.cc` and `XrdBwmConfig.cc`. File objects use `oh` to track the current handle and call into BWM state through the singleton.

State and persistence: fields in `XrdBwm` are long-lived plugin process state. `XrdBwmFile` holds only `tident` and `oh`. No persistent on-disk structures are declared.

Dependencies and integration points: includes `XrdBwmHandle.hh`, XRootD pthread and SFS interfaces; forward-declares authorization, logger, policy, config stream, and version types.

Risks: the header exposes many mutable fields publicly in the “configuration values” block, which couples implementation files to object internals. Destructor intentionally does not clean complex global state. `XrdBwmFile` destructor calls `close` only if `oh` is non-null, including dummy handle behavior.

Test signals: compile ABI against XrdSfs interface, newFile/newDir object creation, destructor cleanup path, and config-driven policy/logger/authorization setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmConfig.cc

Purpose: parses BWM configuration directives and wires authorization, policy, tracing, and logging into the plugin.

Important APIs/types/functions: `XrdBwm::Configure`, `ConfigXeq`, `xalib`, `xlog`, `xpol`, `xtrace`, `setupAuth`, and `setupPolicy`. Parser macros dispatch recognized directives: `authorize`, `authlib`, `log`, `policy`, and `trace`.

Control flow: `Configure` enables full tracing from `XRDDEBUG`, optionally opens the config file, captures BWM config lines, and applies `bwm.` directives. It then conditionally initializes authorization, chooses a loaded custom policy or default `XrdBwmPolicy1`, starts the logger, and registers policy/logger with `XrdBwmHandle`. `xpol` supports either `maxslots in out` or `lib path [params]`.

State and persistence: mutates singleton fields: auth library/parameters, logger object, policy library/parameters, slot counts, trace mask, and authorization/policy pointers. No data persists outside process memory.

Dependencies and integration points: uses `XrdOucStream`, `XrdOuca2x`, `XrdOucPinLoader`, XrdAcc default authorization, BWM policy plugin entry point `XrdBwmPolicyObject`, and XRootD logging.

Risks: if no config file is specified, it logs an error but continues with defaults because the `if` lacks braces around the `else` pairing style but is syntactically intentional. Custom policy loader object lifetime is subtle; unloading is avoided when objects must remain valid. `xlog` accepts program/socket/log targets but validation is deferred.

Test signals: no-config defaults, invalid config file, each directive, bad slot values, default policy creation, custom policy/auth load failures, trace option accumulation/off, and logger startup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.cc -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.cc

Purpose: manages lifecycle of BWM request handles, including scheduling, async dispatch, cancellation, completion logging, and handle reuse.

Important APIs/types/functions: static `XrdBwmHandle::Policy`, `Logger`, `Free`, `numQueued`; local `XrdBwmHandleCB` callback/error object pool; `Activate`, public/private `Alloc`, `Dispatch`, `refHandle`, `Retire`, and `setPolicy`.

Control flow: `Activate` calls `Policy->Schedule`. Positive returns immediately dispatch and optionally return visa data; zero fails; negative means queued, so it captures the client callback, installs `myEICB`, records the handle in a hash table, and returns `SFS_STARTED`. `Dispatch` runs in a dedicated thread, blocks on `Policy->Dispatch`, resolves queued handles, waits for callback handoff, marks dispatched/error, and calls the original callback. `Retire` calls `Policy->Done`, removes scheduled refs if needed, emits logger event, frees strings, and returns the object to the pool.

State and persistence: handle objects are pooled in array chunks. Active queued handles are indexed in 256 buckets by policy reference id. Each handle owns duplicated LFN/local/remote strings and timing/counter fields. State is volatile only.

Dependencies and integration points: depends on `XrdBwmPolicy`, `XrdBwmLogger`, XrdSfs async callback/error APIs, XProtocol status codes, and trace macros.

Risks: concurrency is delicate: callback replacement, `myEICB.Wait`, and ref-table removal must remain ordered. `refID % 256` can be negative if custom policies return negative ids incorrectly. Object pooling intentionally never frees arrays. Logger counters `xSize/xTime` are never updated in this file.

Test signals: immediate schedule success, queue then dispatch, queued cancellation before dispatch, dispatch failure, lost handle simulation, logger event fields, and repeated allocation/reuse under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.hh -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.hh

Purpose: declares the request handle abstraction connecting BWM file operations to the scheduling policy and optional logger.

Important APIs/types/functions: `HandleState` values `Idle`, `Scheduled`, `Dispatched`; public `Activate`, `Alloc`, `Dispatch`, `Name`, `Retire`, `setPolicy`; private static allocator/ref-table helpers; `XrdBwmPolicy::SchedParms Parms`; callback fields `ErrCB` and `ErrCBarg`; inner `theEICB` semaphore callback used to synchronize async handoff.

Control flow: file open allocates a handle in `Idle`; `fctl` calls `Activate`; dispatch thread calls static `Dispatch`; close/destructor calls `Retire`.

State and persistence: per-handle state tracks policy status, request parameters, queue/run times, size/time counters, and policy reference handle. Static state tracks the active policy/logger and free handles.

Dependencies and integration points: includes `XrdBwmPolicy.hh`, `XrdOucErrInfo`, and XRootD pthread wrappers. The callback design is tied to SFS async error information.

Risks: the handle carries raw pointers for string fields and external callback pointers, so ownership discipline is enforced only in implementation. `Name()` assumes `Parms.Lfn` is valid unless called on dummy/uninitialized handles.

Test signals: API lifecycle from allocation through activation and retirement, callback wait/post behavior, policy registration, and use with dummy handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.cc -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.cc

Purpose: asynchronously emits BWM scheduling events to the server log, a FIFO/named socket, or an external collector program.

Important APIs/types/functions: local `XrdBwmLoggerMsg` message blocks; `XrdBwmLoggerSend` thread trampoline; constructor/destructor; `Event`, `sendEvents`, `Start`, `Feed`, `getMsg`, and `retMsg`.

Control flow: `Start` interprets target `*` as server log, `>path` as FIFO/socket path created by `XrdNetSocket`, otherwise sets up and starts an `XrdOucProg`. It then starts a sender thread. `Event` formats an XML-ish `<stats id="bwm">` message from `Info`, queues it, and posts a semaphore. `sendEvents` drains the queue and writes to the selected sink. Message blocks are recycled with a bounded in-flight cap.

State and persistence: persistent process state includes target string, program/socket fd, message queues, free pool, thread id, and queue counters. Events are not durably stored by this class; persistence depends on the sink.

Dependencies and integration points: uses XrdOucProg for collector programs, XrdNetSocket FIFO support, XrdSys threading/synchronization, and XrdSysError logging.

Risks: formatted XML has `<sz>%lld<sz>` instead of a closing `</sz>`, likely producing malformed messages. `Start` initializes `msgFD` to 0 in constructor, so destructor may close stdin if not started carefully. Queue overflow drops events with throttled warnings. Program feed blocking is isolated to sender thread but still can build queue pressure.

Test signals: target modes (`*`, `>socket`, program), queue overflow warning, sender thread shutdown, malformed XML regression, collector backpressure, and destructor resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.hh -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.hh

Purpose: declares BWM event logging, including the event payload shape and asynchronous delivery state.

Important APIs/types/functions: `XrdBwmLogger::Info` contains identity, LFN, local/remote nodes, arrival/begin/complete times, policy queue counts, transfer size/time, and flow direction. Public methods are `Event`, `Prog`, `sendEvents`, and `Start`.

Control flow: callers create a logger from a target string, call `Start`, then call `Event` when a request retires. Delivery is done by `sendEvents` in a background thread.

State and persistence: header exposes internal queue and free-list members, thread id, sink handles, EOL mode, and cap `maxmInQ = 256`. No disk persistence is guaranteed.

Dependencies and integration points: uses `XrdSysPthread` and forward-declares message/program/error classes. Used by `XrdBwmConfig` and `XrdBwmHandle`.

Risks: all event string fields are raw `const char *`; callers must keep them valid through formatting. Public `sendEvents` is thread entry API rather than an intended external control point.

Test signals: compile against handle/config, Info field mapping, target string preservation from `Prog`, and queue cap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy.hh -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy.hh

Purpose: defines the abstract scheduling policy interface for BWM and the C entry point contract for external policy plugins.

Important APIs/types/functions: pure virtual `Dispatch`, `Done`, `Schedule`, and `Status`; enum `Flow {Incoming, Outgoing}`; `SchedParms` request descriptor; external `XrdBwmPolicyObject(XrdSysLogger *, const char *, const char *)`.

Control flow: `Schedule` handles a new request and returns positive for immediate dispatch, zero for failure, or negative for queued. `Dispatch` blocks until a queued request can run or must fail. `Done` releases active resources or cancels queued requests. `Status` reports queue/active counts.

State and persistence: none in the abstract base, but the contract requires active/queued request identity stability while a handle is live.

Dependencies and integration points: custom policy shared libraries implement this interface and are loaded by `XrdBwmConfig.cc`. `XrdBwmHandle` relies on exact sign semantics and id reuse rules documented here.

Risks: policy implementers must preserve `abs(handle)` identity across negative/positive returns; violations can lose handles or leak resources. Response buffers are caller-owned and size-limited, but the interface trusts implementers to respect `RespSize`.

Test signals: contract tests for custom policies: immediate, queued, failed, dispatch failure, cancellation, active completion, status counts, and response-buffer bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.cc -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.cc

Purpose: implements the built-in simple slot-count BWM policy with separate incoming and outgoing concurrency limits.

Important APIs/types/functions: constructor initializes slot counts and `refID`; `Dispatch` waits for queued work and moves it to executing; `Done` releases active slots or cancels queued refs; `Schedule` grants, queues, or rejects requests; `Status` reports counts.

Control flow: `Schedule` creates a `refReq`, decrements available slots and adds to Xeq when capacity exists, queues when capacity is exhausted but max slots are nonzero, or rejects when that direction is disabled. `Dispatch` checks incoming first, then outgoing, and waits on `pSem` if no queued request can run. `Done` removes from active first and posts the semaphore if a slot becomes newly available.

State and persistence: all state is in `theQ[In/Out/Xeq]`, the semaphore, mutex, and monotonically increasing `refID`. There is no persistence.

Dependencies and integration points: implements `XrdBwmPolicy` for default use by `XrdBwmConfig`.

Risks: `refSch::Add` appears to link new nodes through `rP->Next = Last`, which creates a reverse/backward chain while `Next()` consumes from `First`; after more than one queued element, traversal/order behavior is suspect. `refID` can overflow. Incoming always has dispatch priority over outgoing.

Test signals: maxslots zero rejection, immediate grant, FIFO behavior for multiple queued requests, cancellation from queued/active lists, semaphore wakeups on slot release, and status count accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.hh -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.hh

Purpose: declares the default BWM scheduling policy and its queue data structures.

Important APIs/types/functions: `XrdBwmPolicy1` overrides `Dispatch`, `Done`, `Schedule`, and `Status`; enum `Flow {In, Out, Xeq, IOX}` indexes internal queues; `refReq` stores reference id and direction; nested `refSch` stores queue head/tail, count, current slots, max slots, and `Add`, `Next`, `Yank`.

Control flow: the header models three queues: incoming queued, outgoing queued, and executing. Slots are consumed from direction queues and represented in Xeq until `Done`.

State and persistence: process-local queue state under `pMutex`, wakeups through `pSem`, and an integer `refID`. No persistent state.

Dependencies and integration points: inherits from `XrdBwmPolicy` and uses XRootD mutex/semaphore wrappers. Constructed from `bwm.policy maxslots`.

Risks: queue helper methods are inline and central to correctness; any linking error affects policy fairness and handle cancellation. No copy/move protections are declared, but policy objects are intended singleton-like.

Test signals: direct unit tests of `refSch::Add/Next/Yank`, policy construction with different slot counts, and concurrent schedule/done behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmTrace.hh

Purpose: defines trace macros and bit flags for BWM diagnostics.

Important APIs/types/functions: external `BwmTrace`; macros `GTRACE`, `TRACES`, `FTRACE`, `XTRACE`, `ZTRACE`, `DEBUG`, `EPNAME`; flags `TRACE_ALL`, `TRACE_calls`, `TRACE_delay`, `TRACE_sched`, `TRACE_tokens`, `TRACE_debug`.

Control flow: in non-`NODEBUG` builds, macros check `BwmTrace.What` and emit prefixed messages through `XrdOucTrace`; in `NODEBUG`, they compile away.

State and persistence: trace state is the global `BwmTrace.What` mask set by env/config. No persistence.

Dependencies and integration points: used across BWM implementation and configured by `xtrace` in `XrdBwmConfig.cc`.

Risks: tracing expressions can reference local variables such as `oh`, `tident`, and `epname`, so macro use must match expected context. Debug-only code can hide compile issues in `NODEBUG` permutations.

Test signals: build with and without `NODEBUG`, trace option mapping, and representative trace output for calls/delay/sched/tokens/debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdCeph/CMakeLists.txt

Purpose: defines conditional Ceph support targets, including the Ceph POSIX helper library, main XrdCeph OSS plugin, and xattr plugin.

Important APIs/types/functions: checks `ENABLE_CEPH`, `FORCE_ENABLED`, and `find_package(ceph)`; sets `BUILD_CEPH`; builds `XrdCephPosix`, module `XrdCeph-${PLUGIN_VERSION}`, and module `XrdCephXattr-${PLUGIN_VERSION}`; links `RADOS_LIBS`, `XrdUtils`, and `XrdServer`; exports RADOS include paths.

Control flow: if Ceph is disabled or unavailable without force, it unsets `BUILD_CEPH` and returns. Otherwise targets are declared and installed.

State and persistence: build-system state only. Runtime persistence is in Ceph/RADOS and plugin behavior outside this file.

Dependencies and integration points: integrates librados/ceph detection with XRootD plugin modules. The buffer sources researched here are part of the main XrdCeph module.

Risks: build behavior changes substantially with `FORCE_ENABLED`; missing Ceph packages disable plugin silently unless forced. The buffer code is compiled only when the main module builds, so standalone tests need matching include/link setup.

Test signals: configure with Ceph disabled, optional missing, forced missing, and present; verify target names, link libraries, include dirs, SOVERSION for `XrdCephPosix`, and installed modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.cc

Purpose: implements shared Ceph buffer utilities: extent math, extent holder aggregation, debug logging lock, and RAII nanosecond timer.

Important APIs/types/functions: global `cephbuf_iolock` under debug; `Extent::in_extent`, `isContiguous`, `allInExtent`, `someInExtent`, `containedExtent`, comparison operators; `ExtentHolder` constructors/destructor, `push_back`, `asExtent`, byte accounting, sorting/copy helpers; `Timer_ns` constructor/destructor.

Control flow: extents model half-open ranges `[begin,end)`. `ExtentHolder::push_back` maintains aggregate begin/end as extents are added. Sorting returns by offset and then end. Timer captures start time and writes elapsed nanoseconds on destruction.

State and persistence: utility objects are in-memory only. `cephbuf_iolock` serializes debug log writes process-wide.

Dependencies and integration points: used by Ceph buffer algorithms, IO adapters, and readv adapters. Depends on STL containers, chrono, mutex, and algorithm.

Risks: `Extent::in_extent` uses `pos > begin()` rather than `pos >= begin()`, excluding the first byte, unlike other methods. `ExtentHolder(const ExtentContainer&)` iterates over `m_extents` instead of the input `extents`, so it copies nothing; this affects readv conversion shortcuts. `convert` users need sorted input, but not all constructors enforce sorting.

Test signals: boundary tests for extent inclusion, contained subranges, holder copy construction, bytes missing with overlaps/gaps, sorting, and timer value update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.hh

Purpose: declares common helpers used by the Ceph buffering layer.

Important APIs/types/functions: debug macro `BUFLOG`; `Timer_ns`; `Extent`; `ExtentContainer`; `ExtentHolder`. `Extent` exposes range predicates and subset extraction. `ExtentHolder` exposes aggregate range, contained/missing byte accounting, sorting, and copies of extents.

Control flow: classes are simple value/RAII utilities. `BUFLOG` builds a string under a mutex and writes to `std::clog` when `CEPHBUFDEBUG` is defined.

State and persistence: no persistent state beyond the debug mutex declared externally. `ExtentHolder` caches `m_begin` and `m_end` as extents are pushed.

Dependencies and integration points: included by all buffer/readv concrete classes and interfaces. It is part of the XrdCeph module, not a public installed API in this file.

Risks: `CEPHBUFDEBUG` is hard-defined to `1`, meaning debug logging is always compiled and can be noisy/expensive. Comments mention future xrootd logging integration. The range math uses `off_t + size_t` conversions, so overflow should be considered for very large offsets.

Test signals: compilation in debug/non-debug variant if macro changes, thread-safe logging smoke test, and all extent/holder behavior used by readv merging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.cc

Purpose: implements a Ceph IO adapter using XrdCeph asynchronous POSIX calls internally, but waits synchronously for completion before returning.

Important APIs/types/functions: local callbacks `aioReadCallback` and `aioWriteCallback`; `CephBufSfsAio` constructor, `doneRead`, `doneWrite`; `CephIOAdapterAIORaw` constructor/destructor, `read`, and `write`.

Control flow: `read`/`write` obtain the raw buffer, create a `CephBufSfsAio`, fill `sfsAio` buffer/offset/length, call `ceph_aio_read` or `ceph_aio_write`, then wait on the condition variable until callback marks done. On read success, buffer length, starting offset, and validity are updated.

State and persistence: holds non-owned buffer pointer, file descriptor, and timing/byte/request counters. Data persistence happens through Ceph writes, not this class.

Dependencies and integration points: depends on `XrdCephPosix.hh` async APIs, `XrdSfsAio`, `Timer_ns`, and `IXrdCephBufferData`. Used as an `ICephIOAdapter`.

Risks: `CephBufSfsAio` constructs `unique_lock` locked; callbacks unlock it from another thread, which is not valid ownership for `std::unique_lock` and is a serious concurrency risk. Counters add negative `rc` values after write failures. Timing units mix nanoseconds and milliseconds in atomic fields/logging.

Test signals: async read/write success, submit failure, callback error result, race/deadlock tests under thread sanitizer, zero-byte operations, and buffer metadata updates after read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.hh

Purpose: declares the AIO-backed raw Ceph adapter and its blocking AIO helper object.

Important APIs/types/functions: `CephBufSfsAio` derives from `XrdSfsAio` and overrides `doneRead`, `doneWrite`, `Recycle`; exposes mutex, unique lock, condition variable, and `isDone`. `CephIOAdapterAIORaw` implements `ICephIOAdapter::read/write`.

Control flow: callers use the same synchronous adapter interface as raw IO; the implementation uses callbacks and condition variables internally.

State and persistence: adapter state is non-owned buffer pointer, fd, timing/byte counters. `CephBufSfsAio` owns synchronization state for one operation.

Dependencies and integration points: includes XrdSfs AIO interface, buffer interfaces, and utilities. It is interchangeable with `CephIOAdapterRaw` at the algorithm layer.

Risks: synchronization fields are public and unusual; `unique_lock` as a member invites ownership misuse. Buffer pointer ownership is explicitly not taken, so construction order and lifetime matter.

Test signals: header ABI compatibility with XrdSfsAio, construction/destruction, read/write override dispatch through `ICephIOAdapter`, and lifetime tests where buffer outlives adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.cc

Purpose: implements the synchronous raw Ceph IO adapter using XrdCeph POSIX-style pread/pwrite functions.

Important APIs/types/functions: constructor stores non-owned buffer and fd; destructor logs aggregate stats; `write` calls `ceph_posix_pwrite`; `read` calls `ceph_posix_maybestriper_pread`.

Control flow: `write` validates raw const buffer, times the pwrite, updates write counters on success, and returns the byte count/error. `read` validates mutable raw buffer, performs possibly striperless pread, logs errors, updates counters, and marks the buffer length/starting offset/valid on success.

State and persistence: adapter accumulates runtime counters and writes through to Ceph for persistence. It does not own the buffer or fd.

Dependencies and integration points: depends on `XrdCephPosix.hh`, `IXrdCephBufferData`, and `BUFLOG`. Used by `XrdCephBufferAlgSimple`.

Risks: no capacity check before reading into the buffer; callers must keep `count <= capacity`. Destructor write-speed guard checks `m_stats_read_timer` instead of `m_stats_write_timer`, which can suppress or skew write speed. Atomic counters are logged directly and unit math appears inconsistent.

Test signals: null buffer returns `-EINVAL`, successful read metadata, read error logging, pwrite success/error, striperless flag behavior, and destructor stats with read-only/write-only workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.hh

Purpose: declares the synchronous Ceph POSIX IO adapter used by the buffer algorithm.

Important APIs/types/functions: `CephIOAdapterRaw` implements `ICephIOAdapter`; constructor accepts `IXrdCephBufferData *`, fd, and `useStriperlessReads`; overrides `write(off64_t,size_t)` and `read(off64_t,size_t)`.

Control flow: the adapter expects callers to fill or consume the associated buffer object and then call adapter read/write against Ceph offsets.

State and persistence: stores non-owned buffer pointer, fd, striperless-read flag, and stats counters. Persistent data effects occur through Ceph writes.

Dependencies and integration points: includes buffer interfaces, `ICephIOAdapter`, `BufferUtils`, chrono/memory/atomic. It provides the low-level storage bridge for `XrdCephBufferAlgSimple`.

Risks: no ownership semantics are encoded in types; a dangling buffer pointer would be fatal. Stats fields are not all atomic (`longest` values), so concurrent use may race unless externally serialized.

Test signals: construction with valid/invalid buffer, polymorphic use via `ICephIOAdapter`, and concurrent read/write behavior when used behind the algorithm mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/ICephIOAdapter.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/ICephIOAdapter.hh

Purpose: defines the minimal storage IO interface used by Ceph buffer algorithms.

Important APIs/types/functions: abstract destructor; pure virtual `write(off64_t offset, size_t count)` writes from the associated buffer to Ceph; pure virtual `read(off64_t offset, size_t count)` reads from Ceph into the associated buffer.

Control flow: implementations hide whether IO is synchronous, AIO-backed, striperless, or otherwise. The buffer algorithm only asks to load/flush buffer contents by offset and byte count.

State and persistence: no state in the interface. Implementations are responsible for buffer association and persistent writes.

Dependencies and integration points: includes `IXrdCephBufferData.hh` and is consumed by `IXrdCephBufferAlg`/`XrdCephBufferAlgSimple`.

Risks: the interface does not expose buffer capacity or ownership, so safety relies on implementation/caller discipline. Return convention is POSIX-like `ssize_t` but not documented for partial writes.

Test signals: mock implementations for algorithm tests, partial/error return handling, and replacement of raw adapter with AIO adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/ICephIOAdapter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferAlg.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferAlg.hh

Purpose: declares the high-level buffering algorithm interface used by XrdCeph buffered file code.

Important APIs/types/functions: pure virtual `read_aio`, `write_aio`, synchronous `read`, `write`, and `flushWriteCache`.

Control flow: callers can route synchronous or XrdSfsAio operations through one abstraction. Implementations decide when to cache, bypass, flush, or translate AIO to sync behavior.

State and persistence: no interface state. Persistent effects come from implementation write/flush behavior.

Dependencies and integration points: includes `IXrdCephBufferData`, `ICephIOAdapter`, and forward-declares `XrdSfsAio`. Implemented by `XrdCephBufferAlgSimple`.

Risks: `read` takes `volatile void *`, which forces casts in implementation and may obscure const/threading intent. `flushWriteCache` must be called by owners before close/destruction to avoid data loss; the interface cannot enforce it.

Test signals: mock algorithms for file layer tests, AIO callback completion, flush-on-close behavior, and error propagation from implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferAlg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferData.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferData.hh

Purpose: defines the physical buffer memory abstraction for Ceph buffering.

Important APIs/types/functions: capacity/length accessors, validity flag accessors, starting offset accessors, `invalidate`, `readBuffer`, `writeBuffer`, and raw const/mutable memory accessors.

Control flow: algorithms use this interface to copy client bytes into/out of a buffer and adapters use `raw()` to pass the backing memory to Ceph IO calls.

State and persistence: no state in the interface. Implementations track memory, current valid data length, and external offset mapping.

Dependencies and integration points: used by IO adapters and algorithms; implemented by `XrdCephBufferDataSimple`.

Risks: raw pointer access bypasses bounds checking, so adapter and algorithm count values must be consistent with `capacity`. `writeBuffer` includes both local offset and external offset, which can be confusing when the algorithm separately tracks `m_bufferStartingOffset`.

Test signals: generic contract tests for capacity, invalidation, bounds checking, raw pointer availability, and offset/length semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferData.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephReadVAdapter.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephReadVAdapter.hh

Purpose: defines the abstraction for converting many readv extents into larger combined read requests.

Important APIs/types/functions: pure virtual `convert(const ExtentHolder &)` returns `std::vector<ExtentHolder>`, where each output holder represents one merged read and contains the original constituent extents.

Control flow: caller translates readv requests into extents, invokes a concrete adapter, then maps combined read data back to original readv segments.

State and persistence: no interface state. Implementations may keep stats, as `XrdCephReadVBasic` does.

Dependencies and integration points: depends on `BufferUtils.hh` for `ExtentHolder`; used by XrdCeph readv-capable file code.

Risks: the interface does not preserve original readv indices, so caller-side ordering/mapping must be reliable. Header includes `<iostream>` with a FIXME, adding unnecessary compile dependency.

Test signals: mock conversion behavior, empty input, unsorted input, overlap/gap cases, and caller mapping back to readv slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephReadVAdapter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.cc

Purpose: implements a simple single-buffer read/write cache for XrdCeph files.

Important APIs/types/functions: constructor/destructor; `read_aio`, `write_aio` translate AIO to synchronous operations and complete callbacks; `read` handles cache hits/fills and large-read bypass; `write` buffers sequential writes; `flushWriteCache` writes pending data through the adapter; `rawRead/rawWrite` are unimplemented.

Control flow: `read` locks a recursive mutex, bypasses the cache for reads at least as large as capacity, otherwise loops until requested bytes are satisfied or EOF, loading the cache via `m_cephio->read` when the current offset is outside cached data. `write` requires sequential offsets once data is buffered, writes chunks into the buffer, flushes when full, and leaves partial data cached until explicit flush. AIO methods call sync methods and then `doneRead`/`doneWrite`.

State and persistence: owns buffer data and IO adapter via `unique_ptr`, tracks fd, striperless flag, cache starting offset/length, recursive mutex, and byte stats. Dirty write data is only persisted when the buffer fills or `flushWriteCache` is called.

Dependencies and integration points: depends on `IXrdCephBufferData`, `ICephIOAdapter`, XrdCeph POSIX bypass reads, and XrdSfsAio. Intended for `XrdCephOssBufferedFile`.

Risks: callers must flush partial writes before close to avoid data loss. Large-read bypass uses direct `ceph_posix_maybestriper_pread` instead of the adapter, bypassing adapter instrumentation/policy. `volatile void *` casts and recursive mutex indicate interface friction. Non-sequential writes return `-EINVAL`.

Test signals: cache hit/miss, read across buffer boundary, EOF short reads, large-read bypass, sequential writes with full/partial flush, non-sequential write error, AIO completion, and concurrent access serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.hh

Purpose: declares the simple Ceph buffer algorithm concrete class.

Important APIs/types/functions: constructor takes owned `IXrdCephBufferData` and `ICephIOAdapter`, fd, and striperless flag; overrides AIO and sync read/write plus `flushWriteCache`; exposes `buffer()` accessors for review/testing; protected `rawRead/rawWrite` placeholders.

Control flow: public API matches `IXrdCephBufferAlg`; implementation serializes buffer access and controls cache fill/flush.

State and persistence: owns cache memory and IO adapter, tracks fd, buffer range, mutex, and usage stats. Persistent writes are deferred until flush.

Dependencies and integration points: includes interfaces and utilities. It is built into the XrdCeph module and selected by buffered file implementation.

Risks: ownership is mixed with the adapter: comment says no ownership for `m_cephio`, but the type is `unique_ptr`, so it does own it. Exposing mutable `buffer()` can break invariants if external callers modify state without the algorithm mutex.

Test signals: constructor ownership/destruction, buffer accessor invariants, flush semantics, and use with mock IO adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.cc

Purpose: implements a `std::vector<char>` backed buffer data object for Ceph buffering.

Important APIs/types/functions: static global memory counters; constructor/destructor; capacity/length/valid/offset accessors; `invalidate`; `readBuffer`; `writeBuffer`; raw accessors are inline in the header.

Control flow: construction allocates a zero-filled vector and marks the buffer valid. `readBuffer` validates state and bounds, copies up to available data from internal offset to caller buffer, and returns bytes copied. `writeBuffer` validates bounds, copies bytes into the internal vector at local offset, updates external offset, length, and validity.

State and persistence: stores buffer size, validity, vector memory, external offset, valid length, per-object counters, and static aggregate memory counters. No persistence outside memory.

Dependencies and integration points: uses `Timer_ns` and `BUFLOG`; implements `IXrdCephBufferData` for the simple algorithm and raw adapters.

Risks: destructor `clear` plus `reserve(0)` does not guarantee memory release; `shrink_to_fit` would be clearer if immediate release matters. Constructor marks an empty buffer valid, though length is zero. Timing counters are declared but not updated. `writeBuffer` external offset may be redundant/inconsistent with algorithm tracking.

Test signals: construct/destruct memory counters, zero capacity raw pointer, read invalid buffer, read beyond length, write bounds failures, length growth after writes, and invalidate reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.hh

Purpose: declares a simple vector-backed implementation of `IXrdCephBufferData`.

Important APIs/types/functions: constructor with buffer capacity; overrides capacity, length, validity, starting offset, invalidate, read/write buffer methods, and raw pointer accessors. Static atomics track total memory and live buffer count.

Control flow: algorithms/adapters treat this class as the physical cache storage. Inline `raw()` returns `&m_buffer[0]` only when capacity is nonzero.

State and persistence: per-buffer vector, length, validity, external offset, timer/counter fields, plus static aggregate counters. No disk persistence.

Dependencies and integration points: includes `IXrdCephBufferData`, `BufferUtils`, STL vector/atomic/chrono. Used by the XrdCeph buffered file stack.

Risks: no internal locking; callers must serialize access. Capacity is a separately stored `m_bufferSize`, so vector capacity/size divergence would matter if changed. Static counters are useful for diagnostics but not exposed through a stable API.

Test signals: polymorphic behavior through `IXrdCephBufferData`, raw pointer stability, capacity/length semantics, and thread-safety assumptions under algorithm locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferDataSimple.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.cc -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.cc

Purpose: implements a basic readv extent combiner that groups small reads into larger contiguous Ceph reads.

Important APIs/types/functions: destructor logs aggregate used/wasted bytes; `convert` transforms one `ExtentHolder` into a vector of grouped `ExtentHolder` reads.

Control flow: `convert` obtains input extents, sets left/right iterators, shortcuts to one combined holder if total range is below `m_minSize`, otherwise groups consecutive extents until the aggregate range would exceed `m_maxSize`, recording useful and wasted bytes. Stats accumulate across calls.

State and persistence: keeps only aggregate used/wasted byte counters. No persistent state.

Dependencies and integration points: uses `Extent`, `ExtentHolder`, and `BUFLOG`; used by XrdCeph readv file code to reduce many small reads.

Risks: it dereferences `it_end->end()` even though `it_end` equals `extentsIn.end()`, an invalid iterator. The shortcut copy relies on `ExtentHolder(const ExtentContainer&)`, which currently copies from the wrong container. Input is not sorted here, so grouping quality depends on caller ordering. The destructor percentage formula divides by `totalBytes*100` instead of multiplying by 100.

Test signals: empty input, one extent, total below min size, grouping above max size, unsorted extents, iterator sanitizer tests, and stats accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.hh -->
# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.hh

Purpose: declares the default/basic readv adapter for XrdCeph.

Important APIs/types/functions: `XrdCephReadVBasic` implements `IXrdCephReadVAdapter::convert`; configurable member defaults are `m_minSize = 2 MiB` and `m_maxSize = 16 MiB`; counters `m_usedBytes` and `m_wastedBytes` track efficiency.

Control flow: convert groups input extents into larger requests constrained by the min/max sizes, leaving remapping to the caller.

State and persistence: in-memory stats only, logged on destruction.

Dependencies and integration points: includes `BufferUtils.hh` and `IXrdCephReadVAdapter.hh`. Compiled into the XrdCeph module as one readv strategy.

Risks: size thresholds are protected members, not constructor parameters, so tuning requires subclassing/source edits. No explicit requirement that input extents are sorted is documented in the interface.

Test signals: conversion behavior around 2 MiB and 16 MiB thresholds, counter accumulation, destructor logging, and use through base adapter pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.hh -->
