# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-sysfs.c

## Purpose
Creates and destroys server sysfs objects for sessions, paths, path attributes, disconnect control, and stats.

## Important APIs, Types, And Functions
Exports `rtrs_srv_create_path_files()` and `rtrs_srv_destroy_path_files()`. Defines kobject release callbacks for paths and stats, attributes `disconnect`, `hca_port`, `hca_name`, `src_addr`, `dst_addr`, and the generated `rdma` stats attribute. Helper functions create/destroy one-time session root folders and per-path stats files.

## Control Flow
When the server completes info request processing, it calls `rtrs_srv_create_path_files()`. This registers the session device under class `rtrs-server` once, creates a `paths` kobject, adds a path kobject named from source/destination addresses, attaches path attributes, and then adds a `stats` child. Writing `1` to `disconnect` removes that sysfs file first with `sysfs_remove_file_self()` and queues path close to avoid deadlock.

## State And Persistence
Sysfs mirrors live in-memory server session/path state. `dev_ref` counts active path users of the session device. Kobject release frees `srv_path`; stats kobject release frees per-CPU stats and the stats object.

## Dependencies And Integration Points
Depends on `rtrs-pri.h`, `rtrs-srv.h`, `rtrs-log.h`, address formatting from `rtrs.c`, `close_path()` from server core, and stats helpers from `rtrs-srv-stats.c`.

## Risks
Kobject/device reference ordering is delicate, especially on error unwind and disconnect from sysfs. Attribute names expose address formatting choices as ABI. `src_addr`/`dst_addr` intentionally present peer/local directions from the server perspective and can be confusing.

## Test Signals
Check sysfs tree creation/removal across first and additional paths, read all attributes, write disconnect, stats reset/read, error injection in kobject creation, and close during active IO.
