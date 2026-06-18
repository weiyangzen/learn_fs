<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/logger.go -->
# sources/cloud-native/moby/internal/testutil/logger.go

Purpose: defines a narrow `Logger` interface with logging methods expected from `testing.T` and asserts `*testing.T` satisfies it. This lets helper packages accept any compatible logger without importing `testing.T` concretely everywhere. Control flow and persistence are absent. Dependencies are the testing package. Risks are minimal; API drift in helper expectations would be caught at compile time. Test signal is build-time.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/logger.go -->
