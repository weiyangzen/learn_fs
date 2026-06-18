# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsConfigure.cc

## Purpose
`XrdMgmOfsConfigure.cc` is the MGM OFS plugin bootstrap path. It parses `xrd.cf.mgm` directives, initializes process-wide MGM state, connects the namespace to QuarkDB, creates required `/eos/<instance>/proc` namespace directories, starts background services, installs signal handlers, and seeds metrics. It is the file that turns a constructed `XrdMgmOfs` object into a running manager/redirector daemon.

## Important APIs and functions
- `xrdmgmofs_stack(int sig)` implements `SIGUSR1`/`SIGUSR2` stack dump handling. `SIGUSR1` snapshots tracked in-flight threads and signals each with `SIGUSR2`; `SIGUSR2` appends that thread's lock state and stack trace to `/var/eos/md/stacktrace.<time>`.
- `XrdMgmOfs::StartHeapProfiling`, `StopHeapProfiling`, and `DumpHeapProfile` are realtime-signal handlers for jemalloc profiling operations through `mJeMallocHandler`.
- `XrdMgmOfs::Configure(XrdSysError& Eroute)` is the main configuration routine. It sets XrdCl defaults, default MGM paths/URLs, parses config records, validates required QuarkDB and local directories, creates service objects, starts worker threads, and returns non-zero on startup failure.
- `XrdMgmOfs::InitStats()` pre-registers MGM counter names in `MgmStats`, including file, directory, HTTP, FUSEX, quota, redirect, tape REST, workflow, and scheduler counters.
- `XrdMgmOfs::SetupProcFiles()` creates or updates proc pseudo-files such as `whoami`, `who`, `quota`, `reconnect`, and `master`, with `sys.proc` attributes for command-backed reads where appropriate.

## Control flow
`Configure` begins with process defaults: it forces SSS for XRootD clients, enables TPC for zero-size files, initializes string lookup tables, applies environment overrides for archive URL/service class, configures jemalloc signal hooks, and cleans/creates `TmpStorePath`. It derives host, short host prefix, manager ID, manager IP, manager port, and HTTP port from XRootD environment and network APIs.

The config parser loops over `XrdOucStream::GetMyFirstWord()` records. It handles `all.role`, `ofs.tpc redirect`, `mgmofs.*` keys, `xrd.protocol`, and tape REST API keys. Parsed state includes filesystem root, broker URL, instance, namespace library path, QuarkDB cluster/password, qclient persistence directory/flusher settings, authorization plugin, tape enablement and tape GC spaces, prepare defaults, redirector mode, archive/metalog/auth/report directories, FST gateway, trace masks, auth thread/port/local binding, proto workflow options, JWT token path, HTTP port, and tape REST endpoint mappings. Invalid booleans, missing values, inaccessible files, malformed tape REST endpoint versions, and config stream errors set `NoGo`.

After parsing, startup hard-fails without QuarkDB members and password. It also validates broker URL shape, `MgmMetaLogDir`, and `MgmAuthDir`, optionally loads the namespace plugin, derives queue names, configures log fan-out files and aliases, kills/restarts optional `eos-tty-broadcast`, loads external authorization if enabled, sets XRootD redirector role state, creates `QuarkDBConfigEngine`, and opens comment/fuse trace logs.

Runtime services are then initialized: audit log directory and rotation, symmetric key generation from `/etc/eos.keytab`, tape garbage collector validation, HA master state through `QdbMaster`, QDB-backed `MessagingRealm`, optional ZMQ/FUSE serving, `GeoTreeEngine`, mapping, namespace boot, root and `/eos` directory checks, proc/recycle/conversion/devices/archive/clone/workflow/tracker/token/tape REST directories, proc files, bulk request cleaner, replication tracker, device tracker, archive endpoint, stats/archive/error/fs monitor threads, HTTP/gRPC/WNC/REST-gRPC servers, monitoring config, admin socket, tape REST manager config, converter engine, LRU/WFE/device/recycler daemons, FUSE server, IO stats, shutdown/crash/coverage/stack signal handlers, auth master/workers, geotree updater, and scheduler placement strategies.

## State and persistence behavior
This file mutates most long-lived `XrdMgmOfs` fields: names, aliases, ports, queue paths, QuarkDB contact details, auth settings, tape flags, proc paths, archive endpoint, redirector mode, audit flags, scheduler settings, and thread holders. It persists or touches local filesystem state under `/var/tmp/eos`, `/var/eos/ns-queue`, `/var/log/eos/mgm`, the configured XRootD log directory, the auth/metalog/report/archive directories, and `/etc/eos.keytab`. It also persists namespace metadata via `eosView` and service stores, creating system containers and proc pseudo-files when this node is master. QuarkDB-backed state is established through `QdbMaster`, `QuarkDBConfigEngine`, and `MessagingRealm`.

## Dependencies and integration points
The file integrates XRootD config/error/logging/network APIs, EOS common logging/mapping/audit/password/plugin utilities, QuarkDB config and shared-manager messaging, namespace interfaces, FsView/Scheduler/Quota/GeoTree/Converter/Drainer/LRU/Recycler/WFE/ReplicationTracker subsystems, ZMQ and FUSEX serving, HTTP/gRPC services, tape REST/gc components, admin socket, and proc command infrastructure. It also depends on macros and global `gOFS` for cross-component access.

## Risks and edge cases
- `system("rm -rf ...")`, `mkdir -p`, `chown -R`, and `pkill` calls are string-built and operationally sensitive; path validation depends on config trust.
- Several startup checks require local files and writable directories (`/etc/eos.keytab`, logbook files, auth/metalog/report dirs); missing ownership or permissions prevent boot.
- `Configure` is a monolithic sequence with partial side effects before later failure, so failed startup can leave directories, namespace objects, logs, or spawned helper processes behind.
- Tape mode requires `EOS_HA_REDIRECT_READS`; misconfiguration hard-fails after many prior initialization steps.
- Master-only namespace creation means redirectors or slaves depend on already initialized root/proc namespace state.
- Signal handlers perform filesystem and logging work; the design favors debug utility but should be reviewed carefully for async-signal-safety assumptions.
- Config parser booleans often log errors without consistently setting `NoGo`, so invalid optional directives may not uniformly fail startup.

## Test signals
Useful tests include config parser coverage for every directive family, invalid boolean/missing value/malformed tape REST version cases, broker URL and QuarkDB password hard-fail cases, redirector-vs-manager startup differences, proc directory/file creation on master, non-master behavior when root permissions are unset, audit environment combinations, tape enabled/disabled and tape GC space combinations, auth plugin load failures, and signal-driven stack/jemalloc actions in an integration environment. Runtime smoke tests should assert expected `MgmStats` keys, started service threads, REST/gRPC activation flags, scheduler placement strategy loading, and generated proc pseudo-files with correct `sys.proc` attributes.
