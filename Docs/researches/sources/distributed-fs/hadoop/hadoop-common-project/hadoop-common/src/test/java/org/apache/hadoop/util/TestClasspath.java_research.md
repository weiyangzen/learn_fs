<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestClasspath.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestClasspath.java

## Purpose

`TestClasspath.java` tests the `Classpath` command-line utility for printing classpaths, writing manifest jars, help text, and invalid options.

## Important APIs, Types, and Functions

It uses `Classpath.main`, `ExitUtil.disableSystemExit`, captured stdout/stderr streams, `assertJar`, `JarFile`, `Manifest`, and temporary `TEST_DIR`.

## Control Flow

Setup redirects `System.out` and `System.err`, then tests `--glob`, `--jar path`, jar replacement, missing jar path, `--help`, `-h`, and an unrecognized option. Jar tests inspect the generated manifest's `Class-Path` attribute.

## State and Persistence Behavior

Temporary jars are written under `TestClasspath`; stdout/stderr and global exit behavior are modified and restored in teardown.

## Dependencies and Integration Points

It integrates with `Classpath`, `ExitUtil`, `FileUtil`, `GenericTestUtils`, Java jar/manifest APIs, and system properties.

## Risks and Edge Cases

Global stream redirection and disabled system exit can leak if teardown fails. Manifest contents depend on current classpath. Existing jar replacement must be safe.

## Test Signals

Signals include exact classpath output, empty stderr on success, generated jar existence, manifest `Class-Path`, help text content, and `ExitException` plus stderr for invalid invocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestClasspath.java -->
