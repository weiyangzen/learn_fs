<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ImageServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ImageServlet.java

## Purpose

`ImageServlet` is the NameNode HTTP endpoint for transferring FSImage, edit-log files, and alias map data. It supports checkpoint download by Secondary/Standby NameNodes and checkpoint upload back to active or observer NameNodes.

## Important APIs and Types

`doGet` serves latest or requested image files, finalized edit logs, or alias map bootstrap data. `doPut` receives checkpoint images. Helpers build query strings, set filename and verification headers, configure throttlers, validate requestors, and parse parameters through `GetImageParams` and `PutImageParams`. `ImageUploadRequest` orders concurrent uploads by txid and remote address.

## Control Flow, State, and Persistence

Before serving or accepting data, the servlet obtains `FSImage` from the servlet context, validates initialization, checks Kerberos/admin authorization when security is enabled, and compares storage-info strings. GET opens the target file, sets content length and stored MD5 headers, then copies bytes with configured throttling. PUT checks HA state, suppresses older or duplicate concurrent checkpoint uploads using a synchronized sorted set, rejects too-frequent ordinary image uploads based on checkpoint period and txn thresholds, streams the upload into checkpoint storage, saves the digest, renames the checkpoint image, purges old storage, and removes checkpointing state in `finally`.

## Dependencies and Integration Points

It integrates with Jetty servlets, `NameNodeHttpServer`, `FSImage`, `NNStorage`, `TransferFsImage`, `MD5FileUtils`, `NameNodeMetrics`, `HAServiceProtocol`, `InMemoryAliasMap`, `HttpServer2` admin checks, Kerberos principals for NameNode/Secondary/other HA NameNodes, and DFS image-transfer configuration keys.

## Risks and Test Signals

Risks include authorization gaps, storage-info mismatch handling, races where files disappear after headers, duplicate upload ordering, checkpoint rejection thresholds with clock skew, large-file length handling through `Util.FILE_LENGTH`, and response code distinctions for wrong HA target versus conflict. Tests should cover secure and insecure request validation, latest and txid image GET, edit-log GET, alias-map GET, PUT duplicate conflicts, recent-image rejection override, MD5/content-length headers, throttling config, and cleanup of `currentlyDownloadingCheckpoints` on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ImageServlet.java -->
