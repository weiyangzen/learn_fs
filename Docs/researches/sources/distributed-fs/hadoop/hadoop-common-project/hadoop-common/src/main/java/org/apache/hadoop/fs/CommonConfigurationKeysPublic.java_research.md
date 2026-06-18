## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeysPublic.java

Purpose: public constant registry for documented Hadoop common configuration keys and defaults, generally mirroring `core-default.xml`.

Important APIs and types: exposes filesystem defaults (`fs.defaultFS`, df/du intervals, trash, file implementation, creation parallelism), topology mapping keys, IO and sequence/TFile tuning, caller context, IPC client/server networking and slow RPC settings, socket factory and SOCKS proxy, group mapping/cache/authentication/security keys, crypto codec defaults for AES and SM4 CTR, KMS client cache/failover settings, secure random and credential provider keys, sensitive config redaction regexes, tags, shutdown timeout, Prometheus/JMX/HTTP metrics settings, and server metrics runner interval.

Control flow: no methods; class initialization builds some default strings from imported crypto codec classes and `CipherSuite` suffixes, and builds the sensitive-config regex list with `String.join`.

State and persistence behavior: constants only. Configuration persistence lives in XML/configuration files and consumers.

Dependencies and integration points: imported throughout Hadoop common, HDFS, MapReduce, security, crypto, KMS, IPC, HTTP, metrics, and filesystem components. `CommonConfigurationKeys` extends this class for internal additions.

Risks: as a public class, constants are API compatibility. Defaults affect cluster behavior, security posture, performance, and backward compatibility. The sensitive config default includes a self-reference constant name string, so consumers must understand it as a redaction pattern list rather than resolving recursively.

Test signals: verify constants align with `core-default.xml`, public deprecations remain available, crypto codec defaults instantiate in expected order, sensitive-key redaction catches cloud and credential patterns, and changed defaults have migration tests.
