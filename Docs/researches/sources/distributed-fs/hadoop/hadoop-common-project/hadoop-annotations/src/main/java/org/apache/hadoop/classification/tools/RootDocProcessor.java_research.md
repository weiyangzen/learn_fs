# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/RootDocProcessor.java

Purpose: shared static coordinator for Hadoop doclet filtering. It stores selected stability and whether unannotated classes should be treated as private, then wraps a `DocletEnvironment`.

Important APIs, types, and functions: static setters/getters are `setStability()`, `getStability()`, `setTreatUnannotatedClassesAsPrivate()`, and `isTreatUnannotatedClassesAsPrivate()`. `process(DocletEnvironment)` returns a new `HadoopDocEnvImpl`.

Control flow: doclet wrappers set stability and public-only mode, then call `process()` before delegating to StandardDoclet or JDiff.

State and persistence: all configuration is static process state, initialized to `-unstable` and `false` for unannotated private handling. No disk persistence.

Dependencies and integration points: depends on JDK doclet environment and `HadoopDocEnvImpl`. It is the bridge between option parsing in `StabilityOptions` and actual environment filtering.

Risks and test signals: static state can leak between doclet invocations in the same JVM. Test signals should reset or isolate invocations and verify default unstable behavior plus public-only toggling.
