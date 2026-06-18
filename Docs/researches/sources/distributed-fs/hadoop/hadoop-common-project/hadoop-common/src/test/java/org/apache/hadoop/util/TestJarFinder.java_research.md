# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJarFinder.java

Purpose: verifies `JarFinder`, which locates the containing jar for a class or creates a jar from an expanded classpath directory.

Important APIs and types: `JarFinder.getJar`, `JarFinder.jarDir`, `GenericTestUtils.getTestDir`, `JarOutputStream`, `JarInputStream`, `Manifest`, and Java `Properties`.

Control flow: `testJar` asks for the jar containing `LoggerFactory`, expected to be classpath-provided. `testExpandedClasspath` asks for the test class itself and expects an on-the-fly jar. Manifest tests create temporary directories with and without `META-INF/MANIFEST.MF`, add a properties file, call `jarDir`, then reopen the byte-array jar and assert a manifest is present either way.

State and persistence: uses temporary filesystem directories under Hadoop's test dir and in-memory jar byte arrays. The helper `delete` recursively removes test directories with a path-length guard.

Dependencies and integration points: integrates classloader resource lookup, jar stream writing, manifests, and Hadoop test directory conventions.

Risks: missing manifests, unsafe recursive deletion, classpath directory packaging failures, or inability to locate dependency jars. Test signals are filesystem existence checks and `JarInputStream.getManifest()` assertions.
