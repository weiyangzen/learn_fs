# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/test_fuse_dfs.c

## Purpose
Native end-to-end test runner for `fuse_dfs` using a native MiniDFS cluster wrapper and real FUSE mount.

## Important APIs, Types, And Functions
Helpers include `verifyFuseWorkload`, `fuserMount`, `isMounted`, `waitForMount`, `cleanupFuse`, and `spawnFuseServer`. `main` orchestrates temp mount creation, cluster lifecycle, FUSE process lifecycle, workload execution, and cleanup.

## Control Flow
The test optionally uses `TLH_FUSE_MNT_POINT` or creates a temp dir, verifies the workload on local FS, starts a formatted MiniDFS cluster, forks/execs `fuse_dfs` with server/port/init options, waits for `/proc/mounts` to show the mount, runs workload, unmounts, waits for the FUSE process, shuts down cluster, and removes temp dir.

## State, Persistence, And Dependencies
Touches local mount table, temp directories, child processes, MiniDFS cluster JVM, and HDFS namespace. Depends on `fusermount`, `/proc/mounts`, `native_mini_dfs`, libhdfs, and POSIX process APIs.

## Integration Points
Connects C workload, native cluster wrapper, built `fuse_dfs` binary, and libhdfs/JNI runtime.

## Risks
Linux/FUSE specific. Cleanup is best effort but failed mount/unmount can leave processes or mountpoints. `fusermount` exec errors use a reserved status. Signal handling expects SIGTERM after unmount as acceptable.

## Test Signals
`FUSE_TEST: SUCCESS` indicates local workload, HDFS mount workload, unmount, process exit, and cluster shutdown all succeeded.
