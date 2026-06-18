# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseSignalHandler.java

Purpose: handles JVM `TERM` signal for mounted JNI FUSE processes so unmount runs before exit.

Important APIs and flow: `handle(Signal)` logs the signal, calls `FuseUmountable.umount(false)` only for signal number 15, logs and returns on unmount failure, and otherwise calls `System.exit(0)`.

State, dependencies, risks, and tests: state is the mounted `FuseUmountable` reference. It depends on `sun.misc.Signal`, a non-standard API. Risks include exact numeric signal check, no handling for INT/HUP, returning without exit if unmount fails, and reliance on process-global signal handlers. No direct assigned test covers it.
