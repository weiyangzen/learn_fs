# sources/cloud-native/moby/daemon/libnetwork/libnetwork_windows_test.go

## Purpose
Provides Windows-specific shared test constants for libnetwork tests.

## Important APIs, Types, And Functions
Defines `bridgeNetType = "nat"` and `specPath = filepath.Join(os.Getenv("programdata"), "docker", "plugins")`.

## Control Flow
There is no runtime flow beyond package initialization.

## State And Persistence
Remote plugin tests on Windows use `%ProgramData%\docker\plugins` rather than `/etc/docker/plugins`. Network tests use Windows `nat` as the bridge-equivalent network type.

## Dependencies And Integration Points
Imports `os` and `path/filepath`; integrates with shared tests that refer to `bridgeNetType` and `specPath`.

## Risks
If `programdata` is unset, `specPath` becomes a relative-ish path rooted at `docker/plugins`; tests may behave unexpectedly. The network type alias must remain aligned with Windows driver naming.

## Test Signals
Indirectly exercised by Windows libnetwork tests that create NAT networks or plugin specs.
