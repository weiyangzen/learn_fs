# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/StackMain.java

Purpose: standalone launcher for `StackFS`.

Important APIs and flow: `main` expects mount point and source path, loads libfuse based on configuration, strips `-o` prefixes from remaining options, sets process type, starts metric sinks, and mounts `StackFS` in blocking mode. On failure it prints the stack trace, forces unmount, and exits nonzero.

State, dependencies, risks, and tests: process state includes metrics sinks and FUSE mount. It depends on global Alluxio configuration and JNI FUSE library loading. Risks include simplistic option parsing (`substring(2)`), direct stdout/stderr usage, and no validation that source path exists. No assigned direct tests cover it.
