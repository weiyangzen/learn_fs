## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.c

Purpose: implements the shared ALSA-side helper for USB Audio Class gadget functions. It creates a virtual `snd_card`/PCM device for a `struct g_audio`, moves samples between USB isochronous requests and ALSA DMA buffers, exposes mixer/rate/pitch controls, and exports lifecycle hooks used by UAC1/UAC2 function drivers.

Important APIs, types, and functions:
- `struct uac_rtd_params` is per-stream runtime state. It tracks endpoint enablement, the active ALSA substream, ring-buffer `hw_ptr`, preallocated USB requests, feedback request, pitch, current sample rate, feature-unit volume/mute state, control element IDs, and a spinlock for state read/write from control paths.
- `struct snd_uac_chip` is the ALSA card private data. It owns playback/capture `uac_rtd_params`, `snd_card`, `snd_pcm`, and playback packet scheduling precomputations (`p_residue_mil`, `p_interval`, `p_framesize`).
- `u_audio_iso_complete()` is the main isochronous completion callback. For playback IN packets it calculates adaptive packet length from sample rate, pitch, endpoint interval, frame size, and accumulated fractional residue, then copies ALSA DMA data into request buffers. For capture OUT packets it copies received data into ALSA DMA memory. It advances `hw_ptr`, notifies ALSA periods, and requeues the request.
- `u_audio_iso_fback_complete()` updates and requeues the asynchronous feedback endpoint request with `u_audio_set_fback_frequency()`.
- ALSA PCM callbacks are `uac_pcm_open()`, `uac_pcm_trigger()`, `uac_pcm_pointer()`, and null close/prepare helpers in `uac_pcm_ops`.
- Endpoint lifecycle exports are `u_audio_start_capture()`, `u_audio_stop_capture()`, `u_audio_start_playback()`, `u_audio_stop_playback()`, and `u_audio_suspend()`.
- Control exports are `u_audio_get/set_capture_srate()`, `u_audio_get/set_playback_srate()`, `u_audio_get/set_volume()`, and `u_audio_get/set_mute()`.
- `g_audio_setup()` allocates runtime buffers/requests, registers the ALSA card and PCM, and creates pitch, mute, volume, and volatile rate controls as needed. `g_audio_cleanup()` releases the card and runtime storage.

Control flow:
- Setup starts with caller-filled `g_audio->params`, endpoint max packet sizes, and gadget pointer. `g_audio_setup()` allocates the private chip, initializes capture/playback runtime depending on channel masks, creates the ALSA card/PCM, registers controls according to feedback endpoint and feature-unit flags, sets a managed continuous DMA buffer, and registers the card.
- Host alternate-setting enable in a UAC function calls `u_audio_start_capture()` or `u_audio_start_playback()`. Each function configures the endpoint for current speed, enables it, allocates missing requests, assigns callbacks/buffers, queues all requests, and marks the rate control active. Capture can also enable an IN feedback endpoint.
- Completion callbacks are continuous recycling loops. If ALSA is not actively running, requests are requeued without copying meaningful PCM data. Once ALSA starts, completions copy to/from `runtime->dma_area`, update `hw_ptr`, and call `snd_pcm_period_elapsed()` when a period boundary is crossed.
- Stop paths mark controls inactive, dequeue or free outstanding requests through `free_ep()` / `free_ep_fback()`, disable endpoints, and allow completion callbacks to free requests that could not be dequeued synchronously.

State and persistence:
- Persistent runtime state is kernel memory under `g_audio->uac`. It lasts from `g_audio_setup()` until `g_audio_cleanup()`.
- Stream state includes `srate`, `pitch`, `volume`, `mute`, `active`, endpoint-enabled flags, and request arrays. It is not persisted outside the module.
- ALSA control values are mirrored into `uac_rtd_params`; host-facing UAC control changes are expected to call exported setters, while ALSA user changes invoke `audio_dev->notify()` so the UAC function can report feature-unit changes to USB control state.
- `p_residue_mil` persists across playback completions during one streaming episode to distribute fractional samples across packets.

Dependencies and integration points:
- Depends on ALSA core/PCM/control APIs, USB composite gadget APIs, UAC descriptor constants, and `u_audio.h` / `uac_common.h`.
- UAC1/UAC2 function drivers provide descriptors, endpoints, rate lists, channel masks, sample sizes, feature-unit IDs, and a `notify()` callback.
- Uses `config_ep_by_speed()`, `usb_ep_enable()`, `usb_ep_queue()`, `usb_ep_dequeue()`, and endpoint descriptor interval/maxpacket fields from the gadget framework.
- ALSA user space sees the registered card/PCM and mixer controls. USB control request handlers use exported get/set helpers.

Risks:
- Error handling in `u_audio_start_capture()` has TODO comments: feedback endpoint configuration/enable/allocation failures can leave the OUT endpoint enabled and queued unless the caller tears it down.
- Several allocation failures after endpoint enablement return directly without disabling endpoints or freeing already allocated request state.
- `u_audio_pitch_get()` / `u_audio_pitch_put()` do not take `prm->lock`, unlike most rate/volume/mute paths, so pitch updates can race with feedback and playback packet calculations.
- `u_audio_iso_complete()` uses `req->actual = req->length` for playback before copying; correctness depends on IN requests being prepared as device-to-host payloads.
- Period elapsed detection compares wrapped `hw_ptr` modulo period against `req->actual`; unusual period/request sizing can affect notification cadence.
- Mutable static `u_audio_controls[]` names are overwritten during setup; concurrent setup of multiple cards could race on control template names if multiple gadget instances are created.

Test signals:
- Build with UAC1/UAC2 gadget functions enabled and verify no sparse/lockdep warnings around spinlocks and callback contexts.
- Enumerate a UAC gadget, run ALSA playback and capture at every configured rate/sample size/channel mask, and check for steady `snd_pcm_period_elapsed()` behavior without xruns.
- Exercise host sample-rate control requests and ALSA volatile rate controls; inactive streams should report rate `0`, active streams should notify selected rate.
- Test mute/volume from both host controls and ALSA mixer, confirming `notify()` callbacks and `snd_ctl_notify()` events.
- For asynchronous capture feedback, inspect feedback packet values at full speed and high speed and vary pitch within configured limits.
