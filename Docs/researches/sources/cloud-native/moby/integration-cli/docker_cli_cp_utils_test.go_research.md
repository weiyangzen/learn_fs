# sources/cloud-native/moby/integration-cli/docker_cli_cp_utils_test.go

Purpose: shared fixtures and assertions for the `docker cp` integration suite. It models file trees with regular files, directories, symlinks, ownership, and permissions, and provides path builders that keep host and container path syntax distinct.

Important APIs/types/functions: `fileType`, `fileData`, `fileData.creationCommand`, `mkFilesCommand`, `defaultFileData`, `defaultMkContentCommand`, `makeTestContentInDir`, `testContainerOptions`, `makeTestContainer`, `makeCatFileCommand`, `cpPath`, `cpPathTrailingSep`, `containerCpPath`, `containerCpPathTrailingSep`, `runDockerCp`, `getTestDir`, `isCpDirNotExist`, `isCpCannotCopyDir`, `fileContentEquals`, `symlinkTargetEquals`, `containerStartOutputEquals`, and `defaultVolumes`.

Control flow: fixture generation can happen inside a container as a shell command or on the host through Go filesystem calls. `makeTestContainer` constructs `docker run --cidfile` arguments, applies volume/workdir/read-only options, seeds content when requested, and returns the created container ID. Assertion helpers read files, read symlink targets, or start a container and compare output.

State and persistence: creates temp directories, files, symlinks, ownership/mode metadata, Docker containers, and optional volumes. `defaultVolumes` creates different mount declarations for local and remote daemons because host bind mounts are not available remotely.

Dependencies and integration points: depends on `github.com/moby/go-archive` for expected copy errors, integration `cli`, `icmd`, platform checks, and busybox shell utilities. It is the common contract between copy matrix tests and lower-level archive package semantics.

Risks: shell command generation quotes only fixture-controlled values; new arbitrary fixture data would need careful escaping. `makeTestContentInDir` assumes parent directories appear before children in `defaultFileData`. Ownership changes are skipped on Windows and can fail on restricted filesystems.

Test signals: because many cp tests use these helpers, a failure here would cascade. The helper design makes path separator, trailing slash, symlink, and metadata assumptions explicit for regression tests.
