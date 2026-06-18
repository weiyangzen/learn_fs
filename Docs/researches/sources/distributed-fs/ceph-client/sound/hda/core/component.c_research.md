# sources/distributed-fs/ceph-client/sound/hda/core/component.c

## Purpose
`component.c` provides the HDA-to-DRM audio component bridge used mainly for HDMI/DP audio. It lets HDA controller/codec code acquire display power, override codec wake, synchronize audio rate, query ELD/audio-enabled state, and register audio component callbacks.

## Important APIs, Types, and Functions
Exports are `snd_hdac_set_codec_wakeup()`, `snd_hdac_display_power()`, `snd_hdac_sync_audio_rate()`, `snd_hdac_acomp_get_eld()`, `snd_hdac_acomp_register_notifier()`, `snd_hdac_acomp_init()`, and `snd_hdac_acomp_exit()`. Internal component master ops are `hdac_component_master_bind()` and `_unbind()`.

## Control Flow
`snd_hdac_acomp_init()` allocates a devres `drm_audio_component`, stores audio ops, initializes a completion, adds a typed component match, and registers a component master. Master bind binds all components, validates DRM ops/device, pins the DRM module, calls optional audio `master_bind`, and completes waiters. Display power uses `bus->display_power_status` as a bitset and calls DRM `get_power`/`put_power` when transitioning between zero and nonzero.

## State and Persistence Behavior
State is stored in `bus->audio_component`, `display_power_status`, and `display_power_active`. The display-power cookie returned by DRM is retained until the last HDA user releases power. Devres owns the component allocation.

## Dependencies and Integration Points
It depends on Linux component framework, DRM audio component ops, module refcounting, HDA bus/device structs, and optional codec `audio_ops->pin2port` mapping.

## Risks
Power refcount transitions must stay balanced; exit warns and forcibly puts active power. Module pinning can fail. Port/pipe mapping differs by graphics driver and codec. Dynamic unbinding is intentionally prevented by module pinning, so lifetime assumptions are strict.

## Test Signals
Validate bind/unbind, module refcount behavior, display power get/put pairing across multiple codec/controller users, codec wake override calls during reset, ELD retrieval for mapped pins, and cleanup with active power.
