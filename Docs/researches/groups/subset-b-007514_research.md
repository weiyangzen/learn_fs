<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/resources/hdfs-default.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/resources/hdfs-default.xml

## Purpose
`hdfs-default.xml` is the canonical default configuration catalog for the HDFS module. It documents and supplies defaults for NameNode, DataNode, JournalNode, Secondary NameNode, WebHDFS, balancer, mover, storage policy satisfier, security, HA/federation, caching, snapshots, erasure coding, provided storage, disk balancer, and client behavior. The file explicitly warns operators not to edit it directly; site overrides belong in `hdfs-site.xml`.

## Important APIs, Types, And Functions
- The public surface is a large set of `<property>` entries under a Hadoop `<configuration>` root. Each entry defines a `<name>`, `<value>`, and usually a `<description>`.
- Address and binding keys configure service endpoints: `dfs.namenode.rpc-address`, `dfs.namenode.servicerpc-address`, `dfs.namenode.lifeline.rpc-address`, `dfs.namenode.http-address`, `dfs.datanode.address`, `dfs.datanode.http.address`, `dfs.datanode.ipc.address`, `dfs.journalnode.rpc-address`, and matching `*-bind-host` / HTTPS keys.
- Storage and persistence keys include `dfs.namenode.name.dir`, `dfs.namenode.edits.dir`, `dfs.namenode.shared.edits.dir`, `dfs.datanode.data.dir`, `dfs.journalnode.edits.dir`, checkpoint directories, fsimage compression/parallel-load settings, edit-log retention, and storage directory permissions.
- Block-management keys define replication, block size, safemode thresholds, block reports, invalidation, decommission, stale/slow DataNode avoidance, placement-policy classes, upgrade domains, and EC placement/reconstruction.
- Client and data-transfer keys cover write retries, pipeline replacement policy, socket caches/timeouts, short-circuit reads, mmap cache, hedged reads, dead-node detection, refresh of located blocks, fsck timeouts, congestion backoff, and failover retry policy.
- Security keys configure HDFS permissions, ACLs, xattrs, block access tokens, delegation tokens, Kerberos principals/keytabs for daemons and SPNEGO, data transfer encryption/SASL QOP, WebHDFS OAuth2/CSRF, X-Frame-Options, and admin ACLs.
- HA and federation keys include `dfs.nameservices`, `dfs.nameservice.id`, `dfs.internal.nameservices`, `dfs.ha.namenodes.*`, `dfs.ha.namenode.id`, automatic failover, edit-log tailing/rolling, observer reads, standby checkpointing, stale reads, and failover proxy/resolver settings.
- Operational subsystem keys configure balancer, mover, storage policy satisfier, disk balancer, provided storage alias maps, cache reports, metrics percentiles, audit logging, lock tracing, and GC/lock monitoring.

## Control Flow
The file has no executable control flow; it is loaded by Hadoop's configuration machinery as an XML resource. Runtime behavior emerges when HDFS classes query these keys through Hadoop `Configuration`, typically after combining `hdfs-default.xml`, `hdfs-site.xml`, command-line overrides, and programmatic overrides. Empty defaults often mean "disabled", "auto-detect", or "derive from another property"; several descriptions state fallback chains such as service RPC falling back to NameNode RPC, checkpoint edits dir falling back to checkpoint dir, and internal nameservices falling back to `dfs.nameservices`.

Feature toggles gate major code paths. Examples include HA automatic failover, lifeline RPC, WebHDFS CSRF, HTTP/HTTPS policy, centralized caching, observer nodes, storage policy satisfier mode, disk balancer, provided storage alias map service, data transfer encryption, erasure coding validation, retry cache, and dead-node detection. Numeric throttles and thread counts bound periodic loops such as heartbeats, block reports, directory scans, cache reports, image transfers, edit-log tailing, decommission scans, balancer iterations, and reconstruction work.

## State And Persistence
This file itself is static source data. Its values control persistent HDFS state locations and compatibility-sensitive formats: NameNode namespace images and edit logs, DataNode block directories, JournalNode edit storage, checkpoint images, alias map stores, cache metadata, and storage policy behavior. Several settings affect what state is retained (`dfs.namenode.num.checkpoints.retained`, extra edits retained, edit segment caps) or whether existing state can be read efficiently (`dfs.image.parallel.load`, compression codec, provided storage alias maps). Runtime-only state is also shaped through retry caches, cache reports, mmap/socket caches, dead-node detection state, balancer moved-window tracking, and delegation token/key lifetimes.

## Dependencies And Integration Points
`hdfs-default.xml` is consumed across the HDFS Java codebase through configuration constants and by daemon launchers that include this resource on the classpath. It integrates with Hadoop common configuration merging, the NameNode and DataNode RPC/HTTP servers, Kerberos/SPNEGO login, KMS/key providers for encryption zones, JournalNode/quorum journal managers, WebHDFS/HttpFS clients, native libraries for short-circuit reads and cache hints, operating-system limits such as `RLIMIT_MEMLOCK`, topology resolvers, block placement policy classes, alias map implementations, and web UI/JMX endpoints. Documentation and tests also depend on this file remaining synchronized with code defaults.

## Risks And Edge Cases
- Defaults here are production-impacting even without site overrides; a bad default can change security posture, persistence paths, availability, or cluster performance.
- Empty values are overloaded and must be interpreted consistently by each consumer. Misinterpreting an empty endpoint, principal, resolver, or class name can start unwanted services, disable required services, or silently fall back.
- Many properties are class names. Renaming Java implementations without updating these values breaks startup or feature activation.
- Some descriptions encode constraints not enforced by XML, such as valid percentages, positive intervals, max values, and ratios. Validation must live in code and tests.
- Security toggles have sharp edges: HTTP-only defaults, disabled transfer encryption, optional block tokens, anonymous/simple web settings, and CSRF disabled by default are appropriate only in expected deployment contexts.
- Persistence and compatibility settings such as fsimage parallel loading, compression, format permission, storage policies, and provided storage can affect rollback, rolling upgrades, and data recoverability.
- Large thread counts and throttles for balancer, mover, block reports, cache operations, EC reconstruction, and DataNode transfer can overload NameNode/DataNode resources if changed without capacity testing.

## Test Signals
Useful signals include XML well-formedness validation, Hadoop configuration-load tests, tests that compare `DFSConfigKeys`/`HdfsClientConfigKeys` defaults with `hdfs-default.xml`, daemon startup tests with default configuration, HA/federation mini-cluster tests, secure MiniKDC/SPNEGO tests, WebHDFS HTTP policy/CSRF tests, balancer/mover/storage policy satisfier integration tests, fsimage/edit-log compatibility tests, and docs generation checks that consume the default configuration catalog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/resources/hdfs-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/shellprofile.d/hadoop-hdfs.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/shellprofile.d/hadoop-hdfs.sh

## Purpose
This shell profile registers the HDFS component with Hadoop's shell launcher framework and contributes HDFS jars, resources, webapps, and optional build output to the process classpath.

## Important APIs, Types, And Functions
- Calls `hadoop_add_profile hdfs` when sourced, making the profile available to Hadoop shell initialization.
- Defines `_hdfs_hadoop_classpath`, the profile hook that appends HDFS-specific classpath entries.
- Uses launcher helper APIs `hadoop_add_classpath` and `hadoop_add_profile`.
- Reads launcher environment variables: `HADOOP_ENABLE_BUILD_PATHS`, `HADOOP_HDFS_HOME`, `HDFS_DIR`, and `HDFS_LIB_JARS_DIR`.

## Control Flow
When the profile is sourced, it immediately registers the `hdfs` profile. Later, when Hadoop shell code builds the classpath for this profile, `_hdfs_hadoop_classpath` runs. If `HADOOP_ENABLE_BUILD_PATHS` is non-empty, it adds `${HADOOP_HDFS_HOME}/hadoop-hdfs/target/classes` for developer builds. If `${HADOOP_HDFS_HOME}/${HDFS_DIR}/webapps` exists, it adds `${HADOOP_HDFS_HOME}/${HDFS_DIR}` so webapp resources are visible. It always adds globbed jar paths from the HDFS lib jar directory and the main HDFS directory.

## State And Persistence
The script has no persistent state. Its stateful effect is process-local mutation of the Hadoop classpath assembled by the parent shell launcher. Because it is sourced, function definitions and profile registration live in the caller's shell process.

## Dependencies And Integration Points
The file depends on the Hadoop shell function library already defining `hadoop_add_profile` and `hadoop_add_classpath`. It integrates with Hadoop distribution layout conventions where HDFS jars live under `${HADOOP_HDFS_HOME}/${HDFS_DIR}` and dependency jars under `${HADOOP_HDFS_HOME}/${HDFS_LIB_JARS_DIR}`. It also supports in-tree Maven builds through the `target/classes` path.

## Risks And Edge Cases
- Missing or wrong `HADOOP_HDFS_HOME`, `HDFS_DIR`, or `HDFS_LIB_JARS_DIR` values produce incomplete classpaths.
- The webapp classpath addition is conditional on the `webapps` directory; packaging changes that relocate webapps can break NameNode/DataNode web UI resource discovery.
- Build-path mode may accidentally prefer un-packaged classes over jars if enabled in production-like shells.
- Glob paths are intentionally appended as quoted prefix plus literal `/*`; downstream helper behavior must preserve expansion semantics expected by Hadoop launch scripts.

## Test Signals
Good signals include running HDFS shell commands from an installed distribution, checking `hadoop classpath`/HDFS daemon classpaths include HDFS jars and webapps, developer-build command tests with `HADOOP_ENABLE_BUILD_PATHS=1`, and packaging tests that verify the profile is sourced during daemon/client startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/shellprofile.d/hadoop-hdfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/balancer/balancer.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/balancer/balancer.js

## Purpose
This browser-side script powers the HDFS Balancer web UI overview tab. It fetches Balancer-related JMX beans, normalizes a few fields for the Dust template, derives host/start-time display fields, and renders the `#tmpl-balancer` template into `#tab-overview`.

## Important APIs, Types, And Functions
- The module is an immediately invoked function expression using strict mode and a private `data` object.
- `dust.loadSource(dust.compile($('#tmpl-balancer').html(), 'balancer'))` compiles the page template.
- `BEANS` declares three JMX requests: MBean server info, singleton `Hadoop:service=Balancer,name=BalancerInfo`, and wildcard `Hadoop:service=Balancer,name=Balancer-*`.
- External helper `load_json(BEANS, success, failure)` performs the grouped asynchronous data load.
- `guard_with_startup_progress(fn)` wraps success processing and shows a startup-progress-friendly message for `TypeError`.
- `workaround(balancers)` derives `BlockPoolID` from each balancer bean's `modelerType` suffix after `-`.
- `extractMetrics()` parses `MBeanServerId` into `HostName` and `BalancerStartedTimeInMillis`.
- `HELPERS.helper_date_tostring` formats millisecond timestamps using Moment.js.
- `render()` creates a Dust base with helpers and injects rendered HTML into `#tab-overview`.
- `show_err_msg()` displays the alert panel with a generic Balancer load failure.

## Control Flow
On page load the script compiles the template, declares required JMX beans, and invokes `load_json`. The success callback copies each response into `data`: wildcard balancer beans are passed through `workaround`, while singleton beans use the first returned bean. It then calls `extractMetrics()` and `render()`. The failure callback invokes `show_err_msg`; the success callback is additionally wrapped to catch `TypeError`, which commonly happens when the Balancer HTTP server starts before all expected JMX beans are available.

## State And Persistence
All state is in the page-local `data` object and the DOM. The script persists nothing to browser storage or the server. It mutates bean objects in memory by adding `BlockPoolID`, `HostName`, and `BalancerStartedTimeInMillis` before rendering.

## Dependencies And Integration Points
The script depends on jQuery (`$`), Dust.js, `dust.helpers.tap`, Moment.js, Hadoop's shared `load_json` helper, a DOM template with id `tmpl-balancer`, an overview tab with id `tab-overview`, and alert elements `alert-panel` / `alert-panel-body`. Its backend integration is the Balancer HTTP server's `/jmx` endpoint and the Hadoop JMX object names listed in `BEANS`.

## Risks And Edge Cases
- `workaround` assumes every wildcard bean has a `modelerType` containing `-`; if not, `BlockPoolID` becomes an unexpected substring.
- `extractMetrics` assumes `MBeanServerId` is `host_timestamp`; missing `_` falls back to `"invalid data"`.
- The guard catches only `TypeError`, so template errors or other runtime exceptions may fail silently through the Dust callback path or surface in the browser console.
- `dust.render` ignores its `err` argument and writes `out` unconditionally, which can hide template failures.
- Error display discards the detailed URL/cause passed by the failure callback, reducing diagnosability.
- The UI trusts JMX response shape. Missing `beans[0]` during startup or with incompatible Hadoop versions is the main fragility.

## Test Signals
Useful tests include loading the Balancer UI against a running balancer HTTP server, mocking `/jmx` responses for all three bean queries, checking `BlockPoolID` derivation for multiple block pools, testing startup responses with missing beans, verifying Moment formatting of start time, and browser/JS tests that assert `#tab-overview` receives rendered content or `#alert-panel` appears on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/balancer/balancer.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/datanode/dn.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/datanode/dn.js

## Purpose
This browser-side script powers the HDFS DataNode web UI overview tab. It retrieves the DataNode JMX info bean, converts JSON-encoded fields into structures suitable for templating, derives the displayed host name, and renders the `#tmpl-dn` Dust template.

## Important APIs, Types, And Functions
- The module is an immediately invoked function expression using strict mode and a private `data` object.
- `dust.loadSource(dust.compile($('#tmpl-dn').html(), 'dn'))` compiles the DataNode template.
- `load()` issues `$.get('/jmx?qry=Hadoop:service=DataNode,name=DataNodeInfo', success).fail(show_err_msg)`.
- `workaround(dn)` normalizes JMX bean fields before rendering.
- `node_map_to_array(nodes)` converts an object map into an array and injects each map key as `p.name`.
- `render()` defines `helper_relative_time`, renders template `dn`, and activates `#tab-overview`.
- `show_err_msg()` displays a generic DataNode load failure in the alert panel.

## Control Flow
After initialization, `load()` runs immediately. The JMX success callback takes `resp.beans[0]`, passes it to `workaround`, copies `DatanodeHostname` to `data.dn.HostName`, and calls `render()`. `workaround` parses `dn.VolumeInfo` from a JSON string to an object map, converts that map to an array for template iteration, and parses `dn.BPServiceActorInfo` from a JSON string. `render()` builds a Dust base with a relative-time helper backed by Moment.js, renders `dn`, writes output into `#tab-overview`, and marks the tab active.

## State And Persistence
State is held only in the page-local `data` object and DOM. The script does not persist to local storage or the server. It mutates the JMX bean object by replacing `VolumeInfo` and `BPServiceActorInfo` strings with parsed data and by adding `HostName`.

## Dependencies And Integration Points
The script depends on jQuery, Dust.js, `dust.helpers.tap`, Moment.js, the DOM template `#tmpl-dn`, the overview and alert DOM nodes, and the DataNode HTTP server's `/jmx` endpoint. It is tightly coupled to the JMX schema for `Hadoop:service=DataNode,name=DataNodeInfo`, especially `VolumeInfo`, `BPServiceActorInfo`, and `DatanodeHostname`.

## Risks And Edge Cases
- Missing `resp.beans[0]`, malformed JSON in `VolumeInfo` or `BPServiceActorInfo`, or schema changes throw before render and are not caught by the `.fail()` network handler.
- `node_map_to_array` mutates each volume object by assigning `name`; if a parsed volume entry is not an object, this can fail or produce surprising data.
- `render()` ignores the Dust `err` argument and writes `out` unconditionally.
- `helper_relative_time` assumes the supplied value is seconds and numeric; bad values produce confusing relative-time text.
- The error message is generic and does not expose HTTP status or parse failure details.

## Test Signals
Useful signals include loading the DataNode UI against a live MiniDFSCluster/DataNode, mocking the JMX endpoint with valid and invalid `VolumeInfo`/`BPServiceActorInfo`, verifying volume map-to-array conversion and `HostName` derivation, checking the relative-time helper with known values, and browser tests that assert overview rendering or alert display on request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/datanode/dn.js -->
