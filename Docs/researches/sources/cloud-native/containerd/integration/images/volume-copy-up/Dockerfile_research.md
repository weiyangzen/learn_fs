# sources/cloud-native/containerd/integration/images/volume-copy-up/Dockerfile

## Purpose

This fixture image defines image volumes with preexisting files to test volume copy-up behavior, including Linux handling of paths that resemble Windows drive-letter paths or contain colons.

## Important APIs, Types, And Functions

- `ARG BASE` selects an OS/architecture-specific base image from the Makefile.
- `RUN` commands create `/test_dir/test_file`, `/C:/weird_test_dir/weird_test_file`, and `/:colon_prefixed/colon_prefixed_file`.
- `VOLUME` declares `/test_dir`, `C:/weird_test_dir`, and `/:colon_prefixed`.

## Control Flow

At image build time, the Dockerfile creates directories and files, then marks them as image-defined volumes. At runtime, CRI volume copy-up logic should populate host volume directories with those contents.

## State And Persistence Behavior

The built image persists the declared volumes and initial file contents in image metadata/layers. Tests later validate host volume state and container-visible contents.

## Dependencies And Integration Points

It is built by the sibling Makefile and consumed by user namespace volume copy-up tests. It deliberately includes path forms that interact with Windows path normalization logic.

## Risks And Edge Cases

The Linux Dockerfile comments explain that Windows treats drive-letter paths specially, while Linux must not mangle them. Changing volume paths can invalidate tests expecting exactly three Linux volumes.

## Test Signals

`TestUsernsVolumeCopyUp` checks that these declared volumes are copied up and have correct contents/ownership in a user namespace.
