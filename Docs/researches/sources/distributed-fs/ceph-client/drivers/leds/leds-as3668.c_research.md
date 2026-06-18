# sources/distributed-fs/ceph-client/drivers/leds/leds-as3668.c

## Purpose
Implements the AMS/Osram AS3668 four-channel I2C current LED driver. Each firmware child node maps to one current channel with independent on/off mode bits and current register.

## Important APIs, Types, And Functions
`struct as3668_led` stores a classdev, chip pointer, fwnode, mode bit mask, and current register. `struct as3668` stores the client and four LED slots. Key functions are `as3668_channel_mode_set`, `as3668_brightness_get`, `as3668_brightness_set`, `as3668_dt_init`, `as3668_probe`, and `as3668_remove`.

## Control Flow
Probe reads the chip ID register and rejects nonmatching hardware, allocates state, parses child nodes, then writes all channel modes and currents to off/zero. Child parsing reads `reg`, fills channel-specific mask/register, assigns max brightness 255, get/set callbacks, and registers classdevs with fwnode metadata.

Setting brightness reads the shared mode register, replaces this channel's two-bit mode with on/off, writes the mode register, then writes the channel current register.

## State And Persistence
There is no explicit lock or regmap cache; hardware state is read/written via SMBus byte operations. Per-channel mode/current is stored in AS3668 registers. Remove writes the mode register to zero.

## Dependencies And Integration Points
Depends on I2C SMBus byte access, OF child nodes, LED class, and compatible `ams,as3668`. It uses `uapi/linux/uleds.h` only for LED brightness constants/types.

## Risks
Concurrent brightness writes can race on the shared mode register because there is no mutex around read-modify-write. `as3668_brightness_get` returns an SMBus error as an enum brightness without filtering negative values. Probe initializes hardware after classdev registration, so userspace activity during probe is theoretically possible before final zeroing.

## Test Signals
Verify chip ID rejection, child `reg` validation, four classdev registration, brightness get/set for each current register, shared mode bit preservation under sequential writes, and remove clearing all modes.
