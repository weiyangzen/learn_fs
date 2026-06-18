# sources/cloud-native/moby/integration-cli/docker_cli_cp_test.go

Purpose: integration coverage for `docker cp` container-to-host and general path handling. The suite protects historical security and behavior regressions around path traversal, rootfs-relative paths, symlink semantics, volumes, special container files, stdout tar output, and copying from created or stopped containers.

Important APIs/types/functions: `DockerCLICpSuite`, `TearDownTest`, `OnTimeout`, constants such as `cpTestPath`, `cpFullPath`, `cpContainerContents`, and `cpHostContents`, plus tests `TestCpGarbagePath`, `TestCpRelativePath`, `TestCpAbsolutePath`, `TestCpAbsoluteSymlink`, `TestCpFromSymlinkToDirectory`, `TestCpToSymlinkToDirectory`, `TestCpSymlinkComponent`, `TestCpVolumePath`, `TestCpToStdout`, and `TestCpSymlinkFromConToHostFollowSymlink`.

Control flow: most tests create a busybox container, seed files or symlinks, wait for setup completion, run `docker cp`, and compare host-side files or symlink targets. Traversal tests create matching host paths to ensure `../../..` and absolute paths cannot escape the container rootfs. Volume tests bind local paths, copy from named volumes, bind-mounted directories, and bind-mounted files, then compare host and copied bytes. The stdout test pipes `docker cp container:/path -` into `tar -vtf -`.

State and persistence: the tests mutate temporary host directories, container root filesystems, bind mounts, Docker-managed volumes, and container metadata. They intentionally verify that copying does not alter restartability, that created containers can still provide files, and that special files such as `/etc/resolv.conf`, `/etc/hosts`, and `/etc/hostname` are copied from the live container view.

Dependencies and integration points: uses the integration CLI helpers, `icmd`, `RunCommandPipelineWithOutput`, the local daemon guard, Unix-only capabilities where required, tar, `su`, bind mounts, and busybox shell commands. It exercises archive APIs indirectly through the CLI and daemon archive/extract endpoints.

Risks: path traversal and symlink resolution are security-sensitive. Tests depending on local bind mounts, `su`, Linux symlink behavior, or volume permissions are platform/userns constrained. The tests also assume busybox command availability and timing around exited containers.

Test signals: failures indicate regressions in cp path sanitization, symlink copy-vs-follow behavior, volume archive access, special-file materialization, tar stream output, container restart state after archive access, or `-L` symlink following.
