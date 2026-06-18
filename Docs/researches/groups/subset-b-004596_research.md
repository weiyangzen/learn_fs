# Research Group: subset-b-004596

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.c

## Purpose
This file is the low-level hardware access and device programming layer for the NetXen/QLogic `netxen_nic` Ethernet driver. It provides revision-specific register access, PCI memory windowing, MAC and multicast programming, firmware command submission helpers, board and link helpers, WoL capability checks, and firmware minidump capture. `netxen_setup_hwops()` is the central integration point: it installs function pointers in `struct netxen_adapter` for P2 128 MB BAR mappings versus P3 2 MB mappings, and for P2 direct NIU MAC programming versus P3 firmware-command-based programming.

## Important APIs and Functions
- `netxen_pcie_sem_lock()` / `netxen_pcie_sem_unlock()` acquire and release PCIe hardware semaphores with a bounded sleep loop.
- `netxen_setup_hwops()` selects adapter operations including `crb_read`, `crb_write`, `pci_set_window`, `pci_mem_read`, `pci_mem_write`, `io_read`, `io_write`, `macaddr_set`, `set_multi`, `set_mtu`, and `set_promisc`.
- `netxen_get_ioaddr()` maps a CRB offset into an MMIO pointer, using direct P2 normalization or P3 2 MB CRB translation.
- `netxen_nic_change_mtu()`, `netxen_config_intr_coalesce()`, `netxen_config_hw_lro()`, `netxen_config_bridged_mode()`, `netxen_config_rss()`, `netxen_config_ipaddr()`, `netxen_linkevent_request()`, and `netxen_send_lro_cleanup()` issue device configuration requests.
- `netxen_get_flash_mac_addr()` and `netxen_p3_get_mac_addr()` retrieve MAC addresses from flash or CRB MAC blocks.
- `netxen_nic_get_board_info()` reads flash board metadata and maps board type to GbE or 10 GbE port type.
- `netxen_nic_set_link_parameters()` derives link speed, duplex, and autonegotiation state from PHY status or port mode.
- `netxen_dump_fw()` and the `netxen_md_*()` family parse and execute firmware minidump templates.

## Control Flow
The file starts with address translation tables for the legacy 128 MB CRB space and the newer 2 MB CRB window. Register reads and writes flow through either `netxen_nic_hw_read_wx_128M()` / `netxen_nic_hw_write_wx_128M()` or `netxen_nic_hw_read_wx_2M()` / `netxen_nic_hw_write_wx_2M()`. Directly mapped CRB blocks are accessed with `readl()`/`writel()`, while indirect blocks take `adapter->ahw.crb_lock`, program a CRB window register, access the register, then release the hardware and software locks.

Device memory accesses flow through `adapter->pci_mem_read` and `adapter->pci_mem_write`. OCM can be accessed directly through a PCI window, while QDR/DDR paths use MIU/SIU test agents: the code writes address and data registers, starts the test agent, polls `TEST_AGT_CTRL` for `TA_CTL_BUSY` to clear, and returns `-EIO` on timeout.

MAC programming is split by hardware generation. P2 writes NIU station, multicast, and promiscuous-mode registers directly, temporarily disabling receive while changing XG config. P3 builds firmware command descriptors (`nx_nic_req_t`) and pushes them through `netxen_send_cmd_descs()`, which locks the TX queue, checks ring availability, copies descriptors, advances the producer, and rings the command producer doorbell.

Firmware minidump collection starts in `netxen_dump_fw()`: it computes capture size from the template mask, allocates `md_capture_buff`, stamps driver metadata, then `netxen_parse_md_template()` walks template entries and dispatches to CRB, memory, ROM, cache, OCM, mux, and queue readers. Entry sizes are checked and entries are marked skipped or size-error when the captured size does not match the template.

## State and Persistence
Persistent device state is primarily MMIO and flash state. The file mutates `adapter->ahw` window tracking (`crb_win`, `ocm_win`), port metadata (`board_type`, `port_type`), link state fields (`link_speed`, `link_duplex`, `link_autoneg`, `module_type`), multicast state (`mc_enabled`, `mac_list`), feature flags, and minidump fields under `adapter->mdump`. Firmware-facing operations persist through CRB/PCI memory writes and host request descriptors. Flash reads are protected by ROM locks from other files. Minidump capture persists in allocated kernel memory until explicitly cleaned by main driver removal or ethtool paths.

## Dependencies and Integration Points
This file depends on `netxen_nic.h` for adapter structures, descriptor formats, CRB constants, minidump structures, command opcodes, and macros such as `NXRD32()` / `NXWR32()`. It depends on `netxen_nic_hw.h` for PHY and NIU bit helpers. It is called by `netxen_nic_main.c` during PCI mapping, board discovery, netdev setup, open/close, feature changes, and firmware recovery. It is called by `netxen_nic_init.c` for ROM and firmware boot interactions, and by ethtool/sysfs paths for diagnostics and minidumps.

## Risks and Edge Cases
- CRB and memory windowing is highly revision-specific; wrong revision detection can send reads or writes to the wrong BAR or indirect window.
- Several hardware polling loops are bounded but busy or sleep based; timeout values are hardware assumptions and failures surface as `-EIO`.
- P3 multicast list updates allocate with `GFP_ATOMIC` and send firmware add/delete commands while reconciling lists; allocation or command failure can desynchronize software and firmware MAC filters.
- `netxen_config_bridged_mode()` toggles the bridge flag with XOR after command submission; if the firmware command fails after partial side effects, software state may not match hardware.
- Minidump parsing trusts firmware-provided template sizes and offsets enough to walk entries in allocated buffers; corrupted templates are partially guarded by masks and size checks but remain a high-risk parsing surface.
- Diagnostic read/write paths elsewhere can call these low-level memory functions, so alignment and range checks must remain strict at callers.

## Test Signals
Useful validation signals include successful probe/open on both P2 and P3 hardware, correct MAC and multicast filtering under promiscuous/all-multicast transitions, MTU/LRO/RSS/interrupt coalescing ethtool changes, firmware link-event enable and fallback PHY polling, minidump capture after firmware reset, sysfs diagnostic CRB/memory reads in diagnostic mode, and error-path tests for invalid offsets, unaligned memory access, semaphore timeout, and test-agent timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.h

## Purpose
This header provides NetXen hardware-facing constants, register bit helpers, PHY register numbers, promiscuous-mode constants, and CRB mapping table types used by `netxen_nic_hw.c` and the wider `netxen_nic` driver. It is not a public API; it is a local hardware description layer for NIU, PHY, and CRB addressing details.

## Important APIs, Types, and Macros
- `NETXEN_MEMADDR_MAX` and `NETXEN_PCI_MAPSIZE_BYTES` describe hardware memory and PCI mapping size expectations.
- `netxen_nic_set_link_parameters()` is declared for callers that need to refresh adapter link fields.
- `_netxen_crb_get_bit()` is the primitive used by many field extractors.
- `netxen_gb_*` macros set, clear, and query GbE MAC config bits such as flow control, resets, TX/RX sync, and soft reset.
- `netxen_gb_mii_mgmt_*` and `netxen_get_gb_mii_mgmt_*` build and inspect MII management commands.
- `NETXEN_NIU_GB_MII_MGMT_ADDR_*` constants name PHY management registers.
- `netxen_get_phy_speed()`, `netxen_get_phy_link()`, and `netxen_get_phy_duplex()` decode PHY status register 17.
- `NETXEN_NIU_NON_PROMISC_MODE`, `NETXEN_NIU_PROMISC_MODE`, and `NETXEN_NIU_ALLMULTI_MODE` define P2 promiscuous programming modes.
- `crb_128M_2M_sub_block_map_t` and `crb_128M_2M_block_map_t` describe direct CRB sub-block translations from 128 MB offsets to 2 MB BAR offsets.

## Control Flow
The header has no executable control flow beyond macro expansion. Its macros are used in runtime paths where callers read a 32-bit register value, mutate or decode selected bits, and write the result back. The CRB mapping types are populated in `netxen_nic_hw.c` and consumed by the CRB address translation path for P3-style 2 MB mappings.

## State and Persistence
The header itself owns no state. It defines bit layouts that mutate hardware state when used with register writes. The most important persistent effects are enabling/disabling flow control, MAC resets, pause masks, PHY speed/duplex bits, and promiscuous modes. Because many helpers modify their argument expression with `|=` or `&=`, callers must pass mutable lvalues, not expressions with side effects.

## Dependencies and Integration Points
The header forward-declares `struct netxen_adapter` and is included by `netxen_nic_hw.c`, `netxen_nic_init.c`, and `netxen_nic_main.c`. It assumes register constants from `netxen_nic.h` for full use. Its PHY status helpers are directly used by link-parameter refresh logic, and its CRB map types are the basis of the P3 direct-versus-indirect register access decision.

## Risks and Edge Cases
- The mutating macros are not type-safe and can evaluate arguments in surprising ways if passed nontrivial expressions.
- Bit definitions are hardware-contract sensitive; a wrong bit position affects link, reset, pause, or PHY programming.
- Some comments duplicate the "NIU XG Pause Ctl Register" heading for GbE pause masks, which can confuse maintenance even though the bit helpers are distinct.
- `NETXEN_NIU_*` promiscuous constants are simple numeric modes for P2, while P3 uses firmware vport miss modes; callers must use the operation pointer selected by `netxen_setup_hwops()`.

## Test Signals
Build coverage is the primary direct signal. Runtime signals include correct link speed/duplex reporting for GbE PHYs, successful flow-control and reset behavior on P2 hardware, correct all-multicast/promiscuous handling, and absence of sparse/compiler warnings around macro use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_init.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_init.c

## Purpose
This file contains initialization, firmware loading, software ring allocation, RX/TX buffer lifecycle, receive completion processing, transmit completion processing, and ROM access helpers for the NetXen driver. It bridges PCI/flash firmware images into adapter memory, waits for firmware readiness, initializes NIC capabilities, and manages host-side descriptor rings used by the runtime data path.

## Important APIs and Functions
- `netxen_alloc_sw_resources()` and `netxen_free_sw_resources()` allocate/free TX command buffers, RDS rings, RX buffer arrays, and initialize SDS ring metadata.
- `netxen_release_rx_buffers()` and `netxen_release_tx_buffers()` unmap DMA and free SKBs during detach or reset.
- `netxen_rom_fast_read()` and `netxen_rom_fast_read_words()` provide ROM reads under ROM lock.
- `netxen_pinit_from_rom()` replays CRB initialization entries from flash after decoding internal CRB addresses.
- `netxen_request_firmware()`, `netxen_validate_firmware()`, and helper parsers validate and select unified, MN, cut-through, or flash firmware images.
- `netxen_need_fw_reset()`, `netxen_load_firmware()`, `netxen_phantom_init()`, and `netxen_init_firmware()` decide whether to reset firmware, load it to device memory, wait for PEG state, and perform host handshake.
- `netxen_process_rcv_ring()` handles status descriptors and dispatches normal RX, old RX, SYN offload, LRO, and firmware response descriptors.
- `netxen_process_cmd_ring()` reclaims TX descriptors and wakes the network queue.
- `netxen_post_rx_buffers()` and the no-doorbell variant replenish receive descriptors.

## Control Flow
Initialization begins with software resource allocation: a TX ring is allocated, then each receive descriptor ring is sized based on hardware revision, port type, cut-through mode, jumbo/LRO role, and firmware capabilities. RX buffers are initially placed on free lists, and SDS rings are linked to MSI-X vectors and NAPI structures by the main driver.

Firmware selection starts with `adapter->fw_type = NX_UNKNOWN_ROMIMAGE`; `nx_get_next_fwtype()` advances through supported image types until either a valid file firmware is found or flash firmware is selected. Unified images are validated by checking the file header, product table, bootloader descriptor, and firmware descriptor bounds. Legacy images are validated by magic, size, version, BIOS compatibility, flash compatibility, and minimum supported versions. Loading copies bootloader and firmware 64-bit words either from the selected firmware file or from flash into device memory via `adapter->pci_mem_write()`, then releases reset bits appropriate to P2/P3/P3P.

The runtime RX path is descriptor-driven. `netxen_process_rcv_ring()` reads host-owned status descriptors until budget or ownership exhaustion, dispatches packet descriptors to `netxen_process_rcv()` or `netxen_process_lro()`, handles firmware response messages, returns descriptors to firmware ownership, then refills RDS rings from per-SDS free lists and writes the status consumer. Normal RX unmaps DMA, sets checksum state, adjusts packet offset, sets protocol, and submits through GRO. LRO updates IP/TCP headers and passes the aggregated SKB to the stack.

The TX completion path reads the firmware hardware consumer, unmaps DMA fragments, frees SKBs, advances the software consumer, wakes stopped queues when ring space is available, and returns whether the ring is fully caught up. RX buffer posting allocates SKBs as needed, maps them for DMA, fills descriptors, advances producer indexes, writes CRB producer registers, and on older P2 firmware may also send a doorbell message.

## State and Persistence
The file owns host-side resource state in `adapter->tx_ring`, `adapter->recv_ctx.rds_rings`, SDS free lists, RX buffer state (`NETXEN_BUFFER_FREE`/busy), DMA mappings, descriptor producers/consumers, firmware metadata (`adapter->fw`, `fw_type`, `file_prd_off`, `fw_version`), hardware capability fields, dummy DMA for P2 watchdog support, and adapter stats. It persists firmware boot state by writing CRB registers such as `CRB_CMDPEG_STATE`, `CRB_NIC_CAPABILITIES_HOST`, `CRB_MPORT_MODE`, reset registers, and device memory image contents.

## Dependencies and Integration Points
This file depends on low-level CRB and memory operations installed by `netxen_setup_hwops()` in `netxen_nic_hw.c`. It uses Linux firmware loading, DMA mapping, SKB, NAPI/GRO, VLAN, checksum, and netdevice APIs. `netxen_nic_main.c` calls these functions during probe, open, detach, reset, NAPI poll, firmware health recovery, and remove. Firmware minidump setup lives in `netxen_nic_ctx.c`, while ethtool controls expose some firmware/minidump behavior.

## Risks and Edge Cases
- Firmware file parsing uses little-endian conversions and offset arithmetic; malformed firmware must be rejected before out-of-bounds descriptor access.
- Ring allocation has multiple staged allocations; error paths must free partially allocated rings and DMA mappings.
- RX processing must tolerate bogus ring indexes, reference handles, lengths, and descriptor counts from hardware without corrupting memory.
- LRO path rewrites packet headers and assumes enough header/data layout from firmware status fields.
- TX completion uses `spin_trylock_bh()` and can report incomplete work to force NAPI to continue; missed completions may stall queues.
- Firmware reset decisions depend on heartbeat, flash version, file version, and previous failure state; mistakes can leave a live firmware unnecessarily reset or a dead firmware reused.

## Test Signals
Important signals include successful firmware load from unified and flash images, validation rejection of malformed firmware, clean attach/detach under fault injection, RX/TX traffic with checksum offload, TSO and LRO traffic, jumbo frame receive, RX refill under allocation pressure, TX queue stop/wake behavior, NAPI budget behavior, and firmware heartbeat/reset recovery. DMA API debug and KASAN/KCSAN are useful for buffer lifecycle and ring concurrency issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_main.c

## Purpose
This is the main Linux PCI and netdevice driver for QLogic/NetXen 1/10 GbE adapters. It declares module metadata, PCI ID matching, probe/remove, power management, PCI error recovery, netdev operations, interrupt setup, NAPI polling, transmit path, firmware health workqueues, sysfs diagnostics, IPv4 address notification, and module init/exit registration.

## Important APIs and Functions
- `netxen_nic_probe()` enables the PCI device, maps BARs, starts firmware, configures interrupts, registers the netdev, and creates diagnostic entries.
- `netxen_nic_remove()`, `netxen_nic_shutdown()`, suspend/resume, and PCI error handlers tear down or restore device state.
- `netxen_setup_pci_map()` maps 128 MB, 32 MB, or 2 MB BAR layouts and calls `netxen_setup_hwops()`.
- `netxen_setup_intr()`, `netxen_setup_msi_interrupts()`, and `netxen_nic_request_irq()` select INTx/MSI/MSI-X and bind IRQ handlers to SDS rings.
- `netxen_nic_attach()`, `netxen_nic_detach()`, `__netxen_nic_up()`, and `__netxen_nic_down()` manage runtime hardware/software context.
- `netxen_nic_xmit_frame()` is the netdev TX entry; `netxen_tso_check()` formats checksum, VLAN, and TSO descriptors.
- `netxen_intr()`, `netxen_msi_intr()`, `netxen_msix_intr()`, and `netxen_nic_poll()` implement interrupt-to-NAPI flow.
- `netxen_fw_poll_work()`, `netxen_check_health()`, `netxen_detach_work()`, `netxen_fwinit_work()`, and `netxen_attach_work()` implement firmware health monitoring and reset recovery.
- Sysfs handlers expose `bridged_mode`, `diag_mode`, binary `crb`, `mem`, and `dimm` files.
- IPv4 and netdev notifiers program firmware destination IP filters for direct devices, VLANs, and bonding masters.

## Control Flow
Probe rejects unsupported revisions, enables PCI, requests BARs, allocates `net_device` with private `netxen_adapter`, initializes locks/lists, maps PCI resources, reads board info, checks flash firmware compatibility, starts firmware, determines physical port, sets MTU bounds, configures interrupts, registers the netdev, schedules firmware polling, and creates diagnostics.

Opening the netdev calls `netxen_nic_attach()` and then `__netxen_nic_up()`. Attach handshakes with firmware, allocates NAPI/SDS rings, software rings, hardware resources, posts initial RX buffers, requests IRQs, initializes coalescing defaults, creates sysfs entries, and marks `is_up`. Up initializes the port, programs MAC/multicast/MTU/RSS/coalescing/LRO, enables NAPI and interrupts, requests link events or polls PHY state, and sets `__NX_DEV_UP`.

Transmit starts in `netxen_nic_xmit_frame()`: it normalizes excessive non-TSO fragments with `__pskb_pull_tail()`, stops the queue if ring space is low, maps SKB fragments to DMA, fills command descriptors with up to four buffers each, sets VLAN/checksum/TSO opcode information, copies TSO headers into descriptors when required, updates stats, and writes the command producer. Completion is handled from NAPI through `netxen_process_cmd_ring()` in the init file.

Interrupt handlers clear target status or legacy state and schedule NAPI. NAPI polls TX completions and RX status ring work, completes when under budget, and re-enables interrupts only if the device is still up.

Firmware health is a delayed-work state machine. The poll work checks link when firmware link notifications are absent, checks temperature, honors requested resets, reads firmware heartbeat, and requests detach/reset after repeated heartbeat failures. Detach work stops the netdev and context, decrements firmware/device reference counts, then schedules firmware reinitialization. Firmware init work starts firmware when safe and schedules attach work to restore the running netdev and IP filters.

## State and Persistence
Key state includes module parameters (`auto_fw_reset`, MSI settings, port modes), adapter flags (`MSI/MSI-X`, reset owner, bridge, diag), `adapter->state` bits (`__NX_DEV_UP`, `__NX_RESETTING`, `__NX_FW_ATTACHED`), firmware/device CRB state (`NX_CRB_DEV_STATE`, reference count), IRQ vector tables, NAPI/SDS ring state, MAC/IP lists, stats, workqueue objects, and sysfs-visible diagnostic flags. Persistent hardware effects include firmware boot, port mode, WoL port mode, interrupt mode, CRB/device reference counters, MAC/multicast filters, RSS/LRO/coalescing configuration, and firmware IP filter programming.

## Dependencies and Integration Points
This file integrates the local NetXen hardware layer (`netxen_nic_hw.c`), initialization/data-path helpers (`netxen_nic_init.c`), context allocation (`netxen_nic_ctx.c`), ethtool ops, and Linux PCI/netdev/NAPI/IRQ/PM/AER/sysfs/notifier APIs. It registers a `pci_driver` and, when IPv4 support is enabled, global netdevice and inetaddr notifiers. It exposes diagnostics through PCI device sysfs and feature control through netdev ops and ethtool-supported feature changes.

## Risks and Edge Cases
- Probe and attach have many staged resources; unwind ordering must match allocation ordering to avoid IRQ, NAPI, DMA, or BAR leaks.
- Firmware reset is coordinated across multiple PCI functions by CRB reference counts and device state; races can affect multi-function adapters.
- TX descriptor construction combines DMA mapping, VLAN, checksum, and TSO header-copy side effects; error paths must not leak mapped fragments or leave producer state inconsistent.
- Diagnostic sysfs CRB/memory writes are powerful and guarded only by `diag_mode`, alignment, and range checks.
- `netxen_cancel_fw_work()` waits on `__NX_RESETTING`; incorrect bit handling can deadlock removal or suspend.
- Bonding/VLAN notifier logic walks upper/lower devices under RCU and mirrors IP filters into firmware; missed events can leave stale firmware IP filters.
- Legacy interrupt handling has hardware-specific clearing sequences and shared IRQ filtering; incorrect ordering can drop or storm interrupts.

## Test Signals
Validation should cover PCI probe/remove, open/close cycles, suspend/resume, AER slot reset, INTx/MSI/MSI-X selection, RSS with multiple SDS rings, TX TSO/checksum/VLAN combinations, RX under NAPI budget, firmware hang recovery, temperature panic handling, bridge mode sysfs, diagnostic mode access control, bonding/VLAN IP address events, link notification and PHY-poll fallback, and resource leak checks on every probe/attach failure label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/Makefile

## Purpose
This Makefile defines how the QLogic/Marvell `qed` core driver is built by Kbuild. It creates the `qed.o` module/object when `CONFIG_QED` is enabled and lists the base object files plus optional protocol and virtualization objects gated by Kconfig symbols.

## Important Build Entries
- `obj-$(CONFIG_QED) := qed.o` makes the composite driver conditional on `CONFIG_QED`.
- `qed-y` includes core objects such as chain management, context management, DCBX, debug, devlink, hardware access, firmware init ops, interrupts, L2, main, MCP, management TLV, PTP, selftest, slowpath commands, and SPQ.
- `qed-$(CONFIG_QED_FCOE)`, `qed-$(CONFIG_QED_ISCSI)`, `qed-$(CONFIG_QED_LL2)`, and `qed-$(CONFIG_QED_OOO)` add optional protocol/support files.
- `qed-$(CONFIG_QED_NVMETCP)`, `qed-$(CONFIG_QED_RDMA)`, and `qed-$(CONFIG_QED_SRIOV)` add grouped optional object sets for NVMe/TCP, RDMA/iWARP/RoCE, and SR-IOV/VF support.

## Control Flow
There is no runtime control flow. Kbuild evaluates configuration symbols and appends matching objects to the composite `qed.o` link. Base objects are always included with `CONFIG_QED`; optional objects are included only when their respective symbols are enabled.

## State and Persistence
The Makefile persists build composition, not runtime state. Its ordering affects which translation units are compiled and linked into `qed.o`, which in turn determines available symbols and feature coverage for the driver.

## Dependencies and Integration Points
This file integrates with Linux Kbuild and QED Kconfig symbols. It must stay synchronized with source files, exported symbols, and feature conditionals in headers such as `qed.h` and public headers under `include/linux/qed/`. Protocol drivers such as qede, storage offloads, and SR-IOV support depend on this object composition.

## Risks and Edge Cases
- Missing an object in `qed-y` can cause link failures or runtime feature absence.
- Adding optional objects without the correct `CONFIG_` guard can pull in unavailable dependencies.
- Object ordering usually should not matter for normal kernel linking, but generated init sections and duplicate symbols still require care.
- The SPDX license expression permits GPL-2.0-only or BSD-3-Clause use, matching the dual-licensed QED sources.

## Test Signals
Build matrix coverage is the key signal: `CONFIG_QED=y/m`, with and without FCoE, iSCSI, LL2, OOO, NVMETCP, RDMA, and SR-IOV. Linker errors, modpost warnings, and missing exported-symbol diagnostics identify Makefile composition regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed.h

## Purpose
`qed.h` is the central private header for the QED core driver. It defines common constants, helper macros, device and hardware-function structures, resource and feature enums, tunnel configuration structures, firmware data containers, interrupt parameters, debug structures, register access macros, and internal prototypes shared across QED implementation files.

## Important APIs, Types, and Macros
- `STORM_FW_VERSION`, chip/type macros, `MAX_HWFNS_PER_DEVICE`, and resource count macros define firmware and hardware limits.
- `qed_db_addr()` and `qed_db_addr_vf()` compute doorbell addresses for PF and VF contexts.
- `QED_MFW_GET_FIELD()` and `QED_MFW_SET_FIELD()` manipulate management firmware bitfields.
- Tunnel types include `enum qed_tunn_mode`, `enum qed_tunn_clss`, `struct qed_tunnel_info`, `struct qed_tunn_start_params`, and `struct qed_tunn_update_params`.
- Personality and capability enums include `enum qed_pci_personality`, `enum qed_resources`, `enum QED_FEATURE`, `enum qed_dev_cap`, and `enum qed_wol_support`.
- `struct qed_hw_info` stores per-hwfn resource starts/counts, feature counts, personality, traffic classes, FIDs, MAC/WWN identity, capabilities, MTU, and WoL support.
- `struct qed_hwfn` represents one hardware function/path with BAR views, PTTs, SPQ/EQ/ConSQ, slowpath tasklets/workqueues, protocol contexts, MCP/DCBX/LLH/IOV state, DMAE, QM, debug, doorbell recovery, and NVM metadata.
- `struct qed_dev` is the top-level device containing chip identity, BARs, hwfns, interrupt settings, protocol callbacks, firmware data, recovery state, debug state, and per-protocol limits.
- `REG_RD()`, `REG_WR()`, `REG_WR16()`, and `DOORBELL()` wrap MMIO access through `regview` and `doorbells`.
- Prototypes expose internal services such as device info fill, link/bandwidth update, firmware unzip, recovery scheduling, protocol stats, slowpath IRQ, TLV handling, WFQ, LLH filters, and doorbell recovery.

## Control Flow
The header mostly defines data contracts. Inline control flow exists in doorbell address helpers and `qed_concrete_to_sw_fid()`, which decodes a concrete PF/VF function ID into a software function ID. Many macros guide runtime branch selection: personality macros select protocol behavior, `for_each_hwfn()` iterates hardware functions, `QED_IS_CMT()` detects multi-hwfn devices, affinity macros choose leading or protocol-affine hwfns, and resource macros compute resource ranges.

## State and Persistence
This header defines almost all long-lived QED core state. `struct qed_dev` persists across the PCI device lifetime and owns BAR mappings, firmware pointers, interrupt mode, recovery flags, protocol callback cookies, debug buffers, and hardware functions. Each `struct qed_hwfn` persists per engine/path and owns slowpath queues, PTTs, protocol-specific contexts, DMAE buffers, QM configuration, doorbell recovery state, debug arrays, and workqueue/tasklet state. Hardware-persistent changes occur through code using this state to write registers, doorbells, management firmware messages, NVM updates, and protocol contexts.

## Dependencies and Integration Points
`qed.h` pulls in Linux kernel headers, public QED interface headers, and generated/hardware-specific headers (`qed_hsi.h`, `qed_dbg_hsi.h`, `qed_mfw_hsi.h`). It is included broadly by QED implementation files built in the Makefile and forms the private integration contract between core, L2, storage offloads, RDMA, SR-IOV, debug, MCP, PTP, and devlink code. Public protocol drivers interact through higher-level ops, but many callbacks and cookies are rooted in these structures.

## Risks and Edge Cases
- Because this header is central, field layout changes have wide blast radius across optional features and build configurations.
- MMIO macros are thin wrappers with no barriers beyond accessor semantics; callers must enforce ordering and locking.
- Many pointers in `qed_hwfn` and `qed_dev` are conditionally allocated; consumers must respect feature flags and initialization state.
- Resource macros assume valid enum indexes and initialized resource arrays.
- CMT and affinity macros encode subtle multi-engine behavior; selecting the wrong hwfn can misroute protocol operations.
- Doorbell address calculation depends on hardware constants and CID/DEMS encoding; errors can ring the wrong context.

## Test Signals
Coverage should include full QED build matrices, sparse and W=1 builds, probe on BB/AH/K2-like devices or emulation, multi-hwfn/CMT paths, SR-IOV enabled/disabled builds, RDMA/storage optional builds, link and bandwidth update paths, firmware recovery, debug dump allocation, doorbell recovery, and LLH filter operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_chain.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_chain.c

## Purpose
This file implements allocation, initialization, and freeing of QED DMA-backed chains. Chains are ring-like queues used by QED slowpath, LL2, storage, RDMA, and other subsystems. The implementation supports three layout modes: a single contiguous DMA page, a next-pointer linked list of DMA pages, and a page-block-list (PBL) table that points to DMA pages.

## Important APIs and Functions
- `qed_chain_alloc()` is the exported allocator. It fills default page size, computes page count, sanity-checks capacity, initializes the `struct qed_chain`, allocates backing memory for the selected mode, resets chain cursors, and frees partial allocations on failure.
- `qed_chain_free()` is the exported destructor. It dispatches to mode-specific free helpers and clears the chain base virtual/physical addresses.
- `qed_chain_init()` zeroes and initializes chain geometry such as element size, page size, page count, element counts, masks, capacity, and optional external PBL table metadata.
- `qed_chain_alloc_next_ptr()` allocates each page separately, embeds `struct qed_chain_next` at the unusable tail area of each page, and links the last page back to the first.
- `qed_chain_alloc_single()` allocates one coherent page and resets the chain.
- `qed_chain_alloc_pbl()` allocates an address table with `vzalloc()`, optionally allocates an internal coherent PBL table, allocates each coherent data page, writes page physical addresses into the PBL, and stores virtual/DMA addresses in `pp_addr_tbl`.
- `qed_chain_alloc_sanity_check()` rejects zero-size chains, invalid count types, and chains whose rounded actual size exceeds the selected counter width.

## Control Flow
Allocation starts by defaulting `params->page_size` to `QED_CHAIN_PAGE_SIZE` when unset. Single mode always uses one page; other modes compute page count from requested elements, element size, page size, and mode-specific unusable elements. After sanity checks, `qed_chain_init()` establishes geometry and optional external PBL state. The mode switch then allocates memory. On success, the chain is ready for producer/consumer helpers in `linux/qed/qed_chain.h`; on failure, `qed_chain_free()` releases any partially allocated pages/tables.

Freeing reverses the selected layout. Next-pointer mode walks from the first page through embedded next pointers and frees coherent pages until a null virtual address or `page_cnt` pages. Single mode frees the one coherent page if present. PBL mode walks `pp_addr_tbl`, frees each data page until an empty entry, frees the internal PBL table unless the caller supplied an external one, vfree()s the address table, and nulls it.

## State and Persistence
State persists in `struct qed_chain`: geometry fields, capacity/size, base virtual and DMA address, PBL table virtual/physical/size, external-PBL flag, and per-page virtual/DMA address table for PBL mode. Hardware persistence is indirect: coherent DMA pages and PBL tables are intended to be consumed by device firmware/hardware rings. The allocator does not itself register chains with firmware; users pass the initialized chain to QED subsystems.

## Dependencies and Integration Points
The file includes `linux/qed/qed_chain.h` for chain structures and geometry/reset macros, `linux/dma-mapping.h` for coherent DMA allocation, `linux/vmalloc.h` for virtual address tables, and `qed_dev_api.h` for exported prototypes and `struct qed_dev`. Callers include SPQ/EQ/ConSQ, LL2, iSCSI, NVMe/TCP, and other QED modules that need DMA queue storage.

## Risks and Edge Cases
- `qed_chain_alloc_pbl()` can return `-EOVERFLOW` after allocating `pp_addr_tbl` or an internal PBL table without locally freeing before returning; the top-level allocator only calls `qed_chain_free()` after mode allocators return through the common failure path, so direct early returns inside the helper must be checked carefully for leaks.
- Geometry depends on element size, page size, and unusable next-pointer elements; invalid parameters can silently reduce usable capacity if callers misunderstand the mode.
- External PBL mode trusts caller-provided table virtual/physical addresses and table capacity.
- Next-pointer free relies on valid embedded next pointers; memory corruption in a chain page can affect cleanup.
- Count type checks use rounded actual chain size, which can reject requests near `U16_MAX` or `U32_MAX` after page rounding.

## Test Signals
Tests should allocate and free all modes with small, exact-page, multi-page, and near-limit element counts; verify capacity and cursor reset behavior; inject DMA allocation failures at each page; exercise external and internal PBL modes; run with DMA API debug, KASAN, and kmemleak; and cover real callers such as SPQ/EQ/LL2/storage queues through probe/open/teardown cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_chain.c -->
