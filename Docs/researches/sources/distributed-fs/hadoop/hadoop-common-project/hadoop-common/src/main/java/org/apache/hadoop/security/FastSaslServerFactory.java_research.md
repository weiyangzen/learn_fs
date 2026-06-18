# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslServerFactory.java


Purpose: `FastSaslServerFactory` is the server-side companion to `FastSaslClientFactory`, caching JVM `SaslServerFactory` instances by mechanism.

Important APIs and types: It implements `SaslServerFactory`, stores mechanism-to-factory lists, returns cached mechanism names, and creates the first non-null `SaslServer` for a mechanism/protocol/serverName tuple.

Control flow and state: The constructor snapshots `Sasl.getSaslServerFactories()` for the supplied props. `createSaslServer()` looks up the mechanism and tries each cached provider in order until one accepts.

Dependencies and integration: It depends on Java SASL and JAAS callback handling. Hadoop RPC server setup uses it to reduce repeated provider scans.

Risks and test signals: As with the client factory, the cache is static from construction time. Tests should cover missing mechanisms, provider ordering, and policy props such as no-plaintext.
