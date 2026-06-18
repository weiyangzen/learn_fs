# sources/distributed-fs/ceph-client/drivers/input/misc/uinput.c

## Purpose
`uinput.c` implements `/dev/uinput`, the userspace interface for creating virtual input devices, injecting input events, and servicing force-feedback upload/erase requests from the kernel input core back to userspace.

## Important APIs, Types, and Functions
`struct uinput_device` stores the virtual `input_dev`, lifecycle state, mutex, event ring buffer, wait queues, FF request slots, and locks. `struct uinput_request` represents pending FF upload/erase requests. Core paths are `uinput_open()`, `uinput_write()`, `uinput_read()`, `uinput_poll()`, `uinput_ioctl_handler()`, `uinput_create_device()`, and `uinput_destroy_device()`. Setup helpers include `uinput_dev_setup()`, `uinput_abs_setup()`, legacy write setup, and validation helpers. FF callbacks include `uinput_dev_upload_effect()`, `uinput_dev_erase_effect()`, and request submit/flush helpers.

## Control Flow
Opening `/dev/uinput` allocates a fresh `uinput_device`. Userspace either configures capabilities with ioctls plus `UI_DEV_SETUP`/`UI_ABS_SETUP` or writes legacy `struct uinput_user_dev`, then calls `UI_DEV_CREATE`. Creation validates abs/MT/FF configuration, installs input callbacks, registers the virtual input device, and marks state `UIST_CREATED`. After creation, writes inject one or more `struct input_event` records into the virtual device. Input-core output events and FF requests are queued into the small ring or request table so userspace can read events and complete FF ioctls. `UI_DEV_DESTROY`, close, or release tears the device down and flushes outstanding requests.

## State and Persistence Behavior
State transitions are `UIST_NEW_DEVICE`, `UIST_SETUP_COMPLETE`, and `UIST_CREATED`. Device name/phys strings are heap-owned and freed on destroy. Event output uses a 16-entry circular buffer protected by the input device event lock. FF requests use 16 slots, completions, and 30-second timeouts. The virtual input device persists in input core only between `UI_DEV_CREATE` and destroy/close.

## Dependencies and Integration Points
The file depends on the input core, miscdevice registration, UAPI `linux/uinput.h`, compat input conversion helpers, multitouch helpers, poll/read/write/ioctl file operations, and force-feedback core. It registers misc minor `UINPUT_MINOR` and devname `uinput`, consumed by libevdev, libinput tests, compositors, and other userspace virtual-device creators.

## Risks and Edge Cases
The output ring overwrites old unread events when full because head advances without tail management. State changes require careful lock ordering between `mutex`, `state_lock`, input `event_lock`, and request locks. FF requests time out after 30 seconds and must be completed or flushed during teardown to avoid hung input-core callers. Legacy and modern setup paths must keep abs validation consistent. Timestamp injection accepts only recent nonfuture timestamps, silently ignoring invalid ones. Compat FF upload copies truncated compat structures and intentionally does not support custom periodic waveforms.

## Test Signals
Test modern and legacy device creation, all `UI_SET_*BIT` ioctls, `UI_ABS_SETUP` size variants, invalid abs ranges and MT slot counts, event injection/read/poll, nonblocking behavior, timestamp acceptance/rejection, `UI_GET_SYSNAME`, FF upload/erase begin/end/timeout/flush, compat ioctls, destroy during pending requests, and close without explicit destroy.
