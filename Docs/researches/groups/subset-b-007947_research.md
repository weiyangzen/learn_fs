# subset-b-007947 Research

Grouped source research for XRootD OFS third-party-copy coordination and default OSS storage-system APIs. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.cc

## Purpose

`XrdOfsTPC.cc` implements the high-level OFS third-party-copy control path. It validates TPC CGI/environment fields, enforces configured authentication and path restrictions, creates origin-side authorization grants, creates destination-side copy jobs, exports runtime feature flags, and ties configuration in `XrdOfsTPCConfig` to `XrdOfsTPCAuth`, `XrdOfsTPCJob`, and `XrdOfsTPCProg`. The source was read as a complete 699-line implementation.

## Important APIs, Types, and Functions

The file defines static `XrdOfsTPC` methods: `AddAuth`, `Allow`, `Authorize`, `Init`, `Require`, `Restrict`, `Start`, `Validate`, plus helpers `Death`, `Fatal`, `genOrg`, `getTTL`, `Screen`, and `Verify`. It owns the `XrdOfsTPCParms` globals `fcAuth`, `fcNum`, `tpcOK`, `encTPC`, `tpcMon`, and `Cfg`, and defines the private allow-list class `XrdOfsTPCAllow`. Static authorization lists include `AuthDst`, `AuthOrg`, `ALList`, `RPList`, `fsAuth`, and credential path `cPath`.

## Control Flow

`Start()` finalizes path-restriction defaults, installs a default transfer command of `xrdcp --server` when none is configured, initializes the transfer-program pool, starts the authorization TTL thread, exports `XRDTPC`, and marks TPC as enabled. `Authorize()` handles source-open authorization. If the request has destination and no origin, this server is the origin granting a rendezvous authorization after local read authorization and origin auth screening. If the request has origin and no destination, this server is the destination validating that the origin granted access, checking allow-list host/DN/group/VO restrictions, finding the matching `XrdOfsTPCAuth`, and returning it. `Validate()` handles write-side requests that ask the destination to fetch from a source. It validates delegated credentials, source URL pieces, source LFN semantics, stream count, rendezvous CGI, optional reproxy path, and finally creates an `XrdOfsTPCJob`.

## State and Persistence Behavior

All state is process-local. Authorization requirements, credential-forwarding auth table, allow-list entries, path restrictions, and TPC configuration are static process state. `Validate()` creates heap `XrdOfsTPCJob` instances containing copy metadata, forwarded credentials, and optional reproxy paths. `Death()` and `XrdOfsTPCInfo` cleanup can remove partially created destination files when `Cfg.autoRM` is enabled. No durable database is maintained; rendezvous state lives in the in-memory auth queue.

## Dependencies and Integration Points

The file integrates with `XrdAccAuthorize` for read authorization, `XrdSecEntity` identity fields, `XrdOucTPC` CGI helpers, `XrdOucEnv` request environment, `XrdOucPList`/`XrdOucTList` restrictions, `XrdOss` file cleanup, `XrdOfsStats`, `OfsEroute`, `OfsTrace`, and the TPC helper classes. It exports `XRDTPC` and `XRDTPCDLG` environment signals consumed by xrootd clients and transfer tooling.

## Risks and Edge Cases

Security depends on exact CGI interpretation and canonical destination host matching. Allow-list matching is sensitive to identity fields and host DNS behavior. URL construction can fail on long LFN/CGI inputs. Delegated credential handling checks for GSI private-key material when required, but optional credentials can silently fall back to rendezvous tokens. `autoRM` cleanup uses `Args.Lfn` in one path even when comments refer to PFNs, so deletion behavior must be reviewed when path translation changes.

## Test Signals

Useful tests include origin and destination TPC handshakes; encrypted-auth requirement failures; allow-list host/DN/group/VO accept and reject cases; oversized CGI/LFN validation; delegated-credential required, optional, and GSI cases; `tpc.streams` clamping; reproxy path export; and `autoRM` failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.hh

## Purpose

`XrdOfsTPC.hh` declares the base OFS TPC object and its static control interface. It is the shared contract used by authorization objects, queued copy jobs, and OFS open/sync paths that need a polymorphic TPC handle.

## Important APIs, Types, and Functions

The central type is `class XrdOfsTPC`, containing public `XrdOfsTPCInfo Info`, virtual `Del()` and `Sync()`, and nested request context `Facts` with key, LFN, PFN, origin, destination, user security entity, error object, and environment. Static APIs configure and operate TPC: `AddAuth`, `Allow`, `Authorize`, `credPath`, `Init`, `Require`, `Restrict`, `Start`, and `Validate`. `reqALL`, `reqDST`, and `reqORG` select which side an auth requirement applies to.

## Control Flow

This header has no executable flow, but it defines the call graph shape. OFS request code creates `Facts`, calls `Authorize()` for source-open rendezvous validation or `Validate()` for destination write-side copy setup, then later calls virtual `Sync()` and `Del()` on the returned object.

## State and Persistence Behavior

Instances carry a reference count (`Refs`) and queue flag (`inQ`), while static members carry process-wide auth requirements, allow lists, path restrictions, credential path, and access-authorizer pointer. The state is in-memory and lifetime-managed by `Del()` implementations in derived classes.

## Dependencies and Integration Points

The header depends on `XrdOfsTPCInfo` and forward-declares OFS, OUC, ACC, and SEC types to keep compile coupling low. It is included by `XrdOfsTPCAuth` and `XrdOfsTPCJob`, and the `Facts` structure is the narrow bridge from OFS request parsing into TPC logic.

## Risks and Edge Cases

`Refs` and `inQ` are `char`, which is compact but risky if lifetime rules change or unusually many references are added. Because `Facts` stores borrowed pointers, callers must keep request strings, environment, error object, and security entity valid through the immediate call.

## Test Signals

Compile tests should cover inclusion from auth/job/prog implementations. Behavioral tests should exercise base-pointer deletion, waiting `Sync()` paths, and static configuration setup before and after `Start()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.cc

## Purpose

`XrdOfsTPCAuth.cc` implements in-memory TPC rendezvous authorization. It lets an origin publish a grant, lets a destination fetch or wait for that grant, rejects duplicate/mismatched requests, expires stale entries, and replies asynchronously to clients blocked in wait-response.

## Important APIs, Types, and Functions

Implemented methods are `XrdOfsTPCAuth::Add`, `Del`, `Expired`, `Find`, `Get`, and `RunTTL`. Static state is `authMutex` and linked-list head `authQ`. The external thread entry `XrdOfsTPCAuthttl` invokes `RunTTL(0)`.

## Control Flow

`Add()` is called by the origin side. It builds the canonical origin ID, checks for a matching pending destination request, replies to that callback if present, or stores a new grant in `authQ`. `Get()` is called by the destination side. It removes a matching grant and returns it, rejects duplicate pending requests, or creates a pending callback entry and returns `SFS_STARTED`. `RunTTL(1)` starts the background TTL thread; `RunTTL(0)` loops forever scanning `authQ`, expiring entries, notifying callbacks, updating stats, and sleeping until the next expiration.

## State and Persistence Behavior

All authorization grants and pending requests are heap objects linked through `authQ`. Each object has an expiration time, inherited reference state, callback state in `Info`, and copied rendezvous strings. Entries are removed on match, delete, duplicate handling, or TTL expiry. Nothing persists across process restart.

## Dependencies and Integration Points

This implementation uses `XrdOfsTPCInfo` for matching and callbacks, `XrdOfsStats` for grant/expiry/error counters, `XrdSysMutex` for serialization, `XrdSysThread` for the TTL thread, `XrdSysTimer` for sleeping, and `XrdSfsInterface` return codes.

## Risks and Edge Cases

Duplicate authorization handling is security-sensitive: a duplicate grant without a pending callback is treated as protocol error, while duplicate pending destination requests are rejected and notified. `RunTTL()` sleeps based on `Cfg.maxTTL`; invalid zero or tiny TTL configuration could create noisy wakeups. `Del()` deletes under `authMutex`, so future destructor changes must avoid lock-order cycles.

## Test Signals

Tests should cover origin-before-destination, destination-before-origin, duplicate origin, duplicate destination, expiration with and without callbacks, reference-counted delete after successful `Get()`, and TTL thread startup failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.hh

## Purpose

`XrdOfsTPCAuth.hh` declares the authorization-grant object used by TPC rendezvous. It derives privately from `XrdOfsTPC` and specializes the base object for grant lookup, pending callback, TTL expiration, and queue membership.

## Important APIs, Types, and Functions

Public methods are `Add(Facts&)`, `Del()`, inline `Expired()`, detailed `Expired(const char*, int)`, static `Get(Facts&, XrdOfsTPCAuth**)`, and static `RunTTL(int)`. Private static `Find()` searches/removes from the global auth queue. Members are `Next` and `expT`; static members are `authMutex` and `authQ`.

## Control Flow

The header defines a two-sided flow: origins construct an object and call `Add()`, while destinations call `Get()` to consume or wait for a matching object. Expiration is driven by `RunTTL()`.

## State and Persistence Behavior

Each object persists in memory until matched, explicitly deleted, or expired. The expiration timestamp is computed from constructor TTL plus current time. Queue and reference state are inherited from `XrdOfsTPC`.

## Dependencies and Integration Points

The header includes `XrdOfsTPC.hh` and `XrdSysPthread.hh`, making it part of the OFS TPC synchronization layer. It is consumed by `XrdOfsTPC.cc` during authorization and by `XrdOfsTPCAuth.cc` for implementation.

## Risks and Edge Cases

Private inheritance means callers normally interact through static methods or base casts in implementation files; accidental API expansion may expose surprising conversion rules. Expiry uses wall-clock `time(0)`, so clock adjustments can extend or shorten grants.

## Test Signals

Compile coverage should check consumers can forward-declare or include it cleanly. Runtime tests should assert that `Expired()` flips at expected times and that delete/reference behavior is correct around matched grants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCConfig.hh

## Purpose

`XrdOfsTPCConfig.hh` defines the configuration structure shared by TPC authorization, validation, and transfer-program execution. It centralizes defaults and flags for the OFS TPC subsystem.

## Important APIs, Types, and Functions

The exported type is `struct XrdOfsTPCConfig`. Fields include monitor pointer `tpcMon`, transfer program `XfrProg`, checksum type `cksType`, credential path `cPath`, reproxy path format `rPath`, TTLs `maxTTL`/`dflTTL`, stream defaults and maxes, concurrent transfer max `xfrMax`, error monitor level `errMon`, and booleans `LogOK`, `doEcho`, `autoRM`, `noids`, and `fCreds`.

## Control Flow

There is no executable control flow beyond the constructor. Runtime flow reads this struct from `XrdOfsTPC`, `XrdOfsTPCAuth`, `XrdOfsTPCInfo`, and `XrdOfsTPCProg` to decide authorization lifetime, transfer command setup, stream count, logging, monitoring, credential export, and cleanup.

## State and Persistence Behavior

The configuration is a process-lifetime object in `XrdOfsTPCParms::Cfg`. It stores owned or borrowed C strings allocated by the surrounding configuration parser; the destructor intentionally does nothing because the global is never deleted.

## Dependencies and Integration Points

It forward-declares `XrdXrootdTpcMon` and otherwise stays standalone. It is the integration point between xrootd config parsing and the TPC runtime files in this subset.

## Risks and Edge Cases

Defaults are behaviorally significant: `maxTTL=15`, `dflTTL=7`, `xfrMax=9`, and `noids=true` affect security and concurrency even when config is sparse. Because string ownership is not documented by the struct itself, config-parser changes must preserve lifetime assumptions.

## Test Signals

Configuration tests should verify default transfer behavior, TTL clamping, stream clamping, monitor activation, `autoRM`, `fCreds`, and reproxy format expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.cc

## Purpose

`XrdOfsTPCInfo.cc` implements the metadata container shared by TPC auth grants and transfer jobs. It owns copied rendezvous strings, destination paths, callback objects, forwarded credentials, checksum/protocol options, and cleanup behavior.

## Important APIs, Types, and Functions

Implemented methods are destructor, `Fail`, `Match`, `Reply`, `Set`, and `SetCB`. Inline setters and flags are declared in the header. `Set()` canonicalizes destination host names with `XrdNetAddr`; `Reply()` safely detaches and completes `XrdOucCallBack` objects.

## Control Flow

`Set()` replaces key/origin/LFN/destination/checksum fields and validates destination host resolution. `Match()` compares nullable key, origin, LFN, and destination fields exactly. `SetCB()` creates an async callback from `XrdOucErrInfo`; `Reply()` clears the callback pointer, optionally unlocks a passed mutex before invoking the callback, and only replies if `Engage()` marked the object as in wait-response state. `Fail()` formats a copy error and updates stats.

## State and Persistence Behavior

The object owns heap copies of strings and credentials and deletes its callback in the destructor. If marked as destination (`isDST`) and not successful (`isAOK`), the destructor can unlink the destination LFN when `Cfg.autoRM` is enabled. Callback state is one-shot: `Reply()` nulls `cbP` before unlocking or invoking user-visible completion.

## Dependencies and Integration Points

It integrates with `XrdOucCallBack`, `XrdOucErrInfo`, `XrdNetAddr`, `XrdOss` cleanup, `OfsEroute`, `XrdOfsStats`, and `XrdSfsInterface` return/error conventions. It is embedded in `XrdOfsTPC`, so all derived TPC objects inherit this state.

## Risks and Edge Cases

Host canonicalization can fail and reject otherwise plausible destination strings. `SetCreds()` overwrites `Crd` without freeing an existing value; current callers set it once, but reuse would leak. `Reply()` correctness depends on callers holding the appropriate serialization lock when passing `mP`.

## Test Signals

Tests should cover nullable field matching, destination canonicalization failures, callback reply with and without wait-response engagement, auto-remove destructor behavior, and failure-stat accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.hh

## Purpose

`XrdOfsTPCInfo.hh` declares the TPC metadata object embedded in every `XrdOfsTPC`. It is the shared storage contract for rendezvous auth and destination copy jobs.

## Important APIs, Types, and Functions

Public methods include `Engage`, `Fail`, `isDest`, `Match`, `Reply`, `Set`, `SetCB`, `SetCreds`, `SetRPath`, `SetStreams`, and `Success`. Public data members include `cbP`, `Cks`, `Key`, `Org`, `Lfn`, `Dst`, `Spr`, `Tpr`, `Rpx`, credential environment/name/data fields, stream count, and state booleans `inWtR`, `isDST`, `isAOK`.

## Control Flow

The header exposes a deliberately direct data model. Callers populate the object during authorization or job creation, mark callbacks as engaged during async waits, and mark success when the transfer completes.

## State and Persistence Behavior

All string/credential data is heap-owned by the object except `Env`, which points to an environment-variable name. Persistence is process-memory only. Destination cleanup behavior is driven by `isDST` and `isAOK`.

## Dependencies and Integration Points

The header includes `XrdOucCallBack.hh` and forward-declares error and mutex types. It is included by `XrdOfsTPC.hh`, making it central to OFS TPC state layout.

## Risks and Edge Cases

Most members are public, so invariants are convention-based rather than enforced by accessors. `Engage()` must be called under a serialization lock per the comment. Public raw pointers increase risk when adding reuse paths.

## Test Signals

Compile and lifecycle tests should exercise construction with optional fields, `Set()` replacement, callback ownership, credential ownership, and destructor cleanup with all optional pointers populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.cc

## Purpose

`XrdOfsTPCJob.cc` implements queued/running/done destination-side TPC copy jobs. It bridges OFS write-open/sync semantics to a bounded pool of external transfer-program workers.

## Important APIs, Types, and Functions

Implemented methods are constructor, `Del`, `Done`, and `Sync`. Static state is `jobMutex`, FIFO head `jobQ`, and tail `jobLast`. Each job stores `Next`, assigned `XrdOfsTPCProg *myProg`, completion `eCode`, `Status`, and optional source-LFN rename positions `lfnPos`.

## Control Flow

`Sync()` is the main entry. If already running, it installs a callback and returns `SFS_STARTED`. If done, it returns success or stored error. If waiting, it tries `XrdOfsTPCProg::Start`; on no worker, it enqueues itself and returns `SFS_STARTED`; on thread creation error, it records a terminal resource failure. `Done()` marks a running job complete, replies to any waiter, pulls the next queued job if present, attaches the freed program to it, and returns that next job to the runner loop. `Del()` removes queued jobs or cancels running jobs and notifies premature-close callbacks.

## State and Persistence Behavior

Jobs live on the heap and are reference-counted with the inherited `Refs`. The queue is process-memory only, serialized by `jobMutex`. Completion text is stored in `Info.Key` when a job fails, reusing the field that previously held the source URL. No copy state persists after object deletion except files created by the transfer, with optional cleanup through `autoRM`.

## Dependencies and Integration Points

The job layer uses `XrdOfsTPCProg` for execution, `XrdOucCallBack` for wait-response behavior, `XrdSfsInterface` return codes, `OfsEroute` logging, and `XrdOfsStats` indirectly through `Info.Fail`.

## Risks and Edge Cases

`Info.Key` changes meaning from source URL to error text after completion, which is compact but easy to misuse. Callback replies intentionally unlock `jobMutex`; lifetime/ref accounting around that path is critical. Queue fairness is FIFO, but only worker completion starts queued jobs.

## Test Signals

Tests should cover immediate start, queued start, running async wait, done success, done failure, cancellation via close, resource failure from thread creation, and FIFO handoff when multiple jobs wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.hh

## Purpose

`XrdOfsTPCJob.hh` declares the destination-side copy-job subtype of `XrdOfsTPC`. It gives OFS a polymorphic object that can be synchronized, deleted, queued, and completed by transfer workers.

## Important APIs, Types, and Functions

Public methods are `Del`, `Done`, `Sync`, the constructor, and destructor. Private state includes global queue mutex/head/tail, per-job next pointer, assigned program, error code, `jobStat` enum (`isWaiting`, `isRunning`, `isDone`), and `lfnPos` rename bookkeeping.

## Control Flow

The header defines the job lifecycle used by `XrdOfsTPCJob.cc`: constructed by `XrdOfsTPC::Validate`, possibly started by `Sync`, completed by `XrdOfsTPCProg::Run`, and cleaned by OFS close paths.

## State and Persistence Behavior

State is in-memory only. Queue membership is represented by inherited `inQ` plus `Next`; lifetime is inherited reference counting.

## Dependencies and Integration Points

It includes `XrdOfsTPC.hh` and `XrdSysPthread.hh`, and forward-declares `XrdOfsTPCProg`. It is used by `XrdOfsTPC.cc` and `XrdOfsTPCProg.cc`.

## Risks and Edge Cases

The header exposes a small API, but lifecycle depends on private static queue invariants. `lfnPos` is set in the constructor but not consumed in the read implementation, so related behavior may depend on other build variants or legacy code.

## Test Signals

Compile tests should verify the derived object can be returned as `XrdOfsTPC *`. Lifecycle tests should validate status transitions and deletion in each state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.cc -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.cc

## Purpose

`XrdOfsTPCProg.cc` implements the bounded pool of external transfer-program runners for OFS TPC jobs. It prepares command arguments/environment, writes temporary delegated-credential files, drains transfer output, reports monitoring data, and returns workers to the idle pool.

## Important APIs, Types, and Functions

Implemented methods are constructor, `ExportCreds`, `Init`, `Run`, `Start`, and `Xeq`. Static state is `pgmMutex` and idle stack `pgmIdle`. Local RAII class `credFile` builds unique credential-file paths and unlinks them on destruction. Thread entry `XrdOfsTPCProgRun` calls `Run()`.

## Control Flow

`Init()` allocates `Cfg.xfrMax` `XrdOfsTPCProg` objects and calls `XrdOucProg::Setup` with `Cfg.XfrProg`. `Start()` pops an idle runner, attaches a job, and starts a thread. `Run()` loops while each completed job hands it another queued job. For each job it calls `Xeq()`, fills monitor timing/URL/client/size data if configured, invokes `Job->Done()`, and finally pushes itself back onto the idle list. `Xeq()` writes credentials if needed, builds `-C` checksum and `-S` stream arguments, exports `XRD_TIDENT`, optional source/target protocol variables, optional `XRD_CPTARGET`, and optional credential env var, starts the external program, drains lines to capture failure text and IPv4 marker, gets the exit code, logs/removes on failure, and marks success on success.

## State and Persistence Behavior

Runners are long-lived heap objects recycled through an idle stack. Threads are per active transfer. Temporary credential files are mode `0600`, named under the configured credential path using origin plus sequence, and unlinked by `credFile`. Transfer success/failure is written back into the job and optional monitor, not persisted elsewhere.

## Dependencies and Integration Points

The file uses `XrdOucProg` and `XrdOucStream` for external process execution, `XrdSysThread`, `XrdSysFD`, `XrdNetIdentity`, `XrdXrootdTpcMon`, `XrdOss` for stat/unlink, and OFS trace/error globals. It is the runtime boundary to `xrdcp --server` or any configured transfer program.

## Risks and Edge Cases

Credential filenames include origin text; any unexpected characters must be tolerated by the filesystem and security policy. The failure-message parser records text after `": "`, so transfer-program output format changes affect user errors. `Start()` leaves the runner attached if thread creation fails until caller handles `rc`; this path needs regression coverage. Monitoring temporarily edits query delimiters in job strings and restores them, so null/malformed strings are important edge cases.

## Test Signals

Tests should cover pool sizing, no-idle queuing, thread creation failure, command argument construction, credential export/unlink, checksum and stream options, reproxy environment, transfer stdout parsing, nonzero exit cleanup, monitor reporting, and cancellation via `JobStream.Drain()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.hh

## Purpose

`XrdOfsTPCProg.hh` declares the worker object that runs an external TPC transfer program for `XrdOfsTPCJob` instances.

## Important APIs, Types, and Functions

Public methods are `Cancel`, static `Init`, `Run`, static `Start`, `Xeq`, constructor, and destructor. Private state includes `ExportCreds`, global idle-list mutex/head, `XrdOucProg Prog`, `XrdOucStream JobStream`, list `Next`, current `Job`, prefix name `Pname`, and error buffer `eRec`.

## Control Flow

The class lifecycle is pool-based: `Init()` creates workers, `Start()` assigns one job and starts a thread, `Run()` executes jobs and recycles the worker, `Cancel()` drains the process stream.

## State and Persistence Behavior

Workers are persistent process-memory pool entries. Per-transfer state is current `Job`, process stream, and error record. No durable persistence is owned by the header contract.

## Dependencies and Integration Points

It includes `XrdOucProg`, `XrdOucStream`, and `XrdSysPthread`, and forward-declares `XrdOfsTPCJob`. It is used exclusively by the TPC job runner implementation and job queue.

## Risks and Edge Cases

Because one object is reused across transfers, `Run()` and `Xeq()` must reset enough per-job state. `Cancel()` only drains the stream; process termination semantics depend on `XrdOucStream`/`XrdOucProg`.

## Test Signals

Compile tests should include the header alongside `XrdOfsTPCJob`. Runtime tests should inspect reuse after success and failure, cancellation, and preservation of error text boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTrace.hh

## Purpose

`XrdOfsTrace.hh` defines trace macros and trace-bit constants for the OFS layer. It gives OFS and TPC code a common way to emit conditional debug traces through `XrdSysTrace`.

## Important APIs, Types, and Functions

When `NODEBUG` is not defined, macros include `GTRACE`, `TRACES`, `FTRACE`, `XTRACE`, `ZTRACE`, `DEBUG`, and `EPNAME`. In debug-disabled builds they compile to no-ops or zero. Trace flags include directory, open/close, read/write/AIO, exists/chmod/getmode/getsize, remove/rename, sync, truncate, fsctl, stats, mkdir, stat, debug, and checkpoint bits.

## Control Flow

The macros wrap trace emission sites: code defines an endpoint with `EPNAME`, tests a category with `GTRACE`, and emits through `SYSTRACE` only when enabled. In `NODEBUG` builds, related control flow is removed at compile time.

## State and Persistence Behavior

No storage is owned here. Runtime state lives in external `OfsTrace.What` and logger configuration.

## Dependencies and Integration Points

The header includes `XrdSysHeaders`, `XrdSysTrace`, and `XrdOfs.hh` in debug builds. TPC program execution uses `EPNAME`/`DEBUG`; other OFS files use file and operation trace categories.

## Risks and Edge Cases

Macro expressions depend on local variables such as `tident`, `epname`, and sometimes `oh`, so misuse can create compile errors only in debug builds. Some trace bits share values by aliases, which is intentional but can confuse filtering.

## Test Signals

Build both debug and `NODEBUG` configurations. Smoke-test trace categories by enabling `debug`, `open`, `read`, `write`, and `aio` and checking logs appear without changing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdOss/CMakeLists.txt

## Purpose

`XrdOss/CMakeLists.txt` wires the default XRootD object storage system implementation into the `XrdServer` target and builds the GPFS stat plugin module.

## Important APIs, Types, and Functions

The file uses `target_sources(XrdServer PRIVATE ...)` to add default OSS sources and headers, then defines `XrdOssSIgpfsT-${PLUGIN_VERSION}` as a `MODULE` library from `XrdOssSIgpfsT.cc`, links it privately to `XrdUtils`, and installs it to `${CMAKE_INSTALL_LIBDIR}`.

## Control Flow

There is no runtime control flow. Build flow adds OSS implementation units such as `XrdOss.cc`, `XrdOssApi.cc`, `XrdOssAio.cc`, path/cache/copy/create/mss/rename/stat/unlink components, and related headers to the server build.

## State and Persistence Behavior

Build state is limited to CMake target membership and generated build-system metadata. No runtime persistence is defined here.

## Dependencies and Integration Points

The list is the integration point between XrdServer and the default OSS subsystem. The GPFS module integrates with plugin loading through XRootD versioned plugin naming.

## Risks and Edge Cases

Omitting a source here can silently remove runtime behavior from `XrdServer`; adding headers as private sources improves IDE visibility but does not compile them. Plugin naming depends on `PLUGIN_VERSION` being defined by the parent build.

## Test Signals

Build tests should verify `XrdServer` links with all OSS objects and that the GPFS module is produced and installed in the expected library directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOss.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOss.cc

## Purpose

`XrdOss.cc` provides default base-class behavior for the generic OSS interfaces in `XrdOss.hh`. It supplies no-op or unsupported virtual methods and generic page-read/page-write/vector helpers for storage plugins that do not override them.

## Important APIs, Types, and Functions

Implemented `XrdOss` methods include `Connect`, `Disc`, `EnvInfo`, `Features`, `FSctl`, `Reloc`, `StatFS`, `StatLS`, `StatPF`, `StatVS`, `StatXA`, and `StatXP`. Implemented `XrdOssDF` helpers include `Fctl`, synchronous/asynchronous `pgRead`, synchronous/asynchronous `pgWrite`, range-list preread `Read`, `ReadV`, and `WriteV`.

## Control Flow

Most `XrdOss` methods return `-ENOTSUP` or no-op defaults. `pgRead()` calls the normal byte `Read()` then computes page checksums into `csvec` when supplied. Async `pgRead`/`pgWrite` perform the synchronous operation into `XrdSfsAio::Result` and call completion callbacks. `pgWrite()` optionally verifies supplied checksums before writing. `ReadV` and `WriteV` iterate vector entries, require full transfer for each entry, and return `-ESPIPE` on short I/O.

## State and Persistence Behavior

The base helpers do not own persistent state. They operate on virtual file objects and may update `XrdSfsAio` result fields. `pgwEOF` exists in the base object but is not modified here.

## Dependencies and Integration Points

The file integrates with `XrdOucPgrwUtils` for page checksum calculation/verification and `XrdSfsAio` for async completion. Storage plugins inherit these defaults unless they advertise and implement more capable behavior.

## Risks and Edge Cases

Default async page operations are synchronous completions, so callers must not assume real asynchronous dispatch unless feature flags and overrides say so. Short vector I/O is treated as `-ESPIPE`, which may differ from POSIX callers' expectations. Checksum verification returns `-EDOM`.

## Test Signals

Tests should cover default unsupported methods, page checksum calculation, checksum verification failure, async completion callbacks, vector full-read/write success, and vector short-I/O failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOss.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOss.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOss.hh

## Purpose

`XrdOss.hh` defines the public XRootD object storage system plugin interface. It specifies per-file/directory object operations (`XrdOssDF`), filesystem-wide operations (`XrdOss`), option/feature flags, plugin entry-point typedefs, and default name-to-name helpers.

## Important APIs, Types, and Functions

`XrdOssDF` declares directory operations (`Opendir`, `Readdir`, `StatRet`), file operations (`Open`, `Clone`, `Fchmod`, `Fstat`, `Fsync`, `Ftruncate`, `getMmap`, `isCompressed`, read/write/async/page/vector methods), common `Close`, `Fctl`, `getErrMsg`, `getFD`, and `getTID`. `XrdOss` declares `newDir`, `newFile`, `Chmod`, `Connect`, `Create`, `Disc`, `EnvInfo`, `Features`, `FSctl`, `Init`, `Mkdir`, `Reloc`, `Remdir`, `Rename`, `Stat`, `Stats`, space/stat/xattr methods, `Truncate`, `Unlink`, and `Lfn2Pfn`. It defines flags such as `XRDOSS_mkpath`, `XRDOSS_new`, `XRDOSS_Online`, feature bits like `XRDOSS_HASPGRW`, and plugin typedefs `XrdOssGetStorageSystem_t`, `XrdOssGetStorageSystem2_t`, and `XrdOssAddStorageSystem2_t`.

## Control Flow

This header contains mostly virtual contracts and inline defaults. Runtime flow is selected by OFS calling into an `XrdOss` instance, obtaining `XrdOssDF` objects, and then invoking directory/file operations through virtual dispatch.

## State and Persistence Behavior

`XrdOssDF` stores trace identity, page-write EOF tracking, file descriptor, and type flags. `XrdOss` itself has no base storage. Concrete implementations decide persistence. Plugin entry points may wrap or replace the native implementation.

## Dependencies and Integration Points

The interface depends on POSIX stat/types, `XrdOssVS`, `XrdOucIOVec`, `XrdOucRange`, and forward-declared OUC/SFS/Sys types. It is the ABI-like boundary for external OSS plugins, default OSS implementation, OFS, proxy/cache layers, and storage wrappers.

## Risks and Edge Cases

This header is a compatibility boundary: changing virtual method order, signatures, flags, or object layout can break plugins. Several defaults return directory/file mismatch errors, so derived classes must override the right methods for their declared `DFType`. Public plugin typedef comments strongly imply version metadata should accompany plugins.

## Test Signals

ABI-sensitive tests include plugin compile/load tests, default method behavior, feature-bit discovery, `Lfn2Pfn` V1/V2 compatibility, file descriptor ownership, async/page capability negotiation, and wrapper plugin stacking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOss.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssAio.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssAio.cc

## Purpose

`XrdOssAio.cc` implements asynchronous read/write/fsync support for the default OSS file object using POSIX AIO when available, with synchronous fallback completion when AIO is disabled or unavailable.

## Important APIs, Types, and Functions

Implemented methods are `XrdOssFile::Fsync(XrdSfsAio*)`, `Read(XrdSfsAio*)`, `Write(XrdSfsAio*)`, and `XrdOssSys::AioInit()`. Helper/thread functions include `XrdOssAioWait`, local signal constants `OSS_AIO_READ_DONE` and `OSS_AIO_WRITE_DONE`, and fallback signal-handler shims `XrdOssAioRSH`, `XrdOssAioWSH`, and `sigwaitinfo` when needed. Static state includes `XrdOssFile::AioFailure` and `XrdOssSys::AioAllOk`.

## Control Flow

On systems with POSIX AIO and successful `AioInit()`, file async methods fill the `aiocb` file descriptor, completion signal, and trace identity, then call `aio_read`, `aio_write`, or `aio_fsync`. AIO wait threads synchronously wait for read/write signals, obtain `aio_error` and `aio_return`, store `aiop->Result`, and invoke `doneRead()` or `doneWrite()`. If AIO is unsupported, disabled, returns `EAGAIN`/`ENOSYS`, or initialization fails, the methods execute the synchronous file operation and immediately call the completion routine.

## State and Persistence Behavior

AIO state is process-global: `AioAllOk` enables native AIO, wait threads run for process lifetime, and failure count throttles logging. Each request owns its `XrdSfsAio` control block and receives result/completion. No durable persistence exists.

## Dependencies and Integration Points

The code depends on platform AIO/signal APIs, `XrdSfsAio`, `XrdSysThread`, `XrdSysPlatform`, and OSS trace/error globals. It integrates with `XrdOssFile` methods from `XrdOssApi.cc` for fallback synchronous I/O.

## Risks and Edge Cases

Platform behavior is conditional and explicitly disables macOS POSIX AIO. Signal selection uses real-time signals when available, so process-wide signal masking must be correct. Fallback `Fsync(XrdSfsAio*)` assigns `-errno` after `Fsync()` even though `Fsync()` already returns negative errno, which should be reviewed. Busy-waiting while `aio_error` returns `EINPROGRESS` may spin briefly.

## Test Signals

Tests should cover builds with and without `_POSIX_ASYNCHRONOUS_IO`, initialization failure, fallback completion, native read/write completion, fsync completion, unexpected signal logging, AIO `EAGAIN` fallback, and result sign conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssAio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.cc

## Purpose

`XrdOssApi.cc` implements the default OSS storage-system entry points, plugin loading, initialization, local/remote path translation, directory operations, file open/read/write/stat/close operations, clone support, memory mapping, compression hooks, cache accounting, and basic filesystem mutation helpers.

## Important APIs, Types, and Functions

Top-level globals are `XrdOssSS`, `OssEroute`, and `OssTrace`. Exported factory functions are `XrdOssGetSS` and `XrdOssDefaultSS`. Implemented `XrdOssSys` methods in this file include `Init`, `Lfn2Pfn`, `GenLocalPath`, `GenRemotePath`, `Chmod`, `Mkdir`, `Mkpath`, `Stats`, and `Truncate`. Implemented `XrdOssDir` methods include `Opendir`, `Readdir`, `StatRet`, `Close`, and `Fctl`. Implemented `XrdOssFile` methods include clone variants, `Open`, `Close`, preread `Read`, byte `Read`, `ReadV`, `ReadRaw`, `Write`, `Fchmod`, `Fctl`, `Flush`, `Fstat`, `Fsync`, `getMmap`, `isCompressed`, `Ftruncate`, and private `Open_ufs`.

## Control Flow

`XrdOssGetSS()` verifies version compatibility, initializes default OSS when no plugin is configured, or loads a plugin and resolves the V2 then V1 storage-system factory. `XrdOssSys::Init()` configures the default system and stores the global pointer. Path helpers use optional name-to-name mappers. Directory open chooses local directory reading unless staging and remote reading are configured, otherwise delegates to MSS directory hooks. File `Open()` checks path options, applies read-only policy, opens the local file, triggers staging on missing remote files, validates regular-file status, sets cache accounting for write opens, optionally maps memory based on path/xattr flags, and records clone capability. Reads/writes use `pread`/`pwrite`, with vector preread hints and size limits. Close updates cache accounting and recycles memory/compression resources.

## State and Persistence Behavior

`XrdOssSys` holds configuration-derived roots, path lists, mappers, stage commands, cache/stage counters, preread parameters, stat plugin hooks, and version info. `XrdOssFile` owns an FD, optional cache pointer, memory-map object, compression object, file size snapshot, and clone flag. Operations persist by mutating the local filesystem and, for staged paths, by interacting with configured MSS/stage subsystems. Cache accounting is adjusted on truncate, close, and unlink-like flows elsewhere.

## Dependencies and Integration Points

The file integrates with `XrdOucPinLoader` and `XrdSysPlugin` for plugin loading, `XrdOucName2Name` for path mapping, `XrdOssCache`, `XrdOssMio`, optional compression (`oocx_CXFile`), xattrs, stage/MSS helpers, POSIX filesystem APIs, `XrdSysFD`, and OSS trace/error systems. It is the main implementation behind `XrdOss.hh` and `XrdOssApi.hh`.

## Risks and Edge Cases

Plugin ABI compatibility is critical. Path option handling combines staging, remote, read-only, migration, xattr, memory-map, and clone flags, so regressions often appear only under specific config. `Open()` must close FDs on non-regular files and compression attach failures. `Write()` appears to compare `retval == EBADF` after `pwrite` failure instead of `errno == EBADF`, which may be a latent bug in compressed-file error mapping. Vector preread uses global atomic counters and platform-specific fadvise behavior.

## Test Signals

Tests should cover default and plugin factory paths, version mismatch, N2N mapping success/failure, local and staged opens, read-only/force-read-only policy, directory local/MSS reads, `StatRet`, clone/ioctl success and unsupported paths, cache accounting on writes/truncate/close, memory-map xattr flags, compressed read/raw behavior, vector short read failure, and max-size write rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.hh

## Purpose

`XrdOssApi.hh` declares the default OSS concrete classes: `XrdOssDir`, `XrdOssFile`, and `XrdOssSys`. It extends the public OSS interface with implementation state, configuration hooks, cache/stage/MSS helpers, and default storage behavior.

## Important APIs, Types, and Functions

`XrdOssDir` implements `Close`, `Fctl`, `Opendir`, `Readdir`, `StatRet`, and `getFD`, and stores local/MSS directory handles, stat-return pointer, EOF/open flags, and directory options. `XrdOssFile` implements clone, open/close, chmod/control, sync/truncate/stat, mmap/compression introspection, byte/vector/raw/async I/O, and stores FD-related cache/mmap/compression state. `XrdOssSys` implements the filesystem methods from `XrdOss` plus `Configure`, config display, staging, stat variants, MSS methods, stats, `AioInit`, name-to-name mapping, path options, and many protected config/cache/stage helpers.

## Control Flow

This header establishes the default implementation flow: `XrdOssSys` creates `XrdOssDir`/`XrdOssFile`; those objects delegate path policy, mapping, cache, and stage decisions back to global `XrdOssSS`; and config parser helpers fill `XrdOssSys` state before service starts.

## State and Persistence Behavior

The header declares extensive process-lifetime configuration: local/remote roots, stage commands, RSS commands, FD fences, trace flags, path/space lists, N2N/stat plugins, preread settings, cache allocation parameters, usage/quota paths, and stage counters. Per-file and per-directory objects own live handles and transient operation state. Durable persistence occurs through the filesystem, cache files, stage/MSS commands, and optional usage/quota files configured elsewhere.

## Dependencies and Integration Points

It includes the public OSS API, config/error/stat headers, OUC export/path-list/stream helpers, and Sys error/pthread headers. It forward-declares cache, stage, name mapping, program, and plugin structures. It is consumed by most `XrdOss*.cc` implementation units.

## Risks and Edge Cases

This is an implementation ABI inside the server. Many public data members are shared across compilation units, so renaming or changing semantics has broad blast radius. `Features()` reports `XRDOSS_HASNAIO|XRDOSS_HASFICL`, with the comment noting async I/O is off for disk and clone-aware behavior; callers must interpret those bits consistently.

## Test Signals

Compile integration across all `XrdOss` sources is essential. Runtime tests should cover configuration permutations, stage/cache/MSS paths, path option macros `Check_RO`/`Check_RW`, AIO feature reporting, and constructor defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.cc

## Purpose

`XrdOssAt.cc` implements directory-relative OSS operations using POSIX `*at()` syscalls. It supports opening relative files/directories, stat, unlink, and remove-directory against an already open OSS directory object.

## Important APIs, Types, and Functions

Implemented `XrdOssAt` methods are `Opendir`, `OpenRO`, `Remdir`, `Stat`, and `Unlink`. Local macros `BOILER_PLATE` validate that the anchor object is a directory, the path is relative, and the directory FD is available; `OPEN_AT` opens with close-on-exec handling. Local RAII `openHelper` closes untransferred FDs.

## Control Flow

Each method validates the anchor and relative path. `Opendir()` opens the target with `openat`, wraps it in `fdopendir`, and returns an `XrdOssDir`. `OpenRO()` returns an `XrdOssFile` around an `openat` FD. `Remdir()` calls `unlinkat(..., AT_REMOVEDIR)`. `Stat()` calls `fstatat` and optionally maps device info through `XrdOssCache::DevInfo`. `Unlink()` refuses directories, deletes regular files directly with cache adjustment, or follows symlink targets to remove the underlying cache data and then the symlink.

## State and Persistence Behavior

Operations mutate only the online local filesystem view relative to the directory FD. Returned file/dir objects own transferred FDs. `Unlink()` updates cache accounting by device or cache base path depending on symlink target naming.

## Dependencies and Integration Points

The implementation depends on `XrdOssDF`, default `XrdOssDir`/`XrdOssFile`, `XrdOssCache`, `XrdOssPath`, `XrdSysFD`, and POSIX `openat`, `fstatat`, `unlinkat`, and `readlinkat`. It is unavailable when `HAVE_FSTATAT` is not defined.

## Risks and Edge Cases

Absolute paths and missing directory FDs are rejected, preventing unintended name-to-name translation. Symlink target deletion is sensitive: failure to unlink an existing target is logged and returned. One error path returns `-retc` after `retc` is already negative, which would flip the sign and should be reviewed. Cache adjustment depends on the target path's `xChar` suffix convention.

## Test Signals

Tests should cover unsupported builds, non-directory anchors, absolute path rejection, opened FD transfer, close-on-exec behavior, stat with device info, regular-file unlink cache adjustment, symlink target unlink, missing symlink target, directory unlink rejection, and sign of symlink-target unlink errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.hh

## Purpose

`XrdOssAt.hh` declares `XrdOssAt`, an extended helper API for operations relative to an open OSS directory. It complements the path-based `XrdOss` methods with safer online-only relative operations.

## Important APIs, Types, and Functions

The class declares `Opendir`, `OpenRO`, `Remdir`, `Stat`, and `Unlink`, plus option flag `At_dInfo`. It stores a reference to the associated `XrdOss` filesystem as `ossFS`, although current implementation primarily uses the anchor directory object and default OSS concrete types.

## Control Flow

Callers create one `XrdOssAt` for an OSS system, pass an open directory `XrdOssDF`, and operate on relative path names. The header explicitly notes that many `*at()` variants are not implemented, paths must be relative, no name-to-name processing is applied, and only online copies are affected.

## State and Persistence Behavior

The class itself owns no mutable operation state. Persistence effects are the underlying filesystem changes performed by implementation methods.

## Dependencies and Integration Points

It includes `XrdOucEnv.hh` and forward-declares `stat`, `XrdOss`, and `XrdOssDF`. It integrates with consumers that need race-resistant relative directory operations, such as recursive scans or namespace operations already holding a directory handle.

## Risks and Edge Cases

The contract intentionally differs from Unix `*at()` name handling because no N2N translation occurs. Callers expecting remote/tape-backed behavior must use standard OSS methods. The stored `ossFS` reference currently has limited use, so future extension should avoid assuming it has no semantic role.

## Test Signals

Tests should verify relative-only semantics, online-only behavior, interoperability with `XrdOssDir` and `XrdOssFile`, unsupported method expectations, and `At_dInfo` stat augmentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.hh -->
