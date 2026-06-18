# `sources/distributed-fs/ceph-client/include/linux/mlx5/driver.h`

## Purpose

`driver.h` is the central public mlx5 core-driver contract for this Ceph client source tree's vendored Linux mlx5 stack. It exposes the top-level `struct mlx5_core_dev`, core private state, command transport definitions, health/page-allocation/debugfs resources, SR-IOV and LAG helpers, RoCE and MACsec capability gates, UAR/BFREG doorbell allocation types, rate-limiter state, memory-key helpers, notifier registration, and many firmware command entry points. Most implementation lives in mlx5 core, Ethernet, RDMA, LAG, and library `.c` files; this header defines the ABI those modules share inside the kernel tree.

## Important APIs, Types, and Constants

- Device identity and capability constants include `MLX5_ADEV_NAME`, `MLX5_IRQ_EQ_CTRL`, `MLX5_BOARD_ID_LEN`, `MLX5_MAX_PORTS`, register IDs such as `MLX5_REG_PCAP`, `MLX5_REG_MCAM`, and `MLX5_REG_RESOURCE_DUMP`, and capability-related enums for atomics, page-fault resume flags, DCBX mode, debug resource type, port policy, and core device type.
- Command infrastructure centers on `struct mlx5_cmd`, `struct mlx5_cmd_work_ent`, `struct mlx5_cmd_msg`, `struct mlx5_cmd_mailbox`, `struct mlx5_cmd_stats`, `struct mlx5_async_ctx`, and `struct mlx5_async_work`. Public command entry points include `mlx5_cmd_exec()`, `mlx5_cmd_do()`, `mlx5_cmd_check()`, `mlx5_cmd_exec_polling()`, `mlx5_cmd_exec_cb()`, `mlx5_cmd_use_events()`, `mlx5_cmd_use_polling()`, `mlx5_cmd_is_down()`, and the typed-size helper macros `mlx5_cmd_exec_inout()` and `mlx5_cmd_exec_in()`.
- `struct mlx5_core_dev` is the primary persistent device object. It holds Linux device and PCI pointers, PCI and interface state locks, firmware capabilities, command state, init segment mapping, `struct mlx5_priv`, device profile, mlx5e shared resources, RoCE/MACsec/IPsec state, clock/tracer/resource-dump handles, devlink pointer, write-combining state, and optional FPGA/SF/MACsec fields behind configuration guards.
- `struct mlx5_priv` aggregates submodule state: IRQ/EQ tables, page allocator counters and xarray, health reporter state, debugfs dentries, auxiliary devices, event dispatchers, flow steering, MPFS, eswitch, SR-IOV context, LAG, devcom, firmware reset, RoCE flow table objects, flow counter stats, rate-limit table, flow-table pool, BFREG allocators, and optional SF manager notifiers.
- Memory and queue helpers include `struct mlx5_frag_buf`, `struct mlx5_frag_buf_ctrl`, `mlx5_frag_buf_alloc_node()`, `mlx5_frag_buf_free()`, `mlx5_init_fbc()`, `mlx5_init_fbc_offset()`, `mlx5_frag_buf_get_wqe()`, and `mlx5_frag_buf_get_idx_last_contig_stride()`.
- Doorbell/UAR and BFREG types include `struct mlx5_db`, `struct mlx5_uars_page`, `struct mlx5_bfreg_head`, `struct mlx5_bfreg_data`, `struct mlx5_sq_bfreg`, plus `mlx5_db_alloc_node()`, `mlx5_db_alloc()`, `mlx5_db_free()`, `mlx5_alloc_bfreg()`, `mlx5_free_bfreg()`, `mlx5_get_uars_page()`, and `mlx5_put_uars_page()`.
- Resource-management APIs include memory key, protection domain, PSV, page-allocation, multicast group, register access, debugfs, flow-counter-adjacent, rate-limit, software ICM, TPH steering-tag, and VF get/put helpers.
- Notifier APIs split fast EQ/FW event paths from slow software paths: `mlx5_notifier_register()`, `mlx5_notifier_unregister()`, `mlx5_eq_notifier_register()`, `mlx5_eq_notifier_unregister()`, `mlx5_blocking_notifier_register()`, `mlx5_blocking_notifier_unregister()`, and `mlx5_blocking_notifier_call_chain()`.
- LAG, SR-IOV, multipath, RoCE, MACsec, and write-combining helpers include `mlx5_lag_is_*()`, `mlx5_lag_query_*()`, `mlx5_lag_for_each_peer_mdev`, `mlx5_sriov_blocking_notifier_register()`, `mlx5_core_is_pf()`, `mlx5_core_is_vf()`, `mlx5_core_is_ecpf_esw_manager()`, `mlx5_get_roce_state()`, `mlx5e_is_macsec_device()`, `mlx5_is_macsec_roce_supported()`, and `mlx5_wc_support_get()`.

## Control Flow and Lifetimes

This header does not implement the driver state machine, but it describes the shared lifetimes. A PCI-backed `mlx5_core_dev` is created by core probe code, initialized through command queue setup, firmware capability reads, page allocation, health polling, IRQ/EQ setup, flow steering, auxiliary-device creation, and optional eswitch/LAG/SF/MACsec/RDMA resources. Consumers use inline predicates and exported entry points to gate behavior on capability bits and device type. Teardown must reverse those dependencies: stop health/page workers, destroy flow tables/counters/keys, unregister notifiers, remove auxiliary devices, release BFREG/UAR pages, reclaim pages, and mark interface/PCI state down.

The command flow is represented as a queue of `mlx5_cmd_work_ent` objects. Callers prepare input/output buffers and call `mlx5_cmd_exec*()`. The command layer uses semaphores and bitmasks in `mlx5_cmd.vars`, allocates command slots/tokens under spinlocks, submits via workqueue or polling, completes by event or polling, records stats, and returns firmware status through `mlx5_cmd_check()` and `mlx5_cmd_out_err()`. Async commands hold `mlx5_async_ctx.num_inflight` until `mlx5_cmd_cleanup_async_ctx()` can wait for callbacks to drain.

The fragment-buffer inline flow is simple but fast-path sensitive: initialize `mlx5_frag_buf_ctrl` from page fragments, queue stride and queue size; resolve a WQE index by adding `strides_offset`, selecting the fragment by `log_frag_strides`, and computing the byte offset by `log_stride`. An invalid `log_stride`, `log_sz`, or offset corrupts WQE addressing.

## State and Persistence Behavior

State is in memory and hardware/firmware, not on disk. Persistent-in-runtime fields include capability arrays, command queues, health counters, page-accounting counters, xarrays of pages/statistics/privileged UIDs, notifier chains, flow-steering handles, LAG/eswitch/SR-IOV state, device resource IDs, and debugfs/devlink handles. Locks and concurrency primitives are part of the contract: `pci_status_mutex`, `intf_state_mutex`, spinlocks in command/cache/stat structures, command semaphores, health workqueues/timers, page allocator xarrays, BFREG mutexes, rate-limit mutexes, and blocking notifier heads. Firmware objects created through command APIs persist until matching destroy/dealloc functions are called.

## Dependencies and Integration Points

The header depends on Linux kernel primitives (`pci`, `irq`, `workqueue`, `completion`, `semaphore`, `xarray`, `mempool`, `notifier`, `auxiliary_bus`, `mutex`, devlink, net namespaces) and mlx5 hardware-interface headers (`device.h`, `doorbell.h`, `eq.h`). It is included by mlx5 Ethernet core, RDMA, vDPA, eswitch, LAG, IPsec/MACsec, flow steering, and page/health/command modules. Usage references in this tree show flow-steering callers in `drivers/net/ethernet/mellanox/mlx5/core/*`, RDMA callers in `drivers/infiniband/hw/mlx5/*`, and exported command/LAG/MACsec/EQ symbols bridging between subsystems.

## Risks and Edge Cases

- `struct mlx5_core_dev` and `struct mlx5_priv` are broad shared contracts; layout or semantic changes can silently break many modules.
- Command execution is highly concurrent. Slot, token, semaphore, callback, and timeout handling need strict pairing to avoid command leaks, callback-after-free, or firmware command starvation.
- Hardware capability gates must be checked before optional flows such as RoCE disable, MACsec RoCE, LAG, TPH, SF, eswitch management, and write combining.
- Inline helpers assume non-null device pointers and initialized capability/fragment metadata; misuse is likely to produce low-level memory or hardware failures rather than friendly errors.
- Notifier callbacks may run in atomic or blocking contexts depending on registration path; callback implementations must respect the context.
- Hardware resources such as mkeys, PDs, PSV objects, BFREGs, UARs, flow tables, counters, and software ICM must follow create/destroy pairing, often across error unwind paths.

## Test Signals

Useful validation includes building mlx5 core with `CONFIG_MLX5_CORE`, RDMA, eswitch, LAG, SF, TPH, and MACsec combinations; sparse/smatch checks for pointer and lock misuse; command failure injection and timeout tests; module probe/remove/reload cycles; firmware reset and health reporter tests; SR-IOV PF/VF and ECPF capability tests; RoCE enable/disable and GID table tests; LAG peer iteration and bond speed paths; and hardware or simulator tests that exercise command event mode, polling mode, page allocation, debugfs/devlink visibility, and MACsec RoCE capability gating.
