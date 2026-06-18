# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-generic.h

## Purpose

This 91-line header is the shared ROHM PMIC support contract. It defines chip IDs, a minimal regmap device wrapper, and generic dynamic-voltage-scaling descriptors used by ROHM regulator drivers across several PMIC families.

## Important APIs, Types, and Functions

Important exports include `enum rohm_chip_type`, `struct rohm_regmap_dev`, DVS level bit definitions for run/idle/suspend/LPSR/SNVS, `struct rohm_dvs_config`, and regulator helper prototypes `rohm_regulator_set_dvs_levels()` and `rohm_regulator_set_voltage_sel_restricted()` when `CONFIG_REGULATOR_ROHM` is enabled.

## Control Flow

No flow executes in the header. At runtime, ROHM regulator probe code reads device-tree DVS properties, uses `rohm_dvs_config` to map each state to register/mask/on-mask fields, and programs the PMIC through regmap.

## State and Persistence Behavior

`rohm_dvs_config` is static description data; actual state persists in PMIC voltage and enable registers. `ROHM_DVS_LEVEL_UNKNOWN` flags unsupported or unparsed levels.

## Dependencies and Integration Points

It includes `regmap.h` and `regulator/driver.h`, and integrates ROHM MFD cores with regulator framework descriptions and device-tree power-state configuration.

## Risks and Edge Cases

Conditional prototypes mean users must compile with regulator support or guard calls. Incorrect `level_map` or mask values can program a voltage for the wrong suspend/run state.

## Test Signals

ROHM regulator build tests with and without `CONFIG_REGULATOR_ROHM`, device-tree DVS parsing tests, and board suspend/resume tests verifying state-specific voltage and enable values.
