<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStreamCallback.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStreamCallback.java

Purpose: callback interface for UFS implementations that support `AtomicFileOutputStream`. It extends `UnderFileSystem` with a direct-create operation used for temporary writes.

Important APIs and control flow: declares `createDirect(String path, CreateOptions options)` returning an `OutputStream` that writes directly to storage without atomicity guarantees. `AtomicFileOutputStream` uses normal UFS operations from the inherited interface for rename, delete, owner update, and status lookup.

State, persistence, and integration: no state itself; implementers decide how direct temporary writes are persisted. Dependencies include the broader `UnderFileSystem` contract and `CreateOptions`. Risks include implementers accidentally routing `createDirect` back through atomic creation and recursion, or not matching option semantics. Test signals are concrete UFS tests that atomic streams create temp files directly and publish only on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStreamCallback.java -->
