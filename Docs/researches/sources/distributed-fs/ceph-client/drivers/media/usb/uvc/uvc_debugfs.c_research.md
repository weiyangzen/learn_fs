# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_debugfs.c

Purpose: provides debugfs support for UVC stream statistics. It creates a global `uvcvideo` debugfs directory and per-stream directories containing a read-only `stats` file.

Important APIs and functions: public functions are `uvc_debugfs_init`, `uvc_debugfs_cleanup`, `uvc_debugfs_init_stream`, and `uvc_debugfs_cleanup_stream`. File operations are `uvc_debugfs_stats_open`, `uvc_debugfs_stats_read`, and `uvc_debugfs_stats_release`, backed by `uvc_debugfs_stats_fops`. The per-open buffer type is `struct uvc_debugfs_buffer`.

Control flow: module init calls `uvc_debugfs_init` to create the root under `usb_debug_root`. Stream registration calls `uvc_debugfs_init_stream`, which names the directory from USB bus number, device number, and streaming interface number, then creates `stats`. Opening `stats` allocates a 1024-byte buffer and snapshots `uvc_video_stats_dump`; reads copy that snapshot through `simple_read_from_buffer`; release frees the buffer. Stream unregister and module cleanup remove debugfs trees recursively.

State and persistence: the global root dentry and per-stream `debugfs_dir` pointers are transient. Stats contents are snapshotted per open, not live-updated during a read. Nothing persists outside debugfs.

Dependencies and integration points: depends on Linux debugfs, USB debug root, and `uvc_video_stats_dump` from the streaming implementation. It is called from UVC module init/exit and from stream video registration/unregistration in `uvc_driver.c`.

Risks: debugfs creation failures are not checked, which is normal for optional diagnostics but means absent files are not fatal. The fixed 1024-byte stats buffer can truncate future statistics if `uvc_video_stats_dump` grows. Directory names can collide only if bus/device/interface tuples collide, which USB core should prevent for live devices.

Test signals: mount debugfs, load UVC, stream from a camera, verify `/sys/kernel/debug/usb/uvcvideo/<bus>-<dev>-<intf>/stats` appears, read it before and after streaming errors, and confirm cleanup on disconnect and module unload.
