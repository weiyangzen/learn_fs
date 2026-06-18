<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/LdapConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/LdapConstants.java

## Purpose
Defines shared constants for LDAP integration tests.

## Important APIs, types, and functions
`LDAP_BASE_DN` is `dc=example,dc=com` and `LDAP_SERVER_ADDR` is `localhost`. The private constructor prevents instantiation.

## Control flow
No runtime control flow beyond class loading.

## State and persistence
Static constant state only. No persistence exists.

## Dependencies and integration points
Consumed by LDAP authentication handler tests that need a consistent local LDAP address and base DN.

## Risks and test signals
Hard-coded localhost assumptions require tests to provision a local LDAP server. Signals are compile-time access and integration-test configuration consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/LdapConstants.java -->
