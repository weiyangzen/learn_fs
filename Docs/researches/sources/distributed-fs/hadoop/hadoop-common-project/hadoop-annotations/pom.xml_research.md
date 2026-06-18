# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/pom.xml

Purpose: Maven module descriptor for the Hadoop annotations jar containing audience/stability annotations and doclet filtering helpers.

Important APIs, types, and functions: declares parent `hadoop-project`, artifact `hadoop-annotations`, packaging `jar`, provided dependency on `io.github.zhtttylz:jdiff`, and a compiler-plugin override that uses `source`/`target` plus `--add-modules jdk.javadoc` and `--add-exports jdk.javadoc/jdk.javadoc.internal.tool=ALL-UNNAMED`.

Control flow: Maven compiles this module as a jar. The compiler override is necessary because the doclet bridge imports JDK internal javadoc classes and cannot use the parent `release` configuration.

State and persistence: no runtime state. Build output is the annotations jar consumed by other Hadoop modules.

Dependencies and integration points: integrates with the Hadoop parent build, JDiff doclet APIs, and JDK 17 javadoc internals used by `HadoopDocEnvImpl`.

Risks and test signals: JDK internal exports are brittle across JDK upgrades. Provided JDiff means runtime users of JDiff doclets need it available from the doc generation classpath. Test signals include `mvn -pl hadoop-common-project/hadoop-annotations compile` on the supported JDK and doclet execution under the docs profile.
