<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStream.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStream.java

Purpose: Alluxio UFS output stream that provides atomic file creation by writing to a temporary path and renaming to the permanent path on close. It also implements `ContentHashable` for post-write fingerprinting.

Important APIs and control flow: the constructor derives a random temporary file name near the target path and calls `AtomicFileOutputStreamCallback.createDirect`. `write` methods delegate to the temporary stream. `close` is idempotent, closes the temporary stream, renames temp to permanent, deletes temp and throws if rename fails, then optionally preserves owner/group from `CreateOptions`. `getContentHash` reads the permanent file status and returns its content hash.

State, persistence, and integration: persists bytes first at a temporary UFS path and then at the final path after rename. Dependencies include callback methods from the concrete UFS, `PathUtils.temporaryFileName`, `IdUtils`, `CreateOptions`, and UFS status metadata. Risks include temp-file leakage if close is never called, atomicity depending on UFS rename semantics, and content hash lookup only after close/permanent path availability. Test signals should cover rename failure cleanup, owner/group preservation, idempotent close, and content hash retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/AtomicFileOutputStream.java -->
