# sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_test.go

Purpose: integration coverage for host-to-container `docker cp` behavior, matching the copy matrix implemented by the archive package and adding container-specific checks for symlink destinations and read-only targets.

Important APIs/types/functions: methods on `DockerCLICpSuite`: `TestCpToSymlinkDestination`, matrix tests `TestCpToCaseA` through `TestCpToCaseJ`, `TestCpToErrReadOnlyRootfs`, and `TestCpToErrReadOnlyVolume`. These tests depend heavily on helpers from `docker_cli_cp_utils_test.go`: `makeTestContainer`, `makeTestContentInDir`, `cpPath`, `containerCpPath`, and error comparators.

Control flow: tests create host fixture trees, create containers with optional seeded content and workdirs, run `docker cp`, then use `docker start -a` or host bind-mount inspection to verify copied bytes. The A-J cases cover file-to-new-file, file-to-missing-directory error, overwrite, file into directory, directory creation, directory-to-file error, directory under existing directory, contents-only copy with `/.`, contents-only-to-file error, and contents-only into existing directory. Symlink destination checks verify that copying to symlinks writes through to targets without replacing the link.

State and persistence: host temp directories hold source fixtures, containers receive copied content in rootfs or bind-mounted volumes, and read-only tests assert that failed writes leave expected paths absent. Some checks use repeated container starts to confirm persisted filesystem content after copy.

Dependencies and integration points: integrates Docker CLI `cp`, `run`, `create`, and `start`, busybox shell/stat behavior, bind mounts via local daemon, and archive package error strings `ErrDirNotExists` and `ErrCannotCopyDir`.

Risks: host path trailing separator and `/.` intent are easy to regress. Symlink destination behavior is especially sensitive because replacing a symlink instead of its target would alter container state and could create security issues. Read-only rootfs and read-only volume errors depend on Linux mount semantics and user namespace constraints.

Test signals: failures isolate the copy matrix contract for host-to-container operations and show whether daemon extraction follows archive package semantics, preserves symlinks correctly, and rejects writes into immutable targets.
