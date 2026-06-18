# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestProxyUserFromEnv.java

Purpose: Tests login-user proxying via the `HADOOP_PROXY_USER` system property.

Important APIs/types/functions: `UserGroupInformation.HADOOP_PROXY_USER`, `UserGroupInformation.getLoginUser`, `getRealUser`, `Runtime.exec("whoami")`, and username normalization for Windows domain prefixes.

Control flow: sets the proxy-user system property to `foo.bar`, obtains login UGI, asserts proxy username, reads the real OS username from `whoami`, strips any domain prefix after backslash, and asserts the real UGI username matches.

State and persistence: mutates a JVM system property and UGI login-user singleton/cache.

Dependencies/integration points: process environment/OS user identity and UGI proxy-user initialization.

Risks: system property is not cleared in the test; `whoami` process and username formatting are platform-dependent; UGI login cache can leak into later tests.

Test signals: confirms environment/system-property proxy user is reflected as login user with a real underlying UGI.
