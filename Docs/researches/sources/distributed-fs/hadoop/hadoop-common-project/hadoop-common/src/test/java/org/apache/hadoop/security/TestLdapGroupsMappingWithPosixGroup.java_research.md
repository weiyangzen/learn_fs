# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithPosixGroup.java

Purpose: Tests LDAP group lookup configured for POSIX account/group schemas.

Important APIs/types/functions: `LdapGroupsMapping` POSIX config keys, `GROUP_SEARCH_FILTER_KEY`, `USER_SEARCH_FILTER_KEY`, `GROUP_MEMBERSHIP_ATTR_KEY`, `POSIX_UID_ATTR_KEY`, `POSIX_GID_ATTR_KEY`, `GROUP_NAME_ATTR_KEY`, mocked LDAP attributes, and inherited base fixtures.

Control flow: setup mocks user attributes `uid`, `uidNumber`, and `gidNumber`. The test stubs searches containing `posix` to return user then group enumerations, configures POSIX filters and attributes, gets groups for `some_user`, then changes `POSIX_UID_ATTR_KEY` from `uidNumber` to `uid` and asserts the same groups.

State and persistence: mock LDAP attributes/search results and mutable mapping configuration.

Dependencies/integration points: POSIX LDAP schema support in `LdapGroupsMapping`.

Risks: search verification expects only two calls even after a second `getGroups` path may use cached context/state; does not validate exact filter arguments beyond containing `posix`.

Test signals: confirms POSIX UID/GID attributes can drive group lookup and alternate UID attribute configuration remains valid.
