<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterS3UfsTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterS3UfsTest.java

**Purpose:** Integration-style test for `FileSystemMaster` metadata sync against an S3-compatible UFS provided by `S3ProxyRule`.

**Important APIs/types/functions:** Uses Alluxio S3 configuration keys, AWS `AmazonS3ClientBuilder`, `S3ProxyRule`, `mount`, `exists`, `MountContext`, and `ExistsContext`.

**Control flow:** `before` configures endpoint, region, path-style access, and credentials from the S3 proxy, creates a bucket, then delegates to the base filesystem master setup. `basicSync` mounts `s3://test-bucket/` at `/s3_mount`, writes an object via the AWS client, and asserts `mFileSystemMaster.exists` sees the mounted object. `basicWrite` is ignored because directory/file creation semantics require client-side data writes outside the master scope.

**State and persistence behavior:** Mutates a local S3 proxy bucket and the Alluxio mount table. The test validates metadata visibility rather than data persistence or file content.

**Dependencies and integration points:** Integrates Alluxio UFS S3 configuration, AWS SDK, S3Proxy, mount table, and filesystem master existence checks. It is sensitive to network port 8001 and local proxy lifecycle.

**Risks:** Fixed proxy port can collide with other processes. The test does not cover write/complete-file behavior, S3 directory marker semantics, credentials failure, or object deletion sync.

**Test signals:** After mounting and uploading `test_file`, `exists(/s3_mount/test_file)` returns true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterS3UfsTest.java -->
