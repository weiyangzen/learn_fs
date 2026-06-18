# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8622.c

## Purpose

This driver supports Parade PS8622/PS8625 eDP-to-LVDS bridge chips. It performs strict power/reset/sleep sequencing, writes a large fixed configuration over page-offset I2C addressing, attaches a downstream panel bridge, and optionally exposes the chip's internal PWM backlight.

## Important APIs, Types, And Functions

`struct ps8622_bridge` stores the I2C client, DRM bridge, panel bridge, optional 1.2 V regulator, optional backlight device, sleep/reset GPIOs, max/current DP lane counts, and enabled flag. `ps8622_set()` writes one register to `client->addr + page`. `ps8622_send_config()` programs HPD low/high, analog tuning, DPCD fields, lane counts, PWM mode/brightness, LVDS output mapping, spread spectrum, and logic/clock settings.

Bridge callbacks are `ps8622_pre_enable()`, `ps8622_disable()`, `ps8622_post_disable()`, and `ps8622_attach()`. Backlight updates use `ps8622_backlight_update()`.

## Control Flow

Probe gets the downstream panel bridge from port 0, optional `vdd12`, required sleep/reset GPIOs, determines max lane count from I2C ID, reads optional `lane-count`, registers a backlight unless `use-external-pwm` is set, sets bridge type/of_node, adds the bridge, and stores client data.

Pre-enable asserts reset low, enables the regulator, exits sleep, waits within datasheet T1/T2 bounds, deasserts reset, waits 20 ms, sends configuration, and marks enabled. Disable only waits for panel PWM-off timing. Post-disable enters sleep, disables regulator, waits for rail fall, asserts reset, and waits the power-off interval. Backlight writes register `0x01:0xa7` only when enabled.

## State And Persistence

`enabled` guards repeated sequencing and backlight writes. Backlight brightness persists in `bl->props` and is pushed to hardware during config/update. The chip's page-addressed register state is fully reprogrammed on each pre-enable. Power state is controlled by GPIOs and optional regulator.

## Dependencies And Integration Points

Dependencies include I2C transfer, GPIO, regulators, backlight subsystem, DRM bridge/panel helpers, OF properties, and I2C ID data. It integrates between an eDP source and LVDS panel bridge.

## Risks And Edge Cases

`ps8622_set()` returns boolean-style failure rather than errno and logs with `pr_warn`, so detailed failure context is limited. The fixed configuration is highly board/chip specific, including 6-bit VESA single-channel LVDS and spread-spectrum values. `ps8622_attach()` uses `ps8622->bridge.encoder` rather than the `encoder` argument, which relies on bridge core state being set. Backlight registration is non-devm and must be unregistered on remove. Internal PWM updates fail while disabled.

## Test Signals

Test PS8622 and PS8625 IDs, lane-count clamping, external versus internal PWM, backlight brightness update while enabled/disabled, regulator absent/present, exact power/reset timing with scope or logs, I2C write failure during config, panel attach, repeated enable/disable cycles, and remove cleanup.
