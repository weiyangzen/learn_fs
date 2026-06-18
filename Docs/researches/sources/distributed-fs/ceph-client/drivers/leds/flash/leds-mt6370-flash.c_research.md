# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6370-flash.c

## Purpose
This platform driver supports the MT6370 PMIC flashlight block. It exposes one or two flash LED class devices, including a joint-output mode when a firmware LED uses both flash channels.

## Important APIs, Types, and Functions
`struct mt6370_priv` stores regmap, mutex, torch/strobe usage masks, active channel bitmap, count, and per-LED array. `struct mt6370_led` stores the flash class device, V4L2 handle, parent private pointer, and LED number. LED operations are `mt6370_torch_brightness_set()`, `mt6370_flash_brightness_set()`, `_mt6370_flash_brightness_set()`, `mt6370_strobe_set()`, `mt6370_strobe_get()`, `mt6370_timeout_set()`, and `mt6370_fault_get()`.

## Control Flow
Probe counts child nodes, gets the parent regmap, and parses each child. `led-sources` selects channel 0, channel 1, or joint mode with both channels. Current and timeout properties are clamped to hardware ranges, minimum strobe current is preprogrammed, class callbacks are installed, and each flash LED is registered with optional V4L2 flash support. Torch and strobe setters split current across both channels for joint mode and program enable bits in `MT6370_REG_FLEDEN`.

## State and Persistence
State is volatile and mutex-protected. `leds_active` prevents duplicate channel allocation. `fled_torch_used` and `fled_strobe_used` track active modes and enforce mutual exclusion. Devm actions release V4L2 flash handles. No hardware state is persisted across removal.

## Dependencies and Integration Points
The driver depends on the MT6370 parent regmap, LED flash class, firmware `led-sources`, `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us` properties, and optional V4L2 flash class. It binds `mediatek,mt6370-flashlight`.

## Risks and Edge Cases
Joint mode uses synthetic `led_no == 2`, so all bit operations involving `BIT(led_no)` must remain separate from hardware channel masks. Torch and strobe share control logic and intentionally reject concurrent use. The timeout setter lacks explicit locking while most related paths use the mutex. Fault reads use raw 16-bit status and must match regmap endianness. There is no remove callback because devm manages class devices and V4L2 release is registered as a devm action.

## Test Signals
Test one-channel and two-channel `led-sources`, duplicate channel rejection, current splitting in joint mode, torch/strobe mutual exclusion, ramp delays on strobe transitions, timeout register values, fault mapping, and V4L2 external strobe. Remove/unbind should release V4L2 subdevices through the devm action.
