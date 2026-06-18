# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/IncludePublicAnnotationsJDiffDoclet.java

Purpose: JDiff doclet wrapper that includes only public Hadoop API elements and excludes private, limited-private, and unannotated class-level elements.

Important APIs, types, and functions: implements `Doclet` with a `JDiff` delegate and supports custom `-unstable` and `-evolving` options. `run()` and static `start()` set `RootDocProcessor.setTreatUnannotatedClassesAsPrivate(true)` before delegating to JDiff on a processed environment. Static compatibility methods provide `languageVersion()`, `optionLength()`, and `validOptions()`.

Control flow: custom options update `StabilityOptions`; `run()` applies stability to `RootDocProcessor`, enables unannotated-class exclusion, wraps the environment, and runs JDiff. The static path follows the same public-only filtering intent.

State and persistence: delegate, reporter, and locale are per instance; filtering mode and stability are static global state in helper classes for the doclet invocation.

Dependencies and integration points: depends on JDiff, JDK doclet APIs, `RootDocProcessor`, and `HadoopDocEnvImpl`. Used for API diff documentation that should reflect public Hadoop APIs only.

Risks and test signals: supports `-unstable` and `-evolving` in the instance option set but not `-stable`, despite static optionLength recognizing it. Static mutable state can affect sequential doclet runs. Test signals include JDiff output containing `@Public` APIs, excluding unannotated classes, and stability filtering with each flag.
