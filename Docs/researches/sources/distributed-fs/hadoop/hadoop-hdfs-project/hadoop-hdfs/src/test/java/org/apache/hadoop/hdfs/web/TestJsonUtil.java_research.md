# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtil.java

Purpose: unit coverage for server/client WebHDFS JSON conversion helpers.

Important APIs/types/functions: `JsonUtil.toJsonString/toJsonMap`, `JsonUtilClient.toFileStatus`, `toDatanodeInfo`, `toAclStatus`, `toXAttrs`, `getXAttr`, `toSnapshotDiffReportListing`, `HdfsFileStatus.Builder`, `AclStatus`, `ContentSummary`, `SnapshotDiffReportListing`.

Control flow: file-status tests build `HdfsFileStatus` objects with and without EC policy and symlink data, serialize to JSON, parse with Jackson, reconstruct client-side status, and compare `FileStatus` equivalence. Datanode tests decode current and legacy `name`-based maps and assert invalid/missing address forms fail. ACL, content summary, and XAttr tests compare exact JSON strings or parsed structures. Snapshot diff listing tests round-trip empty and populated modify/create/delete entry lists and compare all fields/byte arrays.

State and persistence behavior: pure in-memory maps, JSON strings, and protocol objects.

Dependencies and integration points: bridges WebHDFS REST JSON shape with HDFS protocol classes, ACL/XAttr helpers, erasure coding policy encoding, and snapshot diff pagination models.

Risks: exact JSON string assertions are order-sensitive and tightly coupled to serializer output. `checkDecodeFailure` accepts any exception, not a specific parse error. Some timestamps use `Time.now`, but equality is round-trip based.

Test signals: JSON round-trip fidelity, backward-compatible datanode decoding, ACL/XAttr/content summary encoding, and snapshot diff listing preservation.
