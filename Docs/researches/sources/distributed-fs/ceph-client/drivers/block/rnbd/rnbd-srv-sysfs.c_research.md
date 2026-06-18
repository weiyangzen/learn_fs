# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-sysfs.c

## Purpose
Implements the RNBD server sysfs representation. It creates the `rnbd-server` class with a `ctl` device, a `devices` kobject, one kobject per exported backing block device, and one child kobject per client session using that device.

## Important APIs, types, and functions
- `rnbd_srv_create_sysfs_files()` and `rnbd_srv_destroy_sysfs_files()` manage the server class, control device, and root `devices` kobject.
- `rnbd_srv_create_dev_sysfs()` creates a device kobject and `block_dev` symlink to the backing disk.
- `rnbd_srv_create_dev_session_sysfs()` adds per-session entries below `device/sessions`.
- Session attributes expose `read_only`, `access_mode`, `mapping_path`, and writable `force_close`.
- Release callbacks `rnbd_srv_dev_release()` and `rnbd_srv_sess_dev_release()` free server device objects or call `rnbd_destroy_sess_dev()`.

## Control flow
The server core lazily creates device sysfs files after successfully opening a backing block device. It then creates the per-session kobject before linking the session-device into the device's list. `force_close` removes its own sysfs file first to avoid deadlock, destroys session sysfs, and lets kobject release close the session-device.

## State and persistence behavior
Sysfs state mirrors in-memory `rnbd_srv_dev` and `rnbd_srv_sess_dev` objects. Kobject release is part of the destruction path: removing a session kobject ultimately closes the block device file, updates write-open counters, removes xarray ids, and frees memory in server core.

## Dependencies and integration points
Uses Linux kobject/sysfs/device class APIs and server core functions in `rnbd-srv.h`. It integrates with `disk_to_dev()` for backing disk symlinks and with module-param-visible server state through the core.

## Risks and test signals
Kobject lifetime and `force_close` self-removal are the main risks. Tests should force-close active sessions, close from client and server simultaneously, unload the module with open exports, and verify `block_dev` links and `sessions` directories are removed without warnings.
