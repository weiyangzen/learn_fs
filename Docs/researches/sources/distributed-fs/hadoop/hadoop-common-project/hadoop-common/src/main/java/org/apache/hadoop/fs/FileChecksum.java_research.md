## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileChecksum.java

Purpose: `FileChecksum` is the public stable abstract base for file checksum objects returned by Hadoop filesystems. It standardizes algorithm name, byte length, checksum bytes, optional checksum options, and equality/hash behavior.

Important APIs and types: subclasses implement `getAlgorithmName`, `getLength`, `getBytes`, and Writable serialization methods inherited from `Writable`. `getChecksumOpt()` returns null by default and can be overridden by implementations such as `CompositeCrcFileChecksum`. `equals` compares algorithm names and byte arrays; `hashCode` XORs their hashes.

Control flow, state, and persistence: this class stores no state. It defines value semantics over subclass-reported algorithm and bytes. Persistence is delegated to each concrete Writable implementation.

Dependencies and integration: it is returned by `FileSystem.getFileChecksum` and `AbstractFileSystem` checksum paths, and used by applications to compare file content integrity across filesystems. It depends on `Arrays`, `Options.ChecksumOpt`, and `Writable`.

Risks and test signals: risks include subclasses returning mutable arrays, null algorithm names, inconsistent `getLength` vs `getBytes().length`, or incomplete Writable state. Tests should cover equality/hash consistency, algorithm mismatch, byte mismatch, null/default checksum options, and concrete subclass serialization contracts.
