# sources/cloud-native/containerd/integration/images/image_list.sample.toml

## Purpose

This sample TOML file documents how to override integration test image references with the `-image-list` flag.

## Important APIs, Types, And Functions

- Keys correspond to fields in `images.ImageList`: `alpine`, `busybox`, `pause`, `VolumeCopyUp`, `VolumeOwnership`, and `ArgsEscaped`.
- Values are fully qualified image references used by integration tests.

## Control Flow

The file has no executable control flow. It is consumed by `image_list.go` when a test process is started with `-image-list=<path>`.

## State And Persistence Behavior

It is static configuration. When copied and passed to tests, it affects process-local image map initialization only.

## Dependencies And Integration Points

It integrates with TOML unmarshalling in `initImages` and with test image pull behavior throughout the integration suite.

## Risks And Edge Cases

The sample uses mixed key casing; override authors should verify TOML decoding maps keys to intended exported fields. The `VolumeCopyUp` sample version is `2.1`, while the current default in code is `2.2`, so copying it verbatim may intentionally or accidentally test an older fixture.

## Test Signals

Tests started with this sample should pull Docker Hub BusyBox/Alpine and the listed containerd fixture images instead of hard-coded defaults.
