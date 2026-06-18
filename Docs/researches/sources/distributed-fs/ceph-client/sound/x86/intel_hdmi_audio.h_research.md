# sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.h

## Purpose
Defines private structures and channel/speaker mapping types for the Intel HDMI/DP LPE audio driver.

## Important APIs, Types, And Functions
- Constants include `MAX_PB_STREAMS`, `MAX_CAP_STREAMS`, `BYTES_PER_WORD`, and driver name `INTEL_HAD`.
- `enum cea_speaker_placement` defines bit positions for CEA speaker layout.
- `struct cea_channel_speaker_allocation` and `struct channel_map_table` support InfoFrame channel allocation and ALSA channel-map control generation.
- `struct pcm_stream_info` stores the active ALSA substream and an IRQ/work refcount.
- `struct snd_intelhad` is the per-port runtime context.
- `struct snd_intelhad_card` is the card-wide context with ALSA card, MMIO, IRQ, pipe/port counts, and per-port contexts.

## Control Flow
The header has no direct flow; `intel_hdmi_audio.c` fills these structures during probe, hotplug, ALSA open/close/prepare/trigger, and IRQ handling.

## State And Persistence
The main state holders are `snd_intelhad` and `snd_intelhad_card`. They persist for the ALSA card lifetime and include connection status, ELD, DP flag, stream refcount, register cache, ring indices, work item, mutex, spinlock, and jack/channel-map objects.

## Dependencies And Integration Points
Includes `intel_hdmi_lpe_audio.h` for register constants and uses ALSA/DRM types through source inclusions. It binds private driver logic to i915-provided platform data and ALSA PCM/control objects.

## Risks
`pcm_ctx[3]` assumes a maximum of three ports/pipes. Refcount and lock fields in `snd_intelhad` must be used consistently because IRQ and workqueue paths dereference the active substream.

## Test Signals
Compile tests with different i915 platform-data port counts, plus runtime hotplug and close-while-IRQ tests that stress fields declared here.
