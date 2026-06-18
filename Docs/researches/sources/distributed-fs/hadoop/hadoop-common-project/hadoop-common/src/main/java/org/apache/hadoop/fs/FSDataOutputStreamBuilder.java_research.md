## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStreamBuilder.java

Purpose: `FSDataOutputStreamBuilder` is the public evolving abstract builder for creating or appending `FSDataOutputStream` instances through either `FileSystem` or `FileContext` pathways.

Important APIs and types: it extends `AbstractFSBuilderImpl<S, B>` and stores filesystem/default write settings: permission, buffer size, replication, block size, recursive parent creation, create flags, progress callback, and checksum options. Fluent methods include `permission`, `bufferSize`, `replication`, `blockSize`, `recursive`, `progress`, `create`, `overwrite`, `append`, and `checksumOpt`. Concrete subclasses implement `getThisBuilder()` and `build()`.

Control flow, state, and persistence: constructors derive defaults from `FileContext` server defaults or `FileSystem` configuration/default replication/block size. `getPermission()` lazily supplies `FsPermission.getFileDefault()`. `overwrite(false)` removes the overwrite flag; `create()` and `append()` add flags. State is held in the builder until `build()`; no persistence exists.

Dependencies and integration: it bridges public builder calls to `FileSystem` and `AbstractFileSystem` create/append implementations, relying on `CreateFlag`, `Options.ChecksumOpt`, `FsPermission`, `Progressable`, and common IO buffer configuration.

Risks and test signals: risks include inconsistent defaults between FileSystem and FileContext paths, mutable flag set exposure through protected getter, and unsupported mandatory options handled by subclasses. Tests should cover defaults, fluent chaining, recursive flag, overwrite toggling, permission defaulting, checksum option propagation, and subclass build validation.
