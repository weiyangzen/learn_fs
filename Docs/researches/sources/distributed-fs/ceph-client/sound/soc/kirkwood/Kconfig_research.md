# sources/distributed-fs/ceph-client/sound/soc/kirkwood/Kconfig

## Purpose
Defines build options for Marvell Kirkwood/Dove/MVEBU audio and the Armada 370 DB machine driver.

## Important APIs, Types, And Functions
`SND_KIRKWOOD_SOC` enables the core I2S/SPDIF controller support for `ARCH_DOVE`, `ARCH_MVEBU`, or `COMPILE_TEST`. `SND_KIRKWOOD_SOC_ARMADA370_DB` depends on the core driver, MVEBU/COMPILE_TEST, and I2C, selecting CS42L51 and SPDIF codec support.

## Control Flow, State, And Persistence
No runtime state exists. The symbols select which controller and board glue objects are built.

## Dependencies And Integration Points
Matches the Kirkwood Makefile and the `armada-370-db.c` codec requirements.

## Risks And Test Signals
Risks are missing dependencies for OF, clocks, or MBUS APIs under COMPILE_TEST. Test signals are compile coverage for both core and board symbols.
