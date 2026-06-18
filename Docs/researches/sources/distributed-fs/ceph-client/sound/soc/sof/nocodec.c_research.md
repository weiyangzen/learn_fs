# sources/distributed-fs/ceph-client/sound/soc/sof/nocodec.c

Purpose: Implements the dummy/no-codec ASoC machine driver used when SOF runs without a real codec-specific machine driver.

Important APIs/state: Static `sof_nocodec_card` is named `nocodec` with topology shortname `sof-nocodec`. `sof_nocodec_bes_setup()` builds one BE DAI link per SOF DAI driver using dummy codec, parent platform name, DAI IDs, playback/capture-only flags, and `sof_pcm_dai_link_fixup`. `sof_nocodec_probe()` receives `snd_soc_acpi_mach` platform data, creates links from `mach_params.dai_drivers`, and registers the card.

Control flow: Probe sets card device and marks topology shortname created, allocates BE links and two link components per DAI, fills CPU/platform/codec references, then registers with devm ASoC card registration. The platform driver is named `sof-nocodec`.

Dependencies and integration: Depends on SOF core creating a platform device with machine params, ASoC dummy codec, SOF PCM fixup, and `snd_soc_pm_ops`.

State and persistence: Link allocations are devm-managed. The static card is shared by module instance, so probe assumes one active device.

Risks: Static `snd_soc_card` can be problematic if multiple no-codec devices probe. DAI link names are generated `NoCodec-%d`; topology must match expected DAIs. No FE links are created here; this only supplies BEs for SOF topology integration.

Test signals: No-codec boot with each platform DAI set, playback-only/capture-only link flags, topology loading with `sof-nocodec`, and multi-device probe behavior.
