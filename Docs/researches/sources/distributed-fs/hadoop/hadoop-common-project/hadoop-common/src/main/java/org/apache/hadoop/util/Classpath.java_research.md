# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Classpath.java

Purpose: `Classpath` is the Java implementation behind `hadoop classpath` advanced modes, printing an expanded classpath or writing it into a manifest jar.

Important APIs and types: `main(String[])` parses `--glob`, `--jar <path>`, `-h`, and `--help`. Private `terminate` prints to stderr and calls `ExitUtil.terminate`.

Control flow: no args/help prints usage. `CommandFormat` parses options. `--glob` prints `java.class.path`. `--jar` validates an output path, creates a temporary manifest jar with `FileUtil.createJarWithClassPath`, and replaces the requested output path with that jar.

State and persistence behavior: reads the `java.class.path` system property and current working directory. `--jar` writes/replaces a jar file; `--glob` only writes stdout.

Dependencies and integration points: integrates Hadoop shell scripts with `FileUtil`, `Path`, `CommandFormat`, environment variables, and `ExitUtil`.

Risks: `--jar` performs filesystem replacement and may overwrite the target. Unknown options terminate. The classpath is whatever the JVM process already received; shell-side wildcard expansion may already have occurred.

Test signals: cover help/no-arg output, unknown option exit, `--glob` output, missing/empty `--jar` target, manifest jar creation, replace failures, and disabled system-exit handling.
