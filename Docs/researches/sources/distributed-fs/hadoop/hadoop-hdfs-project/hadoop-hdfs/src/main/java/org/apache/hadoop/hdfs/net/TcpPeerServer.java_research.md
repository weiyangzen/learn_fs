# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/TcpPeerServer.java

Purpose: Implements a TCP-backed `PeerServer` for HDFS DataNode data-transfer connections, including both regular and pre-bound secure-server-socket construction.

Important APIs and functions: The normal constructor creates a `ServerSocket` or `ServerSocketChannel`-backed socket depending on write-timeout needs, then binds via `Server.bind`. The secure constructor wraps `SecureResources.getStreamingSocket()`. `getStreamingAddr()` returns the bound IP and port. `setReceiveBufferSize()`, `getReceiveBufferSize()`, `accept()`, `getListeningString()`, `close()`, and `toString()` implement `PeerServer`.

Control flow: Normal construction selects channel-backed sockets when socket write timeout is positive, binds with configured backlog, and later `accept()` converts accepted sockets to Hadoop `Peer` objects using `DFSUtilClient.peerFromSocket`.

State and persistence behavior: Holds one `ServerSocket`, either created locally or supplied by secure DataNode startup. No additional persistent state is kept.

Dependencies and integration points: Depends on Java networking, Hadoop IPC `Server.bind`, `DFSUtilClient.peerFromSocket`, `SecureDataNodeStarter.SecureResources`, and `PeerServer`. It is used by DataNode xfer server setup.

Risks: Secure mode depends on the pre-bound socket lifecycle from privileged startup. `getStreamingAddr()` uses `getHostAddress()` and local port, which may differ from advertised hostnames. Close logs and suppresses close errors. Channel-backed socket choice must match write-timeout behavior expected by peers.

Test signals: Tests should bind normal and secure sockets, verify backlog/bind address, accept a TCP client and produce a `Peer`, check receive buffer sizing, verify streaming address for wildcard/specific binds, and close under active/idle states.
