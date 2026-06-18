# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Kconfig

## Purpose
This Kconfig file defines common support for B2C2 FlexCop DVB devices shared by PCI and USB front-end drivers.

## Important APIs, Types, and Functions
`DVB_B2C2_FLEXCOP` is a tristate depending on `DVB_CORE`, `I2C`, and either PCI or USB FlexCop driver selection. It defaults to `y` when a bus driver is selected and auto-selects many demodulator/tuner/LNB helper drivers under `MEDIA_SUBDRV_AUTOSELECT`. `DVB_B2C2_FLEXCOP_DEBUG` is a bool selected through bus drivers.

## Control Flow
The common FlexCop object is enabled when either bus-specific driver needs it. Auto-selection pulls in possible frontend drivers so runtime probing can try multiple board variants.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
This config drives the common object built from FlexCop core, I2C, SRAM, EEPROM, FE/tuner, misc, and hardware filter code.

## Risks and Test Signals
Configuration coverage should verify all optional frontend attach paths are reachable only when their selected modules are built-in/reachable. Missing auto-selected dependencies lead to skipped attach functions at compile time.
