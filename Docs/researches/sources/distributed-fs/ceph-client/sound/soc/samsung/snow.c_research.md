# sources/distributed-fs/ceph-client/sound/soc/samsung/snow.c

## Purpose
Machine driver for Google Snow Exynos boards with MAX98090/MAX98091/MAX98095 and optional HDMI codec support. It parses old and new DT bindings, computes I2S bus clock rates, sets codec MCLK, and registers a single I2S card.

## Important APIs, Types, And Functions
- `struct snow_priv` stores one dynamically filled DAI link and I2S bus clock.
- `snow_card_hw_params()` validates 16/24-bit audio, computes BFS/RFS from rate and width, selects an available PLL rate/prescaler combination, and sets the I2S bus clock.
- `snow_late_probe()` sets codec sysclk to 24 MHz `FIN_PLL_RATE`.
- `snow_probe()` builds the DAI link, supports new child-node DT with `snd_soc_of_get_dai_link_codecs()`, supports legacy `samsung,i2s-controller`/`samsung,audio-codec`, and registers the card.

## Control Flow
Probe allocates private link state, initializes I2S format, tries new DT binding first, obtains codec list and `i2s_opclk0` for new bindings, otherwise falls back to legacy phandles, assigns platform OF node, optionally parses card name, stores drvdata, and registers the card. `hw_params` runs only on new binding links with ops installed. Remove releases OF nodes, codec allocations, and clock.

## State And Persistence
Private DAI link and clock pointer persist for device lifetime. Clock rate is adjusted per stream. Static `snow_snd` card is shared template state.

## Dependencies And Integration Points
Depends on Samsung I2S, DT child-node bindings, MAX9809x/HDMI codec links, common clock framework, and ASoC card parsing helpers.

## Risks And Edge Cases
- Static card template plus dynamic link pointer is not multi-instance safe.
- PLL selection loop tests unsigned difference `(pll_rate[i] - rclk * psr) <= 2`, which can underflow when PLL is lower than target.
- Remove unconditionally calls `snd_soc_of_put_dai_link_codecs()` and `clk_put()` even for legacy path where codec allocation/clock may differ.
- Only selected rates and 16/24-bit widths are supported.

## Test Signals
Probe with legacy and new DT bindings, multi-codec HDMI case, supported/unsupported rate and width tests, I2S clock-rate verification, late-probe codec sysclk setup, and remove-path resource cleanup.
