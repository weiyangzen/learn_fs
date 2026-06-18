<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/storeutils/store.go -->
# sources/cloud-native/moby/internal/testutil/storeutils/store.go

Purpose: creates a temporary libnetwork datastore for tests. `NewTempStore` initializes a `datastore.Store` in a test temp directory and asserts creation succeeds. State is an on-disk temporary datastore removed by the testing framework. Dependencies are libnetwork datastore and `gotest.tools/assert`. Risks are low; backend behavior remains tied to datastore implementation details. Test signal supports networking tests needing isolated persistent store state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/storeutils/store.go -->
