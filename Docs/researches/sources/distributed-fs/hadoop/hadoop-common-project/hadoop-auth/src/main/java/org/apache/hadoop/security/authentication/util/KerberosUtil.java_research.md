<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosUtil.java

## Purpose
Collects Kerberos/JGSS helper functions for login module selection, realm/principal construction, keytab principal enumeration, subject credential checks, and decoding the server principal from GSS/SPNEGO tokens.

## Important APIs, types, and functions
`getKrb5LoginModuleName()` selects IBM or Sun Kerberos login modules. Static OIDs identify SPNEGO, Kerberos V5, and Kerberos principal-name types. `getDefaultRealm()` and `getDomainRealm()` derive realm information from JVM Kerberos libraries. `getServicePrincipal()` builds lowercased `service/fqdn[@realm]` names. `getPrincipalNames()` reads Apache Kerby keytabs and filters by regex. `hasKerberosKeyTab()` and `hasKerberosTicket()` inspect JAAS subjects. `getTokenServerName()` uses an inner DER iterator to parse a raw GSS token and extract the AP-REQ ticket server principal.

## Control flow
Principal construction fills missing hostnames from the local canonical host and then asks Kerberos domain-realm mapping for a realm. Token decoding unwraps SPNEGO if present, verifies the Kerberos OID and AP-REQ token id, traverses ticket DER fields, and joins service components plus realm.

## State and persistence
The class is stateless except for static OID constants. It reads persistent keytab files but does not modify them.

## Dependencies and integration points
Depends on JGSS, JAAS subject classes, Java Kerberos principal/ticket/keytab types, Apache Kerby keytab parsing, reflection into Sun/IBM Kerberos internals, networking host lookup, and `PlatformName.IBM_JAVA`. Used by Kerberos server/client tests, `KerberosAuthenticationHandler`, and JAAS helpers.

## Risks and test signals
DER parsing is minimal and can throw runtime buffer/tag exceptions for malformed or truncated tokens. Reflection into internal Kerberos classes may fail under module restrictions. Keytab reading normalizes escaped slashes. Tests should cover malformed token lengths, SPNEGO and raw Kerberos tokens, non-Kerberos OIDs, keytab duplicate principals, wildcard filtering, default realm absence, service principal host normalization, and IBM/Sun login module behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosUtil.java -->
