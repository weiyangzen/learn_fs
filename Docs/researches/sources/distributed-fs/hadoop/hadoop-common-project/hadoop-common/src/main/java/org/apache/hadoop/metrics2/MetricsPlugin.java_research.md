## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsPlugin.java

Purpose: Minimal lifecycle contract for configurable metrics plugins.

Important APIs/types/functions: `init(SubsetConfiguration conf)` initializes a plugin instance from a configuration subset.

Control flow: `MetricsConfig.getPlugin` reflectively creates plugin classes and invokes `init`; filters and sinks implement this contract.

State and persistence: Interface only; implementations decide their in-memory configuration state.

Dependencies/integration: Depends on Apache Commons Configuration `SubsetConfiguration`; base contract for `MetricsFilter` and sink implementations.

Risks/test signals: Plugin initialization failures surface during metrics system startup. Tests should cover class loading, missing class names, and configuration property propagation.
