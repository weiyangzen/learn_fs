# sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse-sdk

Purpose: SDK-oriented shell entrypoint for mounting arbitrary UFS addresses through Alluxio FUSE without requiring an Alluxio namespace path.

Important APIs and helpers: `mount_command` separates JVM options from class arguments; `launch_fuse_process` parses mount options and foreground mode; `wait_for_fuse_mounted` polls `mount`; `print_mount_status` lists running AlluxioFuse mounts; `unmount_command`, `umount_fuse`, and `wait_for_fuse_process_killed` manage shutdown; `check_fuse_jar` validates the shaded jar.

Control flow and state: `main` dispatches `mount`, `umount|unmount`, and help. Mount requires `ufs_address` and `mount_point`, aggregates repeated `-o` options, refuses already-mounted targets, builds a Java command invoking `alluxio.fuse.AlluxioFuse -m <mount> -u <ufs>`, and either execs foreground or starts background and waits up to about a minute for the mount to appear.

Dependencies and integration: depends on Alluxio libexec configuration, Java, shaded FUSE jar, AlluxioFuse class, OS `mount`, `umount`, `fusermount`, `ps`, `grep`, `awk`, and logs under `ALLUXIO_LOGS_DIR`.

Risks and test signals: shell parsing of process command lines and unquoted command execution can break for spaces/special characters. `umount_fuse` calls `fuse_mounted` without passing `mount_point` in its final check, which can mask state. It has no unit tests in this subset.
