# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HAUtilClient.java

`HAUtilClient` provides client-side helpers for HDFS HA logical URIs and delegation-token service names. It distinguishes logical nameservices from physical NameNodes and clones logical HA delegation tokens for concrete NameNode addresses.

Important APIs are `isLogicalUri()`, `isClientFailoverConfigured()`, `buildTokenServiceForLogicalUri()`, `buildTokenServicePrefixForLogicalUri()`, `getServiceUriFromToken()`, `isTokenForLogicalUri()`, and `cloneDelegationTokenForLogicalUri()`.

Logical URI detection compares the URI host to configured nameservice IDs. Failover detection checks the per-host failover proxy provider key. Token helpers create and parse scheme-specific HA token service names. Token cloning selects the logical HA token from UGI credentials, privately clones it for each physical NameNode token service, and inserts aliases intended to avoid accidental propagation of physical tokens.

State is limited to a static `DelegationTokenSelector`; cloning mutates only the supplied `UserGroupInformation`. Dependencies include `DFSUtilClient`, `HdfsClientConfigKeys.Failover`, `HdfsConstants.HA_DT_SERVICE_PREFIX`, Hadoop token APIs, and `SecurityUtil`.

Risks include hostless or malformed URIs not matching logical services, missing source tokens only being logged, and consumers needing the same private alias convention. Test signals include nameservice detection, provider-key detection, service string construction, token URI parsing, logical-token detection, and multi-NameNode cloning with and without a source token.
