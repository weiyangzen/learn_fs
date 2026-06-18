# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtilClient.java

Purpose: focused client-side JSON helper tests for simple array conversion and block-location decoding.

Important APIs/types/functions: `JsonUtilClient.toStringArray`, `toBlockLocationArray`, `JsonUtil.toJsonMap`, `JsonUtil.toJsonString`, `JsonSerialization.mapReader`, `BlockLocation`, `StorageType`.

Control flow: `testToStringArray` converts a three-element `List<String>` and asserts length/order. `testToBlockLocationArray` builds a `BlockLocation` with names, hosts, topology path, storage type, offset, and length, serializes it through WebHDFS JSON helpers, parses it back to a map, converts via `JsonUtilClient`, and compares the string representation to the original block location.

State and persistence behavior: in-memory only.

Dependencies and integration points: verifies client JSON utility behavior used by WebHDFS block location REST responses and simple list conversion.

Risks: block-location comparison uses `toString`, which may miss fields not included in the string representation. Only a single block and storage type are covered.

Test signals: ordered string-array conversion and one-block BlockLocation JSON round trip.
