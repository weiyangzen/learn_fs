<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils_test.go -->
# sources/cloud-native/moby/internal/testutil/stringutils_test.go

Purpose: unit tests for random alpha string generation. Helpers verify generated length and that repeated generated strings are not all identical, then tests call those helpers for `GenerateRandomAlphaOnlyString`. State is in-memory generated strings. Dependencies are `gotest.tools/assert` and comparisons. Risks include probabilistic uniqueness assertions that could theoretically flake, though probability is low for normal lengths. Test signal covers basic contract only, not character-class exhaustiveness if helper does not check it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils_test.go -->
