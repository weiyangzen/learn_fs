# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsServerDefaults.java

Purpose: `FsServerDefaults` is a writable value object carrying server-side filesystem defaults to clients: block size, checksum settings, packet size, replication, buffer size, transfer encryption, trash interval, checksum type, key provider URI, storage policy ID, and snapshot trash-root flag.

Important APIs: overloaded constructors, getters for every field, static `WritableFactories` registration, and `Writable.write/readFields`.

Control flow and state: instances hold simple fields. Serialization writes only block size, checksum bytes, write packet size, replication, file buffer size, checksum type, and storage policy ID. It does not serialize `encryptDataTransfer`, `trashInterval`, `keyProviderUri`, or `snapshotTrashRootEnabled` in this implementation, so those values are constructor/runtime only unless carried by other protocol layers.

Dependencies and integration: used by `FileSystem.getServerDefaults`, clients creating files, HDFS protocol adapters, `DataChecksum.Type`, and Hadoop `Writable` factories.

Risks: writable compatibility is delicate because omitted fields may appear default after round-trip. Constructors chain defaults, so additions must preserve old behavior. Null/empty key provider URI has semantic meaning for encryption-zone support.

Test signals: round-trip writable tests, constructor default tests, checksum enum serialization, key provider semantics, storage policy ID propagation, and compatibility with older clients.
