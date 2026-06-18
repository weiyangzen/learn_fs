# sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.c

Purpose: ALSA read-only controls that expose Qualcomm USB audio offload routing for each playback PCM on a USB sound card.

Important APIs, types, and functions: implements `snd_usb_offload_create_ctl()`. It defines card-route and PCM-route controls whose get callbacks call `snd_soc_usb_update_offload_route()` with `SND_SOC_USB_KCTL_CARD_ROUTE` or `SND_SOC_USB_KCTL_PCM_ROUTE`. `CARD_IDX()` and `PCM_IDX()` unpack card and PCM IDs from `private_value`.

Control flow: for each playback `snd_usb_stream` with an endpoint and PCM index <= 255, `snd_usb_offload_create_ctl()` adds two card-interface controls. Each control stores the USB sound card number in the upper bits and PCM index in the lower bits, then query callbacks ask the ASoC USB backend which card/PCM currently manages the offload route. On backend errors, returned integer values are set to `-1`.

State and persistence: controls are attached to the ALSA card and are read-only. They do not cache route values; each read delegates to the backend device passed as the kcontrol chip.

Dependencies and integration points: depends on `sound/soc-usb.h`, usb-audio card and stream lists, ALSA control APIs, and the backend device supplied by `qc_audio_offload.c`.

Risks: the function mutates static `snd_kcontrol_new` templates (`name`, `count`, `private_value`) for each control creation; this is acceptable during serialized card setup but would be risky if called concurrently. Control names are stack buffers copied by `snd_ctl_new1()`, so they rely on ALSA duplicating names immediately. Only playback streams are represented.

Test signals: USB cards with offload support should show `USB Offload Playback Card Route PCM#N` and `USB Offload Playback PCM Route PCM#N`; reads should return `-1` when no route exists and backend card/PCM IDs when an ASoC offload route is active.
