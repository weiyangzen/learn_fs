# subset-b-007915 research

This grouped report covers the requested XRootD `XrdApps` tools, copy configuration helpers, client proxy plugin, and record/replay plugin files. Each file section is wrapped with the exact reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAccTest.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdAccTest.cc

Purpose: implements `xrdacctest`, a command-line and interactive harness for testing XRootD authorization policy decisions. It loads the default access authorization object, builds an `XrdSecEntity`, then asks whether operations on one or more paths are allowed or which privilege bits apply.

Important APIs/types/functions: global `Authorize` is an `XrdAccAuthorize`; `Entity` is the mutable `XrdSecEntity` under test; `optab` maps short operation names to `Access_Operation`; `Usage()` prints accepted identity and operation syntax; `SetID()` updates optional identity strings; `ZapEntity()` resets identity fields; `main()` parses global options and initializes `XrdAccDefaultAuthorizeObject()`; `DoIt()` parses per-command identity updates and performs access checks; `cmd2op()` maps operation tokens; `PrivsConvert()` converts `XrdAccPrivCaps` to compact privilege letters.

Control flow: startup sets `Entity.addrInfo`, a synthetic trace identity, exports `XRDINSTANCE`, and initializes the authorization object from `-c` config. If arguments remain, one request is executed. Otherwise stdin is read line-by-line with simple quote handling, parsed into tokens, and sent through `DoIt()`. `DoIt()` accepts either legacy positional `<user> <host>` identity or v2 `-a/-e/-g/-h/-o/-r/-u` identity options, handles `*` as identity reset, maps the operation, resolves host metadata when present, and prints `allowed`, `denied`, or privilege letters per path.

State/persistence: state is process-local. The global `Entity` persists across interactive commands until reset or overwritten, and `Entity.ueid` is incremented for each interactive line. No files are written.

Dependencies/integration: integrates with `XrdAccAuthorize`, `XrdAccConfig`, `XrdAccPrivs`, `XrdSecEntity`, `XrdNetAddr`, `XrdOucEnv`, and `XrdOucStream`. It depends on the access plugin exported by `XrdAccDefaultAuthorizeObject()`.

Risks/test signals: interactive state reuse can surprise tests unless `*` or explicit identity fields are used. `cmd2op()` returns `AOP_Any` after printing an invalid-operation message, so bad operations may still produce privilege output. Tests should cover v1 and v2 identity forms, `none` clearing, quoted paths, single-shot exit status, invalid operations, host resolution failures, and `?` privilege rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAccTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAppsCconfig.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdAppsCconfig.cc

Purpose: implements `cconfig`, a utility that reads an XRootD configuration file through `XrdOucStream`, evaluates conditional/directive substitution for a selected host/instance/program, optionally filters requested directives, captures the resulting expanded config, and writes it to stdout or a file.

Important APIs/types/functions: `inList()` checks directive names against static exception lists; `cfOut()` writes captured config to `-o` with mode `0644`; `Usage()` prints CLI syntax; `main()` handles `-c`, `-h`, `-n`, `-o`, and `-x`, builds the `XRDINSTANCE`-style stream identity, attaches the config fd to `XrdOucStream`, and drives capture/echo.

Control flow: options are parsed, the host is resolved through `XrdNetAddr`, selector directives are stored in an `XrdOucNList_Anchor`, and the config is opened. Each first word is checked against the optional selector queue. Certain directives in `noSub` are read with environment substitution disabled so message/copy command strings are preserved. Directives in `ifChk` are scanned for `if` and evaluated with `XrdOucUtils::doIf()`, suppressing echo if the condition fails. Everything else consumes the rest of the line and echoes the captured version.

State/persistence: the main state is captured expanded config in an `XrdOucString`. Persistence happens only when `-o` is provided, via truncating write to the chosen output file.

Dependencies/integration: depends on XRootD utility parsing and conditional-expression machinery: `XrdOucStream`, `XrdOucEnv`, `XrdOucNList`, `XrdOucUtils::InstName()`, `XrdOucUtils::doIf()`, `XrdNetAddr`, and `XrdSysError`.

Risks/test signals: directive exception lists are hard-coded and can drift from server config behavior. `cfOut()` returns on write failure without closing the fd on that path. Tests should cover host/name/program selection, directive filtering, `if` evaluation, no-substitution directives, slash scanning for `frm.xfr.copycmd`, output-file errors, and config read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAppsCconfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCks.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCks.cc

Purpose: implements `xrdcks`, a local extended-attribute checksum tool for querying, setting, and deleting XRootD checksum metadata on a file.

Important APIs/types/functions: global `xCS` is an `XrdOucXAttr<XrdCksXAttr>` wrapper; `Stat` stores target file metadata; `Display()` prints checksum name/value and marks stale checksums when recorded file mtime differs; `Unable()` formats xattr/stat errors and exits; `Usage()` documents `path cksname [cksval|delete]`; `main()` validates checksum name/value, stats the file, and calls `Get()`, `Set()`, or `Del()`.

Control flow: arguments are checked, the checksum type is validated with `xCS.Attr.Cks.Set(name)`, and the operation is selected from the optional third argument. Query reads the xattr, verifies that the stored checksum type matches the requested type, and displays it. Delete removes the xattr. Set parses a hex value, stamps current file mtime into `fmTime`, clears `csTime`, and writes the xattr.

State/persistence: persists checksum metadata in filesystem extended attributes through `XrdOucXAttr`. It also embeds the file mtime in the xattr so later query can report stale metadata.

Dependencies/integration: integrates `XrdCksXAttr`, `XrdOucXAttr`, POSIX `stat()`, and local filesystem xattr support.

Risks/test signals: query mode appears to have an argument-count defect: after accepting exactly `path cksname`, the code still enters the `else` branch and reads `argv[3]`, which is out of bounds for `argc == 3`. The `strncmp("0x", csVal, 2)` branch also advances non-`0x` strings instead of `0x`-prefixed strings, which looks inverted. Tests should cover query with two operands, delete, set with and without `0x`, invalid checksum names/lengths, stale mtime display, missing xattr, and filesystems without xattr support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.cc

Purpose: implements the runtime behavior of the XrdCl proxy-prefix file plugin. It wraps an `XrdCl::File`, rewrites the URL passed to `Open()` by prepending a proxy prefix, and delegates all later file operations to the wrapped file object.

Important APIs/types/functions: `ProxyPrefixFile::Open()` rejects double-open, creates `XrdCl::File(false)`, calls `ConstructFinalUrl()`, and opens the rewritten URL; `GetPrefixUrl()` reads `XROOT_PROXY` then `xroot_proxy`; `trim()` removes leading/trailing spaces from exclusion tokens; `GetExclDomains()` parses `XROOT_PROXY_EXCL_DOMAINS`; `ConstructFinalUrl()` applies suffix exclusion checks and prepends the prefix; `GetFqdn()` canonicalizes hostnames with `getaddrinfo()`.

Control flow: `Open()` is the only operation with plugin-specific behavior. URL construction reads environment, parses the original URL host with `XrdCl::URL`, strips any port, canonicalizes the host, checks comma-separated exclusion suffixes, and conditionally inserts the prefix at the start of the original URL.

State/persistence: `mIsOpen` and `pFile` are in-memory state. Configuration is read from environment variables every time a URL is constructed; no persistent files are written.

Dependencies/integration: depends on `XrdCl::File`, `XrdCl::URL`, `XrdCl::DefaultEnv` logging, POSIX environment variables, and DNS canonicalization through `getaddrinfo()`.

Risks/test signals: `trim()` dereferences iterators before checking empty strings, so empty exclusion tokens can be unsafe. The suffix exclusion guard compares exclusion length to `url_prefix.size()` instead of the origin host length, risking incorrect matches or reverse-iterator overrun when an exclusion is longer than the host. DNS canonicalization can block or fail, in which case the raw host is used. Tests should cover empty/missing prefix, uppercase/lowercase env names, exclusion suffixes, hosts with ports, unresolved hosts, double open, and URL rewrite logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.hh

Purpose: declares `xrdcl_proxy::ProxyPrefixFile`, an `XrdCl::FilePlugIn` implementation that intercepts `Open()` to apply proxy-prefix rewriting and forwards the normal XrdCl file API to a contained `XrdCl::File`.

Important APIs/types/functions: overrides include `Open`, `Close`, `Stat`, `Read`, `PgRead`, several `Write` overloads, `PgWrite`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, `IsOpen`, `SetProperty`, and `GetProperty`. Private helpers are `trim()`, `GetPrefixUrl()`, `GetExclDomains()`, `ConstructFinalUrl()`, and `GetFqdn()`. Members are `mIsOpen` and raw pointer `pFile`.

Control flow: the header defines a mostly transparent delegation layer; all operations except `Open()` assume `pFile` has already been allocated by a successful or attempted open.

State/persistence: owns `pFile` and deletes it in the implementation destructor. There is no durable state.

Dependencies/integration: integrates with `XrdClPlugInInterface`, `XrdClDefaultEnv`, `XrdCl::Buffer`, `ChunkList`, page IO APIs, vector IO APIs, and property propagation on `XrdCl::File`.

Risks/test signals: most methods dereference `pFile` without null checks, so calling operations before `Open()` can crash instead of returning `errInvalidOp`. `mIsOpen` is maintained separately from `pFile->IsOpen()` and is not visibly reset on close. Tests should exercise operation-before-open behavior, close/reopen expectations, all overloaded write paths, property forwarding, and ABI compatibility with the `FilePlugIn` interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.cc

Purpose: exports the XrdCl plugin entry point and implements `ProxyFactory`, which creates proxy-prefix file plugins and maps plugin configuration values into environment variables consumed by `ProxyPrefixFile`.

Important APIs/types/functions: `XrdVERSIONINFO(XrdClGetPlugIn, XrdClGetPlugIn)` publishes version metadata; extern "C" `XrdClGetPlugIn(const void*)` casts the config map and returns `new ProxyFactory`; `ProxyFactory::ProxyFactory()` reads selected keys and calls `setenv(..., overwrite=0)`; `CreateFile()` returns a new `ProxyPrefixFile`; `CreateFileSystem()` logs unsupported status and returns null.

Control flow: plugin loading calls `XrdClGetPlugIn()`, construction optionally exports `XROOT_PROXY`, `xroot_proxy`, `XROOT_PROXY_EXCL_DOMAINS`, and `xroot_proxy_excl_domains` if present and non-empty, then XrdCl asks the factory for per-URL file plugins.

State/persistence: mutates process environment, intentionally not overwriting existing variables. No filesystem persistence.

Dependencies/integration: integrates with the XrdCl plugin loader ABI, `XrdVersion`, `XrdCl::PlugInFactory`, `XrdCl::DefaultEnv` logging, and `ProxyPrefixFile`.

Risks/test signals: using process-wide environment variables means multiple plugin instances or concurrent users share configuration. Lowercase `xroot_proxy_excl_domains` is exported but `ProxyPrefixFile::GetExclDomains()` reads only uppercase `XROOT_PROXY_EXCL_DOMAINS`, so lowercase exclusion config is ineffective. Tests should cover config-to-env mapping, no-overwrite behavior, factory creation, unsupported filesystem plugin, and mixed upper/lowercase config keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.hh

Purpose: declares `xrdcl_proxy::ProxyFactory`, the XrdCl plugin factory for creating `ProxyPrefixFile` instances.

Important APIs/types/functions: `ProxyFactory` derives from `XrdCl::PlugInFactory`; it has a config-map constructor, virtual destructor, `CreateFile(const std::string&)`, and `CreateFileSystem(const std::string&)`.

Control flow: XrdCl plugin loading constructs this factory through the exported C symbol in the `.cc` file; callers then request file plugins per URL. The header does not store config state.

State/persistence: no data members and no durable state; all side effects are implemented in the constructor in the `.cc` file.

Dependencies/integration: depends on `XrdCl/XrdClPlugInInterface.hh` and the XrdCl plugin factory lifecycle.

Risks/test signals: the factory ignores the URL parameter when creating files and does not support filesystem plugins. Tests should compile against the current `PlugInFactory` virtual signatures and verify file plugin construction through the exported loader path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClAction.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClAction.hh

Purpose: defines the serializable action model used by the XrdCl recorder plugin. Each operation type captures its request arguments, timing, status, and optional response summary for later replay.

Important APIs/types/functions: base `Action` stores file id, timeout, start/stop times, `XRootDStatus`, and serialized response; `RecordResult()` records completion state; `time()` and `timeNow()` produce Unix seconds with nanosecond precision; `ToString()` emits a quoted CSV row. Derived actions include `OpenAction`, `CloseAction`, `StatAction`, `ReadAction`, `PgReadAction`, `WriteAction`, `PgWriteAction`, `SyncAction`, `TruncateAction`, `VectorReadAction`, `VectorWriteAction`, and `FcntlAction`.

Control flow: the recorder creates a specific action before submitting an async operation. On callback, `RecordResult()` captures the status/response and `ToString()` serializes the row as `id,name,start,args+timeout,stop,status,response`.

State/persistence: action instances are transient, but their `ToString()` output is persisted by `Recorder::Output`. The file id is the recording plugin object's pointer cast to `uint64_t`, making it a per-process correlation key rather than a stable identity.

Dependencies/integration: depends on `XrdClXRootDResponses` response types such as `StatInfo`, `ChunkInfo`, `PageInfo`, and `VectorReadInfo`, plus XrdCl flag/mode/chunk types used by replay parsing.

Risks/test signals: CSV escaping is minimal and assumes arguments/status/response do not contain embedded quotes that need escaping. `ToString()` trims trailing spaces from `status.ToString()` by calling `ststr.back()`, which assumes a non-empty status string. `TruncateAction` stores a `uint64_t` argument into a `uint32_t size` member. Tests should verify every action's argument format round-trips through `XrdClReplay`, response serialization for null responses, large truncate sizes, vector chunk ordering, and status string formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClAction.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClActionMetrics.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClActionMetrics.hh

Purpose: defines `XrdCl::ActionMetrics`, the replay-side accumulator for operation timing, byte counts, IOPS, errors, offsets, synchronicity, and human/json reporting.

Important APIs/types/functions: constructor seeds `delays` and `ios` maps for Open/OpenR/OpenW/Read/Write/Stat/Close/PgRead/PgWrite/Truncate/Sync/VectorRead/VectorWrite; `Dump(bool json)` renders per-file or summary metrics; getters aggregate read/write IOPS and bytes; `addDelays()` and `addIos()` are mutex-protected for async callbacks; `add()` combines another metric and tracks read/write synchronicity; `humanreadable()` formats byte counts; nested `synchronicity_t` averages read and write groups.

Control flow: replay initializes one metrics object per file and one summary. Action executors update counters before submission and update measured time/error counters from callbacks. After threads complete, metrics are optionally dumped individually, aggregated, and included in the final summary.

State/persistence: in-memory only. It stores maps keyed by string metric names and vectors of per-file synchronicity percentages for summary aggregation.

Dependencies/integration: integrates with `XrdClReplay.cc` callback paths, `Action` timing semantics, C++ mutexes, maps, vectors, and JSON/text output code.

Risks/test signals: JSON rendering manually removes the last comma by seeking backward, which can misbehave if no metrics were emitted for an object. Map key typos become user-facing metric names. Tests should cover empty metrics, json/text output with per-file and summary modes, async concurrent updates, read/write classification in `add()`, and human-readable byte thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClActionMetrics.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorder.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorder.hh

Purpose: implements the XrdCl recorder file plugin. It wraps `XrdCl::File`, records supported file operations and their asynchronous responses, and writes CSV rows for replay and analysis.

Important APIs/types/functions: nested singleton `Output` owns the CSV fd and serialized writes; `Output::Instance()` opens the output lazily; `Output::Write()` writes a complete action row under lock; `Recorder::RecordHandler` wraps user response handlers and records callback results; `Recorder::SetOutput()` selects `XRD_RECORDERPATH`, config path, or `/tmp/xrdrecord.csv`; operation overrides create the matching `Action` subclass and submit the wrapped call with a `RecordHandler`.

Control flow: factory code calls `SetOutput()`, construction binds `output` to `Output::Instance()`, and each intercepted async operation allocates an `Action` plus self-deleting `RecordHandler`. When XrdCl completes the request, the handler records status/response, writes CSV, forwards the callback to the original handler when present, and deletes itself.

State/persistence: persistent output is the CSV file. It is opened with `O_CREAT|O_WRONLY|O_TRUNC`, so first open truncates prior content. `Output` is a process singleton shared by all recorder instances and protected by a mutex. Each `Recorder` owns one `XrdCl::File`.

Dependencies/integration: depends on `XrdCl::FilePlugIn`, `XrdCl::File`, `ResponseHandler`, `DefaultEnv` logging, POSIX `open/write/close`, and action classes from `XrdClAction.hh`.

Risks/test signals: `Output::IsValid()` checks `fd > 0`, so a valid fd `0` would be treated invalid, though normal opens usually produce fd 3+. If `file.Open()` or another operation returns immediate failure without invoking the response handler, the allocated `RecordHandler` may leak and no action row is written. Visa and property operations are not recorded. Tests should cover output path precedence, failed output open, concurrent operations writing complete rows, immediate submission failures, null user handlers, and each recorded operation's callback forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorder.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.cc

Purpose: provides the C ABI entry point used by XrdCl to load the recorder plugin.

Important APIs/types/functions: includes `XrdClRecorder.hh` and `XrdClRecorderPlugin.hh`; `XrdVERSIONINFO(XrdClGetPlugIn, XrdClGetPlugIn)` exposes version metadata; extern "C" `XrdClGetPlugIn(const void*)` casts the config pointer to `std::map<std::string,std::string>` and returns a new `XrdCl::RecorderFactory`.

Control flow: XrdCl dynamically loads the shared library, resolves `XrdClGetPlugIn`, passes plugin config, and receives a factory that can create recorder file plugins.

State/persistence: this file has no state beyond allocating the factory. Output-file state is configured by the factory/header implementation.

Dependencies/integration: integrates with the XrdCl plugin loader ABI, `XrdVersion`, and `RecorderFactory`.

Risks/test signals: the entry point assumes the opaque config pointer, when non-null, has the expected map type. Tests should validate dynamic loading, version symbol availability, null config handling, and factory lifetime cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.hh

Purpose: declares and mostly implements `XrdCl::RecorderFactory`, the plugin factory that configures recorder output and creates `Recorder` file plugins.

Important APIs/types/functions: constructor reads config key `output` and calls `Recorder::SetOutput()`; `CreateFile()` constructs a `Recorder`, checks `IsValid()`, and returns it as `FilePlugIn`; `CreateFileSystem()` logs unsupported status and returns null.

Control flow: plugin load constructs the factory. The first created recorder triggers singleton output opening through `Recorder` construction. Invalid output setup causes `CreateFile()` to return null instead of a plugin.

State/persistence: no members in the factory. It causes process-global recorder output path state to be set through `Recorder::SetOutput()`.

Dependencies/integration: depends on `XrdClPlugInInterface` and on `Recorder` being visible from `XrdClRecorder.hh` before this header's inline constructor and `CreateFile()` are compiled.

Risks/test signals: output configuration is global, so multiple factory instances with different output paths can race or override before output opens. `CreateFileSystem()` uses `Log` and `DefaultEnv` names that must be available through included XrdCl headers. Tests should cover missing `output`, invalid paths, returning null on invalid output, and unsupported filesystem plugin reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplay.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplay.cc

Purpose: implements `xrdreplay`, a tool that reads recorder CSV output, optionally rewrites arguments, replays or simulates the captured XrdCl operations with original timing, and reports per-file and aggregate IO metrics. It can also create or verify input datasets implied by read samples.

Important APIs/types/functions: `BufferPool` limits replay buffer memory via `XRD_MAXBUFFERSIZE`; `mytimer_t` measures elapsed time; `barrier_t` posts semaphores when async operations complete; `AssureFile()` verifies or creates files for read datasets; `ActionExecutor` parses action arguments and submits XrdCl file operations; `ToColumns()` parses quoted CSV rows; `ParseInput()` groups rows by original file id into per-file action timelines; `ExecuteActions()` runs one file timeline in a thread; `main()` coordinates parse, replay, reporting, dataset create/verify, and exit status.

Control flow: input rows are parsed into columns, optional regex replacements are applied to the argument field, file ids are mapped to new `XrdCl::File(false)` instances, unsuccessful recorded rows are counted, and successful rows become `ActionExecutor` entries ordered by start time. Unless print/simulate mode is active, per-file threads sleep until each recorded relative start time adjusted by `--speed`, submit async operations, and use semaphores to avoid exiting before final callbacks. Main joins all threads and prints long, summary, json, or dataset assurance output.

State/persistence: replay itself persists no normal output files except when `--create` or `--truncate` creates remote/local files via XrdCl operations. In-memory state includes per-file action lists, metrics, response error counts, buffers, and file objects.

Dependencies/integration: integrates with XrdCl high-level operation wrappers (`Open`, `Read`, `Write`, `VectorRead`, etc.), `XrdCl::File`, `XrdCl::Utils::splitString`, `XrdSysSemaphore`, `ActionMetrics`, and `ReplayArgs`.

Risks/test signals: the CSV parser is custom and does not implement general CSV escaping. Regex replacement validates token count after indexing `tokens[0]`, so malformed replacement strings are risky. `GetVectorReadArgs()` reserves `tokens.size()-1`, which underflows for empty args. JSON summary has metric copy/paste errors (`PgRead::n` used for pgwrite and `VectorRead::n` for vectorwrite) and a misspelled `bandwdith` key. Non-json write bandwidth prints read bytes. Tests should cover CSV rows with quoted fields, unsuccessful sample suppression, print versus replay timing, speed scaling, memory cap blocking/reclaim, vector operations, dataset creation/verification, json summary values, and callback status mismatch accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplay.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplayArgs.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplayArgs.hh

Purpose: defines `XrdCl::ReplayArgs`, the option parser and accessors for `xrdreplay`.

Important APIs/types/functions: constructor parses `--help`, `--print`, `--create`, `--truncate`, `--long`, `--json`, `--summary`, `--replace`, `--suppress`, `--verify`, and `--speed`; `usage()` prints help and exits; accessors expose booleans, speed, regex replacements, and optional input path.

Control flow: `getopt_long()` populates option flags. Create/truncate imply print/simulated mode. JSON enables long and summary output. Verify forces print mode and disables create/truncate/json. At most one positional path is accepted; otherwise stdin is used.

State/persistence: stores parsed options in memory only. No durable state.

Dependencies/integration: used by `XrdClReplay.cc`; depends on `getopt_long`, `std::vector`, `std::string`, and `strtod`.

Risks/test signals: the short usage text contains typos, and the short option string includes `r:` and `x:` while long options accept required args. The condition `if (option_json && (option_long || option_summary)) option_long = option_summary = true;` only promotes JSON when one of long/summary was already set, despite main's JSON output expecting structured sections. Tests should cover option interactions, invalid speed values, repeated `--replace`, stdin input, too many positional arguments, verify overriding create/json, and JSON with no explicit long/summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplayArgs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.cc

Purpose: implements `XrdCpConfig`, the main command-line configuration parser and validator for `xrdcp`-style copy operations.

Important APIs/types/functions: static `opLetters` and `opVec` define short/long options; constructor initializes defaults; destructor releases file lists, checksum objects, proxy and parameter storage; `Config()` parses options, resolves destination/source files, validates conflicts, reads `--infiles`, and expands recursive local directories; numeric helpers `a2i`, `a2l`, `a2t`, `a2z`, and `a2x` validate values; `defCks()` configures checksum behavior; `defOpq()`, `defOpt()`, and `defPxy()` parse legacy opaque/define/proxy options; `Legacy()` supports old aliases; `ProcFile()` validates each source; `Usage()` prints detailed help.

Control flow: `Config()` allocates a parameter vector, processes legacy and modern options in one loop, applies mode side effects such as server implying silent/nopbar/force, enables make-path from `XRD_MAKEPATH`, then treats the final operand as destination. It resolves local destination metadata, processes sources from CLI and optional input file, enforces source counts and protocol restrictions, validates checksum/TPC/ZIP conflicts, and optionally expands local directories recursively into individual `XrdCpFile` entries.

State/persistence: builds an in-memory linked list of `XrdCpFile` sources and one destination object, stores option bits in `OpSpec`, checksum manager/calculator objects, proxy settings, rate limits, and totals for local files. It reads an input file list when requested but does not write files.

Dependencies/integration: depends on `XrdCpFile`, `XrdCksManager`, `XrdCksCalc`, `XrdCksData`, `XrdOucStream`, `XrdSysError`, `XrdSysE2T`, `getopt_long`, and XRootD version/license headers.

Risks/test signals: the ZIP/checksum conflict checks use bitwise `&` chains such as `OpSpec & DoZip & DoCksrc`, which do not test both flags as intended because the flag constants do not overlap. Error handling exits directly, making unit tests need process-level harnesses. `a2z()` reports invalid byte rates as "not a valid time." Tests should cover every option, legacy aliases, invalid numeric bounds, proxy parsing, checksum modes including `auto` and additional source checksums, TPC qualifiers, server/silent side effects, `--infiles`, recursive expansion, local/local rejection, stdin restrictions, remote recursive policy, ZIP conflicts, and environment-driven make-path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.hh

Purpose: declares the `XrdCpConfig` data model, option bit constants, parser entry point, and private helpers used by `xrdcp` configuration processing.

Important APIs/types/functions: nested `defVar` stores legacy `-DI`/`-DS` definitions; public fields expose parsed destination/source opaque strings, program name, rate limits, parallelism, proxy host/port, option mask, debug/verbose flags, source/stream counts, retry policy, checksum state, file lists, ZIP path, and additional checksums. `Want()` tests option bits. Constants define `Do*` flags and option ids for checksum, force, recursion, TPC, TLS, xattr, ZIP, continue, retry policy, and more. `Config()` is the public parser.

Control flow: consumers construct `XrdCpConfig`, call `Config(argc, argv, Opts)`, then inspect public fields and linked file lists to drive copy execution. Private methods implement validation and parsing details.

State/persistence: all state is process-local and owned by the object; destructor frees linked lists and helper objects. No persistence is declared here.

Dependencies/integration: forward-declares `XrdCks`, `XrdCksCalc`, `XrdCpFile`, and `XrdSysError`; includes `XrdCksData`; exposes option flags consumed by the copy application.

Risks/test signals: the class exposes many mutable public fields, so invariants depend on callers not mutating parsed state inconsistently after `Config()`. `OpSpec` is a 64-bit mask with both character option ids and bit flags nearby, making new-option allocation error-prone. Tests should assert default constructor values, destructor ownership, `Want()` behavior, unique bit assignments, and compatibility of public fields with downstream copy code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.cc

Purpose: implements `XrdCpFile`, a small parsed-file descriptor used by `xrdcp` configuration to classify source/destination operands, resolve local metadata, and expand recursive local directories.

Important APIs/types/functions: constructor parses protocols and normalizes paths; alternate constructor wraps filesystem-walk entries; `Extend()` recursively indexes local files under a directory using `XrdOucNSWalk`; `Resolve()` stats local paths and classifies regular files, directories, `/dev/null`, and `/dev/zero`; static `mPfx` controls namespace-walk message prefix.

Control flow: construction strips trailing slashes except root-like forms, treats `-` as stdio, recognizes xroot/xroots/root/roots/http/https/dav/davs/pelican/s3 URLs, handles `file://localhost` and absolute `file://` paths, and defaults other strings to local files. `Resolve()` temporarily removes a CGI query suffix for `stat()`, restores it, and updates protocol/size. `Extend()` walks a directory recursively and appends each returned regular file to a linked list.

State/persistence: stores mutable `Path`, directory offset/length metadata, protocol enum, protocol name, file size, and `Next` pointer. It reads filesystem metadata but writes nothing.

Dependencies/integration: used by `XrdCpConfig`; depends on POSIX `stat`, path string handling, and `XrdOucNSWalk` for recursive local indexing.

Risks/test signals: `ProtName[8]` is too short to store longer protocol names such as `pelican` plus terminator if copied elsewhere, though constructor copies header length minus delimiter. Local CGI stripping mutates `Path` temporarily and assumes restoration on the success/failure path. Tests should cover URL protocol classification, file URL host forms, trailing slash normalization, stdio, directories, special devices, local paths with `?`, recursive expansion offsets, and unsupported file types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.hh

Purpose: declares the `XrdCpFile` linked-list node used to represent parsed copy operands for `xrdcp`.

Important APIs/types/functions: `PType` enumerates `isOther`, `isDir`, `isFile`, `isStdIO`, `isXroot`, `isXroots`, `isHttp`, `isHttps`, `isPelican`, `isS3`, `isDevNull`, and `isDevZero`; public fields include `Next`, `Path`, `Doff`, `Dlen`, `Protocol`, `ProtName`, and `fSize`; methods are `Extend()`, `Resolve()`, `SetMsgPfx()`, constructors, and destructor.

Control flow: callers create nodes while parsing operands, call `Resolve()` for local paths, optionally call `Extend()` for recursive directories, then traverse the `Next` chain to schedule copy work.

State/persistence: owns `Path` memory and frees it in the destructor. No durable state.

Dependencies/integration: integrated with `XrdCpConfig` and copy execution code that interprets directory-offset fields when constructing destination paths.

Risks/test signals: public mutable fields permit accidental ownership or protocol changes. The linked-list ownership model requires exactly one owner to delete each node. Tests should verify constructors initialize all fields, destructor frees duplicated paths but not externally moved namespace-walk paths incorrectly, and recursive path metadata is preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCrc32c.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCrc32c.cc

Purpose: implements `xrdcrc32c`, a standalone utility that computes a CRC32C checksum for a local file or stdin and prints it in hexadecimal.

Important APIs/types/functions: `Fatal()` reports system errors and exits; `Usage()` prints CLI help; `main()` parses `-d`, `-h`, `-n`, `-s`, and `-x`, opens the input, allocates a page-aligned 1 MiB buffer, streams reads through `XrdOucCRC::Calc32C()`, and prints the checksum with optional path/newline formatting.

Control flow: options set `O_DIRECT`, output formatting, path inclusion, and newline inclusion. If the operand is absent or `-`, stdin is used. Otherwise the file is opened read-only. The loop updates `csVal` until EOF, then errors are checked and output is emitted.

State/persistence: no persistent state. It reads input data and writes checksum text to stdout.

Dependencies/integration: depends on `XrdOucCRC`, `XrdSysE2T`, POSIX `open/read`, `posix_memalign`, and page-size alignment. `O_DIRECT` is defined as zero on platforms that lack it.

Risks/test signals: direct IO can impose alignment and filesystem constraints even though the buffer is aligned; file offsets and read sizes are fixed at 1 MiB. The allocated buffer is not freed on error exits. Tests should cover stdin, file input, direct mode, no-newline/no-path/no-leading-zero formatting, read/open errors, empty files, and known CRC32C vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCrc32c.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMapCluster.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdMapCluster.cc

Purpose: implements `xrdmapc`, a diagnostic utility that starts at an XRootD manager node, maps manager/server topology through locate requests, optionally locates/verifies a path, and prints text or JSON output.

Important APIs/types/functions: `clMap` represents managers/servers and links manager, server, and recursive levels; global flags control manager/server listing, verification, quiet mode, JSON, path, and timeout; `MakeURL()` builds `xroot://host//`; `MapCode()` translates XrdCl/XRootD errors into display state and file verification markers; `MapCluster()` recursively locates subscribers; `MapPath()` marks nodes that locate a target path; `PathChk()` stats the path on a server; `PrintMap()` and `PrintJson()` render output; `SetEnv()` tunes XrdCl connection settings; `main()` parses options and orchestrates mapping.

Control flow: after validating the initial `<host>:<port>` with `XrdNetAddr`, the program creates a base node, applies XrdCl environment defaults, and calls `MapCluster()`. Cluster mapping issues `Locate("*")`, splits returned locations into servers and managers, hashes them by address, and recurses into managers. If a path is supplied, `MapPath()` locates it from the base and recursively through managers; `--verify` additionally stats each listed server during text printing. Finally text or JSON is emitted, with warnings for located path nodes not connected to the discovered topology.

State/persistence: all topology data is heap-allocated in linked `clMap` objects and an `XrdOucHash`. The tool writes only stdout/stderr diagnostics.

Dependencies/integration: integrates with `XrdCl::FileSystem::Locate/Stat`, `LocationInfo`, `XrdNetAddr`, `XrdOucHash`, XRootD protocol error codes, and XrdCl default environment settings (`ConnectionWindow`, `ConnectionRetry`, `TimeoutResolution`).

Risks/test signals: recursive topology discovery has no explicit cycle guard beyond hash storage not being consulted before recursing, so cyclic manager graphs can duplicate work or recurse deeply. Some `state` strings are heap-allocated with `strdup()` and never freed, acceptable for a short-lived tool but visible in leak tests. JSON output is hand-built without escaping host/state strings. Tests should cover option parsing, invalid initial nodes, locate errors, no-subscriber handling, manager-only/server-only listings, JSON suppression of stderr, path locate and refresh, verification states, phantom nodes, and cyclic/duplicate manager responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMapCluster.cc -->
