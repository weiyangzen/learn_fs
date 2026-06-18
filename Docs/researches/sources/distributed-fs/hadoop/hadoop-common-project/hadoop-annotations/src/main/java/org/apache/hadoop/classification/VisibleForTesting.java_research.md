# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/VisibleForTesting.java

Purpose: marker annotation for program elements that are present or more visible specifically for Hadoop internal tests.

Important APIs, types, and functions: `@VisibleForTesting` targets types, methods, fields, and constructors; it is documented and retained in class files with `RetentionPolicy.CLASS`.

Control flow: no executable control flow. The annotation is informational and can be consumed by static analysis, review, or generated docs.

State and persistence: metadata is stored in compiled class files but not guaranteed to be available via runtime reflection because retention is `CLASS`.

Dependencies and integration points: depends only on Java annotation APIs. Used in modules such as Hadoop auth to expose test hooks like `KerberosAuthenticator.wrapExceptionWithMessage()` and `JWTRedirectAuthenticationHandler.constructLoginURL()`.

Risks and test signals: external consumers may be tempted to depend on testing-only APIs despite the documented private/unstable semantics. Test signal is compile-time availability to tests without broadening intended API stability.
