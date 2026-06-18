# sources/cloud-native/moby/integration-cli/docker_cli_build_unix_test.go

Purpose: adds Unix-only classic builder integration tests for resource constraint propagation, ADD ownership normalization, and cancellation cleanup when a build client disconnects.

Important APIs and helpers: tests are methods on `DockerCLIBuildSuite` and use `cli.Docker`, `cli.DockerCmd`, `cli.BuildCmd`, `fakecontext.New`, `inspectFieldJSON`, `newEventObserver`, `matchEventLine`, `processEventMatch`, and `isKilled`. The resource test unmarshals selected `HostConfig` fields into a local struct containing memory, swap, cpuset, CPU shares/quota, and `container.Ulimit` values. `isKilled` inspects `exec.ExitError` and `syscall.WaitStatus`.

Control flow: `TestBuildResourceConstraintsAreUsed` builds with `--rm=false` and explicit memory, swap, cpuset, CPU, ulimit, and label flags, locates the most recent build container by label, inspects its `HostConfig`, and then runs the resulting image to confirm those constraints did not persist into normal containers. `TestBuildAddChangeOwnership` creates a context file owned by `daemon:daemon`, builds a Dockerfile that ADDs it, and verifies both the destination directory and file are root-owned inside the image. `TestBuildCancellationKillsSleep` starts `docker build` against a Dockerfile with a one-year sleep, parses the build container ID from output, observes daemon events, kills the client process, and expects a container `die` event.

State and persistence behavior: the resource test deliberately leaves the build container around with `--rm=false` so its host config can be inspected, then verifies resource settings are build-container state rather than image state. The ownership test checks filesystem metadata in the committed build layer. The cancellation test validates runtime process/container cleanup after client socket loss and does not persist an image as the primary assertion.

Dependencies and integration points: guarded by `//go:build !windows`. It depends on Linux daemon features, CFS quota support, Unix `chown`, OS process control, daemon events, build output format that includes `Running in <id>`, and `TODOBuildkit` because BuildKit event/output behavior differs.

Risks: resource assertions are host-capability sensitive and can fail on systems without cpuset or quota support. Cancellation is race-prone because it coordinates CLI process output, daemon events, and container lifecycle timing. The build-container ID extraction depends on classic builder text output, making it unsuitable for BuildKit without redesign.

Test signals: focused Unix coverage for build-time host config isolation, ADD ownership semantics, and cancellation cleanup. These tests complement the larger cross-platform build suite by exercising host-level behavior that cannot be expressed in portable Dockerfile assertions.
