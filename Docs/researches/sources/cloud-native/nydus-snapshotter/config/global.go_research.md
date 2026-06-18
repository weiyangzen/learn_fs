# sources/cloud-native/nydus-snapshotter/config/global.go

Purpose: cache processed configuration for packages that avoid threading `SnapshotterConfig` through every call.

APIs/flow: getter functions expose daemon mode, fs driver, log settings, paths, mirrors, system controller, skip TLS, backend source, and tarfs export flags. `ProcessConfigurations` derives cache/snapshots/config/socket/mount paths, parses daemon mode, and forces fscache to shared daemon mode. `PrepareLogDir` and `SetUpEnvironment` set log dir and create/normalize root.

State/dependencies: global package variable holds origin pointer and derived paths; creates root directory.

Integration points: consumed broadly by snapshot, daemonconfig, logging, and system controller code.

Risks/tests: global mutable state complicates tests and concurrent reconfiguration. `SetUpEnvironment` normalizes root after some derived paths may already be computed unless call order is maintained.
