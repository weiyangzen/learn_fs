# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sysfs.c

## Purpose
`cros_ec_sysfs.c` exposes selected Chrome EC control and diagnostic functions through sysfs attributes on the EC class device: reboot control, firmware/chip/board version display, flash geometry, keyboard wake angle, USB PD mux state, and AP-driven altmode capability.

## Important APIs, Types, and Functions
- `reboot_show()` and `reboot_store()` parse reboot commands and send `EC_CMD_REBOOT_EC`.
- `version_show()` sends `GET_VERSION`, `GET_BUILD_INFO`, `GET_CHIP_INFO`, and `GET_BOARD_VERSION`.
- `flashinfo_show()` sends `EC_CMD_FLASH_INFO`.
- `kb_wake_angle_show()`/`store()` use `MOTIONSENSE_CMD_KB_WAKE_ANGLE`.
- `usbpdmuxinfo_show()` reads port count and per-port mux flags.
- `ap_mode_entry_show()` reports `EC_FEATURE_TYPEC_REQUIRE_AP_MODE_ENTRY`.
- `cros_ec_ctrl_visible()` hides attributes not applicable to a device.

## Control Flow
Probe creates an attribute group on the parent EC class device. Each sysfs read/write allocates a command buffer if needed, fills command metadata and parameters, calls `cros_ec_cmd_xfer_status()` or `cros_ec_cmd()`, formats results with `sysfs_emit*()`, and frees temporary memory. Removal deletes the attribute group. Visibility checks run when sysfs builds the group and hide keyboard wake angle unless sensor discovery found the needed accelerometers; USB PD attributes are shown only for the primary EC name.

## State and Persistence
This file stores no persistent private state. It reads and mutates EC firmware state through host commands: reboot action flags, keyboard wake angle setting, and queried status. Attribute visibility depends on `struct cros_ec_dev` fields and platform data.

## Dependencies and Integration Points
It depends on the platform driver named `"cros-ec-sysfs"`, Chrome EC command definitions, `to_cros_ec_dev()`, the generic command helpers, platform data `cros_ec_platform`, and feature state populated by protocol/sensorhub code. User space integrates through sysfs files under the EC class device.

## Risks and Edge Cases
`reboot_store()` token parsing accepts any word prefix matched by `strncasecmp()` and advances by whitespace-delimited words; ambiguous or suffixed tokens could be accepted if they start with a valid command. Version display returns partial output when later optional commands fail, embedding transfer/result errors in the text. `usbpdmuxinfo_show()` returns `-EIO` if no per-port mux reads succeed. The visibility path assumes platform data and `ec_name` are present.

## Test Signals
No local tests are present. Manual/runtime signals are sysfs attribute creation, correct hide/show behavior, successful formatted version/flashinfo reads, and expected EC behavior after reboot or keyboard wake angle writes.
