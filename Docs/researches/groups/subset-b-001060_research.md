# subset-b-001060 research

Grouped research report for the requested block-driver subset. Each source section is delimited for deterministic reconciliation into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt-sysfs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.c -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.c

## Purpose
Implements the RNBD client data plane and lifecycle. It creates RTRS client sessions, maps remote server devices into local `gendisk` instances, translates blk-mq requests into RNBD protocol messages over RDMA, handles reconnect/remap behavior, and tears down mapped devices and sessions.

## Important APIs, types, and functions
- Public entry points: `rnbd_clt_map_device()`, `rnbd_clt_unmap_device()`, `rnbd_clt_remap_device()`, and `rnbd_clt_resize_disk()`.
- Session management uses global `sess_list`, `sess_lock`, `struct rnbd_clt_session`, `find_and_get_or_create_sess()`, `alloc_sess()`, `free_sess()`, and refcount helpers.
- Device management uses `struct rnbd_clt_dev`, IDA minor allocation, per-device mutexes, `insert_dev_if_not_exists_devpath()`, `rnbd_delete_dev()`, and dev-state transitions.
- Admin messages use `send_msg_sess_info()`, `send_msg_open()`, `send_msg_close()`, `send_usr_msg()`, and completion workers.
- I/O path uses `rnbd_queue_rq()`, `rnbd_client_xfer_request()`, `msg_io_conf()`, and `rnbd_softirq_done_fn()`.
- blk-mq integration is through `rnbd_mq_ops`, `setup_mq_tags()`, queue mapping, polling support via `rnbd_rdma_poll()`, and `rnbd_init_mq_hw_queues()`.

## Control flow
On module init the driver verifies protocol structure sizes, registers block major `rnbd`, creates sysfs, and allocates a workqueue. Mapping starts by rejecting duplicate `pathname`/session pairs, finding or creating an RTRS session, querying session attributes, allocating blk-mq tags, sending session info, allocating a client device, sending an open request, then building a disk with queue limits derived from the server open response. I/O requests require a nonblocking RTRS I/O permit, allocate a chained sg table, encode sector/size/op/prio into `rnbd_msg_io`, submit `rtrs_clt_request()`, and complete asynchronously.

Reconnect events come from RTRS. Disconnect transitions mapped devices to `DEV_STATE_MAPPED_DISCONNECTED` and emits offline uevents. Reconnect sends session info and async open messages for existing devices, updates capacity, and emits online uevents. Unmap marks the device unmapped under lock, removes it from the session list, removes sysfs/disk objects, optionally sends close, then drops references.

## State and persistence behavior
All state is in memory. Sessions are refcounted and shared by devices unless polling queues require isolated sessions. `busy`, per-CPU requeue lists, and `cpu_queues_bm` track stopped blk-mq queues waiting for RTRS permits. Device state is guarded by `dev->lock`; session device lists are guarded by `sess->lock`; global session/device uniqueness scans are guarded by `sess_lock`. Local disk IDs come from `index_ida` and are freed when the device refcount reaches zero.

## Dependencies and integration points
Depends on block layer `gendisk`, blk-mq tag sets, queue limits, request mapping, Linux IDA/refcount/workqueue/kobject APIs, RTRS client APIs, and the RNBD protocol definitions. It is invoked by client sysfs and interacts with server `rnbd-srv.c` through `RNBD_MSG_SESS_INFO`, `OPEN`, `IO`, and `CLOSE`.

## Risks and test signals
- Permit exhaustion and requeue fairness are subtle; tests should force queue depth below active hctx count and confirm no I/O hang.
- Async admin messages hold device/session refs; reconnect/remap/unmap races need lockdep, KASAN, and RTRS fault injection coverage.
- `rq_to_rnbd_flags()` maps flush/FUA semantics into protocol flags; cross-version server testing should include flush, discard, secure erase, write zeroes, and `REQ_NOUNMAP`.
- Polling queues are incompatible with shared sessions; mapping two devices with conflicting `nr_poll_queues` should fail.
- Size and queue-limit changes should be tested through remap and explicit resize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.h -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.h

## Purpose
Declares the RNBD client-side shared state, request context, queues, device/session objects, and exported functions used between the client core and sysfs layer.

## Important APIs, types, and functions
- `enum rnbd_clt_dev_state` defines `INIT`, `MAPPED`, `MAPPED_DISCONNECTED`, and `UNMAPPED`.
- `struct rnbd_iu` is the per-request/per-admin-message unit holding an RTRS permit, request or response buffer, sg table, worker, errno, wait completion, refcount, and inline scatterlist storage.
- `struct rnbd_clt_session` holds the RTRS session, wait queue, reconnect readiness, blk-mq tag set, queue-depth/segment limits, per-CPU requeue state, device list, protocol version, and session name.
- `struct rnbd_queue` binds blk-mq hardware contexts to RNBD requeue lists.
- `struct rnbd_clt_dev` holds one mapped disk's kobject, queue, hw queues, server device id, local IDA id, state, path, access mode, disk, sysfs symlink name, and unload work.
- Exports client core calls plus sysfs creation/destruction and symlink removal.

## Control flow
The header establishes the contract: sysfs creates and controls `rnbd_clt_dev` instances through exported functions, while the core embeds per-request `struct rnbd_iu` objects into blk-mq request private data and uses session/device fields to coordinate RTRS and block-layer state.

## State and persistence behavior
The structures are transient kernel state. Refcounts protect sessions and devices across sysfs calls, block-device opens, RTRS callbacks, and workqueue completions. `RNBD_INLINE_SG_CNT` depends on SG chaining support and affects request private data sizing.

## Dependencies and integration points
Includes Linux wait, inet, blk-mq, refcount APIs, `rtrs.h`, `rnbd-proto.h`, and `rnbd-log.h`. Its types are consumed by `rnbd-clt.c`, `rnbd-clt-sysfs.c`, and logging macros.

## Risks and test signals
Changing any field used by blk-mq private data, kobject release, or refcount paths can create lifetime bugs. Build coverage should include architectures with and without `CONFIG_ARCH_NO_SG_CHAIN`. Runtime tests should cover sysfs unmap while block devices are open and while admin message completions are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-log.h -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-log.h

## Purpose
Provides small logging macros for RNBD client and server code that prepend device path and session name to messages.

## Important APIs, types, and functions
- `rnbd_clt_log()` formats `<pathname@sessname>`.
- `rnbd_srv_log()` formats `<pathname@sessname>:` for server session-device objects.
- Convenience macros wrap `pr_err`, `pr_err_ratelimited`, `pr_info`, and `pr_info_ratelimited` for client and server paths.

## Control flow
This header is included by both client and server headers, allowing implementation files to call `rnbd_clt_err()`, `rnbd_srv_info()`, and ratelimited variants without repeating session/path formatting.

## State and persistence behavior
No state is owned here. Macros evaluate fields of live client/server objects; callers must ensure the referenced object and its `sess` pointer remain valid.

## Dependencies and integration points
Includes `rnbd-clt.h` and `rnbd-srv.h`, which creates a circular-looking but include-guarded dependency. It integrates with kernel printk APIs.

## Risks and test signals
Because macros dereference object fields directly, use-after-free bugs in caller lifetime management may surface as logging crashes. Build checks should catch include-order regressions; runtime fault paths should verify ratelimited logs do not dereference already released session objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-proto.h -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-proto.h

## Purpose
Defines the RNBD wire protocol shared by client and server: protocol version, message types and layouts, access modes, cache policy flags, and conversions between Linux request operations and RNBD I/O flags.

## Important APIs, types, and functions
- `RNBD_PROTO_VER_MAJOR`/`MINOR` are `2.2`; `RTRS_PORT` defaults to `1234`.
- Message structures include `rnbd_msg_hdr`, `rnbd_msg_sess_info`, `rnbd_msg_sess_info_rsp`, `rnbd_msg_open`, `rnbd_msg_open_rsp`, `rnbd_msg_io`, and `rnbd_msg_close`.
- `enum rnbd_access_mode` supports `ro`, `rw`, and `migration`; `rnbd_access_modes[]` provides strings.
- `enum rnbd_io_flags` encodes read, write, flush, discard, secure erase, write zeroes, sync, FUA, preflush, and nounmap.
- `rnbd_to_bio_flags()` converts protocol flags to server-side `blk_opf_t`; `rq_to_rnbd_flags()` converts client requests to protocol flags.

## Control flow
Client code fills protocol messages before calling RTRS; server code decodes the same layouts in `rnbd_srv_rdma_ev()`. Module init on both sides uses `BUILD_BUG_ON()` to assert fixed sizes for the wire ABI.

## State and persistence behavior
The header owns no runtime state. It defines little-endian wire fields and reserved padding, so layout and endian conversion are persistent ABI concerns between client and server versions.

## Dependencies and integration points
Depends on Linux block request types, limits, inet types, and RDMA headers. It is included by RNBD client, server, trace, and logging code.

## Risks and test signals
- Any structure layout change can break interoperability; keep size assertions and cross-version tests.
- `rq_to_rnbd_flags()` uses `op_is_flush()` to set `RNBD_F_FUA`, which deserves attention in flush/FUA semantic tests.
- Test all operation translations in both directions, including invalid op warnings and old-server behavior where server checks `usrlen` before reading `prio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-sysfs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.c -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.c

## Purpose
Instantiates RNBD server tracepoints declared in `rnbd-srv-trace.h`.

## Important APIs, types, and functions
- Includes RTRS and RNBD server/protocol headers so tracepoint prototypes see the relevant types.
- Defines `CREATE_TRACE_POINTS` before including `rnbd-srv-trace.h`, which emits the tracepoint definitions.

## Control flow
The file has no runtime functions of its own. It is compiled into the RNBD server trace object so calls such as `trace_process_rdma()` and `trace_process_msg_open()` resolve to real tracepoints.

## State and persistence behavior
No driver state is owned here. Tracepoint enablement and buffers are handled by the kernel tracing subsystem.

## Dependencies and integration points
Depends on tracepoint declarations in `rnbd-srv-trace.h` and server types from RTRS/RNBD headers. It must include the trace header last so helper types and constants are visible.

## Risks and test signals
Build failures are the primary signal if include order or trace event prototypes drift. Runtime validation is enabling `rnbd_srv:*` trace events while opening, closing, and issuing I/O through RNBD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.h -->
# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.h

## Purpose
Declares tracepoints for the RNBD server: session creation/destruction, I/O processing, session-info negotiation, open messages, and close messages.

## Important APIs, types, and functions
- `DECLARE_EVENT_CLASS(rnbd_srv_link_class)` captures session name and queue depth.
- `DEFINE_LINK_EVENT(create_sess)` and `DEFINE_LINK_EVENT(destroy_sess)` instantiate session lifecycle events.
- `TRACE_EVENT(process_rdma)` captures direction, protocol version, device id, sector, flags, size, priority, RDMA data length, and user header length.
- `TRACE_EVENT(process_msg_sess_info)`, `process_msg_open`, and `process_msg_close` capture admin protocol details.
- `TRACE_DEFINE_ENUM()` and `show_rnbd_access_mode()` make access-mode values readable in trace output.

## Control flow
Server core calls these tracepoints before or during message handling. The trace system records fields using fast assignment macros and formats them through `TP_printk` when read.

## State and persistence behavior
No RNBD state is stored. The events snapshot selected fields at trace time. Strings are copied into trace records through `__string`/`__assign_str`.

## Dependencies and integration points
Includes Linux tracepoint support and relies on forward-declared RNBD/RTRS types plus constants from `rnbd-proto.h`. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation at this local header.

## Risks and test signals
Trace events dereference message and session fields, so call sites must only pass validated buffers. Test by enabling each event and exercising session connect/disconnect, open, close, I/O, and old-version session info to confirm useful fields and no trace format breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/block/rnull/Kconfig

## Purpose
Adds the kernel configuration option for the Rust null block driver.

## Important APIs, types, and functions
- `config BLK_DEV_RUST_NULL` is a tristate option named "Rust null block driver (Experimental)".
- It depends on `RUST` and `CONFIGFS_FS`.
- Help text describes the driver as a Rust implementation of C `null_blk` with configfs-controlled virtual block devices.

## Control flow
Kconfig makes the module selectable only when Rust support and configfs are enabled. If selected as built-in or module, the corresponding Makefile builds `rnull_mod`.

## State and persistence behavior
No runtime state. Configuration choice persists in the kernel build config.

## Dependencies and integration points
Integrates with the kernel Kconfig system and the rnull Makefile. It signals that userspace control is through configfs.

## Risks and test signals
The help text contains a typo ("virutal"). Build tests should cover `n`, `m`, and `y` where Rust/configfs are available, plus dependency-hidden behavior when either dependency is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/Makefile -->
# sources/distributed-fs/ceph-client/drivers/block/rnull/Makefile

## Purpose
Builds the Rust null block driver object when `CONFIG_BLK_DEV_RUST_NULL` is enabled.

## Important APIs, types, and functions
- `obj-$(CONFIG_BLK_DEV_RUST_NULL) += rnull_mod.o`.
- `rnull_mod-y := rnull.o` makes `rnull.rs` the module's primary object; the Rust module imports `configfs.rs` as a Rust submodule.

## Control flow
The kbuild rule participates in normal kernel build selection. When enabled as a module, it produces `rnull_mod.ko`; when built-in, the object is linked into the kernel.

## State and persistence behavior
No runtime state. It affects build artifacts only.

## Dependencies and integration points
Depends on Kconfig selection and Rust kbuild support. `configfs.rs` is pulled by Rust module resolution rather than directly listed here.

## Risks and test signals
Build coverage should verify module and built-in configurations. Renaming `rnull.rs` or the Rust module name requires synchronized Makefile changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/configfs.rs -->
# sources/distributed-fs/ceph-client/drivers/block/rnull/configfs.rs

## Purpose
Implements the configfs interface for the Rust null block driver. It creates the `rnull` subsystem and per-device config groups whose attributes control whether a null block disk exists and what parameters it uses.

## Important APIs, types, and functions
- `subsystem()` returns a pinned configfs subsystem with root `features` attribute and child groups of type `DeviceConfig`.
- `Config::show()` reports supported features: `blocksize,size,rotational,irqmode`.
- `Config::make_group()` initializes `DeviceConfigInner` with defaults: powered off, 4096 byte block size, non-rotational, 4096 MiB capacity, `IRQMode::None`, and group name.
- `IRQMode` supports `None` (`0`) and `Soft` (`1`) with `TryFrom<u8>` validation and `Display`.
- Device attributes: `power`, `blocksize`, `rotational`, `size`, and `irqmode`.

## Control flow
Users create a configfs group under `rnull`. Before power-on, they may change block size, rotational flag, size, and irq mode. Writing true to `power` constructs a `NullBlkDevice::new()` disk and stores it in `disk: Option<GenDisk<NullBlkDevice>>`; writing false drops the disk and powers off. Configuration attributes return `EBUSY` while powered.

## State and persistence behavior
Per-group state is protected by a Rust kernel `Mutex<DeviceConfigInner>`. The `GenDisk` object is owned by the `disk` option and destroyed by dropping it. Configfs group state lasts until userspace removes the group or the module unloads; it is not persisted across reboot/module reload.

## Dependencies and integration points
Depends on Rust-for-Linux configfs abstractions, kernel string formatting/parsing, `GenDiskBuilder::validate_block_size()`, and `NullBlkDevice::new()` from `rnull.rs`.

## Risks and test signals
- The code locks the mutex multiple times in some store paths; race behavior is still serialized, but powered checks and updates are split in a few methods.
- Capacity accepts any `u64` MiB value; very large values should be tested for builder/sector overflow behavior.
- Test configfs group creation/removal, power cycling, invalid booleans, invalid block sizes, invalid irq mode values, and attempts to mutate attributes while powered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/configfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/rnull.rs -->
# sources/distributed-fs/ceph-client/drivers/block/rnull/rnull.rs

## Purpose
Implements a Rust null block driver module. It registers a configfs subsystem, creates in-memory block disks on demand, and completes every request successfully without storing data.

## Important APIs, types, and functions
- `module!` declares `rnull_mod`, author, description, and GPL license.
- `NullBlkModule` owns the pinned configfs subsystem.
- `NullBlkDevice::new()` creates a single-queue blk-mq tag set, queue data containing `IRQMode`, and a `GenDisk` with requested capacity, block sizes, and rotational flag.
- `impl Operations for NullBlkDevice` defines `queue_rq()`, `commit_rqs()`, and `complete()`.
- `QueueData` stores the configured completion mode.

## Control flow
Module init logs load and initializes configfs. Configfs calls `NullBlkDevice::new()` when a group is powered on. Requests enter `queue_rq()`: in `IRQMode::None`, they are ended synchronously with `Request::end_ok()`; in `IRQMode::Soft`, they are completed through blk-mq soft completion and later ended in `complete()`.

## State and persistence behavior
The module keeps only the configfs subsystem. Each disk's queue data stores IRQ mode. No request payloads are persisted or inspected; all I/O is discarded and reads complete without backing storage semantics beyond successful completion.

## Dependencies and integration points
Uses Rust-for-Linux block mq/gen_disk APIs, `Arc` tag sets, `KBox` queue data, and the local `configfs` module. It parallels the C `null_blk` driver concept but implements a smaller feature set.

## Risks and test signals
- `capacity_mib << (20 - SECTOR_SHIFT)` should be tested with large capacities.
- The code expects `end_ok()` not to fail because no extra request refs are held; request-lifetime API changes would matter.
- Test both IRQ modes, queue depth saturation, module unload with powered devices, and configfs power cycling under I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/rnull/rnull.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/sunvdc.c -->
# sources/distributed-fs/ceph-client/drivers/block/sunvdc.c

## Purpose
Implements the Sun LDOM virtual disk client driver. It binds to VIO `vdc-port` devices, negotiates a VIO/LDC virtual disk connection, creates a blk-mq disk, maps requests into LDC descriptor-ring cookies, and recovers from LDC resets.

## Important APIs, types, and functions
- `struct vdc_port` is the central per-port state: VIO driver state, disk, completion, request id/sequence, descriptor ring request array, transfer limits, media attributes, blk-mq tag set, and reset work.
- Handshake functions: `vdc_send_attr()`, `vdc_handle_attr()`, `vdc_handshake_complete()`.
- Event and ring handling: `vdc_event()`, `vdc_ack()`, `vdc_end_one()`, `__vdc_tx_trigger()`, `vdc_alloc_tx_ring()`, `vdc_free_tx_ring()`.
- I/O path: `vdc_queue_rq()` and `__send_request()` map blk requests to `vio_disk_desc` entries and trigger peer notification.
- Generic control operations use `generic_request()` for flush, write-cache, geometry, VTOC, SCSI, and devid style commands.
- Probe/remove/reset: `vdc_port_probe()`, `probe_disk()`, `vdc_port_remove()`, `vdc_ldc_reset()`, `vdc_requeue_inflight()`, and reset timer/work handlers.

## Control flow
Module init creates a workqueue, registers block major `vdisk`, and registers the VIO driver. Probe filters duplicate mpgroup ports, allocates a `vdc_port`, initializes VIO state, allocates LDC and exported descriptor ring, performs the VIO handshake, probes disk capacity/media, allocates blk-mq disk, and adds it. Queueing starts a request, checks drain and ring space, maps sg entries with correct LDC permissions, fills the current descriptor, uses a write barrier before marking it ready, triggers the peer, and advances the producer index. ACK events unmap cookies, free descriptor slots, end requests, and restart stopped queues. Reset stops queues, requeues inflight requests, tears down LDC/ring state, reallocates, and restarts handshake.

## State and persistence behavior
Runtime state is per VIO port. Descriptor-ring producer/consumer indices, request pointers, request ids, negotiated disk attributes, and reset timers are in memory only. The block disk persists for the bound VIO device lifetime. `drain` gates queue behavior during prolonged link-down handling.

## Dependencies and integration points
Depends on SPARC VIO/LDC APIs, machine description properties, Linux blk-mq, scatterlist mapping, CD-ROM ioctls for virtual optical media, workqueues, timers, and block queue limits. It integrates with firmware-described `vdc-port` devices and peer LDOM virtual disk servers.

## Risks and test signals
- `vdc_nack()` is unimplemented, so peer NACK behavior may leave requests unresolved.
- Descriptor ring exhaustion and LDC reset races require stress testing with queue depth 512, link flaps, and timeout-driven drain.
- `generic_request()` notes missing TX ring exhaustion handling.
- Test protocol versions 1.0/1.1/1.2, CD/DVD ioctl paths, mpgroup duplicate detection, media reserved cases (`vdisk_size == -1` or missing physical block size), and reset recovery with inflight I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/sunvdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/swim.c -->
# sources/distributed-fs/ceph-client/drivers/block/swim.c

## Purpose
Implements the original Macintosh SWIM floppy controller driver for m68k-era hardware. It probes internal/external drives, exposes them as floppy block devices, and performs read-only MFM sector reads through timing-sensitive low-level helper routines.

## Important APIs, types, and functions
- Register layouts `struct swim` and `struct iwm` define SWIM/IWM MMIO offsets.
- `struct floppy_state` stores physical drive location, media geometry, disk state, refcount, `gendisk`, tag set, and parent controller.
- Hardware helpers: `set_swim_mode()`, `get_swim_mode()`, `swim_select()`, `swim_action()`, `swim_readbit()`, `swim_drive()`, `swim_motor()`, `swim_eject()`, `swim_seek()`, `swim_track00()`.
- Data path: `swim_read_sector()`, `floppy_read_sectors()`, and `swim_queue_rq()`.
- Block operations: `floppy_open()`, `floppy_release()`, `floppy_ioctl()`, `floppy_getgeo()`, and `floppy_check_events()`.
- Probe/remove: `swim_probe()`, `swim_floppy_init()`, `swim_remove()`.

## Control flow
Platform probe reserves MMIO, switches the chip to SWIM mode, allocates controller state, scans internal and external drives, registers floppy major, allocates a small blk-mq disk for each drive, and adds `fdN` disks. Open powers the motor, sets MFM mode, detects media geometry if needed, validates write protection, and updates capacity. Queueing serializes with `swd->lock`, rejects writes or no-media requests, translates sector numbers to track/head/sector, reads sectors with retries through assembly helpers, updates the block request, and completes it.

## State and persistence behavior
Per-drive state tracks inserted/ejected media, media type, write protection, geometry, current track, open refcount, and registration. This state is volatile and refreshed on open after eject/media change. The driver registers fixed floppy major `FLOPPY_MAJOR` and one minor per detected drive.

## Dependencies and integration points
Depends on platform device resources, m68k Macintosh VIA helpers, raw MMIO access, blk-mq, floppy ioctls, and `swim_asm.S` functions `swim_read_sector_header()` and `swim_read_sector_data()`.

## Risks and test signals
- Writes are rejected in queueing even though open checks write protection; read-only behavior should be explicit in user tests.
- `swim_read_sector()` returns `0` when header fields mismatch, causing retries until failure.
- Timing loops use sleeps and local IRQ disabling around low-level reads; hardware-only testing is needed for regressions.
- `FDGETPRM` copies the entire `floppy_type` array, which may not match traditional ioctl expectations.
- Test drive detection, no media, media change, eject, write attempts, bad sectors, and cleanup after partial disk registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/swim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/swim3.c -->
# sources/distributed-fs/ceph-client/drivers/block/swim3.c

## Purpose
Implements the Power Macintosh SWIM3 floppy controller driver. It binds to macio devices, controls SWIM3 and DBDMA registers, exposes floppy disks through blk-mq, and uses a state machine, interrupts, timers, and DMA commands for reads and writes.

## Important APIs, types, and functions
- `enum swim_state` models controller activity: `idle`, `locating`, `seeking`, `settling`, `do_transfer`, `jogging`, `available`, `revalidating`, and `ejecting`.
- `struct floppy_state` holds MMIO/DMA mappings, IRQs, geometry, write-protect state, DMA command buffer, timeout, wait queue, current request, tag set, and macio/media-bay context.
- Request flow: `swim3_queue_rq()`, `act()`, `setup_transfer()`, `swim3_interrupt()`, and `swim3_end_request()`.
- Timer handlers: `scan_timeout()`, `seek_timeout()`, `settle_timeout()`, `xfer_timeout()`.
- Drive access: `grab_drive()`, `release_drive()`, `fd_eject()`, `floppy_open()`, `floppy_release()`, `floppy_revalidate()`, and `floppy_ioctl()`.
- Device setup: `swim3_add_device()`, `swim3_attach()`, `swim3_mb_event()`, and `swim3_init()`.

## Control flow
Attach registers floppy major for the first drive, allocates a blk-mq disk/tag set, maps SWIM3 and DMA MMIO, requests the SWIM3 interrupt, initializes geometry, then adds an `fdN` disk. Queueing accepts one request at a time under `swim3_lock`, rejects absent media/write-protected writes, computes cylinder/head/sector, sets state to `do_transfer`, and calls `act()`. The state machine seeks or locates current cylinder, sets up DBDMA and controller transfer registers, arms interrupts and timeouts, and returns. Interrupts handle sector seen, seek complete, and transfer complete/error, update partial request progress, retry where possible, or end the request.

## State and persistence behavior
State is static per possible drive in `floppy_states[]` and `disks[]`. Current request and controller state are protected by `swim3_lock`; open/ioctl paths use `swim3_mutex`. Media presence and write protection are cached and refreshed through open/revalidate/media-bay events. Timers represent pending hardware timeouts and are cancelled on interrupt completion.

## Dependencies and integration points
Depends on PowerPC macio, Open Firmware matching, DBDMA, media bay APIs, pmac feature calls, raw MMIO, blk-mq, floppy ioctl ABI, and fixed `FLOPPY_MAJOR`.

## Risks and test signals
- There is no remove path shown for freeing disks/resources, so hot-unplug support appears limited.
- DMA address handling uses a local `phys_to_bus` hack with `PCI_DRAM_OFFSET`; architecture assumptions are important.
- Only one active request per drive is supported; queue resource behavior should be tested.
- State-machine retries, timeout cancellation, media bay changes, write-protect checks, and partial-transfer request updates are high-risk areas.
- Test read and write flows, seek failures, transfer CRC/underrun/overrun errors, eject/revalidate, media-bay removal, and module load on systems with zero, one, or two controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/swim3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/swim_asm.S -->
# sources/distributed-fs/ceph-client/drivers/block/swim_asm.S

## Purpose
Provides timing-sensitive m68k assembly helpers for the original SWIM floppy driver. These routines read MFM sector address headers and sector data directly from SWIM registers.

## Important APIs, types, and functions
- Exports `swim_read_sector_header(struct swim __iomem *base, struct sector_header *header)`.
- Exports `swim_read_sector_data(struct swim __iomem *base, unsigned char *data)`.
- Internal routines `mfm_read_addrmark` and `mfm_read_data` wait for address/data marks, read bytes, and return either bytes read or `-1`.
- Constants define SWIM register offsets, sector header field offsets, seek/retry loop limits, and 512 byte sector size.

## Control flow
The C driver calls the exported functions with interrupts disabled around repeated sector scanning. The assembly resets selected mode registers, waits for MFM address marks (`a1 a1 a1 fe`) or data marks (`a1 a1 a1 fb`), copies header fields or data bytes into the caller buffer, reads trailing CRC bytes, clears mode, and returns.

## State and persistence behavior
No persistent state is kept. The routines manipulate hardware registers and caller-provided buffers. Return value `512` indicates a full data sector read; `-1` indicates timeout or missing expected byte; header read returns `0` on its normal exit.

## Dependencies and integration points
Architecture-specific to m68k Macintosh SWIM hardware. It is linked with `swim.c`, which declares the extern functions and interprets returned data while managing higher-level geometry and retries.

## Risks and test signals
- Correctness depends on exact polling loops and instruction timing; compiler-level C rewrites would be risky.
- Header path appears to set `d0 = 0` on `header_exit` after possible timeout through `bpl header_exit`, so caller validation of header fields is important.
- Hardware tests should include marginal disks, CRC errors, missing address marks, short reads, and repeated retries while validating no register mode is left active after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/swim_asm.S -->
