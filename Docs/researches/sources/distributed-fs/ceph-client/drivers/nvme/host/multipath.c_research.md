# sources/distributed-fs/ceph-client/drivers/nvme/host/multipath.c

## Purpose
This file implements native NVMe multipath support for namespace heads. It creates shared multipath disks and character devices, selects a live namespace path for each bio or passthrough request, requeues I/O when paths fail, tracks ANA state, exposes multipath sysfs attributes, and manages delayed removal of namespace-head devices.

## Important APIs, Types, And Functions
Module parameters are `multipath`, `multipath_always_on`, and `iopolicy`. I/O policies are `numa`, `round-robin`, and `queue-depth`. Public functions include `nvme_mpath_default_iopolicy()`, freeze helpers, `nvme_failover_req()`, `nvme_mpath_start_request()`, `nvme_mpath_end_request()`, `nvme_kick_requeue_lists()`, `nvme_mpath_clear_current_path()`, `nvme_mpath_clear_ctrl_paths()`, `nvme_mpath_revalidate_paths()`, `nvme_find_path()`, `nvme_mpath_alloc_disk()`, `nvme_mpath_add_disk()`, `nvme_mpath_remove_disk()`, `nvme_mpath_put_disk()`, `nvme_mpath_init_ctrl()`, `nvme_mpath_init_identify()`, `nvme_mpath_update()`, `nvme_mpath_stop()`, and `nvme_mpath_uninit()`.

The namespace-head block operations are `nvme_ns_head_ops`, with `submit_bio`, open/release, ioctl, geometry, unique-id, zones, and persistent reservation hooks. Character-device operations are `nvme_ns_head_chr_fops`. Sysfs attributes include subsystem `iopolicy`, per-path `ana_grpid`, `ana_state`, `queue_depth`, `numa_nodes`, and head `delayed_removal_secs`.

## Control Flow
Initialization starts when a namespace head is allocated. `nvme_mpath_alloc_disk()` initializes locks, requeue work, partition-scan work, delayed removal work, and optionally allocates a head disk if multipath is enabled or forced and the namespace ID is unique enough. It suppresses partition scanning until a separate work item can run outside controller scan context.

Bio submission enters `nvme_ns_head_submit_bio()`. The bio is split to queue limits, `head->srcu` is taken, and `nvme_find_path()` selects a namespace path by the current subsystem policy. A found path remaps the bio to the path disk, marks it `REQ_NVME_MPATH`, emits a block remap trace, and submits it. If no usable path exists but a path may recover, the bio is put on `head->requeue_list`; otherwise it is failed.

Path selection filters disabled paths by controller state, ANA pending flag, and namespace readiness. NUMA policy caches a current optimized path per NUMA node and falls back to nearest non-optimized. Round-robin walks siblings after the current path and prefers optimized paths while still allowing non-optimized fallback. Queue-depth policy chooses the optimized path with the lowest active count, falling back to lowest-depth non-optimized.

ANA handling starts in `nvme_mpath_init_identify()`, which validates controller ANA capabilities, computes the ANA log size, allocates or resizes `ana_log_buf`, and reads the ANA log. `nvme_read_ana_log()` gets the log page, parses each ANA group with bounds checks, updates namespace ANA states, and arms or deletes the ANATT timer depending on groups in change state. `nvme_update_ns_ana_state()` clears pending state, records group and ANA state, and makes the namespace-head disk live when a path becomes optimized or non-optimized and the controller is live.

Failover uses `nvme_failover_req()`: clear cached current paths, queue an ANA reread on ANA errors, move bios from the failed request to the namespace-head requeue list, clear status, end the original request, and schedule requeue work. `nvme_requeue_work()` resubmits queued bios through the head so path selection runs again.

## State And Persistence
Multipath state is attached to `struct nvme_subsystem`, `struct nvme_ns_head`, `struct nvme_ns`, and `struct nvme_ctrl`. The subsystem stores `iopolicy`. Each namespace head stores a multipath disk, cdev, SRCU-protected path list, per-node current path pointers, requeue list, flags, delayed removal seconds, and work items. Each namespace stores ANA group/state and flags such as `NVME_NS_ANA_PENDING` and `NVME_NS_SYSFS_ATTR_LINK`. Each controller stores ANA log buffer, ANA lock, ANATT timer/work, and queue-depth active count.

State is mostly runtime. Sysfs writes to `iopolicy` and `delayed_removal_secs` persist until module/controller teardown. ANA state is refreshed from controller log pages. Current path caches are intentionally invalidated on iopolicy changes, path failures, capacity mismatches, and controller path clearing.

## Dependencies And Integration Points
This file depends on blk-mq, gendisk, bio remapping, kblockd, sysfs, SRCU, module parameters, timers, NVMe identify/log helpers, NVMe namespace/controller/subsystem structures from `nvme.h`, optional zoned block support, and ioctl functions from `ioctl.c`.

Integration points are broad: core namespace scanning calls allocation/add/remove helpers, request completion calls start/end accounting helpers, transport error paths call failover and path clearing helpers, ANA AEN or error handling queues `ana_work`, and userspace observes/controls policy and delayed removal through sysfs.

## Risks
Path selection and removal are concurrency-sensitive. SRCU protects path traversal, but disk add/remove, sysfs link creation, delayed removal, requeue work, and namespace scan can overlap. Incorrect ordering can leave stale current-path pointers, duplicate sysfs links, live head disks without paths, or bios queued forever.

ANA parsing trusts controller-provided log structure after explicit bounds checks. Bad `ngrps`, `nnsids`, group IDs, or states return errors and can disable ANA support during identify. ANATT handling uses one timer for all changing groups, trading precision for simplicity. Queue-depth policy depends on `nvme_mpath_start_request()` and `nvme_mpath_end_request()` balancing active counts; missed end paths would bias routing.

The delayed removal feature intentionally queues I/O when no path is available. Misconfiguration can make failures appear as hangs until the delay expires. `multipath_always_on` can create head devices even for cases that would otherwise stay single-path, so namespace uniqueness checks are important.

## Test Signals
Test with single-path, multi-controller shared namespace, private namespace, ANA and non-ANA controllers, `multipath=0`, `multipath_always_on=1`, and each iopolicy. Exercise optimized/non-optimized/inaccessible/persistent-loss/change ANA transitions, ANA log parse errors, ANATT timeout reset, failover on ANA status, controller reset, path removal and re-addition, capacity mismatch, and namespace deletion during queued I/O.

Sysfs tests should verify iopolicy changes clear cached paths, queue-depth and numa_nodes visibility/content, ana state attributes, sysfs path links, and delayed_removal_secs behavior. I/O tests should verify bio remap tracing, accounting on the head disk, requeue then successful resubmit, final failure when no path is available, polled and nowait features on the head disk, zoned report forwarding, persistent reservations, and ioctl/io_uring passthrough through namespace heads.
