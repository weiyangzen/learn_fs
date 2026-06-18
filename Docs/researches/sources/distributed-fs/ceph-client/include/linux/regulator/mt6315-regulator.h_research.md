# sources/distributed-fs/ceph-client/include/linux/regulator/mt6315-regulator.h

## Purpose

This header defines MediaTek MT6315 regulator IDs and register constants needed by its regulator driver.

## Important APIs, Types, and Functions

Package/type constants include `MT6315_RP`, `PP`, and `SP`. Regulator IDs cover `MT6315_VBUCK1` through `VBUCK4`, ending at `MT6315_VBUCK_MAX`. Register macros define top key/protection registers, buck top control/ELR registers, debug registers for each buck, and a four-phase analog config register. Protection key values are `PROTECTION_KEY_H` and `PROTECTION_KEY`.

## Control Flow

The driver uses the register constants to unlock protected areas, identify package mode, configure buck topology, and read/write debug or voltage-related registers.

## State and Persistence Behavior

No C state is defined. The constants address PMIC hardware state that can persist until reset or power loss. Protection-key writes gate access to sensitive registers.

## Dependencies and Integration Points

The header is standalone and integrates with MediaTek PMIC/regmap driver code.

## Risks

Incorrect register addresses or protection-key sequencing can fail writes or modify protected PMIC state incorrectly. Package constants must match hardware variants.

## Test Signals

Tests should validate register-map accesses against datasheet addresses, protected write unlock sequences, package-specific topology, and all four buck descriptors.
