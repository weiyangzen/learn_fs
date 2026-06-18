# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv.h

## Purpose
Declares RNBD server data structures and cross-file APIs shared by the server core and sysfs implementation.

## Important APIs, types, and functions
- `struct rnbd_srv_session` contains the RTRS server session pointer, session name, queue depth, per-session xarray id map, mutex, and negotiated protocol version.
- `struct rnbd_srv_dev` represents one backing block device shared across sessions, with sysfs kobjects, kref, name, session-device list, lock, and write-open count.
- `struct rnbd_srv_sess_dev` binds a session to a device and file, including kobject, numeric device id, `keep_id`, readonly flag, kref, destruction completion, path, and access mode.
- Declares force close, sysfs create/destroy helpers, and `rnbd_destroy_sess_dev()`.

## Control flow
The server core allocates and fills these objects, while sysfs code exposes and releases them. Kobject release of a session-device calls back into `rnbd_destroy_sess_dev()`, so this header is the ownership contract between sysfs and core.

## State and persistence behavior
All structures represent live kernel state. Krefs protect backing devices and session-device bindings; the xarray maps server-side ids to session-device references. `destroy_comp` lets destruction wait for inflight I/O references to drain.

## Dependencies and integration points
Includes Linux IDR/kref, RTRS, RNBD protocol, and RNBD logging. Consumed by `rnbd-srv.c`, `rnbd-srv-sysfs.c`, `rnbd-srv-trace.c`, and `rnbd-log.h`.

## Risks and test signals
Lifetime fields are security-sensitive because RDMA completions, sysfs release, and disconnect can all converge. Tests should combine sysfs force-close, client close, and inflight I/O while checking for xarray/kref leaks or premature frees.
