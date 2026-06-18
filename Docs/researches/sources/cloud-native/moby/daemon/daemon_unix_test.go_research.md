# sources/cloud-native/moby/daemon/daemon_unix_test.go

## Purpose
Tests Unix-specific validation and translation helpers for shared namespaces, security options, Linux resource warnings, and blkio device conversion.

## Important APIs, Types, And Functions
- `fakeContainerGetter` supports namespace adaptation tests.
- `TestAdjustSharedNamespaceContainerName` verifies `container:name` modes become `container:ID`.
- `TestParseSecurityOptWithDeprecatedColon`, `TestParseSecurityOpt`, and `TestParseNNPSecurityOptions` cover AppArmor, seccomp, labels, no-new-privileges, writable cgroups, deprecated colon syntax, and invalid option errors.
- `TestVerifyPlatformContainerResources` checks OOM/memory warning behavior.
- `deviceTypeMock`, `TestGetBlkioWeightDevices`, and `TestGetBlkioThrottleDevices` validate device major/minor extraction.

## Control Flow
Tests build synthetic host configs and sysinfo structs, call the relevant helper directly, and assert exact error strings, flags, warnings, and generated OCI device structures. Device tests create a character device with a known major/minor when running as root.

## State And Persistence
Most state is in-memory. Device tests create a temporary directory and `mknod` device, then remove it. SELinux-dependent assertions are softened because labels depend on host state.

## Dependencies And Integration Points
Depends on Unix build tags, SELinux package behavior, Linux `mknod` for device tests, sysinfo capability fields, daemon config store, and container security option structs.

## Risks And Edge Cases
Root-required device tests skip in unprivileged environments. Security label assertions are limited when SELinux is enabled, leaving exact label generation to integration coverage.

## Test Signals
Failures identify regressions in user-facing `--security-opt` parsing, daemon default no-new-privileges precedence, warning/discard behavior for unsupported resource controls, and blkio device mapping into OCI specs.
