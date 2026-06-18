# sources/cloud-native/moby/integration/daemon/nri/testdata/test_plugin.go

Purpose: standalone NRI plugin binary fixture used by reload tests to validate daemon-managed plugin discovery and plugin configuration reload.

Important APIs and types: `config`, `plugin`, `Configure`, `CreateContainer`, and `main`. The plugin uses NRI `stub.New`, `stub.Run`, `api.MustParseEventMask`, and `api.ContainerAdjustment`.

Control flow: `main` parses optional `-name` and `-idx`, constructs a stub that exits the process on close, and runs it. `Configure` parses JSON config when present and subscribes to `CreateContainer`. `CreateContainer` always injects `NRI_TEST_PLUGIN=wozere` and conditionally injects the configured env var/value pair.

State and persistence: plugin state is the in-memory parsed config from the daemon-provided plugin config file. The plugin itself persists nothing; the test writes its config externally.

Dependencies and integration: depends on containerd NRI APIs, JSON config delivered by the daemon, and executable plugin discovery from the daemon's configured plugin path.

Risks: exits with status 1 on stub setup/run errors and status 0 on close, so failures can be silent except through daemon/plugin behavior in tests. Config schema is intentionally minimal.

Test signals: verifies external plugin process startup, config parsing, event subscription, and container-create env adjustment after daemon reload.
