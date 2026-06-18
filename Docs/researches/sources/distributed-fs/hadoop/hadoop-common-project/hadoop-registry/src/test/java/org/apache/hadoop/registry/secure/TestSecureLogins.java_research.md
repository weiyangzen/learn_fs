# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureLogins.java

Purpose: validates Kerberos login plumbing used by secure registry tests.

Important APIs and functions: tests verify realm availability, JAAS file binding, Alice and ZooKeeper `LoginContext` creation, direct Krb5 login module reflection, default realm lookup, Kerberos rule configuration, valid Kerberos short-name parsing under Hadoop and MIT mechanisms, and keytab-based UGI login plus SASL ACL creation.

Control flow: login tests create contexts from keytabs, log subject details, set ZooKeeper SASL client properties, and always log out. `testKerberosAuth()` reflects into the Krb5 login module and manually calls `initialize`, `login`, and `commit` with platform-specific options.

State and persistence: relies on MiniKdc/keytabs/JAAS from the superclass. It mutates Kerberos rule mechanism and resets it to the default mechanism.

Dependencies and integration: integrates MiniKdc, JAAS, Hadoop UGI, HadoopKerberosName, KerberosUtil, ZooKeeper environment keys, and registry security ACL helpers.

Risks and test signals: strong end-to-end signal for local Kerberos setup. Reflection into JDK login modules and default realm lookup are environment-sensitive; failures may indicate platform/security setup rather than registry code defects.
