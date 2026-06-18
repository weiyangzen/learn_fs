# Research: subset-b-004455

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq_cmd.h

## Purpose

`i40e_adminq_cmd.h` is the firmware-facing Admin Queue ABI for Intel i40e devices in this tree. It defines Admin Queue opcodes, descriptor payload overlays, indirect buffer layouts, bit masks, and compile-time structure-size checks used by `i40e_common.c`, `i40e_adminq.c`, NVM/DCB/link code, cloud filter code, and the iWARP client path. The header is intentionally low-level: command structs must match firmware-defined byte layouts, with most direct command payloads constrained to the 16-byte `libie_aq_desc.params.raw` area and larger data passed as indirect buffers.

## Important APIs, Types, And Constants

- `enum i40e_admin_queue_opc` is the central opcode registry. It covers core AQ commands, resource ownership, device/function capabilities, switch/VSI/VEB/MAC-VLAN/filter management, DCB and scheduler commands, PHY/link/NVM commands, LLDP, RSS/tunnel commands, virtualization mailbox commands, DDP, OEM, async events, and debug operations.
- Firmware API version constants such as `I40E_FW_API_VERSION_MAJOR`, `I40E_FW_API_VERSION_MINOR_X722`, `I40E_MINOR_VER_GET_LINK_INFO_XL710`, and `I40E_MINOR_VER_FW_LLDP_STOPPABLE_X722` gate behavior in common code.
- `I40E_CHECK_STRUCT_LEN` and `I40E_CHECK_CMD_LENGTH` enforce ABI sizes at compile time. These are test-like guards for the firmware contract.
- Descriptor overlays include `i40e_aqc_get_version`, `i40e_aqc_queue_shutdown`, `i40e_aqc_mac_address_read/write`, `i40e_aqc_add_get_update_vsi`, `i40e_aqc_set_vsi_promiscuous_modes`, `i40e_aqc_add_veb`, `i40e_aqc_macvlan`, `i40e_aqc_pf_vf_message`, `i40e_aqc_nvm_update`, `i40e_aqc_lldp_*`, `i40e_aqc_get_set_rss_*`, and `i40e_aqc_phy_register_access`.
- Larger indirect buffer contracts include `i40e_aqc_vsi_properties_data`, `i40e_aq_get_phy_abilities_resp`, scheduler bandwidth response/config buffers, DCB/CEE responses, WoL data, cloud filter entries, DDP profile responses, and RSS key data.

## Control Flow And Usage

This header has no executable control flow, but it shapes control flow throughout the driver. Callers allocate and fill `libie_aq_desc`, call `i40e_fill_default_direct_cmd_desc()` with an opcode from this file, cast `desc.params.raw` through `libie_aq_raw()`, set little-endian fields and AQ flags, and pass optional indirect buffers to `i40e_asq_send_command*()`.

Typical flows:

- Device initialization reads firmware/API version, discovers capabilities, reads MAC addresses, configures switch/VSI state, and learns PHY/link capabilities.
- Link management uses PHY abilities, set PHY config, MAC config, restart autonegotiation, link-status event masks, and PHY debug/register access definitions.
- Filtering uses MAC-VLAN, VLAN, control packet, promiscuous, cloud, tunnel, and RSS command layouts.
- SR-IOV and RDMA/iWARP paths use PF-to-VF virtual channel messages and VSI queue-option bits such as `I40E_AQ_VSI_QUE_OPT_TCP_ENA`.
- DCB and scheduler paths use LLDP, CEE DCBX, ETS, bandwidth allocation, partition bandwidth, and queue-set handle structures.
- NVM and DDP paths use NVM read/erase/update/config structures and personalization profile section responses.

## State And Persistence Behavior

The header describes state that lives in firmware, hardware tables, NVM, and driver-owned mirror structs. Some commands are transient, such as debug register reads or link-status queries. Others change persistent or semi-persistent state:

- NVM update/erase/config commands can modify firmware/NVM contents. X722 preservation flags control what is retained.
- LLDP start/stop commands can request persistence across power cycles when firmware capabilities allow it.
- MAC write flags can alter LAA/WoL-related address behavior.
- DDP commands load or roll back dynamic device personalization profiles.
- Switch, VSI, scheduler, cloud filter, MAC-VLAN, and tunnel commands modify hardware tables that persist until reset, removal, or replacement.

All multi-byte firmware fields are little-endian (`__le16`, `__le32`), while byte arrays such as MAC addresses, IPv6 addresses, and module descriptors have command-specific ordering. The file calls out at least one big-endian warning for IPv6 proxy data.

## Dependencies And Integration Points

- Includes `<linux/net/intel/libie/adminq.h>` for common Admin Queue descriptor and shared command definitions.
- Includes Linux bit/type helpers.
- Used heavily by `i40e_common.c`, `i40e_adminq.c`, `i40e_dcb.c`, `i40e_nvm.c`, `i40e_main.c`, and client/iWARP integration.
- Command structs must remain synchronized with firmware and with common-code wrappers that assume exact field offsets.

## Risks

- ABI drift is the largest risk: changing field order, size, endian type, or flags can silently break firmware communication.
- Some layouts intentionally include padding for compiler/FW alignment differences, especially the legacy CEE DCB response. These must not be "cleaned up" mechanically.
- Duplicate macro names occur in the CEE DCB area and should be treated cautiously during refactors.
- Command flags such as `LIBIE_AQ_FLAG_BUF`, `LIBIE_AQ_FLAG_RD`, `LIBIE_AQ_FLAG_LB`, and `LIBIE_AQ_FLAG_SI` must match whether firmware expects direct, indirect, read, write, or sideband semantics.
- Firmware API-version gates mean fields can be ignored or interpreted differently on XL710 versus X722 and older firmware.

## Test Signals

- Compilation is a meaningful first-order test because `I40E_CHECK_*` catches many ABI-size regressions.
- Runtime coverage should exercise firmware-version discovery, link status, PHY abilities, VSI add/update/get, MAC-VLAN add/remove, RSS key/LUT get/set, LLDP/DCB commands, NVM read/update error paths, and virtual channel PF-to-VF messaging.
- Useful negative tests include zero/invalid buffer sizes, unsupported firmware capability bits, large-buffer AQ paths, and endian-sensitive fields.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_alloc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_alloc.h

## Purpose

`i40e_alloc.h` is the small shared allocation contract for i40e common code. It gives hardware/shared modules a driver-local abstraction for coherent DMA memory and ordinary virtual memory without embedding allocation implementation details in common Admin Queue, HMC, NVM, or DCB code.

## Important APIs, Types, And Functions

- `struct i40e_dma_mem` tracks DMA-backed memory through virtual address `va`, bus/DMA address `pa`, and `size`.
- `struct i40e_virt_mem` tracks non-DMA virtual memory through `va` and `size`.
- `i40e_allocate_dma_mem(struct i40e_hw *hw, struct i40e_dma_mem *mem, u64 size, u32 alignment)` allocates DMA memory for shared code consumers.
- `i40e_free_dma_mem(struct i40e_hw *hw, struct i40e_dma_mem *mem)` releases a DMA allocation and is expected to clear or invalidate the tracking fields in its implementation.
- `i40e_allocate_virt_mem(struct i40e_hw *hw, struct i40e_virt_mem *mem, u32 size)` allocates normal zeroed/driver memory.
- `i40e_free_virt_mem(struct i40e_hw *hw, struct i40e_virt_mem *mem)` releases virtual memory.

The implementations are in `i40e_main.c`, while callers include Admin Queue ring setup, ARQ/ASQ buffer info arrays, HMC page/table management, DCB buffers, and NVM update helpers.

## Control Flow

The header itself only declares contracts. Typical flow is:

1. A subsystem prepares an empty `i40e_dma_mem` or `i40e_virt_mem`.
2. It calls an allocation helper with a target size and, for DMA, alignment.
3. The returned `va`, `pa`, and `size` are stored in queue, HMC, NVM, or DCB structures.
4. Cleanup calls the matching free helper during unwind, shutdown, reset cleanup, or error handling.

## State And Persistence Behavior

The state is in the memory tracking structs, not in the header. DMA allocations back hardware-visible descriptor rings and command buffers, so stale `pa`/`va` fields can cause hardware access to freed memory if cleanup ordering is wrong. Virtual allocations carry driver-only buffers. No allocation state persists across driver unload; hardware-visible DMA state must be torn down before queue or HMC state is destroyed.

## Dependencies And Integration Points

- Includes Linux types and forward-declares `struct i40e_hw`.
- Integrates with `i40e_adminq.h` queue memory fields, `i40e_hmc.h` backing pages/tables, `i40e_type.h` NVM buffers, and `i40e_main.c` OS-specific allocator implementations.
- The abstraction keeps common code independent of exact Linux allocator calls.

## Risks

- Size type mismatch: DMA allocation accepts `u64 size`, while virtual allocation uses `u32 size`; callers must avoid truncating large virtual allocations.
- Missing matched frees can leak coherent DMA or virtual memory. Double frees or stale pointers can corrupt queue/HMC teardown.
- Alignment is caller-specified for DMA and must match hardware requirements.
- Because the structs are minimal, ownership and lifetime are implicit in caller code.

## Test Signals

- Error-unwind tests around Admin Queue and HMC initialization should verify every successful allocation is freed.
- Fault injection on allocation failures should leave `va`, `pa`, and size fields in a safe state.
- DMA API debug and KASAN/KMEMLEAK are strong signals for misuse.
- Reset/unload/reload loops can expose stale DMA or virtual allocation lifetime bugs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_client.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_client.c

## Purpose

`i40e_client.c` is the LAN-driver side of the auxiliary client interface, primarily for the iWARP/RDMA client. It creates an `i40e_info` view of the PF, exposes callback operations to the client, registers an auxiliary device named `iwarp`, opens/closes the client when service state allows, forwards VF virtual-channel events, and maps RDMA queue/vector interrupts into i40e hardware registers.

## Important APIs, Types, And Functions

- Global state: `i40e_devices` tracks LAN devices under `i40e_device_mutex`; `i40e_client_ida` allocates auxiliary device IDs.
- `i40e_lan_ops` exposes `virtchnl_send`, `setup_qvlist`, `request_reset`, and `update_vsi_ctxt` to the client.
- `i40e_client_get_params()` derives runtime MTU and priority-to-traffic-class/queue-set-handle QoS parameters from DCB/VSI state.
- Notification functions call client callbacks when a client exists and is opened: `i40e_notify_client_of_vf_msg()`, `i40e_notify_client_of_l2_param_changes()`, `i40e_notify_client_of_netdev_close()`, `i40e_notify_client_of_vf_reset()`, `i40e_notify_client_of_vf_enable()`, and `i40e_vf_client_capable()`.
- `i40e_client_update_msix_info()` refreshes the client-visible iWARP MSI-X count and entries.
- `i40e_register_auxiliary_dev()` allocates and registers the auxiliary device. `i40e_auxiliary_dev_release()` frees the ID and wrapper.
- `i40e_client_add_instance()` builds `pf->cinst`, fills `lan_info`, copies MAC/version/firmware/MSI-X data, and registers the auxiliary `iwarp` device.
- `i40e_lan_add_device()` and `i40e_lan_del_device()` manage PF list membership and client instance lifetime.
- `i40e_client_subtask()` opens the client on service events and keeps the VSI TCP enable queue option in sync with netdev up/down state.
- `i40e_client_virtchnl_send()` sends `VIRTCHNL_OP_RDMA` messages to a VF using `i40e_aq_send_msg_to_vf()`.
- `i40e_client_setup_qvlist()` programs CEQ/AEQ interrupt routing registers for client-owned vectors.
- `i40e_client_request_reset()` maps client reset requests to PF reset service bits.
- `i40e_client_update_vsi_ctxt()` gets and updates PF VSI context to toggle `I40E_AQ_VSI_QUE_OPT_TCP_ENA`.
- Exported symbols `i40e_client_device_register()` and `i40e_client_device_unregister()` are used by the RDMA auxiliary client driver to attach/detach.

## Control Flow

PF registration calls `i40e_lan_add_device()`, which adds a list node, creates a client instance, registers the auxiliary device, sets `__I40E_CLIENT_SERVICE_REQUESTED`, and schedules service. The iWARP auxiliary driver probes and calls `i40e_client_device_register()`, which stores the client pointer and schedules service again. `i40e_client_subtask()` runs in the i40e service path; if the PF is not down or config-busy and the netdev is registered, it calls the client's `open()` and marks the instance opened only if open succeeds.

After open, event notification helpers gate every callback on `pf->cinst`, `client`, the specific operation pointer, and `__I40E_CLIENT_INSTANCE_OPENED`. Close paths call the client `close()` callback, clear the opened bit, and release any queue-vector list. Unregister waits for service scheduling state, closes if needed, clears the client pointer, and releases the service bit.

The queue/vector setup flow validates that each requested vector lies within `[pf->iwarp_base_vector, pf->iwarp_base_vector + pf->num_iwarp_msix)`, saves a copy of the `qvlist_info`, writes `PFINT_LNKLSTN`, `PFINT_CEQCTL`, and `PFINT_AEQCTL`, then flushes hardware. On validation failure it frees the partially stored list and returns `-EINVAL`.

## State And Persistence Behavior

Persistent driver state includes `pf->cinst`, `cdev->state` bits, `cdev->lan_info`, `ldev->qvlist_info`, the global LAN-device list, and auxiliary device IDs. Hardware state includes interrupt linkage/control registers and VSI queue option state. This state lasts until netdev close, client unregister, PF removal, reset, or LAN device deletion. No state is persisted to NVM, but service bits and hardware register writes can survive until reset or explicit cleanup.

## Dependencies And Integration Points

- Depends on `include/linux/net/intel/i40e_client.h` for client ABI types and callback signatures.
- Depends on `i40e.h` for PF/VSI state bits, register macros, queue constants, and service scheduling.
- Uses Admin Queue wrappers from `i40e_common.c`, especially `i40e_aq_send_msg_to_vf()`, `i40e_aq_get_vsi_params()`, and `i40e_aq_update_vsi_params()`.
- Integrates with the Linux auxiliary bus and the RDMA client implementation under `drivers/infiniband/hw/irdma/i40iw_if.c`.

## Risks

- `i40e_lan_del_device()` assumes `pf->cinst` exists when dereferencing `pf->cinst->lan_info.aux_dev`; callers must not delete a non-created instance.
- `i40e_client_device_unregister()` uses a busy-wait on `__I40E_SERVICE_SCHED`; incorrect service-bit handling can stall unregister.
- The qvlist setup validates vector ownership but not all semantic combinations of CEQ/AEQ/ITR values; bad client input can program invalid queue routing if higher-level checks are incomplete.
- Client callback pointers are checked before use, but callback execution is inherently cross-subsystem and must respect locking and reset state.
- `i40e_client_update_vsi_ctxt()` rejects VF VSI updates and only supports TCP enable; unsupported flags warn and do not update.
- The service task sets the opened bit before calling `open()` and clears it on failure; callback implementations must tolerate this lifecycle ordering.

## Test Signals

- Probe/remove and auxiliary-device bind/unbind loops should leave no leaked `i40e_client_instance`, auxiliary ID, or qvlist memory.
- RDMA client open/close tests should verify callbacks fire only when opened.
- SR-IOV tests should cover VF message, VF reset, VF enable, and `vf_capable()` flows.
- MSI-X/qvlist tests should include valid vectors, out-of-range vectors, CEQ disabled entries, AEQ entries, and register cleanup on close.
- Netdev up/down and MTU/DCB changes should trigger L2 parameter refresh and TCP enable bit updates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_common.c

## Purpose

`i40e_common.c` is the shared hardware-control implementation for i40e. It wraps Admin Queue commands, performs low-level register programming, initializes shared hardware identity, manages link/PHY/flow-control state, reads and updates NVM-facing data, discovers capabilities, configures switch/VSI/filter/scheduler resources, handles DDP packages, and provides debug/LED/MDIO helpers. It is the main bridge between higher-level i40e driver code and firmware/hardware contracts from `i40e_adminq_cmd.h`.

## Important APIs, Types, And Functions

- Device identity/init: `i40e_set_mac_type()`, `i40e_init_shared_code()`, `i40e_set_pci_config_data()`.
- AQ debug and liveness: `i40e_debug_aq()`, `i40e_check_asq_alive()`, `i40e_aq_queue_shutdown()`.
- Reset/cleanup: `i40e_pf_reset()`, `i40e_poll_globr()`, `i40e_clear_hw()`, `i40e_clear_pxe_mode()`, `i40e_aq_clear_pxe_mode()`.
- RSS: internal `i40e_aq_get_set_rss_lut()` and `i40e_aq_get_set_rss_key()` plus public get/set wrappers.
- MAC/PBA: `i40e_aq_mac_address_read()`, `i40e_aq_mac_address_write()`, `i40e_get_mac_addr()`, `i40e_get_port_mac_addr()`, `i40e_get_pba_string()`.
- PHY/link/flow control: `i40e_aq_get_phy_capabilities()`, `i40e_aq_set_phy_config()`, `i40e_set_fc()`, `i40e_aq_set_mac_config()`, `i40e_aq_get_link_info()`, `i40e_update_link_info()`, `i40e_get_link_status()`, `i40e_aq_set_phy_int_mask()`, `i40e_aq_set_mac_loopback()`, `i40e_aq_set_phy_debug()`.
- Switch/VSI/VEB/filtering: `i40e_aq_add_vsi()`, `i40e_aq_get_vsi_params()`, `i40e_aq_update_vsi_params()`, promiscuous/default VSI helpers, `i40e_aq_get_switch_config()`, `i40e_aq_set_switch_config()`, `i40e_aq_add_veb()`, `i40e_aq_get_veb_parameters()`, MAC-VLAN add/remove v1/v2 wrappers, control packet filters, cloud filters, and tunnel add/delete.
- Virtualization: `i40e_aq_send_msg_to_vf()` formats PF-to-VF Admin Queue sideband messages.
- Resource/NVM/capabilities: `i40e_aq_request_resource()`, `i40e_aq_release_resource()`, `i40e_aq_read_nvm()`, `i40e_aq_erase_nvm()`, `i40e_aq_update_nvm()`, `i40e_aq_discover_capabilities()`, and internal `i40e_parse_discover_capabilities()`.
- LLDP/DCB/scheduler: LLDP get/set/event/start/stop helpers, `i40e_aq_set_dcb_parameters()`, `i40e_aq_get_cee_dcb_config()`, `i40e_aq_dcb_updated()`, and scheduler bandwidth query/config wrappers around `i40e_aq_tx_sched_cmd()`.
- Registers/debug/LED/PHY access: debug register read/write/dump, RX control read/write with AQ fallback logic, Clause 22/45 MDIO accessors, AQ PHY register accessors, GPIO/PHY LED helpers, alternate RAM reads, and partition bandwidth config.
- DDP package handling: `i40e_aq_write_ddp()`, `i40e_aq_get_ddp_list()`, `i40e_find_segment_in_package()`, `i40e_write_profile()`, `i40e_rollback_profile()`, and validation/execution helpers.

## Control Flow

Initialization begins with `i40e_init_shared_code()`: determine MAC type from PCI IDs, reject unsupported types, mark link info stale, compute port/PF ID from registers, and initialize NVM. Firmware version/capability discovery is then done through Admin Queue wrappers that fill descriptors, set indirect-buffer flags, send commands, and copy firmware responses into `hw` fields.

Reset flow in `i40e_pf_reset()` first waits for global reset steady state, waits for firmware core/global modules to report ready, optionally triggers PF software reset, handles a global reset that appears during PF reset polling, then clears PXE mode. `i40e_clear_hw()` separately disables interrupts, queue linked lists, and Tx/Rx queues after deriving queue/vector/VF counts from allocation registers.

Link flow starts with `i40e_aq_get_link_info()`, which updates `hw->phy.link_info`, `hw->phy.media_type`, flow-control current mode, FEC/pacing/CRC/link-status-event flags, and `hw->phy.phy_types` when AQ PHY access supports richer data. `i40e_update_link_info()` layers on PHY abilities when media is present and link state needs timely FEC/module information. `i40e_get_link_status()` lazily refreshes link info if `hw->phy.get_link_info` is set.

Filter and switch flows generally prepare descriptors from `i40e_adminq_cmd.h`, set valid flags, perform endian conversion, send direct or indirect AQ commands, and copy response counters/SEIDs back to caller state. MAC-VLAN v2 variants return AQ status through a caller-provided stack variable to avoid races on `hw->aq.asq_last_status`.

Capability discovery sends either list-device or list-function capability opcodes, then `i40e_parse_discover_capabilities()` maps firmware records into `hw->dev_caps` or `hw->func_caps`. It also derives `hw->num_ports`, partition ID/count, OCP-card special cases, and disables FCoE in unsupported NPAR/Flex10 modes.

DDP flow validates package track ID, supported device table, and rollback/original section types. Original profiles execute AQ sections and write MMIO sections through DDP AQ; rollback writes rollback MMIO sections in reverse order.

## State And Persistence Behavior

This file mutates both software mirrors and hardware/firmware state:

- Software state: `hw->mac.type`, `hw->phy.*`, `hw->fc.current_mode`, `hw->dev_caps`, `hw->func_caps`, `hw->num_ports`, `hw->partition_id`, `hw->partition_count`, `hw->pba_id`, and PCI bus descriptors.
- Hardware registers: interrupt routing, queue enables, Tx pre-disable, GPIO LEDs, RX control registers, MDIO registers, filter-control registers, and reset/PXE registers.
- Firmware state: Admin Queue configuration for VSI/switch/VEB/MAC-VLAN/cloud filters/RSS/tunnels/LLDP/DCB/PHY/NVM/DDP/resource locks.
- Persistent or durable changes can occur through NVM update/erase, persistent LLDP start/stop, LAA/WoL MAC write flags, DDP profile loading, and alternate/partition bandwidth programming depending on firmware behavior.

Most state is reset-scoped or driver-lifetime-scoped, but callers must treat NVM and persistent LLDP/DDP operations as durable.

## Dependencies And Integration Points

- Depends on `i40e_adminq_cmd.h` for all command payloads and opcodes.
- Depends on `i40e_devids.h`, `i40e_prototype.h`, `i40e_register.h`, Linux PCI/etherdevice/delay/bitfield helpers, and `libie` Admin Queue helpers.
- Used by high-level i40e probe/init/reset/service/configuration paths, iWARP client code, DCB code, NVM code, devlink, ethtool, SR-IOV, and filter management.
- Relies on `rd32()`, `wr32()`, `i40e_asq_send_command*()`, endian helpers, `FIELD_PREP/FIELD_GET`, and firmware capability/version helper predicates.

## Risks

- Admin Queue wrappers are highly sensitive to flags, endian conversion, buffer length, and opcode/struct pairing.
- Many functions update shared `hw` state after firmware calls; concurrent service, reset, link, or client paths must preserve expected locking at higher layers.
- `hw->aq.asq_last_status` is global per hardware object; v2 MAC-VLAN helpers exist because reading it after a command can race.
- Reset and polling paths use fixed sleep/retry loops. Hardware or firmware timing changes can cause false failures or long stalls.
- NVM and DDP operations can permanently alter device behavior if called with wrong offsets, sizes, preservation flags, or package sections.
- Some helper functions fall back from AQ register access to direct MMIO. This improves compatibility but can hide firmware access failures.
- Capability parsing derives partition information from hardware registers and NVM/OCP state; wrong counts can affect WoL and partition behavior.
- Cloud filter big-buffer Geneve handling mutates tenant IDs by shifting them for hardware expectations; callers must not reuse the same buffers assuming original tenant ID layout.

## Test Signals

- Compile tests catch API drift through header size checks and prototype mismatches.
- Device probe/reset/unload loops should exercise `i40e_init_shared_code()`, capability discovery, queue cleanup, PF reset, and PXE clearing.
- Link tests should cover link up/down, media changes, FEC, pause modes, firmware API-version gates, and `hw->phy.get_link_info` lazy refresh.
- Filter tests should cover MAC-VLAN add/remove v1/v2, VLAN-specific promiscuous modes, control packet filters, cloud filters including Geneve big-buffer entries, RSS key/LUT operations, and tunnel add/delete.
- NVM/DDP tests need strict negative coverage for invalid offsets, oversized buffers, unsupported track IDs, rollback/original section mismatches, and AQ error reporting.
- DCB/LLDP/scheduler tests should verify capability-gated persistent operations and bandwidth/ETS query/config wrappers.
- Debug and register-access tests should include AQ EAGAIN retry/fallback paths for RX control access and MDIO timeout handling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_common.c -->
