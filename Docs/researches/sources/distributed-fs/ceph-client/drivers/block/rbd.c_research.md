# sources/distributed-fs/ceph-client/drivers/block/rbd.c

## Purpose
Implements the in-kernel Ceph RADOS Block Device driver. It maps Ceph RBD images into Linux block devices, handles sysfs map/unmap control, translates block requests into Ceph OSD object operations, supports RBD v1 and v2 metadata, snapshots, clone layering, exclusive locks, object maps, data pools, striping v2, discards, write zeroes, watch/notify refreshes, and parent copyup.

## Important APIs, Types, And Functions
Key state types are `struct rbd_device`, `struct rbd_client`, `struct rbd_spec`, `struct rbd_options`, `struct rbd_image_header`, `struct rbd_img_request`, and `struct rbd_obj_request`. `rbd_device` owns block-disk state, Ceph client/spec/options, header/layout/mapping, watch and exclusive-lock state, object map, parent chain, blk-mq tag set, sysfs device, and open/removal state.

User-visible control is provided through the `rbd` bus attributes `add`, `remove`, `add_single_major`, `remove_single_major`, and `supported_features`, plus per-device sysfs attributes such as `size`, `features`, `pool`, `image_id`, `current_snap`, `parent`, and `refresh`. Block operations are `rbd_open()`, `rbd_release()`, and blk-mq `rbd_queue_rq()`.

Metadata helpers include `rbd_dev_image_id()`, `rbd_dev_header_name()`, `rbd_dev_header_info()`, `rbd_dev_v1_header_info()`, `rbd_dev_v2_header_info()`, `rbd_dev_v2_header_onetime()`, `rbd_dev_v2_snap_context()`, `rbd_dev_setup_parent()`, `rbd_dev_probe_parent()`, and `rbd_dev_refresh()`.

Request processing centers on `rbd_queue_workfn()`, `rbd_img_fill_request()`, `rbd_img_handle_request()`, `rbd_obj_handle_request()`, `rbd_obj_advance_read()`, `rbd_obj_advance_write()`, and `rbd_obj_advance_copyup()`. Exclusive locking and watch/notify are handled by `rbd_try_acquire_lock()`, `rbd_acquire_lock()`, `rbd_request_lock()`, `rbd_release_lock()`, `rbd_watch_cb()`, `rbd_watch_errcb()`, and `rbd_reregister_watch()`.

## Control Flow
Module init validates libceph compatibility, creates request slab caches, allocates the global workqueue, optionally registers a single block major, and registers the `rbd` sysfs bus. Mapping starts when a privileged user writes an add string. `do_rbd_add()` parses monitor addresses, Ceph/RBD options, pool/image/snapshot identity, obtains or creates a shared `rbd_client`, resolves the pool id, creates an `rbd_device`, marks read-only snapshots, probes image metadata and parent chain, initializes the disk, optionally acquires the exclusive lock, adds the sysfs device and disk, and links it into `rbd_dev_list`.

I/O enters `rbd_queue_rq()`, which maps block operations to `OBJ_OP_READ`, `OBJ_OP_WRITE`, `OBJ_OP_DISCARD`, or `OBJ_OP_ZEROOUT`, rejects writes to read-only mappings, initializes an image request in the blk-mq PDU, and queues `rbd_queue_workfn()` on the global workqueue. The worker captures snapshot/parent state under `header_rwsem`, splits the image extent into object requests using Ceph striping helpers, then starts the image state machine. The image state machine obtains exclusive lock if required, captures current write snap context, checks mapping bounds, starts each object state machine, waits for pending object completions, and completes the blk-mq request.

Read object flow first consults the object map when usable. A missing object in a layered image is reverse-mapped to the parent and read through a child image request; holes and short reads are zero-filled. Write/discard/zeroout flow may pre-update object map state, issue guarded object operations, perform copyup when an object is missing but parent data overlaps, update snapshot object maps for fast-diff/deep-copyup, then post-update object map deletion state. Parent-chain recursion is avoided by scheduling child image requests through the workqueue and open-coding completion unwinding.

Removal starts from a privileged write to remove. `do_rbd_remove()` finds the device, rejects busy devices unless `force` is specified, sets `REMOVING`, optionally freezes and marks the disk dead, deletes disk/sysfs state, releases locks, unregisters watches, releases image metadata and parent devices, and drops the final device reference.

## State And Persistence Behavior
Kernel runtime state is extensive but volatile: shared Ceph clients, per-device blk-mq disks, image headers, snapshot contexts, object maps, parent chain references, lock owner information, watch handles, pending request state machines, and open counts. Persistent state lives in Ceph RADOS objects: v1 headers/data objects, v2 id/header/object-map/data objects, RBD class metadata, snapshots, locks, and data pools. The driver reads and updates persistent object maps and locks using Ceph class methods and OSD operations, but all local maps and headers are reloaded on map, refresh, lock acquire, watch re-registration, or notification.

Concurrency is coordinated with `header_rwsem`, `lock_rwsem`, `watch_mutex`, `object_map_lock`, `lock_lists_lock`, per-request mutexes, global client/device list locks, and krefs. Parent references use `atomic_inc_return_safe()` and `atomic_dec_return_safe()` so parent metadata can be torn down once in-flight parent-dependent requests drain.

## Dependencies And Integration Points
The driver is deeply integrated with libceph (`ceph_client`, OSD client, monitor client, class lock client, striper, decode helpers), Linux blk-mq, sysfs bus/device infrastructure, IDA allocation, workqueues, krefs, RCU string handling in object locators, and RBD on-disk constants from `rbd_types.h`. It depends on Ceph OSD class methods such as `get_id`, `get_size`, `get_features`, `get_snapcontext`, `object_map_load`, `object_map_update`, `copyup`, `parent_get`, and lock/watch/notify behavior.

## Risks
Major risk areas are request state-machine correctness, exclusive-lock handoff, object-map consistency, and parent copyup. Object map updates are asynchronous and protected by class locks; failures are often logged and surfaced but can leave performance features invalid or require refresh. Lock transitions must quiesce running I/O before release, reacquire after watch reregistration, and safely handle dead clients through watcher checks and monitor blocklisting. Header refresh races can change size, snapshots, and parent overlap while I/O is in flight, so `header_rwsem` and parent refs are critical. Discard/zeroout behavior depends on `alloc_size`, object boundaries, filestore compatibility comments, and object-map deletion state. The map string parser is sysfs-facing and CAP_SYS_ADMIN-gated, but invalid option handling and token ownership remain sensitive.

## Test Signals
Strong signals include Ceph RBD map/unmap smoke tests, read/write/discard/write-zeroes workloads, snapshot read-only mappings, clone/layered read fallback, copyup under parent overlap, flatten refresh behavior, object-map enabled and invalid cases, exclusive-lock contention between clients, watch error/reregister simulation, forced remove during I/O, xfstests or fio on mapped images, and Ceph QA suites that exercise in-kernel RBD. Sysfs attributes should reflect capacity, features, parent chain, snapshot identity, and refresh updates.
