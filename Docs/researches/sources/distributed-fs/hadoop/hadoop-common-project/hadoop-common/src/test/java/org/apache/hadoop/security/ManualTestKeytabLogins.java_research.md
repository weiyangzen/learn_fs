# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ManualTestKeytabLogins.java

Purpose: Manual regression driver for HADOOP-6947, verifying two different keytab/principal logins can be performed in one JVM.

Important APIs/types/functions: `main`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `getUserName`, and JUnit `assertTrue` used in a command-line context.

Control flow: requires exactly four arguments: principal/keytab pairs. It logs in the first UGI, prints it, asserts username equals the first principal, then repeats for the second pair.

State and persistence: uses Kerberos keytab files and mutates UGI/Kerberos login state in the JVM; no test framework setup.

Dependencies/integration points: external Kerberos environment, valid keytabs, Hadoop CLI classpath.

Risks: not an automated unit test; exits process on bad arguments; depends on real KDC/keytabs; assertions may be disabled only if run outside normal test settings.

Test signals: when run manually, proves separate keytab logins return distinct expected UGIs without overwriting each other incorrectly.
