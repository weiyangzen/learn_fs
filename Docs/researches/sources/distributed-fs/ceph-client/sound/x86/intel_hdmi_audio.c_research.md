# sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.c

## Purpose
Implements the Intel HDMI/DP LPE ALSA platform driver used on Atom platforms without HDAudio. It binds to an i915-created platform device, creates ALSA playback PCM devices, programs HDMI/DP audio registers, handles display hotplug/ELD changes, and advances a fixed hardware buffer descriptor ring.

## Important APIs, Types, And Functions
- Module parameters `index`, `id`, and `single_port` control ALSA card identity and legacy port mapping.
- `had_pcm_hardware` advertises playback formats, rates, channel counts, period constraints, and buffer limits.
- Register helpers `had_read_register*()`, `had_write_register*()`, and `had_enable_audio()` centralize MMIO access and preserve cached `AUD_CONFIG` state.
- Channel allocation helpers derive HDMI Audio InfoFrame channel allocation and ALSA chmap controls from ELD speaker data.
- `had_prog_status_reg()`, `had_prog_dip()`, `had_prog_n()`, `had_prog_cts()`, and `had_init_audio_ctrl()` program channel status, infoframe, clocking, and core audio configuration.
- Ring helpers `had_init_ringbuf()`, `had_prog_bd()`, `had_process_ringbuf()`, and `had_pcm_pointer()` map the ALSA ring to four hardware buffer descriptors.
- ALSA callbacks `had_pcm_open()`, `close()`, `prepare()`, `trigger()`, `sync_stop()`, and `pointer()` provide playback operation.
- `display_pipe_interrupt_handler()` acknowledges per-pipe buffer-done/underrun IRQs and dispatches them to port contexts.
- `had_audio_wq()` processes i915 hotplug/ELD notifications under a workqueue and runtime PM.
- `__hdmi_lpe_audio_probe()` creates the ALSA card, PCMs, controls, jacks, IRQ, MMIO mapping, and i915 notification callback.

## Control Flow
Probe receives i915 platform data, maps MMIO, requests IRQ, sets a 32-bit DMA mask, initializes per-port `snd_intelhad` contexts, creates playback-only PCM devices, registers IEC958/ELD/chmap controls and jacks, registers the ALSA card, stores `notify_audio_lpe` into i915 platform data, enables runtime PM, and schedules initial work for all ports. On hotplug, i915 calls `notify_audio_lpe()`, which schedules `had_audio_wq()`. The workqueue copies ELD, updates DP/HDMI clock state, transitions connected state, rebuilds channel map, reports jack state, assigns pipe, and may reprogram N/CTS for an active stream.

For playback, ALSA open resumes runtime PM and exposes the active substream. Prepare programs N/CTS/DIP/status/audio-control registers and initializes the four-BD hardware ring. Trigger START/RESUME/PAUSE_RELEASE acknowledges stale IRQs and sets `aud_en`; STOP/PAUSE disables it. IRQs ack sticky status bits, advance/reprogram BDs on buffer-done, call `snd_pcm_period_elapsed()`, and stop with xrun on underrun or disconnect.

## State And Persistence
`snd_intelhad_card` persists card-wide MMIO, IRQ, port/pipe counts, and three per-port contexts. Each `snd_intelhad` tracks connection, ELD, DP/HDMI clocking, pipe/port, jack, channel map, cached `aud_config`, current substream plus refcount, spinlock, mutex, and ring indices (`bd_head`, `pcmbuf_head`, `pcmbuf_filled`). State is in kernel memory only and is reset on driver removal or hot-unplug. Runtime PM state persists through autosuspend.

## Dependencies And Integration Points
Depends on ALSA core/PCM/control/jack APIs, Linux platform device, MMIO, IRQ, DMA, runtime PM, DRM ELD helpers, and `drm/intel/intel_lpe_audio.h` platform data from i915. Hardware register definitions come from `intel_hdmi_lpe_audio.h`; private data structures come from `intel_hdmi_audio.h`.

## Risks
- Hardware has a documented AUD_CONFIG read/modify/write bug, so cached config must remain authoritative.
- The substream refcount wait in close busy-spins with `cpu_relax()` until IRQ/work users release the substream.
- `had_process_ringbuf()` treats invalid BD length or all-empty descriptors as xrun; hardware register anomalies can stop playback.
- Hotplug changes can stop active streams and reassign pipes; ordering between connected state and `ctx->pipe` changes is subtle.
- DP clocking supports only fixed link rates defined in the header; unsupported link rates cause `-EINVAL`.
- Channel map allocation mutates `eld[DRM_ELD_SPEAKER]` for a workaround, so ELD-derived data is not purely read-only.

## Test Signals
Test probe with valid i915 platform data, no platform data, MMIO/IRQ failure paths, HDMI and DP hotplug/unplug, ELD speaker masks, channel map control reads, IEC958 control changes, playback at every advertised rate/format/channel count, period sizes aligned to 64 bytes, underrun IRQs, runtime suspend/resume, and `single_port=1`. Inspect jack reports, xrun behavior, and buffer pointer monotonicity.
