<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/JarFinder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/JarFinder.java

## Purpose

`JarFinder.java` is a test utility for locating the jar containing a class or creating a temporary jar from class-directory resources.

## Important APIs, Types, and Functions

Important functions include `jarDir`, `getJar(Class)`, `getJar(Class, String)`, `makeClassLoaderTestJar`, and private helpers `copyToZipStream`, `zipDir`, and `createJar`.

## Control Flow

`getJar` asks the classloader for the class resource. If the resource is already inside a jar, it decodes and returns that jar path. If it is in a classes directory, it creates a jar under a generic test directory. `jarDir` writes a manifest when needed, recursively zips files, skips `META-INF/MANIFEST.MF`, and streams file bytes into entries.

## State and Persistence Behavior

The utility creates jar files on disk in test directories and writes zip entries/manifests. It otherwise holds no long-lived state.

## Dependencies and Integration Points

It integrates with classloader tests, `GenericTestUtils`, `JarOutputStream`, `ZipOutputStream`, `JarFile`, `Manifest`, URL decoding, and Java resource lookup.

## Risks and Edge Cases

Risks include URL decoding differences, directory recursion order, manifest duplication, missing parent directory creation, and stale generated jars in test dirs.

## Test Signals

Signals include generated jars opening successfully, manifests being present, class/resources being loadable, and existing jar resources returning their original jar path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/JarFinder.java -->
