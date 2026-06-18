## sources/cloud-native/moby/integration-cli/requirements_windows_test.go

Purpose: Windows build companion for requirement helpers. `setupLocalInfo` is a no-op and `onlyCgroupsv2` always returns false.

Control flow is intentionally empty because Windows does not use the Unix `sysinfo`/cgroups path. State and persistence are none. Dependencies are only package `main` and build selection by filename/build constraints.

Risks are semantic drift if tests begin relying on other Unix-only requirement helpers without Windows counterparts. Test signals are indirect through compilation and skip decisions: Windows builds can link shared tests that call `setupLocalInfo` or `onlyCgroupsv2` without importing Unix-only packages.
