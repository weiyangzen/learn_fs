# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSubjectUtil.java

Purpose: Tests `SubjectUtil`, a compatibility layer over Java `Subject` execution APIs across Java versions, focusing on exception propagation semantics for `doAs`, `callAs`, `current`, and `sneakyThrow`.

Important APIs and control flow: the test computes `JAVA_SPEC_VER`, asserts `SubjectUtil.HAS_CALL_AS` for Java versions above 17, and exercises `doAs(Subject, PrivilegedAction)`, `doAs(Subject, PrivilegedExceptionAction)`, `callAs(Subject, Callable)`, and `sneakyThrow`. It checks checked exceptions, `PrivilegedActionException`, runtime exceptions, `CompletionException`, `LinkageError`, and null action handling. Assertions branch for Java versions above 11 where `PrivilegedAction` checked-exception propagation differs.

State and dependencies: state is mostly Java runtime version behavior and the current subject. Dependencies are JAAS/security privileged action APIs, `Callable`, `CompletionException`, JUnit 5 assert helpers, and `IOException`.

Integration points: Hadoop authentication code uses subject-scoped execution for Kerberos and secure client actions. These tests preserve compatibility across Java LTS transitions and newer `Subject.callAs` behavior.

Risks and test signals: assertions depend tightly on Java exception wrapping and message text, which can change between JDK implementations. The version parser handles `1.8`, `9`, and later numeric forms but assumes a simple first component. The tests are strong signals for not accidentally double-wrapping or swallowing exceptions.
