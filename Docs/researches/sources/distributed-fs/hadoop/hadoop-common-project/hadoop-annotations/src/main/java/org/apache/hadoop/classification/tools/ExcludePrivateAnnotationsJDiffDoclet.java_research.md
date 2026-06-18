# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/ExcludePrivateAnnotationsJDiffDoclet.java

Purpose: legacy static-entry JDiff doclet wrapper that excludes Hadoop private and limited-private annotated elements before generating JDiff output.

Important APIs, types, and functions: `languageVersion()` returns `SourceVersion.RELEASE_17`; `start(DocletEnvironment)` delegates to `JDiff.start(RootDocProcessor.process(root))`; `optionLength()` recognizes stability options before forwarding to `JDiff.optionLength()`; `validOptions()` applies stability options, filters them out, then delegates validation to JDiff.

Control flow: javadoc/JDiff calls static doclet entry points. Stability options update `RootDocProcessor`; `RootDocProcessor.process()` wraps the environment with `HadoopDocEnvImpl`; JDiff sees the filtered environment.

State and persistence: static stability state lives in `StabilityOptions`/`RootDocProcessor` for the JVM invocation. No disk state is written by this wrapper itself.

Dependencies and integration points: depends on JDK doclet APIs and the `jdiff.JDiff` dependency. Integrates Hadoop annotation filtering into API-diff generation.

Risks and test signals: static mutable filtering state can leak across multiple doclet invocations in the same JVM. JDiff option compatibility depends on `filterOptions()` removing only Hadoop-specific flags. Test signals are JDiff generation with `-stable`, `-evolving`, and `-unstable`, plus exclusion of Private/LimitedPrivate classes.
