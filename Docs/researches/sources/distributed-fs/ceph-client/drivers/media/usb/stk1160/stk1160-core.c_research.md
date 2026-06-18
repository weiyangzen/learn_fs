
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-core.c

## Purpose
`stk1160-core.c` is the USB probe, register-access, device-reset, and teardown core for STK1160 USB video capture devices.

## Important APIs, Types, and Functions
Important functions are `stk1160_read_reg()`, `stk1160_write_reg()`, `stk1160_select_input()`, `stk1160_reg_reset()`, `stk1160_scan_usb()`, `stk1160_probe()`, `stk1160_disconnect()`, and the v4l2 release callback `stk1160_release()`. The module parameter `input` selects the default input. USB ID support is `05e1:0408`.

## Control Flow
Probe rejects USB audio-class interfaces, allocates an alternate-setting packet-size table, scans all endpoints for video/audio isochronous endpoints, allocates `struct stk1160`, initializes vb2, locks, and V4L2 controls, registers the V4L2 device, registers the STK1160 I2C adapter, creates the SAA711x decoder subdevice, resets and stops the decoder, programs STK1160 reset defaults, selects the configured input, performs optional AC97 setup, and finally registers the video node. Disconnect clears interface data, takes vb2 and V4L locks, uninitializes isochronous URBs, returns queued buffers with errors, unregisters the video node, disconnects the V4L2 device, sets `udev` to NULL for active users, and drops the V4L2 device reference.

## State and Persistence
Runtime state is stored in `struct stk1160`: USB handle, altsetting packet sizes, current alternate, selected input, norm, frame size, format, vb2 queue, I2C adapter/client, SAA711x subdevice, locks, and isochronous control. Hardware register state is programmed at probe by `stk1160_reg_reset()` and input selection. There is no persistent storage.

## Dependencies and Integration Points
The file integrates Linux USB control messages, V4L2 core, SAA711x I2C subdevice probing, the internal STK1160 I2C bridge, videobuf2 setup from `stk1160-v4l.c`, isochronous teardown from `stk1160-video.c`, and AC97 setup from `stk1160-ac97.c`.

## Risks and Edge Cases
Probe must register the video device last so users cannot race partially initialized state. `stk1160_scan_usb()` warns but still allows non-high-speed devices, where streaming may be unreliable. Input selection depends on fixed GPIO values and SAA7115 routing. Disconnect relies on lock ordering and `udev = NULL` to make active file operations fail safely. `stk1160_release()` unregisters I2C and V4L2 resources only after all references are gone.

## Test Signals
Test probe on video and audio interfaces, high-speed and full-speed ports, all alternate settings and packet-size detection, SAA711x subdevice creation, default input parameter, clean disconnect during idle and streaming, and V4L2 device reference release after user file descriptors close.
