# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExtendedBlockId.java

`ExtendedBlockId` is an immutable key for an HDFS block, consisting of `blockId` and block pool ID. It gives caches and maps a compact identity value without retaining a full `ExtendedBlock`.

The public API is `fromExtendedBlock(ExtendedBlock)`, the `(long, String)` constructor, getters, and overrides for `equals()`, `hashCode()`, and `toString()`. Equality requires the same runtime class and matching block ID and pool ID; hashing uses Apache Commons Lang builders.

There is no complex control flow or persistence. Both fields are final, and the diagnostic string shape is `blockId_bpId`. Dependencies are `ExtendedBlock`, `EqualsBuilder`, and `HashCodeBuilder`.

Risks are small: the constructor does not validate `bpId`, and callers should not treat `toString()` as a stable serialized format unless explicitly documented elsewhere. Test signals include conversion from `ExtendedBlock`, equality/hash behavior, null pool IDs if callers permit them, and string format.
