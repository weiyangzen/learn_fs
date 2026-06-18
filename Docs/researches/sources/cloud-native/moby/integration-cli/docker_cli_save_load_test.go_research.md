# sources/cloud-native/moby/integration-cli/docker_cli_save_load_test.go

## Purpose

`docker_cli_save_load_test.go` defines `DockerCLISaveLoadSuite`, the cross-platform file for image archive save/load integration tests, although most tests require a Linux daemon. It validates `docker save` and `docker load` behavior for repositories, tags, image IDs, archive contents, compression failure paths, parent metadata, missing images, multiple names, and load output messages.

The suite treats image archives as an interoperability boundary: saved image data must preserve inspect metadata where expected, contain the right OCI or legacy archive members, and restore image identity after deletion and reload.

## Important APIs, Types, and Helpers

The main type is `DockerCLISaveLoadSuite`, with teardown and timeout delegated to `DockerSuite`. The suite uses `cli.DockerCmd`, `dockerCmdWithError`, `RunCommandPipelineWithOutput`, `deleteImages`, `inspectField`, `loadSpecialImage`, and `cli.BuildCmd`. It also uses `image.InspectResponse` from `github.com/moby/moby/api/types/image` to compare structured inspect output after save/load.

The tests rely on shell tools invoked with `exec.Command`, including `tar`, `grep`, `xz`, and `gzip`. `icmd.RunCmd` is used where stdin/stdout wiring and expected exit code assertions are central to the test.

## Control Flow and Coverage

The compression tests create an image by running and committing a container, pipe `docker save` through `xz` and/or `gzip`, delete the image, and confirm `docker load` fails when given unsupported nested/compressed data. The important assertion is negative: failed load must not leave the repository inspectable afterward.

`TestSaveSingleTag` tags `busybox`, saves one tag, lists the tar archive, and checks for manifest/index files and the expected image ID. It adjusts expectations when the containerd snapshotter/image store is active. `TestSaveImageId` loads a synthetic empty filesystem image, tags it, obtains long and short IDs, saves by short ID, and checks the archive for the long content-addressed blob path.

`TestSaveAndLoadRepoFlags` pipes `docker save` directly into `docker load`, then compares `docker inspect` JSON before and after. It normalizes `Metadata.LastTagTime` under the snapshotter because that timestamp lives outside the portable archive contract. `TestSaveWithNoExistImage` validates the missing-image error path for `docker save -o`.

`TestSaveMultipleNames` verifies saving multiple repository references for the same image and reading `index.json` to ensure both tags are present. `TestLoadZeroSizeLayer` is skipped and documents a legacy archive format issue around deliberately empty layer files. `TestSaveLoadParents` creates two committed images with a parent-child relationship, saves both, removes the child, reloads, and checks the `Parent` field for legacy graphdriver stores. `TestSaveLoadNoTag` distinguishes load output when saving by image ID versus saving by repository name.

## State and Persistence Behavior

The tests mutate image state by tagging, committing, deleting, saving, and loading images. Several tests intentionally delete images between save and load to ensure restoration is real. Archive data is passed through stdout pipelines or temp files depending on the scenario. Inspect JSON is used as a persisted-state oracle for image identity and metadata.

Parent metadata behavior is explicitly store-dependent: `TestSaveLoadParents` skips when using the containerd snapshotter because the `Parent` image property is not supported there. Snapshotter mode also changes archive structure expectations and inspect timestamp comparisons.

## Dependencies and Integration Points

This suite integrates the CLI image commands, daemon image store, archive exporter/importer, content-addressed blob layout, snapshotter-specific OCI index behavior, and local command pipelines. It depends on external binaries (`tar`, `grep`, `xz`, `gzip`) being present in the test environment. It also depends on `busybox` and the special empty filesystem image helper.

The tests cross the CLI/daemon boundary through stdin/stdout streaming, `-o` and `-i` file options, and structured daemon inspection. That makes them sensitive to both archive format changes and user-facing load/save messages.

## Risks and Maintenance Notes

Archive format evolution is the main risk. The tests already contain conditional logic for snapshotter versus graphdriver behavior and a skipped legacy zero-layer case. Exact output strings such as "Loaded image:", "Loaded image ID:", and "No such image:" are user-facing contracts but can break if wording changes.

Pipelines through compression tools and `tar` make these tests dependent on host utilities. Saving by short ID is used because a TODO notes full image ID save behavior was failing at the time. Parent metadata tests are legacy-store-specific and should not be generalized to containerd image stores without a new contract.

## Test Signals

Passing tests signal that `docker save` emits archives with expected manifest/blob/tag contents, `docker load` restores image identity and metadata where supported, invalid or unsupported input does not create partial images, missing-image errors are clear, and load output correctly distinguishes named images from image-ID-only archives.
