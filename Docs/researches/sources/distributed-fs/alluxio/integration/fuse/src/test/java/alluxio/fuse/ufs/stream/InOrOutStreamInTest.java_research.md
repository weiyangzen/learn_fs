# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamInTest.java

Purpose: read-side specialization tests for `FuseFileInOrOutStream` when opened with `O_RDWR` against an existing file. It inherits most behavior from `InStreamTest` and only changes stream creation and write expectations.

Important APIs and control flow: `createStream` invokes `mStreamFactory.create(uri, OpenFlags.O_RDWR.intValue(), DEFAULT_MODE.toShort())`. The overridden `write` test creates a real file, opens the in-or-out stream, writes one byte, and expects `AlreadyExistsRuntimeException`, differentiating O_RDWR-on-existing behavior from a pure read stream's failed-precondition write.

State, dependencies, integration, risks, tests: state includes existing file content created by `writeIncreasingByteArrayToFile`. Dependencies include `FuseFileStream`, JNR open flags, and Alluxio runtime exceptions. The signal is narrow but important: O_RDWR does not imply append/overwrite permission on existing immutable Alluxio files. It does not test O_RDWR creation of missing files because that is covered by the out-side subclass.
