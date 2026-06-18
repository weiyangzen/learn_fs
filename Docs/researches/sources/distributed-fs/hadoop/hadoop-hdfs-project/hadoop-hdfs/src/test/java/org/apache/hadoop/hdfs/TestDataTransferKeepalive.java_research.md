# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataTransferKeepalive.java

Purpose: verifies client and datanode socket keepalive behavior for data-transfer reads, including stale cached peers, client-side expiry, slow-reader write timeout, and many closed sockets in the client cache.

Important APIs and types: `MiniDFSCluster`, `DataNode`, `PeerCache`, `ClientContext`, `Peer`, `FSDataInputStream`, `DFSTestUtil`, `DataNodeProperties`, and socket cache/keepalive/write-timeout config keys.

Control flow: setup starts a one-DN cluster with short datanode keepalive and no block acquire retries. Tests create small or large files, read to populate `PeerCache`, sleep past either DN or client expiry, inspect active xceiver counts, fetch cached peers, restart the DN with a shorter write timeout for slow-reader behavior, and verify reads survive multiple cached closed sockets.

State and persistence: creates `/test`, fills client peer caches keyed by `DFS_CLIENT_CONTEXT`, restarts datanode with modified config, and observes datanode xceiver thread counts.

Dependencies and integration: integrates client peer caching, datanode xceiver lifecycle, socket EOF handling, restart properties, stream close cleanup, and DataNode write timeout behavior.

Risks: timing-sensitive sleeps and xceiver-count polling; direct reliance on internal peer cache and datanode thread counts; slow-reader test has a long timeout because it waits for server-side timeout.

Test signals: expected `PeerCache` sizes, expected xceiver counts, EOF from stale cached peer, null return for expired client peer, eventual xceiver exit during slow read, and successful read despite closed cached sockets.
