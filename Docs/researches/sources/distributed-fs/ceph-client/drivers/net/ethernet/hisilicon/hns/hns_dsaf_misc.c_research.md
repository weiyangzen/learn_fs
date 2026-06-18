# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_misc.c

## Purpose
`hns_dsaf_misc.c` provides platform-specific miscellaneous operations for DSAF: subsystem register access, CPLD/ACPI LED control, reset sequencing for DSAF/XGE/GE/PPE blocks, PHY-interface discovery, SFP presence detection, SerDes loopback programming, and platform-device lookup by fwnode.

## Important APIs and Functions
`hns_misc_op_get` allocates and fills `struct dsaf_misc_op` with either OF/MMIO/syscon callbacks or ACPI DSM callbacks. `hns_dsaf_find_platform_device` finds an associated platform device by fwnode. Internal operations include `hns_cpld_set_led`, `cpld_led_reset`, `cpld_set_led_id`, ACPI LED variants, `hns_dsaf_rst`, per-port reset functions for XGE/GE/PPE, `hns_ppe_com_srst`, `hns_mac_get_phy_if`, `hns_mac_get_sfp_prsnt`, and SerDes loopback variants.

## Control Flow
During DSAF config, `hns_misc_op_get` selects the operation table based on `dev_of_node` or ACPI fwnode. Later MAC/DSAF code invokes these callbacks for reset, LED, PHY mode, SFP presence, and loopback. OF paths write syscon/MMIO registers directly. ACPI paths package integer arguments and call `_DSM` functions identified by `hns_dsaf_acpi_dsm_guid`.

## State and Persistence
The file maintains no global mutable state beyond the static ACPI GUID. It mutates `mac_cb->cpld_led_value`, reset registers, SerDes registers, and platform hardware state through regmap/MMIO or ACPI firmware calls.

## Dependencies and Integration Points
It depends on ACPI DSM APIs, regmap/syscon helpers, platform bus lookup, DSAF register definitions, MAC control blocks, and PPE/DSAF reset semantics. It is consumed through `dsaf_dev->misc_op` by DSAF main and MAC code.

## Risks
ACPI DSM calls mostly log warnings on failure but often do not propagate errors, so hardware reset/LED operations can silently fail from higher layers. OF reset paths rely on port offsets parsed in MAC config and may no-op for out-of-range ports. SerDes loopback lane mapping is static and version-sensitive. `hns_dsaf_find_platform_device` returns a device with a reference from bus lookup; callers must be aware of lifetime expectations.

## Test Signals
OF and ACPI probe paths should verify selected callbacks, reset register writes or DSM calls for each block, LED active/inactive and link/data updates, SFP presence handling, PHY interface detection for v1/v2 and debug/service ports, SerDes loopback toggling, and error propagation for failed syscon reads/writes where available.
