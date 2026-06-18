## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1.h

Purpose: declares defaults and configfs option state for the modern USB Audio Class 1 gadget function that uses `u_audio`.

Important APIs and types:
- Defaults define UAC1 packet size, capture/playback channel masks, sample rates, sample sizes, request counts, interrupt request count, mute/volume presence, and default volume range/resolution.
- `struct f_uac1_opts` embeds `usb_function_instance`, capture/playback channel masks, rate arrays, sample sizes, playback/capture feature-unit mute/volume settings, request count, bound flag, configurable function/terminal/channel/feature-unit names, `lock`, and `refcnt`.

Control flow and integration:
- Configfs fills this options object. The UAC1 function converts it into descriptors and `struct uac_params` for `g_audio_setup()`.
- `bound`/`refcnt` protect descriptor-affecting options from mutation while active.

State and persistence:
- Per-instance in-memory configfs state. Rate arrays are bounded by `UAC_MAX_RATES`.
- Name arrays are fixed-size `USB_MAX_STRING_LEN` buffers.

Dependencies:
- USB composite and `uac_common.h`; integrates with `u_audio.h` in the function implementation.

Risks:
- Rate arrays require validation and zero termination.
- Volume values use 1/256 dB units; configfs conversions must preserve signed bounds and nonzero resolution.
- Endpoint bandwidth depends on channel mask, sample size, and max sample rate.

Test signals:
- Enumerate UAC1 with default and custom capture/playback settings, validate descriptors, ALSA card behavior, and host class control requests.
- Exercise name customization and feature-unit presence toggles.
