<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_pcm.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_pcm.c

Purpose: ALSA PCM implementation for GF1/InterWave synth playback and plain GF1 capture. Playback uploads samples into onboard DRAM and drives GF1 voices; capture uses GF1 record DMA without autoinit support.

Important APIs/types/functions: exported `snd_gf1_pcm_new()`. `struct gus_pcm_private` tracks substream, allocated voices, onboard memory, period/block state, DMA wait queue, and volume. Playback ops implement open/close/hw_params/hw_free/prepare/trigger/pointer/copy/silence. Capture ops implement open/close/hw_params/prepare/trigger/pointer. Mixer control handlers manage `"PCM Playback Volume"` or `"GPCM Playback Volume"`.

Control flow: playback open allocates private state and initializes GF1 DMA. `hw_params` allocates GF1 memory and one/two voices; copy/silence writes into runtime DMA area then either queues GF1 DMA or pokes small blocks directly. Trigger start programs voice start/current/end/pan/frequency/volume ramp; wave interrupts roll period endpoints and call `snd_pcm_period_elapsed()`. Capture programs DMA2 one period at a time and restarts it in the DMA-read interrupt.

State and persistence: per-substream state owns GF1 memory and voices until `hw_free`. Global GF1 PCM volume is cached in `gus->gf1`. Active flags, `bpos`, and DMA counts are volatile playback state.

Dependencies and integration: uses `gus_dma.c`, `gus_mem.c`, `gus_volume.c`, `gus_io.c`, reset voice allocation, ALSA PCM constraints, and ISA DMA. InterWave disables capture because codec capture is handled by WSS.

Risks: noninterleaved playback layout, onboard memory allocation, and voice IRQ rollover are tightly coupled. Close waits for pending DMA and logs serious DMA problems after timeout. Test signals are playback at 1/2 channels and 8/16-bit signed/unsigned formats, period interrupts, copy/silence correctness, volume changes during playback, capture on plain GF1, suspend stop behavior, and buffer resize freeing memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_pcm.c -->
