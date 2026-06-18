# sources/cloud-native/nydus/smoke/tests/commit_test.go

## Purpose
This suite validates committing a writable container based on a Nydus image and running the committed image through the Nydus snapshotter. It ensures files copied into the container's writable layer are preserved after `nydusify commit`.

## Important APIs, Types, And Functions
`CommitTestSuite` stores a root `*testing.T` because its dynamic generator prepares images before returning subtests. `TestCommitContainer` iterates `ubuntu:latest` over RAFS fs versions 5 and 6. `prepareImage` prepares a local registry source, converts it with `nydusify convert`, and returns the Nydus target plus committed target name. `TestCommitAndCheck` runs the image via `nerdctl --snapshotter nydus`, copies a generated `commit` file into `/root`, invokes `nydusify commit`, runs the committed image, and checks the file content with `nerdctl exec`. Helpers `checkFileContent` and `nerdctlExec` wrap command execution.

## Control Flow
The test first converts the base image, starts a long-lived shell container, mutates it by copying a file, commits the container to a new image, starts a second container from the committed image, and verifies the committed layer content.

## State And Persistence
State is external to the Go process: registry images, containerd/nerdctl containers, and temporary workdir files. The workdir is destroyed after the mutation step, while containers and images are removed through `tool.ClearContainer` defers.

## Dependencies And Integration Points
The test integrates with Docker/registry preparation, `nydusify convert`, `nydusify commit`, `nerdctl`, containerd, and the Nydus snapshotter. It also depends on `uuid` for isolated container names and `tool.PrepareImage` for registry naming.

## Risks
Commands are string-built and executed through shell wrappers, so image names and paths must remain shell-safe. The generator performs image conversion before the returned subtest executes, which can make failures appear during test enumeration rather than in a named subtest. The misspelled `commitedImage` parameter is cosmetic.

## Test Signals
The strongest signal is `stat` plus exact-content `grep` of `/root/commit` inside the committed container. Setup failures expose conversion, registry, snapshotter, or commit CLI regressions.
