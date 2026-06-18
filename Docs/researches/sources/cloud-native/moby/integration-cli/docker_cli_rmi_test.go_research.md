# sources/cloud-native/moby/integration-cli/docker_cli_rmi_test.go

## Purpose

`docker_cli_rmi_test.go` defines `DockerCLIRmiSuite`, the integration test suite for `docker rmi` behavior. It validates the user-visible contract for image untagging and deletion when images are referenced by containers, tags, repositories, parent/child image relationships, and image IDs. The file is not testing a narrow Go API; it drives the Docker CLI against a real test daemon and checks CLI output, exit status, daemon image metadata, and object survival.

The suite is especially focused on conflict semantics: when deletion is blocked, when `-f` can remove tags or images, and when `-f` must still refuse because a running container uses the image. It also covers edge cases around blank names, short IDs, parent images, and history-layer tags.

## Important APIs, Types, and Helpers

The primary type is `DockerCLIRmiSuite`, which holds a shared `*DockerSuite` and forwards `TearDownTest` and `OnTimeout` to the suite-level cleanup and diagnostics. Test methods use the integration helpers from `github.com/moby/moby/v2/integration-cli/cli`, especially `cli.DockerCmd`, `cli.Docker`, `cli.Args`, and `cli.BuildCmd`.

Important shared helpers from the integration package include `dockerCmdWithError` for expected failures, `inspectField` and `getIDByName` for daemon object inspection, `runSleepingContainerInImage` for live image references, and `build.WithDockerfile`/`build.WithoutCache` for constructing isolated images. Assertions are done with `gotest.tools/v3/assert`, `assert/cmp`, and `icmd.Expected`. The suite also uses `stringid.TruncateID` to match daemon conflict messages that include shortened image/container IDs.

## Control Flow and Coverage

The tests follow a consistent integration pattern: create or tag images, create running or stopped containers that reference them, run `docker rmi` with or without `-f`, then inspect CLI output and image/container state. `TestRmiWithContainerFails` confirms a plain `rmi busybox` fails while a container references the image and does not remove the `busybox` repository entry. `TestRmiTag`, `TestRmiImgIDMultipleTag`, and `TestRmiImgIDForce` build up multiple references to the same image ID and check the difference between removing a tag, deleting by ID with multiple tags, and forced deletion.

Conflict paths are covered in detail. `TestRmiImageIDForceWithRunningContainersAndMultipleTags` ensures that even forced deletion by image ID refuses when a running container uses the image. `TestRmiTagWithExistingContainers`, `TestRmiForceWithExistingContainers`, `TestRmiWithMultipleRepositories`, and `TestRmiForceWithMultipleRepositories` distinguish safe untag operations from true image deletion. `TestRmiContainerImageNotFound` verifies that a force-removed image for a stopped container does not confuse the error path for a running-container image.

Several regression-style cases protect parsing and graph relationships. `TestRmiBlank` expects a blank image name validation error instead of a generic missing-ID message. `TestRmiUntagHistoryLayer` and `TestRmiParentImageFail` are currently skipped or marked broken around BuildKit/containerd image-store behavior, documenting fragile historical assumptions. `TestRmiWithParentInUse` exercises commits layered on commits and removes the newest image. `TestRmiByIDHardConflict` ensures deletion by short image ID fails when a container exists and does not silently untag `busybox:latest`.

## State and Persistence Behavior

The file mutates daemon image state heavily: it creates containers, commits them into images, adds multiple tags and repository aliases, and removes images by tag and ID. Assertions rely on persistent daemon state observable through `docker images`, `docker inspect`, and subsequent `rmi` operations. Running containers are deliberately used as hard references that prevent image deletion; stopped containers and tags are used to verify weaker references and force-removal behavior.

Image graph semantics matter. The skipped parent/history tests show that parent/child metadata and historical layer addressing have changed across builders and image stores. Tests that use `testEnv.UsingSnapshotter()` skip legacy parent expectations because containerd-backed image storage treats images differently from the older graphdriver image store.

## Dependencies and Integration Points

This suite integrates the CLI, daemon image service, builder, container lifecycle, and image-reference parser. It assumes a seeded `busybox` image and, in some tests, platform-specific behavior such as Windows commit timing. The suite also depends on exact or partial daemon error strings, including conflict text, repository-reference wording, and running-container messages.

Build integration is required for custom image/tag graphs. Container integration is required because image deletion rules depend on active and stopped container references. Inspection integration is required to compare image IDs, parent fields, and tag survival.

## Risks and Maintenance Notes

The biggest maintenance risk is tight coupling to CLI and daemon error strings. Several assertions use exact conflict text or fixed substrings, so legitimate wording changes can break tests even when behavior is preserved. The second risk is image-store drift: BuildKit and containerd image store changes already caused skipped tests, and future parent/history semantics can invalidate old graph assumptions.

Tests that count lines in `docker images -a` are sensitive to output formatting and pre-existing images. The suite relies on shared test cleanup to isolate state. Running-container tests can be timing-sensitive, especially on Windows where commits wait for containers to exit.

## Test Signals

Passing tests signal that `docker rmi` preserves tags and images when references require it, force deletion removes allowable references, running-container conflicts remain hard conflicts, and invalid image names or ambiguous IDs produce safe errors. Skipped tests signal known gaps around history-layer untagging and parent image conflicts under newer builder/image-store behavior.
