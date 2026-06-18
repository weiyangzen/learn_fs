<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils.go -->
# sources/cloud-native/moby/internal/testutil/stringutils.go

Purpose: generates random alphabetic-only strings for test resource names. `GenerateRandomAlphaOnlyString` returns an `n`-length string using letters, likely backed by pseudo-random selection. State is only random generator state from the standard library if used. Dependencies are minimal. Risks include non-determinism, possible collisions for small lengths, and suitability only for tests rather than security. Test signal is defined in `stringutils_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils.go -->
