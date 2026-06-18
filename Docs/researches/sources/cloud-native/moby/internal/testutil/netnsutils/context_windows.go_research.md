<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/context_windows.go -->
# sources/cloud-native/moby/internal/testutil/netnsutils/context_windows.go

Purpose: Windows stub for network namespace test-context setup. It exposes `SetupTestOSContext` returning a no-op cleanup function so callers can compile across platforms. Control flow, namespace state, and persistence are intentionally absent. Dependencies are only `testing`. Risks are low, but tests needing real namespace isolation must be build-gated away from Windows. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/context_windows.go -->
