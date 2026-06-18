# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/NodePlan.java

Purpose: serializable plan for one DataNode, containing a polymorphic list of diskbalancer `Step` objects plus node identity, port, and creation timestamp.

Important APIs/types/functions: `volumeSetPlans` uses Jackson `@JsonTypeInfo` with `@class`. `parseJson()` first reads a tree, recursively validates all `@class` values with `checkNodes()`, and then deserializes. `stepClassIsAllowed()` checks configured package prefixes from `SUPPORTED_PACKAGES_CONFIG_NAME` in a static `HdfsConfiguration`. `toJson()` writes the plan. Accessors manage node name, UUID, port, timestamp, and step list; package-private `addStep()` appends non-null steps.

Control flow: planners build `NodePlan`, `PlanCommand` writes JSON, `ExecuteCommand` parses JSON before submission, and DataNode-side execution parses/validates again. The recursive class check traverses nested objects and arrays to reject unexpected polymorphic classes before Jackson binds them.

State and persistence behavior: plan JSON is a durable artifact under diskbalancer output directories and is submitted unchanged to DataNodes. Allowed package prefixes are loaded statically from configuration, so runtime config changes after class load may not affect validation.

Dependencies and integration points: depends on Jackson, `HdfsConfiguration`, `DFSConfigKeys.SUPPORTED_PACKAGES_CONFIG_NAME`, and `Step` implementations such as `MoveStep`. This is the main security boundary for plan deserialization.

Risks: allowed-package configuration must include diskbalancer planner classes or parsing fails. Prefix checks must be configured narrowly enough to avoid unsafe polymorphic deserialization. `setURI()` actually sets `nodeName`, a legacy naming oddity. `toList()` usage in `getAllowedPackages()` requires a Java version supporting stream `toList()`.

Test signals: tests include sample `Step` classes and plan validity checks, covering allowed/disallowed `@class` handling and execute-plan validation.
