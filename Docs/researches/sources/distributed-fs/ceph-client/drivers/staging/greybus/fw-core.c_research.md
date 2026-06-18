# sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-core.c

## Purpose
Core Greybus firmware bundle driver. It binds firmware-management class bundles, parses their protocol CPorts, creates per-protocol connections, initializes optional firmware download, SPI, and authentication paths, and makes firmware management mandatory.

## Important APIs, Types, And Functions
`struct gb_fw_core` stores the download, management, SPI, and CAP connections. `to_fw_mgmt_connection()` returns the management connection from device driver data. `gb_fw_core_probe()` and `gb_fw_core_disconnect()` are the Greybus driver lifecycle hooks. SPI setup is isolated in `gb_fw_spi_connection_init()` and `gb_fw_spi_connection_exit()`. Module init calls `fw_mgmt_init()`, `cap_init()`, and `greybus_register()`.

## Control Flow
Probe allocates `gb_fw_core`, walks all CPorts, rejects duplicate mandatory or optional protocol CPorts, creates connections for known protocols, and rejects unknown protocols. Firmware management must exist; download, SPI, and CAP are optional and are disabled if their init fails. Management init runs last; if it fails, the initialized optional connections are exited and every connection is destroyed.

## State And Persistence
State is per bundle and stored with `greybus_set_drvdata()`. No persistent data is written. Runtime PM is released on successful probe except for interfaces marked `GB_INTERFACE_QUIRK_NO_PM`, preserving compatibility with older S2 loader behavior.

## Dependencies And Integration Points
Integrates Greybus core with firmware management/download submodules, CAP authentication support, and `gb_spilib_master_init()` for SPI. Uses Greybus class matching through `GREYBUS_CLASS_FW_MANAGEMENT`.

## Risks
Optional connection failures are intentionally tolerated, so partial functionality is normal and callers must handle missing download/SPI/CAP paths. The duplicate CPort checks are important because connection pointers are singletons. Runtime-PM quirk behavior should not be removed until all loaders support PM.

## Test Signals
Probe matrices should cover missing management CPort, duplicate CPorts, unknown protocol IDs, optional init failures, management init failure after optional success, disconnect after partial setup, and `GB_INTERFACE_QUIRK_NO_PM` behavior.
