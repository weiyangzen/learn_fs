# sources/distributed-fs/ceph-client/drivers/leds/leds-cht-wcove.c

## Purpose
Implements LEDs connected to the Intel Cherry Trail Whiskey Cove PMIC. It exposes charging and indicator LEDs with brightness, hardware blink, breathing pattern support, model-specific default charging triggers, and suspend/resume register preservation.

## Important APIs, Types, And Functions
`struct cht_wc_led` stores classdev, register descriptor, regmap, mutex, and saved registers. `struct cht_wc_leds` contains two LEDs and saved initial LED1 registers. Important callbacks are `cht_wc_leds_brightness_set/get`, `cht_wc_leds_blink_set`, `cht_wc_leds_pattern_set/clear`, register save/restore helpers, probe/remove/shutdown, and PM suspend/resume.

## Control Flow
Probe obtains the parent `intel_soc_pmic`, skips a model where LED1 drives haptics, saves LED1 initial registers, assigns a model-specific charging trigger when known, initializes two classdevs with names `platform::charging` and `platform::indicator`, and registers them. Brightness writes PWM and on/off control bits, disabling hardware blinking when turning off. Blink chooses the closest supported frequency or returns `-EINVAL` for software fallback. For a default charging trigger, blink is translated into slow breathing. Pattern support accepts exactly two-step off/on breathing patterns with supported delta times.

Remove or shutdown disables LEDs and restores initial LED1 registers if LED1 was originally hardware-controlled. Suspend saves all LED registers, disables LEDs, and resume restores saved values.

## State And Persistence
Register snapshots preserve PMIC state across remove/shutdown/suspend. Per-LED mutexes serialize regmap operations. Hardware settings persist because the PMIC is battery-powered, so restoration is part of correctness.

## Dependencies And Integration Points
Depends on `intel_soc_pmic`, PM sleep, regmap, LED class, trigger names for battery chargers, and platform alias `cht_wcove_leds`.

## Risks
Register changes are persistent across reboots/removal on battery-powered PMIC hardware. Model-specific trigger names must match charger drivers. Hardware blink supports only four frequencies; unsupported patterns must fall back cleanly. LED1 may be non-LED hardware on some models and is explicitly skipped.

## Test Signals
Test on supported model IDs, verify default trigger assignment, brightness and PWM writes, blink frequency quantization, breathing pattern acceptance/rejection, suspend/resume restoration, shutdown disable, and initial LED1 hardware-control restoration.
