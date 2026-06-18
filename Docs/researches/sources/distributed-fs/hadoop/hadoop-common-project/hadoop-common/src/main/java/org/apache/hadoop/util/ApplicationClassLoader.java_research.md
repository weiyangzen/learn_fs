# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ApplicationClassLoader.java

Purpose: `ApplicationClassLoader` is a child-first `URLClassLoader` for isolating application classes while delegating configured system classes/resources to the parent loader.

Important APIs and types: constructors accept URL arrays or a classpath string, parent classloader, and system class patterns. Static `constructUrlsFromClasspath` expands existing entries and wildcard jar directories. `getResource`, `loadClass`, and `isSystemClass` implement resource/class selection.

Control flow: static initialization loads `org.apache.hadoop.application-classloader.properties` and `system.classes.default`. For non-system classes/resources, lookup tries this loader first, then parent. For system classes it delegates directly. `isSystemClass` normalizes slashes, strips leading dots, applies ordered positive and negative prefixes, and treats exact class, package suffix dot, and nested class `$` as matches.

State and persistence behavior: stores parent and system class list; no persistence beyond loaded URLs. Static failure to load defaults throws `ExceptionInInitializerError`.

Dependencies and integration points: uses `FileUtil.getJarsInDirectory`, `Path`, Hadoop `StringUtils`, Java `URLClassLoader`, and YARN/application isolation code.

Risks: child-first loading can create incompatible duplicate classes if system patterns are wrong. Missing properties file prevents class initialization. Classpath wildcard entries only include jars present at construction time. Negative system-class rules override positives.

Test signals: cover default property loading, null parent rejection, wildcard jar expansion, nonexistent classpath elements, resource leading slash handling, system class include/exclude rules, nested classes, and parent fallback.
