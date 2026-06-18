# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_pool_os.c

Linux pool device-labeling support. It handles EFI/GPT partition creation for whole disks, relabeling expanded devices, and post-label validation.

Key behavior:
- `zpool_relabel_disk()` opens a device, calls `efi_use_whole_disk()`, fsyncs, flushes block buffers, and tolerates `VT_ENOSPC`.
- `read_efi_label()` and `find_start_block()` inspect current vdev config to preserve an existing partition start offset when replacing or expanding devices.
- `zpool_label_disk()` creates GPT partition 0 for ZFS data and partition 8 as reserved space, aligned for logical sector size.
- `zpool_label_name()` generates unique `zfs-<hex>` partition labels from `/dev/urandom` or `rand()`.
- After writing the label, the code triggers/rescans partition state, waits for udev-visible paths, then rereads the label to validate it.

Failure paths report specific libzfs errors such as open failure, no capacity, label failure, or undersized partition.
