<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/helper.go -->
# sources/cloud-native/moby/internal/testutil/helper.go

Purpose: defines the small `HelperT` interface used by test helpers that only need `Helper()`. It avoids requiring a full `testing.TB` when a narrower capability is enough. Control flow and state are absent. Dependencies are none. Risks are minimal; the value is compile-time decoupling of helper annotations from concrete testing types. Test signal is build-time compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/helper.go -->
