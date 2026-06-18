# subset-b-000198 research

Grouped research report for the requested Moby classic builder, digest-reference, commit, and container-copy integration tests. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_build_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_build_test.go

Purpose: defines the bulk of the classic `docker build` integration coverage for Moby's legacy builder. The suite forces `DOCKER_BUILDKIT=0` in `DockerCLIBuildSuite.SetUpTest`, then exercises Dockerfile parsing, build context transfer, ADD/COPY behavior, cache behavior, image config mutation, build args, labels, remote contexts, authenticated registry pulls, multi-stage builds, Windows path semantics, and emitted image events.

Important APIs and helpers: `DockerCLIBuildSuite` delegates teardown and timeout handling to `DockerSuite`; most tests invoke `cli.BuildCmd`, `cli.Docker`, `cli.DockerCmd`, `build.WithDockerfile`, `build.WithBuildContext`, `build.WithExternalBuildContext`, `cli.WithFlags`, and inspect helpers such as `inspectField`, `inspectFieldJSON`, `inspectFieldAndUnmarshall`, `getIDByName`, and `cli.InspectCmd`. Source fixtures are built through `fakecontext`, `fakegit`, and `fakestorage`; tar and compression fixtures use `archive/tar`, `github.com/moby/go-archive`, and `compression`. Helper functions in this file include `compareDirectoryEntries`, `testContextTar`, and `testBuildDockerfileStdinNoExtraFiles`.

Control flow: each test builds one or more throwaway images, then validates either the resulting image config, runtime output, build output, event stream, local filesystem side effects, or image IDs. Early tests cover environment replacement in `USER`, `VOLUME`, `EXPOSE`, `WORKDIR`, `ADD`, `COPY`, and `ENV`; JSON versus shell forms for `CMD`, `ENTRYPOINT`, `RUN`, and `SHELL`; ONBUILD trigger execution and inheritance; and basic cache invalidation. The middle of the file stresses local and remote ADD/COPY, wildcard expansion, symlink handling, `.dockerignore` patterns and exceptions, stdin Dockerfiles, tar build contexts, git and remote tarball contexts, malformed Dockerfiles, quiet output, resource cleanup, build container removal, and cgroup/network/extra-host options. The later tests focus on build args and ARG scoping, proxy-history exclusions, image labels and label override order, external credential helper use, cache-from/load behavior, multi-stage stage names, `COPY --from` syntax and errors, target builds, Windows-specific path/case restrictions, parse line numbers, `--iidfile`, and image create/tag event emission for both classic builder and BuildKit modes where explicitly requested.

State and persistence behavior: the file validates persistent image metadata such as `Config.User`, `Config.Env`, `Config.Volumes`, `Config.ExposedPorts`, `Config.WorkingDir`, `Config.Cmd`, `Config.Entrypoint`, `Config.Labels`, `Config.StopSignal`, `Config.Shell`, and `Config.ArgsEscaped`. It also checks build cache state by comparing image IDs, counting `Using cache`, and mutating context files, symlink targets, mtimes, labels, Dockerfiles, and build args. Several tests verify daemon-side temporary build context cleanup, absence or presence of intermediate build containers depending on `--rm` and `--force-rm`, named image tags, registry-pushed images, and event records visible through `docker events`. `--iidfile` tests assert the file contains the final stage image digest on success and is removed on build failure.

Dependencies and integration points: integrates the CLI binary, daemon, classic builder, optional BuildKit mode in event tests, registry suites, fake HTTP storage, fake git repositories, local daemon storage, platform defaults, snapshotter detection, cgroup parsing, credential helper fixtures, and Docker API version compatibility. Platform gates through `testRequires`, `skip.If`, `DaemonIsLinux`, `DaemonIsWindows`, `UnixCli`, `Network`, `NotUserNamespace`, `testEnv.IsLocalDaemon`, `testEnv.UsingSnapshotter`, and API-version checks are central to keeping the broad suite viable across Linux, Windows, graphdriver, and containerd-snapshotter backends.

Risks: the file is broad and intentionally end-to-end, so failures can originate from CLI formatting, daemon state, image distribution, registry behavior, local filesystem permissions, OS shell differences, base image changes, cache key changes, or environment timing. A number of tests are skipped because classic builder deprecation messages or ambiguous stdin behavior changed output. Tests that compare exact inspect strings, image IDs, event counts, line-number text, or build output are sensitive to formatting and API-version changes. Time-based mtime tests use sleeps; local-daemon cleanup and permission tests require specific host capabilities; many Linux-only tests depend on busybox tools, `su`, `xz`, `gzip`, cgroups, and user namespace behavior.

Test signals: high-value regression signal for the legacy builder contract, especially Dockerfile parser compatibility, cache correctness, context filtering, symlink breakout prevention, ADD/COPY extraction behavior, ARG scoping, multi-stage copy semantics, labels, events, and Windows path handling. It is less suitable as a narrow unit signal because it depends on complete daemon/CLI integration and a large amount of environment setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_build_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_build_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_build_unix_test.go

Purpose: adds Unix-only classic builder integration tests for resource constraint propagation, ADD ownership normalization, and cancellation cleanup when a build client disconnects.

Important APIs and helpers: tests are methods on `DockerCLIBuildSuite` and use `cli.Docker`, `cli.DockerCmd`, `cli.BuildCmd`, `fakecontext.New`, `inspectFieldJSON`, `newEventObserver`, `matchEventLine`, `processEventMatch`, and `isKilled`. The resource test unmarshals selected `HostConfig` fields into a local struct containing memory, swap, cpuset, CPU shares/quota, and `container.Ulimit` values. `isKilled` inspects `exec.ExitError` and `syscall.WaitStatus`.

Control flow: `TestBuildResourceConstraintsAreUsed` builds with `--rm=false` and explicit memory, swap, cpuset, CPU, ulimit, and label flags, locates the most recent build container by label, inspects its `HostConfig`, and then runs the resulting image to confirm those constraints did not persist into normal containers. `TestBuildAddChangeOwnership` creates a context file owned by `daemon:daemon`, builds a Dockerfile that ADDs it, and verifies both the destination directory and file are root-owned inside the image. `TestBuildCancellationKillsSleep` starts `docker build` against a Dockerfile with a one-year sleep, parses the build container ID from output, observes daemon events, kills the client process, and expects a container `die` event.

State and persistence behavior: the resource test deliberately leaves the build container around with `--rm=false` so its host config can be inspected, then verifies resource settings are build-container state rather than image state. The ownership test checks filesystem metadata in the committed build layer. The cancellation test validates runtime process/container cleanup after client socket loss and does not persist an image as the primary assertion.

Dependencies and integration points: guarded by `//go:build !windows`. It depends on Linux daemon features, CFS quota support, Unix `chown`, OS process control, daemon events, build output format that includes `Running in <id>`, and `TODOBuildkit` because BuildKit event/output behavior differs.

Risks: resource assertions are host-capability sensitive and can fail on systems without cpuset or quota support. Cancellation is race-prone because it coordinates CLI process output, daemon events, and container lifecycle timing. The build-container ID extraction depends on classic builder text output, making it unsuitable for BuildKit without redesign.

Test signals: focused Unix coverage for build-time host config isolation, ADD ownership semantics, and cancellation cleanup. These tests complement the larger cross-platform build suite by exercising host-level behavior that cannot be expressed in portable Dockerfile assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_build_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_by_digest_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_by_digest_test.go

Purpose: validates Docker image references by digest across pull, create, run, build, tag, list, inspect, ps filtering, deletion, and registry integrity checks. It also verifies that altered manifest or layer content is rejected through digest verification.

Important APIs and helpers: constants `remoteRepoName` and `repoName` point at the private registry namespace. `pushDigestRegex` and `digestRegex` parse CLI output. `setupImage` and `setupImageWithTag` create a busybox-based container, commit it with an extra file-bearing layer, push it to the private registry, remove the local tag, and return the pushed manifest digest. Tests use `cli.DockerCmd`, `dockerCmdWithError`, `deleteImages`, `inspectField`, `inspectFilter`, `getIDByName`, `checkPsAncestorFilterOutput`, registry helpers `ReadBlobContents`, `TempMoveBlobData`, and `WriteBlobContents`, plus OCI `ocispec.Manifest` JSON parsing.

Control flow: pull tests compare the digest reported by `docker pull` with the digest parsed from push output and confirm non-existent digest pulls do not fall back to tags. Create/run/build/tag tests use `<repo>@<digest>` references as normal image inputs and inspect resulting container or image state. Image listing tests compare `docker images` and `docker images --digests` output for digest-only, tag-plus-digest, multi-tag, and dangling-filter cases. Delete tests cover removal by digest reference, by image ID, with one or more tags in the same repo, and with tags in another repo. Integrity tests mutate registry blobs behind a stable digest and expect pull failures for manifest or layer verification.

State and persistence behavior: setup mutates the local daemon image store, private registry blobs, and local containers. Pull-by-digest stores repo digest references; tagging adds repo tags to the same image ID; deletion tests assert whether tags, digest references, and image records remain inspectable. The altered-layer test removes the daemon distribution cache to force blob re-fetch before verifying failure.

Dependencies and integration points: depends on the private registry fixture, Docker distribution behavior, content-addressed manifest/layer verification, image inspect JSON (`image.InspectResponse`), OCI manifest layout, daemon storage driver paths, and snapshotter mode differences. Linux gates are used where busybox and registry-layer behavior are assumed, and snapshotter-specific branches adjust expected error text or skip altered-layer verification when content-store reuse would bypass the fake blob.

Risks: CLI output regexes can break with formatting changes. Registry mutation tests are invasive and require careful deferred restoration of moved blob files. Digest listing output is table-format dependent. The altered-layer test reaches into `DockerRootDir/image/<driver>/distribution`, so storage-driver or snapshotter layout changes can invalidate it.

Test signals: strong end-to-end signal for content-addressable image identity, repo digest persistence, digest-aware image lifecycle operations, digest-aware ancestor filtering, and distribution security checks. It is especially valuable for regressions where tag references accidentally substitute for digest references or verification failures are hidden by cache.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_by_digest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_commit_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_commit_test.go

Purpose: tests `docker commit` behavior for completed, running, paused, TTY, bind-mounted, and modified containers, including config changes passed through `--change` and label override behavior.

Important APIs and helpers: `DockerCLICommitSuite` delegates teardown and timeout handling to `DockerSuite`. Tests use `cli.DockerCmd`, `inspectField`, `getPrefixAndSlashFromDaemonPlatform`, `testRequires`, `skip.If`, and assertions from `gotest.tools`. The main public surface under test is `docker commit`, including `-p=false` and repeated `--change` flags.

Control flow: basic tests run or create containers, commit them, trim the returned image ID, and inspect or run the committed image. `TestCommitPausedContainer` pauses a running container before commit and verifies the source container remains paused afterward. Filesystem tests create new files, hardlinks, TTY-created state, or host bind mounts before commit, then run the committed image to ensure the resulting image is valid and expected container-layer state persists. `TestCommitChange` applies Dockerfile-like changes for exposed ports, env, labels, cmd, workdir, entrypoint, user, volume, and ONBUILD metadata, then inspects each config field. `TestCommitChangeLabels` confirms image labels can be changed without mutating the source container labels.

State and persistence behavior: committing snapshots a container writable layer into a new image and may optionally pause the container during capture. Tests validate persisted image filesystem state (`/foo`, hardlink inode relationships), persisted image config, and non-persistence of host bind mount special state beyond image validity. Source container state is also observed for paused status and unchanged labels.

Dependencies and integration points: integrates the container runtime, image store, graphdriver/snapshotter commit path, inspect formatting, busybox shell utilities, Linux hardlink/pause/bind mount behavior, and Windows/containerd skip conditions. Platform path normalization is handled through `getPrefixAndSlashFromDaemonPlatform`.

Risks: hardlink assertions parse `ls -di` output and are Linux-specific. Config string comparisons are sensitive to inspect formatting and env ordering, with explicit Windows differences. Commit behavior depends on snapshotter correctness and pause semantics; source container cleanup is delegated to suite teardown.

Test signals: compact but high-signal coverage that commit captures writable-layer changes, preserves filesystem metadata such as hardlinks, leaves paused containers paused, applies supported config changes, and keeps source container metadata isolated from committed image metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_commit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_from_container_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_cp_from_container_test.go

Purpose: validates `docker cp` behavior when copying from a container to the local filesystem, mirroring the archive package's source/destination matrix for files, directories, directory contents, existing destinations, trailing separators, and symlink destinations.

Important APIs and helpers: tests are methods on `DockerCLICpSuite` and use shared copy-test helpers: `makeTestContainer`, `testContainerOptions`, `getTestDir`, `makeTestContentInDir`, `containerCpPath`, `containerCpPathTrailingSep`, `cpPath`, `cpPathTrailingSep`, `runDockerCp`, `fileContentEquals`, `symlinkTargetEquals`, `isCpDirNotExist`, and `isCpCannotCopyDir`. Assertions use `gotest.tools/assert`.

Control flow: `TestCpFromSymlinkDestination` first creates a populated container and local fixture tree, then copies a container file or directory to local symlinks that target existing files, existing directories, missing files, and missing directories, verifying symlink identity is preserved while targets receive copied content. Cases A through J implement the documented matrix: file-to-new-file, file-to-missing-trailing-dir error, file overwrite, file into directory, directory to new directory, directory-over-file error, directory into directory, directory-contents to new directory, directory-contents-over-file error, and directory-contents into directory. Cases with relevant ambiguity repeat the operation with and without destination trailing separators.

State and persistence behavior: container state is read-only during these tests; local temporary directories are the observed mutable state. Successful copies create or overwrite local files and directories, while error cases assert no successful copy semantics. Symlink tests specifically require that local symlink entries remain symlinks to the same target rather than being replaced.

Dependencies and integration points: Linux-only via `testRequires(c, DaemonIsLinux)`. The suite integrates CLI `docker cp`, container archive export APIs, local archive extraction semantics, symlink handling, and platform path helper behavior from other cp test files.

Risks: symlink behavior and trailing path separator semantics are platform-sensitive, hence Linux gating. Error type helpers abstract over exact messages, but tests still depend on `runDockerCp` preserving distinguishable error categories. Local filesystem cleanup depends on temp directory removal, and path construction helpers must preserve trailing separators accurately.

Test signals: strong behavioral signal for the container-to-host copy contract, especially edge cases where archive extraction could overwrite symlinks, conflate directory and directory-content copies, or accept invalid file-to-directory operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_from_container_test.go -->
