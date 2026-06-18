# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96801.h

## Purpose

This 217-line header defines ROHM BD96801 PMIC control, watchdog, state, IRQ, mask, and regulator fault bit assignments. It distinguishes the chip's two physical interrupt lines, `INTB` and `ERRB`, and maps system, buck, and LDO event sources.

## Important APIs, Types, and Functions

The file defines control registers such as `BD96801_REG_WD_CONF`, `BD96801_REG_PMIC_STATE`, lock/unlock values, main/status/mask register ranges, `BD96801_MAX_REGISTER`, system error masks, ERRB IRQ enum values for system/buck/LDO shutdown and protection faults, INTB IRQ enum values for warning/detection events, and reusable buck/LDO IRQ masks.

## Control Flow

No local flow exists. The MFD IRQ setup uses the main register to discover which ERRB or INTB group is active, then regmap-irq or subdevice handlers resolve specific buck/LDO/system bits from the grouped status registers.

## State and Persistence Behavior

State persists in PMIC registers, including watchdog timeout/status, boot overtime, PMIC/external state, masked interrupt groups, lock state, and fault latches. Unlock/lock values gate protected writes.

## Dependencies and Integration Points

It integrates with ROHM MFD core, watchdog, regulator, and interrupt handling. Child regulators use the common buck/LDO masks for over-current, over/under-voltage, thermal warning, and shutdown classification.

## Risks and Edge Cases

ERRB and INTB IRQ spaces are separate enums; mixing them would mislabel faults. Protected register writes must respect lock sequencing. Gaps and group boundaries in the register map mean naive contiguous IRQ mapping can misroute events.

## Test Signals

Build coverage, regmap-irq mapping tests for each ERRB/INTB register group, watchdog configuration smoke tests, lock/unlock write tests, and regulator fault injection validating that warnings versus shutdown faults are reported distinctly.
