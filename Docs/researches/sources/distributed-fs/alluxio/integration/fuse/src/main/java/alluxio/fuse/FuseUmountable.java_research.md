# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseUmountable.java

Purpose: minimal interface for objects that can unmount a FUSE filesystem. It lets launch/signal code treat JNI and JNR implementations uniformly.

Important APIs and flow: `umount(boolean force)` is the only method. Implementations differ: JNI waits for open stream closure and delegates to native unmount; JNR logs and delegates to `super.umount()`.

State, dependencies, risks, and tests: no state or dependencies. The comment for `force` is confusing because JNI throws on timeout when `force` is false and suppresses timeout when true. Tested indirectly by launch/signal paths only.
