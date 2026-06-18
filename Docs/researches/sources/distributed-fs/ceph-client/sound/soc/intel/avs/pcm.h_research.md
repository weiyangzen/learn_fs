# sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.h

Purpose: Minimal public PCM header exposing period-elapsed notification for AVS streams.

Important APIs/types: Declares `void avs_period_elapsed(struct snd_pcm_substream *substream);`.

Control flow role: Interrupt or stream code can call `avs_period_elapsed()` to schedule the work item that invokes `snd_pcm_period_elapsed()` from process context.

State and persistence: No state is declared here; state lives in `struct avs_dma_data` inside `pcm.c`.

Dependencies and integration: Includes `<sound/pcm.h>` for `struct snd_pcm_substream`. Used by AVS stream/interrupt code that needs to notify ALSA PCM.

Risks: Because only a function is exposed, callers must ensure the substream still has valid DAI DMA data and the work item has not been disabled during shutdown.

Test signals: Period interrupt/callback tests, stream shutdown race tests, and compile coverage for external users.
