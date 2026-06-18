# Research: subset-b-004554

Grouped research for Mellanox `mlxsw` core, ACL flex actions/keys, and environment-module support.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core.h

## Purpose
`core.h` is the public internal contract for the `mlxsw` core module. It declares the central opaque types, bus and driver callback tables, devlink/trap/listener interfaces, register access APIs, port lifecycle helpers, resource helpers, work scheduling helpers, linecard structures, and optional hwmon/thermal hooks consumed across the Mellanox switch driver family.

## Important APIs, Types, And Functions
- Opaque handles include `struct mlxsw_core`, `struct mlxsw_core_port`, `struct mlxsw_driver`, `struct mlxsw_bus`, `struct mlxsw_bus_info`, and `struct mlxsw_fw_rev`.
- `struct mlxsw_driver` describes a device-kind driver: identity, private size, firmware requirements, init/fini callbacks, port split/unsplit, shared-buffer callbacks, devlink trap/policer callbacks, resource/KVD callbacks, PTP transmitted callback, config profile, and SDQ CQE-v2 support flag.
- `struct mlxsw_bus` abstracts the transport. It supplies `init`, `fini`, optional TX/RX, command execution, hardware clock reads, lag/flood mode reads, and feature flags `MLXSW_BUS_F_TXRX` and `MLXSW_BUS_F_RESET`.
- `struct mlxsw_config_profile` is a large driver-to-bus/hardware configuration request with `used_*` flags controlling LAG, flood tables, KVD sizing, CQE timestamp type, and SWID configuration.
- Listener declarations (`struct mlxsw_rx_listener`, `struct mlxsw_event_listener`, `struct mlxsw_listener`) and macros (`MLXSW_RXL`, `MLXSW_RXL_DIS`, `MLXSW_RXL_MIRROR`, `MLXSW_EVENTL`, `MLXSW_CORE_EVENTL`) standardize trap IDs, enabled/disabled actions, trap groups, control-buffer routing, and event-vs-packet dispatch.
- Register APIs provide synchronous query/write and asynchronous/bulk EMAD transaction helpers using `mlxsw_reg_trans_cb_t`.
- Port and devlink helpers expose physical/CPU port registration, netdev linking, devlink port lookup, linecard lookup, and selected-port removal.
- `struct mlxsw_rx_md_info`, `struct mlxsw_tx_info`, `struct mlxsw_txhdr_info`, and `struct mlxsw_skb_cb` define metadata carried in `skb->cb`; the inline `mlxsw_skb_cb()` asserts it fits.
- Linecard declarations define linecard status events, device info, `struct mlxsw_linecard`, `struct mlxsw_linecards`, event operations, devlink info/flash hooks, block-device hooks, and linecard driver registration.

## Control Flow
The header establishes a layering model. Bus implementations register devices through `mlxsw_core_bus_device_register()`, protocol drivers register themselves through `mlxsw_core_driver_register()`, and protocol code uses the exported core helpers to program registers, register traps, create devlink ports, query resources, and schedule work. Packet/event delivery enters through the trap listener API, while administrative operations enter through devlink callbacks routed to `struct mlxsw_driver`.

## State And Persistence Behavior
This header mostly declares state layout rather than implementing it. The notable persistence contracts are in-memory ownership: driver private memory is trailing storage behind `struct mlxsw_core`, SKB metadata reuses `skb->cb`, bus info carries immutable device facts such as PSID/VSD/FW revision, and linecard objects are owned by `struct mlxsw_linecards` with per-linecard mutexes and delayed work.

## Dependencies And Integration Points
The header includes Linux device, module, SKB, workqueue, net namespace, auxiliary bus, and devlink headers, plus local `trap.h`, `reg.h`, `cmd.h`, `resources.h`, and `mlxfw.h`. It is the common integration point used by bus drivers, Spectrum protocol drivers, linecard support, environment support, trap code, hwmon/thermal optional modules, and firmware flashing.

## Risks And Edge Cases
- `struct mlxsw_driver` has many optional callbacks. Callers must check for hook availability before use, as `core.c` does for devlink operations.
- `mlxsw_skb_cb()` relies on compile-time size compatibility with `skb->cb`; extending metadata can break this invariant.
- Config-profile `used_*` flags must match initialized values. Adding a field without a corresponding flag or bus handling can silently misconfigure hardware.
- Linecard indexing uses one-based slot indices in `mlxsw_linecard_get()` by subtracting one; callers must not pass zero.
- Trap macros bake in actions and trap groups. Incorrect macro selection can enable traps unexpectedly or route packets to the wrong group.

## Test Signals
Compile coverage is important because this file defines cross-module ABI-like structures. Runtime signals include successful driver/bus registration, devlink port operations, trap listener registration through macro-generated definitions, register transaction callbacks, resource query/get behavior, linecard event operations, and optional hwmon/thermal builds both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.c

## Purpose
`core_acl_flex_actions.c` builds and owns encoded ACL flexible action blocks for mlxsw devices. It turns high-level actions such as drop, trap, mirror, forward, VLAN rewrite, QoS rewrite, counters, policers, FID set, ignore, multicast router, NAT IP/L4 rewrites, and sampling into hardware action-set byte encodings. It also deduplicates action sets and hardware resources so multiple rules can share KVD linear entries, forwarding entries, cookies, and policers.

## Important APIs, Types, And Functions
- `struct mlxsw_afa` owns action-builder global state: maximum actions per set, hardware operations, operation private pointer, rhashtables for encoded sets/forwarding entries/cookies/policers, an IDR for cookie indexes, and a policer list.
- `struct mlxsw_afa_set` represents one encoded action set (`MLXSW_AFA_SET_LEN`) with hash key, KVDL index, first-set marker, trap/police flags, refcount, and pre-commit `prev`/`next` links.
- `struct mlxsw_afa_block` is a rule action chain. It owns the first/current set, current action index, finished flag, and a resource destructor list.
- `struct mlxsw_afa_ops` callbacks allocate/delete KVDL action sets and forwarding entries, read activity, allocate/free counters, create/delete mirrors, policers, and samplers.
- Creation/destruction APIs are `mlxsw_afa_create()`, `mlxsw_afa_destroy()`, `mlxsw_afa_block_create()`, `mlxsw_afa_block_destroy()`, and `mlxsw_afa_block_commit()`.
- Block terminal APIs are `mlxsw_afa_block_continue()`, `mlxsw_afa_block_jump()`, and `mlxsw_afa_block_terminate()`.
- Exported append APIs encode specific actions: `mlxsw_afa_block_append_vlan_modify()`, `drop()`, `trap()`, `trap_and_forward()`, `mirror()`, `fwd()`, QoS DSCP/ECN/switch-priority helpers, allocated/new counters, `police()`, `fid_set()`, `ignore()`, `mcrouter()`, `ip()`, `l4port()`, and `sampler()`.
- `mlxsw_afa_cookie_lookup()` maps a hardware user-defined cookie index back to a `flow_action_cookie` under RCU.

## Control Flow
An AFA instance is created with operation callbacks and initialized rhashtables. A caller creates an action block, appends actions, terminates or jumps/continues the binding, commits the block, and later destroys it. A block always starts with at least one pass-by-default set; if `dummy_first_set` is requested, the first set remains empty and the second set carries real actions.

Appending an action calls `mlxsw_afa_block_append_action_ext()`. It rejects already finished blocks, creates a new set if the action would exceed `max_acts_per_set`, and also splits when trap and police actions would otherwise share a set, working around a hardware limitation. It marks trap/police presence, advances the set action cursor, writes the action type, and returns the payload area for the action-specific packer.

Commit walks from the current set backward. For each set it looks for an identical encoded set in `set_ht`; if found it bumps the refcount and discards the duplicate, otherwise it calls `ops->kvdl_set_add()` and inserts the new set into the hash. Previous sets are patched with `NEXT` pointers to the committed KVDL index of their successor. The first set is returned directly to rules; subsequent sets live in KVD linear memory.

Actions requiring hardware resources allocate a resource object before appending and link it onto the block's resource list. On append failure the resource is immediately destroyed; on block destruction every registered destructor releases its resource. Forwarding entries are keyed by local port and backed by KVDL PBS entries. Cookies are keyed by raw `flow_action_cookie`, assigned 20-bit nonzero IDR indexes, and freed with RCU. Policers are keyed by flow-action index and kept in both a rhashtable and list. Mirrors and samplers call span/psample callbacks and store returned span IDs.

## State And Persistence Behavior
AFA state is in-memory plus hardware resources allocated through `mlxsw_afa_ops`. Encoded action sets and forwarding entries persist in hardware KVD linear space until their refcounts drop to zero. Cookie indexes persist in the instance IDR while any block references them. Counter, mirror, policer, and sampler resources persist until block destruction. `mlxsw_afa_destroy()` warns if policers or cookies remain, which catches leaked block/resource references.

## Dependencies And Integration Points
The file depends on Linux rhashtable, IDR, refcount, RCU, flow offload cookies, psample groups, and netlink extack. It uses local item-field helpers to define and pack hardware bitfields, and local trap IDs for ACL discard trap actions. Device-specific allocation and deletion are intentionally delegated through `struct mlxsw_afa_ops`, allowing Spectrum implementations to map these abstract actions to their KVDL/counter/mirror/policer/sampler facilities.

## Risks And Edge Cases
- Hash keys include the whole encoded set and `is_first`; uninitialized bytes would break deduplication, so sets are zero-allocated and packers must only write defined fields.
- `mlxsw_afa_block_first_kvdl_index()` warns if there is no second set; callers must only request activity for blocks with KVDL-backed continuation.
- Drop-with-cookie uses a 20-bit IDR range and reserves index zero; exhaustion returns an error and must propagate to flow offload.
- Police and trap splitting is required for hardware correctness. New trap-like or police-like actions must use the correct action type.
- Forward-to-ingress-port is explicitly unsupported and returns `-EOPNOTSUPP`.
- Resource destructors depend on block lifetime. Destroying an AFA instance before all blocks are destroyed leaves warnings and potential hardware resource leaks.
- Cookie lookup requires RCU read-side protection because cookies are freed with `kfree_rcu()`.

## Test Signals
Exercise block creation, append, commit, and destruction with single-set and multi-set action chains; duplicate blocks should share KVDL entries and refcounts. Validate trap+police splitting, dummy-first-set behavior, cookie allocation/lookup/free under RCU, policer reuse by `fa_index`, mirror/sampler cleanup on append errors, sampler rate limit rejection, counter allocation/free pairing, and extack strings on expected failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.h

## Purpose
`core_acl_flex_actions.h` declares the ACL flexible-action builder interface. It lets higher-level ACL code create an AFA context, build action blocks, commit and query them, look up drop cookies, and append supported hardware actions without knowing the byte layout implemented in `core_acl_flex_actions.c`.

## Important APIs, Types, And Functions
- Opaque `struct mlxsw_afa` and `struct mlxsw_afa_block` hide global action state and per-rule action-chain state.
- `struct mlxsw_afa_ops` is the hardware integration contract. It provides KVDL set add/delete/activity, forwarding-entry add/delete, counter allocation/free, mirror add/delete, policer add/delete, sampler add/delete, and `dummy_first_set`.
- Lifecycle APIs are `mlxsw_afa_create()`, `mlxsw_afa_destroy()`, `mlxsw_afa_block_create()`, `mlxsw_afa_block_destroy()`, and `mlxsw_afa_block_commit()`.
- Accessors expose encoded first/current sets, first KVDL index, and action-set activity.
- Control APIs end a block with continue, jump to ACL group, or terminate.
- Append APIs cover drop with optional `flow_action_cookie`, trap, trap-and-forward, mirror, forwarding, VLAN modification, QoS rewrites, counters, FID set, ignore, multicast router action, SIP/DIP rewrite, L4 port rewrite, policer, and sampler.

## Control Flow
Callers instantiate `mlxsw_afa` with device callbacks, create a block per ACL rule, append actions in order, set the terminal behavior, commit the block so sets are shared/KVDL-backed as needed, use `mlxsw_afa_block_first_set()` or KVDL index when programming the rule, and destroy the block when the rule is removed.

## State And Persistence Behavior
The header indicates ownership but not representation. Blocks own temporary and hardware-backed resources until destroyed. The AFA context owns deduplication tables and allocator state. Cookie lookup returns a pointer valid only under RCU read-side protection, as documented by the implementation.

## Dependencies And Integration Points
The header depends on Linux types, netdevice, and flow offload. It exposes netlink extack propagation so append failures can be reported to tc/flow-offload users. The ops table connects this generic builder to Spectrum KVDL, counters, span/mirror, policer, and psample implementations.

## Risks And Edge Cases
- Operation callbacks must be internally consistent; a successful add must be matched by the corresponding delete on resource release.
- Append functions may allocate resources before encoding. Callers must destroy blocks even after partial failures to release anything already attached.
- `dummy_first_set` changes the structure of committed blocks and is significant for users that query the first KVDL index or activity.
- `mlxsw_afa_block_append_police()` always writes through `p_policer_index`; callers must pass a valid pointer.

## Test Signals
Compile-time users should cover all append prototypes. Runtime tests should verify callback pairing, extack propagation, block commit before rule programming, activity retrieval, cookie lookup for trapped drops, and cleanup after failed append sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.c

## Purpose
`core_acl_flex_keys.c` implements ACL flexible-key selection and encoding. It maps requested match elements into a minimal ordered set of hardware key blocks, caches those key layouts, accepts key/mask values in an internal storage format, and encodes or clears the final hardware key and mask through device-specific block callbacks.

## Important APIs, Types, And Functions
- `mlxsw_afk_element_infos[]` defines internal scratchpad geometry for every `enum mlxsw_afk_element`: source system port, Ethernet addresses, ethertype, protocol, VLAN/PCP/TCP flags, L4 ports, TTL/ECN/DSCP, virtual router fields, IP address chunks, FDB miss, L4 range, and split virtual-router fields.
- `struct mlxsw_afk` owns cached key infos, maximum block count, ops, and available hardware blocks.
- `mlxsw_afk_create()` initializes the AFK context and validates that every hardware block instance has the same type and compatible size as its internal element definition.
- `struct mlxsw_afk_key_info` is a cached chosen layout: refcount, number of blocks, `element_to_block[]`, requested element usage, and an array of selected block definitions.
- The greedy picker functions count how many requested elements each block can cover, repeatedly choose the block with most remaining hits, then fill `key_info` with high-entropy blocks first followed by the rest.
- `mlxsw_afk_key_info_get()` caches/refcounts layouts by exact element-usage bitmap; `mlxsw_afk_key_info_put()` releases them.
- `mlxsw_afk_values_add_u32()` and `mlxsw_afk_values_add_buf()` populate internal key/mask scratch storage and mark elements used only when the mask is nonzero.
- `mlxsw_afk_encode()` emits block-by-block key and mask data by locating each element's selected block instance, copying from scratch storage, applying optional `u32_key_diff`, and calling `ops->encode_block()` for each block.
- `mlxsw_afk_clear()` calls `ops->clear_block()` over a requested block index range.

## Control Flow
A device driver creates an AFK context with its block table and encode/clear callbacks. Higher layers fill a `mlxsw_afk_element_usage` bitmap for a rule template and call `mlxsw_afk_key_info_get()`. If the same bitmap has been used, the cached layout is refcounted. Otherwise the picker allocates a new layout, computes block coverage, selects blocks until all requested elements are covered, enforces `max_blocks`, and links the layout into the cache.

For each rule instance, callers fill `mlxsw_afk_element_values`. Zero masks are ignored so irrelevant fields are not encoded. Encoding iterates selected blocks and currently used values, skips elements not assigned to the current block, writes a temporary 16-byte block key/mask, and delegates final placement into the output key/mask buffers to the device-specific `encode_block()` callback.

## State And Persistence Behavior
State is in-memory only. AFK caches key layouts in a list with refcounts; `mlxsw_afk_destroy()` warns if cached layouts remain. Element values are caller-owned transient storage. Encoded hardware keys are written into caller-provided buffers and are not persisted by this module.

## Dependencies And Integration Points
The implementation depends on Linux bitmaps, refcounts, and allocation helpers, plus local `item.h` field accessors. The hardware-specific integration is through `struct mlxsw_afk_ops`: the block catalog comes from the device family, and output encoding/clearing is delegated so this core code remains independent of the final register/key format.

## Risks And Edge Cases
- The greedy picker optimizes by current hit count, not by exhaustive search. It can fail with `-EINVAL` if coverage requires more than `max_blocks`.
- If a requested element appears in no block, `mlxsw_afk_picker_most_hits_get()` eventually returns a negative value. Callers must handle `ERR_PTR()`.
- Block validation uses `WARN_ON()` but does not reject creation, so a bad block table can still lead to bad encoding.
- `mlxsw_afk_encode()` assumes all elements in `values->elusage` are a subset of `key_info->elusage`; otherwise warning paths skip or return null element instances.
- Temporary block buffers are fixed at 16 bytes. Block definitions and encode callbacks must match that maximum.

## Test Signals
Useful tests build AFK contexts with overlapping block coverage and verify chosen block count/order, high-entropy block prioritization, cache refcount reuse, failure when elements are uncovered or `max_blocks` is too low, zero-mask omission, U32 diff application, buffer element copying, and clear callback ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.h

## Purpose
`core_acl_flex_keys.h` defines the abstract match-element vocabulary and public AFK API used to build hardware ACL key blocks. It describes what fields can be matched, how device-specific blocks declare element placement, how callers represent requested element usage and values, and how selected key layouts are encoded.

## Important APIs, Types, And Functions
- `enum mlxsw_afk_element` lists supported match elements: system port, MAC fields, ethertype, protocol, IPv4/IPv6 address chunks, L4 ports, VLAN ID/PCP, TCP flags, IP TTL/ECN/DSCP, virtual-router variants, FDB miss, and L4 port range.
- `enum mlxsw_afk_element_type` distinguishes U32 bitfield elements from byte-buffer elements.
- `struct mlxsw_afk_element_info` and `MLXSW_AFK_ELEMENT_INFO_*` macros describe internal scratchpad layout.
- `struct mlxsw_afk_element_inst` and `MLXSW_AFK_ELEMENT_INST_*` macros describe where an element appears in a concrete hardware block, including optional key-value adjustment and size-check override.
- `struct mlxsw_afk_block` describes one available hardware key block: encoding ID, element instances, instance count, and high-entropy priority.
- `struct mlxsw_afk_element_usage` wraps a bitmap with helpers to add, zero, fill, iterate, and test subset relationships.
- `struct mlxsw_afk_ops` supplies the block catalog plus `encode_block()` and `clear_block()` callbacks.
- Public APIs create/destroy AFK contexts, get/put selected key layouts, query selected block encodings/count, add U32 or buffer values, encode key/mask output, and clear block ranges.

## Control Flow
Callers first describe all fields needed by a rule template in `mlxsw_afk_element_usage`. `mlxsw_afk_key_info_get()` returns a selected layout. Rule instances then place actual key/mask values into `mlxsw_afk_element_values` and call `mlxsw_afk_encode()` with the layout to produce hardware key and mask buffers.

## State And Persistence Behavior
The header exposes two main state lifetimes: `struct mlxsw_afk` is a long-lived context with a block catalog and cached layouts, while `struct mlxsw_afk_element_values` is per-rule transient storage. `mlxsw_afk_key_info` is opaque and refcounted through get/put.

## Dependencies And Integration Points
The header depends on Linux bitmap/types and local `item.h`. It is consumed by Spectrum ACL code that knows the device-specific block encodings and by flow parsing code that translates tc flower or other rules into AFK element usage/value sets.

## Risks And Edge Cases
- `MLXSW_AFK_ELEMENT_STORAGE_SIZE` must grow when adding elements beyond the current scratchpad range; otherwise value writes can overflow intended storage.
- Element instance definitions must match the element's type and size unless `avoid_size_check` is deliberately used.
- Subset checks are directional. Passing arguments in the wrong order can accept incompatible key layouts.
- `VIRT_ROUTER` and split virtual-router elements coexist; users must select the form expected by their hardware blocks.

## Test Signals
Compile tests should cover every macro form. Functional tests should validate element-usage helpers, layout get/put, block encoding IDs, value addition for U32 and buffer elements, subset checks, storage-size assumptions when new elements are added, and device-specific encode/clear callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.c

## Purpose
`core_env.c` manages transceiver/module environment state for mlxsw devices. It supports ethtool module info and EEPROM reads/writes, module resets, module power-mode policy, module temperature thresholds and overheat counters, plug and temperature-warning events, module type validation, and line-card activation/inactivation integration.

## Important APIs, Types, And Functions
- `struct mlxsw_env` owns the core pointer, bus info, maximum modules per slot, slot count including main board, maximum EEPROM transaction length, `line_cards_lock`, and per-slot `struct mlxsw_env_line_card` pointers.
- `struct mlxsw_env_line_card` stores active state, current module count, and flexible per-module `struct mlxsw_env_module_info` records.
- `struct mlxsw_env_module_info` caches overheat counter, current overheat state, number of mapped ports, number of administratively up ports, power-mode policy, and module type from PMTM.
- EEPROM APIs include `mlxsw_env_get_module_info()`, `mlxsw_env_get_module_eeprom()`, `mlxsw_env_get_module_eeprom_by_page()`, and `mlxsw_env_set_module_eeprom_by_page()`. They validate active line cards and module type, query MCIA, split reads/writes by hardware transaction length, process MCIA status, and handle SFP/QSFP/CMIS paging.
- Thermal APIs include `mlxsw_env_module_temp_thresholds_get()`, `mlxsw_env_module_overheat_counter_get()`, `mlxsw_env_module_has_temp_sensor()`, `mlxsw_env_temp_event_set()`, and MTWE event work.
- Reset and power APIs include `mlxsw_env_reset_module()`, `mlxsw_env_get_module_power_mode()`, `mlxsw_env_set_module_power_mode()`, `mlxsw_env_module_port_up()`, and `mlxsw_env_module_port_down()`.
- Mapping APIs `mlxsw_env_module_port_map()` and `mlxsw_env_module_port_unmap()` track how many ports share a module, which gates reset behavior.
- Initialization/finalization are `mlxsw_env_init()` and `mlxsw_env_fini()`. They allocate line-card/module caches, register linecard event ops, register MTWE/PMPE trap listeners, enable module events, cache module types, query MCIA transaction length, and clean up with ordered-workqueue flushes.

## Control Flow
Initialization queries MGPIR for module count and slot count. For modular systems, it allocates `num_of_slots + 1` line-card records and uses the maximum modules per slot; for non-modular systems, slot zero gets the main-board module count immediately. All module power policies default to high. It registers linecard active/inactive callbacks, temperature-warning and module-plug event listeners, enables PMAOS operation-state and MTMP temperature events for slot zero, queries module types through PMTM, detects whether 128-byte MCIA transactions are supported through MCAM, and marks the main board active.

EEPROM read flow first validates that the line card is active and the module type supports EEPROM access. Legacy ethtool reads detect cable identifier and use `mlxsw_env_query_module_eeprom()` in a loop, which clamps each transaction to `max_eeprom_len`, avoids crossing low-page boundaries, chooses I2C low/high address, adjusts QSFP/CMIS upper-page offsets, queries MCIA, checks status, and copies returned bytes. Page-based ethtool reads/writes use caller-provided page/bank/I2C address and loop until requested length is processed.

Power-mode flow is policy-driven. `HIGH` keeps modules high-power. `AUTO` transitions to low power when no mapped port is administratively up and back to high power when the first port goes up. Applying hardware power mode disables the module through PMAOS, writes the low-power override through PMMP, then re-enables the module; failure tries to restore the previous state. If a line card is inactive, policy is cached and applied by `mlxsw_env_got_active()`.

Event flow uses core trap listeners. MTWE temperature warnings are copied into heap work items; ordered work compares sensor warning bits to cached `is_overheat`, increments overheat counters only on no-warning to warning transitions, and clears state on recovery. PMPE plug events for plugged/enabled modules schedule work that clears overheat state, checks for a temperature sensor, and enables MTMP events. Linecard activation queries module count, enables module events, caches module types, marks active, and reapplies cached power policies.

## State And Persistence Behavior
Runtime state is cached in `mlxsw_env` and protected by `line_cards_lock`. Overheat counters persist only for the lifetime of the driver instance. Power-mode policy is cached per module and applied to hardware when possible; inactive line cards retain the desired policy until activation. Port map/up counters coordinate reset and auto-power decisions but are not persisted. EEPROM data and module hardware state are external device/module state reached through registers.

## Dependencies And Integration Points
The file integrates with Linux ethtool module APIs, SFP constants, netlink extack, mutexes, and mlxsw core trap/workqueue helpers. It depends on register definitions for MCIA, MTMP, MTBR, PMAOS, PMMP, MCION, PMPE, MGPIR, PMTM, and MCAM. It registers `mlxsw_linecards_event_ops` with the linecard subsystem and uses `mlxsw_core_env()` to retrieve the environment handle from core.

## Risks And Edge Cases
- Linecard/module indexing must stay within `num_of_slots` and `max_module_count`; PMPE validates with `WARN_ON_ONCE()`, but most public APIs assume valid caller indices.
- `mlxsw_env_module_event_disable()` is empty, so event disable relies mostly on unregister/fini and inactive flags. Future event additions need explicit disable handling.
- MTWE only supports the main board, so temperature warning work always updates slot zero even though other paths are slot-aware.
- Reset is rejected if any port using the module is administratively up or if multiple ports share the module without the shared reset flag.
- Power-mode transitions manipulate module enable state. Partial failures attempt rollback but can still leave hardware inconsistent if register writes fail repeatedly.
- EEPROM page and offset calculations differ for SFP, QSFP, and CMIS. Boundary mistakes can read wrong pages or overrun a caller request.
- Module type validation rejects twisted-pair modules for EEPROM/reset/power operations, so callers must surface `-EINVAL`/`-EOPNOTSUPP` clearly.

## Test Signals
Test non-modular and modular init paths, linecard active/inactive callbacks, EEPROM reads across low-page boundary and with 48-byte vs 128-byte MCIA limits, CMIS flat and paged module info, MCIA status-to-extack mapping, reset rejection for up/shared modules, auto power transitions on first port up and last port down, inactive-linecard policy caching, MTWE overheat counter transitions, PMPE plug event temperature enablement, and finalization with ordered work flushed before listener unregister/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.h

## Purpose
`core_env.h` declares the mlxsw environment/module management interface used by port drivers and ethtool integration. It exposes module EEPROM, reset, power-mode, thermal threshold, overheat counter, port mapping/up-down accounting, and environment lifecycle APIs while keeping `struct mlxsw_env` private.

## Important APIs, Types, And Functions
- `mlxsw_env_module_temp_thresholds_get()` retrieves module temperature thresholds.
- `mlxsw_env_get_module_info()` and `mlxsw_env_get_module_eeprom()` implement legacy ethtool module-info and EEPROM access.
- `mlxsw_env_get_module_eeprom_by_page()` and `mlxsw_env_set_module_eeprom_by_page()` implement page/bank-aware module EEPROM access.
- `mlxsw_env_reset_module()` handles ethtool PHY reset flags for modules.
- `mlxsw_env_get_module_power_mode()` and `mlxsw_env_set_module_power_mode()` expose ethtool module power-mode policy and current mode.
- `mlxsw_env_module_overheat_counter_get()` reports cached overheat transition counts.
- `mlxsw_env_module_port_map()`, `mlxsw_env_module_port_unmap()`, `mlxsw_env_module_port_up()`, and `mlxsw_env_module_port_down()` let port code report module sharing and administrative state.
- `mlxsw_env_init()` and `mlxsw_env_fini()` manage environment subsystem lifetime.

## Control Flow
The header's API shape makes port drivers call map/unmap as ports are associated with modules, port_up/down as administrative state changes, ethtool handlers call info/EEPROM/reset/power methods, and core lifecycle code call init/fini during device registration and unregister.

## State And Persistence Behavior
All persistent implementation state is hidden behind opaque `struct mlxsw_env`, returned from `mlxsw_env_init()` and destroyed by `mlxsw_env_fini()`. The public functions mutate per-module cached state and hardware state through the core pointer.

## Dependencies And Integration Points
The header includes Linux ethtool declarations and forward-declares ethtool structures. It depends on callers having valid `struct mlxsw_core`, `struct net_device`, slot index, and module index values. It is consumed by port drivers that implement ethtool module operations and by `core.c` for environment lifecycle.

## Risks And Edge Cases
- Public APIs accept raw slot/module numbers; caller-side validation matters because the implementation often assumes valid ranges.
- Port map/up counters must be balanced. Missing `unmap` or `port_down` calls can block resets or keep modules high-power.
- Page-based EEPROM writes can alter module state; users need extack feedback and hardware capability checks.

## Test Signals
Compile users for every ethtool hook, balanced map/unmap/up/down paths, init/fini pairing in core registration, error propagation through extack for page operations, and reset/power-mode behavior from port administrative state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.h -->
