# sources/distributed-fs/ceph-client/drivers/input/misc/rt5120-pwrkey.c

## Purpose
`rt5120-pwrkey.c` reports the Richtek RT5120 PMIC power key through the input subsystem. It handles separate press and release IRQ names by reading the PMIC interrupt-status register to derive current key state.

## Important APIs, Types, and Functions
`struct rt5120_priv` stores parent regmap and input device. `rt5120_pwrkey_handler()` reads `RT5120_REG_INTSTAT` and reports `KEY_POWER` pressed when `RT5120_PWRKEYSTAT_MASK` is clear. `rt5120_pwrkey_probe()` obtains the regmap, named IRQs `pwrkey-press` and `pwrkey-release`, allocates input, registers it, and requests both threaded IRQs.

## Control Flow
Probe allocates state, fetches parent regmap, resolves named IRQs, registers an I2C-bus input device, and requests both IRQs with the same threaded handler. On interrupt, the handler reads status, reports the inverted status bit, and syncs.

## State and Persistence Behavior
Only the regmap pointer and input device are persistent. The key state is read from hardware on every IRQ and stored in input core. No register writes are performed.

## Dependencies and Integration Points
It depends on RT5120 MFD regmap setup, named platform IRQs, OF compatible `richtek,rt5120-pwrkey`, input core, and threaded IRQ handling.

## Risks and Edge Cases
If `regmap_read()` fails, the handler returns `IRQ_NONE`, which may interact badly with a shared/threaded interrupt line. Registering the input device before requesting IRQs can expose a device briefly without event source. No wakeup handling is configured. The status bit polarity must match the PMIC specification.

## Test Signals
Test press/release IRQs, regmap read errors, named IRQ absence, input registration failure, status polarity, OF matching, and suspend/wakeup behavior supplied by parent PMIC code.
