# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/Hdfs.java

Purpose: `AbstractFileSystem` implementation for the `hdfs` URI scheme, delegating filesystem operations to `DFSClient`.

Important APIs and functions: constructor validates scheme/host and creates `DFSClient`; overrides create, delete, block locations, checksum, status, link status, filesystem status/defaults, listing, corrupt block listing, mkdir, open, truncate, rename, owner/permission/replication/times, checksum verification, symlinks, canonical service name, delegation tokens, ACLs, xattrs, access checks, storage policies, token renew/cancel, and snapshots.

Control flow: most methods translate `Path` to URI path and call `DFSClient`. Listing has notable batching behavior: `DirListingIterator` fetches first batch and lazily fetches more when exhausted; `listStatus()` eagerly accumulates all batches into an array and throws if the directory disappears between batches. File status methods convert `HdfsFileStatus` into qualified `FileStatus` objects and throw `FileNotFoundException` on null.

State and persistence: state is a `DFSClient` and mutable `verifyChecksum` flag. Persistent data lives in HDFS NameNode/DataNode state, not in this wrapper. Delegation token operations affect HDFS security token lifecycle.

Dependencies and integration: integrates FileContext `AbstractFileSystem`, `DFSClient`, HDFS protocol statuses, ACL/xattr/storage policy APIs, token APIs, corrupt block iterator, and HDFS configuration initialization.

Risks and test signals: wrapper correctness depends on consistent path translation and exception mapping. `getDelegationTokens()` adds the returned token without null filtering, so callers must tolerate whatever `DFSClient.getDelegationToken()` returns. No tests in this subset directly exercise `Hdfs`; coverage likely lives elsewhere in HDFS client tests.
