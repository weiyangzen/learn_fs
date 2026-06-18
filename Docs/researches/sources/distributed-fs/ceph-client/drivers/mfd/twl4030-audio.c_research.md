# sources/distributed-fs/ceph-client/drivers/mfd/twl4030-audio.c

## Purpose
`twl4030-audio.c` is an MFD child driver for the TWL4030 audio/voice block. It configures the audio PLL input frequency, tracks shared audio resources with reference counts, exports resource enable/disable and MCLK query helpers, and creates codec and/or vibra child devices based on platform data or device tree.

## Important APIs, Types, And Functions
State is `struct twl4030_audio`, containing `audio_mclk`, a mutex, resource descriptors for power/APLL, and two child cells. A global `twl4030_audio_dev` lets exported helpers find state. Exported APIs are `twl4030_audio_enable_resource()`, `twl4030_audio_disable_resource()`, and `twl4030_audio_get_mclk()`. Helpers include `twl4030_audio_set_resource()`, `twl4030_audio_get_resource()`, `twl4030_audio_has_codec()`, `twl4030_audio_has_vibra()`, and probe/remove.

## Control Flow
Probe requires platform data or an OF node, allocates state, reads the TWL HFCLK rate via `twl_get_hfclk_rate()`, maps it to an APLL input-frequency value, writes `TWL4030_REG_APLL_CTL`, configures resource register/mask metadata for codec power and APLL, conditionally creates `twl4030-codec` and `twl4030-vibra` cells, stores global device state, and adds children. Resource enable increments a reference count and only sets the hardware bit on the first request. Resource disable decrements and only clears the bit when the count reaches zero.

## State, Persistence, And Dependencies
Resource request counts are in-memory state protected by a mutex. Hardware state is the codec power bit, APLL enable bit, and APLL input-frequency register. Dependencies include the TWL core exported I2C helpers, `twl_get_hfclk_rate()`, MFD core, OF child/property parsing, and `linux/mfd/twl4030-audio.h`.

## Integration Points
Codec and vibra children use the exported resource helpers to coordinate shared power/APLL resources. Device tree can add a `codec` child node and `ti,enable-vibra` property. Platform data can pass codec/vibra sub-platform data into child cells.

## Risks
The exported helpers assume `twl4030_audio_dev` is non-NULL; calls before probe or after remove can dereference NULL. TWL I2C read/write return values are ignored inside resource get/set and APLL setup. Probe stores global state before `mfd_add_devices()` and clears it only if child creation fails. Underflow protection on disable returns `-EPERM`, but unbalanced users can still disturb shared resource availability.

## Test Signals
Test all accepted MCLK rates and invalid rate rejection, codec/vibra child creation from platform data and OF, resource reference counting with multiple users, invalid resource IDs, disable without enable, I2C failure injection around register writes, remove cleanup, and exported helper calls after child driver bind/unbind.
