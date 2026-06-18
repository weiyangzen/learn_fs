# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsStandardDoclet.java

Purpose: Standard Javadoc doclet wrapper that should document only Hadoop `@InterfaceAudience.Public` API elements, excluding private, limited-private, and unannotated class-level elements.

Important APIs, types, and functions: implements `Doclet` around a `StandardDoclet` delegate. `getSupportedOptions()` adds `-unstable` and `-evolving`; `run()` enables unannotated-class exclusion, applies stability, processes the environment, and delegates to the standard doclet with the filtered environment. Static `start()`, `optionLength()`, and `validOptions()` support legacy-style entry points.

Control flow: javadoc calls `init()`, option processing updates `StabilityOptions`, then `run()` wraps the environment through `RootDocProcessor.process(env)` and invokes `delegate.run(filtered)`.

State and persistence: per-instance state is the delegate. Global filtering state is stored in `RootDocProcessor` and `StabilityOptions`.

Dependencies and integration points: depends on JDK `StandardDoclet`, Hadoop annotation filtering, and JDK 17 doclet APIs.

Risks and test signals: the `-evolving` option handler sets `StabilityOptions.Level.UNSTABLE` instead of `EVOLVING`, which likely makes `-evolving` too permissive. Like other wrappers, the instance option set omits `-stable`. Test signals should assert option behavior and generated docs under `-unstable`, `-evolving`, and `-stable`.
