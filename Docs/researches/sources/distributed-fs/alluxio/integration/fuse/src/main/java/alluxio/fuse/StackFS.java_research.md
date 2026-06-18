# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackFS.java

Purpose: JNI-FUSE local stack filesystem used as a performance/test harness. It maps paths under a mount point directly to a local root path without Alluxio client/server interaction.

Important APIs and flow: `transformPath` concatenates root and FUSE path. Callbacks implement local `getattr`, `readdir`, `open`, `read`, `create`, `write`, `mkdir`, recursive `rmdir`, synthetic `statfs`, `unlink`, no-op `utimens`, `rename`, `chmod`, `chown`, no-op `flush`/`release`, and fixed fs name. File metadata is read through NIO/POSIX APIs; read/write use local file streams.

State, dependencies, risks, and tests: state is only `mRoot`. It depends on local filesystem POSIX attributes, Alluxio metrics, JNI FUSE structs, and `FileUtils`. Risks include path concatenation without normalization, write opening `FileOutputStream` without append and ignoring offset, recursive `rmdir` behavior unlike POSIX empty-directory removal, a likely wrong `rename` existence error for existing destination, and synthetic statfs. No assigned direct tests cover StackFS.
