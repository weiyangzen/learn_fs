# sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_max98090_ti.c

## Purpose
This Cherrytrail/Braswell machine driver supports MAX98090 codec boards and optional TI TS3A227E headset detection. It manages platform MCLK behavior, headset GPIO fallback, TI jack notifier behavior, SSP2 DPCM routing, and Chromebook clock quirks.

## Important APIs, Types, and Functions
`struct cht_mc_private` stores MCLK, jack state, TS3A227E presence, and quirk flags. `platform_clock_control()` enables or disables MCLK for normal boards but does nothing for `QUIRK_PMC_PLT_CLK_0` boards. `cht_aif1_hw_params()` sets MAX98090 sysclk to 19.2 MHz. `cht_ti_jack_event()` force-enables or disables TS3A227E `SHDN` and `MICBIAS` pins on microphone events. `cht_codec_init()` either registers the TI notifier after aux-device jack creation or creates a GPIO-backed headset jack. `cht_max98090_headset_init()` creates a four-button jack and calls `ts3a227e_enable_jack_detect()`.

## Control Flow and Integration
Probe allocates private state, applies DMI quirks for Chromebook models using `pmc_plt_clk_0`, detects whether `104C227E` exists, disables aux-device registration and installs ACPI GPIO mappings when absent, fixes platform names, gets the selected MCLK, optionally enables clk0 permanently to avoid MAX98090 PLL unlocks, applies SOF naming/PM ops, and registers the card. Remove disables the always-on clk0 quirk clock.

## State, Persistence, and Dependencies
State includes MCLK enable state, jack object, aux-device presence, and quirk bit. Persistent hardware effects include MCLK rate/enable behavior, MAX98090 sysclk, TI jack-detect registration, and DAPM MICBIAS/SHDN pin state. Dependencies include MAX98090, TS3A227E, ACPI GPIO mapping, DMI, common clock, Atom SST DPCM links, and SOF parent detection.

## Risks and Test Signals
Risks include wrong clock choice for Chromebook variants, aux-device removal changing jack creation order, leaving `pmc_plt_clk_0` enabled on probe error paths, and GPIO-only jack detection being degraded but non-fatal. Test signals include MAX98090 sysclk programming, four-button TI headset events when present, fallback HP/mic GPIO events when TI absent, no PLL unlock messages on clk0 boards, and 48 kHz SSP2 playback/capture.
