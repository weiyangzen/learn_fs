# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1.c

## Purpose
This file implements the configfs USB Audio Class 1.0 gadget function named `uac1` using the shared `u_audio` engine. It exposes a virtual ALSA-backed audio function without requiring a physical codec. The implemented topology is configurable in both directions: USB OUT to ALSA capture, and ALSA playback to USB IN. It builds UAC1 AudioControl and AudioStreaming descriptors dynamically from `struct f_uac1_opts`, including optional feature units for mute and volume controls.

## Important APIs, types, and functions
`struct f_uac1` embeds `struct g_audio` and tracks the assigned AC, AS IN, and AS OUT interface numbers, current alternate settings, an EP0 setup copy, optional interrupt endpoint state, and current capture/playback sample rates. `f_audio_alloc_inst()` creates the configfs instance with defaults from `u_uac1.h`; `f_audio_alloc()` creates one function object and wires `bind`, `unbind`, `set_alt`, `get_alt`, `setup`, `disable`, `suspend`, and `free_func`. `f_audio_bind()` is the main descriptor and ALSA setup path. `setup_descriptor()`, `build_ac_header_desc()`, and `build_fu_desc()` patch class descriptors and descriptor arrays based on channel masks and feature-unit options. `f_audio_setup()` dispatches UAC1 class control requests to feature-unit handlers and endpoint sample-rate handlers. `f_audio_set_alt()` starts and stops `u_audio` capture/playback streams.

## Control flow
Allocation starts with configfs defaults and a refcount-protected option object. Binding validates channel masks, sample sizes, sample rates, and volume ranges; attaches strings; allocates dynamic AC and feature-unit descriptors; assigns interface IDs; autoconfigures optional interrupt, OUT isochronous, and IN isochronous endpoints; assigns FS/SS descriptors; copies options into `audio->params`; and calls `g_audio_setup()`. Runtime interface selection restarts the AC interrupt endpoint for alt 0 and maps AS OUT alt 1 to `u_audio_start_capture()` and AS IN alt 1 to `u_audio_start_playback()`. EP0 class requests read or update mute, volume, and endpoint sampling frequency, then queue the composite EP0 request.

## State and persistence
Persistent configuration lives in configfs attributes on `struct f_uac1_opts` until a function is linked; stores reject changes while `opts->refcnt` is nonzero. Runtime state is in `struct f_uac1`: alternate settings, `int_count`, interrupt endpoint pointer, and current sample rates. The actual audio data state lives in `u_audio` and ALSA objects created by `g_audio_setup()`. No on-disk persistence is implemented.

## Dependencies and integration points
The file depends on the composite gadget framework, Linux USB audio descriptor definitions, `u_audio.h`, and `u_uac1.h`. It integrates with configfs through generated `CONFIGFS_ATTR` attributes, with the ALSA-backed gadget audio layer through `g_audio_setup()`, `u_audio_start_*()`, `u_audio_stop_*()`, and `u_audio_set/get_*()` calls, and with host UAC1 control behavior through EP0 setup callbacks. It registers through `DECLARE_USB_FUNCTION_INIT(uac1, ...)`.

## Risks and edge cases
The static global descriptor objects and global dynamic descriptor pointers are patched during bind, so concurrent instances depend on configfs refcounting and gadget serialization to avoid cross-instance descriptor mutation. Rate-list configfs parsing clears the existing array before fully validating all tokens, so invalid input can leave an empty list while still under the lock. Endpoint sample-rate handling expects exactly three data bytes and recognizes hard-coded endpoint IDs `(USB_DIR_IN | 2)` and `(USB_DIR_OUT | 1)`, which is sensitive to descriptor layout assumptions. Unsupported entity/control combinations log errors and stall or return `-EOPNOTSUPP`.

## Test signals
Useful tests include configfs attribute read/write coverage before and after linking, invalid channel mask/sample size/rate/volume validation, enumeration on FS and SS gadgets with IN-only, OUT-only, and duplex settings, UAC1 host GET/SET mute and volume requests, sample-rate SET_CUR requests, altsetting stream start/stop, suspend/disable cleanup, and interrupt notification throttling via `UAC1_DEF_INT_REQ_NUM`.
