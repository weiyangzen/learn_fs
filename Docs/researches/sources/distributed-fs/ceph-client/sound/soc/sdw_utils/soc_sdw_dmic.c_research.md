# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_dmic.c

Purpose: provides generic SoC DMIC DAPM initialization for SoundWire machine drivers.

Important APIs and data: `dmic_widgets[]` declares `SoC DMIC`; `dmic_map[]` routes `DMic` from `SoC DMIC`; `asoc_sdw_dmic_init()` installs both on the card DAPM context.

Control flow and state: the function adds the widget first, returns immediately if widget creation fails, then adds routes. It has no static mutable state; all persistent effects are DAPM widgets/routes owned by the card.

Dependencies and integration: uses `snd_soc_dapm_new_controls()` and `snd_soc_dapm_add_routes()`. It is a generic helper for boards that need a non-codec digital microphone path in addition to SoundWire endpoints.

Risks: route endpoint names must match the machine/card topology. The helper does not check if the controls already exist, so callers must avoid duplicate initialization. Failure is logged but only the returned error tells callers to abort.

Test signals: DAPM should include `SoC DMIC` and a `DMic` route; card probe should fail cleanly on widget/route allocation errors; capture path tests should confirm the DAPM source powers as expected.
