## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-ctl.c

Purpose: this file implements ALSA mixer and IEC958 controls for the BCM2835 audio driver and propagates control changes to active VideoCore audio streams.

Important functions: `snd_bcm2835_ctl_info()`, `snd_bcm2835_ctl_get()`, and `snd_bcm2835_ctl_put()` implement volume, mute, and playback device control behavior. `bcm2835_audio_set_chip_ctls()` iterates active substreams and sends updated controls. IEC958 controls are handled by `snd_bcm2835_spdif_default_info/get/put()` and `snd_bcm2835_spdif_mask_info/get()`. `create_ctls()` installs controls, while `snd_bcm2835_new_headphones_ctl()` and `snd_bcm2835_new_hdmi_ctl()` expose route-specific control sets.

Control flow: ALSA queries control metadata, reads current values under `chip->audio_mutex`, and writes validated values back under the same mutex. On change, all open streams receive `bcm2835_audio_set_ctls()`. HDMI gets both regular mixer controls and IEC958 default/mask controls; headphones get regular controls only.

State and persistence: control state is stored in `struct bcm2835_chip` fields `volume`, `mute`, `dest`, and `spdif_status`. These values persist for the ALSA card lifetime and are applied to streams when controls change and again during PCM prepare.

Dependencies and integration points: depends on ALSA core/control/TLV APIs, IEC958 definitions, and transport function `bcm2835_audio_set_ctls()` from `bcm2835-vchiq.c`. Control objects are created from `bcm2835.c` after PCM creation.

Risks: mute semantics are inverted at the transport layer: `CTRL_VOL_MUTE` is 0 and `CTRL_VOL_UNMUTE` is 1, so `if (!chip->mute)` sends the mute volume. Control updates are serialized on `audio_mutex` but send VCHIQ messages while holding it, which can block other ALSA operations. `PCM_PLAYBACK_DEVICE` is supported by generic callbacks but is not included in the declared control arrays, so it is effectively unused here.

Test signals: `amixer` get/set for volume and switch, HDMI IEC958 status changes including non-audio passthrough, updating controls while streams are active, validation of min/max boundaries, and route-specific card creation are important. Transport errors should be visible in logs without corrupting cached control values.
