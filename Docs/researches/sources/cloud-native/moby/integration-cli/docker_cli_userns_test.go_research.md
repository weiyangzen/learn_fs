## sources/cloud-native/moby/integration-cli/docker_cli_userns_test.go

Purpose: tests daemon user namespace remapping with `--userns-remap=default` and vfs storage. It validates UID/GID maps, host file ownership for bind mounts, auto-created bind source directories, and per-container `--userns host` override.

Control flow starts the daemon with remapping, runs containers, derives the remapped UID/GID from the daemon root directory basename, chowns a temp directory, mounts existing and non-existing host paths, and inspects `/proc/<pid>/uid_map` and `gid_map` through a shell pipeline. `findUser` parses `docker top` output to identify the process user.

State includes daemon root path, host filesystem ownership, running container PID namespace mappings, and created bind directories/files. Dependencies include Linux user namespace kernel support, `RunCommandPipelineWithOutput`, `stringid`, and `syscall.Stat_t`. Risks include assumptions about daemon root naming, root privileges for chown, and `/proc` availability. Test signals are `stat` output `0:0` in-container, remapped user in `top`, matching uid/gid maps, and root user under `--userns host`.
