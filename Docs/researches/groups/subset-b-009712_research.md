# subset-b-009712 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/grafana.dashboard.json -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/grafana.dashboard.json

Purpose: sample Grafana dashboard for a local NFS-Ganesha Prometheus deployment. It is schemaVersion 27, uses datasource `Prometheus`, and has dashboard title `Ganesha (local)`.

Important API/config surface: the visible top-level panels include summary rows plus request rate, 50th percentile latency, throughput, and metadata cache hit ratio graphs. The dashboard also carries nested row panels for latency percentiles, request/response size heatmaps, errors, per-export metrics, per-export latency, RPCs in flight, RPC receive/complete rates, and active clients.

Control flow/state: no runtime logic or persistence beyond Grafana dashboard JSON. The dashboard depends on Grafana loading the JSON and evaluating PromQL queries such as `ganesha:nfs_requests:rate1m`, `ganesha:latency_ms_percentile:rate1m`, `ganesha:nfs_bytes_transferred:rate1m`, and `ganesha:mdcache_cache_hit_ratio:rate1m`.

Dependencies/integration: tightly coupled to `prometheus.rules.yml`, which defines the `ganesha:*` recording rules and percentile labels the dashboard queries. It assumes NFS-Ganesha exports Prometheus metrics for RPCs, NFS operations, bytes, errors, MDCACHE, latency buckets, and per-export variants.

Risks: the dashboard uses older Grafana graph/row structure with nested panels, so migration to newer Grafana may flatten or reinterpret rows. The empty `uid`, no templating variables, and fixed datasource name make it less portable. Panels silently fail if recording rules are not installed.

Test signals: import the JSON into Grafana with the Prometheus datasource named `Prometheus`, load `prometheus.rules.yml`, and confirm the 30 query-bearing panels render non-empty series under Ganesha load.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/grafana.dashboard.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/kvsfs.ganesha.nfsd.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/kvsfs.ganesha.nfsd.conf

Purpose: minimal NFS-Ganesha export sample for the KVSFS FSAL.

Important config surface: one `EXPORT` with `Export_Id = 77`, `Path = "/"`, `Pseudo = /kvsfs`, `Protocols = NFSV3, 4, 9p`, `SecType = sys`, `MaxRead`/`MaxWrite` set to 32768, `Filesystem_id = 192.168`, and a wildcard `client` allowing RW with `no_root_squash`. The `FSAL` block selects `name = KVSFS` and points `kvsns_config` at `/etc/kvsns.d/kvsns.ini`.

Control flow/state: declarative sample only. At daemon load, Ganesha parses the export, initializes the KVSFS FSAL, and uses the external KVS namespace config as persistent backend configuration.

Dependencies/integration: requires a build with KVSFS support, a valid KVS namespace configuration file, and consumers using NFSv3, NFSv4, or 9P. The wildcard client block integrates with Ganesha export access checks.

Risks: permissive wildcard RW/no-root-squash access is unsafe outside a controlled test network. The sample uses a fixed export id and filesystem id, which can collide in multi-export deployments. KVSFS startup will fail or behave incorrectly if `kvsns_config` is missing or stale.

Test signals: run `ganesha.nfsd` with the sample after installing KVSFS prerequisites, mount `/kvsfs`, and verify read/write behavior and protocol negotiation for NFSv3/NFSv4/9P where enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/kvsfs.ganesha.nfsd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/lustre.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/lustre.conf

Purpose: absolute-minimal sample export for the LUSTRE FSAL.

Important config surface: a single `EXPORT` with `Export_Id = 77`, `Path = /nonexistent`, `Pseudo = /nonexistent`, `Access_Type = RW`, and `FSAL { Name = LUSTRE; }`.

Control flow/state: Ganesha parses this export and dispatches operations through FSAL_LUSTRE. The file has no dynamic behavior and no persistent state of its own; Lustre metadata and data state live in the mounted Lustre filesystem.

Dependencies/integration: requires FSAL_LUSTRE built and runtime Lustre client support. The `Path` must be replaced with a valid Lustre mount path in real deployments. NFSv4 clients use `Pseudo` for namespace construction.

Risks: as written, `/nonexistent` is intentionally placeholder and will not be a useful export. The sample omits client restrictions, security flavor tuning, transports, and protocol restrictions, so production deployments must harden it.

Test signals: after substituting a valid Lustre path, validate daemon config parsing, NFSv4 pseudo path traversal, and basic create/read/remove operations against the Lustre-backed export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/lustre.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/mem.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/mem.conf

Purpose: sample export for the in-memory `MEM` FSAL used for testing.

Important config surface: `EXPORT` id `1234` maps arbitrary `Path` and `Pseudo` strings to `FSAL { Name = MEM; }` with RW access. A top-level `MEM` block sets `Inode_Size = 1114112` and `UP_Test_Interval = 20`.

Control flow/state: all filesystem state is volatile and owned by FSAL_MEM in process memory. `Inode_Size` sizes the in-memory inode population needed by pyNFS-style tests; `UP_Test_Interval` starts periodic upcall exercise behavior.

Dependencies/integration: requires MEM FSAL support and integrates mainly with test harnesses, NFS protocol validation, and upcall paths rather than a persistent backing filesystem.

Risks: data disappears on daemon restart. The sample uses arbitrary paths and permissive access, so it is inappropriate for production storage. `UP_Test_Interval` can add background behavior that may confuse latency measurements if left enabled unintentionally.

Test signals: use for parser and protocol smoke tests where persistence is not required; verify creates, lookups, and removes survive only for the running process lifetime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/mem.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.alerts.yml -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.alerts.yml

Purpose: sample Prometheus alert rule for detecting possible Ganesha hangs.

Important config surface: one group, `ganesha-alerts`, containing `GaneshaPotentialHang`. The expression checks that RPCs were received during `$HANG_WINDOW` while `rpcs_completed_total` has zero rate over the same window. The alert fires for `$HANG_WINDOW` and labels severity as `critical`.

Control flow/state: Prometheus evaluates the rule after the operator renders `$HANG_WINDOW` with `envsubst`. No state is stored in the file; Prometheus maintains alert state.

Dependencies/integration: depends on Ganesha Prometheus metrics `rpcs_received_total` and `rpcs_completed_total`. It is meant to be generated by setting `HANG_WINDOW`, for example `2m`, before loading into Prometheus.

Risks: using an unset `$HANG_WINDOW` produces invalid PromQL/YAML for Prometheus. Low traffic services can avoid the alert entirely because it requires received RPCs. Long-running operations with no completions can create false positives if the window is too short.

Test signals: render with a concrete window, run `promtool check rules`, and validate alert behavior by comparing receive and complete counters during normal load and a controlled hang or blocked backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.alerts.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.rules.yml -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.rules.yml

Purpose: Prometheus recording rules that normalize raw Ganesha metrics for dashboards and alerting.

Important config surface: group `ganesha-rules` records RPC in-flight/completion/receive metrics, active-client estimates, NFS request rates, client request rates, per-export rates, byte throughput, request/response size histograms, NFS error rates and ratios, MDCACHE hit/miss ratios, wait time, and latency histogram rates. It computes percentiles for 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, and 99 percentiles using `histogram_quantile`.

Control flow/state: Prometheus periodically evaluates expressions and persists resulting time series according to Prometheus retention. Labels intentionally drop `instance` and `job` for many aggregates and preserve operation/export/status dimensions depending on rule.

Dependencies/integration: required by `grafana.dashboard.json`, which queries the `ganesha:*` records. Depends on raw metrics such as `nfs_requests_total`, `client_requests_total`, `nfs_bytes_*`, `nfs_errors_total`, `mdcache_cache_*`, and `nfs_latency_ms_bucket`.

Risks: ratios can divide by zero and produce NaN/Inf during idle periods. Dropping `instance` and `job` aggregates multiple servers, which is useful globally but can hide per-instance faults. Histogram quantiles are only meaningful if bucket labels and metric cardinality are consistent.

Test signals: run `promtool check rules`, load alongside a Ganesha metrics endpoint, and verify Grafana panels resolve all `ganesha:*` queries without missing series.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.rules.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v3.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v3.conf

Purpose: sample export that exposes a remote NFSv3 server through FSAL_PROXY_V3.

Important config surface: top-level `PROXY_V3 { num_sockets = 64; }` controls the proxy connection pool. The `EXPORT` maps remote `Path = /tmp` to local `Pseudo = /tmp_proxy`, uses RW access, `Squash = no_root_squash`, and `FSAL { Name = PROXY_V3; Srv_Addr = 10.0.0.3; }`.

Control flow/state: Ganesha receives client operations and forwards them to the configured remote server using pooled NFSv3 connections. Persistent file state remains on the upstream NFS server.

Dependencies/integration: requires FSAL_PROXY_V3 support and network reachability to `Srv_Addr`. The pseudo path still matters for Ganesha NFSv4 namespace even though the backend is NFSv3.

Risks: placeholder server address and `/tmp` path must be changed. `no_root_squash` and broad RW access are unsafe for untrusted clients. The socket pool size can stress upstream servers or limit concurrency if poorly tuned.

Test signals: point `Srv_Addr` at a real NFSv3 export, mount through Ganesha, and verify forwarded lookup/create/read/write behavior plus connection-pool behavior under concurrent load.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v3.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v4.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v4.conf

Purpose: sample export that proxies a remote NFSv4 server through FSAL_PROXY_V4.

Important config surface: one `EXPORT` with id `77`, remote `Path = /tmp`, local `Pseudo = /tmp_proxy`, RW access, `Squash = no_root_squash`, and `FSAL { Name = PROXY_V4; Srv_Addr = 10.0.0.3; Use_Privileged_Client_Port = true; }`.

Control flow/state: Ganesha handles client requests and relays file operations/state to the upstream NFSv4 server. Persistent state is owned by the remote server; Ganesha also participates in NFSv4 client/session/state mediation.

Dependencies/integration: requires FSAL_PROXY_V4 and network connectivity to the upstream NFSv4 service. `Use_Privileged_Client_Port` integrates with upstream exports that trust privileged source ports.

Risks: privileged client ports can be required by legacy security policy but are not a complete security boundary. Placeholder address/path must be replaced. Root-unsquashed RW proxying can amplify misconfiguration against the upstream export.

Test signals: configure a real upstream NFSv4 target, mount the Ganesha pseudo path, and validate stateful operations such as open, close, locks, and recovery behavior in addition to basic I/O.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v4.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/rgw.conf

Purpose: sample NFSv4 export of a Ceph RGW namespace through FSAL_RGW.

Important config surface: `EXPORT` id `1` exports `Path = "/"` at `Pseudo = "/"`, restricts `Protocols = 4` and `Transports = TCP`, and provides RGW user/access/secret key fields under `FSAL { Name = RGW; ... }`. The `MDCACHE` block warns that `Dir_Chunk` must not be set to `0`. The `RGW` block points to `ceph_conf`, client `name`, cluster, and optional `init_args`.

Control flow/state: Ganesha maps NFS operations onto RGW object/bucket semantics. Persistent state lives in Ceph/RGW. MDCACHE directory chunking influences POSIX-style `readdir` behavior over object storage.

Dependencies/integration: requires FSAL_RGW, Ceph libraries/configuration, valid RGW credentials, and network access to the Ceph cluster.

Risks: sample credentials are placeholders and must not be committed with real secrets. Exporting object storage as NFS has semantic gaps around directories, renames, permissions, and consistency. Setting `Dir_Chunk = 0` can break RGW `readdir`.

Test signals: validate config parsing with real Ceph settings, mount NFSv4 over TCP, list buckets/objects, and exercise create/read/remove while watching RGW and Ganesha logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw_bucket.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/rgw_bucket.conf

Purpose: sample FSAL_RGW export scoped to a single bucket.

Important config surface: `EXPORT` id `1` uses `Path = "testbucket"` and `Pseudo = "/testbucket"`, allows RW NFSv4 over TCP, and supplies RGW user/access/secret keys. The `RGW` block selects `ceph_conf`, client `name`, and `cluster`.

Control flow/state: NFS clients see the named bucket as the export root; operations are translated to RGW object operations. Persistent state is external in Ceph RGW.

Dependencies/integration: requires FSAL_RGW, a live Ceph cluster, valid RGW user credentials with bucket access, and the bucket named in `Path`.

Risks: real credentials must be protected. Bucket-level export narrows namespace exposure but still has object-storage semantic differences from POSIX. Missing bucket or wrong user permissions result in mount or operation failures that look like NFS errors to clients.

Test signals: mount `/testbucket` over NFSv4, verify object listing and object I/O, and test permission failures with invalid credentials to ensure errors are diagnosable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/rgw_bucket.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/vfs.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/vfs.conf

Purpose: minimal sample export for the generic POSIX VFS FSAL.

Important config surface: a single `EXPORT` with id `77`, `Path = /nonexistent`, `Pseudo = /nonexistent`, RW access, and `FSAL { Name = VFS; }`.

Control flow/state: Ganesha parses the export and delegates operations to FSAL_VFS, which uses the local kernel/filesystem as backing state. The file itself is static configuration.

Dependencies/integration: requires FSAL_VFS support and a real local path substituted for `/nonexistent`. Integrates with local filesystem permissions, export access policy, and NFSv4 pseudo namespace.

Risks: placeholder path makes the sample nonfunctional until edited. Default broad RW access lacks production client, squash, security, and protocol controls.

Test signals: replace the path with a test directory, start Ganesha, mount the pseudo path, and verify local filesystem changes match NFS client operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/vfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/xfs.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/xfs.conf

Purpose: minimal sample export for the XFS-specific FSAL.

Important config surface: one `EXPORT` with id `77`, `Path = /xfs`, `Pseudo = /xfs`, RW access, and `FSAL { Name = XFS; }`.

Control flow/state: Ganesha serves the configured XFS path via FSAL_XFS. Persistent state is the underlying XFS filesystem; this file only supplies daemon configuration.

Dependencies/integration: requires FSAL_XFS support and an XFS-backed path mounted at `/xfs` or an edited equivalent. NFS clients consume the pseudo path.

Risks: assumes `/xfs` exists and is appropriate to export. The sample omits client and security hardening. XFS-specific behavior may diverge from generic VFS tests, so backend-specific validation matters.

Test signals: export an actual XFS directory, mount it, and verify inode/filehandle stability, create/read/write/remove behavior, and daemon logs during startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/xfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/dbus/CMakeLists.txt

Purpose: builds the internal D-Bus support module for NFS-Ganesha.

Important build surface: adds `${DBUS_INCLUDE_DIRS}`, defines object-library source set `gshdbus_STAT_SRCS` containing `dbus_server.c`, `properties_handler.c`, `signal_handler.c`, and `dbus_heartbeat.c`, then builds `add_library(gshdbus OBJECT ...)`. It applies `add_sanitizers(gshdbus)` and compiles as PIC with `-fPIC`.

Control flow/state: no runtime control flow; it determines which D-Bus translation units are compiled into the larger daemon/library target. If `USE_LTTNG` is enabled, the object target depends on generated trace headers and includes generated file properties.

Dependencies/integration: requires CMake variables for D-Bus include dirs and optional LTTng generation. The object library is intended for linkage into Ganesha server components that expose D-Bus admin APIs and heartbeat signals.

Risks: missing DBus headers or generated LTTng files breaks builds. Object-library use means link dependencies must be supplied by the final consumer target, not here.

Test signals: configure with and without `USE_LTTNG`, verify `gshdbus` object compilation, and run daemon startup on a system bus to validate runtime linkage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_heartbeat.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/dbus_heartbeat.c

Purpose: periodic D-Bus heartbeat broadcaster for daemon health.

Important APIs/functions: `dbus_heartbeat_cb(void *arg)` calls `nfs_health()` and, when healthy, emits a D-Bus boolean signal via `gsh_dbus_broadcast(DBUS_PATH HEARTBEAT_NAME, DBUS_ADMIN_IFACE, HEARTBEAT_NAME, ...)`. `init_heartbeat()` registers the callback through `add_dbus_broadcast`.

Control flow/state: heartbeat scheduling is delegated to the D-Bus broadcast loop. The callback returns `BCAST_STATUS_OK` on success, `BCAST_STATUS_WARN` if broadcasting fails, and suppresses signal emission when `nfs_health()` is false. Interval state is stored in the broadcast item created from `nfs_param.core_param.heartbeat_freq * NS_PER_MSEC`.

Dependencies/integration: depends on `nfs_health`, `gsh_dbus_broadcast`, D-Bus names/macros from `gsh_dbus.h`, and core parameter configuration. Integrated by `init_dbus_broadcast()` when heartbeat frequency is positive.

Risks: a failed D-Bus connection degrades to warning return but does not itself stop the daemon. The interval conversion assumes heartbeat frequency units match milliseconds. No unhealthy signal is sent, so listeners infer failure from missing heartbeats.

Test signals: set a positive heartbeat frequency, monitor the system bus for heartbeat signals while healthy, then force broadcast failure or health failure and check logging/absence behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_priv.h -->
## sources/user-network-fs/nfs-ganesha/src/dbus/dbus_priv.h

Purpose: private declarations shared by D-Bus implementation files.

Important API surface: declares `dbus_proc_property` for handling `org.freedesktop.DBus.Properties`; `dbus_append_signal_string` as a simple signal payload helper; and `dbus_send_signal` for constructing and sending a signal with a caller-provided payload callback.

Control flow/state: header only; no state. It establishes internal coupling between `dbus_server.c`, `properties_handler.c`, and `signal_handler.c`.

Dependencies/integration: relies on D-Bus C types (`DBusMessage`, `DBusMessageIter`, `DBusConnection`, `DBusError`) and Ganesha D-Bus interface structures. It is not a public admin API header; it supports the object path/message framework.

Risks: prototypes expose raw pointers and callback contracts without ownership annotations. Payload callbacks must append correct D-Bus types and handle iterator failures; callers must manage connection lifetime externally.

Test signals: compilation of all D-Bus sources is the primary signal. Runtime coverage comes from property Get/GetAll/Set calls and signal emission paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_server.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/dbus_server.c

Purpose: low-level D-Bus service framework for Ganesha object paths, method dispatch, introspection, broadcasts, heartbeat scheduling, and package lifecycle.

Important APIs/types/functions: singleton `thread_state` stores initialization, thread id, wait entry, system-bus connection, D-Bus error, serial, AVL callout registry, and flags. `gsh_dbus_pkginit()` connects to `DBUS_BUS_SYSTEM`, builds optional prefixed name for `org.ganesha.nfsd`, requests bus ownership, initializes broadcasts, and marks initialized. `gsh_dbus_register_path()` registers object paths under `DBUS_PATH`. `dbus_message_entrypoint()` handles Introspect, Properties, and registered interface methods. `gsh_dbus_thread()` runs broadcast callbacks and `dbus_connection_read_write_dispatch`. `gsh_dbus_pkgshutdown()` joins the thread, unregisters object paths, releases the bus name, and unrefs the connection.

Control flow/state: object path handlers are stored in an AVL tree keyed by full path. Broadcast items are kept in a sorted global list protected by `dbus_bcast_lock`; callbacks are rescheduled by interval/count or removed. The D-Bus loop polls every 100 ms and exits on shutdown flag or disconnect.

Dependencies/integration: uses libdbus, pthreads, Ganesha lists/AVL/time helpers, RCU registration, logging, core parameters, and D-Bus interface descriptors from `gsh_dbus.h`.

Risks: global singleton state limits multiple independent bus instances. Broadcast callbacks execute while the broadcast mutex is held, so slow callbacks can block list mutation. `gsh_dbus_pkgshutdown()` joins `gsh_dbus_thrid` even if startup/thread creation sequencing is wrong. Prefix validation only accepts one simple component before the default name.

Test signals: daemon startup on a system bus, introspection XML requests, method calls on registered paths, broadcast callback scheduling, heartbeat delivery, disconnect handling, and clean shutdown without leaked object paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/properties_handler.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/properties_handler.c

Purpose: implementation of the standard `org.freedesktop.DBus.Properties` methods for Ganesha D-Bus objects.

Important APIs/functions: `lookup_interface()` resolves a named interface, with a fake properties interface for scanners. `lookup_property()` finds a property descriptor by name. `dbus_proc_property()` handles `GetAll`, `Get`, and `Set`, appending variants and dictionaries through `DBusMessageIter` and invoking per-property get/set callbacks from `struct gsh_dbus_prop`.

Control flow/state: no persistent state beyond static `props_interface`. `GetAll` iterates readable/readwrite properties and builds `a{sv}`. `Get` opens one variant and calls the property getter. `Set` validates exact argument shape of interface, property name, and variant, then recurses into the variant for the property setter.

Dependencies/integration: depends on D-Bus error names, Ganesha interface/property descriptor structures, and callback functions supplied by each registered object interface. Used by `dbus_message_entrypoint()` when method calls target `DBUS_INTERFACE_PROPERTIES`.

Risks: `Get` calls `(*prop)->get(&variant_iter)` twice before closing the variant, which can duplicate appended data or trigger getter side effects. `GetAll` treats write-only properties as a read-only error rather than omitting them, which may surprise standard clients. Setter failures return false without always setting a detailed D-Bus error.

Test signals: D-Bus clients should exercise `Get`, `GetAll`, `Set`, unknown interface/property, read-only write, and malformed argument paths, including a getter that can detect double invocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/properties_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/signal_handler.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/signal_handler.c

Purpose: helper implementation for sending simple D-Bus signals.

Important APIs/functions: `dbus_append_signal_string()` appends a string payload to a signal iterator and returns `ENOMEM` on append failure. `dbus_send_signal()` creates a signal with object/interface/signal names, initializes an iterator, invokes a payload callback, sends the message, flushes the connection, and unrefs the message.

Control flow/state: only a static signal serial in `dbus_send_signal`. The caller controls connection lifetime, signal names, and payload construction through the callback.

Dependencies/integration: uses libdbus and the private header declarations. It is an older/general helper alongside the variadic `gsh_dbus_broadcast()` in `dbus_server.c`.

Risks: if the payload callback fails, `dbus_send_signal()` returns immediately without unrefing the allocated message, leaking it. A send failure also returns without unrefing. The helper assumes the payload callback appends exactly the signal signature clients expect.

Test signals: unit or integration tests should force payload failure and send failure to catch leaks, and validate a string payload signal on the system bus.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/signal_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/doc/CMakeLists.txt

Purpose: top-level documentation build gate.

Important build surface: if `USE_MAN_PAGE` is enabled, it adds the `man` subdirectory. Otherwise no documentation targets are created from this directory.

Control flow/state: CMake-only conditional; no runtime state.

Dependencies/integration: integrates the Sphinx man-page build into the main CMake tree through `src/doc/man/CMakeLists.txt`. Controlled by the `USE_MAN_PAGE` option.

Risks: disabling `USE_MAN_PAGE` silently skips manpage generation and installation. Any packaging expecting generated man pages must ensure the option and Sphinx dependencies are present.

Test signals: configure with `-DUSE_MAN_PAGE=ON` and verify the `manpages` target appears; configure with it off and verify the docs directory does not add build requirements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/doc/man/CMakeLists.txt

Purpose: generates and installs NFS-Ganesha man pages from reStructuredText using Sphinx.

Important build surface: initializes core man sources (`ganesha-config`, log, cache, export, core) and conditionally appends pages based on feature options such as `USE_9P`, `USE_FSAL_CEPH`, `USE_FSAL_RGW`, `USE_FSAL_XFS`, `USE_FSAL_GLUSTER`, `USE_FSAL_VFS`, `ENABLE_QOS`, `USE_FSAL_LUSTRE`, `USE_FSAL_PROXY_V4`, `USE_FSAL_PROXY_V3`, `USE_FSAL_GPFS`, and `USE_RADOS_RECOV`. It creates output paths under `${CMAKE_BINARY_DIR}/doc`, installs `.8` files to `share/man/man8`, and defines `manpages ALL`.

Control flow/state: CMake expands the source list, registers one Sphinx custom command producing all selected man outputs, and makes the always-built `manpages` target depend on them.

Dependencies/integration: requires `${SPHINX_BUILD}` and `conf.py`. Feature flags align generated documentation with compiled FSAL/protocol support.

Risks: installing files declared as custom-command outputs can be fragile if Sphinx fails or source lists diverge from `conf.py`. Because `manpages` is `ALL`, missing Sphinx breaks normal builds when `USE_MAN_PAGE` is enabled.

Test signals: run a build with representative FSAL flags and verify generated `.8` files match selected `.rst` inputs and install into the expected man8 directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/conf.py -->
## sources/user-network-fs/nfs-ganesha/src/doc/man/conf.py

Purpose: Sphinx configuration that auto-discovers NFS-Ganesha man pages.

Important APIs/functions: `_get_description(fname, base)` parses each `.rst` file's initial title block, expects an underline of `=` characters, splits the title line on `--`, and asserts the page name matches the filename base. `_get_manpages()` scans the directory for `.rst` files except `index.rst` and yields Sphinx `man_pages` tuples with section 8.

Control flow/state: at import time, `man_pages = list(_get_manpages())` discovers pages dynamically. `master_doc = 'index'` is set to satisfy Sphinx toctree expectations.

Dependencies/integration: used by the CMake Sphinx command with `-c` pointing at this directory. It relies on strict heading conventions across all man `.rst` files.

Risks: import-time asserts make documentation builds fail hard on a malformed title, missing `--`, or filename/title mismatch. It discovers all `.rst` files, while CMake selects a feature-dependent subset as explicit dependencies, so generated pages and dependency tracking can diverge.

Test signals: run `sphinx-build -b man` and add a malformed temporary `.rst` to confirm failures are clear. Verify all selected feature pages have titles in `name -- description` form.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/doc/man/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/gtest/CMakeLists.txt

Purpose: top-level GoogleTest build orchestration for Ganesha tests.

Important build surface: pulls in GoogleTest support, sets include paths and unit-test libraries/flags, and adds subdirectories for FSAL API and NFSv4 tests. It also builds standalone tests for examples and core structures such as red-black tree/hash distribution depending on local conditions.

Control flow/state: CMake creates test binaries but this file does not itself run Ganesha. The child `fsal_api` directory defines latency executables that embed/start Ganesha through the shared test harness.

Dependencies/integration: depends on GTest, pthread/C++ support, internal headers, `ganesha_nfsd`, libtirpc, optional LTTng, and gperftools depending on test family.

Risks: build-time availability of optional tracing/profiling libraries can gate tests. Several child tests are benchmarks more than deterministic unit tests and may be expensive to run manually.

Test signals: configure with unit tests enabled, build the gtest tree, and verify expected fsal_api and nfs4 binaries are produced.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/CMakeLists.txt

Purpose: declares FSAL API latency and correctness test binaries.

Important build surface: each test source is assigned to a small source variable, built with `add_executable`, passed through `add_sanitizers`, linked to `ganesha_nfsd`, `${LIBTIRPC_LIBRARIES}`, `${UNITTEST_LIBS}`, `${LTTNG_LIBRARIES}`, `${LTTNG_CTL_LIBRARIES}`, and `${GPERFTOOLS_LIBRARIES}`, and compiled with `${UNITTEST_CXX_FLAGS}`. Covered binaries include lookup, readlink, mkdir, symlink, link, unlink, rename, getattrs, close, commit2, write2, read2, open2, close2, reopen2, setattr2, readdir, mknode, lock_op2, handle_to_key, release, handle_to_wire, and readdir correctness.

Control flow/state: build-only; no `add_test` registrations are present, so CTest will not automatically run these binaries from this file alone.

Dependencies/integration: all binaries depend on the embedded Ganesha test harness and direct FSAL APIs. LTTng and gperftools are linked because many tests expose runtime tracing/profiling CLI flags.

Risks: heavy repetition makes source additions error-prone and easy to forget in one stanza. Linking tracing/profiling libraries for all binaries can complicate minimal environments. Absence of `add_test` reduces CI signal unless another layer invokes binaries.

Test signals: build all declared targets and run selected binaries with `--config`, `--export`, optional `--session`, and optional `--profile` against a prepared export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close2_latency.cc

Purpose: latency/correctness benchmark for the FSAL `close2` object operation.

Important APIs/types/functions: fixtures derive from `gtest::GaneshaFSALBaseTest`. `Close2LoopLatencyTest` preallocates `STATE_TYPE_SHARE` states through `op_ctx->fsal_export->exp_ops.alloc_state` and frees them with `free_state`. Tests call `test_root->obj_ops->open2`, `obj->obj_ops->close2`, `mdcdb_get_sub_handle`, and `fsal_remove`.

Control flow/state: `SIMPLE` opens one file with a state, closes it with `close2`, removes it, drops the object ref, and frees state. `SIMPLE_BYPASS` closes the MDCACHE sub-handle. `LOOP` and `LOOP_BYPASS` create/open 100000 files, time only the close loop, then remove files and release refs.

Dependencies/integration: embeds Ganesha via the gtest environment, needs a configured export id, and can parse common CLI options for config/log/debug/export/LTTng/profile.

Risks: the source contains a malformed-looking chained `opts.add_options()` stanza around the `export` option that should be watched in builds. Loop count is large and consumes many states/files. Bypass mode relies on MDCACHE internals.

Test signals: assertions check zero major status and non-null state/sub-handles; timing output reports average nanoseconds per `close2`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close2_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close_latency.cc

Purpose: latency/correctness benchmark for legacy/helper `fsal_close`.

Important APIs/types/functions: uses `fsal_open2` to create/open files, `fsal_close` for the measured operation, `fsal_remove` for cleanup, and object `put_ref` after removal. Fixture derives from `GaneshaFSALBaseTest`; `CloseFullLatencyTest` can prime many entries but the listed tests use the empty fixture.

Control flow/state: `SIMPLE` opens one file, closes it, removes it, and releases the object. `LOOP` opens 100000 files first, times only `fsal_close` over the object array, then removes and releases each file. Persistent state is in the configured export; test state is arrays of handles.

Dependencies/integration: embedded Ganesha test environment, FSAL open/close/remove helper APIs, and a writable export. CLI parsing supports config/log/debug/export/session/event-list/profile but this file does not use event/profile hooks in test bodies.

Risks: `LOOP_COUNT` must be lower than available file descriptor/state limits, as the file comment notes. Failures during the open phase can leave created files until fixture/environment teardown.

Test signals: status major equals zero for open, close, and remove; stderr prints average `fsal_close` latency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_commit2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_commit2_latency.cc

Purpose: benchmark and smoke-test `commit2` and wrapper `fsal_commit` on an opened file.

Important APIs/types/functions: fixture allocates a share state, opens `TEST_FILE` with `open2`, and closes/removes it in teardown. Tests call `test_file->obj_ops->commit2`, `fsal_commit`, `fsal_write`, and `mdcdb_get_sub_handle`. Writes use `fsal_io_arg`, `fsal_io_direction`, offsets, lengths, and stable/unstable flags.

Control flow/state: `SIMPLE` and `SIMPLE_BYPASS` commit a fixed range. Four write tests perform small/large stable/unstable writes then commit the written range. `LOOP` times one million direct `commit2` calls, and `FSAL_COMMIT` times one million wrapper calls. Persistent file content lives in the export and is cleaned up in teardown.

Dependencies/integration: requires an FSAL supporting `open2`, `write`, and `commit2`; embedded Ganesha environment; optional CLI tracing/profiling values.

Risks: backends may treat stable writes or zero/no-op commits differently, so latency comparisons are backend-specific. One million commit calls can be expensive on durable storage. Stack allocation for I/O args must match buffer sizes.

Test signals: assertions verify write return and commit status; stderr reports average `commit2` and `fsal_commit` latency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_commit2_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_getattrs_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_getattrs_latency.cc

Purpose: benchmarks attribute retrieval through MDCACHE and backend-bypass paths.

Important APIs/types/functions: tests call `obj_ops->getattrs`, `get_optional_attrs`, `obj_ops->lookup`, `mdcdb_get_sub_handle`, `create_and_prime_many`, and `remove_many`. Constants use `DIR_COUNT = 100000` and `LOOP_COUNT = 1000000`.

Control flow/state: simple tests get attributes for the root and its sub-handle. `GET_OPTIONAL_ATTRS` loops over optional attribute collection. Full fixture primes many files. `BIG_CACHED` repeatedly reads the same root handle; `BIG_UNCACHED` looks up many file handles before timing getattrs; bypass variants repeat against sub-handles. References from lookup are released after timing.

Dependencies/integration: embedded Ganesha, MDCACHE debug helper for bypass, and a writable export capable of creating 100000 files.

Risks: arrays sized at one million handles/sub-handles are memory-heavy. `BIG_BYPASS_UNCACHED` stores backend handles after releasing MDCACHE wrapper objects; correctness depends on sub-handle lifetime rules. No `fsal_release_attrs` appears for output attrs, so future attr allocations would need scrutiny.

Test signals: zero major status on all attribute calls and printed average timings for optional, cached, uncached, and bypass getattrs paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_getattrs_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_key_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_key_latency.cc

Purpose: benchmarks FSAL handle-to-key conversion.

Important APIs/types/functions: fixture creates a regular test file using `fsal_create` and removes it in teardown. Tests call `test_file->obj_ops->handle_to_key` or the same operation on `mdcdb_get_sub_handle(test_file)`, using `gsh_buffdesc` for returned key address/length.

Control flow/state: `SIMPLE` and `SIMPLE_BYPASS` validate that conversion produces a non-null address and non-zero length. `LOOP` and `LOOP_BYPASS` reset `fh_desc` and time one million conversions. Persistent state is the one test file.

Dependencies/integration: requires FSAL handle implementation and MDCACHE debug access for bypass. The test harness parses standard config/export/tracing/profiling flags.

Risks: the returned `gsh_buffdesc.addr` ownership is not released in loops, which is safe only if `handle_to_key` points into stable handle memory rather than allocating each call. Backend implementations with allocation semantics would leak under the benchmark.

Test signals: non-null/non-zero handle key assertions and average nanoseconds per `handle_to_key` printed for cached and bypass paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_key_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_wire_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_wire_latency.cc

Purpose: benchmarks converting FSAL object handles to wire-format NFSv4 digests.

Important APIs/types/functions: fixture creates/removes a regular test file. Tests call `obj_ops->handle_to_wire` with `FSAL_DIGEST_NFSV4` and `gsh_buffdesc`; bypass tests use `mdcdb_get_sub_handle(test_file)`.

Control flow/state: simple tests allocate a wire buffer through the operation, verify status, and free `fh_desc.addr`. Loop tests call conversion one million times and free the last buffer after timing. Persistent state is only the test file.

Dependencies/integration: FSAL must implement NFSv4 wire handle conversion. The benchmark integrates with MDCACHE bypass internals and the embedded Ganesha harness.

Risks: if `handle_to_wire` allocates a fresh buffer each call, loop tests free only the final pointer and leak prior allocations. If it reuses a buffer, freeing behavior must match ownership contract. The benchmark focuses latency and does not validate digest contents.

Test signals: zero major status from `handle_to_wire` and average timing output for direct and bypass conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_wire_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_link_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_link_latency.cc

Purpose: benchmarks hard-link creation via object ops and `fsal_link`.

Important APIs/types/functions: fixture creates `TEST_FILE` as source. Full fixture creates `DIR_COUNT = 100000` additional files. Tests call `test_file->obj_ops->link`, `fsal_link`, `lookup`, `fsal_remove`, `mdcdb_get_sub_handle`, `enableEvents`, `disableEvents`, and optional `ProfilerStart/Stop`.

Control flow/state: `SIMPLE` links the source, verifies both source and link by lookup, removes the link, and brackets with LTTng events. `SIMPLE_BYPASS` repeats against backend handles. Loop and full tests create many links, time creation, then remove links. Full variants measure behavior in a large directory.

Dependencies/integration: requires backend hard-link support, MDCACHE, LTTng/gperftools optional hooks, and a writable export.

Risks: hard links are unsupported or restricted on some FSALs/object backends. Large loops create one million names and can exhaust directory capacity or runtime. Bypass cleanup uses backend handles and may diverge from MDCACHE state if errors occur.

Test signals: zero status for link/remove, lookup identity checks in simple tests, and average timings for object-op, wrapper, large-directory, and bypass paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_link_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lock_op2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lock_op2_latency.cc

Purpose: smoke-test and benchmark FSAL byte-range lock operation `lock_op2`.

Important APIs/types/functions: fixture creates a regular test file. Tests prepare `fsal_lock_param_t request_lock` and call `test_file->obj_ops->lock_op2(..., FSAL_OP_LOCK, ...)`; bypass tests operate on `mdcdb_get_sub_handle(test_file)`.

Control flow/state: simple tests perform one lock call. Loop tests perform one million lock calls and time them. Persistent state is the test file plus any lock state registered in the backend/state subsystem.

Dependencies/integration: requires backend `lock_op2` implementation and the Ganesha locking/state code. The test passes null owner/state-like arguments, so it mostly exercises minimal FSAL lock path handling.

Risks: repeatedly taking the same lock without explicit unlock may depend on backend idempotency or owner interpretation. Null lock owner/state arguments may not represent real NFS lock flow. Bypass mode avoids MDCACHE policy checks.

Test signals: zero major status for lock operations and printed average nanoseconds per `lock_op2` for normal and bypass paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lock_op2_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lookup_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lookup_latency.cc

Purpose: benchmarks lookup through MDCACHE, FSAL wrapper, and backend-bypass paths.

Important APIs/types/functions: tests call `root_entry->obj_ops->lookup`, `fsal_lookup`, `test_root->obj_ops->lookup`, `mdcdb_get_sub_handle`, `create_and_prime_many`, `remove_many`, `enableEvents`, `disableEvents`, and optional gperftools profiling. `FILE_COUNT = 100000`; `LOOP_COUNT = 1000000`.

Control flow/state: simple tests verify lookup of the test root from the export root and backend root. Loop tests repeatedly lookup the same root or wrapper API. Full tests prime a large directory and time single or many lookup calls across generated filenames. All returned handles are released.

Dependencies/integration: embedded Ganesha, MDCACHE debug support for bypass, optional LTTng and profiler integration, and a writable export.

Risks: benchmark timing can be dominated by cache state established during fixture priming. Large loop count and profiling can perturb results. Bypass tests compare backend handles to MDCACHE sub-handles, so pointer identity assumptions are backend/MDCACHE specific.

Test signals: zero status, expected handle identity, balanced `put_ref`, event/profiler bracketing, and average lookup timings for wrapper/direct/bypass/large-directory cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lookup_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mkdir_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mkdir_latency.cc

Purpose: benchmarks directory creation via `mkdir` object op and `fsal_create(..., DIRECTORY, ...)`.

Important APIs/types/functions: tests use `obj_ops->mkdir`, `fsal_create`, `lookup`, `unlink`, `fsal_remove`, `mdcdb_get_sub_handle`, and `gtws_subcall` to switch `op_ctx->fsal_export` for backend subcalls. Full fixture pre-populates 100000 files.

Control flow/state: simple tests create one directory, verify lookup returns the created handle, then remove it. Loop tests create one million generated directories and remove them. Full tests repeat in a populated directory, with bypass variants calling backend FSAL directly and using backend unlink cleanup.

Dependencies/integration: writable export with directory creation, MDCACHE internals for bypass, and the embedded Ganesha harness.

Risks: `gtws_subcall` temporarily mutates global/thread operation context and must always restore it. Million-directory loops are expensive and can stress backend directory scaling. The test name `TEST_ROOT` is also used as a child directory name inside the test root, which can be confusing.

Test signals: zero major status, lookup identity checks, cleanup removes all generated directories, and average timings for object-op, wrapper, populated-directory, and bypass mkdir paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mkdir_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mknode_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mknode_latency.cc

Purpose: benchmarks special-node creation using `mknode` and `fsal_create(..., SOCKET_FILE, ...)`.

Important APIs/types/functions: tests call `obj_ops->mknode`, `fsal_create`, `lookup`, `fsal_remove`, `nfs_export_get_root_entry`, and `mdcdb_get_sub_handle`. Full fixture creates/removes 100000 regular files before measuring.

Control flow/state: simple tests create a socket node, verify lookup, release handles, and remove it. Loop tests create one million socket nodes and remove them. Full and bypass variants measure in populated directories and backend-root paths.

Dependencies/integration: requires backend support for `SOCKET_FILE` nodes; many network/object filesystems may not support this operation. Uses embedded Ganesha and MDCACHE bypass hooks.

Risks: bypass tests overwrite `sub_hdl` with `nfs_export_get_root_entry(a_export, &sub_hdl)` after obtaining an MDCACHE sub-handle, which deserves scrutiny for intent and reference ownership. Special node creation may require privileges or be unsupported, causing backend-specific failures.

Test signals: zero status for mknode/create/remove, lookup identity in simple cases, and average timing output for object-op, wrapper, full-directory, and bypass variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mknode_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_open2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_open2_latency.cc

Purpose: benchmarks `open2` through wrapper, object op, bypass, and open-existing-only paths.

Important APIs/types/functions: fixtures prepare `fsal_attrlist attrs_in` and allocate arrays of `STATE_TYPE_SHARE` states. Tests call `fsal_open2`, `obj_ops->open2`, `obj_ops->close2`, `fsal_close`, `fsal_create`, `fsal_remove`, `nfs_export_get_root_entry`, and `mdcdb_get_sub_handle`.

Control flow/state: simple tests open/create one file with share state, close it, remove it, and release state/handle. Loop tests open 100000 generated files while timing wrapper or direct `open2`, then close/remove. `OPEN_ONLY` pre-creates files, then times opening existing files without create cost.

Dependencies/integration: requires open2-capable FSAL, state allocation/free support from export ops, MDCACHE bypass support, and a writable export.

Risks: loops allocate many states/files and can hit resource limits. Bypass tests combine backend handles with Ganesha state objects; correctness depends on compatible state ownership. `OPEN_ONLY` creates files under `root_entry` but later opens/removes via `test_root`, so path relationships must match fixture setup.

Test signals: zero status for create/open/close/remove, non-null backend handles, and average timings for `fsal_open2`, direct `open2`, bypass `open2`, and open-only paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_open2_latency.cc -->
