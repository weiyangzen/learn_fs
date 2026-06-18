# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestRaceWhenRelogin.java

Purpose: Concurrency regression test for HADOOP-13433, ensuring repeated Kerberos relogin keeps the TGT as the first ticket while other threads acquire service tickets.

Important APIs/types/functions: `KerberosSecurityTestcase`, `UserGroupInformation.reloginFromKeytab`, `getSubject().getPrivateCredentials`, `KerberosTicket`, `Sasl.createSaslClient`, `ThreadLocalRandom`, `AtomicBoolean`, and MiniKDC principal creation.

Control flow: setup creates a keytab with client and multiple server principals, enables Kerberos, and logs in the client UGI. The test starts one relogin thread that calls relogin 100 times and verifies first ticket starts with `krbtgt`; ten service-ticket threads repeatedly create SASL clients for different server protocols until stopped. Final assertion requires no relogin iteration observed wrong ticket order.

State and persistence: MiniKDC/keytab, shared UGI subject credentials, Kerberos ticket collection, many threads, and global immediate-renew flag.

Dependencies/integration points: Kerberos ticket renewal, SASL service-ticket acquisition, concurrent UGI credential mutation.

Risks: race/timing-dependent by design; exceptions inside service-ticket threads are swallowed; test duration includes sleeps up to roughly five seconds plus service-thread delays.

Test signals: catches synchronization regressions where concurrent service-ticket acquisition reorders credentials so TGT is no longer first after relogin.
