# sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_unix_test.go

Purpose: Unix-only coverage for ownership and permission behavior when copying from host into containers, especially `docker cp -a` and user-namespace root mapping.

Important APIs/types/functions: `TestCpToContainerWithPermissions`, `TestCpCheckDestOwnership`, and `getRootUIDGID`. The tests use `syscall.Stat_t` to inspect host-side ownership on a bind mount and parse `testEnv.DaemonInfo.DockerRootDir` to infer remapped root UID/GID.

Control flow: the permission test creates fixture content with non-default ownership and modes, creates a named container that prints `stat -c '%u %g %a'`, copies a directory into `/` with `docker cp -a`, starts the container, and compares the reported ownership/mode values. The destination ownership test bind-mounts a temp directory, copies a file into it via the container path, stats the host file, and verifies ownership equals container root, accounting for userns remapping.

State and persistence: temporary host directories and bind mounts are mutated; container rootfs receives copied files. The tests assert persisted metadata, not just byte content.

Dependencies and integration points: Linux daemon, local daemon bind mounts, Unix ownership APIs, busybox `stat`, Docker root directory naming under user namespace remapping, and the CLI archive/extract path.

Risks: assumptions about Docker root directory naming are fragile if userns storage layout changes. Host filesystems that do not support chown or mode preservation can cause false failures. These tests are intentionally excluded on Windows.

Test signals: failures indicate regressions in metadata preservation for `docker cp -a`, incorrect root ownership during extraction into bind mounts, or broken userns remapping integration.
