# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DirectoryListing.java

## Purpose
`DirectoryListing` is the response type for iterative single-directory listing through `ClientProtocol.getListing`. It carries a partial array of `HdfsFileStatus` plus a count of remaining entries.

## APIs and Behavior
The constructor rejects null listings and the inconsistent state of an empty listing with nonzero remaining entries. `getPartialListing()` returns the array, `getRemainingEntries()` exposes the remaining count, `hasMore()` checks whether the count is nonzero, and `getLastName()` returns the local-name bytes of the last entry for use as the next `startAfter` cursor.

## State, Dependencies, and Integration
The object is mutable only through its exposed array reference. It integrates with `ClientProtocol.getListing`, `DFSClient` directory iteration, and `HdfsFileStatus` path-name encoding. No persistence happens here.

## Risks and Test Signals
The array is not defensively copied, so cursor behavior can be corrupted by caller mutation. Tests should cover constructor validation, empty terminal listings, cursor extraction from the last entry, and correct handling of UTF-8 local-name bytes.
