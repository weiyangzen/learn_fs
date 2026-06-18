## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BatchListingOperations.java

Purpose: declares an optional, unstable filesystem extension for listing multiple paths in batched requests.

Important APIs and types: `batchedListStatusIterator(List<Path>)` returns `RemoteIterator<PartialListing<FileStatus>>`; `batchedListLocatedStatusIterator(List<Path>)` returns located entries with block locations.

Control flow: no implementation; filesystem implementations decide batching and iterator behavior. The interface documentation ties support to `CommonPathCapabilities.FS_EXPERIMENTAL_BATCH_LISTING`.

State and persistence behavior: none in the interface.

Dependencies and integration points: integrates with `Path`, `RemoteIterator`, `PartialListing`, `FileStatus`, `LocatedFileStatus`, and path capability probing.

Risks: capability declaration and interface implementation can diverge. Ordering and partial failure semantics are delegated to implementers and need clear implementation-specific tests.

Test signals: for implementers, validate one `PartialListing` per requested path, located status block metadata, error propagation, empty path lists, and capability advertisement.
