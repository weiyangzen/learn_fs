# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cannonlake.c

## Purpose
Describes Cannon Lake-H and Cannon Lake-LP PCH pinctrl/GPIO hardware for the shared Intel pinctrl core. It supplies pad names, function groups, community layouts, register offsets, and ACPI IDs for the platform driver.

## Important APIs, Types, and Functions
`CNL_LP_*` and `CNL_H_*` macros define register offsets for ownership, lock, host software ownership, interrupt status, and interrupt enable. `CNL_LP_COMMUNITY()` and `CNL_H_COMMUNITY()` create `intel_community` entries. Static arrays include `cnlh_pins[]`, `cnlh_groups[]`, `cnlh_functions[]`, `cnlh_communities[]`, `cnlh_soc_data`, plus the corresponding LP arrays `cnllp_*`. ACPI IDs `INT3450` and `INT34BB` select H or LP data. The driver delegates probe to `intel_pinctrl_probe_by_hid`.

## Control Flow
When ACPI enumerates a Cannon Lake pinctrl device, match data gives the shared Intel core the correct SoC descriptor. The common core registers pinctrl, GPIO, IRQ, and PM handling. Function groups define legal mux operations for SPI, UART, I2C, and related pads; plain pins/GPP entries expose GPIO-capable ranges.

## State and Persistence Behavior
Only immutable tables live here. Runtime pad ownership, locks, mux state, GPIO values, IRQ masks/status, and sleep context live in hardware and the shared Intel core.

## Dependencies and Integration Points
Depends on ACPI platform devices, `pinctrl-intel.h`, pinctrl descriptors, and shared Intel PM operations. It integrates with Cannon Lake ACPI firmware, GPIO consumers, and peripheral drivers that rely on SPI/I2C/UART pin groups.

## Risks
H and LP variants have different register layouts and pin ranges; mapping an ACPI ID to the wrong descriptor can corrupt GPIO numbering and register access. Mixed-mode SPI groups require correct per-pin mode arrays. Non-GPIO groups marked with `INTEL_GPIO_BASE_NOMAP` must not become GPIO lines.

## Test Signals
Probe for both ACPI IDs, debugfs pin and group visibility, SPI/I2C/UART mux selection, GPIO interrupt handling through shared registers, non-GPIO groups excluded from GPIO numbering, suspend/resume state retention, and `PINCTRL_CANNONLAKE` builds are useful signals.
