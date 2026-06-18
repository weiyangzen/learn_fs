## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsVisitor.java

Purpose: Visitor interface for type-specific metric handling.

Important APIs/types/functions: Declares `counter` overloads for int and long and `gauge` overloads for int, long, float, and double.

Control flow: Concrete `AbstractMetric` classes call the matching method from `visit`.

State and persistence: Interface only.

Dependencies/integration: Allows consumers to process immutable metrics without instanceof checks. Used by metric classes and potential sinks/exporters.

Risks/test signals: Concrete metric visitor dispatch must match both type and primitive width. Tests should cover every overload.
