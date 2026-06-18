<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6358-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6358-regulator.c

## Purpose
Implements MT6358 and MT6366 regulator support for MT6397-family PMIC devices, including bucks, pickable-range LDOs, linear SRAM LDOs, fixed calibrated LDOs, buck modes, status readback, and VCN33 enable-bit synchronization.

## Important APIs, Types, And Functions
`struct mt6358_regulator_info` stores descriptor, status/QI, DA selector, and mode-register metadata. Descriptor macros define MT6358 and MT6366 buck/LDO/fixed variants. Important functions include `mt6358_map_mode()`, `mt6358_get_buck_voltage_sel()`, `mt6358_get_status()`, `mt6358_regulator_set_mode()`, `mt6358_regulator_get_mode()`, `mt6358_sync_vcn33_setting()`, and `mt6358_regulator_probe()`.

## Control Flow
Probe selects the MT6358 or MT6366 descriptor table based on the parent `mt6397->chip_id`, synchronizes VCN33 WiFi enable state into the BT enable bit and disables the duplicate WiFi bit, then registers every regulator. Buck mode operations map AUTO to NORMAL and FORCE_PWM to FAST through mode registers. Buck and linear/fixed get-voltage paths read DA monitor selectors; pickable LDOs use regulator core pickable range helpers with selector bitfields.

## State And Persistence
Regulator descriptors are static const tables; runtime state is in parent PMIC registers. `mt6358_sync_vcn33_setting()` intentionally changes hardware enable bits at probe to collapse two controls into one logical regulator. No private state is allocated.

## Dependencies And Integration Points
Depends on MT6397 core, MT6358 register and regulator headers, MT6397 regulator DT binding constants, platform devices, regmap, and regulator framework. Platform ID is `mt6358-regulator`; supported parent chip IDs are MT6358 and MT6366.

## Risks And Test Signals
Risks include chip-ID table mismatch, VCN33 sync changing bootloader state, DA monitor masks, pickable range selector arrays, fixed LDO calibration semantics, and mode mapping that only supports NORMAL/FAST. Test by probing both chip IDs, validating VCN33 sync read/write effects, registering every regulator, sweeping buck and LDO voltages, checking status registers, toggling buck FAST/NORMAL modes, and verifying MT6366-specific selector ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6358-regulator.c -->
