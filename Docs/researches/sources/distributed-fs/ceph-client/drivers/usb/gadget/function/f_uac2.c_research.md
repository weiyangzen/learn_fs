# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac2.c

## Purpose
This file implements the USB Audio Class 2.0 gadget function named `uac2`. It exposes configurable UAC2 playback and capture paths backed by `u_audio`, with UAC2 clock sources, optional feature units, isochronous streaming endpoints, optional asynchronous feedback for capture, and FS/HS/SS descriptor sets.

## Important APIs, types, and functions
`struct f_uac2` embeds `struct g_audio`, tracks interface and alternate-setting state, stores a setup request copy, owns an optional interrupt endpoint, and records a transient clock ID while handling sample-rate SET_CUR. `afunc_alloc_inst()` creates default `struct f_uac2_opts` configfs state. `afunc_bind()` validates options, builds and patches descriptors, computes endpoint packet sizes, autoconfigures endpoints, assigns descriptors, fills `g_audio` parameters, and registers the virtual ALSA card. `set_ep_max_packet_size_bint()` and `get_max_bw_for_bint()` calculate bandwidth requirements from channel count, sample size, sample rates, feedback margin, speed, and bInterval. `in_rq_cur()`, `in_rq_range()`, `out_rq_cur()`, and `uac2_cs_control_sam_freq()` implement UAC2 class control requests.

## Control flow
Binding validates channel masks, sample sizes, sample rates, volume ranges, and HS/SS bInterval options. It attaches strings, creates feature-unit descriptors when mute or volume is enabled, assigns terminal, feature-unit, and clock IDs, assigns interface numbers, chooses capture sync mode, computes FS/HS/SS packet sizes, autoconfigures OUT, feedback IN, audio IN, and optional interrupt endpoints, copies endpoint addresses across speed descriptors, builds descriptor arrays, and calls `g_audio_setup()`. At runtime, AC alt 0 restarts the interrupt endpoint; AS OUT alt 1 starts capture; AS IN alt 1 starts playback; disabling resets alt state and stops both streams.

## State and persistence
Configfs options persist in memory under `opts->lock` until the function instance is freed; stores return `-EBUSY` while linked. Runtime state includes current altsettings, endpoint enablement, notification request count, and clock-control request context. Current sample rate, mute, and volume values are delegated to `u_audio`. There is no persistent storage beyond configfs state.

## Dependencies and integration points
The file depends on USB audio v2 descriptor definitions, the composite gadget framework, `u_audio.h`, and `u_uac2.h`. It integrates with `u_audio` for PCM streaming and control values, configfs for options, and the host through UAC2 class-specific interface requests. It registers with `DECLARE_USB_FUNCTION_INIT(uac2, ...)`.

## Risks and edge cases
Descriptor templates are static globals patched at bind time, with dynamic global feature-unit pointers; multi-instance behavior is sensitive to bind/unbind serialization. The rate-list configfs parser does not bound `i` before writing into the fixed-size array, so malformed long lists are risky. Several error returns after feature-unit allocation in `afunc_bind()` return directly instead of going through cleanup labels, which can leak descriptors on rare failures. Packet-size calculation clamps and warns when bandwidth exceeds endpoint limits, which may enumerate but drop audio. Unsupported controls return `-EOPNOTSUPP` or log TODO messages.

## Test signals
Test UAC2 enumeration on FS, HS, SS, and SSP; duplex, IN-only, and OUT-only configurations; adaptive versus async capture; feedback endpoint presence; bInterval auto and fixed settings; high sample-rate packet-size warnings; class GET_CUR/GET_RANGE for clocks and volume; SET_CUR for clock frequency, mute, and volume; interrupt notifications; and configfs mutation rejection while active.
