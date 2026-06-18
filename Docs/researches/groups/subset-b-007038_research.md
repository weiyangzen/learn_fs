# subset-b-007038 Research

Grouped source research for EOS MGM monitoring export, namespace statistics forwarding, and the XRootD MGM OFS plugin core. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.cc -->
# sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.cc

## Purpose
`PrometheusExporter.cc` implements the EOS MGM Prometheus HTTP metrics endpoint. It adapts in-memory MGM traffic-shaping state into `prometheus::MetricFamily` objects, gates collection to the active master, wraps high-cardinality collectors in a cache, and registers the resulting collectors with a `prometheus::Exposer`.

## Important APIs, Types, And Functions
The public implementation is `PrometheusExporter::PrometheusExporter(...)` plus the default destructor. Internal helpers include `MasterOnlyCollectable`, `MonitoringCollector`, `TrafficShapingCollector`, `EntityTotals`, `StandardKey`, `AllKey`, `LabelOrUnknown()`, metric-family builders, `AddGauge()`, `AddCounter()`, `AddReadWriteCounters()`, `AddLoopStats()`, and `AddPolicyMetrics()`.

`TrafficShapingCollector::Collect()` is the main exporter path. It creates metric families for cumulative IO bytes and operations, per-filesystem IO, all-tag IO, loop latency, report processing rate, map cardinality, policy bytes, reservation pressure, traffic-shaping configuration, and the `eos ns stat` compatible enabled flag. The collector delegates population to `AddCounterFamilies()`, `AddSystemFamilies()`, `AddPolicyFamilies()`, `AddPressureFamilies()`, and `AddConfigFamilies()`.

## Control Flow
The constructor creates a `prometheus::Exposer` on the supplied bind address with 8 worker threads, then registers two master-gated collectables: a lightweight `MonitoringCollector` exposing cache TTL and a cached `TrafficShapingCollector` exposing traffic-shaping data. `MasterOnlyCollectable::Collect()` returns an empty vector unless the supplied `should_collect` predicate exists and returns true.

At scrape time, `TrafficShapingCollector` asks `TrafficShapingEngine` for its manager. If no manager is available, no traffic-shaping metrics are emitted. Otherwise it constructs all families, fills them from manager snapshots, and returns the vector. All-tag metrics are emitted only when the current detail-level cardinality is at or below `kMaxAllTagsMetricEntries` (50,000); otherwise the exporter emits limit status and suppresses those high-cardinality series.

## State And Persistence Behavior
The exporter owns no persistent EOS state. Runtime state is limited to the exposer, collector objects, cluster label string, cache TTL, and references into `TrafficShapingEngine`. Counters are derived from traffic-shaping cumulative snapshots; gauges are derived from current engine and manager configuration. The only retention/caching behavior comes from `CachedCollectable`, configured by the constructor TTL.

## Dependencies And Integration Points
This file integrates `prometheus-cpp` (`Collectable`, `Exposer`, `MetricFamily`, `ClientMetric`) with EOS traffic shaping (`TrafficShapingEngine`, `TrafficShapingManager`, `TrafficShapingPolicy`, snapshot types) and EOS label helpers (`UidLabel`, `GidLabel`, `NodeLabel`, `kUnknownId`). It is started and stopped by `XrdMgmOfs::ApplyMonitoringConfig()` and uses the MGM instance name as the `cluster` label.

## Risks And Edge Cases
Metric cardinality is the central risk: all-tag metrics include node, fsid, app, uid, gid, and compatibility labels, so the hard 50,000-entry cap prevents scrape overload but can hide detail. Label compatibility also duplicates uid/gid fields (`uid`, `uid_id`, `uid_name`, `gid`, `gid_id`, `gid_name`, `groups`), so label changes could break dashboards. The collector assumes manager snapshot methods are safe during concurrent scrapes. Disabled user policies export zero for user limit/reservation gauges while controller limits still export raw values, which consumers must interpret correctly.

## Test Signals
Useful tests include master versus non-master collection, cache TTL metric presence, manager-null behavior, all-tag export below/equal/above 50,000 entries, aggregate/detail-level projections, policy enabled/disabled values, reserved-app pressure with missing pressure samples, config gauge values, and scrape output label compatibility for existing dashboards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.hh -->
# sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.hh

## Purpose
`PrometheusExporter.hh` declares the small owning wrapper that exposes MGM metrics through Prometheus. It hides prometheus-cpp implementation details from `XrdMgmOfs` while tying the endpoint to the traffic-shaping engine, cluster label, scrape cache TTL, and master-only collection predicate.

## Important APIs, Types, And Functions
The class `eos::mgm::monitoring::PrometheusExporter` has one constructor:
`PrometheusExporter(std::string bind_address, traffic_shaping::TrafficShapingEngine& engine, std::string cluster, std::chrono::milliseconds cache_ttl, std::function<bool()> should_collect)`.
It has a destructor, deleted copy constructor, and deleted copy assignment. Private state is `mCollectors`, retaining registered `prometheus::Collectable` objects, and `mExposer`, the HTTP exposer.

## Control Flow
The header defines the ownership contract only. Construction starts the endpoint and registers collectors in the `.cc`; destruction tears down the exposer through RAII. Copying is disabled because the exposer binds a listening endpoint and the collector registrations should have a single owner.

## State And Persistence Behavior
The wrapper owns runtime-only endpoint state. It persists no configuration to disk and does not own the referenced `TrafficShapingEngine`; the engine must outlive the exporter instance.

## Dependencies And Integration Points
It forward-declares prometheus-cpp classes and includes `mgm/shaping/TrafficShaping.hh` for the engine type. `XrdMgmOfs` stores the exporter in a `std::unique_ptr`, recreating it when monitoring configuration changes and resetting it during shutdown.

## Risks And Edge Cases
Lifetime coupling is important: the engine reference and master predicate capture must remain valid while scrapes are possible. Bind-address conflicts and exposer construction failures surface from the implementation constructor. Since the class is non-copyable but movable operations are not declared, callers should treat it as unique-owner only.

## Test Signals
Compile tests should verify the header can be included without pulling in prometheus definitions. Runtime tests should construct and destroy an exporter with a test engine, verify copy operations are rejected at compile time, and exercise failure handling through the `XrdMgmOfs::ApplyMonitoringConfig()` integration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.cc -->
# sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.cc

## Purpose
`NamespaceStats.cc` implements the MGM namespace statistics adapter. It satisfies the namespace layer's `INamespaceStats` interface by forwarding namespace operation counters and execution-time samples into the global MGM statistics object.

## Important APIs, Types, And Functions
The file implements `NamespaceStats::Add(const char* tag, uid_t uid, gid_t gid, unsigned long val)` and `NamespaceStats::AddExec(const char* tag, float exectime)`. Both methods call through `gOFS->MgmStats`.

## Control Flow
The control flow is intentionally direct: namespace code calls `INamespaceStats::Add()` or `AddExec()`, this adapter dereferences global `gOFS`, then forwards to `MgmStats.Add()` or `MgmStats.AddExec()`. Comments state that no additional locking is needed because `MgmStats` methods lock internally.

## State And Persistence Behavior
The adapter owns no state and persists nothing. Counter and timing state lives in `eos::mgm::Stat` through `gOFS->MgmStats`, which is owned by the MGM OFS singleton.

## Dependencies And Integration Points
It depends on `NamespaceStats.hh`, `mgm/ofs/XrdMgmOfs.hh` for the global `gOFS`, and `mgm/stat/Stat.hh` for the concrete statistics sink. `XrdMgmOfs` embeds `mNamespaceStats`, making this adapter the bridge from namespace services back into MGM monitoring/stat reporting.

## Risks And Edge Cases
The code assumes `gOFS` is initialized and `MgmStats` is alive whenever namespace stats are emitted. Calls during early boot, failed boot, or late shutdown would be sensitive to singleton lifetime. The adapter trusts `tag` and does no null validation before forwarding.

## Test Signals
Tests should verify namespace events increment the expected MGM stat tags and execution samples. Shutdown and boot-order tests should cover that namespace code does not emit through this adapter before `gOFS` is valid or after statistics teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.hh -->
# sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.hh

## Purpose
`NamespaceStats.hh` declares the MGM implementation of the namespace statistics interface. It lets namespace services report counters and execution timings without depending directly on MGM's `Stat` class.

## Important APIs, Types, And Functions
`NamespaceStats` derives from `INamespaceStats`. It exposes a default constructor, `Add(const char* tag, uid_t uid, gid_t gid, unsigned long val)`, and `AddExec(const char* tag, float exectime)`, both marked `override`.

## Control Flow
The header contains no executable flow. The interface methods are called by namespace code and implemented in the `.cc` as forwarding methods into MGM stats.

## State And Persistence Behavior
The class declares no members. It is a stateless adapter; all durable or aggregate stat behavior belongs to the target MGM statistics object.

## Dependencies And Integration Points
It includes `mgm/Namespace.hh` for MGM namespace macros and `namespace/interface/INamespaceStats.hh` for the base interface. `XrdMgmOfs.hh` includes this header and embeds `eos::mgm::NamespaceStats mNamespaceStats`.

## Risks And Edge Cases
Because the class is stateless and relies on global MGM state in its implementation, tests and alternate namespace hosts need a valid MGM singleton or a different `INamespaceStats` implementation. Any signature drift in `INamespaceStats` will break this override at compile time.

## Test Signals
Compile coverage should confirm interface conformance. Integration tests should construct the namespace group with MGM stats wired in and assert counters/timings appear in `MgmStats` under the expected tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfs.cc -->
# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfs.cc

## Purpose
`XrdMgmOfs.cc` is the core implementation file for the EOS MGM XRootD OFS plugin. It exports the XRootD filesystem factory functions, constructs and tears down the MGM singleton, starts major service objects, applies Prometheus monitoring configuration, implements common OFS helpers, handles prepare requests, manages redirection/stalling responses, sends FST queries, emits deletion records, and provides audit-decision helpers.

## Important APIs, Types, And Functions
Key exported entry points are `XrdSfsGetFileSystem()` and `XrdSfsGetFileSystem2()`, with `XrdVERSIONINFO` metadata for both. Core implemented methods include the `XrdMgmOfs` constructor/destructor, `OrderlyShutdown()`, `Init()`, `newDir()`, `newFile()`, `Disc()`, `ApplyMonitoringConfig()`, `GetMonitoringConfig()`, `HasStall()`, `HasRedirect()`, `getVersion()`, `prepare()`, `_prepare()`, `_prepare_query()`, `truncate()`, `Emsg()`, `Stall()`, `Redirect()`, `ArchiveSubmitterThread()`, `SubmitBackupJob()`, `GetPendingBkps()`, `DiscoverPlatformServices()`, FUSEX cast helpers, `IsNsBooted()`, `WriteRmRecord()`, `WriteRecycleRecord()`, `Tried()`, namespace boot wait helpers, `prepareOptsToString()`, `SetRedirectionInfo()`, `SendQuery()`, `BroadcastQuery()`, `QueryResync()`, `RemoveDetached()`, `IsMaster()`, and audit allow helpers.

## Control Flow
Plugin loading enters through `XrdSfsGetFileSystem()`. It creates a static `XrdMgmOfs`, initializes logging, calls `Init()` and `Configure()`, sets global `gOFS`, enables default stall/redirection behavior, stores the config filename, and loads the MGM authorization plugin through `XrdAccAuthorizeObject()`. `XrdSfsGetFileSystem2()` delegates to the first factory and advertises prepare-handler support to XRootD through `XRD_PrepHandler`.

The constructor initializes default configuration, reads selected environment overrides for HTTP/FUSEX/gRPC/WNC/REST ports, parses audit environment mode and read suffixes, creates service objects such as REST API manager, ZMQ context, IO stats, HTTP/gRPC servers, egroup refresh, recycler, device tracker, tape GC, and filesystem scheduler. Command implementations from `ofs/cmds/*.inc` are included after core helpers, making this file a compilation hub for many OFS operations.

`ApplyMonitoringConfig()` reads global config keys for Prometheus enabled, port, and cache TTL, falls back to `EOS_MGM_PROMETHEUS_*` environment values, validates values, stops the exporter when disabled, and recreates `PrometheusExporter` when bind address or TTL changes. The exporter is master-gated through `[this]() { return mMaster && mMaster->IsMaster(); }`.

Shutdown flows through `OrderlyShutdown()`: it adds a global stall rule, blocks new in-flight requests, joins/cleans service threads, disables config autosave, clears config references, stops routing, auth workers, converter/drain/geotree/io/fuse/fsck/messaging/recycler/WFE/LRU/egroup/http/Prometheus/WNC/quota/FsView/master, and finally stops the traffic-shaping engine.

## State And Persistence Behavior
Most persistent MGM state is owned through members declared in the header and initialized here. This file directly manages runtime singleton state (`gOFS`), boot timestamps, audit environment flags, service lifetimes, Prometheus runtime state, pending backup queue state, and shutdown state. It writes report records to `mIoStats` for final deletion and recycle deletion, including encoded paths, file ids, timestamps, owner ids, and sizes. `RemoveDetached()` mutates namespace metadata by removing detached containers/files or re-triggering unlink-location deletion behavior.

## Dependencies And Integration Points
The file is heavily integrated with EOS common utilities, namespace services, FsView, QuarkDB-backed namespace machinery, traffic shaping, monitoring, bulk prepare, tape GC, FUSEX, HTTP/gRPC servers, ZMQ messaging, auth plugins, proc commands, quota, recycle, LRU, WFE, fsck, converter, drainer, geotree, XRootD OFS/SFS APIs, and XrdCl query APIs. `NamespaceStats` and `PrometheusExporter` connect this core object to stats and monitoring.

## Risks And Edge Cases
Singleton lifetime is a major risk: many helpers dereference `gOFS` and expect initialized services. `OrderlyShutdown()` assumes several threads and pointers are valid and joinable; partial startup failure paths must avoid double-stop or null dereference. Monitoring reconfiguration binds sockets and may fail due to bad config or port conflicts. `BroadcastQuery()` waits until `responses.size() == endpoints.size()`, so send failures and duplicate/invalid endpoints need careful accounting to avoid waits. `_prepare_query()` allocates a JSON buffer with exact `length()` bytes and copies with `strncpy()` without a terminator; this is acceptable for `XrdOucBuffer` length-delimited data but unsafe if treated as a C string elsewhere. Audit attribute-only mode catches all exceptions and returns false, so namespace lookup failures silently disable auditing for that decision.

## Test Signals
High-value tests include plugin factory initialization, configure failure cleanup, monitoring enable/disable/reconfigure paths, invalid Prometheus config values, master-only scrape behavior, orderly shutdown idempotence, stall and redirect rule behavior, prepare/query JSON response handling, backup queue de-duplication and submitter flow, `SetRedirectionInfo()` under and over 2 KiB, `SendQuery()` and `BroadcastQuery()` success/error/invalid URL paths, `RemoveDetached()` for attached/detached files and containers, namespace boot waits, and audit decisions for global and `sys.audit` attribute modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfs.hh -->
# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfs.hh

## Purpose
`XrdMgmOfs.hh` declares the EOS MGM XRootD OFS plugin class and its large integration surface. It is the central contract for metadata operations, proc/fsctl dispatch, namespace access, authorization, monitoring, service lifecycle, FUSEX broadcasts, traffic shaping, tape support, bulk requests, audit decisions, and global MGM runtime state.

## Important APIs, Types, And Functions
The file defines `NamespaceState` and `namespaceStateToString()`, then declares `class XrdMgmOfs : public XrdSfsFileSystem, public eos::common::LogId`. Public XRootD-facing overrides include `newDir()`, `newFile()`, `Disc()`, `chmod()`, `chksum()`, `exists()`, `FSctl()`, `fsctl()`, `getStats()`, `getVersion()`, `mkdir()`, `FAttr()`, `prepare()`, `rem()`, `remdir()`, `rename()`, `stat()`, `lstat()`, and `truncate()`.

EOS internal APIs include underscored metadata operations such as `_chmod`, `_chown`, `_exists`, `_mkdir`, `_find`, `_rem`, `_remdir`, `_rename`, `_symlink`, `_readlink`, `_stat`, `_access`, `_utimes`, `_touch`, `_attr_ls`, `_attr_set`, `_attr_get`, `_attr_rem`, stripe/replication helpers, versioning helpers, `SendQuery()`, `BroadcastQuery()`, `QueryResync()`, `RemoveDetached()`, sharing helpers, `ApplyMonitoringConfig()`, `GetMonitoringConfig()`, stalling/redirection/routing helpers, path mapping, replica deletion, auth thread methods, FUSEX cast helpers, `SetupProcFiles()`, `OrderlyShutdown()`, `SetRedirectionInfo()`, and audit allow helpers.

Private fsctl/proc dispatch methods include `Access`, `AdjustReplica`, `Checksum`, `Chmod`, `Chown`, `Commit`, `Drop`, `Event`, `FuseStat`, `Fusex`, `Getfmd`, `GetFusex`, `IsMaster`, `Mkdir`, `Open`, `Readlink`, `Redirect`, `Rewrite`, `Statvfs`, `Symlink`, `Utimes`, `Version`, `Xattr`, and `dispatchSFS_FSCTL_PLUGIO()`.

## Control Flow
The header documents the MGM operation pattern: public OFS methods map XRootD client identities to EOS `VirtualIdentity`, apply path mapping, authorization, stall, redirect, and routing macros, then delegate to underscored internal methods that operate on EOS identities and namespace services. Many command bodies are compiled from `ofs/cmds/*.inc`, but their declarations and shared state live here.

Service lifecycle is represented by constructor/destructor plus `Configure()`, `Init()`, `SetupProcFiles()`, and `OrderlyShutdown()`. Threaded subsystems are represented by `AssistedThread` members and worker methods for stats, filesystem config, filesystem monitor, auth master/workers, error logging, and archive submission.

## State And Persistence Behavior
The class owns or references nearly all MGM runtime state: config engine and paths, manager identity, namespace services/views/accounting, namespace state and boot ids, global `MgmStats`, IO stats, traffic-shaping engine, auth plugins and stats, ZMQ context, HTTP/gRPC/REST/WNC servers, Prometheus exporter state, FsView-related locks, routing/path maps, drain/converter/fsck/geotree/recycler/LRU/WFE/device/tape/bulk request engines, QuarkDB contact data, request tracker, pending backup queue, object maps for open files/directories, audit environment flags, and buffer pools.

Some fields correspond to persisted or externally durable locations: namespace changelogs, metadata log directory, proc paths, archive paths, auth token directory, IO report store, temporary find store, comment logs, audit logs, QuarkDB contact/client details, and bulk request proc locations. The header itself does not persist data, but it exposes the ownership and configuration surfaces used by implementation files.

## Dependencies And Integration Points
The header integrates XRootD SFS/OFS interfaces, EOS common utilities, auth protobufs, namespace metadata interfaces and locks, MGM proc/admin commands, traffic shaping, inflight tracking, drain/converter/fsck/geotree/FUSEX/tape/bulk/rest/http/grpc subsystems, QuarkDB namespace contact details, and monitoring. It also declares the global `extern XrdMgmOfs* gOFS`, which many MGM components use as their singleton access point.

## Risks And Edge Cases
This class is broad and stateful, so lock ordering and lifetime are critical. The file-level comments define mutex ordering across FsView, namespace, and quota locks; violating that order can deadlock. Many methods depend on `gOFS`, raw service pointers, and initialized namespace state. The mix of raw pointers, `unique_ptr`, atomics, XRootD buffer ownership, pthread ids, and assisted threads makes partial initialization and shutdown ordering risky. Public/internal method pairs can drift if macro-mediated path, auth, stall, or redirect behavior changes in only one path.

## Test Signals
Tests should cover public-to-internal operation routing, identity mapping and authorization boundaries, lock-order-sensitive metadata mutations, namespace boot/failure states, service startup/shutdown order, path mapping/routing, stall/redirect behavior, fsctl dispatch commands, FUSEX broadcasts, attribute and audit behavior, quota-affecting rename/remove flows, stripe replication/drop operations, query/resync helpers, monitoring reconfiguration, traffic-shaping engine lifetime, and singleton-dependent components during boot and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfs.hh -->
