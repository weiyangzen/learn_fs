# sources/cloud-native/moby/daemon/oci_windows_test.go

## Purpose
This file tests Windows credential spec handling and Windows device mapping conversion.

## Important APIs, Types, And Functions
`TestSetWindowsCredentialSpecInSpec` targets `Daemon.setWindowsCredentialSpec`. `dummyRegistryKey` and `setRegistryOpenKeyFunc` mock registry access. `TestSetupWindowsDevices` targets `setupWindowsDevices`.

## Control Flow
Credential spec tests create a temporary daemon root, define a container factory for security options, create a credential spec file, and run subtests for no options, file, registry, swarm config, raw, malformed, unsupported, and empty values. Registry tests replace the package-level opener and restore it afterward. Device tests feed valid and invalid `DeviceMapping.PathOnHost` syntaxes and compare generated `specs.WindowsDevice` entries.

## State, Persistence, And Dependencies
The tests create temporary files under a fake daemon root and mutate the package-level `registryOpenKeyFunc` within cleanup. Swarm dependency manager state is created for `config://` tests. Dependencies include Windows registry package, swarmkit agent/API, gotest filesystem/assertions, and runtime-spec types.

## Integration Points
The tests protect API behavior for `--security-opt credentialspec=...` and `--device` on Windows containers.

## Risks And Edge Cases
Tests assert `config://` is hidden from non-swarm containers by returning the generic invalid-credential-spec error. File path validation covers absolute paths and breakout attempts. Multiple security options behavior is noted in production code but not deeply tested here.

## Test Signals
Coverage is strong for credential spec parsing/storage sources and device syntax. It does not instantiate full Windows OCI specs or HCS.
