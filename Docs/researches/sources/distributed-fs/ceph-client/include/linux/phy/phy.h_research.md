# sources/distributed-fs/ceph-client/include/linux/phy/phy.h

## Purpose
Generic non-Ethernet PHY framework contract used by USB, UFS, PCIe, Ethernet SerDes, MIPI D-PHY, SATA, LVDS, DisplayPort, HDMI, and related providers/consumers.

## Important APIs, Types, and Functions
Defines `enum phy_mode`, `enum phy_media`, `enum phy_ufs_state`, `union phy_notify`, `union phy_configure_opts`, `struct phy_ops`, `struct phy_attrs`, `struct phy`, `struct phy_provider`, and `struct phy_lookup`. Consumer APIs include `phy_get()`, `devm_phy_get()`, optional and OF-index variants, `phy_init()`, `phy_exit()`, `phy_power_on()`, `phy_power_off()`, `phy_set_mode_ext()`, `phy_set_media()`, `phy_set_speed()`, `phy_configure()`, `phy_validate()`, `phy_reset()`, `phy_calibrate()`, and notification helpers. Provider APIs include `phy_create()`, `devm_phy_create()`, provider registration, lookup creation/removal, and xlate helpers.

## Control Flow
Consumers acquire a PHY by lookup or firmware node, optionally runtime-resume it, initialize, configure/validate, set mode/media/speed, power on, notify state changes, then power off/exit and put it. Providers create `struct phy` instances with operation tables and register firmware-node providers or static lookups. Disabled `CONFIG_GENERIC_PHY` builds return benign success for NULL optional PHYs and `-ENOSYS`/`-ENODEV` for real operations.

## State and Persistence
`struct phy` persists device identity, ops, mutex, init and power reference counts, attributes, regulator pointer, and debugfs state. The framework preserves shared-use semantics through counts so multiple consumers do not over-initialize or prematurely power off a PHY.

## Dependencies and Integration Points
Depends on device model, OF/fwnode, runtime PM, regulators, module ownership, and protocol-specific option headers for DP/HDMI/LVDS/MIPI. Integrates broad subsystem consumers through a common lifecycle and provider lookup model.

## Risks
Reference-count imbalance can leak power or power off active links. Optional-NULL success semantics must be distinguished from missing required PHY errors. Providers must serialize operations and validate mode-specific unions correctly.

## Test Signals
Builds with generic PHY enabled/disabled, devm cleanup tests, multi-consumer init/power count tests, DT lookup/xlate tests, and subsystem bring-up tests for each supported `phy_mode`.
