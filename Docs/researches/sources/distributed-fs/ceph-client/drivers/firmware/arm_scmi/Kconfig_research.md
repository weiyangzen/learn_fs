# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Kconfig

## Purpose
Defines configuration for the ARM System Control and Management Interface protocol stack, optional debug/raw/quirk facilities, SCMI transports, vendor extensions, and the SCMI system power-control client driver.

## APIs, Types, And Functions
Main symbols are `ARM_SCMI_PROTOCOL`, `ARM_SCMI_NEED_DEBUGFS`, `ARM_SCMI_RAW_MODE_SUPPORT`, `ARM_SCMI_RAW_MODE_SUPPORT_COEX`, `ARM_SCMI_DEBUG_COUNTERS`, `ARM_SCMI_QUIRKS`, and `ARM_SCMI_POWER_CONTROL`. The file sources transport and NXP i.MX vendor Kconfig fragments.

## Control Flow
When `ARM_SCMI_PROTOCOL` is enabled, nested options expose raw mode, debug counters, quirks, transports, and vendors. `ARM_SCMI_POWER_CONTROL` remains outside the `if` block and can depend on SCMI or compile-test plus OF.

## State, Persistence, And Dependencies
Persistent effect is kernel configuration. Dependencies include ARM/ARM64/COMPILE_TEST, DEBUG_FS, JUMP_LABEL, OF for compile-tested power control, and transport-specific symbols in sourced files.

## Integration Points
These symbols drive `arm_scmi/Makefile`, enable protocol modules such as base/clock/perf/power, and control whether raw debugfs and quirk code is linked.

## Risks And Test Signals
Risks include raw mode accidentally coexisting with regular clients, missing debugfs selects, and quirk framework availability depending on jump labels. Signals are config/build coverage and boot tests with representative SCMI transports.
