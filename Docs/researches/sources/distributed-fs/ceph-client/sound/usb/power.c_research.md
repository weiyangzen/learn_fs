# sources/distributed-fs/ceph-client/sound/usb/power.c

Purpose: UAC3 power-domain discovery and state management for usb-audio streams.

Important APIs, types, and functions: implements `snd_usb_find_power_domain()` and `snd_usb_power_domain_set()`. It parses `UAC3_POWER_DOMAIN` class-specific interface descriptors, allocates `struct snd_usb_power_domain`, records the domain ID, D1-to-D0 and D2-to-D0 recovery times, and sends UAC3 power-domain get/set control requests.

Control flow: `snd_usb_find_power_domain()` scans the control interface extra descriptors, validates UAC3 descriptors, and returns a newly allocated domain object when the requested entity ID appears in `baEntityID`. `snd_usb_power_domain_set()` reads the current state through a class-specific interface request, returns early if already in the requested state, otherwise writes the new state and delays after D1/D2 to D0 transitions according to descriptor recovery time.

State and persistence: the returned domain object is heap state attached elsewhere to stream/substream structures. Actual persistence is device-side power-domain state. The function does not cache current state, so each set request queries hardware first.

Dependencies and integration points: used by `pcm.c` for stream suspend/resume/open/close transitions. Depends on UAC3 descriptor definitions, descriptor validation helpers, and `snd_usb_ctl_msg()`.

Risks: invalid or missing descriptors produce no domain and silently disable this feature for a stream. D0 recovery uses `udelay(pd_rec * 50)`, so large descriptor values can busy-wait. Returning `-EINVAL` for unexpected previous state after a successful set can surprise callers even though the device was commanded.

Test signals: UAC3 devices with power-domain descriptors should transition to D0 during prepare/hw_params, D1 on close/resume, and D2 on suspend; logs should show get/set failures for broken devices; descriptor fuzzing should not read past `extra` data.
