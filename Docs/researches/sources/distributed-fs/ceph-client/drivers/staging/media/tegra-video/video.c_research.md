# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.c

## Purpose
Implements the top-level `tegra-video` host1x driver and module init/exit that bind VI, CSI, and VIP platform clients into one V4L2/media device.

## Important APIs, Types, And Functions
`tegra_v4l2_dev_release()` cleans VI channels, unregisters V4L2/media devices, and frees the aggregate device. `tegra_v4l2_dev_notify()` forwards V4L2 subdev events to the video node and marks the vb2 queue errored on source changes during streaming. `host1x_video_probe()` allocates `tegra_video_device`, initializes/registers media and V4L2 devices, calls `host1x_device_init()`, and optionally creates TPG nodes. `host1x_video_remove()` tears down TPG, exits host1x, and drops the V4L2 device ref. Module init registers host1x and platform drivers for CSI/VIP/VI.

## Control Flow
Module load registers the aggregate host1x driver first, then platform drivers. Host1x probe creates media/V4L2 roots before child clients initialize. Remove unregisters child/platform state via host1x exit, with final channel cleanup deferred to V4L2 release.

## State And Persistence
Owns the aggregate `tegra_video_device` lifetime and stores it as host device driver data. No persistent storage.

## Dependencies And Integration Points
Depends on host1x core, platform driver registration, V4L2 device/media device APIs, and platform drivers declared in `video.h`.

## Risks And Test Signals
Registration unwind paths must avoid leaks and double cleanup, especially with TPG setup failure. Event forwarding assumes subdev hostdata points to a valid VI channel. Test signals include module load/unload, probe failure injection at media/V4L2/host1x/TPG stages, source-change event delivery, and open file descriptors across device removal.
