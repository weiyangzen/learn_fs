# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMapping.java

Purpose: Main test suite for `LdapGroupsMapping`, covering user/group searches, base DN configuration, dynamic filters, hierarchy lookup, reconnect/retry behavior, password sources, LDAP timeouts, and setConf error handling.

Important APIs/types/functions: `LdapGroupsMapping`, config keys for LDAP URL/base DNs/search filters/timeouts/passwords, inherited mock context helpers, `CredentialProviderFactory`, `JavaKeyStoreProvider`, `ServerSocket`, `SubjectInheritingThread`, `doGetGroups`, and Mockito verification.

Control flow: mock tests configure `DirContext.search` sequences for user then group enumeration, validate base DN trimming/defaults, dynamic filter argument resolution, parent group lookup, reconnect after `CommunicationException`, and empty result when LDAP remains down. Password tests read from a file and Java keystore aliases. Timeout tests create minimal local sockets that accept but do not respond or stop after bind success to trigger connection/read timeouts. `testSetConf` injects `Configuration.getPassword` IOException and ensures no NPE.

State and persistence: mock LDAP context, temporary secret files, temporary JKS credential provider files, local server sockets, and mapping configuration.

Dependencies/integration points: Java Naming LDAP APIs, Hadoop credential provider, filesystem, local sockets, Mockito.

Risks: timeout tests are timing/network sensitive; credential provider files in generic test dir can collide; mock search call counts encode implementation details.

Test signals: verifies LDAP group resolution correctness, resilience to connection failures, secure password retrieval, and timeout diagnostics.
