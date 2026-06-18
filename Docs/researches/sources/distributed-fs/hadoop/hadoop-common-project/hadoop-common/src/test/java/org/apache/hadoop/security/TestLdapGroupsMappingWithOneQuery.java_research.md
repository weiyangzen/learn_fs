# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithOneQuery.java

Purpose: Tests `LdapGroupsMapping` single-query lookup using a user's `memberOf` attribute and fallback to secondary lookup when DN parsing fails.

Important APIs/types/functions: `LdapGroupsMapping.MEMBEROF_ATTR_KEY`, mocked `Attribute.getAll`, `NamingEnumeration`, custom inner `TestLdapGroupsMapping` overriding `lookupGroup`, and Mockito `verify`.

Control flow: `setupMocks` stubs the user's `memberOf` attribute to return a list of group DNs. The primary scenario enables `memberOf`, resolves CN values `abc`, `xyz`, and `sss`, asserts no secondary query, and verifies one LDAP search. The fallback scenario includes an invalid DN with `ipaUniqueID`, expects empty groups, sets attempts to one, and asserts overridden `lookupGroup` was called.

State and persistence: mock enumerations and a boolean `secondaryQueryCalled` in the custom mapping.

Dependencies/integration points: LDAP DN parsing and optimized group lookup path.

Risks: invocation count spans two sub-scenarios in one test; fallback expected empty result is tied to invalid DN behavior; custom subclass tracks only method entry, not fallback result quality.

Test signals: verifies one-query optimization avoids extra search for valid `memberOf` data and falls back when memberOf parsing cannot produce groups.
