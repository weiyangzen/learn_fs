# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-cap.h

Purpose: public capture-side declaration header for Vivid video support. It exposes capture queue ops, format helpers, selection/pixel-aspect operations, input/audio/tuner controls, TV standard and DV timing ioctls, EDID programming, frame size/interval enumeration, and stream parameter handlers.

Important symbols include `vivid_update_quality`, `vivid_update_format_cap`, `vivid_update_outputs`, `vivid_update_connected_outputs`, `vivid_get_video_aspect`, `vivid_standard`, `vivid_ctrl_standard_strings`, `vivid_vid_cap_qops`, and the `vidioc_*`/`vivid_vid_cap_*` entry points wired into the V4L2 ioctl table elsewhere. It has no persistent state of its own; all state is in `struct vivid_dev` and related V4L2/vb2 objects used by implementation files.

Dependencies are implicit forward declarations from included vivid core headers in includers plus V4L2 types such as `struct file`, `struct v4l2_format`, `v4l2_std_id`, and `struct vb2_ops`. Risks are declaration/implementation drift and keeping `vivid_standard` in sync with its strings. Test signal is compile coverage plus V4L2 ioctl registration paths that depend on exact prototypes.
