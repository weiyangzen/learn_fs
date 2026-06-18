# sources/cloud-native/moby/integration-cli/docker_cli_commit_test.go

Purpose: tests `docker commit` behavior for completed, running, paused, TTY, bind-mounted, and modified containers, including config changes passed through `--change` and label override behavior.

Important APIs and helpers: `DockerCLICommitSuite` delegates teardown and timeout handling to `DockerSuite`. Tests use `cli.DockerCmd`, `inspectField`, `getPrefixAndSlashFromDaemonPlatform`, `testRequires`, `skip.If`, and assertions from `gotest.tools`. The main public surface under test is `docker commit`, including `-p=false` and repeated `--change` flags.

Control flow: basic tests run or create containers, commit them, trim the returned image ID, and inspect or run the committed image. `TestCommitPausedContainer` pauses a running container before commit and verifies the source container remains paused afterward. Filesystem tests create new files, hardlinks, TTY-created state, or host bind mounts before commit, then run the committed image to ensure the resulting image is valid and expected container-layer state persists. `TestCommitChange` applies Dockerfile-like changes for exposed ports, env, labels, cmd, workdir, entrypoint, user, volume, and ONBUILD metadata, then inspects each config field. `TestCommitChangeLabels` confirms image labels can be changed without mutating the source container labels.

State and persistence behavior: committing snapshots a container writable layer into a new image and may optionally pause the container during capture. Tests validate persisted image filesystem state (`/foo`, hardlink inode relationships), persisted image config, and non-persistence of host bind mount special state beyond image validity. Source container state is also observed for paused status and unchanged labels.

Dependencies and integration points: integrates the container runtime, image store, graphdriver/snapshotter commit path, inspect formatting, busybox shell utilities, Linux hardlink/pause/bind mount behavior, and Windows/containerd skip conditions. Platform path normalization is handled through `getPrefixAndSlashFromDaemonPlatform`.

Risks: hardlink assertions parse `ls -di` output and are Linux-specific. Config string comparisons are sensitive to inspect formatting and env ordering, with explicit Windows differences. Commit behavior depends on snapshotter correctness and pause semantics; source container cleanup is delegated to suite teardown.

Test signals: compact but high-signal coverage that commit captures writable-layer changes, preserves filesystem metadata such as hardlinks, leaves paused containers paused, applies supported config changes, and keeps source container metadata isolated from committed image metadata.
