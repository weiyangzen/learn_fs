# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractTest.java

Purpose: base fixture for testing FUSE against a UFS-backed Alluxio filesystem. It supports either a local temporary UFS or an S3A-backed path selected by the `alluxio.test.s3a.path` system property.

Important APIs and control flow: `before` copies global configuration, chooses the UFS path, registers `S3AUnderFileSystemFactory` or `LocalUnderFileSystemFactory`, sets `FUSE_MOUNT_POINT`, creates `FileSystemContext`, loads libfuse using `AlluxioFuseUtils.getLibfuseVersion`, creates `UfsFileSystemOptions`, and constructs `UfsBaseFileSystem`. It then calls subclass `beforeActions`. `after` recursively deletes the UFS root and calls `afterActions`.

State, dependencies, integration, risks, tests: state includes `mRootUfs`, `mFileSystem`, `mContext`, `mUfsOptions`, and `mIsLocalUFS`. Dependencies include Alluxio test directories, underfs factory registry, libfuse loading, and local/S3 UFS implementations. Risk: global factory registration and lib loading can affect neighboring tests; S3 mode depends on external credentials/path.
