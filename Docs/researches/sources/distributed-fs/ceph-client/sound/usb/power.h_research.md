# sources/distributed-fs/ceph-client/sound/usb/power.h

Purpose: public internal contract for UAC3 power-domain support in usb-audio.

Important APIs, types, and data: defines `struct snd_usb_power_domain`, state constants `UAC3_PD_STATE_D0`, `UAC3_PD_STATE_D1`, and `UAC3_PD_STATE_D2`, and prototypes for `snd_usb_power_domain_set()`, `snd_usb_find_power_domain()`, `snd_usb_autoresume()`, and `snd_usb_autosuspend()`.

Control flow: stream parsing code can find a domain by entity ID, PCM code can set power states around runtime activity, and callers use autosuspend/autoresume helpers to manage USB runtime PM around ALSA open/close or offload stream setup.

State and persistence: the struct holds the power domain ID, recovery timings, and control interface pointer needed to issue later requests. It does not include locking or refcounting, so ownership is handled by the containing usb-audio objects.

Dependencies and integration points: integrates with UAC3 descriptor parsing in `power.c`, PCM lifecycle in `pcm.c`, and card-level runtime PM helpers implemented elsewhere in usb-audio.

Risks: callers must not use a domain after its control interface is gone. State constants are local enum values expected by `power.c` and should remain aligned with the UAC3 request semantics used there.

Test signals: compile users of the prototypes, runtime PM balance across open/close/offload enable/disable, and valid D0/D1/D2 requests on UAC3 hardware.
