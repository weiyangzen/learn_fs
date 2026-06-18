# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestLdapGroupsMappingWithFailover.java

Purpose: Tests LDAP URL failover policy under repeated communication failures.

Important APIs/types/functions: `LdapGroupsMapping`, `LDAP_URL_KEY`, `LDAP_NUM_ATTEMPTS_KEY`, `LDAP_NUM_ATTEMPTS_BEFORE_FAILOVER_KEY`, `DummyLdapCtxFactory.setExpectedLdapUrl`, `CommunicationException`, and Mockito `Answer`.

Control flow: disabled-failover test configures three LDAP URLs but sets attempts-before-failover equal to total attempts, expecting all attempts against the first URL. Failover test configures 12 attempts and failover every 2 attempts, uses a queue of URLs to update expected provider URL before each switch, throws `CommunicationException` every search, and verifies total attempts.

State and persistence: static dummy expected URL, queue of URL strings, atomic per-server attempt counter, and mock context invocation count.

Dependencies/integration points: LDAP context recreation/failover logic.

Risks: validates attempts and URL selection through factory side effects rather than returned groups; all paths end empty, so success path after failover is not covered.

Test signals: confirms retry budget and cyclic LDAP server failover behavior on communication errors.
