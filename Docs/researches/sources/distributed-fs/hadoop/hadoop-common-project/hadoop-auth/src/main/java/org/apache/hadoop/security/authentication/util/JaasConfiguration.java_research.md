<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/JaasConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/JaasConfiguration.java

## Purpose
Creates an in-memory JAAS configuration entry for Kerberos keytab login, mainly for ZooKeeper clients that need SASL without an external `jaas.conf`.

## Important APIs, types, and functions
The constructor builds an `AppConfigurationEntry` for the platform Kerberos login module with `keyTab`, `principal`, `useKeyTab`, `storeKey`, `useTicketCache=false`, and `refreshKrb5Config=true`. `getAppConfigurationEntry()` returns this entry for the configured name and delegates other names to the previous base configuration. `getKrb5LoginModuleName()` selects IBM or Sun login module by `java.vendor`.

## Control flow
Construction captures the current global JAAS config as a fallback. Later JAAS lookups for the entry name get the generated Kerberos options; unrelated entry names preserve existing behavior.

## State and persistence
Stores the generated entry and fallback config in memory. When installed with `Configuration.setConfiguration()`, it affects global JVM JAAS behavior until replaced.

## Dependencies and integration points
Used by `ZookeeperClient` for SASL/Kerberos Curator connections. Depends on JAAS `Configuration` and `AppConfigurationEntry`, JVM vendor properties, and optional `HADOOP_JAAS_DEBUG`.

## Risks and test signals
Global JAAS replacement can affect unrelated code in the same JVM. IBM module detection here is simpler than `PlatformName.IBM_JAVA`, which can diverge. Tests should cover entry-name matching, fallback delegation, debug env var, keytab/principal option contents, and IBM/Sun module selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/JaasConfiguration.java -->
