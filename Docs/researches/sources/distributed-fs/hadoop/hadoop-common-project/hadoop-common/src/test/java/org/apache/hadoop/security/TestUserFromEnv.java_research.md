# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserFromEnv.java

Purpose: verifies that the `HADOOP_USER_NAME` system property path is honored by `UserGroupInformation.getLoginUser`.

Important APIs and types: `UserGroupInformation.HADOOP_USER_NAME`, `System.setProperty`, `UserGroupInformation.getLoginUser`, and JUnit assertions.

Control flow: the single test sets the Hadoop user-name system property to `randomUser`, calls `getLoginUser`, and asserts that the login user's name matches the configured value.

State and persistence: mutates a JVM system property and static UGI login state. The test does not clear the property afterward, so isolation depends on the surrounding test framework or a fresh JVM.

Dependencies and integration points: covers the environment/system-property user override used by Hadoop command-line tools and simple-auth deployments.

Risks: property leakage can affect later UGI tests. If a login user was already initialized before the property is set, behavior could differ; the test assumes UGI has not cached a conflicting login user.

Test signals: narrow but important regression signal for simple user override semantics.
