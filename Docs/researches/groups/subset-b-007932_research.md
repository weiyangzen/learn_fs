# subset-b-007932 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.cc

## Purpose

`XrdCmsClustID.cc` implements the process-global registry that maps CMS cluster identifiers to `XrdCmsClustID` objects. It is used by `XrdCmsCluster` to group ordinary servers, managers, peers, and alternate managers under a stable cluster id, to derive node masks by cluster id, and to keep a small alternate-manager table for a cluster.

## Important APIs and functions

- `XrdCmsClustID::AddID(const char *cID)` normalizes a bi-compatible cluster id by stripping everything through the last space, interns it in the static `XrdOucHash<XrdCmsClustID> cidTab`, and returns the existing or newly allocated cluster-id object.
- `XrdCmsClustID::Find(const char *cID)` applies the same normalization and looks up an existing cluster id without creating it.
- `XrdCmsClustID::Mask(const char *cID)` returns the accumulated `SMask_t` for a cluster id, or zero when unknown.
- `XrdCmsClustID::AddNode(XrdCmsNode *nP, bool isMan)` adds a node mask to the cluster id. For non-manager/server entries it only ORs the mask. For manager or peer alternates it also records the node pointer in the bounded alternate array and enforces a shared slot number.
- `XrdCmsClustID::Exists(XrdLink *lp, const char *nid, int port)` scans alternate entries and delegates identity matching to `XrdCmsNode::isNode`.
- `XrdCmsClustID::RemNode(XrdCmsNode *nP)` removes either a plain server mask or an alternate node pointer and returns the replacement alternate primary candidate if any.

## Control flow

The file is built around three local statics: `cidMtx`, `cidTab`, and `cidFree`. `AddID()` duplicates the normalized id before locking, lazily refreshes `cidFree`, and calls `cidTab.Add(..., Hash_keep)`. When the key already exists, it frees the duplicate string and returns the existing object; when the key is new, it installs the previously prepared `cidFree` and creates a fresh spare object for the next insertion.

`AddNode()` is the key mutator. Non-manager additions are cheap: the node mask is merged into `cidMask` and no alternate table slot is consumed. Manager/peer additions validate capacity (`altMax == 8`) and slot consistency using `nP->ID(iNum)`, then append the node pointer and update `ntSlot` and `cidMask`. `RemNode()` is the inverse: plain servers clear the node mask immediately, while managers/peers are removed from the compacted alternate array, with `cidMask` cleared only when no alternate entries remain.

## State and persistence behavior

State is entirely in-memory and process-global. `cidTab` owns id-to-object lookup, each object owns a duplicated `cidName`, and each object tracks `cidMask`, `ntSlot`, `npNum`, and up to eight `XrdCmsNode *` alternates. There is no persistent storage. State changes are protected by `cidMtx` for add/find/mask/existence/add-node paths; `RemNode()` mutates object fields without taking `cidMtx` itself, so callers must provide a safe context or accept the risk of concurrent mutation.

## Dependencies and integration points

The implementation depends on:

- `XrdCmsNode` for masks, slot/instance identity, name fields, and `isNode()`.
- `XrdCmsTrace`/`Say` for debug and error logging.
- `XrdOucHash` for string-key interning.
- `XrdSysMutex`/`XrdSysMutexHelper` for registry locking.

Its main integration point is `XrdCmsCluster::Add()`, `AddAlt()`, `Remove()`, and `getMask(const char *)`, which use cluster ids for alternate manager replacement, duplicate-login rejection, and cluster mask lookup.

## Risks

- `RemNode()` lacks an internal `cidMtx` guard even though it updates `cidMask`, `npNum`, and `nodeP`; reviewers should confirm all callers already hold a lock that serializes with `AddNode()` and `Exists()`.
- The alternate table hard limit is eight entries. Overflow rejects additional alternate managers/peers and logs an error; large deployments need explicit test coverage for this behavior.
- Cluster id normalization is repeated in `AddID()`, `Find()`, and `Mask()` and depends on the last space in the id string. Inputs with trailing spaces or unexpected embedded whitespace could alias ids unexpectedly.
- `cidFree` is allocated as a spare global object and never reclaimed during process lifetime; this is intentional process-global cache behavior but should be considered when sanitizers report reachable allocations.

## Test signals

Useful tests would exercise: repeated `AddID()` for the same id returning the same object; cluster ids with and without compatibility prefixes; server-only mask accumulation and removal; manager alternate insertion up to and past `altMax`; slot mismatch rejection; `Exists()` duplicate detection; and alternate removal returning the replacement node used by `XrdCmsCluster::Remove()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.hh

## Purpose

`XrdCmsClustID.hh` declares `XrdCmsClustID`, the small registry entry type used to associate a cluster id string with a server mask and a bounded set of alternate manager/peer nodes. The header exposes the operations needed by the cluster table while hiding the registry and locking details in the `.cc` file.

## Important APIs and types

- `class XrdCmsClustID` is the registry entry.
- Static factory/lookups: `AddID()`, `Find()`, and `Mask()`.
- Node membership: `AddNode()`, `RemNode()`, and `Exists()`.
- State queries: `Avail()`, `IsEmpty()`, `IsSingle()`, and `Slot()`.
- Internal constants and fields: `altMax = 8`, `cidMask`, `cidName`, `ntSlot`, `npNum`, and `nodeP[altMax]`.

## Control flow and semantics

The constructor initializes an empty id with no mask, no name, no assigned slot, zero alternate nodes, and a null-filled alternate pointer array. The destructor frees only `cidName`; it does not own or delete any `XrdCmsNode` pointers. Inline methods are intentionally simple predicates used by cluster admission and removal:

- `Avail()` checks whether there is room for another alternate.
- `IsEmpty()` and `IsSingle()` describe alternate-table occupancy.
- `Slot()` exposes the primary cluster table slot shared by alternate manager entries.

The non-inline methods are implemented in `XrdCmsClustID.cc` and provide all mutation and registry access.

## State and persistence behavior

`XrdCmsClustID` stores transient process state. Its only heap-owned field is `cidName`, allocated with `strdup()` in the implementation and freed with `free()` in the destructor. Node pointers are borrowed references into `XrdCmsCluster`/`XrdCmsNode` lifetime management.

## Dependencies and integration points

The header forward-declares `XrdLink` and `XrdCmsNode`, includes `XrdCmsTypes.hh` for `SMask_t`, and uses C library allocation helpers. It is included by `XrdCmsCluster.cc` to associate logins with cluster ids and by any component needing `XrdCmsClustID::Mask()`.

## Risks

- Borrowed `XrdCmsNode *` values make lifetime ordering important. Deletion must go through cluster removal/drop paths that remove node pointers before freeing nodes.
- The fixed `altMax` is not configurable from this header, so any alternate-manager scaling change requires code changes and tests.
- The API does not expose explicit locking semantics; callers cannot tell from the header which methods lock internally.

## Test signals

Header-level test signals are mostly integration tests through `XrdCmsCluster`: successful alternate insertion, alternate overflow, cluster slot mismatch, and cleanup on node removal. Static analysis should also verify that `cidName` allocation/free conventions stay paired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.cc

## Purpose

`XrdCmsCluster.cc` implements the singleton `XrdCms::Cluster`, the central runtime node table for cmsd. It admits and removes subscribers, tracks managers/peers/servers, sends CMS protocol messages, locates files, selects redirect targets, reports statistics, maintains alternate-manager lists, and monitors load/reference counters.

## Important APIs and functions

- `XrdCmsCluster::Add()` admits a new node, reconnects an existing node, installs alternate managers through `XrdCmsClustID`, redirects or bumps old nodes when the table is full, updates peer masks and cluster state, and returns the node locked.
- `AddAlt()` adds a manager/peer alternate under an existing cluster id and can replace a dropped primary with a live alternate.
- `BlackList()` applies or removes blacklist status on matching nodes and can send disconnect requests.
- `Broadcast()` and `Broadsend()` send CMS requests to node masks, with `Broadcast()` returning an unqueried mask and `Broadsend()` choosing one eligible node round-robin.
- `Locate()` finds current or potential locations for a path, using `Cache.Paths`, file-state cache entries, DFS mode, and broadcast state queries.
- `Select(XrdCmsSelect &)` is the high-level file redirect selector for read/write/meta/replica/staging flows.
- `Select(SMask_t, ...)` is a lower-level selector for an already computed mask, used when callers only need host/port resolution.
- `Remove()`, `Drop()`, and the local `XrdCmsDrop` job class implement delayed, immediate, and asynchronous node teardown.
- `SelNode()`, `SelbyCost()`, `SelbyLoad()`, `SelbyLoadR()`, and `SelbyRef()` implement the actual scheduling policies.
- `Space()`, `Stats()`, and `Statt()` summarize cluster space and XML-like statistics.
- `MonPerf()` periodically asks nodes for usage; `MonRefs()` periodically resets selection reference counters.

## Control flow

Node admission starts in `Add()`. It scans `NodeTab[STMax]` for an existing identity, a free slot, and bump candidates. Existing disconnected nodes are rehooked. Manager/peer entries that share a known cluster id can enter as alternates through `AddAlt()`. If capacity is exhausted, ordinary incoming nodes may be redirected using `sendAList()`, or old entries may be removed and replaced. New nodes are constructed, tied to a `XrdCmsClustID`, marked with status flags, counted, and used to update `CmsState`.

Removal uses a two-step design. `Remove(reason, node, immed)` normalizes lock ordering with a stack `theLocks` helper, marks nodes offline, disconnects live links, substitutes a live alternate manager when possible, or schedules a delayed `XrdCmsDrop`. `Drop()` validates the node id/instance pair before actually clearing `NodeTab`, removing alternate-manager text entries, lowering `STHi`, invalidating `Cache` entries, and deleting the node directly or via an asynchronous delete job.

File lookup and selection split path availability from redirect choice. `Locate()` consults `Cache.Paths`, optionally handles wildcard current-server listings, and either uses DFS-specific checks or asks candidate nodes for state. `Select(XrdCmsSelect &)` computes allowed, primary, and staging masks based on path export information, cached file state, write/read semantics, tried-node masks, refresh/new-file/replica flags, and DFS behavior. It then calls `SelNode()` unless a wait or terminal error is required.

`SelNode()` applies network interface constraints, optional affinity packing, space requirements, local-node preference, peer fallback, and delay/error construction. The `Selby*()` helpers scan `NodeTab` under `STMutex`, skip unreachable/offline/bad/overloaded/full nodes, update selector reason flags, increment selection counters, and choose by peer cost, load, randomized load weight, or reference count.

## State and persistence behavior

All cluster state is in memory:

- `NodeTab[STMax]` stores the active node pointers.
- `NodeCnt`, `STHi`, `peerHost`, and `peerMask` summarize table occupancy and peer filtering.
- `AltMans`, `AltMend`, and `AltMent` store fixed-width alternate manager redirect tokens sent by `sendAList()`.
- `SelWtot`, `SelRtot`, and `SelTcnt` are atomic selection counters.
- `NodeWeight[STMax]` is scratch state for randomized load selection.

`STMutex` protects node table structure and most node-state traversal. The code frequently swaps the global table lock for a per-node lock with `g2nLock()` to avoid holding the global lock across node-specific actions. Persistence is delegated elsewhere: file/path knowledge is in `XrdCmsCache`, global state reporting in `XrdCmsState`, and scheduled jobs in `XrdScheduler`.

## Dependencies and integration points

This file integrates with nearly every CMS subsystem:

- `XrdCmsConfig` supplies selection delays, scheduling policy, space thresholds, peer-delay policy, service minimums, and role flags.
- `XrdCmsNode` provides node identity, masks, status flags, load/space/reference counters, network interfaces, send/disconnect/delete behavior, and lock conversion.
- `XrdCmsCache` stores exported path masks and file-state masks.
- `XrdCmsBaseFS` drives DFS/shared-filesystem behavior and retry limits.
- `XrdCmsClustID` supports cluster-id masks and alternate manager replacement.
- `XrdCmsState`, `XrdCmsRRQ`, `XrdCmsBlackList`, `XrdCmsRole`, `XrdCmsSelect`, and protocol structs provide state updates, fast redirect stats, blacklist checks, role names, selection requests, and wire messages.

## Risks

- Locking is complex. `Broadcast()` intentionally drops and reacquires `STMutex` while holding a node reference; removal and deletion correctness depends on reference counts and lock conversion ordering.
- `SelbyLoadR()` builds cumulative weights but does not call the `RefCount` macro on the selected node, unlike the other selectors. That means randomized load scheduling may not update per-node reference counters consistently.
- `SelbyLoadR()` constructs `std::uniform_int_distribution<int>(1, totWeight)` without an explicit `totWeight > 0` guard. Normal positive `P_fuzz + (100 - load)` values should make eligible weights positive, but extreme config or future changes could make this fragile.
- In `Drop()`, peer removal uses `peerHost &= nP->NodeMask`, which preserves only the dropped peer bit rather than clearing it; this deserves review against intended peer-mask semantics.
- Alternate manager text in `AltMans` uses fixed-width blank-padded slots. Formatting changes must preserve `AltSize` assumptions and rotation logic.
- Error responses are assembled into fixed buffers with mostly bounded `snprintf()`, but some code paths assume node interface names fit selection buffers through `GetName()`.

## Test signals

High-value tests include admission/reconnection/displacement cases; manager alternate replacement on primary loss; blacklist apply/remove with disconnect request generation; broadcast behavior with offline and failed-send nodes; DFS and non-DFS locate/select paths; write conflict cases for duplicate/readonly/no-replica files; peer fallback after local delay thresholds; selection counter behavior across all scheduling policies; drop cancellation when node instances change; and stats output sizing with many nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.hh

## Purpose

`XrdCmsCluster.hh` declares the singleton cluster table interface used by cmsd managers, supervisors, peers, and servers. It also defines the CMS node status flags and the `SpaceData` aggregate used for manager/supervisor space reporting.

## Important APIs and types

- Status flags for `Add()`: `CMS_noStage`, `CMS_Suspend`, `CMS_Perm`, `CMS_isMan`, `CMS_Lost`, `CMS_isPeer`, `CMS_isProxy`, `CMS_noSpace`, `CMS_isSuper`, and `CMS_isVers3`.
- Flag groups: `CMS_notServ` and `CMS_hasAlts`.
- `XrdCms::SpaceData` captures total/free space plus read/write and staging free-space/utilization summaries.
- Public cluster methods cover node admission/removal, blacklist updates, broadcast/broadsend, mask lookup, listing, locate/select, monitor threads, reference resets, space summaries, and stats.
- Selection return constants: `NotFound`, `Wait4CBk`, `RetryErr`, and `EReplete`.
- `CmsLSOpts` controls list output shape and desired network interface.
- `SLock()` exposes direct read/write locking for callers that need to coordinate with cluster state.

## Control flow and state shape

The class is a single-instance global, declared as `extern XrdCmsCluster Cluster` in namespace `XrdCms`. The public API is intentionally broad because CMS protocol handlers delegate most cluster-level decisions here. Private helpers split implementation into alternate-manager handling, delayed drop jobs, path/defer logging, bit-count helpers, selection failure formatting, selection algorithms, DFS selection, alternate-manager-list sending, and terminal error formatting.

Core protected state includes:

- `STMutex`, the reader/writer lock for node-table information.
- `NodeTab[STMax]` and `NodeWeight[STMax]`.
- `STHi`, `NodeCnt`, and reserved padding/state.
- atomic selection counters.
- fixed-size alternate-manager token storage.
- `peerHost` and `peerMask` for peer filtering.

## Dependencies and integration points

The header depends on CMS masks/types, `XrdOucTList`, enum operators, pthread/RW lock wrappers, and atomic counters. It forward-declares `XrdLink`, `XrdCmsDrop`, `XrdCmsNode`, `XrdCmsSelect`, `XrdCmsSelector`, `XrdNetAddr`, `XrdCmsBaseFR`, `XrdCmsClustID`, and `XrdCmsSelected` to keep compile dependencies moderate.

Callers use this class as the authoritative cluster surface: protocol login code calls `Add()`, disconnect paths call `Remove()`, request handling calls `Locate()`/`Select()`, admin/stat code calls `List()`/`Stats()`/`Statt()`/`Space()`, and manager coordination uses `Broadcast()`/`Broadsend()`.

## Risks

- `SLock()` exposes the internal lock directly; misuse by external callers can deadlock with node-level locks if they do not follow the implementation's lock ordering.
- Many return codes are negative sentinel values rather than typed results, so callers must distinguish wait, retry, complete-error, and not-found outcomes exactly.
- `NodeCnt` is public, but most state is lock-protected. Any direct reader of `NodeCnt` should be reviewed for synchronization assumptions.
- The fixed `AltMans` capacity is tied to `STMax * AltSize`; changes in address formatting or maximum subscribers can have memory/layout effects.

## Test signals

Header/API tests should assert flag combinations, `CmsLSOpts` enum operators, expected public return constants, and compatibility of callers with the declared locking and return-code contracts. Integration tests should verify that the global `XrdCms::Cluster` is the single cluster object used across modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.cc

## Purpose

`XrdCmsConfig.cc` implements cmsd startup and runtime configuration. It owns global CMS objects, parses `cms.*`/legacy directives, establishes role, networking, admin sockets, cache/base-filesystem behavior, OSS/name/security plugins, exported paths, scheduling and space policy, and starts the background threads that make a configured CMS service active.

## Important APIs and functions

- `Configure0()` imports protocol bootstrap state: logger, trace logger, host/program/instance names, TCP port, scheduler, admin path/mode, debug flag, and inherited environment.
- `Configure1()` handles command-line role overrides, finds and scans the config file, pre-scans role if needed, processes configuration directives, computes role strings/types, exports `XRDROLE` and `XRDROLETYPE`, validates role/port combinations, and applies proxy/metric warnings.
- `Configure2()` completes phase-two setup: cache init, admin socket creation, stable system id generation, login CGI environment, N2N/OSS/prep/baseFS setup, manager/server setup, CMS state initialization, manifest append, and scheduling of `DoIt()`.
- `ConfigXeq()` dispatches directives to individual handlers and separates dynamic-safe directives from startup-only directives.
- `DoIt()` starts notification, prepare, supervisor, admin, manager, state-monitor, ping-clock, and service-enable flows.
- `ConfigDefaults()` initializes all defaults for role flags, delays, scheduling, disk thresholds, plugin paths, sockets, caches, prep state, and timezone.
- `ConfigN2N()`, `ConfigOSS()`, `Manifest()`, `MergeP()`, `setupManager()`, `setupServer()`, and `setupSid()` are the main setup helpers.
- Directive handlers (`xallow`, `xaltds`, `xapath`, `xblk`, `xcid`, `xdelay`, `xdfs`, `xexpo`, `xfsxq`, `xfxhld`, `xlclrt`, `xmang`, `xmode`, `xnbsq`, `xperf`, `xping`, `xprep`, `xprepm`, `xreps`, `xrmtrt`, `xrole`, `xsched`, `xspace`, `xsubc`, `xsupp`, `xtrace`, `xvnid`) map config syntax into `XrdCmsConfig` fields and subsystem calls.

## Control flow

Startup is staged. Phase 0 receives host process state from `XrdProtocol_Config`. Phase 1 parses arguments and configuration enough to determine role and validate base parameters. If the role was not supplied on the command line, it pre-scans only `all.role`/`olb.role`; then it performs the full config scan and dispatches recognized directives by stripping the prefix and calling `ConfigXeq()`.

Phase 2 performs operations that require a resolved role and parsed settings. Managers initialize the cache, all roles create an admin socket path, all roles derive `mySID`, optional N2N and OSS plugins are loaded, the base filesystem and prepare queue start, manager/server setup functions start role-specific resources, `CmsState` is initialized, and an environment manifest can be appended with prefix/admin/cluster id data. On success the object schedules itself as an `XrdJob`, and `DoIt()` starts the long-running service threads.

Directive handlers are mostly small parsers. Manager-only directives silently no-echo on incompatible roles. Numeric conversions use `XrdOuca2x`; plugin/library parsing uses `XrdOucUtils::parseLib`; manager host parsing uses `XrdCmsUtils::ParseManPort()`/`ParseMan()`; export/default path parsing delegates to `XrdOucExport`; conditional directives use `XrdOucUtils::doIf()`.

## State and persistence behavior

The file defines process-global CMS objects in namespace `XrdCms`: `theEnv`, `Admin`, `baseFS`, `Config`, `Say`, `Trace`, and `Sched`. Configuration state is stored as fields on the global `Config` instance. Most strings are heap-owned `char *` values managed by explicit `strdup()`/`free()`, while many role/environment pointers are borrowed or duplicated depending on source.

Persistent side effects are limited but important:

- named admin/notification sockets are created under `AdminPath`;
- `Manifest()` appends `&pfx=`, `&ap=`, and `&cn=` data to an environment file named by `xrdEnv->Get("envFile")`;
- external programs and plugins are loaded or validated;
- environment variables such as `XRDROLE`, `XRDROLETYPE`, `XRDREDIRECT`, `XRDOSSTYPE`, and `XRDOSSCSCAN` are exported.

## Dependencies and integration points

This file is the integration hub for CMS startup. It touches protocol bootstrap (`XrdProtocol_Config`), scheduler/jobs/threads, network sockets and addresses, security, OSS, name-to-name loaders, exports, stream parsing, base filesystem mode, cache, cluster, manager, meter, prepare queue, request queue, supervisor, state monitor, trace, blacklist, and utility functions.

The most direct downstream effects are on `XrdCmsCluster`: scheduling fields (`P_*`, `sched_*`, `MaxLoad`, `MaxDelay`, `DiskLinger`), space fields (`DiskMin`, `DiskHWM`, percentage thresholds, `DiskWT`), delay fields (`LUPDelay`, `SUPDelay`, `SUSDelay`, `PSDelay`, `RWDelay`), and role flags drive cluster selection and node admission.

## Risks

- The parser is broad and role-sensitive; regression tests need both accepted and ignored directives for manager, server, supervisor, peer, proxy, and meta-manager modes.
- Memory ownership is manual and mixed. Repeated dynamic directives free some old strings but not every startup field is designed for dynamic reconfiguration.
- `xnbsq()` appears to compare the literal string `"val"` to `"none"` instead of comparing the parsed `val`, which would prevent `maxq none` from working as described.
- `xrole()` peer handling sets `xPeer`/`xSolo` based on `xServ - 1`; this may be intentional old-style negative marker logic, but the expression is subtle enough to merit a targeted role test.
- `Configure1()` role resolution has legacy negative markers and command-line override behavior; accidental sign changes can alter role defaults.
- `Manifest()` appends unescaped path and cluster-id fragments to an environment file. Inputs containing separators should be checked against the consumer contract.
- `ConfigProc()` accepts legacy prefixes by calling `ConfigXeq(var+4, ...)`; this relies on all accepted directive names having a four-character prefix compatible with that slicing.

## Test signals

Useful signals include startup tests for each role; config parsing tests for every directive family; dynamic reconfiguration tests for `delay`, `fxhold`, `ping`, `sched`, `space`, and `trace`; manager list and subcluster domain validation; DFS option combinations; export merging into `PathList` and `myPaths`; OSS/N2N plugin error handling; admin path creation and warning behavior; scheduler policy derivation; and smoke tests that phase 2 starts the expected threads and state for manager/server/peer/proxy combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.hh

## Purpose

`XrdCmsConfig.hh` declares `XrdCmsConfig`, the global cmsd configuration/job object. It is both the startup coordinator and the shared runtime configuration record consumed by cluster management, cache behavior, filesystem setup, scheduling, security, preparation, and admin subsystems.

## Important APIs and types

- `XrdCmsConfig : public XrdJob` so phase-two startup can schedule `DoIt()` asynchronously.
- Public startup methods: `Configure0()`, `Configure1()`, `Configure2()`, `ConfigXeq()`, and `DoIt()`.
- Utility/status methods: `GenLocalPath()`, `asManager()`, `asMetaMan()`, `asPeer()`, `asProxy()`, `asServer()`, and `asSolo()`.
- Public configuration fields cover delay policy, query policy, server-count/service thresholds, load and scheduling weights, disk thresholds, role flags, ports/sockets, exported paths, plugin names/parameters, local/remote roots, identity fields, security/admin sockets, filesystem programs, and statistics flags.
- Private helpers and directive parsers are declared for defaults, plugin setup, config scanning, manifest writing, role-specific setup, system id generation, and all supported `cms.*` directives.
- Namespace externs publish `XrdCms::Admin`, `XrdCms::Config`, and `XrdCms::Sched`.

## Control flow and state shape

The class exposes many fields directly because existing CMS components read configuration without accessor indirection. The constructor calls `ConfigDefaults()` and labels the job `"cmsd startup"`. Startup is expected to proceed through `Configure0`, `Configure1`, `Configure2`, then scheduled `DoIt()`.

The public fields can be grouped by behavior:

- delay and service policy: `LUPDelay`, `LUPHold`, `DELDelay`, `DRPDelay`, `PSDelay`, `RWDelay`, `QryDelay`, `SUPCount`, `SUPLevel`, `SUSDelay`, and related values;
- performance/scheduling: `P_cpu`, `P_io`, `P_load`, `P_mem`, `P_pag`, `P_dsk`, `P_fuzz`, `P_gshr`, `sched_*`, `MaxLoad`, `MaxDelay`, `RefReset`, `RefTurn`;
- disk/space: `DiskMin`, `DiskHWM`, percentage thresholds, `DiskLinger`, `DiskAsk`, `DiskWT`, `DiskSS`, `DiskOK`;
- role/network/admin: ports, `NetTCP`, role identity strings, manager/subcluster lists, admin/notification/redirect sockets, and security;
- plugins and path mapping: OSS, perf, VNID, N2N, local/remote roots, exported paths, and filesystem operation programs.

## State and persistence behavior

`XrdCmsConfig` is long-lived global state. It owns many heap strings and subsystem pointers but has an empty destructor, reflecting process-lifetime ownership. Some values are static defaults until config parsing changes them; others are runtime dynamic knobs changed through `ConfigXeq()` for the dynamic directives. Persistent effects are implemented in the `.cc` file, mainly socket creation, plugin loading, environment exports, and manifest append.

## Dependencies and integration points

The header includes `XrdJob`, CMS path list/types, OUC path/text lists, and forward-declares scheduler, networking, OSS, stream, admin, security, environment, name mapping, and program types. It is included across CMS modules wherever global configuration is needed. `XrdCmsCluster` uses delay, scheduling, role, disk, and peer settings extensively; `XrdCmsManager`, `XrdCmsState`, `XrdCmsCache`, `XrdCmsPrepare`, and security/OSS setup also depend on it.

## Risks

- The large public mutable field surface makes invariants implicit. For example, changing `SUPCount`, `SUPLevel`, or scheduling fields can alter cluster behavior without local validation.
- Empty destructor and process-lifetime ownership are acceptable for daemon startup but complicate leak-sanitizer expectations and unit-test reuse.
- Several fields use small integer or `char` types for boolean/config modes, so parser range checks in the implementation are critical.
- Dynamic directives share the same object as startup-only state; future dynamic additions must audit whether downstream subsystems observe changes safely.

## Test signals

Tests should verify constructor defaults, role accessor methods, phase-order assumptions, dynamic-vs-static directive dispatch, bounds on small fields, and downstream behavior when cluster selection reads scheduling/space/delay fields. Leak tests should account for intended process-lifetime allocations or instantiate in a controlled harness with cleanup wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.hh -->
