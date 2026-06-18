# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithMiniKdc.java

Purpose: tests UGI automatic credential renewal failure/retry behavior using a MiniKdc with very short ticket lifetimes and a deliberately bogus `kinit` command.

Important APIs and types: `MiniKdc`, `UserGroupInformation`, `spawnAutoRenewalThreadForUserCreds`, `UserGroupInformation.metrics.getRenewalFailures`, `SecurityUtil.setAuthenticationMethod`, `LambdaTestUtils.await`, and `HADOOP_KERBEROS_MIN_SECONDS_BEFORE_RELOGIN`.

Control flow: setup builds a MiniKdc configuration with two-second ticket lifetimes, starts it under `test.dir`, and creates a principal/keytab. The test configures Kerberos auth, sets `hadoop.kerberos.kinit.command` to a bogus executable to force renewal failures, lowers the relogin interval to one second, logs in from keytab, spawns the auto-renewal thread for user credentials, then waits until the renewal failure metric increments.

State and persistence: static `MiniKdc` is stopped in `@AfterEach`, and `UserGroupInformation.reset()` is called. It writes KDC/keytab data under the test directory and mutates UGI metrics/logging/global config.

Dependencies and integration points: integrates Hadoop MiniKdc, UGI renewal thread logic, retry metrics, test logging, and polling with timeout.

Risks: inherently timing-sensitive; short ticket lifetimes and background threads can be flaky on overloaded CI. Metrics are global and may have prior state if not isolated. The test intentionally avoids real `kinit` to prevent renewing a developer's own TGT.

Test signals: proves the renewal thread retries and records failures for expiring Kerberos credentials. Detailed backoff logic is intentionally delegated to `TestUserGroupInformation#testGetNextRetryTime`.
