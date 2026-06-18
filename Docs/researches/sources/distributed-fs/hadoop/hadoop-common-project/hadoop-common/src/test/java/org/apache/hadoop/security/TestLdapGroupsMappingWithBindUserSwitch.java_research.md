# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithBindUserSwitch.java

Purpose: Tests LDAP bind-user cycling when authentication failures occur.

Important APIs/types/functions: `LdapGroupsMapping` bind-user config keys, `BIND_USERS_KEY`, bind username/password/plaintext/alias/file suffixes, `LDAP_NUM_ATTEMPTS_KEY`, `DummyLdapCtxFactory`, Hadoop credential provider, and `AuthenticationException`.

Control flow: one test validates missing bind credentials fail with a runtime error. Other tests configure multiple bind users with plaintext passwords, credential-provider aliases, or password files. Shared helper sets expected bind user/password in the dummy factory, stubs LDAP search to throw a configured number of `AuthenticationException`s while advancing expected credentials, then returns user and group enumerations and asserts final groups and search-call count.

State and persistence: temporary password files, temporary Java keystore credential provider, static dummy factory expected bind credentials, mocked context failures, and atomic failure counter.

Dependencies/integration points: LDAP context creation, Hadoop credential providers, password file extraction, retry/bind switching logic.

Risks: cycles expected credentials with Guava `Iterators.cycle`; static factory expectations must align exactly with reconnect timing; password files/JKS live in generic test dir.

Test signals: confirms configuration validation and that authentication failures rotate through configured bind users across plaintext, alias, and file password sources.
