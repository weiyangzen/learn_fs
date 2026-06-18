# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NetworkTopologyServlet.java

## Purpose
`NetworkTopologyServlet` exposes the NameNode's DataNode network topology at `/topology` in text or JSON form.

## Important APIs, types, and functions
`doGet` resolves the NameNode, obtains `BlockManager`, gets network topology leaves, negotiates format from the Accept header, and delegates to `printTopology`. `printTopology` groups nodes by rack and sorts racks/nodes. `printJsonFormat` emits rack objects with `ip` and optional `hostname`; `printTextFormat` emits readable rack listings. `parseAcceptHeader` returns JSON when Accept contains `json`, otherwise text.

## Control flow
Empty topology prints `No DataNodes`. Printing errors send HTTP 410 and throw an `IOException`. The response stream is wrapped in a UTF-8 `PrintStream` and closed in `finally`.

## State and persistence behavior
The servlet is stateless and read-only. It reflects in-memory DataNode topology and optional reverse DNS lookup results.

## Dependencies and integration points
It depends on servlet APIs, `NameNodeHttpServer`, `BlockManager`, `NetworkTopology`, `Node`, `NodeBase`, Jackson JSON generation, HTTP headers, and `NetUtils`. It is installed by `NameNodeHttpServer`.

## Risks and invariants
JSON/text output shape can be consumed by tools. Accept negotiation is deliberately simple. Reverse DNS may be slow or absent. Closing the servlet output stream is existing behavior and should be changed carefully.

## Test signals
Test empty topology, sorted text output, JSON output, default text when Accept is absent, hostname omission, and error response behavior. Router topology servlet tests provide analogous coverage.
