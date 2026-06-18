# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_pcm.c

## Purpose
Implements ALSA PCM devices for AU88x0 playback/capture paths: ADB analog PCM, SPDIF, A3D, WT, and I2S names. It maps ALSA hw_params/prepare/trigger/pointer callbacks to core DMA, route, SRC, FIFO, and mixer-volume helpers.

## Important APIs, Types, And Functions
Hardware descriptors are `snd_vortex_playback_hw_adb`, `snd_vortex_playback_hw_a3d`, `snd_vortex_playback_hw_spdif`, and `snd_vortex_playback_hw_wt`. ALSA PCM callbacks are `snd_vortex_pcm_open`, `snd_vortex_pcm_close`, `snd_vortex_pcm_hw_params`, `snd_vortex_pcm_hw_free`, `snd_vortex_pcm_prepare`, `snd_vortex_pcm_trigger`, and `snd_vortex_pcm_pointer`. Control callbacks include SPDIF status get/put/mask and per-subdevice PCM volume get/put/info. `snd_vortex_new_pcm()` creates PCM devices, chmaps, SPDIF controls, and per-subdevice volume controls.

## Control Flow
On open, the code applies integer/power-of-two/step constraints and chooses a hardware descriptor based on a stored PCM type byte. hw_params allocates or reallocates ADB/WT routes, configures DMA buffers, and activates PCM volume controls for ADB streams. prepare maps ALSA format to Vortex format, writes DMA mode/start buffer, and sets SRC rate except for SPDIF. trigger starts/stops/pauses/resumes the relevant FIFO. pointer reads core DMA position and converts bytes to frames. Control writes update SPDIF sample rate via `vortex_spdif_init()` or active playback mixer input gains.

## State And Persistence
State is in each `stream_t`, `substream->runtime->private_data`, `vortex->pcm[]`, `vortex->pcm_vol[]`, `vortex->spdif_sr`, and core route/DMA structures. PCM volume values remain in memory while the card exists but are not persisted by this driver. The PCM type is stored in `pcm->name[40]`, a deliberate private hack.

## Dependencies And Integration Points
Depends heavily on core helpers in `au88x0_core.c` and WT helpers in `au88x0_synth.c`, plus ALSA PCM/control/chmap APIs and `snd_pcm_set_managed_buffer_all`. Interrupt period completion is handled in core IRQ code.

## Risks
Using `pcm->name[40]` for the PCM type is fragile and depends on `struct snd_pcm` name storage. The same ops are used for capture and playback, with direction handled at runtime. WT support is explicitly marked not fully working. SPDIF open constrains rates to `vortex->spdif_sr`, and changing SPDIF control while streams are active could conflict with runtime constraints. pointer wraps to zero if beyond buffer size, which may mask bad hardware positions.

## Test Signals
ALSA should expose expected PCM devices and controls. Playback/capture should work with allowed formats, rates, channels, and period sizes; ADB quad channel constraints should apply on AU8830; SPDIF control changes should update accepted rates; per-subdevice PCM volume controls should become active only while a stream is allocated; long-running playback should have stable period elapsed callbacks.
