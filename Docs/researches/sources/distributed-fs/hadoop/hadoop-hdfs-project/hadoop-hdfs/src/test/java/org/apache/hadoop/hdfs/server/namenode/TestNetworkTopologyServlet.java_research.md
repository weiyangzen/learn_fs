# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNetworkTopologyServlet.java

Purpose: Tests the NameNode `/topology` HTTP servlet in text and JSON modes for clusters with racked DataNodes and for clusters with no DataNodes.

Important APIs and functions: Tests start `MiniDFSCluster` with rack arrays, retrieve `cluster.getHttpUri(0)`, open `HttpURLConnection` to `/topology`, optionally set `Accept: application/json`, and parse JSON with Jackson `ObjectMapper`. `StaticMapping.resetMap` clears network topology mappings before each scenario.

Control flow: Text format test starts ten DataNodes across five racks, downloads the servlet response, wraps it with banner text for matching, asserts every rack label appears, and counts `127.0.0.1` occurrences. JSON format test repeats the topology, requests JSON, parses rack nodes, asserts five rack entries, and counts all DataNode entries. No-DataNode tests start zero-DataNode clusters and assert text or JSON-requested response contains "No DataNodes".

State and persistence behavior: No persistent namespace state is relevant. Runtime DataNode registration and rack mapping state feeds servlet output.

Dependencies and integration points: Integrates NameNode HTTP server, network topology/rack mapping, MiniDFSCluster DataNode registration, Jackson JSON parsing, and HTTP content negotiation through the Accept header.

Risks: Text counting assumes local DataNode host strings contain `127.0.0.1`. JSON shape traversal assumes the servlet response is a rack object containing child fields whose values are node arrays. Connections are not wrapped in cluster shutdown finally blocks, so failures before test exit could leave temporary clusters until JVM cleanup.

Test signals: Passing requires rack names and all DataNodes present in text output, JSON rack count and DataNode count matching the cluster layout, and explicit "No DataNodes" output for empty clusters.
