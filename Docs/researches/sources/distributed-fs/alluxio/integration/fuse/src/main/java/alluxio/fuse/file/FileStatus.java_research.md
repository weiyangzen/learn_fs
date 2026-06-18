# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FileStatus.java

Purpose: simple mutable length holder for open FUSE streams.

Important APIs and flow: constructor sets initial length, `getFileLength` returns it, and `setFileLength` updates it. It is used by read streams for EOF checks, write streams for visible in-progress length, and mixed streams before a concrete mode is chosen.

State, dependencies, risks, and tests: state is a plain `long` with no synchronization or volatile marker; callers synchronize at stream level where needed. No dependencies. Risks are visibility if accessed outside stream synchronization, but current JNI `getattr` reads through synchronized stream methods for write streams. Tested indirectly by read EOF and write/getattr behavior.
