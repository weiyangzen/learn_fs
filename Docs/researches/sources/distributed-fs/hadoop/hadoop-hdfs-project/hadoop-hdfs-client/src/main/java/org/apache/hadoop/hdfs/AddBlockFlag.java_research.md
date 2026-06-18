# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/AddBlockFlag.java

Purpose: private evolving enum of hints for NameNode block allocation and replica placement.

Important APIs and types: values are `NO_LOCAL_WRITE`, `IGNORE_CLIENT_LOCALITY`, and `NO_LOCAL_RACK`, each with a short mode. `valueOf(short)` maps wire/encoded mode back to enum or returns null; `getMode()` exposes the short.

Control flow and state: simple enum lookup loops over all values. Modes are stable protocol-adjacent values used by `ClientProtocol#addBlock()`.

Dependencies and integration: references `CreateFlag` equivalents and HDFS `ClientProtocol.addBlock`.

Risks and test signals: returning null for unknown modes makes caller handling important. `NO_LOCAL_RACK` uses mode `0x03`, not a bitmask combination in this enum, so consumers should treat modes as enum identifiers unless protocol code documents otherwise.
