# sources/cloud-native/moby/integration-cli/docker_cli_cp_from_container_test.go

Purpose: validates `docker cp` behavior when copying from a container to the local filesystem, mirroring the archive package's source/destination matrix for files, directories, directory contents, existing destinations, trailing separators, and symlink destinations.

Important APIs and helpers: tests are methods on `DockerCLICpSuite` and use shared copy-test helpers: `makeTestContainer`, `testContainerOptions`, `getTestDir`, `makeTestContentInDir`, `containerCpPath`, `containerCpPathTrailingSep`, `cpPath`, `cpPathTrailingSep`, `runDockerCp`, `fileContentEquals`, `symlinkTargetEquals`, `isCpDirNotExist`, and `isCpCannotCopyDir`. Assertions use `gotest.tools/assert`.

Control flow: `TestCpFromSymlinkDestination` first creates a populated container and local fixture tree, then copies a container file or directory to local symlinks that target existing files, existing directories, missing files, and missing directories, verifying symlink identity is preserved while targets receive copied content. Cases A through J implement the documented matrix: file-to-new-file, file-to-missing-trailing-dir error, file overwrite, file into directory, directory to new directory, directory-over-file error, directory into directory, directory-contents to new directory, directory-contents-over-file error, and directory-contents into directory. Cases with relevant ambiguity repeat the operation with and without destination trailing separators.

State and persistence behavior: container state is read-only during these tests; local temporary directories are the observed mutable state. Successful copies create or overwrite local files and directories, while error cases assert no successful copy semantics. Symlink tests specifically require that local symlink entries remain symlinks to the same target rather than being replaced.

Dependencies and integration points: Linux-only via `testRequires(c, DaemonIsLinux)`. The suite integrates CLI `docker cp`, container archive export APIs, local archive extraction semantics, symlink handling, and platform path helper behavior from other cp test files.

Risks: symlink behavior and trailing path separator semantics are platform-sensitive, hence Linux gating. Error type helpers abstract over exact messages, but tests still depend on `runDockerCp` preserving distinguishable error categories. Local filesystem cleanup depends on temp directory removal, and path construction helpers must preserve trailing separators accurately.

Test signals: strong behavioral signal for the container-to-host copy contract, especially edge cases where archive extraction could overwrite symlinks, conflate directory and directory-content copies, or accept invalid file-to-directory operations.
