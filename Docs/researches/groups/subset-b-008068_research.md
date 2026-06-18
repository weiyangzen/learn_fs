# subset-b-008068 Research

Grouped research for the Apache Ozone Insight CLI module and Recon integration-test slice. Each section is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/pom.xml

Purpose: Maven module descriptor for `ozone-insight`, a hidden Ozone CLI tool packaged as a jar under the `hdds-hadoop-dependency-client` parent. It assembles dependencies needed to inspect live Ozone services through HTTP endpoints, log4j controls, Prometheus metrics, SCM clients, OM classes, and protobuf APIs.

Important build APIs and dependencies: declares picocli, Hadoop common and HDFS client, HDDS CLI/common/config/container/server/SCM modules, Ozone admin/common/interface/manager modules, JAXB API/runtime, and runtime `slf4j-reload4j`. The `classpath.skip` property is false, so this artifact participates in generated classpath handling. The compiler plugin disables annotation processing with `<proc>none</proc>` because config annotations are read reflectively at runtime rather than processed during compilation.

Control flow and integration: SpotBugs uses `dev-support/findbugsExcludeFile.xml`. The enforcer plugin overrides root restrictions to ban selected annotation/processor imports that are inappropriate for this runtime-reflection module. The dependencies reveal integration with picocli command registration, HDDS HTTP/SPNEGO utilities, SCM container operation clients, OM protocol classes, and metrics/log APIs.

State and persistence: no runtime state; it controls artifact assembly and static analysis. Build correctness depends on all referenced Ozone/HDDS modules exporting the classes named in insight implementations.

Risks: the module has broad compile-scope dependencies for a diagnostic CLI, increasing coupling to internal Ozone classes and generated protobuf enums. Disabling annotation processing is intentional but means build-time validation of config annotations is absent here. SpotBugs exclusions file path must exist. Test signals come from the module's JUnit tests for insight filtering, host resolution, config printing, and log processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightPoint.java

Purpose: abstract default implementation of `InsightPoint` that supplies empty metric/config/logger catalogs plus common helper methods for SCM access, log level defaults, RPC metric descriptors, protobuf message counters, and log filtering.

Important APIs: `getMetrics`, `getConfigurationClasses`, and `getRelatedLoggers` return empty lists for subclasses to override. `createScmClient(OzoneConfiguration)` validates `ozone.scm.client.address` and returns a `ContainerOperationClient`. `defaultLevel(verbose)` maps verbose mode to TRACE and normal mode to DEBUG. `addProtocolMessageMetrics` creates one `MetricDisplay` per protobuf enum value filtered by `type`. `addRpcMetrics` defines common Hadoop RPC Prometheus metrics with a caller-supplied servername filter. `filterLog` requires each `filters` entry to appear as `[key=value]` in the log line.

Control flow: insight subclasses call metric helpers while building display groups. Pipeline-backed datanode insight calls `createScmClient`, which fails early if SCM client address is missing. Log streaming calls `filterLog` for post-selection filtering.

State and persistence: stateless except for local descriptor construction. No persistence. It depends on live SCM configuration only when creating an SCM client.

Dependencies and integration: HDDS configuration and SCM client classes, `ContainerOperationClient`, `MetricGroupDisplay`, `MetricDisplay`, `Component`, and `LoggerSource.Level`. Prometheus metric names are hardcoded and must stay aligned with Ozone metric exporters.

Risks and tests: `filterLog` uses regex with raw filter keys/values, so regex metacharacters in values can alter matching. It returns true for an empty map. `createScmClient` depends on `ozone-site.xml` containing SCM client address. `TestBaseInsightPoint` covers single, empty, and multi-filter log matching; helper metric builders and SCM client creation are not directly tested.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightSubCommand.java

Purpose: shared base for picocli insight subcommands. It resolves insight names to concrete `InsightPoint` implementations and maps `Component` objects to HTTP or HTTPS service base URLs.

Important APIs: `getInsight(configuration, selection)` validates a name against `createInsightPoints`. `getHost(conf, component)` prefers component-specified host/port for datanodes and otherwise calls `getComponentAddress` for SCM or OM. `getComponentAddress` chooses HTTP vs HTTPS config keys from `HttpConfig.Policy`, falls back from wildcard bind host to RPC hostname, and preserves the configured/default HTTP service port. `createInsightPoints` registers the stable names consumed by CLI users: SCM node/replica/event/protocol variants, OM key/protocol variants, and datanode pipeline/dispatcher variants.

Control flow: subcommands call `getInsightCommand().getOzoneConf()`, then resolve an insight point by name. Metrics/log/config commands call `getHost` before reaching `/prom`, `/logstream`, `/logLevel`, or `/conf`.

State and persistence: the only state is the injected picocli parent `Insight`. No persistence. `createInsightPoints` instantiates datanode insight points with the active `OzoneConfiguration`, so filters and SCM clients later use the same configuration.

Dependencies and integration: uses Ozone/SCM/OM config keys, `HddsUtils.getHostNameFromConfigKeys`, `HttpConfig`, and all insight point classes. The fallback logic integrates HTTP server bind settings with RPC address settings.

Risks and tests: `getHostOnly` and `getPort` split on the first colon and are fragile for bracketless IPv6 addresses. Unsupported component types throw `IllegalArgumentException`; datanode components must carry host/port. `getInsight` throws a generic `RuntimeException`. `TestBaseInsightSubCommand` covers HTTP-only, HTTPS-only, HTTP-and-HTTPS preference, and fallback-to-RPC behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Component.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Component.java

Purpose: value object identifying the Ozone component instance that owns metrics or logs.

Important APIs: constructors accept `Type`, optional `id`, optional `hostname`, and optional HTTP port. Getters expose those fields. `prefix()` produces display prefixes such as `SCM` or `DATANODE-uuid`. Equality and hash code use only `name` and `id`, intentionally ignoring hostname and port. `Type` enumerates `SCM`, `OM`, `DATANODE`, `S3G`, and `RECON`.

Control flow and integration: `MetricGroupDisplay` and `LoggerSource` embed `Component`. `BaseInsightSubCommand.getHost` either resolves SCM/OM HTTP endpoints from config or uses a component-specified datanode hostname/port. `LogSubcommand` de-duplicates log streaming sources with a `Set<Component>`, so equality semantics matter.

State and persistence: immutable in practice because there are no setters, though fields are not final. No persistence.

Risks and tests: because equality ignores host and port, two datanode components with the same id but different host or port collapse in sets/maps. For ad-hoc datanode filters where id is null, all `DATANODE` components compare equal, which can suppress multiple streams if used together. No direct unit test covers equality or prefix behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Component.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ConfigurationSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ConfigurationSubCommand.java

Purpose: picocli `config` subcommand that prints annotated Ozone configuration keys related to a selected insight point.

Important APIs: `call()` resolves the insight, prints a heading, derives component `Type` from the first dot-separated segment of the insight name, and invokes `showConfig` for each class returned by `InsightPoint.getConfigurationClasses`. `showConfig` creates a new `OzoneConfiguration`, loads remote component config through `getHost(conf, new Component(type)) + "/conf"`, and delegates to `printConfig`. `printConfig` requires a class-level `@ConfigGroup`, scans declared fields only, and prints `@Config` key, default, current value, and description.

Control flow and integration: this subcommand integrates the insight catalog with HDDS config annotations and component HTTP `/conf`. It currently reports only direct declared fields in annotated classes, despite the method comment mentioning superclasses.

State and persistence: no persistent state; remote `/conf` is loaded as an OzoneConfiguration resource for display.

Risks and tests: deriving `Type` from the insight-name prefix assumes all names start with enum-compatible labels. `showConfig` uses a fresh configuration, so address resolution may rely on defaults or local site resources rather than the parent command's exact configuration. It does not URL-authenticate itself; resource loading depends on Hadoop configuration support. `TestConfigurationSubCommand` covers `printConfig` output for `OmConfig`, but not remote `/conf` loading or superclass scanning.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ConfigurationSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Insight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Insight.java

Purpose: top-level hidden picocli command `ozone insight` for inspecting Ozone component logs, metrics, and configuration.

Important APIs: annotated with `@CommandLine.Command`, `hidden = true`, `HddsVersionProvider`, standard help options, and subcommands `ListSubCommand`, `LogSubcommand`, `MetricsSubCommand`, and `ConfigurationSubCommand`. It extends `GenericCli`, inheriting Ozone configuration and command execution behavior. `main` simply constructs `Insight` and runs the supplied args.

Control flow and integration: command-line entry flows through `GenericCli.run`, picocli dispatch, and child subcommands. The parent command supplies `getOzoneConf()` to `BaseInsightSubCommand`.

State and persistence: no local state beyond GenericCli-managed configuration. No persistence.

Risks and tests: because the command is hidden, discoverability depends on explicit use. Failures in subcommands will surface through GenericCli/picocli handling. There is no direct integration test of `Insight.main`; subcommand helper behavior is tested separately.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Insight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightHttpUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightHttpUtils.java

Purpose: static utility for Insight HTTP/HTTPS calls, including SPNEGO-aware connection creation and UTF-8 response reading.

Important APIs: `isSpnegoEnabled(conf)` treats `ozone.http.security.enabled` values `kerberos` or `true` as SPNEGO. `openConnection(url, conf)` creates a Hadoop `URLConnectionFactory` and opens a `HttpURLConnection` with SPNEGO toggle; connection refusal and authentication failure are converted to stderr messages plus null return, while other exceptions become `IOException`. `readResponse` validates HTTP 200 and joins the full response body. `getResponseReader` validates HTTP 200 and returns a streaming `BufferedReader`.

Control flow and integration: metrics and log subcommands call `openConnection` for `/prom`, `/logstream`, and `/logLevel`. `LogSubcommand` owns closing the streaming reader. `MetricsSubCommand` reads a complete Prometheus page into memory.

State and persistence: stateless. No persistence.

Risks and tests: callers must handle null returns from connection/auth failures; current callers usually rethrow runtime exceptions. Full response reading can be expensive if `/prom` grows large, though acceptable for diagnostics. Authentication detection is string-based and tightly coupled to Ozone config semantics. No direct tests cover SPNEGO, non-200 responses, or stderr behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightHttpUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightPoint.java

Purpose: SPI-style interface for a named insight point, defining what the CLI can show for an Ozone subsystem.

Important APIs: `getDescription`, `getRelatedLoggers(verbose, filters)`, `getMetrics(filters)`, `getConfigurationClasses`, and `filterLog(filters, logLine)`.

Control flow and integration: `BaseInsightSubCommand.createInsightPoints` maps string names to implementations. `ListSubCommand` prints descriptions. `LogSubcommand` uses related loggers and `filterLog`. `MetricsSubCommand` fetches metric groups. `ConfigurationSubCommand` uses config classes.

State and persistence: interface only; implementers may be stateless or hold configuration such as datanode insight classes. No persistence contract.

Risks and tests: no type-level guarantee that metric/log components are reachable or that filters are validated before use. Implementations can ignore filters or throw if required filters are missing. Test coverage is indirect through base class and selected command tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ListSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ListSubCommand.java

Purpose: picocli `list` subcommand that prints available insight point names and descriptions, optionally filtered by prefix.

Important APIs: optional parameter `insightPrefix`, `call()` creates insight points with a fresh `OzoneConfiguration`, iterates the linked map, and prints names formatted to 33 characters beside descriptions.

Control flow and integration: relies on `BaseInsightSubCommand.createInsightPoints` preserving deterministic insertion order. It does not need a live cluster except to instantiate datanode insight objects with a configuration.

State and persistence: no persistent state.

Risks and tests: output is written directly to stdout and has no direct unit test. Prefix filtering is simple `startsWith`; empty default lists all. Future insight points requiring expensive construction would affect list latency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ListSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LogSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LogSubcommand.java

Purpose: picocli `log`/`logs` subcommand that temporarily raises related remote loggers and streams matching log events from Ozone HTTP logstream endpoints.

Important APIs: parameters `insightName`, options `-v` and `-f`. `call()` resolves the insight, obtains `LoggerSource` descriptors, sets requested log levels, registers a shutdown hook restoring them to INFO, de-duplicates source components, and streams logs. `streamLog` starts one thread per component and joins them. Per-component `streamLog` opens `<host>/logstream`, filters lines by logger name plus insight filter, formats embedded `<json>...</json>` payloads through `processLogLine`, prefixes output with `[component-prefix]`, and prints. `setLogLevel` calls `<host>/logLevel?log=name&level=level` and requires HTTP 200.

Control flow and integration: depends on `InsightHttpUtils` for authenticated HTTP, `BaseInsightSubCommand.getHost` for endpoint resolution, and Ozone HTTP log endpoints supporting `/logLevel` and `/logstream`. The command is long-running because it joins streaming threads.

State and persistence: remotely mutates logger levels until process shutdown or explicit shutdown hook execution. No local persistence.

Risks and tests: if the process is killed abruptly, remote log levels may stay elevated. Query parameters are not URL-encoded, so logger names or levels with special characters would be risky; current enum/logger values are controlled. `streamLog` can run indefinitely and propagates IO failures as runtime exceptions from worker threads. `processLogLine` uses greedy regex matching across a line and replaces escaped newlines. `TestLogSubcommand` covers JSON newline expansion only, not HTTP, threading, or level restoration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LogSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LoggerSource.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LoggerSource.java

Purpose: descriptor for a remote logger to adjust and stream for an insight point.

Important APIs: stores `Component`, logger name string, and `Level`. Constructors accept an explicit logger name or a component type plus Java class, using `Class.getCanonicalName`. Getters expose fields. `Level` enum supports TRACE, DEBUG, INFO, WARN, ERROR.

Control flow and integration: insight implementations return `LoggerSource` lists. `LogSubcommand` uses them to call `/logLevel`, match streamed log lines by logger name substring, and group source components.

State and persistence: immutable in practice, fields are not final. The descriptor itself is local only; applying it changes remote logging state.

Risks and tests: substring matching can include lines for nested or similarly named loggers. Canonical class names are compile-time coupled to Ozone internals. No direct unit tests for constructors or levels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LoggerSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricDisplay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricDisplay.java

Purpose: descriptor for one Prometheus metric value to display in the Insight CLI.

Important APIs: constructors accept description, metric id, and optional tag filter map. Getters expose id, description, and filter. `checkLine(String)` currently returns false and is unused by `MetricsSubCommand`.

Control flow and integration: insight implementations build these descriptors; `MetricsSubCommand.selectValue` independently matches prometheus lines by `id` and tag filters, then returns the second whitespace-separated token as the value.

State and persistence: local immutable-ish descriptor; filter map reference is mutable if shared externally. No persistence.

Risks and tests: `checkLine` is a stub, which can mislead maintainers. Filter maps are not defensively copied. Metric names and tag names are hardcoded in callers. No direct test covers metric selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricDisplay.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricGroupDisplay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricGroupDisplay.java

Purpose: groups related `MetricDisplay` entries under a component and human-readable section title.

Important APIs: constructors accept a `Component` or component `Type` plus description. `addMetrics` appends descriptors. Getters expose metrics, description, and component.

Control flow and integration: insight implementations return lists of groups. `MetricsSubCommand` collects unique components from groups, fetches each component's `/prom` endpoint once, then prints groups in the supplied order.

State and persistence: mutable list of metrics; no persistence.

Risks and tests: no defensive copy on `getMetrics`; callers can mutate the list. Component equality affects endpoint de-duplication. No direct tests cover grouping behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricGroupDisplay.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricsSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricsSubCommand.java

Purpose: picocli `metrics`/`metric` subcommand that fetches Prometheus metrics for a selected insight point and prints selected values.

Important APIs: option `-f` supplies filters, parameter `insightName` selects an insight. `call()` resolves the insight, computes unique source components from metric groups, downloads `/prom` per component, and prints each group and metric value. `getMetrics(conf, component)` opens `<host>/prom` via `InsightHttpUtils`, reads the response, and splits into lines. `selectValue` scans lines for a metric id prefix and required `key="value"` tags, returning the second whitespace token or `???`.

Control flow and integration: metric descriptors are metadata only; this command implements matching. It integrates with Ozone's Prometheus endpoint and the common HTTP/SPNEGO helper.

State and persistence: no persistent state. Runtime state is the downloaded metrics map.

Risks and tests: `startsWith(metricId)` may match longer metric names sharing the same prefix. Value parsing assumes Prometheus sample lines have at least two space-separated tokens and ignores timestamps. It calls `insight.getMetrics(filters)` twice, which can repeat expensive work for datanode/pipeline insights if metrics become dynamic. No direct tests exercise `/prom` parsing or missing metric behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricsSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/DatanodeDispatcherInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/DatanodeDispatcherInsight.java

Purpose: insight point for the datanode `HddsDispatcher`, covering requests after Ratis replication.

Important APIs: constructor stores `OzoneConfiguration`. `getDatanodeFromFilter` requires `-f datanode=<host_or_ip>`, reads Ozone HTTP policy, chooses default datanode HTTP or HTTPS port, and returns a `DATANODE` component with host and port. `getRelatedLoggers` returns the `HddsDispatcher` logger at TRACE or DEBUG. `getMetrics` adds `hdds_dispatcher_counter` message counters for every `ContainerProtos.Type`. `filterLog` overrides base behavior to always true.

Control flow and integration: CLI callers must provide a datanode filter so `BaseInsightSubCommand.getHost` can contact that datanode directly. Metrics are fetched from that datanode's `/prom`; logs from `/logstream`.

State and persistence: holds configuration only. No persistence.

Risks and tests: it uses default datanode HTTP ports rather than reading per-node configured HTTP address, so non-default datanode ports require enhancement. The HTTP policy branch chooses HTTP port when HTTP is enabled, even under HTTP_AND_HTTPS. Ignoring filters in `filterLog` means log lines are not additionally scoped by `[datanode=...]`. No direct unit test covers missing filter or port selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/DatanodeDispatcherInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/PipelineComponentUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/PipelineComponentUtil.java

Purpose: utility for resolving a pipeline filter into datanode components for pipeline/Ratis insight.

Important APIs: constant `PIPELINE_FILTER = "pipeline"`. `getPipelineIdFromFilters` requires a `pipeline` filter and returns its value. `withDatanodesFromPipeline(scmClient, pipelineId, func)` lists SCM pipelines, finds the matching UUID string, builds a `DATANODE` component for each datanode using uuid, hostname, and hardcoded port 9882, and applies the callback.

Control flow and integration: `RatisInsight` opens an SCM client, retrieves the pipeline id from filters, then uses this utility to add loggers for every datanode in the pipeline.

State and persistence: stateless. Reads live SCM pipeline state through `ScmClient`.

Risks and tests: hardcoded port 9882 ignores HTTP policy and datanode HTTP config. The error message says "No such multi-node pipeline" even for any missing pipeline. The callback return value is ignored and exceptions are not specially handled. No direct tests cover pipeline lookup or missing filters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/PipelineComponentUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/RatisInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/RatisInsight.java

Purpose: insight point for one datanode Ratis pipeline/ring.

Important APIs: constructor stores `OzoneConfiguration`. `getRelatedLoggers` creates an SCM client, resolves the required `pipeline` filter, enumerates datanodes through `PipelineComponentUtil`, and adds logger `org.apache.ratis.server` for each datanode at TRACE or DEBUG. `getDescription` describes the ring. `filterLog` returns true.

Control flow and integration: depends on SCM client address, live pipeline list, and datanode logstream endpoints. It exposes log insight only; it does not define metrics or config classes.

State and persistence: holds configuration. No persistence. Uses try-with-resources to close `ScmClient`.

Risks and tests: `IOException` becomes `UncheckedIOException`, while invalid/missing filters throw `IllegalArgumentException`. Datanode endpoint resolution inherits the hardcoded port behavior from `PipelineComponentUtil`. No direct tests cover Ratis insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/RatisInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/package-info.java

Purpose: package documentation declaring that `org.apache.hadoop.ozone.insight.datanode` contains insight points for Ozone datanodes.

Important APIs/types: no executable API; it attaches package-level Javadoc to datanode insight classes such as `DatanodeDispatcherInsight`, `RatisInsight`, and `PipelineComponentUtil`.

Control flow, state, and persistence: none.

Dependencies and integration: participates in generated Javadoc/package metadata only.

Risks and tests: no runtime risk and no tests needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/KeyManagerInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/KeyManagerInsight.java

Purpose: insight point for OM key-management behavior.

Important APIs: `getMetrics` creates OM metric groups for total keys and key operations plus per-operation success/failure counters for allocate, commit, lookup, list, and delete. `getRelatedLoggers` returns the `KeyManagerImpl` logger on OM. `getDescription` returns "OM Key Manager".

Control flow and integration: metrics are fetched from OM `/prom` and matched by hardcoded metric ids such as `om_metrics_num_key_allocate_fails`. Logs are streamed from OM with the KeyManager logger.

State and persistence: stateless descriptor builder. No persistence.

Risks and tests: metric names must match OM exporter names. Operation pluralization in descriptions is simple string concatenation and cosmetic only. No direct tests cover this insight point.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/KeyManagerInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/OmProtocolInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/OmProtocolInsight.java

Purpose: insight point for the Ozone Manager client RPC endpoint.

Important APIs: `getRelatedLoggers` returns the `OzoneManagerProtocolServerSideTranslatorPB` logger for OM. `getMetrics` adds common RPC metrics filtered by `servername="OzoneManagerService"` and protocol message counters for every `OzoneManagerProtocolProtos.Type` under prefix `om_client_protocol`. `getDescription` identifies the OM RPC endpoint.

Control flow and integration: combines Hadoop RPC metrics and generated OM protobuf enum values for broad operation coverage. Used by `metrics` and `log` subcommands.

State and persistence: stateless. No persistence.

Risks and tests: servername and metric prefix are hardcoded. If RPC server metric tags change, metrics will print `???`. No direct tests cover this insight point.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/OmProtocolInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/package-info.java

Purpose: package-level documentation for Ozone Manager insight points.

Important APIs/types: no executable API; documents the `org.apache.hadoop.ozone.insight.om` package containing `KeyManagerInsight` and `OmProtocolInsight`.

Control flow, state, and persistence: none.

Dependencies and integration: Javadoc/package metadata only.

Risks and tests: no runtime risk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/package-info.java

Purpose: package-level documentation for the Insight framework, described as collecting logs, metrics, and configuration for selected Ozone components.

Important APIs/types: no executable API; documents the root `org.apache.hadoop.ozone.insight` package.

Control flow, state, and persistence: none.

Dependencies and integration: Javadoc/package metadata only.

Risks and tests: no runtime risk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/EventQueueInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/EventQueueInsight.java

Purpose: insight point for SCM internal asynchronous event delivery.

Important APIs: `getRelatedLoggers` returns the SCM `EventQueue` logger at default TRACE/DEBUG level. `getDescription` describes internal async event delivery. It inherits empty metrics and config classes.

Control flow and integration: used by `ozone insight log scm.event-queue` to stream SCM event queue logs.

State and persistence: stateless. No persistence.

Risks and tests: no metric or config support. Logging volume can be high at TRACE. No direct tests cover this insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/EventQueueInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/NodeManagerInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/NodeManagerInsight.java

Purpose: insight point for SCM datanode management and node report/heartbeat processing.

Important APIs: `getRelatedLoggers` returns the `SCMNodeManager` logger. `getMetrics` builds node-counter metrics for every combination of `NodeOperationalState` and `NodeState`, plus heartbeat processed and heartbeat processing failed counters. `getDescription` identifies SCM datanode management.

Control flow and integration: enum-driven metric construction tracks generated HDDS protobuf state enums, reducing manual list drift for node state combinations. Metrics are fetched from SCM `/prom`.

State and persistence: stateless. No persistence.

Risks and tests: generated metric names are lower-cased formatted enum names; exporter naming must match exactly. Adding enum values changes displayed metrics automatically and may expose missing exporter support. No direct tests cover this insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/NodeManagerInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ReplicaManagerInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ReplicaManagerInsight.java

Purpose: insight point for SCM `ReplicationManager`, focused on container health, replication/deletion queues, and EC metrics.

Important APIs: `getRelatedLoggers` returns the `ReplicationManager` logger. `getMetrics` builds three SCM metric groups: container state/health counts, EC replication/deletion/reconstruction counters, and general replication manager inflight/queue/command/timeout/deferred counters. `getConfigurationClasses` exposes `ReplicationManager.ReplicationManagerConfiguration` for the config subcommand. `getDescription` identifies the closed-container replication manager.

Control flow and integration: metrics map directly to Prometheus names emitted by replication manager. The configuration class lets `ConfigurationSubCommand` reflect `@Config` annotations and fetch current values from SCM `/conf`.

State and persistence: stateless descriptor builder. No persistence.

Risks and tests: large hardcoded metric catalog can drift from exporter names. `EcReplicasDeletedTotal` is listed twice with the same metric id, causing duplicate display output. No direct tests cover metric duplication or config exposure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ReplicaManagerInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolBlockLocationInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolBlockLocationInsight.java

Purpose: insight point for the SCM block location protocol endpoint.

Important APIs: related loggers are `ScmBlockLocationProtocolServerSideTranslatorPB` and `SCMBlockProtocolServer`. Metrics include common RPC metrics filtered by `servername="StorageContainerLocationProtocolService"` and message counters for every `ScmBlockLocationProtocolProtos.Type` with prefix `scm_block_location_protocol`.

Control flow and integration: used for protocol-level log streaming and metrics from SCM. It inherits base filter behavior.

State and persistence: stateless. No persistence.

Risks and tests: servername filter appears shared with storage container location service and must match exported tags. No direct tests cover logger list or metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolBlockLocationInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolContainerLocationInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolContainerLocationInsight.java

Purpose: insight point for the SCM container location protocol endpoint.

Important APIs: `getRelatedLoggers` adds `StorageContainerLocationProtocolServerSideTranslatorPB`; it also constructs a `LoggerSource` for `StorageContainerLocationProtocolService` but does not add it to the list. Metrics include common RPC metrics filtered by `servername="StorageContainerLocationProtocolService"` and message counters for every `StorageContainerLocationProtocolProtos.Type` under prefix `scm_container_location_protocol`.

Control flow and integration: metrics and logs are sourced from SCM. The missed `add` means one intended logger is silently omitted.

State and persistence: stateless. No persistence.

Risks and tests: the unadded `LoggerSource` is likely a bug and reduces log coverage. The class Javadoc says block location, which is stale for container location. No direct tests catch the missing logger.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolContainerLocationInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolDatanodeInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolDatanodeInsight.java

Purpose: insight point for SCM's datanode heartbeat/protocol endpoint.

Important APIs: related loggers are `SCMDatanodeProtocolServer` and `StorageContainerDatanodeProtocolServerSideTranslatorPB`. Metrics include common RPC metrics filtered by `servername="StorageContainerDatanodeProtocolService"` and message counters for every `StorageContainerDatanodeProtocolProtos.Type` with prefix `scm_datanode_protocol`.

Control flow and integration: pairs server and translator logs with protocol/RPC metrics to diagnose datanode-to-SCM communication.

State and persistence: stateless. No persistence.

Risks and tests: servername and metric prefix are hardcoded. No direct tests cover this insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolDatanodeInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolSecurityInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolSecurityInsight.java

Purpose: insight point for SCM security protocol behavior.

Important APIs: `getRelatedLoggers` adds `SCMSecurityProtocolServerSideTranslatorPB`; it constructs but does not add a `LoggerSource` for `SCMSecurityProtocolServer`. Metrics include common RPC metrics filtered by `servername="SCMSecurityProtocolService"` and message counters for every `SCMSecurityProtocolProtos.Type` under prefix `scm_security_protocol`.

Control flow and integration: used to inspect SCM security RPC traffic and translator logs.

State and persistence: stateless. No persistence.

Risks and tests: missing `loggers.add` for `SCMSecurityProtocolServer` likely drops intended server logs. Description and Javadoc still mention block location, which is misleading. No direct tests catch the logger omission or stale description.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolSecurityInsight.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/package-info.java

Purpose: package-level documentation for Storage Container Manager insight points.

Important APIs/types: no executable API; documents `org.apache.hadoop.ozone.insight.scm`.

Control flow, state, and persistence: none.

Dependencies and integration: Javadoc/package metadata only.

Risks and tests: no runtime risk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightPoint.java

Purpose: unit test for common `BaseInsightPoint.filterLog` behavior.

Important APIs: creates an anonymous `BaseInsightPoint` with a dummy description and asserts filter matching for one datanode filter, empty filters, and combined datanode plus pipeline filters.

Control flow and test signals: verifies that all configured filters must be present as bracketed `[key=value]` tokens in a log line and that an empty map permits all lines. It also verifies mismatched values reject lines.

State and persistence: no external state or persistence.

Dependencies and integration: JUnit 5 assertions and Java maps only.

Risks and gaps: does not cover `filters == null`, regex metacharacters in filter values, or log lines containing multiple bracketed values. It also does not cover other BaseInsightPoint helpers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightSubCommand.java

Purpose: unit tests for HTTP/HTTPS host resolution in `BaseInsightSubCommand`.

Important APIs: tests `getHost` for HTTP_ONLY SCM/OM configured HTTP addresses, HTTPS_ONLY configured HTTPS addresses, HTTP_AND_HTTPS preference for HTTPS, and fallback from wildcard HTTP/HTTPS bind addresses to SCM/OM RPC hostnames with default web ports.

Control flow and test signals: builds fresh `OzoneConfiguration` instances with specific keys and asserts exact URL strings. It confirms SCM and OM fallback behavior and scheme selection.

State and persistence: no external state.

Dependencies and integration: Ozone/SCM/OM config constants and JUnit 5.

Risks and gaps: does not test explicit `Component` hostname/port, unsupported component types, malformed addresses, IPv6, or absent ports. It also does not verify that `getInsight` resolves all registered names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestConfigurationSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestConfigurationSubCommand.java

Purpose: unit test for configuration annotation printing.

Important APIs: redirects stdout in `@BeforeEach`, restores in `@AfterEach`, creates an `OzoneConfiguration` with a custom `OmConfig.Keys.SERVER_LIST_MAX_SIZE`, invokes `ConfigurationSubCommand.printConfig(OmConfig.class, conf)`, and asserts output contains expected keys, defaults, current custom/default values, and descriptions indirectly through key output.

Control flow and test signals: confirms `printConfig` reads `@Config` metadata and current configuration values for declared fields on an annotated class.

State and persistence: mutates JVM `System.out` for the test duration. No persistence.

Dependencies and integration: AssertJ, JUnit 5, `OmConfig`, `OzoneConfiguration`.

Risks and gaps: does not test classes without `@ConfigGroup`, inherited fields, remote `/conf` loading, or picocli `call()` behavior. Static stdout redirection can interfere with parallel tests if not isolated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestConfigurationSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestLogSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestLogSubcommand.java

Purpose: unit test for `LogSubcommand.processLogLine`.

Important APIs: constructs a log line containing a `<json>...</json>` payload with escaped newlines, calls `processLogLine`, and asserts the result splits into 10 newline-separated lines.

Control flow and test signals: verifies embedded structured payloads are expanded for readability when streamed by the log command.

State and persistence: none.

Dependencies and integration: JUnit 5 only.

Risks and gaps: test method name `filterLog` is misleading. It does not assert exact formatted output, multiple JSON regions, malformed tags, HTTP streaming, log level changes, or shutdown restoration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestLogSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs exclude filter for the Recon integration-test module.

Important APIs: XML root `<FindBugsFilter>` with no exclusion rules.

Control flow and integration: referenced by `integration-test-recon/pom.xml` SpotBugs plugin. It provides a stable file path even though no suppressions are currently needed.

State and persistence: static build configuration only.

Risks and tests: no runtime risk. Empty filter means SpotBugs findings are not suppressed locally; future suppressions would need explicit match rules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/pom.xml

Purpose: Maven descriptor for `ozone-integration-test-recon`, a jar-packaged module containing Recon integration tests against MiniOzoneCluster, Recon server, SCM/OM APIs, REST endpoints, and admin CLIs.

Important build APIs and dependencies: parent is root `ozone`. Dependencies are almost entirely test scoped and include Jackson, Guava, commons-io, JAX-RS, Hadoop common/HDFS client, Apache HTTP client/core, HDDS client/common/config/container/interface/server/SCM/test utilities, Ozone admin/client/common/integration-test test-jar/interface-storage/manager test-jar/mini-cluster/recon/reconcodegen, Ratis common/server test-jar, and slf4j-api.

Control flow and integration: SpotBugs points at the empty local exclude filter. Compiler disables annotation processing. Maven dependency plugin ignores selected Mockito declarations inherited or used elsewhere.

State and persistence: no runtime state; defines test classpath. Tests create MiniOzoneCluster instances, Recon services, Derby Recon DBs, and HTTP/REST clients.

Risks and tests: the module is heavyweight and sensitive to timing because many tests depend on asynchronous Recon/SCM/OM propagation. Broad test-scope dependency set is necessary but can mask unused dependencies. The descriptor itself is covered by Maven build execution rather than unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/StandardOutputTestBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/StandardOutputTestBase.java

Purpose: JUnit 5 base class for tests that need to capture stdout and stderr.

Important APIs: `@BeforeEach setUpStreams` replaces `System.out` and `System.err` with UTF-8 `PrintStream`s backed by byte arrays. `@AfterEach restoreStreams` restores originals. Getter methods expose captured output in default UTF-8 or caller-supplied encodings.

Control flow and integration: `TestNSSummaryAdmin` extends this class to assert CLI output from `OzoneAdmin.execute`.

State and persistence: mutates global JVM streams around each test. No persistence.

Risks and tests: global stream replacement is not safe for parallel tests in the same JVM. Byte arrays are not reset explicitly except by creating a new test instance and before hook; JUnit default per-method lifecycle makes that acceptable. No direct self-test covers this helper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/StandardOutputTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/AbstractTestStorageDistributionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/AbstractTestStorageDistributionEndpoint.java

Purpose: abstract integration-test fixture for Recon storage distribution and pending-deletion endpoints. It centralizes MiniOzoneCluster setup, object creation helpers, OM sync, REST polling assertions, and cleanup.

Important APIs: static `initializeCluster(numDatanodes)` configures aggressive OM/SCM/DN intervals, starts `MiniOzoneCluster` with `ReconService`, waits for readiness, and creates OM/SCM/client handles. `createVolumeAndBucket` creates an FSO bucket with a supplied default replication config. `createOpenKeysAndMultipartKeys` writes open key and multipart state through OM/client APIs. Verification methods poll Recon REST endpoints for `/api/v1/storageDistribution` and `/api/v1/pendingDeletion?component=om|scm|dn`, parse JSON into Recon API types, and assert totals. `syncDataFromOM` directly invokes `OzoneManagerServiceProviderImpl.syncDataFromOM`. `closeAllContainers` fires SCM close events. `cleanup` deletes all filesystem root entries after each test and closes FS; `tear` shuts down the cluster.

Control flow and integration: tests call subclass-specific cluster initialization, create keys/deletions, sync Recon from OM, then retry endpoint assertions until asynchronous Recon/SCM/DN metrics converge. The fixture compares Recon storage totals with SCM datanode usage protos and validates pending deletion at OM metadata, SCM block deletion, and datanode metric layers.

State and persistence: static cluster, conf, OM, SCM, client, and Recon service are shared per subclass. Recon DBs are configured by `ReconService` under the cluster metadata dir. Test FS state is cleaned between methods.

Risks and tests: static shared state requires careful subclass lifecycle. Assertions are wrapped in boolean retry helpers that log debug details, so failures may surface only after wait loops in subclasses. Hardcoded expected byte totals assume specific key counts and replication behavior. Timing-sensitive endpoints need adequate polling. This fixture is itself not tested except through concrete subclasses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/AbstractTestStorageDistributionEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/ReconService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/ReconService.java

Purpose: `MiniOzoneCluster.Service` implementation that embeds a Recon server in integration tests.

Important APIs: constructor allocates free localhost HTTP and datanode addresses and writes Recon address keys. `start(conf)` asserts Recon is not running, resets and sets `ConfigurationProvider`, configures Recon directories and DB URL, creates `ReconServer`, and executes it. `stop()` stops and joins the running server. `toString()` reports live HTTP/HTTPS addresses. `getReconServer()` exposes the server to tests. `configureRecon` sets Recon DB, OM snapshot DB, SCM DB, Derby JDBC URL, safemode wait threshold, and addresses under the cluster metadata directory.

Control flow and integration: MiniOzoneCluster calls `start`/`stop` as an extra service. Tests use `getReconServer` to reach Recon managers, task controllers, HTTP server addresses, and service providers.

State and persistence: stores fixed ports and one mutable `ReconServer`. Persists test Recon data under `<ozone.metadata.dirs>/recon`, including Derby DB and snapshot/SCM DB directories.

Risks and tests: requires `ozone.metadata.dirs` to be set by cluster setup. `start` after `stop` reuses the same address values but reconfigures against the supplied cluster conf, enabling restart tests. Global `ConfigurationProvider` reset can affect other Recon tests in the same JVM. Coverage is indirect through all Recon integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/ReconService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryAdmin.java

Purpose: integration test for Ozone admin namespace summary/du/quota/dist CLIs against a Recon-enabled MiniOzoneCluster.

Important APIs: `@BeforeAll init` creates `OzoneAdmin`, enables FSO paths, sets Recon address, starts a cluster without datanodes plus `ReconService`, creates one random volume with OBS and FSO buckets. Tests execute namespace CLI commands on root, volume, FSO bucket, and OBS bucket paths. `executeAdminCommands` runs `namespace summary`, `namespace du`, recursive/file-name/length `du`, `namespace quota`, and `namespace dist`.

Control flow and integration: extends `StandardOutputTestBase` to capture CLI output. Assertions check absence of invalid volume/bucket errors and presence of empty-data guidance text. OBS test currently checks general output but does not assert the warning mentioned in its comment.

State and persistence: static cluster/client/store/admin and random names across test methods. Captured output is per method through base class. Cluster metadata is test-local.

Risks and tests: no datanodes means commands test namespace metadata paths, not storage data. Output assertions are broad and may miss formatting regressions. The OBS warning comment and assertion are inconsistent. Static cluster shared across tests can retain output-independent namespace state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryMemoryLeak.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryMemoryLeak.java

Purpose: integration tests for HDDS-8565-style NSSummary cleanup when FSO deleted directory entries are hard-deleted from Recon OM metadata tables.

Important APIs: `@BeforeAll init` starts a Recon-enabled 3-datanode cluster, disables frequent OM snapshot tasks by setting long delays, enables ACLs, creates an FSO bucket, configures an Ozone filesystem root, and sets iterate batch size. `testNSSummaryCleanupOnHardDelete` creates `/memoryLeakTest` with 10 subdirs and 5 files each, syncs Recon, verifies summaries exist, deletes the tree, verifies deleted tables, simulates hard delete, and verifies cleanup. `testMemoryLeakWithLargeStructure` repeats at larger scale with 50 subdirs and 20 files each. Helpers create directory structures, sync OM to Recon, wait for `NSSummaryTask` rebuild completion, inspect `DirectoryTable`, `DeletedDirTable`, and `ReconNamespaceSummaryManager`, delete entries from deleted tables, reprocess NSSummary, and verify no deleted-dir rows or matching directory table keys remain.

Control flow and integration: tests drive actual Ozone FS operations, then directly manipulate Recon metadata tables to simulate background hard delete. They reprocess the registered `NSSummaryTask` to validate cleanup logic over current metadata.

State and persistence: static cluster, FS, client, and Recon. Recon metadata and namespace summaries persist in test DBs until cluster teardown. Tests create and delete real FSO namespace entries.

Risks and tests: `expectedDirs` and `expectedFiles` parameters are mostly unused in verification, so the tests assert cleanup presence rather than exact counts. `simulateHardDelete` deletes while iterating a table, which depends on table iterator behavior. Large test can be timing-heavy. The cleanup verification checks directory tables, not direct absence of every NSSummary object by captured object id.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryMemoryLeak.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAndAdminContainerCLI.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAndAdminContainerCLI.java

Purpose: integration tests that compare Recon unhealthy-container reporting with SCM replication-manager/admin-container behavior.

Important APIs: static configuration reduces heartbeat/report/dead-node/task intervals and sets Recon/ReplicationManager task intervals. `@BeforeAll init` starts a 5-datanode cluster with Recon, verifies pipelines and nodes are mirrored, creates an FSO bucket, and writes an Ratis THREE key to establish `containerIdR3`. `testMissingContainer` writes an Ratis ONE key, shuts down all datanodes in its pipeline, waits for zero replicas and SCM missing count, compares Recon unhealthy response, then restarts nodes. Parameterized `testNodesInDecommissionOrMaintenance` drives two pipeline nodes through maintenance or decommission states, waits for op-state and replica-count transitions, and repeatedly compares UNDER_REPLICATED and OVER_REPLICATED Recon responses to SCM reports. Helpers fetch `ReplicationManagerReport`, query Recon unhealthy containers, compare counts and sample IDs, create keys, sync Recon DB with OM, wait for container-key mappings, and extract container IDs from OM key locations.

Control flow and integration: this is a full-cluster timing test spanning datanode lifecycle operations, SCM replication manager, Recon passive SCM/container metadata, OM key metadata, and REST endpoint utility calls. `compareRMReportToReconResponse` requires two stable matching polls to avoid transient agreement while systems converge.

State and persistence: static cluster, SCM client, container managers, bucket, and Recon service. Container state changes persist during the class and are repaired where possible by recommission/restart.

Risks and tests: marked flaky for the maintenance/decommission parameterized test. Timing windows are large but still dependent on cluster scheduling. Static shared state means earlier test failures can affect later tests. The tests validate high-value end-to-end behavior and include explicit stabilization logic for HDDS-15223-style drift.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAndAdminContainerCLI.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAsPassiveScm.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAsPassiveScm.java

Purpose: integration tests for Recon acting as a passive SCM mirror rather than an active SCM command issuer.

Important APIs: `@BeforeEach init` starts a 3-datanode MiniOzoneCluster with Recon and short container/pipeline report intervals. `testDatanodeRegistrationAndReports` waits for Recon pipelines, verifies SCM pipelines exist in Recon, asserts pipeline creation in Recon throws `UnsupportedOperationException`, compares node counts, allocates and writes a container through SCM/datanode pipeline, checks Recon container manager mirrors SCM, and verifies Recon ignores unsupported close-container commands by log capture. `testReconRestart` stops Recon, creates a container and deletes a pipeline in SCM while Recon is down, restarts Recon, verifies nodes are loaded, closed pipeline is absent, and new container appears.

Control flow and integration: exercises Recon's SCM facade, node manager, pipeline manager, container manager, and event queue against a live SCM. Uses `runTestOzoneContainerViaDataNode` to write container data via Xceiver client.

State and persistence: per-test cluster and Recon service. Restart test reuses ReconService addresses and cluster conf; Recon persistent DB path is under cluster metadata.

Risks and tests: waits rely on report intervals and can be timing-sensitive. Log-message assertion couples to exact wording of unsupported command handling. The tests strongly validate passive-mode invariants: no pipeline creation, mirror state, and restart catch-up.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAsPassiveScm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerEndpoint.java

Purpose: integration tests for Recon `ContainerEndpoint.getKeysForContainer`, specifically complete key paths for FSO and OBS buckets.

Important APIs: `@BeforeEach init` clears `ContainerKeyMapperHelper` static state, configures default FSO bucket layout and multiple Recon task threads, starts a 3-datanode cluster with Recon, and creates client/store handles. `testContainerEndpointForFSOLayout` creates an FSO bucket, writes a nested key and a bucket-root key, syncs OM to Recon, waits for event buffer and container-key index, asserts bucket layout, queries keys by container id, and validates key name and complete path. `testContainerEndpointForOBSBucket` performs the same for an OBS bucket with a single key. Helpers instantiate `ContainerEndpoint` directly with Recon server managers, wait until required container key counts are indexed, lookup container IDs through OM key location info, and write key data.

Control flow and integration: drives OM/client writes, Recon OM sync, async Recon task processing, container-key mapper state, and endpoint resource logic without issuing HTTP requests. It waits both for event buffer empty and for container-key counts to avoid races where event queue is drained but batch processing has not updated indexes.

State and persistence: per-test cluster/client/store/recon. Static mapper state is explicitly cleared before and after each test.

Risks and tests: endpoint is constructed with null optional dependencies not needed for `getKeysForContainer`; future endpoint changes may require more wiring. Key/container placement assumptions depend on first block location. The test provides good coverage for path reconstruction differences between FSO and OBS layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerEndpoint.java -->
