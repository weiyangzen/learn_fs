<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterOptionsTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterOptionsTest.java

**Purpose:** Minimal unit test for `FileSystemMasterOptions.completeFileDefaults`.

**Important APIs/types/functions:** Uses `FileSystemMasterOptions.completeFileDefaults` and gRPC `CompleteFilePOptions`.

**Control flow:** The single test obtains defaults, asserts the options object is non-null, and asserts `ufsLength` defaults to 0.

**State and persistence behavior:** No mutable state or persistence. It protects the default option contract used by complete-file operations.

**Dependencies and integration points:** Depends only on JUnit and Alluxio gRPC option type. It is a low-level guard for callers relying on implicit complete-file defaults.

**Risks:** Coverage is intentionally narrow and does not validate other default fields or interactions with complete-file logic.

**Test signals:** Non-null options and `getUfsLength() == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterOptionsTest.java -->
