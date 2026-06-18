# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1_legacy.c

## Purpose
This file implements the older `uac1_legacy` USB Audio Class 1.0 function. Unlike the modern UAC1 function, it does not use the newer `g_audio`/`u_audio` parameter model for both directions. It exposes a fixed UAC1 descriptor topology with one AudioControl interface, one playback-oriented AudioStreaming interface, one isochronous OUT endpoint, and a simple feature unit for mute and volume.

## Important APIs, types, and functions
`struct f_audio` embeds `struct gaudio`, tracks AC/AS interface state, owns the OUT endpoint, maintains a spinlock-protected playback queue, and stores the active class-specific SET control. `struct f_audio_buf` is the temporary buffer queued to deferred playback work. `f_audio_set_alt()` enables the OUT endpoint and prequeues USB requests. `f_audio_out_ep_complete()` accumulates USB OUT data into `audio->copy_buf` and schedules `f_audio_playback_work()` when a buffer is full. `audio_set_intf_req()` and `audio_get_intf_req()` implement class requests over the feature-unit control list. `control_selector_init()` installs the static mute and volume controls, backed by `generic_set_cmd()` and `generic_get_cmd()`.

## Control flow
`f_audio_alloc_inst()` creates a configfs instance with request buffer size, request count, audio buffer size, and ALSA file path options. `f_audio_alloc()` allocates the function, initializes the queue, lock, control selector list, and playback work. `f_audio_bind()` initializes the ALSA gadget once per options object with `gaudio_setup()`, assigns string and interface IDs, builds descriptors from the playback parameters reported by `u_audio_get_playback_*()`, autoconfigures the OUT endpoint, and assigns FS descriptors. When the host selects AS alt 1, the function enables the endpoint, allocates an accumulation buffer, allocates and queues `req_count` OUT requests, and then cycles each completion back to the endpoint. Switching back to alt 0 queues any partial copy buffer to playback work.

## State and persistence
Configuration is stored in `struct f_uac1_legacy_opts` and locked by `opts->lock`; stores reject changes while the function is referenced. Runtime audio data is buffered in heap-allocated `f_audio_buf` objects on `play_queue` and drained by a workqueue callback into `u_audio_playback()`. Control values are kept in the static `usb_audio_control.data[]` arrays rather than persisted or synchronized to a real mixer.

## Dependencies and integration points
The file depends on `u_uac1_legacy.h`, the composite gadget framework, and the older `gaudio` helper API. Its configfs attributes expose low-level buffering knobs and legacy ALSA file names. It registers as `uac1_legacy` with `DECLARE_USB_FUNCTION_INIT`. The USB host-visible surface is static UAC1 descriptors and class requests for interface and endpoint controls.

## Risks and edge cases
The implementation is narrow: comments note only playback support, descriptors are mostly static, and `f_audio_disable()` is empty. The OUT request allocation path does not unwind already queued requests on a later allocation failure. The string attribute store appears inverted: it treats a non-NULL `kstrndup()` result as `-ENOMEM`, preventing updates and leaking the successful allocation path intent. Control request lookup can leave `set_con` NULL while still accepting the data stage, causing the completion to ignore the payload. Static control descriptors and control objects are shared across instances.

## Test signals
Exercise configfs buffer attributes, invalid writes while linked, enumeration of the fixed AC/AS descriptor set, alt 1 enable with different request counts and buffer sizes, continuous OUT streaming and queue rollover, alt 0 partial-buffer flush, mute/volume GET and SET requests, and disconnect/unbind behavior while OUT requests are queued.
