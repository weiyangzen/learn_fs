# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/CreateFileStatus.java

Purpose: in-memory status for an actively created/written FUSE file. It extends `FileStatus` with mode, uid, and gid so `getattr` can expose a plausible stat before Alluxio marks the file complete.

Important APIs and flow: static `create(AuthPolicy, mode, fileLength)` resolves current uid/gid from the policy or uses `-1`, then constructs the status. Getters expose mode and ownership; inherited methods track length.

State, dependencies, risks, and tests: state is mutable length plus fixed mode/uid/gid. It depends on `AuthPolicy` and `AlluxioFuseUtils` constants. Risks include stale uid/gid for policies whose context changes after creation and mode `-1` if no mode was supplied. Tested indirectly by JNI `getattrWhenWriting` and stream create/write tests.
