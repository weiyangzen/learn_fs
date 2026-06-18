# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamOutTest.java

Purpose: write-side specialization tests for `FuseFileInOrOutStream` under `O_RDWR`, inheriting the write behavior suite from `OutStreamTest` while checking unsupported read and empty-create behavior.

Important APIs and control flow: `createStream(uri, truncate)` builds `O_RDWR` flags and optionally ORs `O_TRUNC`. The `read` test writes data then calls `read`, expecting `UnimplementedRuntimeException`. `createEmpty` creates the parent directory, opens/closes an in-or-out stream without writing, then expects `NotFoundRuntimeException` when checking status.

State, dependencies, integration, risks, tests: state is a FUSE stream that only materializes a file after write/close, plus backing UFS status. Dependencies include Alluxio file status, create-directory options, and runtime exceptions. The file signals that read-write mode remains operation-specialized: read from the write path is unsupported and empty no-write close does not create a zero-length file in this mode.
