# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteHandler.java

## Purpose
`UfsFileWriteHandler` handles full-file writes directly to an under file system. It exists because UFS file semantics require all file bytes to be written through one stream rather than independent block-level writers.

## Important APIs, Types, and Functions
`createRequestContext()` creates `UfsFileWriteRequestContext`. `writeBuf()` lazily creates the UFS file and writes bytes from `DataBuffer`. `flushRequest()` flushes the open stream. `completeRequest()` creates an empty file if needed, closes the stream, captures optional content hash, sets owner/group, and closes the UFS resource. `cancelRequest()` closes the stream and deletes the UFS file. `createUfsFile()` builds `CreateOptions` from proto owner, group, mode, and optional ACL, then creates a non-existing file.

## Control Flow, State, and Persistence
The target UFS file is created lazily on first data, flush, or completion. Successful completion persists the UFS file and metadata updates; cancellation deletes it. Content hash is stored in request context when the output stream supports `ContentHashable`.

## Dependencies and Integration Points
It integrates `AbstractWriteHandler`, `UfsManager`, `UnderFileSystem`, `CreateOptions`, `Mode`, ACL proto conversion, UFS write metrics, `ContentHashable`, and `UnderFileSystemFileOutStream` clients.

## Risks and Test Signals
Risks include losing ownership update failures because they are warnings, deleting after close on cancel, unsupported ACL behavior outside HDFS, and ensuring empty-file completion still creates a file. Tests should cover write/flush/complete, empty file create, cancel deletion, ACL and mode propagation, content hash capture, and UFS resource closure on exceptions.
