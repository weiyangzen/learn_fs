# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocksSocketFactory.java

Purpose: Hadoop-configurable `SocketFactory` that creates sockets through a SOCKS proxy.

Important APIs/types/functions: constructors, all `createSocket` overloads, `setConf`, `getConf`, equality/hash code, and private `setProxy`.

Control flow: the default proxy is `Proxy.NO_PROXY`. `setConf` reads `hadoop.socks.server` and parses `host:port` into an unresolved SOCKS proxy. Socket overloads create a proxy-backed socket, optionally bind a local address, and connect to the remote endpoint.

State and persistence: stores `Configuration` and `Proxy`; no persistence.

Dependencies and integration: used by Hadoop networking code when a socket factory class is configured. Depends on `CommonConfigurationKeysPublic.HADOOP_SOCKS_SERVER_KEY`.

Risks: malformed proxy strings throw runtime exceptions, and non-numeric ports throw `NumberFormatException`. `setConf(null)` would dereference null. Equality is proxy-based, so factories with equivalent proxy settings compare equal.

Test signals: usually covered through socket factory and `NetUtils` tests; additional tests should cover malformed proxy configuration.
