# sources/distributed-fs/ceph-client/drivers/video/backlight/mt6370-backlight.c

## Purpose
This platform child driver controls the MediaTek/Richtek MT6370/MT6371/MT6372 backlight block through the parent regmap.

## Important APIs, Types, and Functions
`struct mt6370_priv` stores brightness bit masks/shifts, default max brightness, backlight, device, optional enable GPIO, and parent regmap. `mt6370_check_vendor_info()` reads hardware vendor bits and verifies they match the compatible string, then selects 11-bit common or 14-bit MT6372 brightness encoding. `mt6370_init_backlight_properties()` parses PWM hysteresis, OVP, OCP, max/default brightness, exponential mode, and channel-use properties. `mt6370_bl_update_status()` writes split brightness bytes, drives optional GPIO, and toggles enable bit.

## Control Flow
Probe gets the parent regmap, validates vendor info, obtains optional enable GPIO, initializes hardware properties and backlight props, registers the backlight, applies brightness, and stores driver data. Remove sets brightness zero and updates hardware.

## State and Persistence
Encoding parameters are derived once at probe from hardware and match data. Backlight properties and hardware configuration are volatile runtime state held in memory and registers.

## Dependencies and Integration Points
The driver depends on platform MFD instantiation, parent regmap, GPIO, device properties, bitfield helpers, and the backlight core. It matches `mediatek,mt6370-backlight` and `mediatek,mt6372-backlight`.

## Risks
A wrong compatible string intentionally fails probe after reading hardware vendor info. `mediatek,bled-channel-use` is mandatory and must be 1-15. Register update masks use `val` as both mask and value for some optional fields, so properties that are absent leave those bits untouched rather than cleared.

## Test Signals
Test common vs MT6372 vendor detection, wrong compatible rejection, mandatory channel property, max/default clamping, exponential scale, OVP/OCP/PWM property mapping, GPIO enable, brightness readback, and remove zeroing.
