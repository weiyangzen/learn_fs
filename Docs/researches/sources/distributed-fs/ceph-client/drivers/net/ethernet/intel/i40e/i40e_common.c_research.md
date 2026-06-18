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
- Switch/VSI/VEB/filtering: VSI add/get/update, promiscuous/default VSI helpers, switch config, VEB add/query, MAC-VLAN add/remove v1/v2, control packet filters, cloud filters, and tunnel add/delete.
- Virtualization: `i40e_aq_send_msg_to_vf()` formats PF-to-VF Admin Queue sideband messages.
- Resource/NVM/capabilities: `i40e_aq_request_resource()`, `i40e_aq_release_resource()`, `i40e_aq_read_nvm()`, `i40e_aq_erase_nvm()`, `i40e_aq_update_nvm()`, `i40e_aq_discover_capabilities()`, and internal capability parsing.
- LLDP/DCB/scheduler: LLDP get/set/event/start/stop helpers, `i40e_aq_set_dcb_parameters()`, `i40e_aq_get_cee_dcb_config()`, `i40e_aq_dcb_updated()`, and scheduler bandwidth query/config wrappers.
- Registers/debug/LED/PHY access: debug register read/write/dump, RX control read/write with AQ fallback logic, Clause 22/45 MDIO accessors, AQ PHY register accessors, GPIO/PHY LED helpers, alternate RAM reads, and partition bandwidth config.
- DDP package handling: `i40e_aq_write_ddp()`, `i40e_aq_get_ddp_list()`, `i40e_find_segment_in_package()`, `i40e_write_profile()`, `i40e_rollback_profile()`, and validation/execution helpers.

## Control Flow

Initialization begins with `i40e_init_shared_code()`: determine MAC type from PCI IDs, reject unsupported types, mark link info stale, compute port/PF ID from registers, and initialize NVM. Firmware version/capability discovery is then done through Admin Queue wrappers that fill descriptors, set indirect-buffer flags, send commands, and copy firmware responses into `hw` fields.

Reset flow in `i40e_pf_reset()` waits for global reset steady state, waits for firmware core/global modules to report ready, optionally triggers PF software reset, handles a global reset that appears during PF reset polling, then clears PXE mode. `i40e_clear_hw()` separately disables interrupts, queue linked lists, and Tx/Rx queues after deriving queue/vector/VF counts from allocation registers.

Link flow starts with `i40e_aq_get_link_info()`, which updates `hw->phy.link_info`, `hw->phy.media_type`, flow-control current mode, FEC/pacing/CRC/link-status-event flags, and `hw->phy.phy_types` when AQ PHY access supports richer data. `i40e_update_link_info()` layers on PHY abilities when media is present and link state needs timely FEC/module information. `i40e_get_link_status()` lazily refreshes link info if `hw->phy.get_link_info` is set.

Filter and switch flows generally prepare descriptors from `i40e_adminq_cmd.h`, set valid flags, perform endian conversion, send direct or indirect AQ commands, and copy response counters/SEIDs back to caller state. MAC-VLAN v2 variants return AQ status through a caller-provided stack variable to avoid races on `hw->aq.asq_last_status`.

Capability discovery sends either list-device or list-function capability opcodes, then `i40e_parse_discover_capabilities()` maps firmware records into `hw->dev_caps` or `hw->func_caps`. It also derives `hw->num_ports`, partition ID/count, OCP-card special cases, and disables FCoE in unsupported NPAR/Flex10 modes.

DDP flow validates package track ID, supported device table, and rollback/original section types. Original profiles execute AQ sections and write MMIO sections through DDP AQ; rollback writes rollback MMIO sections in reverse order.

## State And Persistence Behavior

This file mutates software mirrors (`hw->mac.type`, `hw->phy.*`, `hw->fc.current_mode`, capabilities, port/partition data, `hw->pba_id`, and bus descriptors), hardware registers, and firmware-managed tables. Persistent or durable changes can occur through NVM update/erase, persistent LLDP start/stop, LAA/WoL MAC write flags, DDP profile loading, and alternate/partition bandwidth programming depending on firmware behavior. Most switch/VSI/filter/RSS/link state is reset-scoped or driver-lifetime-scoped.

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
- Some helper functions fall back from AQ register access to direct MMIO, which can hide firmware access failures.
- Cloud filter big-buffer Geneve handling mutates tenant IDs by shifting them for hardware expectations; callers must not reuse the same buffers assuming original tenant ID layout.

## Test Signals

- Device probe/reset/unload loops should exercise `i40e_init_shared_code()`, capability discovery, queue cleanup, PF reset, and PXE clearing.
- Link tests should cover link up/down, media changes, FEC, pause modes, firmware API-version gates, and `hw->phy.get_link_info` lazy refresh.
- Filter tests should cover MAC-VLAN add/remove v1/v2, VLAN-specific promiscuous modes, control packet filters, cloud filters including Geneve big-buffer entries, RSS key/LUT operations, and tunnel add/delete.
- NVM/DDP tests need strict negative coverage for invalid offsets, oversized buffers, unsupported track IDs, rollback/original section mismatches, and AQ error reporting.
- DCB/LLDP/scheduler tests should verify capability-gated persistent operations and bandwidth/ETS query/config wrappers.
- Debug and register-access tests should include AQ EAGAIN retry/fallback paths for RX control access and MDIO timeout handling.
