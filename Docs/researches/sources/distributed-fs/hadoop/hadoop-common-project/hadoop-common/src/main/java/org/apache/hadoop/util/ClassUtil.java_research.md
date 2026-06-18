# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ClassUtil.java

Purpose: `ClassUtil` locates the jar or class-file resource that contains a given Java class.

Important APIs and types: `findContainingJar(Class<?>)`, `findClassLocation(Class<?>)`, and private `findContainingResource(ClassLoader, String, String)`.

Control flow: it converts the class name to a `.class` resource path, enumerates all matching resources from the classloader, picks the first with the requested protocol (`jar` or `file`), strips a leading `file:` and any `!` suffix, URL-decodes as UTF-8, and returns the path.

State and persistence behavior: stateless utility; no persistence.

Dependencies and integration points: used by diagnostics and classpath reporting code. Depends on Java `ClassLoader.getResources`, `URLDecoder`, and Hadoop audience annotations.

Risks: returns the first matching resource with the protocol, which may not be the actual class loaded if classpath contains duplicates. Throws `RuntimeException` on IO enumeration failure. Path handling is URL/protocol-specific.

Test signals: cover jar resource paths, exploded class directories, URL-encoded spaces, duplicate resources, classes loaded by null/bootstrap-like loaders if applicable, and no-match null returns.
