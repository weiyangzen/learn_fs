<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice_test.go -->
# sources/cloud-native/moby/daemon/image_store_choice_test.go

Purpose: table-driven coverage for image store selection across Linux-like and Windows daemon startup scenarios.

Important APIs and control flow: `TestDetermineImageStoreChoice` constructs cases for feature flags, `DOCKER_DRIVER`, `TEST_INTEGRATION_USE_GRAPHDRIVER`, graphdriver config, prior graphdriver data, custom snapshotter names, and Windows `windows`/`windowsfilter` driver names. It injects fake `hasPriorDriver`, fake graphdriver registry checks, and fake runtime OS values.

State and persistence: uses `t.Setenv` for environment isolation. No filesystem state is created because prior-driver detection is injected.

Dependencies and integration: depends on daemon config structs, slices membership helpers, and `gotest.tools` comparisons. It validates policy implemented by `determineImageStoreChoice` without requiring registered real drivers.

Risks: `expectError` support exists but the shown cases mostly exercise non-error paths; explicit invalid graphdriver errors may be undercovered. Platform simulation is string based, so any runtime-specific side effects outside `determineImageStoreChoice` are not tested.

Test signals: strong coverage for the startup decision matrix and precedence ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_store_choice_test.go -->
