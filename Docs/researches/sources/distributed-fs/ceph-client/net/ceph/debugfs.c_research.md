# Research: sources/distributed-fs/ceph-client/net/ceph/debugfs.c

## Purpose

`debugfs.c` implements the debugfs surface for the in-kernel Ceph client library when `CONFIG_DEBUG_FS` is enabled. It creates `/sys/kernel/debug/ceph` and one per-client directory named from the cluster fsid and authenticated client global id, then exposes read-only seq-file views for monitor state, OSD map state, OSD client requests, and libceph client options. When debugfs is disabled, the same init and cleanup entry points compile to no-ops so callers do not need conditional code.

The file is observability-only. It does not persist configuration, mutate cluster state, or participate in protocol logic. Its output is nevertheless operationally important because it makes map versions, active requests, linger registrations, backoffs, and client options visible without tracing.

## Important APIs, Types, and Functions

Exported or externally called entry points:

- `ceph_debugfs_init()` creates the top-level `ceph` debugfs directory during module initialization.
- `ceph_debugfs_cleanup()` removes the top-level directory.
- `ceph_debugfs_client_init(struct ceph_client *client)` creates the per-client directory and files: `monc`, `osdc`, `monmap`, `osdmap`, and `client_options`.
- `ceph_debugfs_client_cleanup(struct ceph_client *client)` removes those per-client dentries.

Seq-file show callbacks:

- `monmap_show()` prints monitor map epoch and monitor entity/address rows under `client->monc.mutex`.
- `osdmap_show()` prints OSD map epoch, barrier, pools, OSD addresses/state/weights/locality, and temporary PG mappings under `osdc->lock`.
- `monc_show()` prints monitor subscription state, fs cluster id, and generic monitor requests from `generic_request_tree`.
- `osdc_show()` prints active OSD requests, linger requests, and OSD backoffs across all known OSD sessions plus the homeless OSD.
- `client_options_show()` delegates to `ceph_print_client_options()`.

Formatting helpers include `dump_spgid()`, `dump_target()`, `dump_request()`, `dump_linger_request()`, `dump_snapid()`, `dump_name_escaped()`, `dump_hoid()`, and `dump_backoffs()`. `DEFINE_SHOW_ATTRIBUTE()` generates the file operations for each seq-file view.

## Control Flow

Initialization is simple: `ceph_debugfs_init()` creates a root dentry and stores it in the static `ceph_debugfs_dir`. For each client, `ceph_debugfs_client_init()` formats a directory name as `%pU.client%lld`, creates that directory beneath the root, and attaches each seq-file to the client object as `private` data.

Each read path is lock-scoped around the subsystem whose state it traverses. `monmap_show()` and `monc_show()` use `monc->mutex` because they read monitor subscription and monmap state. `osdmap_show()` and `osdc_show()` take the OSD client read lock before walking map red-black trees or the OSD session tree; the request, linger, and backoff dumps then take each OSD's mutex while walking per-OSD rbtrees. Cleanup removes files in reverse enough order to detach per-client views before removing the directory.

## State and Persistence Behavior

The only file-local state is `ceph_debugfs_dir`, a debugfs dentry pointer. Per-client dentry pointers are stored in `struct ceph_client`, `struct ceph_mon_client`, and `struct ceph_osd_client`. All other state is read from live Ceph client objects. There is no durable persistence and no cached snapshot: seq-file reads reflect the current in-memory state at read time, subject to the locks held while formatting.

## Dependencies and Integration Points

This file depends on Linux `debugfs` and `seq_file`, libceph client structures, monitor client state, OSD client maps/requests/backoffs, Ceph address formatting via `ceph_pr_addr()`, OSD map helpers, and client option printing. It integrates upward with libceph init/teardown paths and downward with the monitor and OSD clients by storing debugfs dentries in their embedded structs.

## Risks and Edge Cases

The main risks are observability races and output cost rather than protocol corruption. Large OSD maps or many requests can produce large debugfs reads while holding locks, so this path can add diagnostic overhead on busy clients. The code assumes internal rbtrees and request objects remain valid under the documented locks. Name escaping for object identifiers is careful for `%`, `:`, `/`, non-printable bytes, and non-ASCII bytes; malformed or very long object names are bounded by stored lengths but can still make output large. If debugfs creation fails, the kernel debugfs helpers generally return error dentries or null-like entries and the code does not propagate errors; this matches many debugfs call sites but means missing observability is not fatal.

## Test Signals

Useful validation is mostly runtime and integration-oriented: build with and without `CONFIG_DEBUG_FS`; mount or initialize a Ceph client and verify the expected files appear; read each file while monitor subscriptions, OSD requests, linger requests, and backoffs are active; run lockdep while reading debugfs under concurrent map updates and request completion; check that client cleanup removes all dentries without use-after-free reports. Output-specific tests should exercise object names requiring escaping, empty maps, missing monmap/osdmap pointers, and clients with no active OSD sessions.
