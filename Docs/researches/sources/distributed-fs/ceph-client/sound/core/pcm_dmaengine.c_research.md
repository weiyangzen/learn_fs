# sources/distributed-fs/ceph-client/sound/core/pcm_dmaengine.c

## Purpose

`pcm_dmaengine.c` provides reusable ALSA PCM helper APIs for drivers that move audio with Linux dmaengine cyclic DMA. It converts PCM params to DMA slave config, opens/closes DMA-backed substreams, implements common trigger and pointer callbacks, requests channels, synchronizes stop, and refines hardware capabilities from DMA channel caps.

## Important APIs, Types, and Functions

`struct dmaengine_pcm_runtime_data` stores the channel, submitted cookie, and fallback period-completion position. Exported APIs include `snd_dmaengine_pcm_get_chan()`, `snd_hwparams_to_dma_slave_config()`, `snd_dmaengine_pcm_set_config_from_dai_data()`, `snd_dmaengine_pcm_trigger()`, `snd_dmaengine_pcm_pointer_no_residue()`, `snd_dmaengine_pcm_pointer()`, `snd_dmaengine_pcm_request_channel()`, `snd_dmaengine_pcm_open()`, `snd_dmaengine_pcm_sync_stop()`, `snd_dmaengine_pcm_close()`, `snd_dmaengine_pcm_close_release_chan()`, and `snd_dmaengine_pcm_refine_runtime_hwparams()`.

## Control Flow

Open validates a DMA channel, constrains periods to integers, allocates runtime private data, and stores the channel. START prepares a cyclic descriptor over the runtime DMA buffer, sets period interrupt callback unless no-period-wakeup is active, submits it, and issues pending DMA. Pause/resume/suspend/stop map to dmaengine pause, resume, terminate, or synchronize behavior. Pointer reads DMA residue and in-flight bytes to compute current frame position and runtime delay.

## State and Persistence Behavior

Per-open state persists in `runtime->private_data`. DMA state persists in the dmaengine channel after START via the submitted cookie. `prtd->pos` is a software fallback advanced by period callbacks and used by deprecated no-residue pointer reporting. Close synchronizes the channel, optionally releases it, and frees private data.

## Dependencies and Integration Points

The file depends on Linux dmaengine, ALSA PCM core, ASoC DAI DMA data structures, `sound/dmaengine_pcm.h`, and PCM buffer helpers. ASoC and platform PCM drivers commonly wire these exported helpers into their `open`, `close`, `trigger`, `pointer`, and hw-param paths.

## Risks and Edge Cases

DMA residue reporting varies by controller; unsupported or coarse residue granularity can produce imprecise pointers and sets `SNDRV_PCM_INFO_BATCH`. START must not submit descriptors with invalid buffer or period sizes. Pause-on-suspend only works when runtime info advertises pause support. `runtime->private_data` ownership means drivers cannot use that field for other state when using this helper.

## Test Signals

Validate playback and capture on dmaengine-backed drivers, pause/resume, suspend, stop synchronization, cyclic period interrupts, no-period-wakeup mode, pointer accuracy under residue and no-residue paths, DMA capability-derived format masks, and channel release on close.
