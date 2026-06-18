# sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.h

Purpose: header for Qualcomm USB offload ALSA route-control creation.

Important APIs, types, and functions: declares `snd_usb_offload_create_ctl(struct snd_usb_audio *chip, struct device *bedev)`.

Control flow: `qc_audio_offload.c` calls the declared function after it identifies an offload-capable USB card and before notifying `snd_soc_usb_connect()`, allowing userspace to query the route mapping from the USB card.

State and persistence: the header defines no state. The implementation creates persistent ALSA card controls that query the supplied backend device.

Dependencies and integration points: depends on `struct snd_usb_audio` from usb-audio internals and `struct device` from the backend ASoC/auxiliary device path.

Risks: callers must pass a valid backend device with `snd_soc_usb_update_offload_route()` support; otherwise control reads return `-1`.

Test signals: compile linkage between `qc_audio_offload.o` and `mixer_usb_offload.o`, plus visible route controls on offload-capable cards.
