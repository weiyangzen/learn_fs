# sources/distributed-fs/ceph-client/sound/soc/intel/boards/ehl_rt5660.c

Purpose: ASoC machine driver for Elkhart Lake systems with an RT5660 codec, PCH DMIC capture links, and up to four iDisp HDMI playback back ends.

Important APIs, types, and functions: `struct sof_card_private` tracks HDMI PCM entries and whether the iDisp codec is present. `struct sof_hdmi_pcm` records a codec DAI and PCM device id for late HDMI control creation. `hdmi_init()` appends HDMI runtime information to the list. `card_late_probe()` calls `hda_dsp_hdmi_build_controls()` when the HDA HDMI codec exists. `rt5660_hw_params()` programs RT5660 sysclk to PLL1 and derives PLL input from BCLK at 50fs. `hdmi_link_init()` switches HDMI codec components to `snd_soc_dummy_dlc` when ACPI `codec_mask` lacks `IDISP_CODEC_MASK`.

Control flow and integration: The static DAI-link table defines one SSP0 RT5660 back end, two DMIC capture BEs, and four iDisp BEs. Probe allocates private state, fixes platform component names from `mach->mach_params.platform`, rewrites HDMI links to dummy codecs if display audio is unavailable, and registers the card with normal ASoC PM ops.

State and persistence: Runtime state is a devm-managed HDMI list and an `idisp_codec` boolean. The card and link arrays are static and are modified in place for dummy HDMI codec fallback. There is no persisted state.

Dependencies: ASoC core, RT5660 codec driver, HDA DSP HDMI helper namespace, ACPI machine parameters, and the SOF/HDA platform component named from machine data.

Risks: `card_late_probe()` returns `-ENOENT` if the HDMI list is empty, so topology/link mismatches can prevent normal late-probe completion. The HDMI link loop uses fixed index constants and depends on the static table order. Test signals include card registration with and without iDisp codec support, HDMI mixer controls, DMIC capture, RT5660 playback/capture clock setup, and absence of dummy-codec topology failures.
