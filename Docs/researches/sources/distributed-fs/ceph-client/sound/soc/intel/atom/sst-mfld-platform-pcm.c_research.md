# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-pcm.c

## Purpose
This file is the Atom SST ASoC platform/CPU-DAI driver for PCM and compressed audio integration. It registers the global DSP device handle used by the platform, maps front-end DAI streams to firmware stream IDs and pipe IDs, creates CPU DAIs for media, deepbuffer, compressed, and SSP backends, implements PCM component operations, and coordinates SSP/vb-timer power behavior around backend activity and system sleep.

## Important APIs, types, and functions
DSP registration is exposed through `sst_register_dsp()` and `sst_unregister_dsp()`, which manage the global `struct sst_device *sst`. Stream metadata is prepared by `sst_fill_stream_params()`, `sst_fill_pcm_params()`, `sst_fill_alloc_params()`, and `sst_platform_alloc_stream()`. PCM callbacks include `sst_media_open()`, `sst_media_close()`, `sst_media_prepare()`, `sst_soc_open()`, `sst_soc_trigger()`, `sst_soc_pointer()`, `sst_soc_delay()`, and `sst_soc_pcm_new()`.

Backend DAI control uses `sst_enable_ssp()`, `sst_be_hw_params()`, `sst_set_format()`, `sst_platform_set_ssp_slot()`, and `sst_disable_ssp()`, which call helpers implemented in `sst-atom-controls.c`. The component driver is `sst_soc_platform_drv`; the platform driver is `sst_platform_driver`. The DAI table `sst_platform_dai[]` defines `media-cpu-dai`, `deepbuffer-cpu-dai`, `compress-cpu-dai`, `ssp0-port`, `ssp1-port`, and `ssp2-port`.

## Control flow
Probe allocates `struct sst_data` and platform stream-map data, initializes the mutex, stores driver data, and registers the ASoC component plus DAIs. Component probe stores the card pointer and calls `sst_dsp_init_v2_dpcm()` to create the DAPM graph and controls. FE startup allocates `sst_runtime_stream`, takes a module reference on the low-level SST driver, powers up the DSP, and applies period/buffer constraints. Prepare either drops an already allocated stream or allocates and initializes a new one, including firmware PCM parameters and period callback registration. Trigger commands call low-level start/drop/pause/resume ops and update protected stream status.

Backend startup starts the firmware scheduler and fills SSP defaults when the DAI first becomes active. Hardware params sends SSP enable once active. Shutdown sends SSP disable and idles the scheduler when the backend no longer has active users. PM prepare suspends the card, powers it off, and idles active SSPs; complete restarts active SSPs and resumes the card.

## State and persistence behavior
Runtime stream state is heap-allocated per PCM open and stored in ALSA runtime private data. Global DSP registration persists in `sst` while the low-level driver is registered. `struct sst_data` stores the platform stream map, card pointer, command byte buffer pointer, and cached SSP command. No data is persisted outside kernel memory and device/firmware state.

## Dependencies and integration points
The file integrates ALSA PCM, compressed offload, ASoC component/DAI APIs, runtime PM through the low-level ops, firmware stream mappings from `asm/platform_sst_audio.h`, and control helpers from `sst-atom-controls.c`. It is the bridge between machine drivers and the low-level SST firmware driver.

## Risks and edge cases
Stream mapping only matches device number and direction, ignoring subdevice despite receiving it. `sst_register_dsp()` holds a module reference for the registered low-level device and users take additional references on open. The `prepare` path drops an existing stream and returns immediately, relying on a later prepare for reallocation. Backend behavior depends on `snd_soc_dai_active()` counts and only `send_ssp_cmd()` supports selected SSP names. Suspend prepare manually invokes ASoC suspend/poweroff and touches active DAIs, so ordering with the wider ASoC PM core is sensitive.

## Test signals
Test platform probe, component probe, DAI registration, PCM playback/capture/deepbuffer open/prepare/start/pause/resume/stop/close, compressed DAI creation, period elapsed callbacks, pointer and delay reads, managed DMA buffer sizing, SSP enable/disable for active backends, mute-stream gain updates, and suspend/resume with active and idle DAIs.
