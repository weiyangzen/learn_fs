# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseConstants.java

Purpose: central list of FUSE operation metric names. JNI code uses these names for call wrapping, metrics timers, and update-check operation signals.

Important APIs and flow: constants cover getattr, readdir, read, write, mkdir, unlink, rmdir, rename, chmod, chown, and truncate. `getFuseMethodNames` returns a new list in a fixed order for `UpdateChecker`.

State, dependencies, risks, and tests: no mutable state. It depends on standard collections only. Risks are missing newer operations such as statfs, flush, release, symlink, and utimens from update-check telemetry. No direct assigned tests; usage is indirect in `UpdateChecker` and JNI callbacks.
