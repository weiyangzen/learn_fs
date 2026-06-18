# sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6328.c

## Purpose
Implements memory-mapped LED control for Broadcom BCM6328 controllers. It supports up to 24 LEDs, active-low polarity, default-state parsing, two hardware blink intervals, serial LED bus configuration, and optional hardware-controlled link/activity LEDs.

## Important APIs, Types, And Functions
`struct bcm6328_led` stores classdev, MMIO base, shared spinlock, pin, shared blink interval bitmaps/delays, and active-low flag. Important functions are endian-aware read/write helpers, `bcm6328_led_mode`, `bcm6328_led_set`, `bcm6328_blink_set`, `bcm6328_hwled`, `bcm6328_led`, and `bcm6328_leds_probe`.

## Control Flow
Probe maps MMIO, allocates a spinlock and two-entry blink caches, disables hardware control, clears link/activity selectors, configures serial LED options from DT properties, then iterates child nodes. A child with `brcm,hardware-controlled` enables hardware control and programs link/activity source selectors; otherwise it allocates a classdev LED, derives default brightness from `default-state`, programs initial mode, sets callbacks, and registers via devm.

Brightness clears the LED from both blink interval caches and writes ON/OFF mode accounting for active-low. Blink normalizes missing delays to 500 ms, requires equal on/off delay and delay <= 63 * 20 ms, then assigns the LED to one of two shared hardware intervals if free or already using the same delay; otherwise it returns `-EINVAL` so the LED core can use software blink.

## State And Persistence
Shared blink interval state is cached in `blink_leds[2]` and `blink_delay[2]` under the spinlock. Hardware state persists in mode, init, hardware disable, and link/activity selector registers.

## Dependencies And Integration Points
Depends on platform MMIO resources, OF child nodes, LED class, spinlocks, and CPU endian handling. Compatible is `brcm,bcm6328-leds`.

## Risks
Only two hardware blink delays can be active; the fallback path must remain correct. Link/activity selectors are valid only for LEDs 0-7 and same source groups; DT errors become warnings. Bit shift mapping for LEDs 0-7 versus 8-23 is non-obvious and easy to break. Shared registers require spinlock coverage.

## Test Signals
Test default-state off/on/keep, active-low behavior, hardware blink with two matching/different delays, fallback to software blink on unsupported delays, hardware-controlled LEDs with link/activity sources, serial LED DT options, and endian-correct register access.
