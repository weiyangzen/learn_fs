# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseOpenUtils.java

Purpose: small flag decoder for FUSE `open`/`create` access modes. It maps masked `O_ACCMODE` bits to `OpenAction.READ_ONLY`, `WRITE_ONLY`, `READ_WRITE`, or fallback `NOT_SUPPORTED`, and exposes helpers for `O_TRUNC` and `O_CREAT`.

Important APIs and flow: `getOpenAction(int)` masks the input flag with `O_ACCMODE` and switches on JNR `OpenFlags`; `containsTruncate` and `containsCreate` perform bit tests. The semantics are tuned for Alluxio's write-once model: completed files are read-only, write opens create or truncate, and read-write is deferred to existing-file/no-truncate versus write-mode cases in stream code.

State, dependencies, risks, and tests: no persistent state. It depends only on `jnr.constants.platform.OpenFlags`, even for JNI callers. Risks are platform flag interpretation and missing coverage for `O_CREAT`/`O_TRUNC` helpers. `AlluxioFuseOpenUtilsTest` validates representative Linux-style flags with high-order bits preserved.
