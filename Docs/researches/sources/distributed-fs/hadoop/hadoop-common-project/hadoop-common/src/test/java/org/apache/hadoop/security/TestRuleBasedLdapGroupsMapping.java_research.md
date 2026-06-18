# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRuleBasedLdapGroupsMapping.java

Purpose: Tests case-conversion rules layered on top of LDAP group mapping.

Important APIs/types/functions: `RuleBasedLdapGroupsMapping`, `RuleBasedLdapGroupsMapping.CONVERSION_RULE_KEY`, `LdapGroupsMapping.doGetGroups`, `getGroups`, `getGroupsSet`, Mockito spy/stubbing, and `Configuration`.

Control flow: each test spies a mapping and stubs `doGetGroups("admin", anyInt())` to return a `LinkedHashSet`. With `to_upper`, `getGroups` returns uppercase groups; with `to_lower`, it returns lowercase groups; with invalid rule `none`, `getGroupsSet` returns the original set unchanged.

State and persistence: local configuration and mocked group set only.

Dependencies/integration points: LDAP groups mapping extension used where group names require normalization.

Risks: stubs the LDAP lookup, so only conversion logic is tested; invalid rule behavior is pass-through rather than error.

Test signals: confirms supported conversion rules preserve order while changing case and unsupported rules leave group names unchanged.
