# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestKDiagNoKDC.java

Purpose: Tests `KDiag` behavior when no MiniKDC is started.

Important APIs/types/functions: `KDiag.exec`, `KerberosDiagsFailure`, `ARG_KEYLEN`, `ARG_NOLOGIN`, `ARG_NOFAIL`, `HADOOP_TOKEN_FILES`, `UserGroupInformation.reset`, and category constants `CAT_LOGIN` and `CAT_TOKEN`.

Control flow: resets UGI before each test. Tests expect login-category failures for standalone and no-login invocations, success/nonthrowing return for `--nofail`, usage return code `-1`, and token-category failure when `HADOOP_TOKEN_FILES` points at a nonexistent file.

State and persistence: shared static `Configuration`, temporarily sets/unsets token files config.

Dependencies/integration points: KDiag command path without Kerberos service, token-file loading.

Risks: behavior can vary on hosts with default Kerberos configuration; shared static conf must be cleaned for token-file test.

Test signals: confirms KDiag remains usable and categorizes failures even without a local test KDC.
