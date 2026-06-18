<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SubjectUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SubjectUtil.java

## Purpose
Provides a compatibility layer over JAAS `Subject` APIs across Java versions where Security Manager-related APIs are deprecated, disabled, or replaced by `Subject.callAs()`/`Subject.current()`.

## Important APIs, types, and functions
Static method handles are resolved for `Subject.callAs`, `Subject.doAs`, `Subject.doAs(PrivilegedExceptionAction)`, and current subject lookup. `THREAD_INHERITS_SUBJECT` captures whether new threads inherit the subject on the current Java version. Public `callAs()`, `doAs(PrivilegedAction)`, `doAs(PrivilegedExceptionAction)`, and `current()` invoke the best available API. Helper adapters convert between `Callable` and privileged actions, and `sneakyThrow()` preserves exception behavior.

## Control flow
Class initialization probes Java APIs reflectively. Java 18+ uses `callAs` when available; older JVMs use `doAs`. Current subject lookup prefers `Subject.current()` and falls back to `Subject.getSubject(AccessController.getContext())`. Exception wrapping is adjusted so public methods mimic legacy API expectations.

## State and persistence
All state is static method-handle and Java-version metadata. No persistence exists.

## Dependencies and integration points
Used by Hadoop code that needs JAAS subject context without binding directly to Security Manager APIs. Depends on method handles, JAAS `Subject`, privileged action types, `Callable`, and Java specification version.

## Risks and test signals
Risks include Java-version parsing assumptions, class-initialization failure if fallback APIs are unavailable, behavior differences in checked exception wrapping across versions, and incorrect thread-subject inheritance assumptions on Java 22/23. Tests should run on multiple Java versions, cover runtime and checked exceptions, null actions, current-subject lookup, and thread inheritance decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SubjectUtil.java -->
