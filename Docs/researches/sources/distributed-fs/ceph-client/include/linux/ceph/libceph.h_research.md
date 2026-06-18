# sources/distributed-fs/ceph-client/include/linux/ceph/libceph.h

## Purpose

`libceph.h` is the central kernel libceph client interface. It defines mount/options state, the shared `ceph_client` object, snapshot contexts, common red-black-tree helper macros, slab/mempool globals, client lifecycle APIs, session APIs, and page-vector helpers.

## Important APIs, Types, and Functions

Key types are `ceph_options`, `ceph_client`, `ceph_snap_context`, and the generated RB helper macros `DEFINE_RB_*`. Important APIs include `ceph_alloc_options()`, `ceph_parse_mon_ips()`, `ceph_parse_param()`, `ceph_create_client()`, `ceph_destroy_client()`, `ceph_open_session()`, `ceph_wait_for_latest_osdmap()`, snap-context get/put/create helpers, `calc_pages_for()`, and page-vector allocation/copy/zero/release functions.

## Control Flow

Client setup flows from option parsing to `ceph_create_client()`, messenger/monitor/OSD client initialization, and `ceph_open_session()`. Runtime operations dispatch through monitor and OSD clients embedded in `ceph_client`; cleanup releases options, sessions, messenger state, caches, and debugfs entries.

## State and Persistence Behavior

`ceph_client` holds per-cluster client state: FSID, options, auth wait state, supported/required features, messenger, monitor client, OSD client, and debugfs dentries. `ceph_snap_context` is refcounted and attached to dirty pages to preserve write snapshot context.

## Dependencies and Integration Points

It includes Ceph messenger, msgpool, monitor, OSD, filesystem protocol, and string-table headers plus VFS/writeback/page-cache primitives. It is the integration root for CephFS and RBD-like kernel clients using libceph.

## Risks and Edge Cases

Option comparison only covers fields before the pointer section unless updated. Shared clients require mount option identity to be correct. Snap contexts are flexible-array refcounted objects and can leak or use-after-free if page ownership is wrong. RB macros `BUG()` on duplicate insertion when using strict insert helpers.

## Test Signals

Exercise option parsing/printing/comparison, shared-client reuse, failed session open unwinding, snap-context refcounting, page-vector boundary calculations, RB helper duplicate handling, and debugfs-enabled/disabled client lifecycle.
