<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFs.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFs.java

## Purpose

`OrangeFs` registers OrangeFS with Hadoop 2's newer `AbstractFileSystem` layer by delegating all operations to an `OrangeFileSystem` instance under the `ofs` scheme.

## Important APIs, Types, and Functions

The only constructor `OrangeFs(URI, Configuration)` calls `DelegateToFileSystem` with a new `OrangeFileSystem`, the scheme string `ofs`, and authority handling disabled via the final boolean argument.

## Control Flow

Hadoop loads this class through `fs.AbstractFileSystem.ofs.impl` in `core-site.xml`. Construction wires the `AbstractFileSystem` facade to the existing `FileSystem` implementation, so all real work flows into `OrangeFileSystem.initialize` and its operation overrides.

## State, Persistence, and Concurrency

This class owns no additional state beyond the delegate created by the superclass. Persistence and concurrency behavior are inherited from `OrangeFileSystem` and OrangeFS.

## Dependencies and Integration Points

It depends on Hadoop `DelegateToFileSystem`, `Configuration`, URI parsing, and the `OrangeFileSystem` class. It is the bridge needed by APIs that use `AbstractFileSystem` rather than `FileSystem.get` directly.

## Risks and Test Signals

The constructor has package visibility, matching Hadoop's reflective construction expectations for this era. Test by resolving `ofs://` paths through both `FileSystem` and `AbstractFileSystem` APIs and confirming operations route to the same OrangeFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFs.java -->
