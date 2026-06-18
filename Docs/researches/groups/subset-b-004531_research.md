# Research: subset-b-004531

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/debugfs.c

## Purpose

`debugfs.c` builds the mlx5 debugfs surface for core device state. It creates the global `mlx5` debugfs root, per-device debugfs directories, command-interface statistics, firmware page counters, VHCA ID reporting, and dynamic per-resource trees for QPs, EQs, and CQs.

The file is diagnostic-only, but its reads are active: QP/EQ/CQ files issue firmware queries or CQ queries when users read debugfs entries.

## Important APIs, Types, and Functions

- `mlx5_register_debugfs()` / `mlx5_unregister_debugfs()` create and remove the global `mlx5_debugfs_root`.
- `mlx5_debugfs_get_dev_root()` returns `dev->priv.dbg.dbg_root`.
- `mlx5_qp_debugfs_init()`, `mlx5_eq_debugfs_init()`, `mlx5_cq_debugfs_init()`, and matching cleanup routines create resource subdirectories.
- `mlx5_cmdif_debugfs_init()` creates `commands/`, `slots_inuse`, and one directory per known command opcode with counters such as `n`, `average`, `failed`, and last failure fields.
- `mlx5_pages_debugfs_init()` exposes firmware page counters for PF/VF/SF/host-PF allocations and failure/drop accounting.
- `mlx5_debug_qp_add/remove()`, `mlx5_debug_eq_add/remove()`, and `mlx5_debug_cq_add/remove()` attach per-object debug entries through `add_res_tree()`.
- `qp_read_field()`, `eq_read_field()`, and `cq_read_field()` are read callbacks that query firmware or core CQ state and convert fields into text.

Key local structures are `struct mlx5_rsc_debug` and `struct mlx5_field_desc`, which connect a debugfs file back to a resource object and field index.

## Control Flow

Device setup creates top-level directories first, then command/page/resource directories. Command debugfs initializes `dev->cmd.stats` as an xarray, allocates one `struct mlx5_cmd_stats` per known opcode, and creates counter files under the opcode name. Cleanup removes the command tree, frees every xarray value, and destroys the xarray.

For resource objects, callers add an object after QP/EQ/CQ creation. `add_res_tree()` allocates a flexible `mlx5_rsc_debug`, creates a directory named by the resource number, then creates one file per field. File reads recover the owning `mlx5_rsc_debug` from the embedded field descriptor, dispatch by resource type, query hardware if needed, and return either a hex value or string.

## State and Persistence Behavior

Persistent state lives in debugfs dentries stored under `dev->priv.dbg`, command statistics in `dev->cmd.stats`, and per-object `qp->dbg`, `eq->dbg`, and `cq->dbg` pointers. `reset_write()` mutates command statistics by zeroing counters under `stats->lock`. Page counter files directly expose live fields in `dev->priv`.

Debugfs entries do not persist across driver unload. Resource file reads are snapshots and may return zero if allocation/query fails.

## Dependencies and Integration Points

The file depends on Linux debugfs, simple file operations, xarray, mlx5 command query helpers, CQ query helpers, QP/EQ/CQ core structures, and `lib/eq.h`. It integrates with QP/CQ/EQ allocation paths, command execution accounting, firmware page management, and VHCA capability reporting.

## Risks and Edge Cases

- `add_res_tree()` uses `sprintf(resn, "0x%x", rsn)` into a 32-byte buffer; resource numbers are bounded enough for current use, but `snprintf` would be more defensive.
- `dbg_read()` reconstructs the parent `mlx5_rsc_debug` with pointer arithmetic from a flexible array member. Layout changes to `struct mlx5_rsc_debug` or field allocation must preserve this assumption.
- `mlx5_debug_eq_remove()` removes `eq->dbg` but does not clear it, unlike QP/CQ removal. Repeated remove calls depend on outer lifecycle not reusing the stale pointer.
- QP/EQ/CQ reads issue firmware operations from debugfs read context and may fail during teardown, reset, or device error.
- Command stats cleanup frees xarray values after removing debugfs; readers must be excluded by debugfs removal semantics.

## Test Signals

Build with debugfs enabled, mount debugfs, load/unload mlx5, and verify `mlx5/` tree removal. Exercise QP/CQ/EQ creation and destruction while reading entries. Run command failures and confirm command stats and reset behavior. Use fault injection for allocation failures in `mlx5_cmdif_alloc_stats()` and `add_res_tree()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dev.c

## Purpose

`dev.c` owns mlx5 auxiliary-device orchestration. It decides which protocol subdrivers are supported and enabled for a core device, allocates the `priv->adev[]` array, creates/removes auxiliary devices for Ethernet, representors, RDMA, multiport RDMA, vDPA-net, DPLL, and fwctl, and handles attach/detach/rescan flows after device configuration changes.

## Important APIs, Types, and Functions

- `mlx5_eth_supported()`, `mlx5_vnet_supported()`, and `mlx5_rdma_supported()` check build options, devlink params, device role, and firmware capabilities.
- Local predicates `is_eth_rep_supported()`, `is_ib_rep_supported()`, `is_mp_supported()`, `is_dpll_supported()`, and `is_fwctl_supported()` gate auxiliary protocols.
- `mlx5_adev_init()` / `mlx5_adev_cleanup()` allocate and free the array of auxiliary-device pointers.
- `mlx5_adev_idx_alloc()` / `mlx5_adev_idx_free()` allocate stable auxiliary IDs from `mlx5_adev_ida`.
- `mlx5_attach_device()` resumes existing auxiliary drivers or creates missing supported devices.
- `mlx5_detach_device()` suspends or deletes auxiliary devices in reverse order and marks the core as detached.
- `mlx5_register_device()`, `mlx5_unregister_device()`, and `mlx5_rescan_drivers_locked()` are the main rescan controls.
- `mlx5_same_hw_devs()` compares NIC software system image GUIDs.
- `mlx5_core_reps_aux_devs_remove()` forcibly removes representor aux devices under ETH device lock.

## Control Flow

The static `mlx5_adev_devices[]` table maps protocol indexes to auxiliary suffixes and support/enable predicates. Add/rescan flows iterate forward. For a missing supported entry, `add_adev()` allocates `struct mlx5_adev`, initializes an `auxiliary_device`, sets parent/release/name/id fields, and calls `auxiliary_device_add()`. For an existing bound device, attach may call the auxiliary driver's `resume()`.

Detach iterates in reverse so dependent representor-style devices are removed before base devices. If `suspend` is requested and the aux driver implements `suspend`, the device is kept but suspended. Otherwise it is deleted and uninitialized. `delete_drivers()` removes devices whose enable predicate is now false, whose support predicate is now false, or when `MLX5_PRIV_FLAGS_DISABLE_ALL_ADEV` is set.

## State and Persistence Behavior

Persistent state includes `dev->priv.adev[]`, per-auxiliary `struct mlx5_adev`, `dev->priv.flags` bits for detach/lightweight/disable-all behavior, and the global IDA. Auxiliary devices are Linux device-model objects with release callbacks; `adev_release()` frees the `mlx5_adev` and clears `priv->adev[idx]`.

The file assumes callers hold the devlink instance lock for public attach/detach/register/unregister paths and uses `mlx5_devcom_comp_lock()` to serialize with devcom component changes.

## Dependencies and Integration Points

Dependencies include auxiliary bus APIs, mlx5 capability macros, eswitch/switchdev state, devlink driver-init params for RDMA/vDPA/Ethernet enablement, lag/multiport helpers, vDPA capability definitions, and fwctl/DPLL build options. It is central to binding `mlx5_core` to independent protocol drivers.

## Risks and Edge Cases

- Attach can partially create aux devices then fail; the caller decides whether to unwind by unregistering.
- Enable predicates use devlink driver-init values; changes generally require reload/rescan, so runtime expectations must match devlink semantics.
- `mlx5_detach_device()` skips deleting a suspended aux device; subsequent attach relies on that aux driver's resume path.
- `mlx5_core_reps_aux_devs_remove()` assumes the ETH auxiliary device lock is already held and logs if ETH is gone.
- Support checks are feature-sensitive; missing firmware caps lead to silent absence for some protocols and warnings for Ethernet-required caps.

## Test Signals

Test with combinations of `CONFIG_MLX5_CORE_EN`, `CONFIG_MLX5_INFINIBAND`, `CONFIG_MLX5_ESWITCH`, `CONFIG_MLX5_VDPA_NET`, and `CONFIG_MLX5_DPLL`. Exercise devlink driver-init toggles followed by reload/rescan. Validate attach/detach under switchdev, multiport slave, lightweight, SF, PF, and VF roles. Use sysfs unbind/rebind of aux drivers and confirm resume/suspend handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.c

## Purpose

`devlink.c` implements the core mlx5 devlink operations and driver-init parameters. It exposes firmware flashing, device info, firmware activation reloads, traps, Ethernet/RDMA/vDPA enablement, EQ sizing, hairpin sizing, max MAC list sizing, PCIe congestion thresholds, and vendor NV params.

## Important APIs, Types, and Functions

- `mlx5_devlink_alloc()` / `mlx5_devlink_free()` allocate the core devlink with `mlx5_devlink_ops`.
- `mlx5_devlink_flash_update()` calls `mlx5_firmware_flash()`.
- `mlx5_devlink_info_get()` reports board serials from VPD, PSID, running firmware version, and stored firmware version.
- `mlx5_devlink_reload_down()` and `mlx5_devlink_reload_up()` implement `driver_reinit` and `fw_activate`, including live patch for `DEVLINK_RELOAD_LIMIT_NO_RESET`.
- Trap helpers include `mlx5_devlink_traps_register()`, `mlx5_devlink_trap_report()`, `mlx5_devlink_trap_action_set()`, and action lookup/count helpers.
- `mlx5_devlink_params_register()` registers base, auxdev, max-MAC, PCIe congestion, and NV params; unregister reverses that order.
- Validation helpers enforce RoCE support, EQ depth range, hairpin queue constraints, num-doorbells limits, max MAC power-of-two constraints, and PCIe congestion threshold ranges.

## Control Flow

Devlink registration starts by registering static driver-init params and setting defaults from current device capabilities. Optional auxdev params are registered only if the matching feature is supported. Error handling unwinds previously registered param groups in reverse order.

Reload down rejects firmware reset in progress, multiport slaves, unsupported firmware activation, and non-driver-reinit operations on lightweight devices. Driver reinit unloads the device; firmware activation either triggers live patch or requests synchronized firmware reset and unload flow. Reload up reloads the driver and verifies firmware reset completion for full firmware activation.

Trap registration creates one list entry per trap in `dev->priv.traps`. Action changes are rejected in switchdev mode, limited to DROP/TRAP, and propagated through the mlx5 blocking notifier chain so consumers can veto by returning `NOTIFY_BAD`.

## State and Persistence Behavior

Persistent state includes devlink registered params and driver-init values, trap list entries under `dev->priv.traps`, firmware activation/reload side effects, and devlink info exposed to userspace. Driver-init params are intended to take effect on reload/rescan rather than immediately changing active datapath state.

## Dependencies and Integration Points

The file integrates with firmware flashing/reset (`fw_reset.h`), mlx5 health reset flows, eswitch devlink operations and rate objects, SF management, NV params, Ethernet/RDMA/vDPA auxiliary-device gating, LAG/multiport checks, and Linux devlink trap/param/info/reload APIs.

## Risks and Edge Cases

- `mlx5_devlink_serial_numbers_put()` suppresses VPD allocation failures by returning success, so missing serials are not fatal.
- Reload with VFs present is only warned as unfavorable, not blocked.
- Firmware live patch requires reset-level 0 support; full activate requires reset-level 3. Wrong expectations produce explicit extack errors.
- Trap action changes rely on notifier consumers to program hardware and report errors in `trap_event_ctx.err`.
- Param defaults are computed from current capabilities; after firmware change, callers must ensure values are reconciled with new caps.

## Test Signals

Use `devlink dev info`, firmware flash dry/error paths, `devlink dev reload action driver_reinit`, full `fw_activate`, and `limit no_reset` live patch. Validate param registration across PF/VF/SF/lightweight devices and unsupported capability cases. Test trap registration/action/reporting in legacy and switchdev modes. Fault-inject param registration failures to verify unwind order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.h

## Purpose

`devlink.h` is the internal contract for mlx5 core devlink IDs, trap state, devlink allocation, param registration, and trap operations. It also exposes the inline helper used by auxiliary-device support checks to determine whether Ethernet is enabled by devlink driver-init state.

## Important APIs, Types, and Functions

- `enum mlx5_devlink_resource_id` and `enum mlx5_devlink_port_resource_id` define resource identifiers for SF counts.
- `enum mlx5_devlink_param_id` reserves vendor param IDs after generic devlink IDs.
- `struct mlx5_trap_ctx`, `struct mlx5_devlink_trap`, and `struct mlx5_devlink_trap_event_ctx` model trap action state and notifier payload.
- Prototypes cover trap registration/reporting/action lookup, devlink allocation/free, and param registration/unregistration.
- `mlx5_core_is_eth_enabled()` reads `DEVLINK_PARAM_GENERIC_ID_ENABLE_ETH` driver-init value and returns false on lookup failure.

## Control Flow

Callers include this header to register core devlink objects early in PCI/core-device setup, then register params and traps after devlink exists. Trap consumers use the action getters/report helper while lower layers send notifier events on action changes.

## State and Persistence Behavior

The header itself has no storage, but its contracts mutate devlink param state and `dev->priv.traps`. The Ethernet-enable helper depends on devlink driver-init value state.

## Dependencies and Integration Points

It depends on `<net/devlink.h>`, `struct mlx5_core_dev`, and `priv_to_devlink()`. It is used by core devlink implementation, auxiliary-device support checks, Ethernet, eswitch, and trap producers.

## Risks and Edge Cases

- Vendor param enum order is ABI-sensitive inside the driver; new IDs should be appended carefully.
- `mlx5_core_is_eth_enabled()` treats read failure as disabled, which is conservative but can suppress Ethernet aux creation if params are not registered yet.
- Trap action is stored as `int` in `struct mlx5_trap_ctx` while most callers use `enum devlink_trap_action`.

## Test Signals

Compile all users after adding params/traps. Validate devlink params are registered before `mlx5_core_is_eth_enabled()` is used for aux-device creation. Exercise trap action get/report paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/cmd_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/cmd_tracepoint.h

## Purpose

`cmd_tracepoint.h` declares the `mlx5_cmd` tracepoint used to report mlx5 command failures with command name, opcode, op_mod, firmware status, syndrome, and Linux error code.

## Important APIs, Types, and Functions

- `TRACE_EVENT(mlx5_cmd, ...)` defines the event payload and formatted output.
- The event records dynamic strings for command and status plus fixed fields for opcode, op_mod, status, syndrome, and err.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation at `./diag/cmd_tracepoint`.

## Control Flow

When command execution code invokes `trace_mlx5_cmd(...)`, ftrace/perf consumers receive a formatted failure record. The header includes `<trace/define_trace.h>` so one including translation unit can instantiate the tracepoint.

## State and Persistence Behavior

No driver state is mutated. Trace records are transient kernel tracing data controlled by ftrace/perf infrastructure.

## Dependencies and Integration Points

Depends on Linux tracepoint APIs and is integrated with mlx5 command execution/failure reporting.

## Risks and Edge Cases

- Tracepoint format is part of tooling expectations; field renames or formatting changes can break scripts.
- Dynamic string capture assumes caller-provided strings are valid for trace assignment at call time.

## Test Signals

Build with tracing enabled and trigger a failing firmware command. Verify `/sys/kernel/tracing/events/mlx5/mlx5_cmd/format` contains the expected fields and perf/ftrace output includes opcode, op_mod, status, syndrome, and err.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/cmd_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/crdump.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/crdump.c

## Purpose

`crdump.c` provides collection and enablement for mlx5 protected CR-space dumps through the PCI VSC gateway. It is used by health/debug paths to snapshot device control-register space when supported.

## Important APIs, Types, and Functions

- `mlx5_crdump_enable()` probes PF-only VSC access, selects scan CR-space, reads its size, and stores it in `dev->priv.health.crdump_size`.
- `mlx5_crdump_disable()` clears the stored dump size.
- `mlx5_crdump_collect()` locks the VSC gateway, takes the SW-reset semaphore, selects CR-space scan space, and fills caller-provided memory.
- `mlx5_crdump_fill()` initializes the buffer with `BAD_ACCESS`, reads the dump block, and verifies the full expected size was read.

## Control Flow

Enablement is a capability probe: non-PF, inaccessible VSC, already-enabled, or unsupported scan space all return success with no dump enabled. Collection refuses if disabled, then serializes access with `mlx5_vsc_gw_lock()` and `MLX5_SEMAPHORE_SW_RESET`. It always releases the semaphore and gateway lock on exit after a successful acquisition.

## State and Persistence Behavior

The only persistent state is `dev->priv.health.crdump_size`. Dump data is written into caller memory. The file temporarily changes VSC gateway space and semaphore state during collection.

## Dependencies and Integration Points

Depends on `lib/pci_vsc.h`, `lib/mlx5.h`, mlx5 health state, and VSC gateway/semaphore helpers. It integrates with health reporters or crash diagnostics that allocate dump buffers.

## Risks and Edge Cases

- Unsupported CR-space scanning is intentionally masked during enablement, so absence of dumps may be silent.
- `mlx5_crdump_collect()` relies on the caller to pass a buffer large enough for `crdump_size`.
- If another PF is resetting or dumping, collection returns busy or semaphore errors.
- Partial VSC reads return `-EINVAL` after logging how much was read.

## Test Signals

Run on PF hardware with VSC access and verify enablement sets a nonzero dump size. Exercise concurrent dump/reset attempts to verify semaphore handling. Fault-inject short reads and gateway lock failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/crdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_rep_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_rep_tracepoint.h

## Purpose

`en_rep_tracepoint.h` declares a representor-neighbor tracepoint for mlx5 Ethernet eswitch/representor neighbor updates.

## Important APIs, Types, and Functions

- `TRACE_EVENT(mlx5e_rep_neigh_update, ...)` records netdev name, MAC address, IPv4/IPv6 destination, and neighbor connectivity.
- The event reads `struct mlx5e_neigh_hash_entry`, `struct mlx5e_neigh`, and a hardware address passed by the caller.

## Control Flow

Representor neighbor update code calls the generated `trace_mlx5e_rep_neigh_update()` helper. The trace assignment maps IPv4 into an IPv6-mapped address for consistent output and copies IPv6 directly for AF_INET6.

## State and Persistence Behavior

No persistent state is changed. Events are transient tracing output.

## Dependencies and Integration Points

Depends on Linux tracepoint APIs and `en_rep.h` neighbor types. It integrates with TC/eswitch representor neighbor tracking and offload debugging.

## Risks and Edge Cases

- The tracepoint assumes `nhe->neigh_dev` and `ha` remain valid during trace assignment.
- Families other than AF_INET/AF_INET6 leave address arrays zeroed.

## Test Signals

Enable the tracepoint and trigger representor neighbor connect/disconnect events for IPv4 and IPv6. Verify netdev name, MAC, addresses, and `neigh_connected` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_rep_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.c

## Purpose

`en_tc_tracepoint.c` instantiates mlx5 TC tracepoints and provides helpers to convert Linux flow action IDs into printable action names.

## Important APIs, Types, and Functions

- `CREATE_TRACE_POINTS` causes `en_tc_tracepoint.h` tracepoints to be defined here.
- `put_ids_to_array()` copies `flow_action_entry.id` values into tracepoint dynamic arrays.
- `parse_action()` formats an array of action IDs into action names using `FLOWACT2STR`.
- `FLOWACT2STR` maps supported `FLOW_ACTION_*` IDs to fixed 16-byte names.

## Control Flow

TC tracepoint fast-assign code calls `put_ids_to_array()` to snapshot action IDs. Print formatting calls `parse_action()`, which writes action names into the trace sequence and returns the resulting buffer pointer.

## State and Persistence Behavior

No persistent driver state is changed. Output exists only in trace buffers.

## Dependencies and Integration Points

Depends on `en_tc_tracepoint.h`, Linux `flow_offload.h`, and trace sequence helpers. It integrates with mlx5e TC flower configure/delete/stats tracepoints.

## Risks and Edge Cases

- `FLOWACT2STR` must track `NUM_FLOW_ACTIONS`; newer action IDs not listed print `UNKNOWN`.
- Names are fixed-width by declaration, so longer future names require updating `NAME_SIZE`.

## Test Signals

Compile after kernel flow action enum changes. Enable `mlx5e_configure_flower` tracing and install TC flower rules with varied actions to verify printed action names and unknown handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.h

## Purpose

`en_tc_tracepoint.h` declares tracepoints for mlx5e TC flower offload configure/delete/stats and neighbor-used updates.

## Important APIs, Types, and Functions

- `DECLARE_EVENT_CLASS(mlx5e_flower_template, ...)` captures a flower rule cookie and action IDs.
- `DEFINE_EVENT(... mlx5e_configure_flower ...)` and `DEFINE_EVENT(... mlx5e_delete_flower ...)` share the template.
- `TRACE_EVENT(mlx5e_stats_flower, ...)` records cookie, bytes, packets, and last-used time.
- `TRACE_EVENT(mlx5e_tc_update_neigh_used_value, ...)` records neighbor netdev, address, and used state.
- Helper prototypes `put_ids_to_array()` and `parse_action()` are implemented in `en_tc_tracepoint.c`.

## Control Flow

TC offload paths call generated trace helpers around rule add/delete/stats operations. The flower template handles absent `f->rule` by recording zero actions and printing `NULL`.

## State and Persistence Behavior

The file defines observability only; no mlx5 runtime state is persisted or changed.

## Dependencies and Integration Points

Depends on Linux tracepoints, trace sequence, `net/flow_offload.h`, and `en_rep.h`. It integrates with mlx5e TC, representor neighbor tracking, and ftrace/perf tooling.

## Risks and Edge Cases

- `f->cookie` is printed as a pointer-shaped value although it is a cookie cast to `void *`.
- Neighbor trace assignment assumes valid `nhe->neigh_dev`.
- Tracepoint schema changes may affect external debugging scripts.

## Test Signals

Enable TC tracepoints, add/delete flower rules with and without actions, query stats, and update IPv4/IPv6 neighbors. Verify fields and action formatting in trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fs_tracepoint.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fs_tracepoint.c

## Purpose

`fs_tracepoint.c` instantiates mlx5 flow-steering tracepoints and implements formatting helpers for flow match headers and destinations. It turns raw mlx5 match masks/values into readable L2/L3/L4, misc, and destination strings.

## Important APIs, Types, and Functions

- `parse_fs_hdrs()` prints outer, misc, and inner match sections according to `match_criteria_enable`.
- `parse_fs_dst()` formats `struct mlx5_flow_destination` variants such as uplink, vport, flow table, TIR, sampler, counter, port, range, table type, none, and VHCA RX.
- `print_lyr_2_4_hdrs()` extracts masked MAC, ethertype, IPv4/IPv6, protocol, ports, VLAN, DSCP/ECN, and fragmentation fields.
- `print_misc_parameters_hdrs()` extracts GRE key, source SQN/port, second VLAN tags, GRE protocol, VXLAN VNI, and IPv6 flow labels.
- `EXPORT_TRACEPOINT_SYMBOL()` exports the flow-steering tracepoints for module users.

## Control Flow

Tracepoint printing code from `fs_tracepoint.h` calls `parse_fs_hdrs()` or `parse_fs_dst()`. The helpers inspect masks first and print only fields whose mask is set. For IPv4/IPv6 addresses, they print based on either ethertype or IP-version mask/value. Destination formatting switches on destination type.

## State and Persistence Behavior

No persistent driver state is changed. The functions operate on tracepoint-copied values and emit transient trace text.

## Dependencies and Integration Points

Depends on `fs_tracepoint.h`, `fs_core.h`, mlx5 IFC field access macros, Linux trace sequence helpers, and Ethernet/IP constants. It integrates with flow table/group/FTE/rule lifecycle tracing.

## Risks and Edge Cases

- Formatting helpers interpret raw firmware match layouts; any IFC layout change requires updates.
- `parse_fs_dst()` handles all known destination enum values in this source snapshot but has no default branch, so future enum additions can compile-warning or print nothing depending on compiler settings.
- IPv6 printing only occurs for full all-ones masks, so partial IPv6 masks are not displayed.
- Destination `FLOW_TABLE_TYPE` dereferences `dst->ft`; callers must ensure copied destination data still meaningfully contains that pointer for tracing.

## Test Signals

Enable flow-steering tracepoints and create/delete flow tables, groups, FTEs, and rules with IPv4, IPv6, VLAN, GRE, VXLAN, TIR, vport, counter, and range destinations. Confirm decoded masks/values match rule programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fs_tracepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fs_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fs_tracepoint.h

## Purpose

`fs_tracepoint.h` declares mlx5 flow-steering tracepoints for flow table, flow group, flow table entry, and flow rule add/delete operations.

## Important APIs, Types, and Functions

- `TRACE_EVENT(mlx5_fs_add_ft/del_ft)` records flow table pointer, id, level, and type.
- `TRACE_EVENT(mlx5_fs_add_fg/del_fg)` records group range, id, match criteria enable flags, and masks.
- `TRACE_EVENT(mlx5_fs_set_fte/del_fte)` records FTE index, action flags, flow tag/source, masks, values, and whether this is add vs set.
- `TRACE_EVENT(mlx5_fs_add_rule/del_rule)` records rule pointer, owning FTE, software action, destination, and counter ID.
- `ACTION_FLAGS` maps mlx5 flow context action bits to printable strings.
- `__parse_fs_hdrs()` and `__parse_fs_dst()` call helper functions implemented in `fs_tracepoint.c`.

## Control Flow

Flow steering code emits these tracepoints during object lifecycle changes. The fast-assign blocks copy masks, values, and destination structs into the trace entry so printing does not depend on later object lifetime.

## State and Persistence Behavior

No driver state is mutated. The tracepoint payload is transient tracing state.

## Dependencies and Integration Points

Depends on Linux tracepoint APIs, `../fs_core.h`, mlx5 flow steering object layouts, and helper implementations in `fs_tracepoint.c`. Tracepoints are exported by the C file for use by other modules.

## Risks and Edge Cases

- The `mlx5_fs_add_rule` trace checks `rule->dest_attr.type & MLX5_FLOW_DESTINATION_TYPE_COUNTER`; destination type is an enum, so bitwise treatment depends on mlx5 destination constants remaining compatible with this pattern.
- Pointer fields in trace output are diagnostic identifiers, not stable object handles.
- Tracepoint payload sizes include several match arrays; enabling tracing on heavy flow churn can be expensive.

## Test Signals

Run flow steering add/delete tests with tracing enabled and compare emitted object IDs, match fields, actions, and destinations to programmed rules. Build with tracepoints enabled as a module/export consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fs_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.c

## Purpose

`fw_tracer.c` implements mlx5 firmware trace collection. It allocates a DMA log buffer, creates an mkey for firmware writes, reads firmware string databases, acquires tracer ownership, handles firmware tracer EQ events, decodes string/timestamp trace records, emits the `mlx5_fw` tracepoint, and stores recent decoded traces for devlink health dumps.

## Important APIs, Types, and Functions

- `mlx5_fw_tracer_create()` allocates software state, workqueue, log buffer, string DB buffers, and saved-trace storage after querying `MTRC_CAP`.
- `mlx5_fw_tracer_init()` allocates PD/mkey, registers an EQ notifier, queues string DB reading, and starts the tracer.
- `mlx5_fw_tracer_cleanup()` unregisters notifier, cancels work, releases ownership, and destroys PD/mkey.
- `mlx5_fw_tracer_destroy()` frees software resources, string DB buffers, log buffer, saved trace mutex, workqueue, and tracer object.
- `mlx5_fw_tracer_reload()` stops tracing, recreates string DB state, and reinitializes.
- `fw_tracer_event()` dispatches ownership change, traces available, and strings DB update EQ subtypes to work items.
- `mlx5_fw_tracer_handle_traces()` consumes the circular trace buffer, detects overwritten blocks, parses records, and rearms firmware events.
- `mlx5_tracer_handle_string_trace()` and timestamp handling assemble multi-record formatted messages.
- `mlx5_fw_tracer_get_saved_traces_objects()` emits saved traces into a devlink fmsg.
- `mlx5_fw_tracer_trigger_core_dump_general()` writes the core dump register and drains traces synchronously.

## Control Flow

Creation probes tracer registers and `trace_to_memory`, then records string DB addresses/sizes and current owner state. Initialization reads string DB asynchronously if not loaded, marks tracer UP under `state_lock`, allocates hardware resources, registers the EQ notifier, and calls `mlx5_fw_tracer_start()`. Start tries to acquire ownership; ownership failure is nonfatal because later events may grant it. When owned, it writes `MTRC_CONF` with trace mode, buffer size, and mkey, then enables/arms tracing with `MTRC_CTRL`.

On traces-available EQ events, the handler copies one 256-byte block from the DMA buffer, parses the final timestamp, and advances while block timestamps are newer than `last_timestamp`. It compares the previous block timestamp to detect wrap overwrite and logs lost events. String events either start a format string, append parameters, or fall back to raw output. Timestamp events flush ready strings with reconstructed full timestamps.

## State and Persistence Behavior

Persistent tracer state includes firmware ownership, tracer version, string DB metadata and buffers, DMA log buffer, PD/mkey, circular consumer index, `last_timestamp`, hash table of in-progress formatted messages, ready list, saved trace ring (`SAVED_TRACES_NUM`), workqueue items, EQ notifier, and state bits (`UP`, `RECREATE_DB`). Saved traces are a ring protected by `st_arr.lock`.

Firmware-visible state is changed through `MTRC_CAP`, `MTRC_CONF`, `MTRC_CTRL`, `MTRC_STDB`, and `CORE_DUMP` registers.

## Dependencies and Integration Points

Depends on mlx5 register access, EQ notifier infrastructure, DMA mapping, PD/mkey allocation, Linux workqueues, jhash, tracepoint `mlx5_fw`, and devlink fmsg. It is integrated with health reporters and firmware diagnostic workflows.

## Risks and Edge Cases

- `mlx5_tracer_get_string()` uses strict `str_ptr > base && str_ptr < base + size`; a string exactly at the base address would not match.
- Format strings are modified in place to replace `%llx` with `%x%x`; string DB buffers must be writable and not shared as immutable data.
- The saved traces dump loop stops before `end_index`, so it may omit the newest entry depending on ring index semantics.
- Work cancellation intentionally uses `cancel_work()` rather than `cancel_work_sync()` for `update_db_work` during cleanup because cleanup can run from that work item; this requires careful sequencing in future changes.
- Heavy trace rates can overwrite circular blocks before software handles them, detected only by timestamp comparison.
- Invalid or unsupported format specifiers are marked `BAD_FORMAT` to avoid unsafe formatting.

## Test Signals

Validate on hardware with tracer registers. Enable `mlx5_fw` tracepoint, trigger firmware trace events, ownership changes, string DB updates, and core dumps. Test reload while traces arrive. Fault-inject PD/mkey/string DB/log buffer allocation failures. Verify devlink saved trace dumps and lost-event warnings under high trace rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.h

## Purpose

`fw_tracer.h` defines the firmware tracer data model, constants, firmware event layouts, state bits, and public lifecycle/API entry points.

## Important APIs, Types, and Functions

- Constants define string DB section counts/read sizes, trace buffer geometry, block size, saved trace count, parameter limits, and timestamp masks.
- `struct mlx5_fw_trace_data` is the saved decoded trace object exported to devlink.
- `struct mlx5_fw_tracer` holds core device pointer, EQ notifier, workqueue/work items, string DB state, DMA buffer state, saved trace ring, timestamp/hash/list state, and locks.
- `struct tracer_string_format`, `struct tracer_event`, `struct tracer_string_event`, and `struct tracer_timestamp_event` describe decoded or partially decoded firmware trace records.
- Public prototypes cover create/init/cleanup/destroy, core dump trigger, saved trace export, and reload.

## Control Flow

The header separates software resource creation from hardware activation: callers create once, initialize when device hardware is up, cleanup before teardown/reset, destroy at final device release, and reload on firmware string DB update.

## State and Persistence Behavior

The declared `mlx5_fw_tracer` object persists across active tracing sessions and reloads. It owns memory that firmware writes through an mkey, cached string DB data, saved decoded traces, and synchronization state.

## Dependencies and Integration Points

Depends on Linux mlx5 driver headers and `mlx5_core.h`. It is consumed by `fw_tracer.c`, the tracepoint header, and health/devlink diagnostics that dump saved firmware traces.

## Risks and Edge Cases

- Buffer geometry constants assume `TRACE_BUFFER_SIZE_BYTE` is a power-of-two multiple of `TRACER_BLOCK_SIZE_BYTE`.
- `SAVED_TRACES_NUM` is used with bitmask wrapping, so it must remain a power of two.
- Firmware event bitfield declarations must match device IFC layouts.
- Public callers must treat `ERR_PTR` and `NULL` tracer returns as valid unsupported/error states.

## Test Signals

Compile with firmware tracer users. Add static/build checks if constants change. Exercise lifecycle: create, init, cleanup, reload, destroy, and saved trace export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer_tracepoint.h

## Purpose

`fw_tracer_tracepoint.h` declares the `mlx5_fw` tracepoint used by firmware tracer decoding to emit human-readable firmware log messages.

## Important APIs, Types, and Functions

- `TRACE_EVENT(mlx5_fw, ...)` records device name, trace timestamp, lost-event flag, event ID, and decoded message string.
- The generated trace helper is called from `mlx5_tracer_print_trace()`.

## Control Flow

Decoded trace strings are formatted by `fw_tracer.c`, then passed to `trace_mlx5_fw()`. The tracepoint snapshots the dev name and message as dynamic strings and prints them with timestamp/lost/event metadata.

## State and Persistence Behavior

No driver state is mutated. Events are transient tracing output.

## Dependencies and Integration Points

Depends on Linux tracepoints and `fw_tracer.h`. The tracepoint is exported by `fw_tracer.c` for tracing tools.

## Risks and Edge Cases

- The tracepoint assumes `tracer->dev->device` is valid when the event is emitted.
- Message contents are firmware-controlled after validation/formatting in `fw_tracer.c`; tooling should not assume stable wording.

## Test Signals

Enable `events/mlx5/mlx5_fw`, trigger firmware traces, and verify dev name, timestamp, lost flag, event ID, and message formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.c

## Purpose

`reporter_vnic.c` implements a devlink health reporter named `vnic` that diagnoses vNIC environment counters and optional ICM consumption.

## Important APIs, Types, and Functions

- `mlx5_reporter_vnic_create()` / `mlx5_reporter_vnic_destroy()` manage the devlink health reporter in `dev->priv.health.vnic_reporter`.
- `mlx5_reporter_vnic_diagnose_counters()` issues `QUERY_VNIC_ENV` for a vport and writes supported counters into a devlink fmsg.
- `mlx5_reporter_vnic_diagnose_counter_icm()` reads `NIC_CAP` and `VHCA_ICM_CTRL` to expose ICM consumption when supported.
- `mlx5_reporter_vnic_diagnose()` is the reporter diagnose callback for the local vport.

## Control Flow

Diagnose builds a command input for vport 0 or a requested other vport, executes `query_vnic_env`, starts a nested fmsg object, then conditionally emits counters based on `MLX5_CAP_GEN()` feature bits. ICM reporting first checks `nic_cap_reg`, reads whether `vhca_icm_ctrl` is available, resolves vport to VHCA ID for other-vport mode, and reads current allocated ICM.

## State and Persistence Behavior

Persistent state is limited to the reporter pointer in health state. Counter data is sampled on demand and emitted to devlink messages; it is not cached.

## Dependencies and Integration Points

Depends on devlink health reporter APIs, mlx5 command interface, vport VHCA lookup, `en_stats.h` counter macros, and core devlink access. It integrates with core health reporter creation/destruction.

## Risks and Edge Cases

- `mlx5_cmd_exec_inout()` return value in `mlx5_reporter_vnic_diagnose_counters()` is ignored, so failed `QUERY_VNIC_ENV` can produce zero/default output.
- devlink fmsg helper return values are ignored, consistent with many reporters but less robust under message construction failures.
- Other-vport ICM reporting depends on successful vport-to-VHCA lookup.

## Test Signals

Run `devlink health diagnose` for the vNIC reporter across devices with different counter capabilities. Inject command failures and verify logs/output behavior. Test other-vport counter export through callers that pass `other_vport=true`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.h

## Purpose

`reporter_vnic.h` declares the vNIC health reporter lifecycle and shared counter-diagnose helper.

## Important APIs, Types, and Functions

- `mlx5_reporter_vnic_create()` creates the devlink health reporter.
- `mlx5_reporter_vnic_destroy()` destroys it if present.
- `mlx5_reporter_vnic_diagnose_counters()` writes vNIC environment counters for a selected vport to a devlink fmsg.

## Control Flow

Core health setup includes this header to create/destroy the reporter. Other health reporters can call the counter helper to include vNIC counters in their own diagnostics.

## State and Persistence Behavior

The header has no storage. Implementations mutate `dev->priv.health.vnic_reporter` and sample firmware counters.

## Dependencies and Integration Points

Depends on `mlx5_core.h` and devlink fmsg types. It integrates core health diagnostics with vNIC/environment counter reporting.

## Risks and Edge Cases

Callers must pass a valid `devlink_fmsg`, vport number, and correct `other_vport` flag. Reporter creation can fail and is represented as an error pointer in health state.

## Test Signals

Compile all health reporter users and run devlink health diagnose paths with and without the vNIC reporter present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.c

## Purpose

`rsc_dump.c` implements mlx5 firmware resource dumps. It discovers supported dump segment types from the firmware menu, creates a physical-address mkey for dump DMA, builds resource dump commands, and exposes an iterator-style API for callers to fetch dump pages.

## Important APIs, Types, and Functions

- `mlx5_rsc_dump_create()` allocates `struct mlx5_rsc_dump` if `MLX5_CAP_DEBUG(resource_dump)` is present.
- `mlx5_rsc_dump_init()` allocates a PD, creates a PA mkey, and reads the firmware dump menu.
- `mlx5_rsc_dump_cleanup()` destroys the mkey and deallocates the PD.
- `mlx5_rsc_dump_destroy()` frees software state.
- `mlx5_rsc_dump_cmd_create()` builds a command for a requested `struct mlx5_rsc_key`.
- `mlx5_rsc_dump_next()` triggers one dump page and returns whether more dump data remains.
- `mlx5_rsc_dump_menu()` reads menu pages and fills `fw_segment_type[]`.

## Control Flow

Initialization creates hardware resources and reads the menu using a special menu segment type. Menu parsing maps firmware segment names to local `enum mlx5_sgmt_type` indexes and records firmware segment IDs. Callers create a command with resource type/index/count/size, then repeatedly call `mlx5_rsc_dump_next()`. Each trigger DMA maps the provided page, fills mkey/address in the command, accesses `MLX5_REG_RESOURCE_DUMP`, validates the firmware sequence number, unmaps the page, and returns `more_dump`.

## State and Persistence Behavior

Persistent state in `dev->rsc_dump` includes PD number, mkey, number of menu items, and the firmware segment type map. Command state stores the firmware resource dump command buffer and requested memory size; firmware updates the command buffer with sequence, size, and continuation flags across calls.

## Dependencies and Integration Points

Depends on mlx5 debug capabilities, core PD/mkey APIs, DMA mapping, firmware register access, Linux pages, and segment definitions from `<linux/mlx5/rsc_dump.h>`. It is used by Ethernet health dumping (`en/health.c`) and other diagnostics.

## Risks and Edge Cases

- `mlx5_rsc_dump_cmd_create()` rejects segment type zero except for menu, so firmware using zero for a real segment would be treated unsupported.
- Menu parsing compares string names; unknown names are ignored.
- `cmd->mem_size` comes from the key and must not exceed the actual mapped page size used by callers.
- Sequence mismatch returns `-EIO`, indicating lost or corrupted dump continuation.
- Cleanup assumes init succeeded enough to create mkey/PD when `dev->rsc_dump` is non-null; lifecycle callers must pair correctly.

## Test Signals

Run resource dump init on capable and incapable devices. Dump menu and known resources such as QP/CQ/MKEY. Exercise multi-page dumps and verify sequence increments. Fault-inject DMA mapping, mkey creation, menu read, and register access failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.h

## Purpose

`rsc_dump.h` declares the mlx5 resource dump lifecycle and command iteration API used by health reporters and diagnostics.

## Important APIs, Types, and Functions

- `MLX5_RSC_DUMP_ALL` is a wildcard/count constant for dump requests.
- Forward declarations hide `struct mlx5_rsc_dump` and `struct mlx5_rsc_dump_cmd`.
- Lifecycle: `mlx5_rsc_dump_create()`, `mlx5_rsc_dump_destroy()`, `mlx5_rsc_dump_init()`, `mlx5_rsc_dump_cleanup()`.
- Command API: `mlx5_rsc_dump_cmd_create()`, `mlx5_rsc_dump_cmd_destroy()`, `mlx5_rsc_dump_next()`.

## Control Flow

Callers create and initialize device-level dump support, then for each dump allocate a command from `struct mlx5_rsc_key`, call `next()` until it returns zero, and destroy the command.

## State and Persistence Behavior

The API owns hidden per-device state and per-command continuation state. Callers own pages passed to `mlx5_rsc_dump_next()`.

## Dependencies and Integration Points

Depends on `<linux/mlx5/rsc_dump.h>`, core driver headers, and `mlx5_core.h`. It integrates with Ethernet health dump helpers and firmware debug resource support.

## Risks and Edge Cases

Callers must handle `NULL` or `ERR_PTR` `dev->rsc_dump` as unsupported, pass a page large enough for the command size, and destroy commands on all paths.

## Test Signals

Compile health reporter users and run resource dump paths on both unsupported and supported devices. Check that repeated `next()` calls terminate and cleanup frees PD/mkey resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dpll.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dpll.c

## Purpose

`dpll.c` is the mlx5 auxiliary DPLL driver for SyncE/EEC support. It registers a Linux DPLL device and input pin, maps mlx5 SyncE firmware status into DPLL lock/pin/quality-level state, tracks the uplink netdev for pin association, and periodically notifies userspace when lock or pin state changes.

## Important APIs, Types, and Functions

- `struct mlx5_dpll` stores DPLL device/pin handles, trackers, mlx5 core device, workqueue, last-notified status, notifier block, and tracked netdev.
- Firmware register helpers: `mlx5_dpll_clock_id_get()`, `mlx5_dpll_synce_status_get()`, and `mlx5_dpll_synce_status_set()`.
- Mapping helpers convert firmware status to `enum dpll_lock_status`, lock-status error, pin state, fractional frequency offset, and ITU option 1 quality levels.
- DPLL ops: `mlx5_dpll_device_lock_status_get()`, `mlx5_dpll_device_mode_get()`, `mlx5_dpll_clock_quality_level_get()`.
- Pin ops: direction get, state get/set, and FFO get.
- `mlx5_dpll_probe()` creates/registers the DPLL device and pin, creates a workqueue, tracks netdev events, and starts periodic polling.
- `mlx5_dpll_remove()` cancels polling, unregisters tracking, destroys DPLL objects, and returns firmware to free-running.

## Control Flow

Probe first sets SyncE admin state to free-running, reads a clock identity, allocates state, gets shared DPLL/pin objects by clock ID and device index, registers them with callbacks, creates a single-thread workqueue, registers a blocking notifier for uplink netdev events, replays the current uplink event, and queues periodic work.

Periodic work reads `MSEES`, derives lock and pin state, sends DPLL change notifications when the value differs from the last valid sample, records the new values, and reschedules itself every 500 ms. Pin state set writes `MSEES` to switch firmware between track and free-running.

## State and Persistence Behavior

Persistent state includes the auxiliary driver's `mlx5_dpll`, registered DPLL device/pin references, firmware SyncE admin status, last observed lock/pin state, workqueue/delayed work, and netdev pin association. Firmware SyncE state is explicitly reset to free-running at probe start and remove end.

## Dependencies and Integration Points

Depends on Linux DPLL subsystem, auxiliary bus, mlx5 register access (`MSECQ`, `MSEES`), mlx5 blocking notifier events, uplink netdev replay, and `CONFIG_MLX5_DPLL` aux-device creation in `dev.c`.

## Risks and Edge Cases

- Periodic register polling every 500 ms can keep reporting delayed state if firmware access fails; failures simply reschedule.
- Quality-level mapping currently accepts network option 1 only and returns `-EINVAL` for unknown codes.
- Multiple mlx5 devices may share a DPLL device and pin; tracker usage must stay paired.
- Remove cancels work before unregistering notifiers, which is important for avoiding callbacks after free.
- Suspend/resume are no-ops; platform power flows rely on upper mlx5 cleanup/reprobe behavior.

## Test Signals

Register the `mlx5_core.dpll` auxiliary driver on SyncE-capable hardware, inspect DPLL netlink state, toggle pin state, disconnect media, and verify lock/pin notifications. Test shared-clock multiport devices and module unload/reload. Fault-inject register access failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.c

## Purpose

`ecpf.c` handles embedded CPU PF (ECPF) host-PF administration. It detects embedded CPU state, enables/disables the external host PF HCA when the ECPF is responsible, and waits for host PF/VF firmware pages to be reclaimed during cleanup.

## Important APIs, Types, and Functions

- `mlx5_read_embedded_cpu()` reads the initialization segment bit `MLX5_ECPU_BIT_NUM`.
- `mlx5_cmd_host_pf_enable_hca()` / `mlx5_cmd_host_pf_disable_hca()` send `ENABLE_HCA` and `DISABLE_HCA` commands for function ID 0 with `embedded_cpu_function=0`.
- `mlx5_ec_init()` initializes ECPF host-PF administration.
- `mlx5_ec_cleanup()` disables host PF administration and waits for host PF/VF page counters.
- Local `mlx5_host_pf_init()` / `mlx5_host_pf_cleanup()` call eswitch host-PF HCA helpers unless eswitch-manager mode owns that lifecycle.

## Control Flow

If the core device is not an ECPF, init and cleanup are no-ops. For ECPF devices, init enables the external host PF HCA unless eswitch manager mode will do so after eswitch setup. Cleanup reverses the operation, then waits for firmware pages attributed to `MLX5_HOST_PF` and `MLX5_VF`.

## State and Persistence Behavior

The file changes firmware HCA enable state for the host PF and observes page counters in `dev->priv.page_counters`. It does not allocate local persistent state.

## Dependencies and Integration Points

Depends on eswitch support, mlx5 command execution, core role helpers, firmware page wait helpers, and `ecpf.h`. It integrates with core device init/cleanup and eswitch host-PF management.

## Risks and Edge Cases

- Cleanup logs but does not fail on host PF disable errors or page reclaim timeouts.
- Eswitch-manager mode changes who enables/disables the host PF; lifecycle ordering with eswitch setup/teardown is critical.
- The host PF command uses function ID 0, so changes to function numbering assumptions would be high impact.

## Test Signals

Boot ECPF hardware in separate host mode and eswitch-manager mode. Verify host PF HCA enable/disable commands and page reclaim waits. Test cleanup while host PF/VFs still hold pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.h

## Purpose

`ecpf.h` declares ECPF helpers and provides no-op stubs when eswitch support is disabled.

## Important APIs, Types, and Functions

- `MLX5_ECPU_BIT_NUM` identifies the embedded CPU bit in the initialization segment.
- Declarations cover embedded CPU read, ECPF init/cleanup, and host-PF enable/disable HCA commands.
- Without `CONFIG_MLX5_ESWITCH`, inline stubs return false or success and do nothing.

## Control Flow

Core initialization can include this header unconditionally. Build-time stubs remove ECPF side effects when eswitch support is absent.

## State and Persistence Behavior

No state in the header. Implementations mutate firmware HCA state and wait on page counters.

## Dependencies and Integration Points

Depends on Linux mlx5 driver headers and `mlx5_core.h`. It is used by core device lifecycle and eswitch/ECPF handling.

## Risks and Edge Cases

Consumers must not assume ECPF behavior exists when `CONFIG_MLX5_ESWITCH` is disabled. Stubbed `mlx5_ec_init()` returning success can hide missing eswitch functionality in builds that do not support it.

## Test Signals

Compile with and without `CONFIG_MLX5_ESWITCH`. Verify callers do not require symbols unavailable in the stub configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en.h

## Purpose

`en.h` is the central mlx5e Ethernet driver contract. It defines datapath/control structures for channels, RQs, SQs, CQs, XDP/AF_XDP, PTP, flow steering, DCB, health reporters, profile callbacks, feature flags, sizing constants, and public function prototypes used across the mlx5e Ethernet implementation.

## Important APIs, Types, and Functions

Major definitions include:

- Sizing/feature constants for MTU conversion, MPWQE/UMR limits, queue sizes, CQ moderation defaults, channel counts, and TX recovery intervals.
- `struct mlx5e_params` for active channel/netdev configuration: queue sizes, RQ type, channel count, mqprio/DCB, moderation, packet merge, inline mode, VLAN/FCS, DIM, XDP, XSK, MTU, PTP RX, and terminate lkey.
- Datapath structures: `mlx5e_cq`, `mlx5e_txqsq`, `mlx5e_xdpsq`, `mlx5e_icosq`, `mlx5e_rq`, `mlx5e_channel`, and `mlx5e_channels`.
- State enums for RQ, SQ, channel, private interface, profile features, packet merge mode, and devcom events.
- `struct mlx5e_priv`, the primary netdev private state with channel maps, RX resources, flow steering, work items, stats, reporters, feature modules, DCB/XSK/QoS state, debugfs root, and devcom.
- `struct mlx5e_profile`, the callback table for NIC/profile-specific init, cleanup, enable/disable, stats, carrier, TIS, and feature behavior.
- Prototypes for open/close, channel switching, queue creation/destruction, moderation, stats, ethtool, VLAN, XDP, mkey/TIS, flow steering, health, and netdev profile management.

## Control Flow

This header defines the common lifecycle shape but implements little behavior. Typical mlx5e flows allocate `mlx5e_priv`, build `mlx5e_params`, create device resources, open channels, activate queues, attach netdev, and later safe-switch or reopen channels under `state_lock`. Channel structures aggregate one RQ, per-TC SQs, internal control SQs, XDP SQs, optional AF_XDP RQ/SQ, NAPI, and queue metadata.

Datapath handlers are function pointers selected from params and feature state. Health/reporting paths use the same structure fields for diagnostics and recovery. Profile callbacks allow NIC, representor, and other profiles to share core open/close/channel machinery while customizing resources and features.

## State and Persistence Behavior

`struct mlx5e_priv` persists for the netdev lifetime and owns long-lived resources such as flow steering, RX resources, workqueue, stats, health reporters, XSK pools, DCB state, QoS state, feature modules, and channel arrays. `struct mlx5e_channels` and individual channel/queue objects persist while the netdev is open or channels are allocated. Queue producer/consumer indexes, DIM state, page pools, XDP program pointers, CQ state, and hardware object IDs are mutable datapath state.

Concurrency is split between datapath cacheline-aligned fields, `state_lock`, netdev/RTNL locking in callers, RCU for selected queue mappings, spinlocks for ICOSQ synchronization, and workqueue recovery paths.

## Dependencies and Integration Points

The header connects nearly every mlx5e module: flow steering, RX resources, DCB, QoS, PTP, TLS/IPsec/PSP/MACsec optional accelerators, XDP/AF_XDP, devlink health reporters, ethtool, netdev ops, mlx5 core objects, work queues, page pools, DIM, switchdev, and Hyper-V VHCA stats.

## Risks and Edge Cases

- Many enum comments require keeping reporter string arrays in other files synchronized.
- Several size constants are tied to hardware field widths and static array sizing; changing them can silently break WQE layout assumptions.
- `mlx5e_get_max_num_channels()` restricts kdump kernels to one channel; tests must account for crash-kernel behavior.
- `mlx5e_get_max_sq_aligned_wqebbs()` prevents DS field overflow by reducing the maximum; changes to WQE sizing must preserve this.
- Large shared structures are sensitive to cacheline layout and lock ownership. Adding fields in datapath areas can affect performance.
- Many prototypes assume callers hold `state_lock`, RTNL, netdev lock, or channel inactive state; misuse can race with queue teardown/reopen.

## Test Signals

Full mlx5e build matrix with XDP, AF_XDP, DCB, PTP, TLS, IPsec, PSP, MACsec, ARFS/RXNFC, QoS, and Hyper-V options. Runtime coverage for netdev open/close, channel count changes, MTU changes, coalesce changes, XDP attach/detach, XSK bind/unbind, health recovery, and safe channel reopen. Static checks for enum/string synchronization and WQE size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/channels.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/channels.c

## Purpose

`en/channels.c` provides small accessors and DIM toggles for `struct mlx5e_channels`. It exposes channel counts, RQN lookup for regular/XSK/PTP receive queues, XSK state checks, and RX/TX dynamic interrupt moderation enable/toggle operations.

## Important APIs, Types, and Functions

- `mlx5e_channels_get_num()` returns `chs->num`.
- `mlx5e_channels_is_xsk()` tests `MLX5E_CHANNEL_STATE_XSK`.
- `mlx5e_channels_get_regular_rqn()` returns a channel regular RQ number and optional VHCA ID.
- `mlx5e_channels_get_xsk_rqn()` returns XSK RQ number and optional VHCA ID, warning if the channel is not XSK-enabled.
- `mlx5e_channels_get_ptp_rqn()` returns PTP RQ number when the PTP RX channel exists and is active.
- `mlx5e_channels_rx_change_dim()` / `tx_change_dim()` enable or disable DIM across channels and TCs.
- `mlx5e_channels_rx_toggle_dim()` / `tx_toggle_dim()` reset DIM state for channels/SQs that currently have DIM enabled.

## Control Flow

Accessors fetch channel pointers through a local bounds-warning helper. DIM change operations iterate channels and, for TX, each DCB traffic class from `mlx5e_get_dcb_num_tc()`. Toggle operations disable and re-enable only existing DIM contexts to reset statistics without disturbing per-channel enablement.

## State and Persistence Behavior

RQN accessors read channel fields. DIM operations mutate per-RQ/per-SQ `dim` state via `mlx5e_dim_rx_change()` and `mlx5e_dim_tx_change()`. No allocation is performed here.

## Dependencies and Integration Points

Depends on `channels.h`, `en.h`, `en/dim.h`, and PTP state definitions. It is used by flow steering/RX resource code that needs RQ numbers and by ethtool/coalesce paths managing DIM.

## Risks and Edge Cases

- Index bounds only emit `WARN_ON_ONCE`; the function still indexes the array, so callers must validate indexes.
- TX DIM loops depend on current params DCB TC count; changing TC layout while channels are active requires proper locking.
- Toggle paths ignore errors from disable calls and return errors only from re-enable calls.

## Test Signals

Exercise RQN lookup for regular, XSK, and PTP receive paths. Change global and per-queue coalesce/DIM settings under one and multiple traffic classes. Test invalid channel indexes under debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/channels.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/channels.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/channels.h

## Purpose

`en/channels.h` declares the public channel accessor and DIM management helpers implemented in `channels.c`.

## Important APIs, Types, and Functions

The header declares channel count, XSK state, regular/XSK/PTP RQN lookup, RX/TX DIM enable/disable, and RX/TX DIM toggle helpers for `struct mlx5e_channels`.

## Control Flow

Consumers use these helpers instead of directly walking `struct mlx5e_channels` when integrating with flow steering, RX resources, PTP, and ethtool coalescing.

## State and Persistence Behavior

The declarations represent read access to channel IDs and mutation of per-queue DIM state through the implementation.

## Dependencies and Integration Points

Depends on Linux kernel types and a forward declaration of `struct mlx5e_channels`. It avoids pulling all of `en.h` into simple users.

## Risks and Edge Cases

Callers must ensure channels are allocated and indexes are valid; implementation warnings are not a safety boundary.

## Test Signals

Compile users and run channel/DIM tests described for `channels.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/channels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dcbnl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dcbnl.h

## Purpose

`en/dcbnl.h` defines mlx5e DCB/DCBX state and lifecycle hooks, with no-op stubs when DCB support is disabled.

## Important APIs, Types, and Functions

- `MLX5E_MAX_PRIORITY` and `MLX5E_MAX_DSCP` define priority/DSCP sizing.
- `struct mlx5e_cee_config` stores pending CEE priority group bandwidth, priority-to-PG mapping, PFC settings, and PFC enablement.
- `struct mlx5e_dcbx` stores DCBX mode, CEE config, DSCP app count, TSA state, capability, buffer configuration, and rate upper limits.
- `struct mlx5e_dcbx_dp` stores datapath DSCP-to-priority mapping and trust state.
- DCB hooks: `mlx5e_dcbnl_build_netdev()`, `mlx5e_dcbnl_initialize()`, `mlx5e_dcbnl_init_app()`, `mlx5e_dcbnl_delete_app()`.

## Control Flow

When `CONFIG_MLX5_CORE_EN_DCB` is enabled, netdev setup and private initialization call these hooks to register DCBNL ops and initialize app/firmware state. Otherwise calls compile to no-ops.

## State and Persistence Behavior

The structures are embedded in `struct mlx5e_priv` when DCB is enabled and persist with the netdev. Datapath state maps DSCP to priorities and trust mode.

## Dependencies and Integration Points

Depends on DCB/DCBX kernel types via users of the enabled configuration and integrates with `en.h`, netdev DCBNL operations, PFC, CEE/IEEE app configuration, and port buffer code.

## Risks and Edge Cases

- Disabled builds silently omit DCB behavior through stubs.
- Comments note `tc_tsa` is not readable from firmware, so driver state is authoritative for that field.
- DSCP array sizing must match valid DSCP values.

## Test Signals

Compile with and without DCB support. Use `dcb`/`lldptool` operations for PFC, ETS, DSCP trust, and app add/delete. Verify netdev ops are absent/no-op in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dcbnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.c

## Purpose

`en/devlink.c` creates the nested devlink instance and devlink port used by mlx5e netdev instances.

## Important APIs, Types, and Functions

- `mlx5e_create_devlink()` allocates a nested devlink in the same net namespace as the parent core devlink, sets the parent/child relationship, registers it, and returns `struct mlx5e_dev`.
- `mlx5e_destroy_devlink()` unregisters and frees the nested devlink.
- `mlx5e_devlink_port_register()` sets physical or virtual port attributes and registers `mlx5e_dev->dl_port`.
- `mlx5e_devlink_port_unregister()` unregisters the port.
- `mlx5e_devlink_get_port_parent_id()` reads the NIC software system image GUID for switch ID.

## Control Flow

Netdev creation allocates a nested devlink with empty mlx5e-specific ops, links it under the core devlink with `devl_nested_devlink_set()`, and registers it. Port registration selects physical flavor for PFs and virtual flavor otherwise. PFs use device index as physical port number and, when eswitch manager, set switch ID from the system image GUID. Devlink port index is derived from eswitch vport index.

## State and Persistence Behavior

Persistent state includes the nested devlink object, `struct mlx5e_dev` private storage, and registered `devlink_port`. The `mlx5e_dev` stores the netdev pointer and devlink port.

## Dependencies and Integration Points

Depends on devlink nested APIs, mlx5 eswitch vport-to-port-index mapping, core devlink, system image GUID query, and `en/devlink.h`. It ties mlx5e netdevs to devlink port representation.

## Risks and Edge Cases

- `mlx5e_create_devlink()` returns `devlink_priv(devlink)` without initializing `mlx5e_dev->netdev`; callers must fill fields as needed.
- Parent nested-devlink setup failure must free the allocated devlink, which this code does.
- Port indexes depend on eswitch mapping helpers and must remain stable for userspace.

## Test Signals

Create PF and VF/SF mlx5e netdevs and inspect `devlink port show`. Verify nested devlink hierarchy, physical vs virtual flavor, switch ID in eswitch manager mode, and cleanup on netdev destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.h

## Purpose

`en/devlink.h` declares mlx5e nested devlink and devlink-port lifecycle helpers.

## Important APIs, Types, and Functions

- `mlx5e_create_devlink()` / `mlx5e_destroy_devlink()` manage nested devlink allocation/registration.
- `mlx5e_devlink_port_register()` / `mlx5e_devlink_port_unregister()` manage the netdev's devlink port.

## Control Flow

Ethernet netdev setup uses these declarations to create devlink representation before registering the port and netdev, then tears them down in reverse.

## State and Persistence Behavior

The implementation persists nested devlink and `devlink_port` state for the netdev lifetime.

## Dependencies and Integration Points

Depends on `<net/devlink.h>` and `en.h` for `struct mlx5e_dev`. Integrates mlx5e with core devlink hierarchy.

## Risks and Edge Cases

Callers must unregister the port before destroying the nested devlink and must keep `struct mlx5e_dev` lifetime tied to the devlink private storage.

## Test Signals

Compile netdev creation/destruction paths and verify devlink port registration/unregistration under PF and non-PF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dim.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dim.h

## Purpose

`en/dim.h` declares mlx5e Dynamic Interrupt Moderation helpers and conversion utilities between Linux DIM CQ-period modes and mlx5 hardware CQ-period modes.

## Important APIs, Types, and Functions

- `mlx5e_dim_cq_period_mode()` converts a boolean start-from-CQE setting to DIM constants.
- `mlx5e_cq_period_mode()` maps `enum dim_cq_period_mode` to `enum mlx5_cq_period_mode`, warning on invalid input and defaulting to EQE.
- Prototypes cover RX/TX DIM work handlers and enabling/disabling DIM on RQs/SQs.

## Control Flow

Coalesce/ethtool and channel code use these helpers to translate user/kernel moderation semantics to hardware CQ modification calls and to schedule DIM work.

## State and Persistence Behavior

The header has no storage. Implementations mutate per-RQ/per-SQ DIM pointers and CQ moderation state.

## Dependencies and Integration Points

Depends on Linux DIM, mlx5 IFC definitions, and forward declarations of RQ/SQ/work structures. Integrated with `channels.c`, ethtool coalesce, and CQ moderation code.

## Risks and Edge Cases

Invalid DIM CQ-period mode triggers `WARN_ON_ONCE` and falls back to EQE mode. Callers should validate external inputs earlier.

## Test Signals

Change coalesce period mode and DIM enablement via ethtool and verify hardware CQ period mode transitions. Compile with DIM-related code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs.h

## Purpose

`en/fs.h` is the mlx5e Ethernet flow-steering interface. It defines flow table wrappers, L2/promisc/VLAN/TTC level constants, hash constants, steering object forward declarations, feature-specific stubs, and public APIs for creating, destroying, and accessing mlx5e flow-steering state.

## Important APIs, Types, and Functions

- `struct mlx5e_flow_table`, `mlx5e_l2_rule`, `mlx5e_promisc_table`, and `mlx5e_l2_table` model mlx5e flow table/group/rule state.
- Flow table level enums define TC, promisc, NIC, VLAN, L2, TTC, inner TTC, UDP/ANY redirect, TLS, ARFS, IPsec/PSP levels.
- ARFS APIs compile to real declarations or `-EOPNOTSUPP`/no-op stubs.
- Core APIs create/destroy TTC and flow steering, initialize/cleanup `mlx5e_flow_steering`, get/set submodules (VLAN, TC, TTC, ARFS, PTP, ANY, UDP, TLS), manage namespaces, set state flags, update RX mode, add/remove VLAN/MAC traps, and handle VLAN RX add/kill.
- Logging macros `fs_err/dbg/warn/warn_once` route through the owning mdev.

## Control Flow

mlx5e profile/netdev setup initializes flow steering, creates base flow tables, attaches TTC tables to RX resources, then optional features add tables at predefined levels. Runtime calls update L2 address lists, VLAN rules, traps, ARFS, ethtool steering, PTP FS, and redirect tables. Submodule setters/getters hide the private `mlx5e_flow_steering` layout.

## State and Persistence Behavior

Flow steering state persists in `struct mlx5e_flow_steering` and submodule pointers. Flow tables own firmware `mlx5_flow_table` objects, flow groups, rules, active VLAN bitmaps, L2 address hash lists, and feature-specific tables. State is hardware-resident and must be destroyed in reverse dependency order.

## Dependencies and Integration Points

Depends on mlx5 flow steering core, TTC library, mod header, RX resources, netdev, ethtool RXNFC, ARFS, TLS/IPsec/PSP optional features, traps, VLAN, and debugfs roots. It is the common interface for receive steering and many accelerators.

## Risks and Edge Cases

- Flow table level constants overlap intentionally for mutually exclusive optional features; additions must avoid unintended priority conflicts.
- ARFS stubs return `-EOPNOTSUPP` for enable/disable when disabled; callers must handle this.
- Submodule pointers are opaque; lifecycle mismatches can leave TTC destinations pointing at destroyed tables.
- Trap APIs rely on devlink trap IDs and TIR numbers being valid.

## Test Signals

Exercise netdev open/close flow steering creation/destruction, VLAN add/kill, promisc/allmulti, L2 address changes, TTC routing, ARFS/RXNFC enabled/disabled builds, PTP RX FS, traps, and accelerator tables. Use flow steering tracepoints to validate object order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_ethtool.h

## Purpose

`en/fs_ethtool.h` declares ethtool RX flow classification/steering helpers for mlx5e, with stubs when RXNFC support is disabled.

## Important APIs, Types, and Functions

With `CONFIG_MLX5_EN_RXNFC`, it declares allocation/free, steering init/cleanup, RXFH field get/set, and RXNFC get/set helpers. Without the option, allocation returns success, cleanup/init are no-ops, and operational get/set functions return `-EOPNOTSUPP`.

## Control Flow

Flow steering setup uses alloc/init hooks, ethtool ops call get/set helpers, and teardown calls cleanup/free. Stubs allow common code to compile without feature conditionals.

## State and Persistence Behavior

The hidden `struct mlx5e_ethtool_steering` stores ethtool steering state when enabled. Disabled builds do not allocate or persist state.

## Dependencies and Integration Points

Integrates with mlx5e flow steering, ethtool RXNFC/RXFH APIs, and `struct mlx5e_priv`.

## Risks and Edge Cases

- Disabled builds make allocation appear successful but later operations unsupported; callers must not treat allocation success as feature availability.
- RXFH field changes must align with hardware/TTC hash capabilities in the implementation.

## Test Signals

Compile with and without RXNFC. Run `ethtool -n/-N` and RXFH field operations, including unsupported configuration paths in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.c

## Purpose

`en/fs_tt_redirect.c` implements auxiliary flow-steering tables that redirect selected traffic types from the main TTC table into feature-specific flow tables. It supports UDP IPv4/IPv6 destination-port rules and an ANY ethertype table, with default rules that fall back to the original TTC destinations.

## Important APIs, Types, and Functions

- `struct mlx5e_fs_udp` owns IPv4/IPv6 UDP flow tables, default rules, and a refcount.
- `struct mlx5e_fs_any` owns the ANY flow table, default rule, and a refcount.
- `mlx5e_fs_tt_redirect_udp_create/destroy()` create/destroy UDP redirect tables and point TTC UDP traffic types at them.
- `mlx5e_fs_tt_redirect_udp_add_rule()` adds a UDP dport rule forwarding to a TIR.
- `mlx5e_fs_tt_redirect_any_create/destroy()` create/destroy the ANY redirect table and point TTC ANY traffic at it.
- `mlx5e_fs_tt_redirect_any_add_rule()` adds an ethertype rule forwarding to a TIR.
- `mlx5e_fs_tt_redirect_del_rule()` deletes a rule handle.

## Control Flow

UDP create allocates state, stores it in `mlx5e_flow_steering`, creates one table for IPv4 UDP and one for IPv6 UDP, creates two groups per table (specific-match and default), adds default rules to the original TTC destinations, then changes TTC destinations to the new tables. Destroy decrements the refcount, restores TTC default destinations, deletes default rules and tables, frees state, and clears the FS pointer.

ANY create follows the same pattern for a single table matching ethertype. Add-rule paths allocate a flow spec, set outer-header match criteria, point the destination to a provided TIR, add the rule to the relevant table, free the spec, and return the rule handle.

## State and Persistence Behavior

Persistent state includes firmware flow tables, flow groups, default flow rules, TTC rule destinations, refcounts, and submodule pointers stored in `mlx5e_flow_steering`. Caller-added rule handles persist until explicitly deleted.

## Dependencies and Integration Points

Depends on `en/fs_tt_redirect.h`, `en/fs.h`, `fs_core.h`, TTC helpers, flow table creation/destruction, mlx5 flow spec macros, and RX TIR numbers. It is used by features that need to steer specific UDP ports or ethertypes away from default TTC handling.

## Risks and Edge Cases

- `fs_any_create_groups()` allocates `MLX5E_FS_UDP_NUM_GROUPS`; this currently equals the ANY group count but is semantically coupled to the UDP constant.
- `fs_any_create_table()` uses `MLX5E_FS_UDP_TABLE_SIZE`; it currently matches the ANY table size formula but is another semantic coupling.
- Destroy paths call `fs_udp_disable()` / `fs_any_disable()` and ignore errors, so TTC restoration failures only log inside helpers if returned there.
- Refcounts are plain ints with no local locking; callers must serialize create/destroy.
- Add-rule functions assume the redirect state exists and table pointers are valid.

## Test Signals

Create UDP and ANY redirect tables, add rules for IPv4/IPv6 UDP ports and ethertypes, verify packets hit selected TIRs, then destroy and confirm TTC defaults are restored. Test multiple create/destroy users via refcount. Fault-inject flow table/group/rule creation failures and validate unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.h

## Purpose

`en/fs_tt_redirect.h` declares traffic-type redirect APIs for UDP and ANY flow-steering tables.

## Important APIs, Types, and Functions

- `mlx5e_fs_tt_redirect_del_rule()` deletes a returned flow rule.
- UDP APIs create/destroy redirect tables and add dport-to-TIR rules for a TTC UDP traffic type.
- ANY APIs create/destroy the redirect table and add ethertype-to-TIR rules.

## Control Flow

Feature modules call create before adding rules, keep rule handles, delete rules when no longer needed, and call destroy when the redirect table is no longer used.

## State and Persistence Behavior

Implementations persist redirect table state in `struct mlx5e_flow_steering` and firmware flow tables/rules. The header exposes only opaque flow handles.

## Dependencies and Integration Points

Depends on `en/fs.h`, mlx5 traffic type enums, flow handles, and TIR numbers. Integrated with feature steering modules needing traffic-type fanout.

## Risks and Edge Cases

Callers must serialize lifecycle, handle `ERR_PTR` from add-rule/create operations, and not delete rules after destroying the owning table.

## Test Signals

Compile users and exercise UDP/ANY redirect lifecycle with packet steering validation and error-unwind tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.c

## Purpose

`en/health.c` provides common mlx5e health reporter helpers for devlink fmsg formatting, CQ/EQ diagnostics, reporter creation/destruction, channel health updates, SQ recovery, channel recovery, EQ recovery, generic report dispatch, resource dump streaming, and queue dump formatting.

## Important APIs, Types, and Functions

- `mlx5e_health_fmsg_named_obj_nest_start/end()` wrap named devlink fmsg object nesting.
- `mlx5e_health_cq_diag_fmsg()` queries a CQ and emits CQN, hardware status, CI, and size.
- `mlx5e_health_cq_common_diag_fmsg()` emits CQ stride and size without querying hardware status.
- `mlx5e_health_eq_diag_fmsg()` emits EQ number, IRQ, vector index, consumer index, and size.
- `mlx5e_health_create_reporters()` / `destroy_reporters()` create/destroy TX and RX reporters.
- `mlx5e_health_channels_update()` marks reporters healthy after channel updates.
- `mlx5e_health_sq_to_ready()` moves an SQ from ERR to RST to RDY.
- `mlx5e_health_recover_channels()` reopens channels under RTNL, netdev lock, and `state_lock`.
- `mlx5e_health_channel_eq_recover()` polls an IRQ-disabled EQ and updates stats.
- `mlx5e_health_report()` either calls direct recovery or `devlink_health_report()`.
- `mlx5e_health_rsc_fmsg_dump()` streams resource dump pages into a devlink binary fmsg.
- `mlx5e_health_queue_dump()` dumps a full QPC for a queue index.

## Control Flow

Reporter-specific code calls the common fmsg helpers to build structured diagnoses and dumps. Recovery may transition a failed SQ through reset states, reopen all channels when the interface is open, or poll a stuck EQ while interrupts are disabled. Resource dumps create a command, loop through `mlx5_rsc_dump_next()`, chunk page data into devlink binary records, and clean up command/page state.

## State and Persistence Behavior

Persistent mutations include reporter pointers/states, SQ firmware state transitions, channel reopen side effects, `stats->eq_rearm`, and devlink health reporter state. Resource dump output is transient fmsg data; resource dump state lives in `mdev->rsc_dump`.

## Dependencies and Integration Points

Depends on `health.h`, EQ helpers, resource dump API, mlx5 CQ/SQ modification/query APIs, devlink health, RTNL/netdev locking, and TX/RX reporter implementations. It is the shared utility layer for mlx5e health reporters.

## Risks and Edge Cases

- `mlx5e_health_cq_diag_fmsg()` ignores `mlx5_core_query_cq()` errors and may report default status.
- `mlx5e_health_rsc_fmsg_dump()` starts the devlink binary nest before command creation; error paths still close the nest except for unsupported return before allocation.
- Recovery paths require correct lock ordering: RTNL, netdev lock, then `state_lock`.
- Direct recovery is used when no reporter exists, so reporter absence changes observability but not recovery attempt.

## Test Signals

Trigger TX/RX CQ errors, SQ errors, RX timeouts, and EQ recovery. Run devlink health diagnose/dump and verify CQ/EQ/resource dump fields. Fault-inject resource dump command creation and continuation failures. Validate lockdep under channel recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.h

## Purpose

`en/health.h` declares common mlx5e health reporter types, CQ/EQ diagnostic helpers, TX/RX reporter entry points, channel recovery helpers, resource dump helpers, and CQE syndrome recovery policy.

## Important APIs, Types, and Functions

- `cqe_syndrome_needs_recover()` returns true for local QP operation error, local protection error, and work request flush error syndromes.
- TX reporter declarations cover create/destroy, TX error CQE, TX timeout, and PTP SQ unhealthy reporting.
- RX reporter declarations cover create/destroy, ICOSQ/RQ CQE errors, RX timeout, and ICOSQ recovery suspend/resume.
- `struct mlx5e_err_ctx` packages recover and dump callbacks plus context for devlink health reports.
- Common helpers cover SQ-to-ready, EQ recovery, channel recovery, health report dispatch, reporter lifecycle, channel state update, resource dump fmsg streaming, and queue dump.

## Control Flow

Reporter implementations include this header to construct `mlx5e_err_ctx`, decide whether CQE syndromes are recoverable, call common diagnostic fmsg helpers, and invoke shared recovery/report routines.

## State and Persistence Behavior

Implementations mutate reporter state, queue state, channel state, and resource dump outputs. The header itself stores no state.

## Dependencies and Integration Points

Depends on `en.h` and `diag/rsc_dump.h`. It ties mlx5e TX/RX reporters, devlink health, resource dump support, and channel recovery together.

## Risks and Edge Cases

- `cqe_syndrome_needs_recover()` is a policy boundary; adding/removing syndromes changes automatic recovery behavior.
- `mlx5e_err_ctx` callbacks must remain valid until devlink health report handling completes.
- Reporter create/destroy order should match implementation dependencies: create TX then RX, destroy RX then TX.

## Test Signals

Compile TX/RX reporter implementations. Exercise recoverable and non-recoverable CQE syndromes, devlink health report/dump callbacks, queue dumps, and reporter lifecycle during netdev open/close and driver reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/health.h -->
