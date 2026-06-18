# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosUtil.java

Purpose: Tests miscellaneous Kerberos utility behavior: service-principal construction, keytab principal extraction and filtering, and ASN.1 token server-principal decoding.

Important APIs and control flow: `testGetServerPrincipal` checks `KerberosUtil.getServicePrincipal` for null, empty, wildcard `0.0.0.0`, uppercase, and lowercase hosts, using `getLocalHostName`, `getDefaultRealmProtected`, and `getDomainRealm` assumptions. Keytab tests create a synthetic keytab with Apache Kerby `Keytab`, adding three kvnos per principal to ensure `getPrincipalNames` deduplicates entries and regex filtering works. `testServicePrincipalDecode` decodes embedded base64 krb5 and SPNEGO tokens and verifies `getTokenServerName`.

State and dependencies: persistent state is a local `test.keytab`, deleted in `@AfterEach`. Dependencies include Apache Kerby keytab types, Java regex, base64, locale, and Hadoop `KerberosUtil`.

Integration points: principal construction affects service login names and host canonicalization; keytab discovery is used by dynamic Kerberos handler principal loading; token decoding supports audit/routing of SPNEGO/Kerberos tokens.

Risks and test signals: `testGetServerPrincipal` depends on local realm/domain lookup behavior and may be environment-sensitive. `deleteKeytab` ignores deletion failure. The embedded binary-token strings provide strong regression coverage for ASN.1 parsing but are opaque and hard to update safely.
