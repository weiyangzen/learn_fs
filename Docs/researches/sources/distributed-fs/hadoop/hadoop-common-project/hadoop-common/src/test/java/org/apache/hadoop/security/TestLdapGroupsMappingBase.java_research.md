# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingBase.java

Purpose: Shared Mockito fixture and dummy LDAP context factory for LDAP group mapping tests.

Important APIs/types/functions: mocked `DirContext`, `NamingEnumeration<SearchResult>`, `SearchResult`, `Attributes`, spy `LdapGroupsMapping`, `getBaseConf`, `DummyLdapCtxFactory`, and `InitialContextFactory.getInitialContext`.

Control flow: `setupMocksBase` resets dummy factory, initializes Mockito annotations, stubs user search to return one user, group enumeration to return two group names, parent group enumeration to return one parent, and exposes helper getters. `getBaseConf` installs `DummyLdapCtxFactory` and expected LDAP URL. The dummy factory asserts provider URL, bind user, and bind password if configured, then returns the mocked context or a real `InitialLdapContext`.

State and persistence: per-test mocks plus static dummy factory expectations/context.

Dependencies/integration points: JNDI LDAP context creation path used by `LdapGroupsMapping`.

Risks: static dummy factory state must be reset every test; shared spy can accumulate interactions if not reset by Mockito init; assertions inside factory couple tests to context environment keys.

Test signals: provides deterministic LDAP search results and verifies LDAP context construction parameters for derived test classes.
