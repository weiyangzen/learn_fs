# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.h

## Purpose
Declares b43legacy radio defaults, TX antenna constants, radio interference mode constants, and public RF/NRSSI/channel/power APIs.

## Important APIs, Types, and Functions
Defines `B43legacy_RADIO_DEFAULT_CHANNEL_BG`, `B43legacy_RADIO_TXANTENNA_*`, and `B43legacy_RADIO_INTERFMODE_*`. Exposes radio locking, 16-bit radio access, radio 2050 init, on/off, channel selection, TX-power setters/defaults, TX antenna selection, TSSI clearing, ACI scan/detect, interference mitigation, NRSSI helpers, and `b43legacy_radio_calibrationvalue()`.

## Control Flow, State, and Persistence
The header has no state. Runtime state is in `struct b43legacy_phy`, including current channel, radio-on flag, attenuation values, NRSSI tables, interference mode, and radio-off context.

## Dependencies and Integration Points
Includes `b43legacy.h` and is used by `phy.c`, `radio.c`, `rfkill.c`, `sysfs.c`, and TX-power/channel paths.

## Risks and Test Signals
Incorrect constants or prototypes affect all RF programming. Test by building b43legacy and exercising channel change, rfkill, interference mitigation, NRSSI calibration, and TX power paths.
