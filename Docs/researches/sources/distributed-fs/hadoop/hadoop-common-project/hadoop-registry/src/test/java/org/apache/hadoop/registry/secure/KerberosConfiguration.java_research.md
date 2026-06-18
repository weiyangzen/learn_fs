# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/KerberosConfiguration.java

Purpose: test-only JAAS `Configuration` implementation for Kerberos client and server logins.

Important APIs and functions: factory methods `createClientConfig()` and `createServerConfig()` set `isInitiator`; `getAppConfigurationEntry()` returns one required Krb5 login module entry with JVM-specific options; `toString()` reports the principal.

Control flow: IBM Java gets `useKeytab`, `credsType`, and optional `useDefaultCcache`; other JVMs get `keyTab`, `useKeyTab`, `storeKey`, `doNotPrompt`, `useTicketCache`, `renewTGT`, `refreshKrb5Config`, and `isInitiator`. If `KRB5CCNAME` is present, ticket cache options are added.

State and persistence: stores principal, absolute keytab path, and initiator flag. May set the `KRB5CCNAME` system property on IBM Java.

Dependencies and integration: used by secure registry tests to create `LoginContext` instances. It depends on Hadoop `KerberosUtil` and platform detection.

Risks and test signals: option differences across JVMs are a portability risk. Debug is always enabled, which is helpful for tests but noisy.
