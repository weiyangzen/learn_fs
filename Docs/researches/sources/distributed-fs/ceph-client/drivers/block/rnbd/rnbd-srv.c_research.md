# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv.c

## Purpose
Implements the RNBD server. It accepts RTRS server sessions, opens requested local block devices, enforces access-mode sharing rules, maps per-session device ids to backing devices, translates remote I/O messages into local bios, and cleans up exports on close/disconnect/module unload.

## Important APIs, types, and functions
- Module parameters: `port_nr` for RTRS listen port and `dev_search_path` for resolving client `dev_name` values, including `%SESSNAME%` namespace substitution.
- Session lifecycle: `create_sess()`, `destroy_sess()`, and `rnbd_srv_link_ev()`.
- I/O path: `rnbd_srv_rdma_ev()`, `process_rdma()`, and `rnbd_dev_bi_end_io()`.
- Admin path: `process_msg_sess_info()`, `process_msg_open()`, `process_msg_close()`.
- Device/session-device lifecycle: `rnbd_sess_dev_alloc()`, `rnbd_srv_get_or_create_srv_dev()`, `rnbd_srv_create_set_sess_dev()`, `rnbd_destroy_sess_dev()`, and `destroy_device()`.
- Access enforcement lives in `rnbd_srv_check_update_open_perm()`: many RO opens, one RW open, or two migration writers.

## Control flow
Module init validates protocol layout, opens an RTRS server context, and creates sysfs. RTRS connect creates a `rnbd_srv_session` with an xarray for device ids. `RNBD_MSG_SESS_INFO` negotiates protocol version. `RNBD_MSG_OPEN` resolves a full path under `dev_search_path`, rejects `..`, opens the block device read-only or read-write, finds/creates shared `rnbd_srv_dev`, allocates a per-session device id, creates sysfs, links the session-device, and fills `rnbd_msg_open_rsp` from queue capabilities. `RNBD_MSG_IO` looks up `device_id` under RCU, builds a bio against `file_bdev()`, maps data for normal reads/writes, handles zero-length special requests by setting `bi_size`, submits the bio, and replies from end_io. Close destroys session-device sysfs and lets kobject release perform final close.

## State and persistence behavior
Global `sess_list` and `dev_list` are in-memory only. Session-device ids live in each session xarray and are protected with RCU plus `kref`. `keep_id` allows force-close to remove resources without immediately reusing an id still known by a client. Shared device write-open counts are protected by `srv_dev->lock`. `dev_search_path` is a module parameter string persisted only for module lifetime.

## Dependencies and integration points
Uses RTRS server APIs, Linux block-device file APIs, bio submission, xarray, kref, sysfs helpers from `rnbd-srv-sysfs.c`, tracepoints, and the shared RNBD protocol. It is the peer for client `rnbd-clt.c`.

## Risks and test signals
- Path handling rejects any `..` substring, which is conservative but can reject legitimate names; it also concatenates paths and then collapses duplicate slashes.
- I/O buffer validation relies on RNBD header lengths from RTRS; fuzz short admin/I/O messages and invalid device ids.
- Access-mode counters must unwind correctly on all open failure paths.
- Test RO sharing, RW exclusion, migration dual-writer behavior, force close during I/O, disconnect cleanup with inflight bios, discard/write-zeroes with `datalen == 0`, protocol negotiation, and tracing.
