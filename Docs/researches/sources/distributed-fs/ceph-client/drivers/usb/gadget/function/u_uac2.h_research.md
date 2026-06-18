## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac2.h

Purpose: declares defaults and configfs option state for the USB Audio Class 2 gadget function that uses `u_audio`.

Important APIs and types:
- Defaults define playback/capture channel masks, sample rates, sample sizes, high-speed bInterval defaults, capture sync mode, feature-unit mute/volume defaults, request counts, interrupt request count, and terminal types.
- `struct f_uac2_opts` embeds `usb_function_instance`, playback/capture audio parameters, capture sync and high-speed intervals, feature-unit settings, request count, feedback max drift, bound flag, configurable string names, playback/capture terminal types, `lock`, and `refcnt`.

Control flow and integration:
- The UAC2 function uses these options to build UAC2 descriptors, calculate endpoint bandwidth and feedback capabilities, and fill `uac_params` for `g_audio_setup()`.
- `fb_max` affects allowed faster-side pitch and endpoint bandwidth.

State and persistence:
- Per-instance configfs state in memory. Rate arrays are bounded by `UAC_MAX_RATES` and must be zero-terminated.
- String name buffers persist in the options object and map to USB string descriptors.

Dependencies:
- USB composite, `uac_common.h`, and `u_audio` implementation.

Risks:
- UAC2 async/sync endpoint behavior depends on `c_sync`, feedback endpoint descriptors, and `fb_max`; inconsistent options can cause host drift or bandwidth issues.
- Terminal type fields are `s16` but defaults are positive USB terminal constants; validation should reject invalid negative or out-of-range values.
- bInterval defaults of 0 must be interpreted carefully by descriptor code.

Test signals:
- Enumerate UAC2 at full/high/super-capable controllers, test playback/capture rates, feedback, terminal names/types, and feature-unit controls.
- Validate endpoint max packet calculations for high sample rates/channel counts.
