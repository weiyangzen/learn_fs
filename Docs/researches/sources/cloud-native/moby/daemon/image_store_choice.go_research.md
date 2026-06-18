<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice.go -->
# sources/cloud-native/moby/daemon/image_store_choice.go

Purpose: decides whether the daemon should use the containerd image store/snapshotter path or the legacy graphdriver image store.

Important APIs and control flow: `imageStoreChoice` encodes default, explicit, and prior-data choices. `IsGraphDriver` and `IsExplicit` classify those choices. `getDriverOverride` resolves a graphdriver or snapshotter name from `DOCKER_DRIVER`, daemon config, and Windows defaults. `determineImageStoreChoice` starts with containerd by default except Windows, applies the `containerd-snapshotter` feature flag, the `TEST_INTEGRATION_USE_GRAPHDRIVER` override, prior graphdriver data detection, and registered graphdriver recognition before returning a choice or an explicit-graphdriver error.

State and persistence: reads environment variables and checks prior graphdriver state under the configured daemon root through injectable functions. No state is written.

Dependencies and integration: depends on daemon config, `graphdriver.HasPriorDriver`, `graphdriver.IsRegistered`, runtime OS, and containerd logging. Its output steers daemon startup, storage initialization, and migration safety.

Risks: behavior depends on environment variables, feature flags, platform, and previously persisted driver state, so startup outcomes can be surprising. Non-registered driver names are treated as snapshotter names unless graphdriver mode was explicit. Prior graphdriver data takes precedence over configured graphdrivers in some paths to avoid accidental migration.

Test signals: `image_store_choice_test.go` covers feature flag precedence, integration-test overrides, registered graphdrivers, custom snapshotters, prior data, and Windows-specific choices.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice.go -->
