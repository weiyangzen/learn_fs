# sources/control-plane/longhorn-engine/integration/data/test_upgrade.py

## Purpose
This file validates live engine binary upgrade and rollback behavior while preserving volume data and frontend endpoint continuity.

## Important APIs, types, and functions
- Single test: `test_upgrade`.
- Uses `get_dev`, `verify_data`, `upgrade_engine`, `get_process_address`, `wait_for_process_running`, `get_controller_version_detail`, `cleanup_replica`, and `open_replica`.
- Constants identify current and upgrade binaries, volume/device names, size strings, and Longhorn dev directory.
- The controller client method `client_upgrade` points the test client at the new engine process address after a successful upgrade.

## Control flow
The test obtains a device from fixed replicas and a controller, writes data, starts the volume with the fixed replicas, then launches an upgrade engine using extra replica fixtures pointed at the same underlying volume data. After verifying data remains readable, it upgrades the controller client to the upgrade engine address, waits for the named process to be running, fetches version details, and verifies the frontend endpoint path.

It then tries an invalid upgrade back to the original binary with a bogus replica URL and expects a gRPC error/rollback without data loss. Finally it cleans and reopens the fixed replicas, starts an engine with the original binary, verifies data, upgrades the controller client back, and checks endpoint/version again.

## State and persistence behavior
The test observes persistent data across engine process swaps, replica cleanup/reopen, and controller client address changes. It also verifies the stable frontend device path under `LONGHORN_DEV_DIR` and process manager state after upgrade.

## Dependencies and integration points
It integrates the engine manager process API, controller gRPC API, fixed and extra replica fixtures, binary paths for current and upgrade engines, and the Longhorn frontend device. It depends on helper semantics that create upgrade processes without destroying the live device.

## Risks and edge cases
- The same-binary upgrade check is commented out, so only wrong-replica rollback is actively tested.
- The test assumes extra replica fixtures reference the same volume backing as the fixed replicas.
- Upgrade success is inferred from process running, version detail fetch, endpoint path, and data integrity; deeper version compatibility is not asserted.

## Test signals
Signals include unchanged data before/after upgrade and rollback attempts, `upgrade_e.spec.binary` matching the upgrade binary, gRPC error on invalid replica upgrade, successful process running state, readable version detail, and stable endpoint `LONGHORN_DEV_DIR/VOLUME_NAME`.
