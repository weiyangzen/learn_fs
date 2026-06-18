# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core.c

## Purpose
`core.c` is the central runtime for the Mellanox switch (`mlxsw`) driver stack. It binds a bus implementation to a protocol-specific `mlxsw_driver`, owns the `struct mlxsw_core` object stored in devlink private memory, exposes register-access helpers, dispatches RX traps and register events, initializes ports/resources/line cards/environment/hwmon/thermal/health, and provides devlink operations for reload, flash, shared-buffer inspection, trap control, and port split/unsplit.

## Important APIs, Types, And Functions
- `struct mlxsw_core` is the process-local device state. It persists the selected driver, bus callbacks, bus private pointer, bus info, EMAD workqueue and transaction list, listener lists, IRQ-event callback list, LAG mapping table, parsed resources, hwmon/thermal/env/linecard handles, devlink ports, maximum port count, active port counter, and firmware-flash state.
- Driver registration uses global `mlxsw_core_driver_list` protected by `mlxsw_core_driver_list_lock`; `mlxsw_core_driver_register()` and `mlxsw_core_driver_unregister()` publish protocol drivers by `kind`.
- Bus lifecycle entry points are `mlxsw_core_bus_device_register()` and `mlxsw_core_bus_device_unregister()`. They allocate/register devlink on first load, attach the bus and driver, call `bus->init()`, initialize resources and subsystems, invoke `driver->init()`, and unwind in reverse order on errors.
- Register access APIs are `mlxsw_reg_query()`, `mlxsw_reg_write()`, `mlxsw_reg_trans_query()`, `mlxsw_reg_trans_write()`, and `mlxsw_reg_trans_bulk_wait()`. Early initialization uses command-interface register access; after EMAD setup the same public API routes through EMAD packets and waits on transaction completions.
- EMAD helpers pack and parse operation/string/latency/register/end TLVs, allocate SKBs, track transaction IDs, transmit retries, process response status, copy successful register payloads into caller buffers, and report hardware errors via devlink tracepoints.
- Trap/listener APIs include `mlxsw_core_rx_listener_register()`, `mlxsw_core_event_listener_register()`, `mlxsw_core_trap_register()`, `mlxsw_core_trap_state_set()`, and bulk trap register/unregister helpers. `mlxsw_core_skb_receive()` matches incoming trapped packets to RCU-protected listeners by trap ID, local port, and mirror reason.
- Port APIs include `mlxsw_core_port_init()`, `mlxsw_core_port_fini()`, `mlxsw_core_cpu_port_init()`, `mlxsw_core_port_netdev_link()`, `mlxsw_core_port_devlink_port_get()`, `mlxsw_core_port_linecard_get()`, and `mlxsw_core_ports_remove_selected()`.
- Firmware/devlink APIs include `mlxsw_core_fw_flash()`, devlink `flash_update`, FW load policy parameter registration, firmware revision validation/auto-flash, and `mlxfw_dev_ops` wrappers over MCQI/MCC/MCDA registers.
- Health handling registers an MFDE event listener and a devlink health reporter named `fw_fatal`; asynchronous work snapshots MFDE payloads and the dump formatter expands fatal cause, assert, KVD insertion-machine stop, and CR-space timeout fields.

## Control Flow
Device registration resolves `bus_info->device_kind` to a registered `mlxsw_driver`. On non-reload it allocates a devlink object sized for `struct mlxsw_core` plus driver private data, locks/registers devlink, and initializes core listener lists and locks. The main initialization sequence is: `bus->init()` with the driver config profile, optional driver resource registration, port-array allocation/resource registration, optional LAG mapping allocation, core trap-group setup, EMAD initialization, devlink params, firmware compatibility validation and possible flash/reset retry, linecards, health, hwmon, thermal, environment, and finally protocol driver `init()`. Each failure label unwinds the subsystems already initialized.

EMAD register access is an asynchronous packet transaction wrapped by a synchronous public call. `mlxsw_core_reg_access()` chooses command interface until `emad.use_emad` is set. EMAD access creates a `mlxsw_reg_trans`, assigns an atomic transaction ID, constructs an SKB with operation/register/string/latency/end TLVs, inserts the transaction into an RCU list under `trans_list_lock`, transmits a clone, and schedules an exponential timeout. Responses arrive through the ETHEMAD trap listener, are parsed, matched by transaction ID, and either complete with copied payload, retry on busy/ack, or capture an error string and fail. `mlxsw_reg_trans_bulk_wait()` waits each listed transaction, cancels its timeout, logs retries/errors, removes it from the bulk list, and frees it through RCU.

Packet receive dispatch converts LAG metadata to a local port via the LAG mapping table when needed, validates trap and port ranges, then scans the RCU listener list. Only enabled matching listeners receive ownership of the SKB; otherwise the packet is freed.

Devlink callbacks mostly delegate to optional driver methods. Shared-buffer, trap, policer, split/unsplit, and flash operations return `-EOPNOTSUPP` when the protocol driver lacks the hook. Reload down unregisters the bus device on buses advertising `MLXSW_BUS_F_RESET`; reload up reruns device registration with the existing devlink and reports both driver reinit and FW activate actions.

## State And Persistence Behavior
All state is kernel in-memory state scoped to the loaded device/module. Persistent device state is programmed through hardware registers and KVD/devlink resources, not stored on disk. `struct mlxsw_core` owns subsystem pointers and is freed with devlink on non-reload unregister. Port state lives in a zeroed array indexed by local port; active port occupancy is exposed to devlink resources through `active_ports_count`. LAG membership mapping is a flat `u16` array indexed by `MAX_LAG_MEMBERS * lag_id + port_index`.

Concurrency is mixed: global driver list uses a spinlock; EMAD transaction insertion/removal uses `spin_lock_bh()` plus RCU list traversal; RX listener lists are deleted with `synchronize_rcu()`; IRQ event handlers use a mutex; health/environment events run on the ordered workqueue; EMAD timeouts run on a per-device EMAD workqueue. Module-level workqueues `mlxsw_wq` and `mlxsw_owq` are created at module init and destroyed at exit.

## Dependencies And Integration Points
The file is tightly integrated with Linux devlink, firmware loader, workqueues, RCU, SKBs, completions, and tracepoints. It depends on mlxsw register pack/unpack definitions (`reg.h`), command mailbox helpers (`cmd.h`), EMAD constants (`emad.h`), traps (`trap.h`), resources (`resources.h`), linecard helpers declared in `core.h`, and MLX firmware flashing (`../mlxfw/mlxfw.h`). The bus abstraction supplies command execution, SKB transmit, hardware clocks, lag/flood modes, and feature flags. The protocol driver supplies port, shared-buffer, trap, resource, KVD-size, and PTP callbacks.

## Risks And Edge Cases
- EMAD correctness depends on reliable transaction ID matching, timeout cancellation, and active counter races between response and timeout paths. Missed cleanup can leak transactions or complete twice.
- `mlxsw_core_skb_receive()` holds an RCU read lock while invoking listener callbacks; callbacks must respect that context and must not sleep unexpectedly.
- Firmware validation can flash firmware during registration and returns `-EAGAIN` to trigger one retry. Bad reset behavior or mismatched FW policy can make registration fail in partially initialized states.
- LAG mapping allocation depends on `MAX_LAG_MEMBERS`; mapping helpers assume the array exists and indices are valid.
- Many devlink operations delegate to optional driver hooks. Missing hooks intentionally surface `-EOPNOTSUPP`, so callers must handle feature variance by device.
- `mlxsw_core_bus_device_unregister()` has special `devlink_is_reload_failed()` handling. Incorrect reload state can skip deinitialization or unregister only a subset.

## Test Signals
Useful signals are devlink registration and reload tests, firmware load-policy and flash-update paths, EMAD success/busy/error/retry traces, `trace_devlink_hwmsg`/`trace_devlink_hwerr`, trap enable/disable register writes, listener duplicate/unregister behavior, packet drop when no listener matches, shared-buffer callbacks, port split/unsplit devlink operations, health reporter test dumps, and module unload with empty listener/IRQ lists.
