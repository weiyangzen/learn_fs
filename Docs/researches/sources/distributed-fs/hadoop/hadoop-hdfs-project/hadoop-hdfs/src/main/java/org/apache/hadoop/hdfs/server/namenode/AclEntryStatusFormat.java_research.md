# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclEntryStatusFormat.java

Purpose: packs and unpacks HDFS ACL entries into the 32-bit integer format used both in memory and on disk.

Important APIs/types/functions: enum fields define bit layout: `PERMISSION` 3 bits, `TYPE` 2 bits, `SCOPE` 1 bit, and `NAME` 24 bits. `getScope()`, `getType()`, `getPermission()`, and `getName()` decode fields. `toInt(AclEntry)` encodes scope/type/permission and, for named users/groups, stores a serial number from `SerialNumberManager.USER` or `.GROUP`. `toAclEntry()` rebuilds `AclEntry` objects, optionally using a string table. `toInt(List<AclEntry>)` converts lists.

Control flow: ACL storage converts feature entries into int arrays via this class; reads convert int arrays back into logical `AclEntry` instances. Named entries go through serial-number managers; mask/other/unnamed entries have no name ID.

State and persistence behavior: the bit layout is explicitly compatibility-sensitive because it is persisted in fsimage/edit state. Serial-number IDs tie ACL names to NameNode string tables.

Dependencies and integration points: used by `AclFeature`/`AclStorage`, `LongBitFormat`, `FsAction`, `AclEntryScope`, `AclEntryType`, and `SerialNumberManager`.

Risks: changing field width/order is on-disk incompatible. Enum ordinal dependence means changing enum ordering in Hadoop permission classes would break decoding. Name IDs are limited to 24 bits.

Test signals: ACL fsimage/offline image and NameNode ACL tests cover persistence, named ACL entries, and string-table decoding.
