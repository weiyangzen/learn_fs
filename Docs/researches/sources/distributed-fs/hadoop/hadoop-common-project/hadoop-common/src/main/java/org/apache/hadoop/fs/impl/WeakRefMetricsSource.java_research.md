# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakRefMetricsSource.java

## Purpose
MetricsSource wrapper that weakly references the real source to avoid keeping large filesystem objects alive after close.

## Important APIs, Types, and Functions
Constructor, getMetrics(), getName(), getSource(), toString().

## Control Flow
getMetrics resolves the weak reference and delegates only if still live; otherwise it emits no metrics.

## State and Persistence Behavior
Stores name and WeakReference<MetricsSource>. State may disappear after GC if no strong references remain.

## Dependencies and Integration Points
Integrates with Hadoop metrics2 registries that need a source object but should not force retention.

## Risks and Test Signals
Risks are metrics silently disappearing if no strong owner exists and unregister code needing the name. Tests should cover delegation and GC-cleared behavior.
