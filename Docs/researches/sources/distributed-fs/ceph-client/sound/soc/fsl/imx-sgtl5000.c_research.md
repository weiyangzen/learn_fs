# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-sgtl5000.c

## Purpose
Machine driver for i.MX boards using an SGTL5000 codec over an SSI interface. It configures AUDMUX, codec clocking, a single I2S link, DAPM widgets/routes, and card registration.

## APIs, Types, and Functions
`struct imx_sgtl5000_data` stores the card, DAI link, codec clock, and clock frequency. `imx_sgtl5000_dai_init()` programs codec sysclk using the codec clock rate. `imx_sgtl5000_probe()` reads mux ports, configures AUDMUX, resolves SSI/codec devices, gets the codec clock, builds link components, parses card metadata, and registers the card. `imx_sgtl5000_remove()` releases the codec clock.

## Control Flow, State, and Persistence
Probe converts one-based DT mux port numbers to zero-based AUDMUX indexes and programs symmetric internal/external routing. It then defers until SSI and I2C codec devices exist, obtains the codec clock, sets the link to I2S normal-bitclock/frame with codec as clock provider, and stores private data in the card. Runtime init passes the clock frequency to SGTL5000. Persistent state is card data plus the acquired `clk`.

## Dependencies and Integration
Depends on `imx-audmux.h`, OF phandles, I2C device lookup, clocks, ASoC DAPM, and the SGTL5000 codec DAI named `sgtl5000`. Integrates with `fsl,imx-audio-sgtl5000`, `model`, `audio-routing`, and SSI CPU DAIs.

## Risks and Test Signals
Risks include no explicit mux-port upper-bound validation here, manual `clk_get`/`clk_put` instead of devm clock management, hard-coded codec DAI name, and static clock-frequency use if the codec clock changes. Test signals are probe defer until codec/SSI availability, AUDMUX routing, sysclk programming on DAI init, successful playback/capture, and balanced clock put on remove/error.
