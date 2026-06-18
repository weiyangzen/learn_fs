# sources/distributed-fs/ceph-client/drivers/clk/meson/axg-audio.c

Purpose: `axg-audio.c` implements the Amlogic AXG/G12A/SM1 audio clock controller. It declares audio bus gates, master clocks, sample clocks, TDM input/output clocks, SPDIF/PDM clocks, pad clock selectors, and newer SM1 eARC/sysclk additions, then registers the selected SoC variant through a custom platform probe.

Important APIs and types: macro families `AUD_GATE`, `AUD_MUX`, `AUD_DIV`, `AUD_PCLK_GATE`, `AUD_SCLK_DIV`, `AUD_TRIPHASE`, `AUD_PHASE`, `AUD_SCLK_WS`, and `AUD_TDM_PAD_CTRL` generate `struct clk_regmap` descriptors. `struct audioclk_data` holds the variant `meson_clk_hw_data`, optional auxiliary reset driver name, and max register. The probe is `axg_audio_clkc_probe()`.

Control flow: the driver selects variant data from OF compatible strings `amlogic,axg-audio-clkc`, `amlogic,g12a-audio-clkc`, and `amlogic,sm1-audio-clkc`. Probe maps MMIO, initializes regmap, enables mandatory `pclk`, resets the device, registers all non-input clock hardware from the variant array, adds the OF clock provider, and optionally creates an auxiliary reset device (`rst-g12a` or `rst-sm1`). Static clock arrays are variant-specific: AXG has the base set, G12A adds SPDIFOUT_B and pad controls, and SM1 changes register offsets, adds `aud_top` sysclk selection, more gates, and eARC clocks.

State and persistence: state is in audio clock registers and registered CCF objects. Input clocks are intentionally skipped at runtime by starting registration at `AUD_CLKID_DDR_ARB`; those input slots are expected from DT parent clocks. Reset side effects happen through `device_reset()` and optional auxiliary reset device creation.

Dependencies and integration points: the driver depends on auxiliary bus, regmap MMIO, reset APIs, Meson clock helpers, phase and sclk divider helpers, and DT binding IDs from `axg-audio-clkc.h`. It integrates with audio subsystem consumers that request TDM, SPDIF, PDM, FRDDR/TODDR, resample, loopback, eARC, and pad clocks.

Risks: this file has many generated descriptors with repeated names and SoC-specific register offsets, so variant arrays must point to the correct descriptor set. Probe requires `pclk`; missing clock or reset resources fail the whole controller. The arrays are sparse and input clocks are populated externally, so binding ID drift or missing parents can break audio graph setup. `CLK_SET_RATE_NO_REPARENT`, phase controls, and duty-cycle flags are important for audio signal integrity.

Test signals: compile all three variants, boot with representative AXG/G12A/SM1 DTs, inspect `clk_summary` for audio IDs, and run audio playback/capture through TDM, SPDIF, and PDM. Verify master clock rates, LRCLK/SCLK phase controls, pad muxes, reset auxiliary device creation, and SM1 eARC clocks where hardware is available.
