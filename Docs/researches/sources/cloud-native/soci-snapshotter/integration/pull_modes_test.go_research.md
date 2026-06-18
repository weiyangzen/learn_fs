# sources/cloud-native/soci-snapshotter/integration/pull_modes_test.go

Purpose: verifies selection and precedence of SOCI v1, SOCI v2, and experimental parallel pull modes.

Important APIs and flow: `createAndPushV2Index` converts an image to a SOCI v2 image, pushes it, and finds the platform-specific v2 index digest. `createAndPushV1Index` builds and pushes a v1 index. `TestPullModes` runs mode matrices: both lazy modes disabled, explicit v1/v2 digest override, v1-only, v2-only, parallel pull/unpack, v2-over-v1 preference, and defaults. Log monitors capture the index digest actually used. `TestV1IsNotUsedWhenDisabled` ensures v1 is not selected when disabled. `TestDanglingV2Annotation` creates a manifest with a dangling v2 annotation and verifies deferred snapshots plus "no valid index" logging. `TestExperimentalParallelPullAsFallback` checks parallel fallback when indexed images are absent and precedence when parallel is explicitly enabled.

State and persistence: writes converted images, v1/v2 indexes, registry tags, and content-store state; restarts containerd per mode.

Dependencies and integration: uses SOCI config `PullModes`, registry helpers, `nerdctl`, `soci convert/create/push`, containerd log monitors, and remote/local/deferred snapshot monitors.

Risks and test signals: excellent coverage for mode precedence and fallback behavior. It is sensitive to structured log message text and requires content-store type alignment for parallel pull.
