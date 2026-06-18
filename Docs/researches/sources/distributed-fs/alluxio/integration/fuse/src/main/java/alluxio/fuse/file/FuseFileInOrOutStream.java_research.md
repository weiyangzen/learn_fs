# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInOrOutStream.java

Purpose: lazy stream for `O_RDWR`-style opens where Alluxio cannot actually support simultaneous read/write. It chooses read-only or write-only behavior based on flags and first operation.

Important APIs and flow: `create` immediately creates a write stream when `O_TRUNC` or `O_CREAT` is present; otherwise it defers. `read` fails if write mode was chosen, lazily creates `FuseFileInStream`, and delegates. `write` and `truncate` fail if read mode was chosen, lazily create `FuseFileOutStream`, and delegate. `getFileStatus`, `flush`, and `close` delegate to the active stream or return current path length when no stream has been chosen.

State, dependencies, risks, and tests: state is synchronized optional in/out stream references plus URI/mode and dependencies. It integrates with `FileSystem`, `AuthPolicy`, `FuseReadWriteLockManager`, and open flag helpers. Risks include surprising first-operation semantics for applications expecting true read-write handles, unsupported read-after-write/write-after-read, and delayed file creation for existing-file write without truncate. Tested indirectly by JNI create/open/write/read/truncate behavior.
