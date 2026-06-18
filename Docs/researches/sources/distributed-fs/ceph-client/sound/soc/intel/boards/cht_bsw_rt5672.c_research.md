# sources/distributed-fs/ceph-client/sound/soc/intel/boards/cht_bsw_rt5672.c

Purpose: ASoC machine driver for Cherry Trail/Braswell and Bay Trail CR platforms using the Realtek RT5672/RT5670 codec. It registers a DPCM sound card with media/deep-buffer front ends and one SSP codec back end, adapting the back end to SSP0 on Bay Trail CR and SSP2 otherwise.

Important APIs, types, and functions: `struct cht_mc_private` stores the headset jack, ACPI-resolved codec name, PMC platform clock, and SSP0 flag. `platform_clock_control()` is a DAPM supply event callback that enables `pmc_plt_clk_3`, programs the codec PLL from 19.2 MHz MCLK, and falls back to RCCLK when idle so jack detection still works. `cht_codec_init()` adds ACPI GPIO mappings, selects RT5670 ASRC sources, adds SSP-specific routes, creates the headset jack, maps button events, configures jack detection, and normalizes MCLK rate. `cht_codec_fixup()` forces the BE to 48 kHz stereo and 16-bit or 24-bit samples depending on SSP. `snd_cht_mc_probe()` resolves the ACPI codec instance, overrides platform names, selects SOF card naming when applicable, and registers the card.

Control flow and integration: Probe allocates private state, rewrites the static DAI link codec name from ACPI, optionally rewrites the CPU DAI to `ssp0-port`, fixes platform components from `snd_soc_acpi_mach`, binds card drvdata, and registers the card. During runtime DAPM clock events and hw_params set PLL/sysclk, while suspend/resume calls Realtek jack suspend/resume helpers.

State and persistence: State is in devm-managed private data and a static card/DAI-link template that probe mutates. No disk persistence exists. The codec name mutation and static card object mean repeated probes would need care, but this platform driver is normally singleton.

Dependencies: Linux ASoC core, ACPI GPIO mapping, common clock framework, RT5670 codec APIs, SST Atom DPCM names, Intel SoC quirks, and optional SOF parent detection.

Risks: MCLK acquisition is mandatory and returns probe failure. Static DAI-link mutation can be fragile if multiple matching devices ever probe. Jack detection depends on the codec keeping RCCLK when idle. SSP0/SSP2 bit-width differences must match firmware topology. Test signals include successful card registration, DAPM route validation, `aplay/arecord` at 48 kHz, jack/button events across suspend/resume, and no clock/PLL errors in dmesg.
