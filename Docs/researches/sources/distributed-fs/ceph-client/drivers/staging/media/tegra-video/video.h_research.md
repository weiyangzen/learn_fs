# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.h

## Purpose
Declares the aggregate Tegra video device shared by top-level host1x, VI, CSI, and VIP modules.

## Important APIs, Types, And Functions
`struct tegra_video_device` contains the root `v4l2_device`, `media_device`, and pointers to initialized VI and CSI clients. It declares TPG node setup/cleanup and extern platform drivers `tegra_vi_driver`, `tegra_vip_driver`, and `tegra_csi_driver`.

## Control Flow
`video.c` creates the aggregate object; VI and CSI host1x init store their pointers into it; TPG setup consumes both pointers to create links and nodes.

## State And Persistence
Runtime-only aggregate state. Lifetime is tied to the V4L2 device release path.

## Dependencies And Integration Points
Depends on host1x, media device, V4L2 device, and `vi.h`. Included by top-level, VI, CSI, and VIP files.

## Risks And Test Signals
Pointers may be temporarily NULL depending on host1x child init ordering; TPG setup explicitly checks this. Test signals are host1x child ordering, TPG setup, and removal ordering.
