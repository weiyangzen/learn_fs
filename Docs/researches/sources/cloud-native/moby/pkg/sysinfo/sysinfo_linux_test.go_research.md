# sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux_test.go

Purpose: Linux unit coverage for sysinfo helper parsing and feature probes.

APIs and flow: tests verify `readProcBool`, `cgroupEnabled`, `New` generic fields, cpuset subset validation, valid/invalid `parseUintList` forms, and max-limit enforcement.

State and dependencies: uses temporary files/directories for proc/cgroup helper tests and live host state for seccomp/AppArmor/namespace expectations.

Integration points: asserts `New` aligns with the same helper functions used internally rather than fixed host expectations.

Risks and signals: live-host tests may vary by environment but compare against local helper outputs. There is no direct test for cpuset mem parsing, leaving the `MemSets` source-string issue exposed.
