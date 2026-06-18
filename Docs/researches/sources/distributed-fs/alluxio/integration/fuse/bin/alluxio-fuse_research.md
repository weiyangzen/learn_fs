# sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse

Purpose: operational shell entrypoint for mounting, unmounting, and listing Alluxio FUSE mounts.

Important APIs and helpers: `get_env` sources Alluxio config and builds the shaded FUSE jar classpath. `check_fuse_jar` validates packaging. `mount_fuse` resolves mount point/alluxio path defaults, optionally starts StackFS, foreground mode, or background AlluxioFuse. `kill_process_and_umount_fuse`, `umount_fuse`, `fuse_stat`, and `fuse_mounted` manage process and mount state.

Control flow and state: `main` parses `mount`, `umount|unmount`, and `stat`. Mount first tries to kill/unmount existing mount state, builds Java command strings from global shell variables/options, then either `exec`s foreground or `nohup`s background and checks the PID after a sleep. Unmount finds a PID from `fuse_stat`, optionally sends SIGKILL, otherwise waits for graceful exit and mount disappearance.

Dependencies and integration: depends on `alluxio-config.sh`, `${BIN}/alluxio getConf`, Java, shaded `alluxio-integration-fuse` jar, `umount`, `fusermount`, `mount`, `ps`, `grep`, `awk`, and AlluxioFuse/StackMain classes.

Risks and test signals: argument handling and command construction are shell-string based, so paths/options with spaces are risky. There is a bug-like check `[[ check_fuse_jar == 1 ]]` that compares literal text instead of calling the function. Process parsing assumes command layout and may match multiple PIDs.
