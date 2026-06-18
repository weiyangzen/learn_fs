# sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.h

## Purpose
Defines supported TerraTec/terrasoniq device IDs and GPIO/I2C bit assignments consumed by `ews.c`.

## Important APIs, Types, and Functions
`EWS_DEVICE_DESC` describes supported boards. `ICE1712_SUBDEVICE_EWX2496`, `EWS88MT`, `EWS88MT_NEW`, `EWS88D`, `DMX6FIRE`, `PHASE88`, and `TS88` are subvendor IDs used for dispatch. The header declares `snd_ice1712_ews_cards[]`. It defines GPIO bits for EWX24/96 and EWS88 serial data/clock/RW, sensitivity selects, MIDI pins, EWS88 CS8414 rate pins, I2C addresses for CS8404/PCF8574/PCF8575, and DMX6Fire AK4524 chip selects plus PCF9554/CS8427 addresses.

## Control Flow
The header has no executable flow. `ews.c` uses these constants in probe-time subvendor switches, I2C device creation, GPIO bit-bang callbacks, AKM chip select, and ALSA control get/put operations.

## State and Persistence Behavior
The macros describe hardware pin and I2C address contracts. Runtime state is stored externally in `ice->gpio` and `struct ews_spec`; expander outputs persist only as long as the powered device keeps them.

## Dependencies and Integration Points
It integrates with `ice1712.c` model detection and with `snd_ice1712_ews_cards[]` in `ews.c`. The constants are also tied to the generic `ICE1712_GPIO()` helper and ALSA I2C device APIs.

## Risks
Polarity and address mistakes are high impact because they can select the wrong expander, invert sensitivity controls, or break shared serial access to both I2C and AK4524 devices. The same GPIO bit positions are reused across EWX, EWS88, and DMX6Fire layouts with different semantics.

## Test Signals
Compile `ews.c`, force each supported `model=` alias, confirm I2C addresses on a bus analyzer or debug logs, exercise GPIO-backed controls and AKM access, and validate that mixer labels match board hardware.
