# sources/distributed-fs/ceph-client/drivers/staging/most/video/video.c

## Purpose
Mostcore video component that exposes one RX sync/isoc MOST channel as a V4L2 read/poll capture node carrying compressed MPEG data.

## Important APIs, Types, And Functions
`struct most_video_dev` stores interface/channel identity, pending MBO list, mute flag, V4L2 device/video_device, open refcount, lock, and waitqueue. `struct comp_fh` tracks one file handle and read offset. Key functions are `comp_probe_channel()`, `comp_disconnect_channel()`, `comp_vdev_open()`, `comp_vdev_close()`, `comp_vdev_read()`, `comp_vdev_poll()`, `comp_rx_data()`, `comp_register_videodev()`, V4L2 ioctl handlers, `comp_init()`, and `comp_exit()`.

## Control Flow
Mostcore probes only RX sync or isoc channels, creates a `v4l2_device`, allocates/registers a `video_device`, and adds it to a global list. Open allows a single active client through `access_ref`, initializes a V4L2 file handle, and starts the MOST channel. RX completions append MBOs to `pending_mbos` unless muted and wake readers. Reads block unless nonblocking, copy data from the head MBO respecting per-file offset, and return MBOs when fully consumed. Close mutes completions, drains pending MBOs, stops the channel, and releases the file handle.

## State And Persistence
Runtime state includes pending MBO queues, read offsets, single-client refcount, mute flag, selected input, and global device list. `list_lock` protects global lookup; per-device `list_lock` protects MBO queues. No persistent storage exists.

## Dependencies And Integration Points
Depends on Mostcore component/configfs APIs, V4L2 core, video ioctl helpers, waitqueues, spinlocks, and user-copy APIs. It registers component `video`.

## Risks
The close path uses `mute` as a workaround because Mostcore can still deliver completions until stop; missed coordination can leak or lose MBOs. `data_ready()` is queried without always holding the queue lock. Format handling is minimal and fixed to MPEG with placeholder dimensions. Exit manually disconnects devices because core teardown lacks automatic disconnects.

## Test Signals
Probe rejects TX and non-sync/isoc channels; `/dev/video*` appears for valid channels; only one open succeeds; blocking and nonblocking reads behave correctly; poll signals readable on RX; partial reads preserve offsets; close drains MBOs without use-after-free; V4L2 querycap/format/input ioctls return expected values.
