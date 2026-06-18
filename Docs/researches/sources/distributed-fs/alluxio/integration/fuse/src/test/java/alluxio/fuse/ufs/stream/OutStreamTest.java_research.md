# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/OutStreamTest.java

Purpose: tests `FuseFileOutStream`, the write-only stream implementation for FUSE writes. It focuses on file creation, truncation bookkeeping, sequential writes, and unsupported read/random-write paths.

Important APIs and control flow: `createStream` uses `O_WRONLY` and optional `O_TRUNC`. Tests cover empty file creation, create-existing failure, truncate flag overwrite, explicit truncate-to-zero then write, read rejection, random write rejection, sequential writes updating `getFileStatus().getFileLength()`, truncation to zero/default/future lengths, middle-truncate rejection, and multiple truncations before close.

State, dependencies, integration, risks, tests: state includes an in-progress stream file-length model that may exceed bytes written before close. Dependencies include create-directory options, `BufferUtils`, and runtime exceptions. Test signals document Alluxio's append limitations and sparse-like length extension semantics. Risk: it mostly checks final length/content patterns with increasing bytes, not sparse gap byte values in all cases.
