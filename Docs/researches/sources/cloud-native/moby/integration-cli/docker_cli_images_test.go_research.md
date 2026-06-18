# sources/cloud-native/moby/integration-cli/docker_cli_images_test.go

Purpose: integration coverage for `docker images` and `docker image ls`: listing, repository/tag filtering, creation-date ordering, label/since/before/dangling filters, output formatting, scratch/busybox image visibility, registry names with ports, and config default format interaction.

Important APIs/types/functions: `DockerCLIImagesSuite`, helper `getImageIDs`, and tests such as `TestImagesEnsureImageIsListed`, `TestImagesEnsureImageWithTagIsListed`, `TestImagesOrderedByCreationDate`, `TestImagesFilterLabelMatch`, `TestCommitWithFilterLabel`, `TestImagesFilterSinceAndBefore`, `TestImagesFilterSpaceTrimCase`, `TestImagesEnsureDanglingImageOnlyListedOnce`, `TestImagesEnsureOnlyHeadsImagesShown`, `TestImagesEnsureImagesFromScratchShown`, `TestImagesFilterNameWithPort`, `TestImagesFormat`, and `TestImagesFormatDefaultFormat`.

Control flow: tests tag busybox, build small images, commit containers, list images with filters and `--format`, parse IDs from tab-separated output, and compare order/visibility. Sleep calls are inserted between builds to make creation-order sorting deterministic. The default-format test writes a temporary CLI config and verifies `-q` still prints only IDs.

State and persistence: creates tags, images, dangling images, committed images, temporary CLI config directories, and failed build intermediate images. Image metadata includes labels, created timestamps, repo tags, and IDs.

Dependencies and integration points: build helper, `stringid.TruncateID`, Docker CLI config, busybox and scratch images, image filter implementation, and CLI formatter.

Risks: sleeps are needed because timestamp granularity can make ordering flaky. Some tests parse build output line positions to identify intermediate images. Failed-build dangling image assumptions depend on builder behavior. Snapshotter/buildkit changes could alter intermediate visibility.

Test signals: failures indicate image list filtering/order regressions, improper dangling handling, bad label filter matching, formatter/config precedence bugs, or repository parsing issues for names containing registry ports.
