# Research report: subset-b-004612

Work item: `subset-b-004612`

Scope:
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.c`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.h`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_init.c`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_io.c`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_main.c`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.c

## Purpose

`qlcnic_hw.c` implements low-level 82xx-oriented hardware access and control-plane helpers for the QLogic qlcnic Ethernet driver. It translates CRB and memory offsets into BAR0 windowed accesses, arbitrates PCIe semaphores, sends firmware request descriptors through TX ring 0, manages station/multicast/MAC-learning filter programming, configures offloads such as RSS/LRO/coalescing/VXLAN-related receive modes indirectly through firmware, and exposes suspend/resume/shutdown hooks used by the main PCI driver.

This file is the bridge between higher-level netdev lifecycle code and device-specific firmware/register mechanisms. Most exported functions are invoked through `struct qlcnic_hardware_ops` or `struct qlcnic_nic_template` assignments in `qlcnic_main.c`.

## Important APIs, Types, And Functions

- `struct qlcnic_ms_reg_ctrl` captures the register set and address/window state needed for 64-bit MS memory agent reads/writes.
- `crb_128M_2M_map[]` and `crb_hub_agt[]` encode the 128M internal CRB address space to 2M BAR0 window mappings for 82xx hardware.
- `qlcnic_pcie_sem_lock()` and `qlcnic_pcie_sem_unlock()` acquire/release hardware semaphores, optionally writing ownership to an ID register. These are used for API and ROM-style serialized access.
- `qlcnic_ind_rd()` and `qlcnic_ind_wr()` provide chip-family aware indirect register reads/writes. 82xx uses firmware dump window registers; 83xx delegates to `qlcnic_83xx_wrt_reg_indirect()`.
- `qlcnic_send_cmd_descs()` queues raw command descriptors on TX ring 0. It checks `__QLCNIC_FW_ATTACHED`, locks the TX queue, enforces descriptor availability, copies descriptors, advances the producer, and rings the firmware producer doorbell.
- `qlcnic_82xx_sre_macaddr_change()`, `qlcnic_nic_add_mac()`, `qlcnic_nic_del_mac()`, `qlcnic_flush_mcast_mac()`, and `qlcnic_82xx_free_mac_list()` maintain the driver's software MAC list and send firmware add/delete events.
- `qlcnic_set_multi()` and `__qlcnic_set_multi()` implement netdev multicast/promiscuous programming, including fallback to accept-all mode when unicast or multicast filter capacity is exceeded.
- `qlcnic_prune_lb_filters()` and `qlcnic_delete_lb_filters()` retire learned loopback/MAC filters from the driver's hash tables and synchronize deletions to firmware.
- `qlcnic_82xx_set_lb_mode()` and `qlcnic_82xx_clear_lb_mode()` coordinate firmware loopback configuration with promisc-mode changes.
- `qlcnic_82xx_set_rx_coalesce()`, `qlcnic_82xx_config_intr_coalesce()`, `qlcnic_82xx_config_hw_lro()`, `qlcnic_82xx_config_rss()`, `qlcnic_82xx_config_ipaddr()`, and `qlcnic_82xx_linkevent_request()` build host-request descriptors for runtime configuration.
- `qlcnic_change_mtu()`, `qlcnic_fix_features()`, and `qlcnic_set_features()` connect netdev feature changes to firmware MTU/LRO settings.
- `qlcnic_82xx_hw_read_wx_2M()` and `qlcnic_82xx_hw_write_wx_2M()` perform direct or windowed CRB accesses with CRB window locking.
- `qlcnic_pci_mem_read_2M()` and `qlcnic_pci_mem_write_2M()` access QDR/DDR/OCM memory using direct OCM windows or the MS memory agent.
- `qlcnic_82xx_get_board_info()` reads board metadata from ROM and maps board types to GbE/XGbE port type.
- `qlcnic_82xx_shutdown()` and `qlcnic_82xx_resume()` provide 82xx power-management hooks.

## Control Flow

Hardware register access first classifies an address as directly mapped or windowed. `qlcnic_pci_get_crb_addr_2M()` returns direct BAR0 addresses when possible, otherwise selects the CRB indirect aperture; read/write wrappers then serialize updates with `ahw->crb_lock` plus the CRB window lock before touching the aperture.

Firmware command submission is descriptor based. Callers fill `struct qlcnic_nic_req`, cast it to `struct cmd_desc_type0`, and submit it with `qlcnic_send_cmd_descs()`. The send helper uses TX ring 0, stops and restarts the queue around low descriptor availability, updates `tx_ring->producer`, and rings `qlcnic_update_cmd_producer()`. There is no synchronous response handling in this file for these descriptor commands; failures are mostly submission failures.

MAC filter programming flows from netdev state into firmware. `qlcnic_set_multi()` dispatches to SR-IOV VF handling or `__qlcnic_set_multi()`. The latter ensures station and broadcast addresses, computes a miss mode from promisc/allmulti/filter counts, optionally flushes and re-adds multicast filters, handles unicast address overflow by enabling accept-all, and toggles driver/RX MAC learning when accept-all mode is required.

Memory access uses a separate path from CRB register access. `qlcnic_pci_mem_read_2M()` and `qlcnic_pci_mem_write_2M()` reject unaligned or out-of-range addresses, set memory-agent registers, poll `TA_CTL_BUSY`, and then read or write 64-bit halves. OCM0 gets a direct windowed path through `qlcnic_pci_mem_access_direct()`.

Power management follows main driver state. Shutdown detaches the netdev, cancels IDC work, brings the interface down if running, clears driver state, and enables wakeup if WOL is supported. Resume restarts firmware, reopens the interface if needed, restores IP address notifications, attaches the netdev, and schedules firmware health polling.

## State And Persistence Behavior

Persistent driver state touched here includes `adapter->mac_list`, learned filter hash tables (`adapter->fhash`, `adapter->rx_fhash`), `adapter->flags`, `adapter->ahw->coal`, link/beacon/port identity fields, and feature-related bits such as `adapter->rx_csum`. Device-persistent state is held in firmware-visible CRB/shared registers, hardware semaphores, board ROM contents, and mailbox/descriptor commands consumed by firmware.

The file uses `adapter->ahw->crb_lock` for CRB window serialization, `adapter->ahw->mem_lock` for memory-agent and CAMQM access, per-filter spinlocks for MAC-learning hash tables, and netdev TX queue locks for descriptor command submission.

## Dependencies And Integration Points

The file depends on definitions from `qlcnic.h`, `qlcnic_hdr.h`, firmware command opcodes, descriptor layouts, PCI BAR mappings, Linux netdev feature APIs, VLAN/multicast lists, DMA-safe MMIO accessors, and chip-family predicates such as `qlcnic_82xx_check()` and `qlcnic_83xx_check()`.

It integrates with `qlcnic_main.c` through `qlcnic_hw_ops` and `qlcnic_ops`, with `qlcnic_io.c` through MAC-learning filter updates, with `qlcnic_init.c` through ROM/firmware and memory access helpers, and with ethtool/sysfs paths that request coalescing, LRO, RSS, LED, beacon, and CRB access.

## Risks

- `qlcnic_config_bridged_mode()` toggles `QLCNIC_BRIDGE_ENABLED` with XOR after sending the command, even if `rv` is nonzero. That can desynchronize software state from firmware state.
- Descriptor command submission depends on TX ring 0 and `__QLCNIC_FW_ATTACHED`; control-plane operations can fail or be delayed when the TX queue is saturated or firmware attachment state is wrong.
- Several MAC-list paths call firmware while walking or mutating software lists. Failed delete/add commands can leave software and firmware filters inconsistent.
- Windowed register and memory-agent paths rely on strict locking. Any new caller bypassing these helpers can corrupt the shared CRB or OCM window.
- `qlcnic_82xx_hw_read_wx_2M()` takes an `err` argument but does not set it on invalid offset, instead returning `-1`; callers must not assume `*err` is authoritative.
- LRO cleanup and feature toggling are only loosely transactional; `qlcnic_set_features()` flips `netdev->features` before firmware LRO configuration succeeds.

## Test Signals

Useful signals include successful probe/start logs, firmware version and board-type detection, `ethtool -k` LRO/RXCSUM/TSO feature toggles, `ethtool -C` coalescing changes, `ip link set promisc/allmulti` filter transitions, multicast/unicast filter overflow behavior, MTU changes, LED/beacon commands, suspend/resume, and firmware reset recovery. Error counters of interest include `xmit_off`, `tx_dma_map_error`, MAC filter limit overruns, and kernel logs for semaphore timeout, invalid CRB offsets, failed memory agent reads/writes, and LRO/RSS/coalesce command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.h

## Purpose

`qlcnic_hw.h` is the public hardware-command interface for the qlcnic driver. It defines shared register indexes, access macros, firmware mailbox command IDs, mailbox/event constants, ring limits, and function prototypes for 82xx hardware operations and common helper entry points used by the rest of the driver.

The header is not just declarations: it defines the vocabulary that ties the main PCI/netdev lifecycle, firmware initialization, mailbox code, ethtool/sysfs paths, and data path together.

## Important APIs, Types, And Constants

- `enum qlcnic_regs` defines indexes into `ahw->reg_tbl` for common shared registers such as PEG halt status, heartbeat, firmware capabilities, driver/device state, firmware version, API version, and flash lock/unlock registers.
- `QLC_SHARED_REG_RD32()` and `QLC_SHARED_REG_WR32()` access BAR0 offsets through the shared register table.
- `QLCRDX()` and `QLCWRX()` access extended BAR0 offsets through `ahw->ext_reg_tbl`.
- `QLCNIC_CMD_*` constants enumerate firmware mailbox commands for RX/TX context creation, MAC/VLAN changes, PCI/NIC info, eSwitch, DCB, statistics, interrupts, RSS, LED, link status, NIC function init/stop, driver version, encapsulation, and other control operations.
- Interrupt constants such as `QLCNIC_INTRPT_INTX`, `QLCNIC_INTRPT_MSIX`, `QLCNIC_INTRPT_ADD`, and `QLCNIC_INTRPT_DEL` encode firmware interrupt configuration actions.
- MAC command constants such as `QLCNIC_GET_CURRENT_MAC`, `QLCNIC_SET_STATION_MAC`, and `QLCNIC_GET_DEFAULT_MAC` define mailbox MAC-address operations.
- Mailbox event constants such as `QLCNIC_MBX_LINK_EVENT`, `QLCNIC_MBX_BC_EVENT`, `QLCNIC_MBX_COMP_EVENT`, and SFP/DCBX events define async message classes.
- `struct qlcnic_mailbox_metadata` describes a mailbox command's ID and input/output argument counts.
- `QLCNIC_GET_OWNER()`, `QLCNIC_SET_OWNER`, `QLCNIC_CLR_OWNER`, `QLCNIC_MBX_TIMEOUT`, `QLCNIC_MBX_RSP_OK`, and `QLCNIC_MBX_ASYNC_EVENT` support mailbox ownership and response handling.
- Ring limits include `QLCNIC_MAX_HW_TX_RINGS`, `QLCNIC_MAX_HW_VNIC_TX_RINGS`, `QLCNIC_MAX_TX_RINGS`, and `QLCNIC_MAX_SDS_RINGS`.
- Prototypes export 82xx operations for register/memory access, NAPI, promiscuous mode, MAC learning, coalescing, RSS, LRO, IP notification, link events, loopback, CRB access, mailbox command issue/allocation, context creation/destruction, board info, LEDs, function number, API locking, shutdown/resume, and firmware dump helpers.

## Control Flow Role

The header enables indirection-heavy control flow. `qlcnic_main.c` builds `struct qlcnic_hardware_ops` and `struct qlcnic_nic_template` using prototypes declared here. Higher-level code normally calls generic wrappers or function pointers, while this header declares the 82xx concrete implementations. For register access, callers use macros that turn enum indexes into BAR0 offsets, so the same caller code can work after family-specific register tables are installed.

Mailbox command constants flow into command allocation and issue helpers outside this header. A caller chooses a `QLCNIC_CMD_*` value, allocates `struct qlcnic_cmd_args`, populates arguments, and uses the hardware operation's mailbox function.

## State And Persistence Behavior

The header has no mutable runtime state, but it defines names for persistent hardware state held in device registers and firmware. The shared register enum covers durable coordination state such as driver active masks, device state, driver reset/quiesce state, NPAR state, firmware image validity, firmware API level, and flash lock ownership. These are used across probe, reset, suspend/resume, AER recovery, and firmware health polling.

## Dependencies And Integration Points

This header depends on common qlcnic structures declared elsewhere (`struct qlcnic_adapter`, `struct qlcnic_hardware_context`, `struct qlcnic_host_sds_ring`, `struct qlcnic_host_tx_ring`, and others). It is included by implementation files such as `qlcnic_hw.c`, `qlcnic_init.c`, and `qlcnic_main.c`.

It integrates with Linux networking through prototypes that use `struct net_device`, `struct ethtool_coalesce`, `netdev_features_t`, `struct pci_dev`, and NAPI-related ring structures. It also integrates with firmware dump support through `struct qlcnic_fw_dump` and template/cache helper prototypes.

## Risks

- The register macros do no bounds checking on enum indexes. A bad enum value or mismatched register table can produce an invalid MMIO access.
- Many command IDs are reused or close in value across chip families; wrong command selection can produce firmware-level misconfiguration that the compiler cannot catch.
- Prototype declarations expose many 82xx-specific helpers globally within the driver, increasing the chance of family-specific operations being called on the wrong adapter unless guarded by chip checks or function tables.
- Ring-limit constants must remain aligned with firmware and descriptor allocation logic. Incorrect values can break MSI-X vector calculation, queue counts, or firmware context creation.

## Test Signals

Compile-time test signals include successful builds with all declarations matching their definitions. Runtime signals include correct shared-register reads during probe, successful mailbox command allocation/issue for commands defined here, correct MSI-X/ring sizing, and absence of invalid MMIO faults during reset or firmware state transitions. Feature tests for RSS, LRO, LED, link events, MAC/VLAN changes, and context create/destroy exercise the constants and prototypes declared in this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_init.c

## Purpose

`qlcnic_init.c` handles software ring-buffer allocation/release, ROM/flash reads, hardware pre-initialization from ROM CRB tables, firmware readiness checks, firmware image selection/validation/loading, and firmware heartbeat/reset decision helpers for the qlcnic driver. It is the initialization support layer used by `qlcnic_main.c` before the netdev can attach and by reset recovery when firmware must be reloaded.

## Important APIs, Types, And Functions

- `struct crb_addr_pair` stores ROM-provided CRB initialization address/data pairs.
- `crb_addr_xform[]`, `crb_addr_transform_setup()`, and `qlcnic_decode_crb_addr()` translate internal Phantom CRB addresses from ROM tables to PCI CRB offsets.
- `qlcnic_alloc_sw_resources()` allocates RDS rings, RX buffer arrays, initializes free lists, and binds SDS rings to IRQs and TX rings.
- `qlcnic_free_sw_resources()`, `qlcnic_release_rx_buffers()`, `qlcnic_reset_rx_buffers_list()`, and `qlcnic_release_tx_buffers()` tear down or reset software buffer ownership and DMA mappings.
- `qlcnic_wait_rom_done()`, `do_rom_fast_read()`, `do_rom_fast_read_words()`, `qlcnic_rom_fast_read()`, and `qlcnic_rom_fast_read_words()` implement serialized flash/ROM reads through ROMUSB registers and the ROM lock.
- `qlcnic_pinit_from_rom()` halts hardware blocks, reads CRB init tables from ROM, filters unsafe registers, writes initialization values, and prepares PEG state.
- `qlcnic_cmd_peg_ready()`, `qlcnic_receive_peg_ready()`, and `qlcnic_check_fw_status()` wait for firmware command and receive PEGs to reach initialized states.
- `qlcnic_setup_idc_param()` reads partition type, physical port, init timeout, and reset acknowledgement timeout from shared registers/ROM.
- `qlcnic_get_flt_entry()` reads flash layout table entries for firmware/bootloader regions.
- `qlcnic_check_flash_fw_ver()` checks on-flash firmware version against `QLCNIC_MIN_FW_VERSION`.
- Unified image helpers (`qlcnic_get_table_desc()`, `qlcnic_validate_header()`, `qlcnic_validate_product_offs()`, `qlcnic_validate_bootld()`, `qlcnic_validate_fw()`, `qlcnic_validate_unified_romimage()`, `qlcnic_get_data_desc()`) parse and validate externally supplied firmware images.
- `qlcnic_get_bootld_offs()`, `qlcnic_get_fw_offs()`, `qlcnic_get_fw_size()`, `qlcnic_get_fw_version()`, and `qlcnic_get_bios_version()` locate and inspect firmware payloads.
- `qlcnic_need_fw_reset()` combines firmware hang, heartbeat, explicit reset, and externally loaded firmware state to decide whether a firmware reload is needed.
- `qlcnic_load_firmware()` writes bootloader and firmware image data into adapter memory using `qlcnic_pci_mem_write_2M()`, then releases PEG reset.
- `qlcnic_request_firmware()` attempts unified firmware from the kernel firmware loader, validates it, and falls back to flash image mode.
- `qlcnic_release_firmware()` releases any loaded firmware blob and clears `adapter->fw`.

## Control Flow

Resource allocation starts with `qlcnic_alloc_sw_resources()`: it creates RDS rings for normal and jumbo receive paths, sizes DMA/SKB buffers, initializes RX buffer handles and free lists, then initializes SDS rings and ties each SDS ring to either its matching TX ring or TX ring 0 depending on multi-TX capability and diagnostic mode. TX ring command-buffer allocation is handled in `qlcnic_main.c`, but TX buffer release lives here.

ROM reads are serialized by `qlcnic_rom_lock()` and `qlcnic_rom_unlock()` from the wider driver. The fast-read path writes ROM address/opcode/count registers, waits for the ROMUSB done bit, clears byte counters, and reads `QLCNIC_ROMUSB_ROM_RDATA`. Multiword reads repeatedly call the single-word routine and store little-endian words into the caller buffer.

Hardware pre-initialization (`qlcnic_pinit_from_rom()`) is a reset-time sequence. It clears command/receive PEG state, disables I2Q and NIU paths, halts SRE/EPG/timers/PEGs, triggers a broad reset that excludes CAM, reads a ROM CRB init table headed by `0xcafecafe`, decodes each CRB address, skips registers that must not be reset or are unsafe, writes remaining CRB values with delay handling, then reinitializes PEG registers and clears halt status.

Firmware selection flows through `qlcnic_request_firmware()`: start as unknown, try unified ROM image via `request_firmware()`, validate product/chip revision/bootloader/firmware extents and version/BIOS compatibility, and fall back to flash ROM image if unavailable or invalid. `qlcnic_load_firmware()` then either copies the external image or reads bootloader from flash layout/legacy offsets and writes 64-bit chunks into adapter memory.

Firmware readiness is checked after load or when another function has already initialized the device. `qlcnic_check_fw_status()` waits for command PEG state to be `PHAN_INITIALIZE_COMPLETE` or `PHAN_INITIALIZE_ACK`, waits for receive PEG state `PHAN_PEG_RCV_INITIALIZED`, and writes an initialize ACK.

## State And Persistence Behavior

The file manipulates software-owned RX buffer arrays, TX command buffers, SDS ring metadata, firmware blob pointers, `adapter->file_prd_off`, `adapter->heartbeat`, `adapter->dev_init_timeo`, `adapter->reset_ack_timeo`, `adapter->need_fw_reset`, and firmware image type. Persistent hardware state includes ROM contents, flash layout table entries, CRB initialization values, PEG state shared registers, firmware image-valid magic, and the firmware image written into device memory.

DMA state is explicitly mapped and unmapped for RX/TX buffers. RX buffers are returned to free lists by clearing SKB ownership and rebuilding lists, while TX buffers are cleaned under `tx_clean_lock`.

## Dependencies And Integration Points

This file depends on `qlcnic.h`, `qlcnic_hw.h`, ROMUSB register definitions, firmware image layout structures (`uni_table_desc`, `uni_data_desc`, flash layout headers), PCI DMA APIs, firmware loader APIs, and memory-write helpers from `qlcnic_hw.c`.

It is called from `qlcnic_main.c` during firmware start, probe, attach/detach, reset recovery, and open/close. It also supports `qlcnic_hw.c` board-info reads and any code that needs ROM fast reads.

## Risks

- `qlcnic_pinit_from_rom()` writes many hardware registers based on ROM data. Incorrect decode, stale ROM contents, or a missing skip rule can leave hardware in a failed state.
- Firmware image parsing uses offsets from the firmware blob; validation checks size boundaries, but future layout changes must keep all offset calculations aligned with firmware format.
- `do_rom_fast_read_words()` increments in 4-byte units and writes `__le32` words; callers must request sensible sizes and aligned buffers.
- RX allocation failures can leave rings partially populated; data path depends on later repost attempts to refill buffers.
- `qlcnic_need_fw_reset()` returns true whenever `adapter->fw` is present, so external firmware selection intentionally forces reload; callers must release firmware after load to avoid repeated reload decisions.
- Heartbeat checks depend on timing constants and shared register updates; a slow or paused firmware can be interpreted as requiring reset.

## Test Signals

Signals include successful firmware load from flash and from `phanfw.bin`, correct fallback when external firmware is missing or invalid, logs for firmware version compatibility, command/receive PEG readiness, ROM lock recovery, successful attach after reset, RX/TX DMA mapping cleanup under interface down/up, and no leaks after repeated open/close. Fault-injection signals include ROM read timeout, bad flash layout entries, unsupported firmware version, allocation failure in ring setup, and firmware heartbeat stall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_io.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_io.c

## Purpose

`qlcnic_io.c` implements the qlcnic packet data path. It builds TX descriptors, maps/unmaps SKB DMA fragments, supports checksum/TSO/VXLAN offloads, handles firmware-assisted MAC learning, processes TX completions, refills RX buffers, parses 82xx and 83xx RX/LRO/status descriptors, dispatches firmware async messages, and wires these operations into NAPI poll handlers and diagnostic receive paths.

## Important APIs, Types, And Functions

- TX descriptor macros (`qlcnic_set_tx_vlan_tci`, `qlcnic_set_tx_flags_opcode`, `qlcnic_set_tx_frags_len`, `qlcnic_set_tx_port`) encode fields in `struct cmd_desc_type0`.
- Status descriptor macros decode owner, opcode, packet length, checksum status, ring handle, VLAN, LRO, and 83xx-specific fields.
- `qlcnic_xmit_frame()` is the netdev TX entry point used by `ndo_start_xmit`.
- `qlcnic_tx_pkt()` builds regular Ethernet/checksum/TSO descriptors and VLAN header templates.
- `qlcnic_tx_encap_pkt()` builds VXLAN encapsulated checksum/LSO descriptors.
- `qlcnic_map_tx_skb()` and `qlcnic_unmap_buffers()` manage DMA mappings for linear and fragmented SKB data.
- `qlcnic_process_cmd_ring()` handles TX completions, unmaps DMA, frees SKBs, advances software consumer, and wakes stopped queues.
- `qlcnic_alloc_rx_skb()`, `qlcnic_post_rx_buffers_nodb()`, and `qlcnic_post_rx_buffers()` allocate/map SKBs and post receive descriptors.
- `qlcnic_process_rxbuf()` unmaps a completed RX buffer and sets checksum state.
- `qlcnic_process_rcv()` and `qlcnic_process_lro()` process 82xx regular and LRO RX completions.
- `qlcnic_83xx_process_rcv()` and `qlcnic_83xx_process_lro()` process 83xx regular and LRO RX completions.
- `qlcnic_process_rcv_ring()` and `qlcnic_83xx_process_rcv_ring()` drain status rings and recycle buffers.
- `qlcnic_handle_fw_message()` handles firmware response descriptors such as link events, loopback responses, and DCB AEN.
- `qlcnic_add_lb_filter()`, `qlcnic_send_filter()`, and `qlcnic_82xx_change_filter()` implement learned MAC filter programming from TX/RX observations.
- NAPI setup helpers (`qlcnic_82xx_napi_add/del/enable/disable`, `qlcnic_83xx_napi_add/del/enable/disable`) bind RX/TX poll functions based on chip family, MSI-X layout, multi-TX support, and SR-IOV VF mode.
- Diagnostic functions (`qlcnic_82xx_process_rcv_ring_diag()`, `qlcnic_83xx_process_rcv_ring_diag()`) consume loopback-test completions.

## Control Flow

TX begins in `qlcnic_xmit_frame()`. It refuses packets if the device is not up, enforces MAC anti-spoofing if configured, selects a TX ring from the SKB queue mapping, adjusts excessive non-TSO fragments by pulling data into the linear area, stops the queue if descriptor availability is low, maps the SKB for DMA, fills buffer addresses and lengths across one or more command descriptors, and then chooses regular or VXLAN encapsulated descriptor formatting. If driver MAC learning is enabled, it may append a firmware MAC filter-change descriptor. Finally it updates TX stats, executes a write memory barrier, and writes the producer doorbell.

Regular TX descriptor building handles VLAN-in-packet, VLAN hardware-accelerated tags, port VLAN insertion, multicast address copy, TSO header copying, and checksum opcode selection for IPv4/IPv6 TCP/UDP. Encapsulated TX handles VXLAN packets, copies outer and inner headers for encapsulated LSO, programs inner/outer header offsets, and records encapsulated offload stats.

TX completion is polled by `qlcnic_process_cmd_ring()`. It compares `sw_consumer` to the firmware-written hardware consumer, unmaps all DMA fragments for each completed SKB, frees the SKB, advances the consumer up to budget, wakes a stopped queue when descriptors recover, and returns whether the ring is fully caught up.

RX completion drains status descriptors until budget or firmware ownership. For each packet descriptor, the code decodes ring and buffer handle, unmaps the RX DMA buffer, applies checksum state, optionally updates MAC-learning filters, sizes/pulls the SKB, validates/strips VLAN tags with port VLAN policy, sets protocol, attaches VLAN tags where needed, and submits to GRO or `netif_receive_skb()` for LRO. Completed buffers are moved to SDS free lists, reallocated, spliced back to RDS free lists, and reposted to hardware.

Firmware messages are encoded as response descriptors interleaved in RX status rings. `qlcnic_handle_fw_message()` reconstructs the message words, dispatches link events into link state/carrier updates, records loopback diagnostic responses, and forwards DCB events.

NAPI control differs by generation. 82xx can use combined RX/TX poll, RX-only poll, and TX-only poll depending on multi-TX and MSI-X. 83xx uses different descriptor parsing and separate TX interrupt handling when TX interrupts are not shared.

## State And Persistence Behavior

Data-path state includes TX producer/software consumer, firmware hardware consumer, TX command buffer SKB/fragment arrays, RDS producer/free lists, SDS consumer/free lists, per-ring NAPI objects, IRQ vector bindings, adapter statistics, link state, loopback diagnostic counters, MAC-learning hash tables, VLAN/PVID settings, and SKB checksum/GSO metadata.

Device-visible persistent state is descriptor-ring memory, MMIO producer/consumer doorbells, interrupt masks, and firmware-programmed MAC filters. DMA mappings are transient but critical; each TX/RX path pairs mapping and unmapping around hardware ownership.

## Dependencies And Integration Points

This file depends on Linux SKB, VLAN, checksum, GRO, NAPI, DMA mapping, IPv4/IPv6, and netdevice queue APIs. It depends heavily on descriptor definitions and ring structures from `qlcnic.h`, and on hardware operation wrappers for enabling/disabling interrupts and changing MAC filters.

Integration points include `qlcnic_main.c` netdev ops (`qlcnic_xmit_frame`), attach/detach lifecycle (NAPI add/del/enable/disable), interrupt handlers that schedule NAPI, firmware context creation that assigns ring CRB addresses, and `qlcnic_hw.c` for MAC filter firmware commands.

## Risks

- Descriptor accounting is subtle for TSO, VLAN TSO templates, and VXLAN LSO because header copies consume extra descriptors before data descriptor producer updates.
- `qlcnic_tx_pkt()` initially writes flags/opcode before `opcode` is finalized and then writes again later; new changes must preserve the final write semantics.
- DMA mapping failure unwind must exactly match the number and type of mappings completed; mistakes leak mappings or unmap invalid DMA addresses.
- RX handle validation prevents out-of-bounds access, but invalid descriptors still consume status entries and increment error counters only in some paths.
- VLAN/PVID policy can drop packets when tagging is disabled and tags do not match `rx_pvid`; this is intentional but easy to misdiagnose as RX loss.
- MAC-learning filter updates are performed in atomic/TX/RX contexts with spinlocks and firmware descriptor commands. Filter hash count and firmware state can diverge on command failure.
- 82xx and 83xx descriptor formats differ; adding shared code without preserving format-specific parsing can break one family.

## Test Signals

Useful signals include traffic across all TX offload modes (plain, checksum partial, TSO, TSO6, VLAN, VXLAN, VXLAN GSO), RX checksum/GRO/LRO behavior, VLAN add/delete and PVID cases, multicast/promiscuous transitions, TX queue stop/wake under stress, NAPI budget behavior, interrupt mode coverage (legacy/MSI/MSI-X), SR-IOV VF receive/transmit, loopback diagnostics, link-event messages, and counters such as `tx_dma_map_error`, `rx_dma_map_error`, `skb_alloc_failure`, `null_rxbuf`, `rxdropped`, `txdropped`, `lro_pkts`, and encapsulation checksum stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_main.c

## Purpose

`qlcnic_main.c` is the central PCI and netdev lifecycle implementation for the qlcnic driver. It declares module parameters and device IDs, registers the PCI driver, probes/removes adapters, selects 82xx/83xx/VF hardware operation tables, configures BAR mappings, firmware startup, interrupt topology, queue counts, netdev features, eSwitch/NPAR policy, open/close attach/detach, reset and firmware health work, PCI AER recovery, power management, VLAN/IP address notifications, and statistics/timeout handling.

## Important APIs, Types, And Functions

- Module parameters: `qlcnic_mac_learn`, `qlcnic_use_msi`, `qlcnic_use_msi_x`, `qlcnic_auto_fw_reset`, and `qlcnic_load_fw_file`.
- `qlcnic_pci_tbl[]` lists supported QLogic physical and VF PCI IDs.
- `qlcnic_reg_tbl[]` maps `enum qlcnic_regs` indexes to 82xx shared register offsets.
- `qlcnic_netdev_ops` wires Linux netdev operations to qlcnic handlers, including open, stop, xmit, stats, RX mode, MAC address, MTU, features, VLAN, FDB, physical port ID, and VXLAN feature checks.
- `qlcnic_ops`, `qlcnic_vf_ops`, and `qlcnic_hw_ops` bind generic driver calls to 82xx or VF-specific implementations.
- Ring/interrupt helpers include `qlcnic_set_tx_ring_count()`, `qlcnic_set_sds_ring_count()`, `qlcnic_setup_tss_rss_intr()`, `qlcnic_enable_msix()`, `qlcnic_82xx_setup_intr()`, `qlcnic_82xx_mq_intrpt()`, and `qlcnic_teardown_intr()`.
- PCI/adapter setup helpers include `qlcnic_setup_pci_map()`, `qlcnic_check_vf()`, `qlcnic_initialize_nic()`, `qlcnic_check_eswitch_mode()`, `qlcnic_setup_netdev()`, `qlcnic_alloc_adapter_resources()`, and `qlcnic_free_adapter_resources()`.
- Firmware lifecycle and reset helpers include `qlcnic_82xx_start_firmware()`, `qlcnic_can_start_firmware()`, `qlcnic_fwinit_work()`, `qlcnic_detach_work()`, `qlcnic_attach_work()`, `qlcnic_check_health()`, and `qlcnic_fw_poll_work()`.
- Interface lifecycle helpers include `qlcnic_attach()`, `qlcnic_detach()`, `__qlcnic_up()`, `qlcnic_up()`, `__qlcnic_down()`, `qlcnic_down()`, `qlcnic_open()`, and `qlcnic_close()`.
- Reset and diagnostic helpers include `qlcnic_reset_context()`, `qlcnic_reset_hw_context()`, `qlcnic_diag_alloc_res()`, and `qlcnic_diag_free_res()`.
- Interrupt handlers include `qlcnic_intr()`, `qlcnic_msi_intr()`, `qlcnic_msix_intr()`, `qlcnic_msix_tx_intr()`, and diagnostic `qlcnic_tmp_intr()`.
- PCI AER and PM hooks include `qlcnic_82xx_io_error_detected()`, `qlcnic_82xx_io_slot_reset()`, `qlcnic_82xx_io_resume()`, generic dispatch wrappers, `qlcnic_shutdown()`, `qlcnic_suspend()`, and `qlcnic_resume()`.
- Address notification helpers under `CONFIG_INET` restore and update IPv4 addresses for base and VLAN devices via firmware IP address commands.

## Control Flow

Module initialization registers netdevice and inetaddr notifiers, then registers the PCI driver. Probe enables the PCI device, checks BAR0, sets a 64-bit DMA mask, requests regions, maps BAR0, allocates the netdev/adapter/hardware context, creates a workqueue, initializes adapter resources and locks, selects chip-specific register/hardware operations, starts firmware, reads MAC and physical port ID, configures DCB and interrupts, discovers active PCI/eSwitch information, sets up netdev features and queue counts, registers the netdev, schedules firmware polling, allocates MAC-learning storage if needed, and registers sysfs/hwmon.

For 82xx startup, `qlcnic_82xx_start_firmware()` coordinates with other PCI functions through shared device state. It calls `qlcnic_can_start_firmware()` to decide whether this function owns firmware initialization, optionally requests external firmware or validates flash firmware, performs ROM pre-init and firmware load if reset is needed, waits for PEG readiness, sets device ready, initializes eSwitch mode and management operations, checks board/options, and clears `need_fw_reset`.

Opening the netdev calls `qlcnic_attach()` and `__qlcnic_up()`. Attach adds NAPI, allocates software and hardware resources, requests IRQs, creates sysfs entries, and notifies UDP tunnel support. Up applies eSwitch port config, creates firmware RX/TX contexts, posts RX buffers, configures MAC filters, MTU, RSS, coalescing, and LRO, sets `__QLCNIC_DEV_UP`, enables NAPI/interrupts, requests link events, and starts TX queues.

Down/close clears `__QLCNIC_DEV_UP`, turns carrier off, disables TX, frees MAC and learned filters, disables promisc, cleans SR-IOV async lists if needed, disables NAPI, destroys firmware contexts, resets RX free lists, and releases TX buffers. Detach removes sysfs, frees hardware resources, releases RX buffers, frees IRQs, deletes NAPI, and frees software resources.

Firmware health polling runs as delayed work. `qlcnic_check_health()` monitors temperature, explicit reset requests, shared device state, heartbeat progress, and context reset requests. On firmware hang or reset state, it marks reset ownership when appropriate, schedules detach/reinit work if auto reset is enabled, and may take firmware dumps. Detach work quiesces the interface and acknowledges reset/quiesce states. Firmware init work waits for all functions to acknowledge, reloads firmware if this function owns reset, then schedules attach work. Attach work waits for NPAR operational state, brings the netdev back up, restores IP address notifications, clears reset bits, updates driver version, and resumes health polling.

Interrupt setup prefers MSI-X, falls back to MSI or legacy based on module parameters and hardware capabilities. MSI-X vector allocation can reduce ring counts and redistribute TX/RX queues. Request/free IRQ logic mirrors whether RX and TX interrupts are shared, split, or diagnostic.

AER recovery detaches the device, cancels health work, brings interfaces down, tears down interrupts, saves PCI state, disables the device, then slot reset re-enables PCI, restarts firmware, rebuilds interrupts, reattaches/reraises the netdev, and resumes polling if the device returns ready.

## State And Persistence Behavior

Driver state spans `adapter->state` bits (`__QLCNIC_DEV_UP`, `__QLCNIC_RESETTING`, `__QLCNIC_START_FW`, `__QLCNIC_AER`, `__QLCNIC_MAINTENANCE_MODE`, multi-TX bits), `adapter->flags` (MSI/MSI-X, eSwitch, firmware hang/reset owner, offload and security flags), queue counts, ring arrays, firmware version, port number, MAC address, DCB state, NPAR/eSwitch tables, VLAN bitmap, learned filter hashes, workqueue/delayed work, and statistics.

Persistent device coordination uses shared CRB registers for driver active references, driver reset/quiesce acknowledgement, device state, NPAR state, IDC version, firmware heartbeat, PEG halt status, firmware version, and operation mode. These registers coordinate multiple functions on the same adapter and survive individual netdev open/close cycles.

Resource persistence is layered: probe/remove own PCI regions, BAR mappings, workqueue, hardware context, netdev, sysfs/hwmon, DCB, and firmware state; attach/detach own NAPI, IRQs, RX/TX software/hardware rings; up/down own firmware contexts, posted RX buffers, link events, and TX queues.

## Dependencies And Integration Points

This file integrates with nearly every driver subsystem: 82xx helpers in `qlcnic_hw.c` and `qlcnic_init.c`, data-path and NAPI helpers in `qlcnic_io.c`, 83xx-specific files, SR-IOV support, DCB support, ethtool/sysfs/hwmon, firmware dump logic, Linux PCI/PM/AER, netdevice, notifier, VLAN, VXLAN UDP tunnel, DMA, interrupt, and workqueue APIs.

The function-pointer tables are the main integration boundary. Generic wrappers elsewhere can call `adapter->ahw->hw_ops` or `adapter->nic_ops` without hard-coding chip family, while probe selects the concrete table based on PCI ID and VF/privilege state.

## Risks

- Reset/firmware coordination is multi-function and timing-sensitive. Incorrect updates to `QLCNIC_CRB_DEV_STATE`, driver active bits, or reset/quiesce acknowledgements can strand other functions waiting for initialization or reset.
- Interrupt fallback changes queue counts. Any code assuming requested ring counts equal active ring counts can break after MSI-X allocation failure.
- Probe has many staged resources and maintenance-mode fallback paths; cleanup ordering must match allocation ordering to avoid leaks, double frees, or registered broken netdevs.
- `qlcnic_alloc_lb_filters_mem()` can allocate `fhash` and then fail allocating `rx_fhash`, leaving partially initialized learning state. Callers mostly tolerate missing heads, but new paths must check allocations.
- `qlcnic_setup_rings()` returns immediately on interrupt setup failure without going through its common `done` path, so reset bits and device attach state require careful review on failures.
- Health polling, AER, suspend/resume, tx timeout, and user-triggered ring changes can all attempt detach/reset flows. The `__QLCNIC_RESETTING` and `__QLCNIC_AER` bits are critical serialization points.
- Netdev feature setup depends on firmware capabilities read earlier. Running feature code before firmware capability initialization would expose unsupported offloads.

## Test Signals

High-value signals include successful probe/remove for each supported PCI ID family and VF mode, open/close cycles, interrupt mode fallback (MSI-X, MSI, legacy), ethtool ring count changes, queue count validation, DCB enablement, eSwitch/NPAR management operations, VLAN/FDB operations, VXLAN tunnel port notification, suspend/resume, AER recovery, firmware health polling/reset recovery, TX timeout recovery, maintenance-mode registration after initialization failure, and module unload cleanup.

Runtime counters and logs to watch include firmware/device state transitions, IDC version mismatch warnings, NPAR operational timeout, MSI-X vector allocation logs, IRQ request failures, firmware hang and PEG halt status logs, temperature panic/warn logs, `Tx timeout` paths, and final stats from `qlcnic_get_stats()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_main.c -->
