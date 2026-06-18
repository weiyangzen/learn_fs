## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MethodMetric.java

Purpose: Mutable metric wrapper that invokes an annotated no-arg method at snapshot time.

Important APIs/types/functions: Constructor validates method arity, stores target/method/info, and creates an implementation based on `Metric.Type`. Helper methods create counter, gauge, or tag implementations for supported return types.

Control flow: Snapshot delegates to an anonymous metric that reflectively invokes the method and writes a counter, gauge, or tag. Errors are logged and do not abort the whole snapshot.

State and persistence: Holds target object, accessible method, metadata, and delegated mutable metric. No persistence.

Dependencies/integration: Created by `MutableMetricsFactory.newForMethod` for `@Metric` methods.

Risks/test signals: Unsupported return types and methods with parameters throw `MetricsException`; invocation failures are logged. Tests should cover default String-as-tag, primitive/wrapper numeric types, get-prefix name derivation, and exception logging.
