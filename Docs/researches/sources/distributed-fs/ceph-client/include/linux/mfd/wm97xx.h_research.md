# sources/distributed-fs/ceph-client/include/linux/mfd/wm97xx.h

## Purpose
Defines the small MFD platform-data contract for WM97xx AC97 companion devices. It lets parent/board code pass an AC97 codec handle, regmap, and optional battery platform data to child drivers.

## Important APIs/Types
`struct wm97xx_platform_data` carries `struct snd_ac97 *ac97`, `struct regmap *regmap`, and `struct wm97xx_batt_pdata *batt_pdata`. The dependent types are forward declared to keep this interface lightweight.

## Control Flow
No executable flow is defined. Parent code populates the structure before device registration; consumers use the pointers during probe and runtime operations.

## State And Persistence
All state is externally owned pointer state. The header does not encode ownership, reference counts, or lifetime.

## Dependencies And Integration Points
Integrates WM97xx MFD child drivers with AC97, regmap, and battery support without forcing broad includes.

## Risks
The main risks are stale pointers, missing optional data, and consumers assuming ownership that is not specified here.

## Test Signals
Probe success for WM97xx children, valid AC97/regmap access, and battery child registration when `batt_pdata` is present.
