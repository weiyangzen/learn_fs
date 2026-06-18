# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/HadoopDocEnvImpl.java

Purpose: filtered `DocletEnvironment` implementation for Hadoop doclets. It subclasses JDK internal `DocEnvImpl` to remain compatible with doclets that expect that implementation while filtering elements by Hadoop audience and stability annotations.

Important APIs, types, and functions: constructor accepts the original environment, selected stability flag, and whether unannotated classes should be private. `extractToolEnvironment()` retrieves `DocEnvImpl.toolEnv` from the original environment. `exclude(Element)` evaluates `InterfaceAudience.Private`, `InterfaceAudience.LimitedPrivate`, `InterfaceAudience.Public`, `InterfaceStability.Unstable`, and `InterfaceStability.Evolving`. Overrides filter `getSpecifiedElements()`, `getIncludedElements()`, and `isIncluded()`, while delegating doc trees, element/type utils, file manager, source version, module mode, and file kind.

Control flow: doclet wrappers call `RootDocProcessor.process()`, which constructs this wrapper. Standard or JDiff doclets then ask for specified/included elements and receive filtered `LinkedHashSet` results preserving base order.

State and persistence: instance state is read-only after construction. No persistent data is written; filtering decisions are recomputed from annotation mirrors.

Dependencies and integration points: depends on `jdk.javadoc.internal.tool.DocEnvImpl` and `ToolEnvironment`, requiring explicit module exports. It integrates directly with Hadoop's annotation classes and JDK doclet APIs.

Risks and test signals: JDK internal inheritance is fragile across Java releases. Filtering only checks annotations present directly on each element, so inherited/package-level classification may not affect all elements unless javadoc includes those annotations on the element. Test signals are doc generation on the supported JDK, filtering by audience and each stability level, and failure behavior when the original environment is not `DocEnvImpl`.
