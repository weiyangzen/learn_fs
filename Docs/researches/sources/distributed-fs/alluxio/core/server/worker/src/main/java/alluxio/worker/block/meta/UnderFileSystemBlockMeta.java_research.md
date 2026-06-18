# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/UnderFileSystemBlockMeta.java

Purpose: Immutable metadata for a block read directly from an under filesystem.

Important APIs: Constructor from session ID, block ID, and `Protocol.OpenUfsBlockOptions`; getters for session, block ID, UFS path, file offset, block size, mount ID, no-cache flag, and user.

Control flow: The constructor copies all relevant fields from the proto options, after which read paths can use the metadata without depending on the mutable request object.

State and persistence: Immutable in-memory state only. It references UFS path and mount IDs but does not persist data.

Dependencies and integration: Used by UFS block read paths and UFS input stream management.

Risks and test signals: The Javadoc contains a garbled proto class reference, but runtime uses `Protocol.OpenUfsBlockOptions`. Tests should cover field copying, no-cache behavior downstream, and offset/size boundaries.
