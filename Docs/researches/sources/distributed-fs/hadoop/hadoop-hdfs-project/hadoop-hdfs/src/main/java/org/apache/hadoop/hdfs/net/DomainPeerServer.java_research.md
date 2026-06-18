# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DomainPeerServer.java

Purpose: Implements a `PeerServer` backed by a Unix domain socket for local HDFS data-transfer or short-circuit style connections.

Important APIs and functions: Constructors bind/listen on `DomainSocket.getEffectivePath(path, port)` or wrap an existing `DomainSocket`. `getBindPath()` returns the socket path. `setReceiveBufferSize()` and `getReceiveBufferSize()` manipulate domain socket receive buffer attributes. `accept()` accepts a `DomainSocket` and wraps it in `DomainPeer`. `getListeningString()`, `close()`, and `toString()` provide server metadata and cleanup.

Control flow: Accept blocks on `sock.accept()`, then attempts to construct a `DomainPeer`. If peer construction fails, the partially created peer or raw accepted socket is closed before rethrowing.

State and persistence behavior: Holds one bound `DomainSocket`. The socket file/path persists according to `DomainSocket` behavior until closed/unlinked by that layer. No additional state is stored.

Dependencies and integration points: Depends on Hadoop native `DomainSocket`, `DomainPeer`, and the `PeerServer` interface. It integrates with DataNode peer accept paths that can use domain sockets instead of TCP.

Risks: Domain socket availability and path permissions are platform-dependent. Close logs and suppresses close errors after catching them. Buffer attribute support depends on the native implementation. Failure cleanup must close accepted sockets to avoid descriptor leaks.

Test signals: Tests should bind effective paths, accept local domain clients, verify receive buffer attributes, force `DomainPeer` construction failure for cleanup, close idempotently, and validate listening strings.
