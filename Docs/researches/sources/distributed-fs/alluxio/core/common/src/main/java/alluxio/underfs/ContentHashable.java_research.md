<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ContentHashable.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ContentHashable.java

Purpose: marker/extension interface for output streams that can return a content hash after writing to the UFS. Alluxio uses this hash in metadata fingerprints when completing files.

Important APIs and control flow: declares `Optional<String> getContentHash() throws IOException`. Implementations such as atomic or object output streams decide when the hash is available and whether it can be absent.

State, persistence, and integration: interface only; state lives in implementing streams and UFS metadata. Dependencies include `Optional` and the `UnderFileSystem#create` contract described in comments. Risks include callers asking before close, backend hashes that are not stable across multipart/single uploads, and `Optional.empty` handling. Test signals include file completion paths incorporating returned hashes into fingerprints when present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ContentHashable.java -->
