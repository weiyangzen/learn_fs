# sources/distributed-fs/ceph-client/sound/soc/meson/axg-toddr.c

Purpose: implements the Amlogic TODDR frontend capture FIFO DAI. It captures audio from one selected internal input into memory through the shared AXG FIFO PCM layer.

Important APIs/types/functions: DAI ops include `axg_toddr_dai_startup`, `axg_toddr_dai_shutdown`, `axg_toddr_dai_hw_params`, `axg_toddr_pcm_new`, and G12A variants `g12a_toddr_dai_prepare` and `g12a_toddr_dai_startup`. Component callbacks are delegated to `axg_fifo_pcm_*` or `g12a_fifo_pcm_hw_params`.

Control flow: startup enables the FIFO peripheral clock, selects original non-resampled signed single-buffer capture, and for G12A/SM1 enables channel synchronization. `hw_params` maps physical width 8/16/32 to FIFO packing type, sets MSB/LSB extraction fields, and leaves DMA buffer programming to the FIFO component. G12A prepare toggles `CTRL1_TODDR_FORCE_FINISH` to reset the write pointer before capture.

State and persistence: capture state is held in the FIFO registers and clock enable state. DAPM input source selection is stored in either `FIFO_CTRL0` for AXG/G12A or `FIFO_CTRL1` for SM1. Match data changes threshold bitfields and available input count.

Dependencies and integration: depends on `axg-fifo.h`, ASoC DAPM, regmap, and the shared FIFO platform driver. Device-tree compatibles select AXG, G12A, or SM1 behavior.

Risks: resampling is explicitly not supported. Unsupported physical widths return `-EINVAL`. Capture channel ordering on G12A depends on the `CTRL0_TODDR_SYNC_CH` workaround and force-finish pointer reset. Wrong mux selection captures silence or the wrong internal source.

Test signals: capture open/close through the FIFO PCM component, correct input mux exposure, stable first-channel placement on G12A/SM1, pointer movement during recording, and no clock/regmap errors on repeated startup/shutdown.
