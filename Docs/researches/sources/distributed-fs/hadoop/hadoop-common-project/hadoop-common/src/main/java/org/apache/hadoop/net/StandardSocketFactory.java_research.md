# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/StandardSocketFactory.java

Purpose: standard Hadoop `SocketFactory` that creates NIO-backed sockets so Hadoop can wrap them with timeout-aware channel streams.

Important APIs/types/functions: constructor, all `createSocket` overloads, `equals`, and `hashCode`.

Control flow: `createSocket()` opens a `SocketChannel` and returns its socket. Other overloads bind and/or connect the created socket.

State and persistence: stateless; equality is class-based.

Dependencies and integration: used by `NetUtils` and default Hadoop networking. Its sockets should be consumed with `NetUtils.getInputStream` and `NetUtils.getOutputStream`, not raw socket streams, because channel mode interactions can block in surprising ways.

Risks: the class comment says SOCKS proxy but implementation is standard NIO sockets. Users that call `Socket.getInputStream()`/`getOutputStream()` directly can hit blocking-mode issues after Hadoop wrappers configure nonblocking mode.

Test signals: covered indirectly by `NetUtils` and socket timeout tests.
