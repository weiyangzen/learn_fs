# Research: subset-b-007363

Grouped source research for Hadoop log throttling and metrics2 core, annotations, filters, implementation, and mutable metric support. Each source file section is bounded with reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogThrottlingHelper.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogThrottlingHelper.java

Purpose: Thread-safe helper that lets callers throttle repeated log statements while retaining per-window summary statistics for numeric values. It does not log directly; it returns a `LogAction` telling the caller whether to emit.

Important APIs/types/functions: `LogAction` exposes `shouldLog()`, `getCount()`, and `getStats(int)`. Constructors accept a minimum log period and optional primary recorder name. `record(double...)` records under the default name; `record(String,long,double...)` coordinates named recorders. `getCurrentStats`, `getLogSupressionMessage`, and testing-only `reset` expose state.

Control flow: `record` assigns the first recorder as primary if needed, records values into a `LoggingAction`, checks elapsed monotonic time for the primary, and marks all current actions loggable when the primary fires. Dependent recorders log only after the primary has triggered and before the primary state is consumed.

State and persistence: Maintains `minLogPeriodMs`, `primaryRecorderName`, `lastLogTimestampMs`, a `Timer`, and a map of current `LoggingAction` instances containing counts and `SummaryStatistics`. State is in-memory only and guarded by synchronized methods.

Dependencies/integration: Uses Hadoop `Timer`, Apache Commons Math `SummaryStatistics`, and Hadoop testing annotations. Integrates with any caller-side logger.

Risks/test signals: Incorrect value arity raises errors through `LoggingAction`; callers must not read `DO_NOT_LOG` stats. Tests should cover primary/dependent ordering, reset, elapsed-time boundaries, stat aggregation, and suppression message grammar.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogThrottlingHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/AbstractMetric.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/AbstractMetric.java

Purpose: Base immutable metric abstraction implementing `MetricsInfo` and requiring concrete metric value, type, and visitor dispatch.

Important APIs/types/functions: Constructor stores non-null `MetricsInfo`; `name`, `description`, and protected `info()` delegate to it. Subclasses implement `Number value()`, `MetricType type()`, and `visit(MetricsVisitor)`. Equality and hashing include info and value.

Control flow: Concrete implementations in `metrics2.impl` wrap numeric values, expose the right `MetricType`, and call the matching visitor method. No mutation is performed after construction.

State and persistence: In-memory final `MetricsInfo` only; no persistence or synchronization.

Dependencies/integration: Used by `MetricsRecord`, record builders, sink filtering, JMX cache generation, and string/JSON builders. Depends on Hadoop preconditions and relocated Guava `Objects`.

Risks/test signals: Equality ignores concrete subclass except via info/value, so tests should verify counter/gauge handling through `type` and visitor dispatch. Null info should fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/AbstractMetric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricStringBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricStringBuilder.java

Purpose: `MetricsRecordBuilder` implementation that renders tags and metrics into a delimited string for diagnostics and textual dumps.

Important APIs/types/functions: Constructors configure prefix, suffix, separator, and key/value separator. `add(MetricsInfo,Object)` and `tuple(String,String)` append formatted entries. Overrides all tag, counter, and gauge builder methods plus `toString`.

Control flow: Each builder callback delegates to `add` or `tuple`; `setContext` writes a context tuple; `parent()` returns the configured collector. Separators are inserted only after the first entry.

State and persistence: Maintains a `StringBuilder`, formatting strings, and a parent collector reference. It is mutable, not synchronized, and intended for one build pass.

Dependencies/integration: Consumes `MetricsTag` and `AbstractMetric` from records and can be used wherever a `MetricsRecordBuilder` is accepted.

Risks/test signals: Formatting regressions affect human-readable output and tests should cover empty output, custom separators, tag/metric order, and all primitive overloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricStringBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricType.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricType.java

Purpose: Public enum identifying immutable metric semantics as `COUNTER` or `GAUGE`.

Important APIs/types/functions: The enum constants are consumed by `AbstractMetric.type()`, visitor logic, builders, and downstream sinks.

Control flow: No executable control flow beyond enum initialization.

State and persistence: Enum singletons only; no mutable state.

Dependencies/integration: Implemented by counter and gauge concrete metric classes and used by output adapters that need to distinguish monotonic counters from point-in-time gauges.

Risks/test signals: Adding enum constants would require visitor and sink changes. Existing tests should assert concrete metric classes return the expected type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsCollector.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsCollector.java

Purpose: Public collection interface used by `MetricsSource` implementations to start one or more records during a snapshot.

Important APIs/types/functions: `addRecord(String)` and `addRecord(MetricsInfo)` return `MetricsRecordBuilder` instances.

Control flow: Implementations decide whether a record is accepted by filters before returning the builder. Sources call this from `getMetrics`.

State and persistence: Interface only; implementation state lives in `MetricsCollectorImpl`.

Dependencies/integration: The central handoff from source code to metrics records. `MetricsSystemImpl` reuses one collector during sampling and clears it between sources.

Risks/test signals: Builder parent/end-record chaining depends on this contract. Tests should ensure source implementations can add multiple records and filtered records are omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsCollector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsException.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsException.java

Purpose: Runtime exception class for metrics framework configuration, registration, and type errors.

Important APIs/types/functions: Provides message-only, cause-only, and message-plus-cause constructors.

Control flow: Thrown throughout registry duplicate checks, annotation processing, filters, and metrics system misuse paths.

State and persistence: Standard exception state only.

Dependencies/integration: Extends `RuntimeException`; subclasses include implementation configuration exceptions.

Risks/test signals: Because it is unchecked, code paths must validate inputs early and produce actionable messages. Tests should assert duplicate metric/tag and unsupported annotation type failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsFilter.java

Purpose: Abstract plugin contract for accepting or rejecting metrics sources, records, tags, and metric names.

Important APIs/types/functions: Extends `MetricsPlugin`; declares `accepts(String)`, `accepts(MetricsTag)`, and `accepts(Iterable<MetricsTag>)`. Provides a default record-level `accepts(MetricsRecord)` based on record name and tags.

Control flow: Metrics collection and sink adapters call filters before recording, JMX caching, or sink publication. Concrete filters compile configuration during `init`.

State and persistence: Base class has no state; concrete filters keep compiled patterns.

Dependencies/integration: Used in source, record, and metric filtering in `MetricsCollectorImpl`, `MetricsSourceAdapter`, `MetricsSinkAdapter`, and `MetricsConfig`.

Risks/test signals: Filter semantics combine name and tag acceptance; tests should cover whitelist-only, blacklist, and mixed tag/name scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsInfo.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsInfo.java

Purpose: Public metadata interface for metric, tag, and record identity.

Important APIs/types/functions: `name()` returns the stable programmatic name; `description()` returns human-readable context.

Control flow: No direct control flow; implementations are immutable value objects or enums.

State and persistence: Interface only. Interned implementations in `Interns` reduce duplicate metadata allocations.

Dependencies/integration: Used by every metric builder, tag, record, annotation factory, and registry. `MsInfo` is a built-in enum implementation for metrics-system fields.

Risks/test signals: Name stability affects JMX attribute names and sink schemas. Tests should verify names avoid illegal whitespace where registries enforce it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsJsonBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsJsonBuilder.java

Purpose: `MetricsRecordBuilder` implementation that accumulates tags and metrics in insertion order and serializes them as JSON.

Important APIs/types/functions: Constructor records a parent collector. `tuple` inserts into a `LinkedHashMap`. Overrides tag, add, context, counter, gauge, parent, and `toString`.

Control flow: Builder calls add entries to `innerMetrics`; `toString` uses a static Jackson `ObjectWriter`, returning a stack trace string if serialization fails.

State and persistence: Mutable map per builder instance; no synchronization or persistence. Duplicate keys overwrite prior entries.

Dependencies/integration: Uses Jackson, Commons Lang `ExceptionUtils`, SLF4J, and metrics model classes. Useful for JSON dumps, not the main sink pipeline.

Risks/test signals: `add(AbstractMetric)` stores `metric.toString()` rather than the raw number, so consumers must not assume every metric value is numeric JSON. Tests should cover duplicate key overwrite and serialization shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsJsonBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsPlugin.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsPlugin.java

Purpose: Minimal lifecycle contract for configurable metrics plugins.

Important APIs/types/functions: `init(SubsetConfiguration conf)` initializes a plugin instance from a configuration subset.

Control flow: `MetricsConfig.getPlugin` reflectively creates plugin classes and invokes `init`; filters and sinks implement this contract.

State and persistence: Interface only; implementations decide their in-memory configuration state.

Dependencies/integration: Depends on Apache Commons Configuration `SubsetConfiguration`; base contract for `MetricsFilter` and sink implementations.

Risks/test signals: Plugin initialization failures surface during metrics system startup. Tests should cover class loading, missing class names, and configuration property propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsPlugin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecord.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecord.java

Purpose: Public immutable snapshot view of one metrics record.

Important APIs/types/functions: Exposes `timestamp`, `name`, `context`, `tags`, and `metrics`.

Control flow: Implementations derive context from a `Context` tag and provide iterable tags/metrics to sinks, filters, and JMX adapters.

State and persistence: Interface only. `MetricsRecordImpl` stores timestamp plus immutable tag/metric lists.

Dependencies/integration: Produced by `MetricsRecordBuilderImpl`, wrapped by `MetricsRecordFiltered`, iterated by `MetricsSinkAdapter`, and exposed to `MetricsSink.putMetrics`.

Risks/test signals: Tags and metrics should be immutable from callers' perspective. Tests should assert context fallback and filtering behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecord.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecordBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecordBuilder.java

Purpose: Fluent abstract builder for constructing one metrics record.

Important APIs/types/functions: Abstract methods add tags, existing metrics, context, counters, and gauges for int, long, float, and double values. `parent()` returns the collector; `endRecord()` returns `parent()`.

Control flow: Source code calls builder methods during `getMetrics`; concrete builders create immutable metric objects, text, or JSON.

State and persistence: Abstract only; mutable state is in implementation builders.

Dependencies/integration: Common API used by mutable metrics, annotations-generated sources, metrics system self-source, and custom source implementations.

Risks/test signals: Fluent chaining relies on every override returning `this`. Tests should cover all primitive overloads and parent/end chaining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecordBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSink.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSink.java

Purpose: Public plugin contract for receiving metrics records.

Important APIs/types/functions: Extends `MetricsPlugin`; declares `putMetrics(MetricsRecord record)` and `flush()`.

Control flow: `MetricsSinkAdapter` filters buffered records, calls `putMetrics` for each accepted record, then flushes once per consumed buffer.

State and persistence: Interface only; concrete sinks may persist to files, network services, or in-memory stores.

Dependencies/integration: Registered with `MetricsSystem`; can be configured reflectively from metrics properties.

Risks/test signals: Slow or throwing sinks interact with queue backpressure and retry logic. Tests should simulate put/flush failures, closeable sinks, and context/filter matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSource.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSource.java

Purpose: Public source contract for snapshotting metrics into a collector.

Important APIs/types/functions: `getMetrics(MetricsCollector collector, boolean all)` emits records and metrics. `all` requests all metrics instead of only changed values.

Control flow: `MetricsSystemImpl.sampleMetrics` invokes sources through `MetricsSourceAdapter`, which injects tags and catches source exceptions.

State and persistence: Interface only; source objects own their own counters, gauges, and registries.

Dependencies/integration: Sources are registered directly or created from annotations by `MetricsSourceBuilder`.

Risks/test signals: Source exceptions are logged and swallowed by the adapter, so tests should assert system sampling continues after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystem.java

Purpose: Public abstract service API for registering sources, sinks, callbacks, and controlling metrics publication.

Important APIs/types/functions: Defines `init`, `start`, `stop`, `shutdown`, source/sink `register`, `unregisterSource`, `publishMetricsNow`, JMX MBean start/stop, `currentConfig`, `getSource`, and `Callback` lifecycle hooks with `AbstractCallback` no-op base.

Control flow: Concrete implementation orchestrates configuration load, timer scheduling, callback invocation, sampling, and sink publication.

State and persistence: Abstract only, but contract implies global service lifecycle and restart behavior.

Dependencies/integration: `DefaultMetricsSystem` exposes a singleton; components register metrics through this API.

Risks/test signals: Callback exceptions should not break service lifecycle in `MetricsSystemImpl`. Tests should cover duplicate registration, source unregistering, shutdown reference counting, and immediate publish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystemMXBean.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystemMXBean.java

Purpose: JMX management interface for controlling and inspecting the metrics system.

Important APIs/types/functions: Exposes start/stop, MBean start/stop, current configuration, and immediate publish operations to JMX clients.

Control flow: `MetricsSystemImpl` implements this interface and registers a control MBean during initialization.

State and persistence: Interface only; operations mutate the concrete metrics system lifecycle.

Dependencies/integration: Registered via Hadoop `MBeans` under the metrics system prefix and control name.

Risks/test signals: JMX callers can start or stop the metrics system outside normal code paths. Tests should verify idempotent start/stop warnings and config string rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystemMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsTag.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsTag.java

Purpose: Immutable tag value object implementing `MetricsInfo`.

Important APIs/types/functions: Constructor stores `MetricsInfo` and string value. `name`, `description`, `value`, protected `info`, equality, hash, and `toString` provide metadata and value semantics.

Control flow: No complex flow; record builders and registries construct tags and records expose them.

State and persistence: Final metadata and value only; no persistence.

Dependencies/integration: Tags are used for context, hostname, source filters, record filtering, JMX tag attributes, and sink records.

Risks/test signals: Null metadata/value validation and equality behavior matter for filter maps and tests. Context tag value drives `MetricsRecordImpl.context()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsTag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsVisitor.java

Purpose: Visitor interface for type-specific metric handling.

Important APIs/types/functions: Declares `counter` overloads for int and long and `gauge` overloads for int, long, float, and double.

Control flow: Concrete `AbstractMetric` classes call the matching method from `visit`.

State and persistence: Interface only.

Dependencies/integration: Allows consumers to process immutable metrics without instanceof checks. Used by metric classes and potential sinks/exporters.

Risks/test signals: Concrete metric visitor dispatch must match both type and primitive width. Tests should cover every overload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metric.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metric.java

Purpose: Runtime annotation for fields and methods that should become Hadoop metrics.

Important APIs/types/functions: `Type` enum includes `DEFAULT`, `COUNTER`, `GAUGE`, and `TAG`. Annotation attributes include `value`, `about`, `sampleName`, `valueName`, `always`, `type`, and `interval`.

Control flow: `MetricsSourceBuilder` scans fields and methods, and `MutableMetricsFactory` maps annotated members to mutable metrics or method-backed metrics.

State and persistence: Annotation metadata retained at runtime.

Dependencies/integration: Used with `@Metrics` on source classes and consumed by reflection utilities.

Risks/test signals: Unsupported field or method return types throw `MetricsException`. Tests should cover all annotation value-name combinations and quantile interval handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metrics.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metrics.java

Purpose: Runtime type annotation that marks a class as a metrics source and supplies source metadata.

Important APIs/types/functions: Attributes include `name`, `about`, and `context`, with defaults allowing class-name based metadata.

Control flow: `MetricsSourceBuilder.initRegistry` reads this annotation, builds source `MetricsInfo`, creates or reuses a `MetricsRegistry`, and tags it with the context.

State and persistence: Runtime annotation metadata only.

Dependencies/integration: Used by metrics system self-source and application metric source classes.

Risks/test signals: Missing annotation is acceptable only if explicit `@Metric` fields/methods can use a default registry. Tests should verify registry reuse and context tag emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/package-info.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/package-info.java

Purpose: Package-level audience and stability metadata for metrics annotations.

Important APIs/types/functions: Applies public/evolving classification to `org.apache.hadoop.metrics2.annotation`.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies/integration: Documentation and compatibility signal for public annotation APIs.

Risks/test signals: No direct tests needed beyond package compilation and generated Javadocs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/AbstractPatternFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/AbstractPatternFilter.java

Purpose: Shared base for include/exclude metrics filters backed by compiled name and tag patterns.

Important APIs/types/functions: Config keys are `include`, `exclude`, `include.tags`, and `exclude.tags`. `init` compiles patterns; `accepts(MetricsTag)`, `accepts(Iterable<MetricsTag>)`, and `accepts(String)` implement whitelist/blacklist logic. Subclasses provide `compile(String)`.

Control flow: Includes win first, excludes reject next, and include-only mode rejects nonmatching inputs. Tag pattern entries must match `name:pattern`.

State and persistence: Stores compiled RE2/J `Pattern` objects in maps and fields; in-memory only.

Dependencies/integration: Loaded from `MetricsConfig` as source, record, and metric filters. `GlobFilter` and `RegexFilter` only differ in pattern compilation.

Risks/test signals: Tag syntax errors throw `MetricsException`; include-only semantics are easy to regress. Tests should cover single-tag and iterable-tag paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/AbstractPatternFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/GlobFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/GlobFilter.java

Purpose: Public filter that interprets configured include/exclude strings as Hadoop glob patterns.

Important APIs/types/functions: Overrides `compile(String)` to use `GlobPattern.compile`.

Control flow: All accept/reject behavior is inherited from `AbstractPatternFilter`.

State and persistence: Only inherited compiled patterns after initialization.

Dependencies/integration: Useful in metrics configuration where operators prefer glob syntax for source, record, metric, or tag filters.

Risks/test signals: Glob-to-regex conversion should be tested for common wildcard patterns, tag filters, and include-only mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/GlobFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/RegexFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/RegexFilter.java

Purpose: Public filter that interprets include/exclude configuration strings as regular expressions.

Important APIs/types/functions: Overrides `compile(String)` using RE2/J `Pattern.compile`.

Control flow: Inherits pattern acceptance ordering from `AbstractPatternFilter`.

State and persistence: Inherited compiled pattern fields and tag-pattern maps.

Dependencies/integration: Instantiated by `MetricsConfig.getFilter` for regex filter class names.

Risks/test signals: Invalid regex syntax fails during initialization. Tests should cover full-match behavior because `matcher(...).matches()` is used rather than find/contains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/RegexFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/package-info.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/package-info.java

Purpose: Package metadata for public/evolving metrics filters.

Important APIs/types/functions: Applies classification annotations to the filter package.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies/integration: Documents compatibility of `GlobFilter` and `RegexFilter`.

Risks/test signals: Package-info should compile and appear in generated API docs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/AbstractMetricsRecord.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/AbstractMetricsRecord.java

Purpose: Partial `MetricsRecord` implementation that centralizes equality, hashing, and string rendering for concrete records.

Important APIs/types/functions: Implements `equals` by comparing timestamp, name, description, tags, and metric elements. Implements `hashCode` from name, description, and tags, and `toString` with timestamp, metadata, tags, and metrics.

Control flow: Concrete records provide all `MetricsRecord` accessors; the abstract base calls those accessors when comparing or rendering.

State and persistence: Stateless abstract base; all record state lives in concrete subclasses or wrappers.

Dependencies/integration: Base for `MetricsRecordImpl` and filtered record wrappers.

Risks/test signals: `hashCode` intentionally omits timestamp and metrics despite `equals` including them, which is legal but can increase hash collisions. Tests should cover equality for metric iterable contents and toString rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/AbstractMetricsRecord.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MBeanInfoBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MBeanInfoBuilder.java

Purpose: Builds JMX `MBeanInfo` metadata from the latest metrics records for a source.

Important APIs/types/functions: Constructor accepts name and description; `reset(Iterable<MetricsRecordImpl>)` rebuilds attributes; `get()` returns `MBeanInfo`.

Control flow: `MetricsSourceAdapter.updateInfoCache` resets the builder using sampled records after refreshing the attribute cache. Tags and metrics become JMX attributes with names matching adapter tag/metric naming rules.

State and persistence: Mutable builder state for current attribute descriptors; cached in `MetricsSourceAdapter`.

Dependencies/integration: Uses JMX metadata types and Hadoop metrics records.

Risks/test signals: Multi-record attribute suffixing must align with `MetricsSourceAdapter` attr cache. Tests should cover tag attributes, metric attributes, duplicate names, and cache refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MBeanInfoBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterInt.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterInt.java

Purpose: Immutable integer counter metric implementation.

Important APIs/types/functions: Constructor stores `MetricsInfo` and int value; `value()` returns `Integer`; `type()` returns `COUNTER`; `visit` calls `MetricsVisitor.counter(info,value)`.

Control flow: Created by `MetricsRecordBuilderImpl.addCounter` and consumed by records, sinks, JMX, and visitors.

State and persistence: Final primitive value and inherited metadata; no mutation.

Dependencies/integration: Extends `AbstractMetric` and implements counter visitor dispatch.

Risks/test signals: Tests should verify type, boxed value, visitor overload, equality, and toString inherited behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterInt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterLong.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterLong.java

Purpose: Immutable long counter metric implementation.

Important APIs/types/functions: Stores long value, returns `Long`, reports `MetricType.COUNTER`, and dispatches to the long counter visitor overload.

Control flow: Built by `MetricsRecordBuilderImpl.addCounter(MetricsInfo,long)`.

State and persistence: Final value and metadata only.

Dependencies/integration: Used for long mutable counters, stats sample counts, and system dropped-publish counters.

Risks/test signals: Visitor overload selection and large long values should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterLong.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeDouble.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeDouble.java

Purpose: Immutable double gauge metric implementation.

Important APIs/types/functions: Stores double value, returns `Double`, reports `MetricType.GAUGE`, and visits the double gauge overload.

Control flow: Created by builders for floating-point gauges such as averages and standard deviation.

State and persistence: Final value and inherited metadata only.

Dependencies/integration: Used by mutable stats and rolling-average metrics.

Risks/test signals: Tests should cover NaN/infinity behavior if upstream stats can produce them, plus visitor dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeDouble.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeFloat.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeFloat.java

Purpose: Immutable float gauge metric implementation.

Important APIs/types/functions: Stores float value, returns `Float`, reports `GAUGE`, and calls `MetricsVisitor.gauge(info,float)`.

Control flow: Created by record builders and mutable float gauges.

State and persistence: Final value and metadata.

Dependencies/integration: Supports the public float gauge builder overload and `MutableGaugeFloat`.

Risks/test signals: Cover visitor overload and precision-preserving value boxing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeFloat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeInt.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeInt.java

Purpose: Immutable integer gauge metric implementation.

Important APIs/types/functions: Stores int value, returns `Integer`, reports `GAUGE`, and visits the int gauge overload.

Control flow: Produced by `MetricsRecordBuilderImpl.addGauge(MetricsInfo,int)`.

State and persistence: Final primitive and metadata.

Dependencies/integration: Used for queue sizes, active source counts, and mutable int gauges.

Risks/test signals: Tests should ensure it is not reported as counter and that visitor dispatch uses the gauge path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeInt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeLong.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeLong.java

Purpose: Immutable long gauge metric implementation.

Important APIs/types/functions: Stores long value, returns `Long`, reports `GAUGE`, and dispatches to `MetricsVisitor.gauge(info,long)`.

Control flow: Built by record builders for long-valued instantaneous readings.

State and persistence: Final value and metadata only.

Dependencies/integration: Supports `MutableGaugeLong` and long gauge builder overloads.

Risks/test signals: Large value and visitor-overload tests protect against int truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeLong.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBuffer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBuffer.java

Purpose: Immutable-ish container grouping sampled records by source name for sink publication.

Important APIs/types/functions: Contains iterable `Entry` objects where each entry has a source name and iterable records. Copy constructor is used by waitable immediate buffers.

Control flow: `MetricsBufferBuilder` creates buffers during sampling; `MetricsSinkAdapter` iterates entries and records for filtering and sink calls.

State and persistence: Holds lists of entries/records in memory for one publication cycle.

Dependencies/integration: Links `MetricsSystemImpl.sampleMetrics` to asynchronous sink queues.

Risks/test signals: Buffer copy semantics matter for immediate publish. Tests should assert iteration order and stable records after builder completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBufferBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBufferBuilder.java

Purpose: Simple builder for collecting source-name to metrics-record entries before publishing.

Important APIs/types/functions: `add(String, Iterable<MetricsRecordImpl>)` appends entries and `get()` returns a `MetricsBuffer`.

Control flow: `MetricsSystemImpl.sampleMetrics` calls `add` once per accepted source, then calls `get`.

State and persistence: Mutable in-memory list for the current snapshot only.

Dependencies/integration: Consumes records from `MetricsSourceAdapter.getMetrics`.

Risks/test signals: Tests should cover empty sources, multiple sources, and preservation of source order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBufferBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsCollectorImpl.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsCollectorImpl.java

Purpose: Concrete collector that accumulates filtered record builders during one source snapshot.

Important APIs/types/functions: `addRecord(MetricsInfo/String)` creates `MetricsRecordBuilderImpl`; `getRecords()` materializes non-null records; `iterator()` exposes builders; `clear()` resets; package setters configure record and metric filters.

Control flow: Record name filtering happens before adding a builder to the list. `getRecords` asks each builder to apply final tag filtering and build immutable records.

State and persistence: Mutable list of builders plus current filters; reused by `MetricsSystemImpl` and cleared between sources.

Dependencies/integration: Used by `MetricsSourceAdapter` and rolling-average internals.

Risks/test signals: Reuse requires `clear()` after every source. Tests should cover record filter rejection, metric filter rejection, and builder iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsCollectorImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfig.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfig.java

Purpose: Metrics-specific configuration loader and plugin factory built on Commons Configuration.

Important APIs/types/functions: Static `create`, `loadFirst`, constants for sink/source keys, `subset`, `getInstanceConfigs`, `getPlugin`, `getFilter`, `getClassName`, `getString`, and `toString` helpers.

Control flow: Loads the first available metrics properties file for a prefix, extracts per-instance subconfigs, overlays default keys, resolves classes with class loaders, instantiates plugins, and calls plugin `init`.

State and persistence: Wraps loaded properties in memory. No writes except stringification by `MetricsSystemImpl.currentConfig`.

Dependencies/integration: Used by `MetricsSystemImpl.configure*` to create sinks, filters, periods, queues, and source configs. Depends on Commons Configuration, reflection, Hadoop class loading utilities, and SLF4J.

Risks/test signals: Misconfigured class names, missing files, and default-instance overlay behavior are primary risks. Tests should cover prefix lookup order, plugin init, class-loader fallback, and instance regex parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfigException.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfigException.java

Purpose: Package-private exception specializing `MetricsException` for configuration problems.

Important APIs/types/functions: Constructors mirror message and cause variants.

Control flow: Thrown by config loading/stringifying/class instantiation failures and caught by `MetricsSystemImpl.init` to allow nonfatal startup in some cases.

State and persistence: Standard exception state.

Dependencies/integration: Extends public metrics exception but remains implementation-local.

Risks/test signals: Catching this class in init makes startup behavior different from other runtime errors. Tests should distinguish typo/nonfatal config failures from fatal programming errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfigException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordBuilderImpl.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordBuilderImpl.java

Purpose: Concrete record builder that applies filters and creates immutable metric objects.

Important APIs/types/functions: Stores parent collector, timestamp, record info, metric/tag lists, filters, and acceptable flag. Implements all builder methods and `getRecord`.

Control flow: Record-level name filtering sets `acceptable` at construction. Metric methods check metric filter before creating `MetricCounter*` or `MetricGauge*`. `getRecord` also applies tag-based record filtering before returning `MetricsRecordImpl`.

State and persistence: Mutable lists during building; returns unmodifiable views to the record constructor. Timestamp captured at construction.

Dependencies/integration: Used by `MetricsCollectorImpl`, mutable metrics, and annotations-generated sources.

Risks/test signals: `add(MetricsTag)` and `add(AbstractMetric)` bypass filter checks, so callers must use proper paths where filtering is expected. Tests should cover timestamping, context tag, metric filters, and unmodifiable records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordBuilderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordFiltered.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordFiltered.java

Purpose: Wrapper around a `MetricsRecord` that filters its metrics iterable for sink delivery.

Important APIs/types/functions: Delegates metadata, timestamp, context, and tags to the wrapped record; `metrics()` returns only metrics accepted by a `MetricsFilter`.

Control flow: `MetricsSinkAdapter.consume` wraps records when a metric filter is configured for a sink.

State and persistence: Holds wrapped record and filter references; no mutation.

Dependencies/integration: Uses Guava-style filtering/iterables or equivalent to lazily filter metrics.

Risks/test signals: Lazy filtering must remain stable while iterated by sinks. Tests should ensure tags are not filtered and metric-name predicates are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordFiltered.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordImpl.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordImpl.java

Purpose: Concrete immutable metrics record implementation.

Important APIs/types/functions: Constructor stores `MetricsInfo`, timestamp, tags, and metrics. Implements `timestamp`, `tags`, `metrics`, and string rendering.

Control flow: Built by `MetricsRecordBuilderImpl.getRecord` after filtering.

State and persistence: Holds record snapshot lists in memory; no persistence. Lists are expected to be unmodifiable from builder.

Dependencies/integration: Consumed by buffers, sink adapters, JMX source adapters, and filters.

Risks/test signals: Snapshot immutability and context tag resolution are critical. Tests should cover toString, iteration, empty metrics, and context extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSinkAdapter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSinkAdapter.java

Purpose: Runtime adapter that isolates sinks behind filtering, queueing, retry, latency, and dropped-update metrics.

Important APIs/types/functions: `putMetrics` enqueues periodic buffers, `putMetricsImmediate` enqueues a waitable buffer, `publishMetricsFromQueue` runs in a daemon `SubjectInheritingThread`, `consume` sends accepted records to the sink, and `snapshot` reports adapter stats.

Control flow: Periodic puts are accepted only when logical time matches sink period. Queue full increments dropped counters. The consumer thread drains all queued buffers, retries exceptions with backoff, clears queue after retry exhaustion, and suppresses repeated errors. Immediate puts wait on a semaphore until consumed or timeout.

State and persistence: Holds filters, queue, thread flags, retry parameters, and registry metrics (`latency`, `dropped`, `qsize`) in memory.

Dependencies/integration: Created by `MetricsSystemImpl` from config or explicit sink registration. Uses `SinkQueue`, sink plugin, Hadoop IO cleanup, time utilities, and mutable metrics.

Risks/test signals: Queue full, sink exceptions, immediate timeout, closeable cleanup, and retry backoff are high-risk. Tests should also cover source/context/record/metric filters and queue gauge refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSinkAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSourceAdapter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSourceAdapter.java

Purpose: Runtime adapter for a metrics source, adding filters, injected tags, and DynamicMBean exposure.

Important APIs/types/functions: Implements JMX `getAttribute`, `getAttributes`, `getMBeanInfo`, read-only mutator stubs, `getMetrics`, `startMBeans`, `stopMBeans`, and cache update helpers.

Control flow: JMX access calls `updateJmxCache`, which refreshes after TTL and releases the adapter lock while invoking source metrics to avoid lock-order deadlocks. `getMetrics` applies record/metric filters, catches source exceptions, and injects system tags into each builder.

State and persistence: Tracks JMX attribute cache, MBean info cache, TTL timestamps, MBean name, and clear/refresh flags. State is in-memory and synchronized around cache changes.

Dependencies/integration: Registered by `MetricsSystemImpl`; uses Hadoop `MBeans`, `MetricsCollectorImpl`, filters, records, tags, and time utilities.

Risks/test signals: Deadlock avoidance, TTL behavior, stale attribute names, duplicate record suffixing, source exceptions, and read-only JMX behavior need tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSourceAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSystemImpl.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSystemImpl.java

Purpose: Central metrics service implementation that loads configuration, registers sources/sinks, samples sources on a timer, publishes buffers to sinks, and exposes control/system metrics.

Important APIs/types/functions: Implements `MetricsSystem`, `MetricsSource`, and `MetricsSystemMXBean`. Key methods: `init`, `start`, `stop`, source/sink `register`, callback registration, `sampleMetrics`, `publishMetrics`, `publishMetricsNow`, `configure*`, `getMetrics`, and `shutdown`.

Control flow: `init` increments ref count and starts unless standby. `start` invokes callbacks, loads config, configures sinks/sources/system tags, and schedules a daemon timer. Timer events sample filtered sources into a `MetricsBuffer`, include self metrics, and publish through sink adapters. Stop cancels timer, stops adapters, clears config, and invokes callbacks.

State and persistence: Maintains source/sink maps for active/all instances, callbacks, collector, metrics registry, injected tags, config maps, monitoring flag, timer, period, logical time, MBean name, self-source, and mini-cluster ref count. State is synchronized and in-memory.

Dependencies/integration: Uses `MetricsConfig`, adapters, annotation builder, `DefaultMetricsSystem`, Hadoop `MBeans`, hostname lookup, mutable system stats, filters, and sinks.

Risks/test signals: Lifecycle idempotency, ref-count shutdown, callback exception handling, config errors, period GCD calculation, source/sink re-registration after restart, and immediate publish should be tested. Timer concurrency and self-metrics inclusion are key integration risks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSystemImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MsInfo.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MsInfo.java

Purpose: Built-in `MetricsInfo` enum for common metrics-system tags and counters.

Important APIs/types/functions: Enum constants cover context, hostname, active/all source and sink counts, and likely other system metadata. `description()` returns the stored description; `toString()` returns name/description style metadata.

Control flow: No dynamic control flow beyond enum use.

State and persistence: Enum constants with descriptions.

Dependencies/integration: Used by registries, record builders, and `MetricsSystemImpl.getMetrics`.

Risks/test signals: Renaming constants changes emitted metric/tag names. Tests should assert public system metric names and descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MsInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/SinkQueue.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/SinkQueue.java

Purpose: Half-blocking circular queue for sink publication where producers never block and consumers block for data.

Important APIs/types/functions: `enqueue`, `consume`, `consumeAll`, `dequeue`, `front`, `back`, `clear`, `size`, and `capacity`. Nested `Consumer` callback consumes objects.

Control flow: `enqueue` returns false when full. Consumer operations enforce a single active consumer, wait for data, call the consumer outside some synchronized paths, then dequeue and clear the consumer lock. `clear` refuses while a consumer is active.

State and persistence: Fixed object array plus head, tail, size, and current consumer thread. In-memory only and synchronized around queue state.

Dependencies/integration: Used by `MetricsSinkAdapter` to buffer `MetricsBuffer` objects.

Risks/test signals: The circular index order, single-consumer guard, interrupt handling, and full-queue drop behavior are critical. Tests should cover capacity one, clear during consumption, and consumeAll order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/SinkQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/package-info.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/package-info.java

Purpose: Package metadata for private metrics implementation classes.

Important APIs/types/functions: Applies Hadoop private audience classification to `org.apache.hadoop.metrics2.impl`.

Control flow: No runtime behavior.

State and persistence: No state.

Dependencies/integration: Documents that adapter, config, buffer, and concrete metric classes are implementation details.

Risks/test signals: Compilation/Javadoc only; no behavioral tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsFactory.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsFactory.java

Purpose: Provides a default `MutableMetricsFactory` singleton for annotation-based source construction.

Important APIs/types/functions: Static `getAnnotatedMetricsFactory` or similar accessor returns the singleton factory.

Control flow: Lazy or static initialization supplies the factory to `MetricsAnnotations.newSourceBuilder`.

State and persistence: Process-local singleton factory; no persistence.

Dependencies/integration: Bridges public annotation helper APIs to `MutableMetricsFactory`.

Risks/test signals: Factory replacement or singleton initialization changes could affect all annotated sources. Tests should verify stable default factory and custom extension points if present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsSystem.java

Purpose: Public static access point for the default Hadoop metrics system singleton and source-name uniqueness support.

Important APIs/types/functions: Provides initialize/instance/shutdown helpers, mini-cluster mode controls, source-name allocation/removal, and convenience registration around `MetricsSystemImpl`.

Control flow: Static methods delegate lifecycle to the singleton implementation, track mini-cluster mode, and generate unique source names when duplicate registration is allowed before monitoring starts.

State and persistence: Static process state including singleton system, source-name tracking, and mini-cluster mode flag. No persistence.

Dependencies/integration: Used by Hadoop components that do not manage their own metrics system and by `MetricsSystemImpl` during registration and shutdown.

Risks/test signals: Static state can leak across tests. Test suites should reset/shutdown, verify duplicate-name suffixing, mini-cluster ref counting, and source name removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/Interns.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/Interns.java

Purpose: Factory/cache for canonical `MetricsInfo` and `MetricsTag` value objects.

Important APIs/types/functions: `info(name,desc)` returns interned metadata; `tag(info,value)` and overloads return interned tags. Internal cache helpers bound cache sizes.

Control flow: Lookup-or-create paths reuse existing objects for repeated metadata/value combinations.

State and persistence: Static in-memory caches only; bounded to avoid unbounded growth.

Dependencies/integration: Used throughout registry, annotations, builders, system metrics, and tags.

Risks/test signals: Cache key equality and maximum size behavior are important. Tests should cover object reuse, different descriptions, different tag values, and cache eviction/bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/Interns.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MethodMetric.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MethodMetric.java

Purpose: Mutable metric wrapper that invokes an annotated no-arg method at snapshot time.

Important APIs/types/functions: Constructor validates method arity, stores target/method/info, and creates an implementation based on `Metric.Type`. Helper methods create counter, gauge, or tag implementations for supported return types.

Control flow: Snapshot delegates to an anonymous metric that reflectively invokes the method and writes a counter, gauge, or tag. Errors are logged and do not abort the whole snapshot.

State and persistence: Holds target object, accessible method, metadata, and delegated mutable metric. No persistence.

Dependencies/integration: Created by `MutableMetricsFactory.newForMethod` for `@Metric` methods.

Risks/test signals: Unsupported return types and methods with parameters throw `MetricsException`; invocation failures are logged. Tests should cover default String-as-tag, primitive/wrapper numeric types, get-prefix name derivation, and exception logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MethodMetric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsAnnotations.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsAnnotations.java

Purpose: Static helper entry points for creating metrics sources from annotations.

Important APIs/types/functions: Provides `newSourceBuilder(Object)`, `makeSource(Object)`, and related helpers that use `DefaultMetricsFactory`.

Control flow: Callers pass a source object; helpers construct a `MetricsSourceBuilder` and either return the builder or generated `MetricsSource`.

State and persistence: Stateless utility class.

Dependencies/integration: Used by `MetricsSystemImpl.register` and self-source registration.

Risks/test signals: Tests should cover plain `MetricsSource` objects, annotated POJOs, invalid annotated classes, and hybrid source/annotation rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsAnnotations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsInfoImpl.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsInfoImpl.java

Purpose: Immutable `MetricsInfo` implementation used by `Interns`.

Important APIs/types/functions: Stores name and description, implements accessors, equality, hash, and string conversion.

Control flow: Created by interning factories and then shared wherever metadata is needed.

State and persistence: Final fields only; no persistence.

Dependencies/integration: Backing implementation for most non-enum metric info objects.

Risks/test signals: Equality/hash must match interning cache keys. Tests should cover same name/description reuse and different description inequality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsInfoImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsRegistry.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsRegistry.java

Purpose: Public helper registry for tags and mutable metrics, making metrics source implementations concise.

Important APIs/types/functions: Creates counters, gauges, quantiles, inverse quantiles, stats, rates, aggregated rates, and rolling averages. Supports `add(name,value)` default rate creation, context/tag registration, metric/tag lookup, and `snapshot`.

Control flow: Creation methods validate duplicate and whitespace names, instantiate mutable metric types, and add them to ordered maps. `snapshot` writes tags first then calls each mutable metric snapshot. Tag overrides are explicit.

State and persistence: Synchronized `LinkedHashMap`-style maps preserve insertion order for metrics and tags. Mutable metrics retain their own counters/statistics. In-memory only.

Dependencies/integration: Used by source classes, metrics system self metrics, sink adapter stats, and annotation factory. Uses `Interns`, mutable metric classes, and `MsInfo`.

Risks/test signals: Duplicate name rejection, whitespace validation, dynamic default rates, tag override semantics, and snapshot ordering are important. Quantile metrics schedule background tasks and should be stopped by owners when appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsSourceBuilder.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsSourceBuilder.java

Purpose: Reflection-based builder that turns annotated objects into `MetricsSource` instances and initializes annotated mutable fields.

Important APIs/types/functions: Constructor scans inherited fields and methods. `build()` returns an existing `MetricsSource` or a generated source that snapshots the registry. `info()` returns source metadata.

Control flow: `initRegistry` reuses an existing `MetricsRegistry` field or creates one from `@Metrics`; field annotations initialize null mutable fields; method annotations create `MethodMetric` entries. Hybrid annotated `MetricsSource` objects require a registry.

State and persistence: Holds source object, factory, registry, source info, and flags for annotations/registry presence.

Dependencies/integration: Used by `MetricsAnnotations` and `MetricsSystemImpl.register`.

Risks/test signals: Reflection access, inherited members, existing non-null fields, hybrid validation, and missing annotations should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsSourceBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounter.java

Purpose: Abstract base for mutable monotonically increasing counter metrics.

Important APIs/types/functions: Extends `MutableMetric` and defines counter semantics for concrete int/long counters.

Control flow: Concrete counters increment internal values and snapshot as counters.

State and persistence: Base class contributes changed-state tracking via `MutableMetric`; concrete classes store numeric values.

Dependencies/integration: Parent of `MutableCounterInt` and `MutableCounterLong`, used by registry and annotations.

Risks/test signals: Counters should not expose decrement paths. Tests should cover changed flag interaction with snapshot `all=false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterInt.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterInt.java

Purpose: Mutable integer counter.

Important APIs/types/functions: Constructor accepts `MetricsInfo` and initial value. `incr()` and `incr(int)` advance the count. `value()` exposes current value. `snapshot` emits an int counter when all or changed.

Control flow: Increment methods update value and set changed; snapshot clears changed after writing.

State and persistence: In-memory int value plus inherited changed flag; synchronized where needed.

Dependencies/integration: Created by registry and annotation factory; emitted through `MetricsRecordBuilder.addCounter`.

Risks/test signals: Integer overflow is possible if counts exceed int range. Tests should cover initial value, increments, `all=false`, and `all=true`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterInt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterLong.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterLong.java

Purpose: Mutable long counter for high-volume counts.

Important APIs/types/functions: Supports `incr()`, `incr(long)`, `value()`, and `snapshot`.

Control flow: Increment marks changed; snapshot emits a long counter when requested or changed and clears the flag.

State and persistence: In-memory long value and changed flag.

Dependencies/integration: Used for dropped publish counts and application metrics via registry/annotations.

Risks/test signals: Tests should cover long values, snapshot changed semantics, and thread-safety expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterLong.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGauge.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGauge.java

Purpose: Abstract base for mutable point-in-time gauge metrics.

Important APIs/types/functions: Extends `MutableMetric` and defines common gauge role for concrete numeric gauge types.

Control flow: Concrete gauges support set/increment/decrement and snapshot as gauges.

State and persistence: Base changed flag from `MutableMetric`; concrete classes store values.

Dependencies/integration: Parent of int, long, and float mutable gauges created by registry and annotations.

Risks/test signals: Gauge operations can go negative depending on caller; tests should cover changed tracking and snapshot type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGauge.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeFloat.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeFloat.java

Purpose: Mutable float gauge.

Important APIs/types/functions: Constructor stores info and initial float; operations set/increment/decrement value; `value()` and `snapshot` expose it as a float gauge.

Control flow: Mutating operations set the changed flag; snapshot emits when all or changed.

State and persistence: In-memory float value.

Dependencies/integration: Created through `MetricsRegistry.newGauge` or field annotation.

Risks/test signals: Precision and NaN handling should be considered. Tests should cover set, incr, decr, snapshot, and changed clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeFloat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeInt.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeInt.java

Purpose: Mutable integer gauge.

Important APIs/types/functions: Provides `incr`, `incr(int)`, `decr`, `decr(int)`, `set(int)`, `value`, and `snapshot`.

Control flow: Mutations update the value and mark changed; snapshot emits an int gauge when needed.

State and persistence: In-memory int and changed flag.

Dependencies/integration: Used for queue size and application gauges.

Risks/test signals: Tests should cover negative values, repeated snapshots with `all=false`, and all mutation overloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeInt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeLong.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeLong.java

Purpose: Mutable long gauge.

Important APIs/types/functions: Provides long set/increment/decrement operations, `value`, and snapshot as a long gauge.

Control flow: Mutations mark changed; snapshot writes only if all or changed and then clears changed.

State and persistence: In-memory long value.

Dependencies/integration: Registry and annotations create it for long-valued instantaneous metrics.

Risks/test signals: Tests should cover large values, negative values, and changed tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeLong.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableInverseQuantiles.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableInverseQuantiles.java

Purpose: Specialized quantile metric for inverse/rate-style values where lower percentiles may be more meaningful than upper latency percentiles.

Important APIs/types/functions: Extends `MutableQuantiles` and overrides quantile definitions and naming as needed.

Control flow: Uses the same scheduled rollover and snapshot mechanics as `MutableQuantiles`, but with inverse quantile targets.

State and persistence: Maintains estimator, previous snapshot/count, interval, and scheduled task through the parent class.

Dependencies/integration: Created by `MetricsRegistry.newInverseQuantiles`.

Risks/test signals: Tests should verify inverse quantile set, generated metric names/descriptions, rollover, and `stop` task cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableInverseQuantiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetric.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetric.java

Purpose: Abstract base for metrics that accumulate mutable state between snapshots.

Important APIs/types/functions: Declares `snapshot(MetricsRecordBuilder, boolean)`. Provides `changed`, `setChanged`, and `clearChanged` flag helpers.

Control flow: Concrete metrics mark changed on mutation and snapshot either all values or only changed values depending on the `all` flag.

State and persistence: In-memory changed flag; no persistence.

Dependencies/integration: Parent of counters, gauges, stats, rates, quantiles, rolling averages, and method metrics.

Risks/test signals: Changed flag semantics are central. Tests should ensure no-value snapshots are suppressed when `all=false` and unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetricsFactory.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetricsFactory.java

Purpose: Factory that maps `@Metric` annotated fields and methods to concrete mutable metric instances.

Important APIs/types/functions: `newForField` handles counter, gauge, rate, rates, aggregated rates, stat, rolling average, and quantile field types. `newForMethod` creates custom or `MethodMetric` wrappers. `getInfo` helpers derive names/descriptions from annotations, fields, methods, and classes.

Control flow: Field processing creates or registers the appropriate metric, throwing `MetricsException` for unsupported types. Method processing creates a metric and registers it by derived info.

State and persistence: Stateless factory; extension hooks allow subclasses to return custom metrics.

Dependencies/integration: Used by `MetricsSourceBuilder` with `DefaultMetricsFactory`.

Risks/test signals: Unsupported types, annotation `always`, sample/value names, interval, and get-prefix stripping should all be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetricsFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableQuantiles.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableQuantiles.java

Purpose: Mutable metric that estimates selected quantiles over a rolling interval using online sampling.

Important APIs/types/functions: Defines default quantiles, constructor builds metric infos and schedules rollover, `add(long)` inserts values, `snapshot` emits previous count and quantile gauges, `stop` cancels the scheduled task, and testing setters expose estimator internals.

Control flow: A static daemon scheduler runs `RolloverSample` every interval. Rollover snapshots estimator values into `previousSnapshot`, clears the estimator, and marks changed. `snapshot` emits the previous rolled values, using zero when no snapshot exists.

State and persistence: Holds metric infos, interval, estimator, previous count/snapshot, and scheduled future in memory. Static scheduler is shared across instances.

Dependencies/integration: Created by registry and annotation factory; uses Hadoop quantile utilities and Guava thread factory.

Risks/test signals: Background task lifecycle and static scheduler can leak across tests. Tests should cover interval validation at registry level, rollover, no-data snapshot, quantile names, and `stop`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableQuantiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRate.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRate.java

Purpose: Convenience mutable rate metric implemented as a `MutableStat` for operation latency/throughput samples.

Important APIs/types/functions: Constructors derive sample and value labels, and inherited `add`/`snapshot` record counts and average time or extended stats.

Control flow: Calls flow through `MutableStat`; adding a sample marks changed and snapshot emits count/average and optional extended gauges.

State and persistence: Inherited interval and previous sample statistics, min/max, total sample count, and changed flag.

Dependencies/integration: Created by registry `newRate`, `MutableRates`, sink adapter latency, and aggregated rates.

Risks/test signals: Name-derived metric info affects external schemas. Tests should cover extended flag and timestamp update inherited from `MutableStat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRates.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRates.java

Purpose: Helper for managing many named `MutableRate` metrics in a registry, commonly from protocol method names.

Important APIs/types/functions: Initializes rates from a protocol class or name list and adds elapsed-time samples by name.

Control flow: On init, creates registry rates for every method/name so metrics appear before samples. `add` delegates to the named rate, creating if needed depending on registry behavior.

State and persistence: Holds a registry reference and possibly caches initialized protocols/names. Actual samples live in registry metrics.

Dependencies/integration: Used by services tracking RPC/method latencies.

Risks/test signals: Duplicate method initialization and dynamic add behavior should be tested, especially with overloaded methods or inherited protocol methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRates.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRatesWithAggregation.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRatesWithAggregation.java

Purpose: High-concurrency rate collection using per-thread local stats aggregated into global mutable rates at snapshot time.

Important APIs/types/functions: `init(Class)` and `init(String[])` pre-create metrics, `add(name,elapsed)` records thread-local samples, `snapshot` aggregates live thread maps and snapshots globals, `collectThreadLocalStates` forces current thread aggregation, and `init(protocol,prefix)` adds a metric-name prefix.

Control flow: Each thread lazily creates a local map stored in `ThreadLocal` and tracked by weak reference. Snapshot removes dead-thread maps, drains local `ThreadSafeSampleStat` values into `MutableRate` instances, then snapshots global metrics.

State and persistence: Concurrent global metrics map, protocol cache, weak-reference queue of thread maps, thread-local map, and prefix. In-memory only.

Dependencies/integration: Created by `MetricsRegistry.newRatesWithAggregation` and annotation factory.

Risks/test signals: Samples from dead threads can be lost if not snapshotted before GC, as documented. Tests should cover multi-thread aggregation, weak reference cleanup, prefixing, and protocol cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRatesWithAggregation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRollingAverages.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRollingAverages.java

Purpose: Maintains rolling average metrics for named operations over multiple scheduled windows.

Important APIs/types/functions: Constructor sets metric value naming and schedules a `RatesRoller`; `add(name,value)` records values in per-name `MutableRate`; `collectThreadLocalStates`, `snapshot`, `getStats(minSamples)`, `setRecordValidityMs`, and `close` manage rolling state.

Control flow: A scheduled roller snapshots current rates into a collector, extracts sum/count, appends `SumAndCount` windows per name, and removes old windows. `snapshot` emits average gauges for names with valid rolled data. `getStats` returns averages when sample counts meet a threshold.

State and persistence: Maintains current rates, rolling window queues, scheduled executor/future, metric metadata, and validity period. In-memory only; `close` cancels background work.

Dependencies/integration: Created by registry/annotation factory and uses `MetricsCollectorImpl`, `MetricsRecordBuilder`, mutable rates, and scheduled executor utilities.

Risks/test signals: Background rollover timing, cleanup of stale windows, close behavior, and average calculation are high risk. Tests should use controlled timing and cover no-sample windows and minimum sample thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRollingAverages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableStat.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableStat.java

Purpose: Mutable statistic metric for counts, averages, and optional extended min/max/stdev values.

Important APIs/types/functions: Constructors derive metric infos; `setExtended`, `setUpdateTimeStamp`, `add(value)`, `add(numSamples,sum)`, `snapshot`, `lastStat`, `resetMinMax`, and `getSnapshotTimeStamp` expose behavior.

Control flow: Adds update interval stats and min/max, marking changed. Snapshot accumulates total samples, emits counter and average, optionally emits stdev, interval/all-time min/max, and interval count, then copies interval stats to previous and resets them when changed.

State and persistence: Maintains interval and previous `SampleStat`, all-time min/max, total sample count, snapshot timestamp, extended flag, update timestamp flag, and changed flag.

Dependencies/integration: Base for `MutableRate`, used by metrics system snapshot/publish stats and many registries.

Risks/test signals: Aggregated `add(numSamples,sum)` can have variance limitations. Tests should cover no-sample snapshots, extended fields, min/max reset, timestamp updates, and changed semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableStat.java -->
