# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/LongBitFormat.java

Purpose: `LongBitFormat` describes and manipulates a named fixed-width bit field inside a `long` record.

Important APIs/types/functions: constructor takes field name, previous field, bit length, and minimum value, deriving offset, max value, and mask. `retrieve(long)` extracts the field. `combine(long, long)` validates against min/max and inserts the value into the record. `Enum` is a small interface exposing field length. Getters expose min and length.

Control flow: callers typically chain field definitions by passing the previous `LongBitFormat`, then use `combine` and `retrieve` for compact record packing.

State and persistence behavior: immutable and serializable. Packed values are stored in caller-owned long records.

Dependencies and integration points: no Hadoop dependencies beyond package placement. Used by HDFS code that packs multiple numeric fields into inode/block metadata longs.

Risks and test signals: max is computed as `(-1L) >>> (64 - LENGTH)`, so length 64 and invalid lengths need careful treatment. Error messages contain the typo `Illagal`, which tests may not want to rely on. Tests should cover chained offsets, min/max validation, replacing existing field bits, retrieval, and boundary lengths.
