# sources/distributed-fs/ceph-client/drivers/video/backlight/lm3630a_bl.c

## Purpose
This I2C/regmap driver controls TI LM3630A dual-bank backlight hardware, with optional PWM and interrupt handling.

## Important APIs, Types, and Functions
The driver uses `struct lm3630a_chip` for device, regmap, platform data, enable GPIO, PWM state, IRQ/workqueue state, and backlight devices. Register helpers wrap regmap access. Backlight update callbacks write bank brightness registers and, when configured, drive a PWM device instead. Firmware parsing validates child banks, `led-sources`, labels, defaults, max brightness, and linear mapping. Interrupt handling records fault bits from the chip.

## Control Flow
Probe checks I2C support, initializes regmap, creates or reads platform data, parses firmware if needed, gets optional enable GPIO high, initializes the chip registers, registers one or two backlight devices based on bank controls, optionally obtains a PWM named `lm3630a-pwm`, and configures IRQ handling if present. Remove writes zero to both brightness registers and tears down IRQ/workqueue resources.

## State and Persistence
Runtime state includes platform configuration, brightness/core properties, PWM state, and interrupt worker state. Hardware registers persist until reset or removal cleanup writes zero.

## Dependencies and Integration Points
The driver depends on I2C, regmap, GPIO, PWM, fwnode APIs, optional IRQ/workqueue infrastructure, and the backlight core. It matches `ti,lm3630a`.

## Risks
Firmware parsing is strict about valid bank/sink combinations; invalid board descriptions fail probe. PWM mode depends on a named PWM and must be coordinated with brightness-register behavior. IRQ cleanup is manual and must match successful interrupt setup. As with many LED drivers, incorrect max/default brightness values can overdrive user expectations even if clamped by code.

## Test Signals
Test DT child parsing for bank A/B, combined LEDB-on-A mode, linear mapping, default/max clamping, enable GPIO, PWM mode acquisition and duty updates, IRQ setup/fault handling, remove zeroing both banks, and regmap failures.
