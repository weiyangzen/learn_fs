<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.h

## Purpose
Provides MT6311 local register addresses and bit masks used by the MT6311 regulator driver.

## Important APIs, Types, And Functions
The header defines SWCID, interrupt, VDVFS control, LDO control, frequency meter registers, interrupt masks, VDVFS enable/control/vosel masks, and VBIASN enable mask. It has no functions or structures.

## Control Flow
No runtime control flow. The C driver uses these constants to configure `struct regulator_desc` fields and validate chip ID through registers declared elsewhere.

## State And Persistence
No driver state exists here. The constants describe persistent PMIC register bits for buck voltage, buck enable, LDO enable, and status/interrupt controls.

## Dependencies And Integration Points
Included only by `mt6311-regulator.c`. It is coupled to `linux/regulator/mt6311.h` for regulator IDs and chip ID constants.

## Risks And Test Signals
Risks include incorrect masks for voltage and enable bits, stale register offsets, and missing definitions for new silicon revisions. Test through compile coverage and hardware read/write validation of VDVFS and VBIASN registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.h -->
