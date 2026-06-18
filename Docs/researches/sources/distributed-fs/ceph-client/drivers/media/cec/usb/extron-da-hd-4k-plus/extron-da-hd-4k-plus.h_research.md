# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.h

## Purpose
This header defines global and per-port state for the Extron DA HD 4K Plus driver.

## Important APIs, Types, and Functions
`struct extron_port` embeds `struct cec_splitter_port`, a CEC adapter, V4L2 video device/control handler, EDID buffers and capability flags, command completion fields, queued CEC RX messages, TX status, physical address update fields, signal/EDID hotplug flags, and a video-device mutex. `struct extron` embeds the splitter, serio connection, port arrays, unit metadata, V4L2 device, setup thread, delayed EDID work, EDID serialization state, command completions, and serial buffers.

## Control Flow
The implementation allocates `struct extron` at serio connect and allocates one `struct extron_port` per HDMI port during setup. The fields coordinate serial command waits, interrupt-to-workqueue delivery, EDID reads/writes, V4L2 controls, and CEC adapter callbacks.

## State and Persistence
All structure fields are runtime state except EDID data and device configuration that may be mirrored from or written to hardware. Spinlocks protect RX queue counters; mutexes serialize video-device and serial/EDID operations.

## Dependencies and Integration Points
The header includes CEC, V4L2, serio, kthread, workqueue, and local `cec-splitter.h` APIs. It is private to the Extron module.

## Risks and Test Signals
Because many flags are shared between interrupt and workqueue contexts, locking coverage around `msg_lock`, `video_lock`, `serio_lock`, and `edid_lock` is central. Tests should exercise disconnect cleanup of registered vs unregistered adapters and queued work cancellation.
