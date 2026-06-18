# Research: subset-b-004544

Grouped research for Mellanox/NVIDIA mlx5 flow-steering, firmware, health, IPoIB, IRQ affinity, and LAG files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.h

## Purpose
`fs_core.h` is the internal object model for mlx5 flow steering. It defines the namespace/prio/table/group/FTE/destination tree, shared flow counter structures, flow-table sizing constants, steering modes, resource-owner variants for firmware/software/HWS steering, and traversal helpers used by the rest of `mlx5/core`.

## Important APIs, Types, And Functions
- `struct mlx5_flow_steering` stores the root namespaces for NIC RX/TX, FDB, sniffer, RDMA, port selection, and eswitch ACL roots.
- `struct fs_node` is the common intrusive tree node with parent/root pointers, child list, rw semaphore, refcount, active flag, delete callbacks, and version.
- `struct mlx5_flow_table`, `mlx5_flow_group`, `fs_fte`, `mlx5_flow_rule`, and `mlx5_flow_handle` define the software representation of hardware flow-table entities.
- `struct mlx5_flow_root_namespace` carries steering mode, DR/HWS domain context, table type, root flow table, chain lock, underlay QPN list, and command vtable.
- `struct mlx5_fc`, `mlx5_fc_bulk`, and `mlx5_fc_cache` define flow-counter identity, pooling/local ownership, cached packet/byte/lastuse state, and HWS action refcount data.
- Declared APIs include flow steering lifecycle (`mlx5_fs_core_alloc/init/cleanup/free`), vport ACL namespace add/remove, root lookup, namespace mode/peer setup, flow-counter stats work control, and packet reformat ID lookup.

## Control Flow And State
The header has no implementation, but it encodes the control-flow hierarchy used by flow creation and teardown. Callers traverse from namespace to priority to flow table to group to FTE to destination using the `fs_for_each_*` helpers, and root namespaces serialize flow-table chaining through `chain_lock`. FTEs may carry duplicate destination/action state through `struct fs_fte_dup`, while tables track forward rules pointing at them.

## Dependencies And Integration Points
It depends on Linux refcounting, xarrays/rhashtables, mlx5 public flow-steering UAPI, and steering backends in `steering/sws` and `steering/hws`. It integrates with firmware command implementations, DR/HWS software steering, eswitch FDB/ACL namespaces, RDMA namespaces, IPoIB underlay QPN handling, flow counters, and ethtool/tc steering consumers.

## Risks And Edge Cases
The main risk is lifetime and locking correctness across a deep shared tree: node deletion callbacks, refcounts, hash entries, and table chaining must stay synchronized. Capability macros map many flow-table types to distinct device capability blocks; adding a table type requires updating `MLX5_CAP_FLOWTABLE_TYPE` and the build-time terminal check. Counter structures mix pooled, single, and local ownership and must not be released through the wrong path.

## Test Signals
Useful signals include successful creation/destruction of flow tables/groups/rules across NIC, FDB, RDMA, and ACL namespaces; no refcount or rhashtable leaks under rule churn; correct behavior in DMFS/SMFS/HMFS modes; underlay QPN rules working for IPoIB; and flow-counter cache updates surviving create/destroy races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_counters.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_counters.c

## Purpose
`fs_counters.c` implements mlx5 flow-counter allocation, pooling, destruction, direct query, cached query, and periodic bulk polling. It bridges firmware counter commands with the internal `mlx5_fc` structures defined in `fs_core.h`.

## Important APIs, Types, And Functions
- `struct mlx5_fc_stats` stores the aging-counter xarray, single-thread workqueue, delayed polling work, sampling interval, reusable bulk query buffer, and `mlx5_fs_pool` counter pool.
- Public APIs include `mlx5_fc_create`, `mlx5_fc_destroy`, `mlx5_fc_id`, `mlx5_fc_query`, `mlx5_fc_query_cached`, `mlx5_fc_query_cached_raw`, `mlx5_fc_query_lastuse`, `mlx5_init_fc_stats`, and `mlx5_cleanup_fc_stats`.
- Local-counter APIs `mlx5_fc_local_create`, `mlx5_fc_local_get`, `mlx5_fc_local_put`, and `mlx5_fc_local_destroy` wrap already-acquired counter IDs with independent refcounting.
- Pool-specific hooks `mlx5_fc_bulk_create`, `mlx5_fc_bulk_destroy`, and `mlx5_fc_pool_update_threshold` adapt the generic `fs_pool` allocator to firmware bulk counter allocation.

## Control Flow And State
`mlx5_init_fc_stats` allocates state, initializes the xarray, allocates an initial small bulk query buffer, creates the `mlx5_fc` workqueue, initializes the counter pool, and starts periodic polling. Aging counters are inserted into the xarray on create and removed on destroy. The delayed work reschedules itself, grows the query buffer when the active counter count exceeds the initial bulk length, and calls `mlx5_fc_stats_query_all_counters`.

Bulk polling walks the xarray under the xarray lock, releases the lock around each firmware `mlx5_cmd_fc_bulk_query`, resets the xarray cursor, and only updates counters whose `lastuse` predates the bulk query start. Cached query returns deltas since the caller's last cached read, while raw cached query returns absolute cached values.

## State And Persistence Behavior
Firmware owns the actual counter values and IDs. Driver state persists in `dev->priv.fc_stats`, the xarray keyed by counter ID, pooled bulk bitmaps, `lastbytes/lastpackets`, and per-counter cache. Cleanup cancels work synchronously, destroys the workqueue, releases all remaining counters, destroys the xarray, tears down the pool, and frees the bulk query buffer.

## Dependencies And Integration Points
The file depends on `fs_core.h`, `fs_pool.h`, `fs_cmd.h`, xarray locking, workqueues, firmware flow-counter allocation/query/free commands, and device capabilities such as `flow_counter_bulk_alloc` and `log_max_flow_counter_bulk`. It is used by flow steering, tc/eswitch rules, aging logic, and HWS action data.

## Risks And Edge Cases
Create/destroy races with the poller are managed through xarray locking and cursor reset; regressions here can produce use-after-free or stale cache updates. Pool-acquired, single, and local counters have distinct release paths. Bulk allocation fallback must preserve correctness when pooling fails. `mlx5_fc_update_sampling_interval` only reduces the interval, so callers expecting later expansion need a separate policy.

## Test Signals
Exercise single and pooled counter allocation, aging and non-aging counters, cached delta reads, raw reads, bulk buffer growth, destruction while polling, cleanup with live counters, pool exhaustion/fallback, and warnings for invalid pooled releases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.c

## Purpose
`fs_ft_pool.c` tracks coarse flow-table capacity buckets for mlx5 firmware flow tables. Firmware does not expose live pool availability, so the driver keeps software counts for a fixed set of supported table sizes.

## Important APIs, Types, And Functions
- `FT_POOLS` lists supported flow table sizes from large to small plus a size-1 termination-table bucket.
- `struct mlx5_ft_pool` stores remaining table counts per bucket.
- `mlx5_ft_pool_init` allocates and initializes `dev->priv.ft_pool`.
- `mlx5_ft_pool_destroy` frees the pool.
- `mlx5_ft_pool_get_avail_sz` selects and reserves a bucket at least as large as the desired size, or the largest available bucket when `desired_size == MLX5_FS_MAX_POOL_SIZE`.
- `mlx5_ft_pool_put_sz` returns a previously reserved size to the matching bucket.

## Control Flow And State
Initialization derives each bucket count from a fixed 16 MiB virtual region divided by that bucket size. Allocation scans from the smallest bucket upward, filters by remaining count and per-table-type `log_max_ft_size` capability, reserves the selected bucket by decrementing its count, and returns the selected size. Release scans for an exact bucket-size match and increments the count.

## Dependencies And Integration Points
The file depends on `fs_ft_pool.h`, `fs_core.h`, `mlx5_core_dev`, and `MLX5_CAP_FLOWTABLE_TYPE` capability lookup. It integrates with flow-table creation code that needs a firmware-compatible table size and must return the size on destroy.

## Risks And Edge Cases
The pool is purely software accounting; if firmware behavior or supported bucket sizes change, accounting may diverge. There is no visible lock in this file, so callers must ensure serialization around `ft_left` updates. Releasing an unknown size only warns, which can hide leaks or double-release asymmetry. Allocation returning 0 means no bucket is available and must be handled by the caller.

## Test Signals
Validate bucket selection for exact, smaller, maximum, and unsupported sizes; allocation exhaustion and subsequent release; capability-limited maximum table sizes; termination-table size handling; and warning behavior for invalid release sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.h

## Purpose
`fs_ft_pool.h` declares the flow-table size pool API used by mlx5 flow steering to reserve and release firmware-compatible flow table sizes.

## Important APIs, Types, And Functions
- Includes `linux/mlx5/driver.h` and `fs_core.h` so callers can pass `struct mlx5_core_dev` and `enum fs_flow_table_type`.
- `mlx5_ft_pool_init` and `mlx5_ft_pool_destroy` manage `dev->priv.ft_pool`.
- `mlx5_ft_pool_get_avail_sz` reserves an available table size for a given table type and desired size.
- `mlx5_ft_pool_put_sz` releases a previously reserved size.

## Control Flow And State
The header does not implement behavior. Its API implies a lifecycle where the device initializes the pool before flow-table creation, callers reserve a size before creating a hardware table, and callers release that size during flow-table destruction.

## Dependencies And Integration Points
It is an internal mlx5 core header consumed by flow-steering table allocation code and implemented by `fs_ft_pool.c`. The API depends on the flow-table type enum from `fs_core.h` because allocation is capability-sensitive.

## Risks And Edge Cases
Callers must pair each successful reservation with exactly one release and must not pass arbitrary sizes to `mlx5_ft_pool_put_sz`. Since the implementation has fixed firmware bucket assumptions, this header should remain internal rather than becoming a generic allocator contract.

## Test Signals
Compile coverage should ensure all flow-table allocator users include this header cleanly. Runtime signals are successful flow-table creation and teardown across all supported table types without pool exhaustion leaks or invalid-size warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_ft_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.c

## Purpose
`fs_pool.c` implements a generic bulk-object pool for flow-steering resources. It tracks free indexes inside bulk allocations with bitmaps and moves bulks between fully-used, partially-used, and unused lists.

## Important APIs, Types, And Functions
- `mlx5_fs_bulk_init`, `mlx5_fs_bulk_bitmap_alloc`, `mlx5_fs_bulk_cleanup`, and `mlx5_fs_bulk_get_free_amount` manage per-bulk length and free bitmap state.
- `mlx5_fs_pool_init` initializes pool lists, counters, lock, callbacks, and device/context pointers.
- `mlx5_fs_pool_cleanup` destroys all bulks still on the pool lists through caller-supplied `bulk_destroy`.
- `mlx5_fs_pool_acquire_index` returns a `struct mlx5_fs_pool_index` from a partially used, unused, or newly created bulk.
- `mlx5_fs_pool_release_index` marks an index free and either moves the bulk to the appropriate list or destroys it when unused capacity exceeds the dynamic threshold.

## Control Flow And State
Acquire takes `pool_lock`, prefers partially used bulks, then unused bulks, then allocates a new bulk via `ops->bulk_create`. It clears the selected free bit, decrements available units, increments used units, and updates list placement. Release sets the bit back, increments available units, decrements used units, moves a formerly full bulk to partial use, and for fully free bulks either returns them to the unused list or destroys them if the pool is over threshold.

## Dependencies And Integration Points
The file depends on kernel bitmaps, lists, mutexes, and the callback table in `fs_pool.h`. `fs_counters.c` is a direct consumer, using the pool for firmware bulk flow counters, but the abstraction can serve other bulk-backed flow-steering resources.

## Risks And Edge Cases
The bitmap starts with all bits set to mean free; misuse of bit semantics can invert allocation. `mlx5_fs_pool_acquire_from_list` moves list entries based on free count and caller intent, so list corruption would affect all future allocations. Cleanup calls `bulk_destroy` even for fully used bulks and relies on the backend to reject busy destruction; callers should drain users before cleanup.

## Test Signals
Test acquire/release ordering, transitions between unused/partial/full lists, bulk allocation failure, threshold-triggered destruction, double release returning `-EINVAL`, and cleanup with both empty and busy bulks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.h

## Purpose
`fs_pool.h` declares the generic mlx5 flow-steering bulk pool abstraction. It lets resource-specific code supply bulk creation, destruction, and threshold policy while sharing bitmap/list accounting.

## Important APIs, Types, And Functions
- `struct mlx5_fs_bulk` contains a pool list node, number of units, and free-unit bitmap.
- `struct mlx5_fs_pool_index` returns a bulk pointer plus unit index to callers.
- `struct mlx5_fs_pool_ops` provides `bulk_create`, `bulk_destroy`, and `update_threshold` callbacks.
- `struct mlx5_fs_pool` stores the device, caller context, callback table, mutex, full/partial/unused lists, and available/used/threshold counters.
- Declared functions cover bulk init/bitmap/cleanup/free-count and pool init/cleanup/acquire/release.

## Control Flow And State
This header models ownership around a pool initialized once, repeatedly acquiring and releasing indexes, then cleaning up after users are gone. It intentionally does not define how a backend maps an index into a resource; the backend stores enclosing data around `struct mlx5_fs_bulk`.

## Dependencies And Integration Points
It depends on `linux/mlx5/driver.h` for device types and kernel primitives. The immediate integration point in this subset is `fs_counters.c`, which embeds `struct mlx5_fs_bulk` in `struct mlx5_fc_bulk` and maps pool indexes to flow counters.

## Risks And Edge Cases
Backends must ensure `bulk_destroy` can detect busy bulks, and users must keep the returned bulk/index valid until release. The pool is not RCU-safe; access is serialized by the internal mutex, but resource users outside acquire/release still need their own lifetime rules.

## Test Signals
Compile and runtime coverage should include at least one real backend, allocation failure paths, release error paths, threshold updates, and cleanup after complete drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw.c

## Purpose
`fw.c` implements firmware-facing mlx5 control-plane helpers: adapter identity queries, HCA capability discovery, HCA init/teardown variants, firmware flashing through the common `mlxfw` FSM, and running/pending firmware version queries.

## Important APIs, Types, And Functions
- `mlx5_query_board_id` and `mlx5_core_query_vendor_id` issue `QUERY_ADAPTER`.
- `mlx5_query_hca_caps` conditionally queries all supported capability blocks, including general, port selection, ethernet/IPoIB offloads, ODP, atomic, RoCE, flow tables, eswitch, QoS, debug, access-register capability maps, device memory, TLS, vDPA/TLP emulation, IPsec, crypto, MACsec, advanced virtualization/RDMA, SHAMPO, and PSP.
- `mlx5_cmd_init_hca`, `mlx5_cmd_teardown_hca`, `mlx5_cmd_force_teardown_hca`, and `mlx5_cmd_fast_teardown_hca` wrap HCA lifecycle commands.
- Firmware-flash register helpers access MCC, MCDA, MCQI, MCQS, and MIRC registers, and `mlx5_firmware_flash` wires mlx5 into `mlxfw_firmware_flash`.
- `mlx5_fw_version_query` locates the boot image component and reads running and pending versions.

## Control Flow And State
Capability discovery starts from general capabilities and only queries optional blocks when the relevant capability bit is present. HCA init can pass software owner ID and software VHCA ID. Fast teardown first asks firmware to prepare, disables the NIC interface, and polls until the NIC state is disabled or PCI access fails/times out.

Firmware flashing uses the `mlxfw_dev_ops` callback table: lock update handle, describe/update component, download blocks through MCDA, verify, activate/reactivate, query FSM state, cancel, and release. Version query scans MCQS component entries until it finds the boot image, reads the running version through MCQI, then checks whether a pending reset-active image exists before querying stored version.

## State And Persistence Behavior
The file mutates device capability caches, `dev->board_id`, HCA state in firmware, firmware update FSM state, pending stored firmware image state, and NIC interface state during fast teardown. It does not persist data in files; persistence is firmware/NVRAM-controlled through the firmware update mechanism.

## Dependencies And Integration Points
It depends on mlx5 command execution, access-register helpers, devlink via `priv_to_devlink`, the shared `mlxfw` library, eswitch manager checks, and timeout helpers. Reset and health code depend on HCA teardown and NIC state helpers.

## Risks And Edge Cases
Capability probing is long and conditional; a new feature bit may require querying a matching capability block before use. Flashing requires multiple register capabilities and returns `-EOPNOTSUPP` if any are absent. Fast teardown must handle PCI channel offline and stale NIC state. Version query uses `U32_MAX` as a failure sentinel for running/pending versions.

## Test Signals
Signals include successful probe capability population on multiple device generations, init/teardown/fast-teardown paths under normal and timeout conditions, firmware flashing rejected on unsupported firmware, flash progress through lock/update/verify/activate, and correct devlink-reported running/pending firmware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.c

## Purpose
`fw_reset.c` implements mlx5 firmware reset negotiation and event handling. It supports devlink-controlled remote reset policy, live patch notifications, PCI sync reset request/ack/nack/unload/now/abort flows, reset timeout handling, PCI link toggle or hot reset, and reset completion/reload.

## Important APIs, Types, And Functions
- `struct mlx5_fw_reset` holds the device, EQ notifier, workqueue, work items, timeout work, flags, reset method, poll timer, completion, and result.
- Public APIs include `mlx5_fw_reset_query`, `mlx5_fw_reset_set_reset_sync`, `mlx5_fw_reset_set_live_patch`, `mlx5_fw_reset_in_progress`, `mlx5_fw_reset_wait_reset_done`, `mlx5_sync_reset_unload_flow`, `mlx5_fw_reset_verify_fw_complete`, event start/stop/drain, init, and cleanup.
- MFRL helpers query and set reset level/type/state/method plus sync start/ack/nack.
- Event workers handle live patch, reset request, unload, reload, reset-now, abort, and timeout.

## Control Flow And State
Initialization is gated by MFRL support, allocates state, creates a single-thread workqueue, registers the `ENABLE_REMOTE_DEV_RESET` devlink param, and initializes work items. Event start registers a general-event notifier. Firmware events dispatch either live-patch work or PCI sync reset state work.

For sync reset, an initiating devlink path calls `mlx5_fw_reset_set_reset_sync`, sets `PENDING_COMP`, and asks firmware to start PCI sync. External reset request events evaluate reset method, hotplug constraints, SF state, management-interface device IDs, and remote-reset policy before sending ACK or NACK. ACK starts health-poll suppression, sync-reset polling, timeout work, and marks reset in progress. Reset-now and unload flows run fast teardown and PCI reset/unload handling, then complete reload or completion.

## State And Persistence Behavior
State is entirely in `dev->priv.fw_reset`, flag bits, timer/workqueue state, MFRL firmware state, NIC interface reset state, and devlink runtime param. Cleanup unregisters the devlink param, drains work if requested, and destroys the workqueue. No filesystem persistence is used.

## Dependencies And Integration Points
The file depends on devlink, EQ notifiers, PCI config/reset APIs, mlx5 health polling, firmware tracer reload, SF table checks, HCA teardown from `fw.c`, device load/unload helpers, and timeout definitions. It coordinates with health recovery by stopping/restarting health polling around sync reset.

## Risks And Edge Cases
Incorrect flag transitions can leave health polling stopped, completion pending, or reset marked in progress. PCI link toggle must save/restore sibling device state and avoid hotplug-interrupt configurations. Reset requests can arrive during devlink reload, device removal, or mode changes. `mlx5_sync_reset_unload_flow` must correctly acknowledge drop mode and timeout if firmware never requests reset action.

## Test Signals
Cover MFRL unsupported init, devlink remote-reset enable/disable, sync reset ACK/NACK paths, reset timeout, abort, unload and reset-now events, live patch tracer reload, PCI hot reset/link toggle success and failure, reload-required handling, and no queued work after drain/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.h

## Purpose
`fw_reset.h` declares the firmware reset interface shared between mlx5 core, devlink reload paths, health recovery, and event setup/teardown.

## Important APIs, Types, And Functions
- Query/control: `mlx5_fw_reset_query`, `mlx5_fw_reset_set_reset_sync`, `mlx5_fw_reset_set_live_patch`, and `mlx5_fw_reset_in_progress`.
- Completion/reload: `mlx5_fw_reset_wait_reset_done`, `mlx5_sync_reset_unload_flow`, and `mlx5_fw_reset_verify_fw_complete`.
- Event lifecycle: `mlx5_fw_reset_events_start`, `mlx5_fw_reset_events_stop`, and `mlx5_drain_fw_reset`.
- Allocation lifecycle: `mlx5_fw_reset_init` and `mlx5_fw_reset_cleanup`.

## Control Flow And State
The header exposes a lifecycle where device initialization creates reset state, event setup registers firmware event handling, devlink or firmware events initiate reset operations, wait/verify APIs synchronize with completion, drain stops pending work during removal, and cleanup frees state.

## Dependencies And Integration Points
It includes `mlx5_core.h` for core device and devlink extension-ack types. Consumers include core device load/unload, devlink reload, firmware flashing activation, and health/error paths that must know whether a firmware reset is active.

## Risks And Edge Cases
Callers must handle the no-op case where firmware reset support is absent and `dev->priv.fw_reset` is null. Wait/verify APIs are meaningful only after a reset has been initiated. Event start/stop should remain paired with device event-notifier lifecycle.

## Test Signals
Build coverage across configurations and runtime tests for init returning 0 on unsupported firmware, null-safe event start/stop/drain, and successful reset wait/verify sequencing after devlink firmware activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/health.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/health.c

## Purpose
`health.c` implements mlx5 device health polling, fatal sensor detection, firmware syndrome reporting, devlink health reporters, firmware trace/core-dump collection, timestamp updates for firmware logs, and recovery/unload actions after device errors.

## Important APIs, Types, And Functions
- NIC interface helpers `mlx5_get_nic_state` and `mlx5_set_nic_state` read/write the initial segment state bits.
- `mlx5_health_check_fatal_sensors` detects PCI read failure, PCI channel offline, disabled NIC interface, software reset, and firmware syndrome reset requests.
- Error/recovery APIs include `mlx5_enter_error_state`, `mlx5_error_sw_reset`, `mlx5_health_wait_pci_up`, `mlx5_trigger_health_work`, `mlx5_start_health_poll`, `mlx5_stop_health_poll`, `mlx5_drain_health_wq`, `mlx5_health_init`, and `mlx5_health_cleanup`.
- Devlink reporter callbacks diagnose, dump, and recover firmware and fatal firmware health events.

## Control Flow And State
`mlx5_health_init` creates devlink reporters unless the device is lightweight, creates the vNIC reporter, allocates a single-thread workqueue, and initializes report/timestamp work. `mlx5_start_health_poll` arms a timer that periodically reads fatal sensors, health counter, and syndrome fields. A fatal sensor immediately marks the device internal-error and queues fatal report work. Missed health-counter increments or changed syndromes queue nonfatal firmware report work.

Fatal reporter work enters error state, invokes devlink health reporting when available, and can unload the driver if recovery is canceled by graceful-period policy. Recovery disables the bad device, waits for PCI reads to return, calls `mlx5_recover_device`, and rechecks fatal sensors. Optional firmware log timestamp work writes wall-clock time to MRTC hourly.

## State And Persistence Behavior
State lives in `dev->priv.health`: timer, workqueue, reporter pointers, health buffer pointers, previous counter, miss counter, syndrome, fatal error, flags, and crdump size. Hardware state is read from the initial segment health buffer and written through NIC state and MRTC registers. Health reporters expose transient diagnostic dumps through devlink, not persistent files.

## Dependencies And Integration Points
The file depends on initial segment MMIO, PCI channel state, devlink health, firmware tracer, core dump collection, vNIC reporter, notifier chains, command flushing, device load/unload/recovery, PCI VSC reset semaphore helpers, and firmware reset timeout constants.

## Risks And Edge Cases
Health polling runs from a timer and queues work; teardown must cancel work and delete timers in the right order. PCI communication failure makes health-buffer reads unreliable and limits recovery options. Software reset is coordinated across PFs through a VSC semaphore. Devlink graceful periods may suppress recovery, leading to driver unload.

## Test Signals
Inject health counter stalls, firmware syndromes, PCI offline, NIC disabled/software reset states, and RFR/CRR syndrome bits. Verify devlink diagnose/dump output, crdump on PFs, recovery success/failure, unload on canceled recovery, timestamp update scheduling, and no health work after drain/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/health.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.c

## Purpose
`hwmon.c` registers mlx5 temperature sensors with the Linux hwmon framework. It discovers ASIC/platform and optional module sensors, reads current/highest/critical temperatures through MTMP, enables maximum-temperature tracking, and supports resetting max-temperature history.

## Important APIs, Types, And Functions
- `struct mlx5_hwmon` stores the mlx5 device, registered hwmon device, channel metadata/config arrays, chip info, sensor descriptors, and sensor counts.
- `mlx5_hwmon_query_mtmp`, `mlx5_hwmon_reset_max_temp`, and `mlx5_hwmon_enable_max_temp` access MTMP.
- hwmon callbacks `mlx5_hwmon_read`, `mlx5_hwmon_write`, `mlx5_hwmon_is_visible`, and `mlx5_hwmon_read_string` implement temp attributes.
- Discovery helpers read MTCAP sensor count/map, derive module sensor index from module number, test module monitoring capability, allocate arrays, and initialize sensor names.
- Public lifecycle is `mlx5_hwmon_dev_register`, `mlx5_hwmon_dev_unregister`, and `hwmon_get_sensor_name`.

## Control Flow And State
Registration first checks MTMP access-register support. Allocation reads sensor count, probes the module sensor by reading its mapped MTMP temperature, allocates descriptor/config arrays for platform plus optional module sensor, and stores `mdev`. Device init reads MTCAP, builds hwmon channel info, fills sensor indexes from the sensor map plus module index, queries names or synthesizes `sensor<index>`, enables max temperature on each channel, and registers `hwmon_device_register_with_info`.

Reads query MTMP for the channel's sensor index and convert firmware units of 0.125 C to millidegrees C. Writes only support `hwmon_temp_reset_history`, which sets MTMP `mtr`.

## State And Persistence Behavior
Software state is stored at `mdev->hwmon` until unregister. Hardware state includes MTMP max-temperature tracking enable and reset-history side effects. Sensor values are live firmware register reads; the driver does not cache temperatures.

## Dependencies And Integration Points
The file depends on `CONFIG_HWMON`, Linux hwmon APIs, mlx5 access-register helpers, MTCAP/MTMP register layouts, and port module-number query support. It integrates with core device registration and can supply sensor names to other mlx5 diagnostics.

## Risks And Edge Cases
Sensor count and sensor map must agree; otherwise channel indexes may not represent the intended sensors. Module monitoring is inferred from a nonzero temperature read, which can miss unsupported or temporarily unavailable modules. Name copying depends on firmware-provided fixed fields. Any MTMP error aborts registration.

## Test Signals
Check registration on devices with and without MTMP, platform sensors only, platform plus module sensor, readable labels/input/highest/crit attributes, reset-history writes, max-temp enable failures, and unregister clearing `mdev->hwmon`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.h

## Purpose
`hwmon.h` declares the mlx5 hwmon registration interface and provides no-op stubs when hwmon support is not enabled.

## Important APIs, Types, And Functions
- With `CONFIG_HWMON`, it declares `mlx5_hwmon_dev_register`, `mlx5_hwmon_dev_unregister`, and `hwmon_get_sensor_name`.
- Without `CONFIG_HWMON`, registration returns success and unregister is an empty inline, allowing core code to call the API unconditionally.

## Control Flow And State
The header does not implement state. It defines a conditional lifecycle hook: register during device setup, unregister during teardown, and optionally query sensor names when hwmon state exists.

## Dependencies And Integration Points
It depends on `linux/mlx5/driver.h` and forward-declared mlx5 hwmon state from core headers. It integrates `hwmon.c` with core device initialization while keeping non-hwmon builds simple.

## Risks And Edge Cases
`hwmon_get_sensor_name` is only declared in hwmon-enabled builds; callers must be guarded accordingly. Stub registration returning 0 means higher-level code cannot use return value alone to know whether sensors exist.

## Test Signals
Build both `CONFIG_HWMON=y/m` and disabled configurations. Runtime signals are successful unconditional core calls and no unresolved symbols in non-hwmon builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ethtool.c

## Purpose
`ipoib/ethtool.c` adapts mlx5 Ethernet ethtool operations to IPoIB netdevices. Most handlers delegate to shared `mlx5e` helpers, while link settings and RX flow validation account for InfiniBand/IPoIB semantics.

## Important APIs, Types, And Functions
- `mlx5i_get_drvinfo`, strings, stats, ringparam, channels, coalesce, timestamp, flash, RSS hash fields, RX NFC, and RX ring count wrap `mlx5e_ethtool_*` helpers using `mlx5i_epriv`.
- `mlx5i_set_channels` rejects channel-count changes while parent IPoIB devices have subinterfaces.
- `mlx5i_get_link_ksettings` queries IB operational width/rate and converts them to ethtool speed/duplex/port/autoneg values.
- `mlx5i_set_rxnfc` rejects `ETHER_FLOW` rules because IPoIB traffic is not Ethernet L2 in the normal sense.
- Exports `mlx5i_ethtool_ops` for parent IPoIB devices and `mlx5i_pkey_ethtool_ops` for child pkey devices.

## Control Flow And State
Etntool calls arrive through the netdev's `ethtool_ops`. Parent devices get broad control over ring/channel/coalesce/RSS/NFC/link settings. Pkey child devices expose only driver info, link state, and timestamp info. Channel changes require RTNL and check `num_sub_interfaces` to avoid breaking child devices sharing parent resources.

## Dependencies And Integration Points
The file depends on `en.h`, `ipoib.h`, `en/fs_ethtool.h`, mlx5e ethtool helpers, IB port operational query, and kernel ethtool structures. It integrates IPoIB netdevs with standard user tools such as `ethtool -S`, `-l`, `-L`, `-c`, `-K`-adjacent stats, flash, and flow steering.

## Risks And Edge Cases
IB width/rate enum conversion must stay current with new link rates. Parent channel reconfiguration while children exist is explicitly blocked; missing RTNL coverage would race child init/uninit. Delegated Ethernet helpers may expose settings that are only partially meaningful for IPoIB, so IPoIB-specific rejection paths matter.

## Test Signals
Run ethtool stats, ring, channel, coalesce, timestamp, RSS hash field, RX NFC, flash, and link-settings commands on parent and pkey devices. Validate speed for SDR through XDR widths, `ETHER_FLOW` rejection, and channel-change rejection when subinterfaces exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.c

## Purpose
`ipoib/ipoib.c` implements mlx5 enhanced IPoIB netdevice support. It builds IPoIB-specific mlx5e parameters, creates and transitions underlay UD QPs, creates TIS objects tied to underlay QPNs, sets up flow steering/RX resources, defines netdev/RDMA callbacks, and exposes RDMA netdev allocation parameters.

## Important APIs, Types, And Functions
- Public entry points include `mlx5i_init`, `mlx5i_cleanup`, `mlx5i_create_underlay_qp`, `mlx5i_destroy_underlay_qp`, `mlx5i_init_underlay_qp`, `mlx5i_uninit_underlay_qp`, `mlx5i_create_tis`, `mlx5i_get_tisn`, `mlx5i_update_nic_rx`, `mlx5i_dev_init`, `mlx5i_dev_cleanup`, `mlx5i_get_stats`, parent get/put helpers, and `mlx5_rdma_rn_get_params`.
- `mlx5i_nic_profile` supplies mlx5e profile callbacks for parent IPoIB devices.
- RDMA netdev callbacks attach/detach multicast groups, transmit via `mlx5i_sq_xmit`, and update pkey index.

## Control Flow And State
`mlx5_rdma_rn_get_params` verifies IB port type and enhanced IPoIB capability, then returns private size, TX/RX queue counts, device parameter, and setup callback. Setup initializes parent resources and QPN hash table for primary devices, initializes mlx5e private state/profile, attaches the netdev, installs RDMA send/mcast callbacks, and sets destructor behavior.

TX initialization creates an underlay UD QP and TIS. RX initialization creates mlx5e flow steering, queue counters, drop RQ, RX resources, aRFS tables, TTC table, and ethtool steering. Opening a netdev transitions the underlay QP through RST2INIT/INIT2RTR/RTR2RTS, adds the underlay QPN to RX flow steering, opens channels, refreshes TIRs, and activates channels. Close removes QPN steering, deactivates/closes channels, and resets the QP.

## State And Persistence Behavior
Per-netdev state lives in `struct mlx5i_priv` plus embedded `mlx5e_priv`: underlay QPN, TISN, qkey, pkey index, parent/child flags, QPN hash table, and mlx5e channels/RX resources. Hardware state includes QP state, TIS object, multicast group attachments, and flow-steering underlay QPN entries.

## Dependencies And Integration Points
The file depends on RDMA netdev APIs, IB verbs address handles, mlx5e channels/params/RX resources/flow steering/timestamps, firmware QP/TIS commands, and IPoIB TX WQE layout from `ipoib.h`. It integrates with `ipoib_vlan.c` for pkey child profiles and QPN lookup.

## Risks And Edge Cases
Open failure paths must unwind QP state, flow steering, and channels in reverse order. QPN can be derived from netdev address when `mkey_by_name` is supported, coupling address layout to QP creation. Parent refcounts and `num_sub_interfaces` must stay under RTNL. IPoIB supports only one TC and linked-list RQs here; enabling unsupported mlx5e features would break assumptions.

## Test Signals
Validate RDMA netdev allocation on IB-capable devices, parent open/close, multicast attach/detach, TX/RX traffic, MTU changes through safe parameter switch, QP state transitions, TIS create/destroy, underlay QPN steering, stats aggregation, and cleanup on setup/open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.h

## Purpose
`ipoib/ipoib.h` is the internal interface for mlx5 enhanced IPoIB support. It defines IPoIB private state, wire-format constants, TX WQE layout, profiles, ethtool ops, QPN hash APIs, underlay QP/TIS APIs, and parent-child reference helpers.

## Important APIs, Types, And Functions
- `struct mlx5i_priv` extends `rdma_netdev` and stores underlay QPN, TISN, subinterface state, qkey, pkey index, QPN-to-netdev hash table, parent netdev, and flexible storage for embedded `mlx5e_priv`.
- Constants describe IPoIB GRH, encapsulation, pseudo-header, hard-header length, and single-TC limit.
- `struct mlx5i_tx_wqe` lays out IPoIB TX WQEs with control, datagram, pad, Ethernet segment, and data segments.
- Declarations cover TIS/QP lifecycle, pkey hash-table operations, shared netdev operations, profile lifecycle, RX update, pkey profile lookup, TX, stats, and parent ref management.
- `mlx5i_epriv(netdev)` extracts the embedded `mlx5e_priv`.

## Control Flow And State
The header supports a two-layer private layout where `struct mlx5i_priv` is the netdev private object and the embedded/flexible `mlx5e_priv` carries common Ethernet-channel machinery. Parent devices own RX resources and QPN mapping; pkey child devices reference parent resources and use the hash table to map underlay QPNs back to netdevs.

## Dependencies And Integration Points
It is compiled only under `CONFIG_MLX5_CORE_IPOIB`, depends on mlx5 flow steering and `en.h`, and is consumed by `ipoib.c`, `ipoib_vlan.c`, ethtool support, RX handlers, and TX implementation. It bridges RDMA netdev callbacks with mlx5e infrastructure.

## Risks And Edge Cases
The private layout relies on `mlx5i_priv` being first-compatible with `rdma_netdev` and on `mlx5i_epriv` pointer arithmetic. Parent/child QPN hash access must be synchronized with NAPI and RTNL assumptions. The TX WQE layout must match firmware expectations exactly.

## Test Signals
Build with and without `CONFIG_MLX5_CORE_IPOIB`, validate private-size allocation, parent and pkey netdev setup, QPN hash lookup during receive, TX WQE posting, and correct behavior when child devices outlive or release parent references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib_vlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib_vlan.c

## Purpose
`ipoib/ipoib_vlan.c` implements pkey child-interface support for mlx5 IPoIB. It provides a QPN-to-netdev hash table shared with the parent, child netdev operations, and a child mlx5e profile that reuses parent RX resources while creating child-specific TX QP/TIS state.

## Important APIs, Types, And Functions
- `struct qpn_to_netdev` and `struct mlx5i_pkey_qpn_ht` implement a small hash table guarded by `spin_lock_bh`.
- Public hash APIs are `mlx5i_pkey_qpn_ht_init`, cleanup, add, delete, and lookup.
- Child netdev operations implement open, close, init, cleanup, MTU change, stats, and hardware timestamp get/set.
- `mlx5i_pkey_nic_profile` overrides parent profile behavior for pkey devices.
- `mlx5i_pkey_get_profile` returns the child profile to `ipoib.c`.

## Control Flow And State
Parent device initialization allocates the QPN hash table. Child `ndo_init` obtains and references the parent with RTNL held, verifies the child has at least as many RX queues as the parent, copies the parent's QPN hash pointer, and then calls common `mlx5i_dev_init` to set address bytes and add its QPN mapping.

Child open transitions the underlay QP, adds its QPN to RX flow steering, creates a child TIS, opens channels, refreshes RX, and activates channels. Close reverses those operations. Child RX init/cleanup are no-ops because RX resources are owned by the parent. Child MTU change only writes the netdev MTU under state lock rather than switching shared RX parameters.

## State And Persistence Behavior
State includes parent `num_sub_interfaces`, child `parent_dev`, shared QPN hash table, child underlay QPN/TISN, and mlx5e channel state. Hardware state includes per-child underlay QP, child TIS, and RX underlay QPN steering entry. There is no persistent storage.

## Dependencies And Integration Points
The file depends on `ipoib.h`, Linux hash lists, RTNL parent lookup, mlx5e channel helpers, flow steering underlay QPN APIs, and the common IPoIB functions in `ipoib.c`. RX handlers can use the hash table to map packets by underlay QPN.

## Risks And Edge Cases
`mlx5i_pkey_del_qpn` looks up before taking the hash lock, while the table is documented as synchronized with NAPI; changes here need careful concurrency review. Child init must release parent references on failures. Shared RX resources mean child queue counts and MTU behavior are constrained by the parent. Open failure unwinding must destroy TIS and remove QPN steering in the right order.

## Test Signals
Create/delete pkey child interfaces, open/close them under traffic, validate QPN lookup, parent channel-change rejection while children exist, child MTU updates, failure injection in QP/TIS/channel creation, and parent reference/hash cleanup after child removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/irq_affinity.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/irq_affinity.c

## Purpose
`irq_affinity.c` implements IRQ allocation and sharing policy for mlx5 IRQ pools. It chooses IRQs based on requested CPU affinity masks, per-CPU load, pool refcount thresholds, and SF sysfs integration.

## Important APIs, Types, And Functions
- `cpu_get`, `cpu_put`, and `cpu_get_least_loaded` maintain `pool->irqs_per_cpu` load accounting and choose the least-loaded online CPU in a requested mask.
- `irq_pool_request_irq` allocates an xarray index, builds an automatic affinity descriptor when needed, and calls `mlx5_irq_alloc`.
- `irq_pool_find_least_loaded` finds an existing IRQ whose affinity mask is a subset of the requested mask and has the smallest refcount.
- `mlx5_irq_affinity_request` is the public request path.
- `mlx5_irq_affinity_irq_release` synchronizes, removes SF sysfs entries when needed, drops the IRQ refcount, and updates CPU accounting when the IRQ is freed.

## Control Flow And State
Request takes the pool mutex, searches existing IRQs, and reuses one below `min_threshold`. If no sufficiently light IRQ exists, it tries to allocate a new IRQ. If allocation fails but a matching existing IRQ exists, it shares that IRQ. It logs overload when refcount exceeds `max_threshold`. For SF pools, a successful request creates an auxiliary-device sysfs IRQ entry after releasing the pool lock; failure rolls back the IRQ reference.

## State And Persistence Behavior
State lives in the IRQ pool xarray, IRQ refcounts, affinity masks, per-CPU counters, and optional SF sysfs entries. IRQ objects persist while referenced by EQs or other users and are freed by `mlx5_irq_put` when the last reference drops.

## Dependencies And Integration Points
The file depends on mlx5 IRQ pool internals, PCI IRQ vector mapping, CPU masks, xarray allocation, auxiliary-device sysfs helpers for SFs, and `mlx5_irq_*` refcount/mask APIs. It integrates with EQ/channel allocation that requests IRQs for completion/control paths.

## Risks And Edge Cases
If a requested mask has no online CPUs, the code falls back to the first online CPU and logs an error. Per-CPU accounting must only decrement when the IRQ is actually freed. Auto affinity descriptor allocation and xarray allocation failure need rollback. Mask-subset matching means broad requested masks can share narrower IRQs, which is intentional but can surprise callers.

## Test Signals
Request IRQs with single-CPU and multi-CPU masks, no-online-CPU masks, allocation failures with and without reusable IRQs, min/max threshold behavior, SF sysfs add/remove rollback, and release after active interrupts with `synchronize_irq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/irq_affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/debugfs.c

## Purpose
`lag/debugfs.c` exposes mlx5 LAG state through debugfs. It creates read-only files for LAG type, port-selection mode, active/disabled state, mode flags, port mapping, and member device names.

## Important APIs, Types, And Functions
- Show handlers `type_show`, `port_sel_mode_show`, `state_show`, `flags_show`, `mapping_show`, and `members_show` read `struct mlx5_lag` under `ldev->lock`.
- `get_str_mode_type` maps internal LAG modes to user-readable strings.
- `mlx5_ldev_add_debugfs` creates the `lag` debugfs directory and files under the mlx5 device debugfs root.
- `mlx5_ldev_remove_debugfs` recursively removes the directory.

## Control Flow And State
When a LAG-capable mdev is added, `lag.c` calls `mlx5_ldev_add_debugfs`. Each file uses `file->private` as the core device, resolves `mlx5_lag_dev`, locks the LAG object, snapshots or prints state, then unlocks. Inactive LAG returns `-EINVAL` for type, port-selection mode, flags, and mapping, while state always prints active or disabled.

## Dependencies And Integration Points
The file depends on Linux debugfs/seq_file helpers and `lag.h` functions such as `mlx5_get_str_port_sel_mode`, `mlx5_infer_tx_enabled`, and LAG iteration macros. It integrates only with diagnostic/debug paths and has no effect on LAG behavior.

## Risks And Edge Cases
Debugfs readers race with LAG teardown unless removal happens early and locking/lifetime are respected; `lag.c` removes debugfs early during mdev removal. Mapping output differs for hash-based and queue-affinity modes, so tools must parse both formats. Inactive mode returning `-EINVAL` is expected.

## Test Signals
Check debugfs file creation/removal on LAG-capable devices, correct output in disabled, RoCE, SR-IOV, multipath, and MPESW modes, hash and non-hash mapping formats, shared FDB flags, and safe reads during bond changes/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.c

## Purpose
`lag/lag.c` implements mlx5 multi-port LAG orchestration. It pairs mlx5 PFs through devcom, tracks netdev bonding state, activates/modifies/deactivates firmware LAG, supports RoCE/SR-IOV/shared-FDB/multipath/MPESW modes, manages port-selection mappings, exposes demux flow-table helpers, and exports LAG query helpers to other mlx5 subsystems.

## Important APIs, Types, And Functions
- Firmware command wrappers create/modify/destroy LAG and vport LAG.
- Device management functions include `mlx5_lag_add_mdev`, `mlx5_lag_remove_mdev`, `mlx5_lag_add_netdev`, and `mlx5_lag_remove_netdev`.
- Activation paths include `mlx5_activate_lag`, `mlx5_deactivate_lag`, `mlx5_disable_lag`, `mlx5_modify_lag`, `mlx5_lag_check_prereq`, and `mlx5_lag_shared_fdb_supported`.
- Demux APIs `mlx5_lag_demux_init`, cleanup, rule add, and rule delete manage LAG demux flow tables/rules.
- Exported query helpers report RoCE/active/hash/master/SR-IOV/shared-FDB state, slave port, number of ports, peer devices, device sequence, bond speed, and congestion counters.

## Control Flow And State
On mdev add, the driver registers a devcom component keyed by system image GUID and net namespace, joins or allocates a shared `mlx5_lag`, registers netdev and port-change notifiers, marks the lowest device index as master once all ports pair, and creates debugfs. Netdev add records the netdev and sets readiness when all ports have netdevs.

Netdev notifier events snapshot bond membership, TX type/hash type, lower-state link/tx flags, inactive slaves, and bond speed into `lag_tracker`, then queue bond work. Bond work obtains devcom lock, serializes on `ldev->lock`, and calls `mlx5_do_bond`. Activation removes/reshuffles auxiliary devices when needed, computes queue-affinity or hash mappings, creates optional port-selection flow tables, sends firmware create LAG, optionally enables shared FDB, restores IB devices/reps, sends active-backup notifications, and sets aggregate vport speeds. Modify updates mapping or active-port bits. Disable resets vport speeds, removes drop rules/single-FDB state, destroys firmware LAG, and restores devices.

## State And Persistence Behavior
State lives in `struct mlx5_lag`: mode, mode flags, readiness flags, number of ports/buckets, mode-change counter, virtual-to-physical map, kref, PF xarray with master mark, tracker, workqueue, devcom/netdev notifiers, MP/MPESW/port-select state, demux table/group/rules, and per-PF netdev/drop-rule state. Hardware state includes firmware LAG context, port-selection resources, eswitch single-FDB links, ingress drop rules, demux flow tables, and vport speed limits.

## Dependencies And Integration Points
The file depends on bonding netdev APIs, devcom, eswitch/offloads, port-selection flow steering, multipath and MPESW helpers, mlx5 command interface, debugfs, EQ notifiers, SR-IOV/RoCE state, auxiliary-device rescans, and devlink-adjacent reload behavior. It is a central integration point for RDMA, eswitch, representors, congestion counters, and LAG-aware consumers.

## Risks And Edge Cases
This code has complex concurrency: global spinlock for short queries, per-LAG mutex for state transitions, devcom lock for cross-device coordination, workqueue retries, and mode-change suppression. Activation must unwind port-selection, shared FDB, drop rules, and device rescans correctly on failures. Bond membership logic assumes all LAG ports and only those ports are enslaved to the same master. Shared FDB support requires exact eswitch capability/peer readiness. Removing a device waits for mode changes and must tear down debugfs early.

## Test Signals
Test two-port and multi-port pairing, bond enslave/release, active-backup and hash modes, lower-state changes, hash-based port selection, shared-FDB switchdev activation, RoCE LAG activation, VF/SR-IOV rejection cases, mdev/netdev removal while active, demux table/rule lifecycle, vport speed aggregation/reset, exported state helpers, and congestion counter aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.h

## Purpose
`lag/lag.h` defines mlx5 LAG core data structures, mode enums, flags, helper accessors, iteration macros, and internal function declarations shared by LAG implementation, debugfs, multipath, MPESW, and other mlx5 subsystems.

## Important APIs, Types, And Functions
- Mode constants cover none, RoCE, SR-IOV, multipath, and multiport eswitch.
- `struct lag_func` records each PF's core device, netdev, drop-rule state, xarray index, and port-change notifier.
- `struct lag_tracker` captures bond TX type, per-port lower state, bonded/inactive flags, hash type, and bond speed.
- `struct mlx5_lag` stores mode, flags, readiness, port count, bucket count, mapping, kref, PF xarray, tracker, workqueue, notifiers, net namespace, multipath/port-select/MPESW state, lock, and demux resources.
- Inline helpers resolve the LAG object, PF entries, device-index mappings, readiness, and support checks.
- Declarations cover activation, modification, demux, debugfs, device add/remove, shared FDB, vport speed, devcom, iteration, and counting helpers.

## Control Flow And State
The header models the shared LAG object as a refcounted cross-device container. Devices are stored in an xarray, with an xarray mark identifying the master PF. Iteration macros walk only present PF entries using helper functions. Capability gating in `mlx5_lag_is_supported` requires vport group manager, lag master, at least two supported ports, valid device index, and port count not exceeding `MLX5_MAX_PORTS`.

## Dependencies And Integration Points
It depends on debugfs, xarray, mlx5 flow steering, core device definitions, and LAG submodules `mp.h`, `port_sel.h`, and `mpesw.h`. It is included by `lag.c`, `debugfs.c`, and other mlx5 modules needing LAG state or exported internal helpers.

## Risks And Edge Cases
The iteration macros rely on assignment in loop conditions and helper return sentinels; misuse can be subtle. `mlx5_lag_pf` returns xarray entries without taking references, so callers need appropriate locking/lifetime protection. Support checks must stay aligned with firmware capabilities as multi-port devices evolve.

## Test Signals
Build coverage across eswitch and non-eswitch configs, multi-port capability detection, xarray master marking, helper mappings between xarray index/device index/sequence, and debugfs/LAG modules compiling against this shared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.h -->
