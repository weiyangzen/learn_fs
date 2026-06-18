<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterPartialListingTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterPartialListingTest.java

**Purpose:** Parameterized suite for partial `FileSystemMaster.listStatus` behavior with batch size, offset id, offset count, prefix, start-after, recursion, deletion, and rename interactions.

**Important APIs/types/functions:** Uses `listStatus` with `ListStatusPartialPOptions` wrapped in `ListStatusContext`, helper generators for prefix/startAfter/offsetCount/offsetId, `context.isTruncated`, `context.getTotalListings`, `delete`, and `rename`.

**Control flow:** The suite creates fixed path sets under root and nested directories, then checks sorted non-recursive listings, depth-first recursive listings, prefix filtering, start-after filtering, and partial paging. It validates offset-id and offset-count forms produce equivalent pages. Mutation tests delete or rename the inode referenced by an offset and verify listing either continues when the inode remains in the same directory or fails when the offset no longer exists under the listing root. Batch tests build 13 files and five nested levels to verify repeated page traversal, final empty page behavior, and total-listing counts.

**State and persistence behavior:** Tests file-system metadata state in `InodeStore` and path topology. It validates cursor stability against inode ids, path renames, and deletions. Recursive partial listings report `totalListings == -1`, while non-recursive listings report total counts.

**Dependencies and integration points:** Extends `FileSystemMasterTestBase`, parameterized by inode store factory. Integrates `DeleteContext`, `RenameContext`, `LoadMetadataPType.NEVER`, `FileInfo` ids/paths, and `InvalidPathException`/`FileDoesNotExistException` error paths.

**Risks:** Assertions encode specific sort and depth-first order; changes to listing order will break many tests. Cursor behavior is subtle: offset id is stronger but can fail after deletion, while startAfter is path-based. Large repetitive loops can obscure the exact failing page without good assertion output.

**Test signals:** Expected page sizes, exact ordered paths, truncation flags, total listings, exceptions for invalid offsets or prefixes, empty results after final page, and equivalence between offset count and offset id for stable listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterPartialListingTest.java -->
