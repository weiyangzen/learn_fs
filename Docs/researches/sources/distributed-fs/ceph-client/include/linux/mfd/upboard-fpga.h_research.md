# sources/distributed-fs/ceph-client/include/linux/mfd/upboard-fpga.h

## Purpose
`upboard-fpga.h` defines the MFD data structures and register IDs for the UP Board CPLD/FPGA companion device. It supports platform/firmware ID reads, function enable registers, GPIO enable/direction registers, bit-banged control GPIOs, and per-board FPGA metadata.

## Important APIs, Types, and Functions
`UPBOARD_REGISTER_SIZE` sets a 16-bit register width assumption. `enum upboard_fpgareg` names platform ID, firmware ID, function enable, GPIO enable, GPIO direction, and `UPBOARD_REG_MAX`. `enum upboard_fpga_type` distinguishes UP and UP2 FPGA variants. `struct upboard_fpga_data` pairs the type with a regmap configuration. `struct upboard_fpga` stores device, regmap, enable/reset/clear/strobe/datain/dataout GPIO descriptors, firmware version, and variant data.

## Control Flow
The parent driver selects an `upboard_fpga_data` variant, initializes regmap through the variant config, toggles control GPIOs as needed for serial register access, reads firmware/platform IDs, and child drivers use shared regmap/register IDs for function and GPIO enablement.

## State and Persistence Behavior
FPGA registers persist platform/firmware identity, enabled peripheral functions, enabled GPIO banks, and GPIO direction settings. Software keeps the firmware version and live GPIO descriptors for the parent device lifetime.

## Dependencies and Integration Points
The header relies on `struct device`, `struct regmap`, `struct regmap_config`, and GPIO descriptors from includers. It integrates with MFD parent probing, regmap, GPIO, pin/function enable subdrivers, and board-specific ACPI/device-tree matching.

## Risks and Test Signals
Risks include variant regmap mismatch, incorrect 16-bit register assumptions, control GPIO sequencing errors, stale firmware-version compatibility checks, and function-enable bits conflicting with GPIO use. Test signals are platform/firmware ID readback, UP vs UP2 probe tests, GPIO bank enable/direction readback, control GPIO timing tests, and child device probing against enabled functions.
