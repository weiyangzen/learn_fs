# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configurable.java

Purpose: public stable interface for objects that can receive and expose a Hadoop `Configuration`. It is a core contract used by tools, filesystems, services, and plugin objects that need late-bound configuration. The source was read as a complete 40-line Java file.

Important APIs/functions: interface `Configurable`; methods `void setConf(Configuration conf)` and `Configuration getConf()`. The type is annotated `InterfaceAudience.Public` and `InterfaceStability.Stable`.

Control flow: no implementation control flow; implementors decide how to store, validate, or react to configuration.

State and persistence: the interface defines an in-memory configuration association but owns no state itself. Implementations commonly store the `Configuration` in a field and may derive additional runtime state from it.

Dependencies and integration: depends on `org.apache.hadoop.conf.Configuration` and classification annotations. It integrates with Hadoop object factories, reflection utilities, and APIs that configure user-supplied components after construction.

Risks: implementations may accept null, retain mutable configuration references, or perform expensive side effects in `setConf`; the interface does not constrain those behaviors. API stability means method signatures cannot be changed without breaking many downstream implementations.

Test signals: compile/API compatibility checks, implementation tests verifying `setConf`/`getConf` round trips, and factory/reflection tests that configure `Configurable` instances.
