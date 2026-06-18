# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandler.java

Purpose: `FsUrlStreamHandler` is the package-private `URLStreamHandler` that creates Hadoop filesystem URL connections.

Important APIs: constructors with default or supplied `Configuration`, and `openConnection(URL)`.

Control flow and state: it stores one configuration reference and creates a new `FsUrlConnection` for each URL. There is no caching or protocol dispatch here; protocol support is decided by the factory.

Dependencies and integration: used by `FsUrlStreamHandlerFactory` and Java URL handling.

Risks: a default constructor creates a fresh `Configuration`, which may not match an application's configured filesystem mappings. Configuration is shared by all connections from the handler.

Test signals: handler opens connections with supplied configuration, default configuration behavior, and compatibility with factory-cached singleton handler.
