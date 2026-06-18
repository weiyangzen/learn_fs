# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NflyFSystem.java

`NflyFSystem` is a private `FileSystem` implementation for `linkNfly` mount points. It presents multiple target URIs as one filesystem: writes are broadcast to all destinations and considered successful when at least `minReplication` destinations succeed; reads prefer the closest destination or the most recent replica depending on flags.

Important types include `NflyKey` (`minReplication`, `readMostRecent`, `repairOnRead`), `NflyNode`, `MRNflyNode`, `NflyOutputStream`, and `NflyStatus`. Construction wraps each target URI in a `ChRootedFileSystem`, resolves host/rack information with `DNSToSwitchMapping`, and sorts nodes by network distance from the client. `createFileSystem(URI[], Configuration, String, FsGetter)` parses settings and returns an initialized nfly filesystem.

Write control flow creates `_nfly_tmp_<name>` files on all nodes, writes/flushed/closes all still-working streams, drops failing nodes from a `BitSet`, and commits by renaming each successful tmp path to the final path if the surviving count meets `minReplication`. Failed insufficient writes delete tmp files best effort. Reads collect file statuses when `readMostRecent` or `repairOnRead` is enabled, optionally sort by mtime, copy newer replicas to stale/missing nodes through tmp paths, then open the best reachable replica. Rename, delete, mkdirs, status, and list operations fan out or choose a nearest readable node.

State is process-local node topology, flags, and statistics. Durable effects are broad: replicated writes, best-effort delete/rename across all nodes, timestamp normalization, and repair-on-read copies.

Risks include non-atomic cross-filesystem commit, leftover temp files, partial delete/rename results, `append` returning null, stale replica comparison by mtime precision, repair races, and path/status stripping through `NflyStatus`. Tests should simulate partial failures, min-replication thresholds, tmp cleanup, read-most-recent ordering, repair-on-read, all-not-found behavior, list/status path rewriting, and nfly settings validation.
