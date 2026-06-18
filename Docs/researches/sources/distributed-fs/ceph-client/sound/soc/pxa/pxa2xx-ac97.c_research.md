# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-ac97.c

Purpose: implements the PXA2xx AC97 ASoC CPU DAI and AC97 controller binding, including reset/read/write callbacks and DMA data for stereo, aux, and mic FIFOs.

Important APIs/types/functions: `pxa2xx_ac97_ops` wraps AC97 controller read/write/reset operations from `pxa2xx-lib`. Startup callbacks select DMA data for HiFi, aux, or mic DAIs. Probe registers the AC97 controller and ASoC component with three DAIs.

Control flow: platform probe validates single-port use, derives DMA FIFO physical addresses from the MEM resource, probes AC97 hardware, registers `snd_ac97_controller`, stores it as driver data, and registers ASoC DAIs. Remove unregisters the controller and removes hardware. PM delegates to PXA AC97 hardware suspend/resume helpers.

State and persistence: DMA address structures are static but filled at probe. AC97 controller state is owned by ALSA AC97 core. Hardware state is handled by pxa2xx-lib.

Dependencies and integration: depends on `sound/ac97/controller.h`, `sound/pxa2xx-lib.h`, DMAEngine PCM, platform resource layout, and DT compatibles for PXA250/270/300 AC97.

Risks: static DMA data assumes one physical AC97 port. Probe registers the AC97 controller before ASoC component; later registration failure may rely on devm unwinding but controller unregister is only in remove. Mic DAI rejects playback explicitly.

Test signals: AC97 codec enumeration, warm/cold reset behavior, stereo/aux/mic capture/playback DMA channels, suspend/resume, and DT resource address mapping.
