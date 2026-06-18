# sources/distributed-fs/ceph-client/drivers/leds/leds-aw200xx.c

## Purpose
Implements Awinic AW20036/AW20054/AW20072/AW20108 LED matrix controllers. It registers firmware-described channels as LED class devices, supports fade brightness plus a per-LED `dim` sysfs control, and computes global current limits from display scan duty.

## Important APIs, Types, And Functions
`struct aw200xx_chipdef` describes channel count and matrix geometry. `struct aw200xx` stores chip definition, client, regmap, mutex, display rows, optional HW enable GPIO, and flexible LED array. `struct aw200xx_led` stores classdev, chip, dim override, and channel number.

Key functions are `dim_show/store`, `aw200xx_brightness_set`, current conversion helpers, `aw200xx_set_imax`, `aw200xx_chip_reset/init/check`, `aw200xx_probe_get_display_rows`, `aw200xx_probe_fw`, and `aw200xx_probe`.

## Control Flow
Probe selects chip definition from OF match data, validates child count, initializes paged regmap, enables optional HWEN GPIO, checks chip ID, initializes mutex, resets the chip, parses firmware children, sets global current, and initializes display size/sleep/global all-on registers.

Firmware parsing computes display rows from highest valid channel, derives allowed per-LED current range from duty ratio, validates each child `reg` and optional `led-max-microamp`, registers a classdev with max brightness 255 and `dim` group, and finally programs the minimum requested current or a default.

Brightness writes page-4 DIM and FADE registers. If `dim` is `auto`, DIM is derived from fade brightness; otherwise a fixed DIM value is used while brightness controls FADE.

## State And Persistence
Per-LED persistent state is `dim` (`-1` for auto) and classdev brightness. Chip-level state includes display rows and selected global current. Regmap uses ranges for paged addressing, MAPLE cache, and disabled internal locking; the driver mutex serializes LED operations.

## Dependencies And Integration Points
Depends on I2C, regmap range windows, optional GPIO, firmware child nodes, LED class, and per-chip compatible strings `awinic,aw20036`, `aw20054`, `aw20072`, and `aw20108`.

## Risks
Current calculation depends on display rows inferred from child channel indexes; invalid or sparse firmware can change duty/current limits. Regmap locking is disabled, making the driver mutex important. Page/range definitions must match hardware or writes can hit wrong pages. `dim_store` accepts `auto` or 0-63, but does not update hardware when switching back to auto until brightness changes.

## Test Signals
Verify all compatible variants, channel count bounds, chip ID check, display row inference, `led-max-microamp` validation, `dim` sysfs behavior, brightness-to-DIM/FADE writes, current register programming, reset action, and HWEN disable on cleanup.
