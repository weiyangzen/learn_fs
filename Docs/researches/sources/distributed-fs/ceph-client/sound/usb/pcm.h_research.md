# sources/distributed-fs/ceph-client/sound/usb/pcm.h

Purpose: internal usb-audio PCM interface used by the card, endpoint, offload, and stream setup code.

Important APIs, types, and functions: declares PCM ops installation, suspend/resume helpers, fixed-rate detection, pitch setup, buffer preallocation, sync endpoint parsing, format lookup, and exported hardware setup/free functions. Key callers can use `snd_usb_find_format()` or `snd_usb_find_substream_format()` for matching `struct audioformat` entries and can call `snd_usb_hw_params()`/`snd_usb_hw_free()` without going through a userspace PCM substream callback.

Control flow: the header separates generic usb-audio stream setup from both ALSA PCM callbacks and platform/offload integrations. Offload code in `qcom/qc_audio_offload.c` directly builds `snd_pcm_hw_params` and then calls the declared `snd_usb_hw_params()` and `snd_usb_hw_free()`.

State and persistence: no state is defined here, but the prototypes operate on `struct snd_usb_stream`, `struct snd_usb_substream`, `struct snd_usb_audio`, and `struct audioformat` instances maintained by the usb-audio core.

Dependencies and integration points: depends on declarations from `usbaudio.h`, ALSA PCM parameter types, and the audioformat model. It is an internal contract for files in `sound/usb` and for optional platform helpers compiled with usb-audio.

Risks: direct callers of `snd_usb_hw_params()` must pair with `snd_usb_hw_free()` and handle runtime PM/opened state consistently with normal PCM callbacks. Format lookup with `strict_match=false` can return a format that still needs later constraints.

Test signals: successful build of core usb-audio and Qualcomm offload, external symbol resolution for GPL exports, and offload paths that configure and release endpoints without opening an ALSA userspace PCM.
