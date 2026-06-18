# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/InterfaceStability.java

Purpose: defines Hadoop API stability annotations that describe compatibility expectations across releases.

Important APIs, types, and functions: container class `InterfaceStability` is `@Public` and `@Evolving`. Nested runtime-retained documented annotations are `Stable`, `Evolving`, and `Unstable`.

Control flow: no runtime logic. Annotations are attached to program elements and consumed by documentation tooling, especially `HadoopDocEnvImpl` and `StabilityOptions`.

State and persistence: stability metadata persists in class files due to runtime retention.

Dependencies and integration points: imports `InterfaceAudience` annotations for its own documentation and classification. Integrates with doclet filters that exclude unstable/evolving APIs depending on `-stable`, `-evolving`, or `-unstable` options.

Risks and test signals: compatibility promises are only as accurate as annotations. Filtering correctness should be tested for each stability level and for private elements with explicit stability annotations.
