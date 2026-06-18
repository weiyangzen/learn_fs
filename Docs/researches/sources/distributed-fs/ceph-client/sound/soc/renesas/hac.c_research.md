# sources/distributed-fs/ceph-client/sound/soc/renesas/hac.c

Purpose: SuperH HAC AC97 CPU DAI/component driver for SH7760/SH7780, providing AC97 bus read/write/reset operations and DAI hw_params data-width programming.

Important functions and types: `struct hac_priv` stores fixed HAC MMIO base addresses per unit. `hac_ac97_write()`, `hac_ac97_read()`, `hac_ac97_warmrst()`, and `hac_ac97_coldrst()` implement `snd_ac97_bus_ops`. `hac_get_codec_data()` and `hac_read_codec_aux()` perform the manual-specified polling flow. `hac_hw_params()` selects 16-bit or 20-bit DMA control bits. `sh4_hac_dai[]` exposes one or two AC97 DAIs depending on CPU subtype.

Control flow: platform probe installs global AC97 ops via `snd_soc_set_ac97_ops()` and registers the component/DAIs. AC97 codec accesses poll command/data-ready bits with microsecond delays. Remove clears global AC97 ops.

State and persistence: fixed `hac_cpu_data[]` provides MMIO bases; there is no dynamic private allocation. AC97 ops are global while the platform driver is bound.

Dependencies and integration: depends on SuperH CPU subtype selection, ASoC AC97 bus, direct fixed MMIO register access, and platform driver `hac-pcm-audio`.

Risks: a prominent FIXME notes only the first AC97 unit can be used because ASoC AC97 callbacks do not identify unit context. Fixed MMIO, polling timeouts, disabled interrupts around register programming, and architecture-specific compile guards all increase fragility.

Test signals: AC97 cold/warm reset reaches codec-ready, register read/write retries succeed, 16-bit hw_params sets expected bits, second DAI is not assumed functional without code changes, and probe/remove leave global AC97 ops balanced.
