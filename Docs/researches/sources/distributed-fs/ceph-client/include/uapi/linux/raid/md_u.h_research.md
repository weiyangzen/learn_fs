<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_u.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_u.h

Purpose: defines the legacy MD RAID userspace ioctl ABI between raidtools/mdadm and kernel RAID drivers.

Important APIs and types: version constants describe major/minor/patchlevel compatibility. Ioctls cover status (`RAID_VERSION`, `GET_ARRAY_INFO`, `GET_DISK_INFO`, `GET_BITMAP_FILE`), configuration (`CLEAR_ARRAY`, `ADD_NEW_DISK`, `SET_ARRAY_INFO`, `SET_BITMAP_FILE`, hot add/remove/fault), and usage (`RUN_ARRAY`, `STOP_ARRAY`, `STOP_ARRAY_RO`, `RESTART_ARRAY_RW`, `CLUSTERED_DISK_NACK`). Payload structs include `mdu_version_t`, `mdu_array_info_t`, `mdu_disk_info_t`, `mdu_start_info_t`, `mdu_bitmap_file_t`, and `mdu_param_t`.

Control flow: management tools open an MD device and issue ioctls to inspect, configure, start, stop, or modify arrays. Kernel MD code mutates in-memory array/disk state and writes persistent metadata through lower layers.

State and persistence: ioctl-visible state includes array geometry, disk membership, active/failed/spare counts, layout, chunk size, bitmap file, and running/stopped state. Durable metadata is stored in MD superblocks or external metadata, not in this header.

Dependencies and integration points: depends on MD ioctl magic from surrounding RAID headers and integrates with MD core, mdadm, block devices, bitmaps, clustered MD, and RAID personalities.

Risks and test signals: risks include legacy ioctl compatibility, device-number assumptions, unsafe hot-remove/fault operations, stale bitmap paths, and mismatch between ioctl state and superblock metadata. Test mdadm ioctl paths, array start/stop/read-only transitions, disk add/remove/fault, bitmap file set/get, and version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_u.h -->
