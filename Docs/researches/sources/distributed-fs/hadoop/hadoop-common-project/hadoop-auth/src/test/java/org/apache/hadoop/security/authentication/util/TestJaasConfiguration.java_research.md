# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestJaasConfiguration.java

Purpose: Tests `JaasConfiguration` construction of Kerberos login-module entries without performing actual Kerberos authentication.

Important APIs and control flow: the test selects the expected login module name from `java.vendor` (`com.ibm...Krb5LoginModule` for IBM, otherwise `com.sun...Krb5LoginModule`). It constructs `JaasConfiguration("foo", "foo/localhost", "/some/location/foo.keytab")`, verifies unknown entry name `bar` returns null, then inspects entry `foo` for `REQUIRED` control flag and six exact options: `keyTab`, `principal`, `useKeyTab`, `storeKey`, `useTicketCache`, and `refreshKrb5Config`.

State and dependencies: no external Kerberos state is used. Dependencies are JAAS `AppConfigurationEntry`, system property `java.vendor`, JUnit, and Java collections.

Integration points: validates the JAAS configuration used by Kerberos-enabled ZooKeeper clients and authentication utilities.

Risks and test signals: hard-coded option count catches accidental additions/removals but may be too strict for platform-specific JAAS needs. The vendor branch ensures IBM Java remains supported.
