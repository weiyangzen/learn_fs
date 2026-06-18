# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-pcm.c

Purpose: registers the PXA2xx PCM platform component that exposes pxa2xx-lib PCM callbacks to ASoC.

Important APIs/types/functions: `pxa2xx_soc_platform` sets `.legacy_dai_naming = 1`; probe calls `devm_snd_soc_register_component`.

Control flow: platform driver `pxa-pcm-audio` registers the component at probe time. Actual PCM operations live in shared `pxa2xx-lib` callbacks used by CPU DAI components.

State and persistence: no driver-private state; component lifecycle is devm-managed.

Dependencies and integration: selected by `SND_PXA2XX_SOC`, provides the platform component used with PXA AC97/I2S/SSP paths.

Risks: this is a thin registration shim; missing probe means old machine drivers depending on `pxa-pcm-audio` will have no PCM platform. No OF match is present, so legacy platform-device creation is expected.

Test signals: platform device probe, ASoC component registration, and PXA machine drivers finding the PCM component.
