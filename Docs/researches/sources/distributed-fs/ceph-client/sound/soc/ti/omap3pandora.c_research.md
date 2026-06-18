<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap3pandora.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap3pandora.c

## Purpose
Legacy ASoC machine driver for the OMAP3 Pandora handheld. It connects an external PCM1773 playback DAC and TWL4030 capture paths through two McBSP links, with board-specific DAC regulator, DAC power GPIO, headphone amplifier GPIO, and DAPM routing.

## APIs, Types, and Functions
Important functions are `omap3pandora_hw_params()`, `omap3pandora_dac_event()`, `omap3pandora_hp_event()`, `omap3pandora_out_init()`, `omap3pandora_in_init()`, and module init/exit. Static card data defines two links, DAPM widgets, and routes for PCM DAC output and TWL4030 inputs.

## Control Flow, State, and Persistence
Module init checks `machine_is_omap3_pandora()`, creates a `soc-audio` platform device, gets `dac` and `amp` GPIOs, and obtains the `vcc` regulator. `hw_params` sets codec sysclk to 26 MHz, McBSP sysclk to external CLKS at 256 x rate, and McBSP divider to 8. DAPM events power the PCM1773 regulator and /PD GPIO with required delays, and toggle headphone amp GPIO. Link init disables unused TWL4030 pins.

## Dependencies and Integration
Depends on legacy machine ID matching, OMAP McBSP clock IDs, TWL4030 codec DAI, regulator framework, GPIO descriptors, and platform-device ASoC registration. McBSP2 handles playback; McBSP4 handles line/mic input.

## Risks and Test Signals
Risks include legacy non-DT binding, static regulator/GPIO globals, external clock assumptions, no cleanup for GPIO-managed state beyond platform device lifetime, and typographical route comments. Test signals are Pandora-only load, DAC regulator sequencing with 1 ms delays, headphone amp DAPM toggle, playback and capture links, McBSP external clock/divider setup across sample rates, and disabled unused TWL4030 pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap3pandora.c -->
