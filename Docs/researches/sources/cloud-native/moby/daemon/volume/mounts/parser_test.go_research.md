# sources/cloud-native/moby/daemon/volume/mounts/parser_test.go

## Purpose
Shared parser tests and mock file-info providers for platform parser suites.

## Important APIs, Types, And Functions
`mockFiProvider` and `mockFiProviderWithError` provide deterministic file existence. `TestParseMountSpec` verifies `NewParser().ParseMountSpec` normalization and fields for bind, volume, and image mounts.

## Control Flow
The test creates a temp source directory, obtains the platform parser, and runs structured mount cases for read-only/read-write binds, trailing separator cleanup, anonymous volumes, and non-Windows image mounts. It asserts type, destination, source, RW, propagation, driver, and copy data.

## State And Persistence
Only temporary directories are used.

## Dependencies And Integration Points
Supports Linux, Windows, and LCOW tests by sharing mock file-info behavior.

## Risks
Because it adapts to `runtime.GOOS`, expected paths come from platform constants in separate files. It does not deeply compare all `MountPoint.Spec` fields.

## Test Signals
Provides cross-platform smoke coverage for parser selection and normalized structured mountpoint output.
