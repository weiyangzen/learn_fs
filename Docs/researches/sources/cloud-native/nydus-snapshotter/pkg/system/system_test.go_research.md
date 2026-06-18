<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/system/system_test.go

Purpose: unit-tests the helper that derives the next nydusd API socket name during hot upgrade.

Important test: `TestBuildUpgradeSocket` checks `buildNextAPISocket` converts `api.sock` to `api1.sock`, and increments numeric suffixes for `api2.sock`, `api23.sock`, and `api222.sock`.

Control flow and state: the test is pure and does not construct a controller or touch sockets. It validates the expected string transformation path used by `upgradeNydusDaemon`.

Dependencies/integration: uses testify assertions only.

Risks and test signals: no negative cases are covered for invalid socket names, multi-dot names, or non-`api` prefixes. The system controller’s HTTP routes, daemon upgrade sequence, symlink replacement, and signal-driven server shutdown remain untested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system_test.go -->
