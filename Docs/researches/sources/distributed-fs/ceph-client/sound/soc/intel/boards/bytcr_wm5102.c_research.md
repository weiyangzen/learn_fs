# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_wm5102.c

## Purpose
This machine driver supports Baytrail/Cherrytrail boards with a Wolfson/Cirrus WM5102 codec. It handles FLL/sysclk setup, SSP0 versus SSP2 routing, speaker VDD GPIO control, jack detection, and board-specific input/output maps.

## Important APIs, Types, and Functions
`struct byt_wm5102_private` stores headset jack, MCLK, speaker-VDD GPIO, and selected MCLK frequency. Quirk fields select internal/headset mic input map, speaker output map, SSP2 use, and 19.2 MHz MCLK. `byt_wm5102_prepare_and_enable_pll1()` resets/configures WM5102 FLL1, sets component sysclk from FLL1, and sets DAI sysclk. `platform_clock_control()` enables MCLK/FLL on DAPM power-up and disables FLL/MCLK on power-down. `byt_wm5102_spkvdd_power_event()` toggles speaker supply GPIO. `byt_wm5102_init()` adds quirk-selected DAPM routes, sets MCLK rate, creates an Arizona jack with headset, lineout, and four button bits, and binds jack detection.

## Control Flow and Integration
Probe gets `pmc_plt_clk_3`, finds the SPI codec device by ACPI name or fallback `spi-wm5102`, requests `wlf,spkvdd-ena` from the codec device, applies Cherrytrail defaults when `soc_intel_is_cht()`, applies module quirk override, builds component strings, fixes platform names, optionally switches the BE CPU DAI to `ssp2-port`, selects SOF/legacy names and PM ops, registers the card, and releases the speaker GPIO on error/remove.

## State, Persistence, and Dependencies
State includes global `quirk`, mutable DAI CPU name, card component string, MCLK frequency, speaker GPIO, and jack binding. Dependencies include WM5102/Arizona codec APIs, SPI bus device discovery, ACPI machine data, GPIO lookup provided by the Arizona SPI MFD driver, common clock, Atom SST DPCM, and SOF parent detection.

## Risks and Test Signals
Risks include probe deferral when the SPI codec or GPIO lookup is not ready, global quirk mutation, keeping the DAI link name `SSP2-Codec` even for SSP0 because SOF topology expects it, and FLL/sysclk mistakes across sample-rate families. Test signals include speaker VDD transitions, headset/lineout jack events, 48 kHz FE constraints, SSP0 16-bit or SSP2 24-bit BE format, correct component string maps, and no GPIO leaks after failed registration or remove.
