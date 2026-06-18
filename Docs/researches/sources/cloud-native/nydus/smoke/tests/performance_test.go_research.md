# sources/cloud-native/nydus/smoke/tests/performance_test.go

## Purpose
This opt-in suite checks that a Nydus-converted container image stays within backend read-count and read-byte baselines for a supported workload. It targets regression detection for fs-version-5, fs-version-6, and zran modes.

## Important APIs, Types, And Functions
`PerformanceTestSuite` stores root `t`, converted image, and container name. `TestPerformance` reads `PERFORMANCE_TEST_MODE`, defaults to `fs-version-6`, configures the build context, selects `PERFORMANCE_TEST_IMAGE` or defaults to `wordpress:6.1.1`, validates support through `tool.SupportContainerImage`, converts the image with `prepareTestImage`, and calls `tool.RunContainerWithBaseline`. `prepareTestImage` prepares a registry image, creates a unique Nydus target, and uses `tool.ConvertImage`.

## Control Flow
The suite is skipped unless `PERFORMANCE_TEST` is set. When enabled it converts the workload once, starts the workload through the Nydus snapshotter, waits for the workload readiness URL, fetches backend metrics, and compares against mode-specific baselines.

## State And Persistence
Converted image references are stored on the suite struct and in the registry/container runtime. The conversion workdir is managed by `tool.ConvertImage`. Runtime metrics come from the Nydus daemon API socket under the snapshotter directory.

## Dependencies And Integration Points
It depends on containerd, nerdctl, nydus-snapshotter, local registry, `nydusify`, `nydus-image`, `nydusd`, and the baseline maps in `tool/container.go`.

## Risks
Performance baselines are environment-sensitive. CPU, network, cache warmth, image version drift, and snapshotter behavior can produce noise. The test only supports images with readiness or stdout recipes in `tool/container.go`.

## Test Signals
A pass means backend read bytes and read count are no more than 105% of the configured baseline for the selected mode after the container workload becomes ready.
