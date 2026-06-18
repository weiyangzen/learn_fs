# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6360.c

## Purpose
This platform driver exposes the MediaTek MT6360 PMIC LED block. It supports individual current-sink LEDs, a virtual multicolor RGB LED, and two flash LEDs with torch, strobe, timeout, fault, and optional V4L2 flash support.

## Important APIs, Types, and Functions
`struct mt6360_priv` stores the parent regmap, lock, active LED bitmaps, torch/strobe usage masks, and a flexible array of `struct mt6360_led`. `struct mt6360_led` is a union over plain LED, multicolor LED, and flash LED class devices. Brightness and flash operations include `mt6360_isnk_brightness_set()`, `mt6360_mc_brightness_set()`, `mt6360_torch_brightness_set()`, `mt6360_strobe_set()`, `mt6360_strobe_get()`, `mt6360_timeout_set()`, and `mt6360_fault_get()`.

## Control Flow
Probe counts child nodes, allocates private storage, gets the parent regmap, then iterates children. Child `color` selects virtual multicolor versus normal `reg`-indexed LED. Current-sink children initialize max brightness and default state, then register plain or multicolor class devices. Flash children initialize torch and strobe limits, preprogram minimum strobe current to avoid current spikes, initialize default torch state, register LED flash devices, and optionally create V4L2 flash subdevices.

## State and Persistence
Runtime state is held in bitmaps: `leds_active` prevents duplicate child use, `fled_torch_used` and `fled_strobe_used` enforce mutual exclusion between torch and strobe paths. Default state may keep hardware brightness at probe, but no state persists beyond the PMIC binding. V4L2 handles are explicitly released on remove or probe failure.

## Dependencies and Integration Points
The driver depends on a parent regmap from the MT6360 MFD, LED class, multicolor LED class, LED flash class, firmware LED properties, and optional V4L2 flash class. Flash fault reporting reads charger and FLED status registers via regmap/raw read.

## Risks and Edge Cases
The hardware has one flash control logic block, so torch and strobe are mutually exclusive and return `-EBUSY` if used concurrently. Multicolor child parsing marks component channels active; malformed child lists can partially mutate `leds_active` before returning errors. The code uses raw 16-bit reads from `MT6360_REG_FLEDSTAT1`, so endianness/regmap bus behavior matters. Probe failure after devm LED registration relies on devm cleanup plus explicit V4L2 release.

## Test Signals
Test current-sink LEDs with `default-state` off/on/keep, RGB multicolor registration with two or three channels, flash torch/strobe mutual exclusion, timeout programming, fault bits for input voltage, timeout, short, and undervoltage, V4L2 external strobe, and duplicate `reg`/channel rejection.
