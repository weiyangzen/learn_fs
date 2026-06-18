# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_mixer.c

## Purpose

This file adds VXPocket-specific ALSA mixer controls for microphone input level or boost. Common playback, routing, and DSP controls are handled by the shared VX core; this file only covers the analog mic differences between VXPocket and VXPocket440.

## Important APIs, types, and functions

`vxp_add_mic_controls()` initializes `chip->mic_level`, programs the hardware default using `vx_set_mic_level()` or `vx_set_mic_boost()`, and adds either `Mic Capture Volume` for `VX_TYPE_VXPOCKET` or `Mic Boost` for `VX_TYPE_VXP440`. The get/put callbacks read and update `struct snd_vxpocket::mic_level`, validate ranges, and serialize changes with `vx_core::mixer_mutex`.

## Control flow

During VX core control creation, `snd_vxpocket_ops.add_controls` calls `vxp_add_mic_controls()`. Put callbacks compare the requested value against cached `mic_level`; changed values are sent through low-level hardware helpers in `vxp_ops.c` before updating the cache and returning ALSA's changed flag.

## State and persistence behavior

The only persistent mixer state is `mic_level`, interpreted as 0-8 analog level for VXPocket or boolean boost for VXPocket440. Hardware CDSP/MICRO registers are not read back here, so cache correctness depends on serialized ALSA control writes and resume reinitialization elsewhere.

## Dependencies and integration points

It depends on ALSA control APIs, TLV dB scale metadata, `vxpocket.h`, and exported low-level functions from `vxp_ops.c`. It is integrated through `snd_vxpocket_ops`.

## Risks and test signals

Risks include cache/hardware divergence after reset, wrong type-specific control exposure, and invalid dB-scale expectations because the VXPocket scale is coarse and remapped. Test mixer enumeration on both V2 and 440 cards, invalid values, repeated no-op puts, source switching to microphone, and suspend/resume retaining effective mic level.
