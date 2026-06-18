# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp21.h

## Purpose
`lnbp21.h` defines LNBP21 system-register bits and the attach API for the LNBP21 LNB supply driver.

## Important APIs, Types, and Functions
The header documents status and control bits: OLF, OTF, EN, VSEL, LLC, TEN, ISEL, and PCL. `lnbp21_attach()` accepts an existing frontend, I2C adapter, and override set/clear masks under `CONFIG_DVB_LNBP21`, with a warning stub otherwise.

## Control Flow
Board drivers call attach to install SEC voltage/tone callbacks. The implementation writes a default config byte, applies override masks on every operation, and probes by powering off.

## State and Persistence
No state is declared here. Bit definitions describe the single volatile system register cached by `lnbp21.c`.

## Dependencies and Integration Points
It depends on DVB frontend types and is used by satellite board drivers that need LNB power control.

## Risks and Edge Cases
The API exposes raw override masks instead of a structured config, so caller mistakes directly alter every hardware write. Read-only fault flags are defined but not consumed by the implementation.

## Test Signals
Build enabled/disabled paths, confirm voltage/tone behavior with override masks, and validate the default current-limit selection on target boards.
