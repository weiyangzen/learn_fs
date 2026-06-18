# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestFixKerberosTicketOrder.java

Purpose: MiniKDC regression coverage for HADOOP-13433, ensuring `UserGroupInformation.fixKerberosTicketOrder` keeps the TGT first and removes destroyed TGTs.

Important APIs/types/functions: `KerberosSecurityTestcase`, `MiniKdc` via `getKdc`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `fixKerberosTicketOrder`, `reloginFromKeytab`, `Subject.getPrivateCredentials`, `KerberosTicket`, `Sasl.createSaslClient`, and `LambdaTestUtils.intercept`.

Control flow: setup creates client and server principals in a keytab and enables Kerberos. The main test obtains a service ticket, manually moves the TGT to the end, confirms a new service ticket request fails, calls `fixKerberosTicketOrder`, verifies the TGT is first, then obtains another service ticket. The destroyed-TGT test destroys the TGT, fixes order, expects no ticket, verifies service-ticket acquisition fails, relogs in, and succeeds.

State and persistence: MiniKDC principals/keytab, UGI subject private credentials, Kerberos tickets, SASL properties, and global immediate-renew test flag.

Dependencies/integration points: Kerberos, JAAS/SASL, Hadoop UGI ticket management.

Risks: highly JDK/Kerberos-implementation sensitive; mutates private credential collection directly; assumes first KerberosTicket ordering matters.

Test signals: catches regressions where service tickets precede TGT or destroyed TGTs remain and break future Kerberos service-ticket acquisition.
