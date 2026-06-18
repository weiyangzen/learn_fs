# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt-sysfs.c

## Purpose
Implements the RNBD client sysfs control plane. It registers the `rnbd-client` class, exposes a `ctl/map_device` attribute for creating remote block mappings, creates per-mapped-device sysfs state/control files below the block disk kobject, and maintains `/sys/.../devices` symlinks back to mapped disks.

## Important APIs, types, and functions
- `rnbd_clt_create_sysfs_files()` and `rnbd_clt_destroy_sysfs_files()` register/unregister the client class, `ctl` device, `map_device` attribute group, and `devices` kobject.
- `rnbd_clt_map_device_store()` parses a userspace mapping command and calls `rnbd_clt_map_device()`.
- `rnbd_clt_parse_map_options()` accepts `path=`, `device_path=`, `dest_port=`, `access_mode=`, `sessname=`, and `nr_poll_queues=` tokens into `struct rnbd_map_options`.
- Per-device attributes expose `state`, `nr_poll_queues`, `mapping_path`, `access_mode`, `session`, and writable `unmap_device`, `resize`, and `remap_device`.
- `rnbd_clt_add_dev_kobj()`, `rnbd_clt_add_dev_symlink()`, and `rnbd_clt_remove_dev_symlink()` attach client metadata to the mapped disk's sysfs tree and create/remove stable links named from `device_path@session`.

## Control flow
Module init in `rnbd-clt.c` calls `rnbd_clt_create_sysfs_files()`. A user writes a map string to `ctl/map_device`; the store path allocates address storage, parses tokens, builds RTRS paths, maps the device through the client core, then creates the per-device kobject and symlink. Per-device stores delegate behavior to the core: `unmap_device` calls `rnbd_clt_unmap_device()`, `resize` calls `rnbd_clt_resize_disk()`, and `remap_device` calls `rnbd_clt_remap_device()`.

## State and persistence behavior
State is kernel-resident only. Sysfs objects mirror live `struct rnbd_clt_dev` objects and vanish on unmap or module removal. The state attribute maps internal states to legacy strings: mapped reports `open`, disconnected reports `closed`, and unmapped reports `unmapped`. `blk_symlink_name` is allocated on symlink creation and freed on removal.

## Dependencies and integration points
Depends on Linux sysfs/kobject/device class APIs, parser helpers, RDMA address parsing through `rtrs_addr_to_sockaddr()`, and exported client-core functions in `rnbd-clt.h`. The sysfs lifetime is tightly coupled to `gendisk` kobjects and module references, especially during unmap and module exit.

## Risks and test signals
- `dest_port` is applied while parsing `path=` tokens, so a `dest_port=` appearing after a `path=` does not affect that earlier path.
- Mandatory option validation sets `ret = 0` for each present mandatory option, but still rejects when any mandatory option is missing; duplicate or unknown tokens are rejected.
- Only six paths are accepted; overflow returns `-ENOMEM`, which is semantically odd for a user input limit.
- Exercise map/unmap/remap/resize sysfs paths, invalid token handling, path count limits, symlink naming with slashes translated to `!`, forced unmap from the same sysfs file, and module unload races.
