# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_drv_interface.c

## Purpose
This file exposes the low-level SST DSP services to the ASoC platform through `struct sst_ops` and `struct compress_sst_ops`. It translates PCM/compressed open, close, start, stop, pause, drain, timestamp, byte-stream, metadata, capability, and power requests into common SST firmware operations and registers the resulting `sst_device` with the platform driver.

## Important APIs, types, and functions
PCM-facing helpers include `sst_open_pcm_stream()`, `sst_close_pcm_stream()`, `sst_stream_init()`, `sst_stream_start()`, `sst_stream_drop()`, `sst_stream_pause()`, `sst_stream_resume()`, `sst_read_timestamp()`, and `sst_send_byte_stream()`. Compressed-facing helpers include `sst_cdev_open()`, `sst_cdev_close()`, `sst_cdev_stream_start()`, `sst_cdev_stream_drop()`, `sst_cdev_stream_drain()`, `sst_cdev_tstamp()`, `sst_cdev_ack()`, `sst_cdev_caps()`, `sst_cdev_codec_caps()`, and `sst_cdev_set_metadata()`. `sst_power_control()` handles runtime PM and firmware load-on-demand. `sst_register()` and `sst_unregister()` bridge to `sst_register_dsp()` and `sst_unregister_dsp()`.

## Control flow
The platform powers on the DSP through `sst_power_control(true)`. If runtime PM resumes the device from reset and this is the first user, firmware is loaded. PCM open allocates a firmware stream using `sst_get_stream()`, while stream init installs PCM period callbacks and substream pointers. Trigger paths update stream status and send firmware start/drop/pause/resume commands. Timestamp reads copy firmware timestamp memory and convert ring/hardware counters into ALSA pointer and delay values. Compressed open allocates a stream and stores fragment/drain callbacks; ack updates cumulative bytes in the firmware timestamp area; drain is asynchronous and completes through the callback.

## State and persistence behavior
The file mutates `ctx->streams[]`: status, callbacks, substream pointers, cumulative bytes, channel count, pipe ID, and task ID. `ctx->stream_cnt` tracks PCM streams. The static `sst_dsp_device` stores callback tables and a current device pointer for registration. Capabilities are static for MP3 and AAC.

## Dependencies and integration points
It depends on runtime PM, PM QoS, ALSA PCM/compress APIs, firmware stream helpers in `sst_stream.c`, IPC helpers in `sst_pvt.c`, and global platform registration in `sst-mfld-platform-pcm.c`. It is the main boundary consumed by the ASoC platform and compressed layer.

## Risks and edge cases
`sst_power_control()` uses runtime PM usage count to decide when to load firmware, which is sensitive to reference balance. PCM `sst_stream_start()` returns success when firmware is not running, masking some state races. Timestamp math assumes firmware counters are coherent and uses 24-bit sample width for compressed IO frames. `sst_cdev_close()` does not runtime-put directly; power down is done by the platform compressed free path.

## Test signals
Test firmware load on first power-up, PCM open/init/start/drop/pause/resume/close, compressed MP3/AAC open/start/drain/ack/tstamp/close, byte-stream control commands, caps output, timestamp pointer/delay correctness, runtime PM reference balance, and error paths for invalid stream IDs or reset firmware state.
