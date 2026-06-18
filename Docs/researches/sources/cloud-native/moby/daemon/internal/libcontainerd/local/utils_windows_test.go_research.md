<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows_test.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows_test.go

Purpose: validates Windows environment parsing for the local HCS executor.

Important APIs and types: `TestEnvironmentParsing` exercises `setupEnvironmentVariables`.

Control flow: builds `[]string{"foo=bar", "car=hat", "a=b=c"}`, parses it, and asserts the expected three-entry map.

State and persistence: no persistent state; test operates on an in-memory slice and map.

Dependencies and integration: package-local test for `utils_windows.go`; it supports the process environment path used by `local_windows.go`.

Risks: coverage is narrow. It does not cover malformed entries, duplicate keys, empty keys, or missing separators.

Test signals: confirms `strings.Cut` first-separator behavior and map population for ordinary Docker environment entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows_test.go -->
