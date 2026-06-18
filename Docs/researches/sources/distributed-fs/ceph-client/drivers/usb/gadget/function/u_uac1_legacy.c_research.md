## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.c

Purpose: implements the legacy UAC1 gadget audio helper that proxies USB audio playback into existing ALSA device files, rather than creating its own virtual ALSA card like `u_audio.c`.

Important APIs and functions:
- `_snd_pcm_hw_param_set()` and `snd_interval_refine_set()` are local helpers for setting ALSA hardware parameter masks/intervals.
- `playback_default_hw_params()` configures the opened playback substream for default interleaved S16_LE, 2 channels, 48000 Hz, issues DROP/HW_PARAMS/PREPARE ioctls, and stores the actual selected parameters.
- `u_audio_playback()` writes a USB audio buffer to the playback substream using `snd_pcm_kernel_write()`, preparing again after XRUN/SUSPENDED states.
- `u_audio_get_playback_channels()` and `u_audio_get_playback_rate()` expose configured playback parameters.
- `gaudio_open_snd_dev()` opens control, playback, and capture device files from `f_uac1_legacy_opts`; it obtains PCM substreams from file private data and initializes playback.
- `gaudio_setup()` opens the ALSA files; `gaudio_cleanup()` closes them.

Control flow:
- The legacy function owns a `struct gaudio` and calls `gaudio_setup()` during bind/activation. That opens the configured control file first, then playback, then optionally capture.
- USB OUT audio payloads are later forwarded by the UAC1 legacy function to `u_audio_playback()`, which handles XRUN recovery and writes frames into the kernel ALSA substream.
- Cleanup closes any opened files.

State and persistence:
- `struct gaudio_snd_dev` stores file pointers, substream pointers, access/format/channels/rate, and parent card pointer.
- The default file paths are declared in the header and can be overridden through `f_uac1_legacy_opts`.
- No samples are persisted; state exists only while the gadget function is bound/open.

Dependencies and integration:
- Depends on kernel file operations (`filp_open`, `filp_close`), ALSA PCM internals/ioctls, and `u_uac1_legacy.h`.
- Integrates with older UAC1 function code that manages USB descriptors/endpoints and calls these helpers for audio payloads.

Risks:
- Uses fixed default playback hardware params regardless of host-selected format unless higher layers coordinate separately.
- `u_audio_playback()` retries indefinitely on short/error writes by jumping to `try_again`; persistent errors can spin.
- Failure after opening control but before opening playback does not close the already opened control file in `gaudio_open_snd_dev()`; caller cleanup is needed.
- Capture open failures are logged but not fatal, leaving capture fields null.
- Direct use of ALSA internal helpers and kernel file paths is fragile compared with the modern virtual-card model.

Test signals:
- Configure valid and invalid playback/control/capture paths and verify setup failure/cleanup behavior.
- Stream UAC1 playback to an ALSA PCM and induce XRUN/SUSPEND to test recovery.
- Confirm reported playback channels/rate match actual `HW_PARAMS`.
