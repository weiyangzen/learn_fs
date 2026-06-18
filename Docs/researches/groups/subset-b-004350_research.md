# subset-b-004350 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.h

## Purpose
Defines the ATL1E/L1E hardware contract used by the Atheros Attansic L1E Ethernet driver. The file is almost entirely declarative: it exposes hardware helper prototypes, PCI/MMIO register offsets, bit masks, interrupt masks, PHY register fields, WOL fields, DMA queue controls, RSS fields, descriptor base-address registers, and MAC statistic register ranges consumed by `atl1e_main.c`, `atl1e_hw.c`, ethtool support, and module option handling.

## Important APIs, Types, and Functions
The exported prototypes are the hardware abstraction surface: `atl1e_reset_hw`, `atl1e_init_hw`, `atl1e_read_mac_addr`, `atl1e_phy_commit`, `atl1e_get_speed_and_duplex`, `atl1e_auto_get_fc`, multicast helpers `atl1e_hash_mc_addr` and `atl1e_hash_set`, MDIO helpers `atl1e_read_phy_reg` and `atl1e_write_phy_reg`, EEPROM helpers, power-saving helpers, `atl1e_phy_init`, `atl1e_force_ps`, and `atl1e_restart_autoneg`.

The important register families are PCI power/capability and VPD registers (`REG_PM_CTRLSTAT`, `REG_DEVICE_CTRL`, `REG_VPD_CAP`, `REG_VPD_DATA`), SPI/TWSI flash registers (`REG_SPI_FLASH_CTRL`, opcode registers, `REG_TWSI_CTRL`), global MAC/GPHY control (`REG_MASTER_CTRL`, `REG_GPHY_CTRL`, `REG_IDLE_STATUS`, `REG_MDIO_CTRL`, `REG_PHY_STATUS`), MAC programming (`REG_MAC_CTRL`, `REG_MAC_STA_ADDR`, `REG_RX_HASH_TABLE`, `REG_MTU`, `REG_WOL_CTRL`), descriptor/DMA/RX-page programming (`REG_DESC_BASE_ADDR_HI`, `REG_TPD_BASE_ADDR_LO`, `REG_HOST_RXF*`, `REG_DMA_CTRL`, `REG_MB_TPD_PROD_IDX`), interrupt status/mask definitions (`REG_ISR`, `REG_IMR`, `IMR_NORMAL_MASK`, `ISR_TX_EVENT`, `ISR_RX_EVENT`), and PHY/MII-specific fields (`MII_AT001_*`).

## Control Flow and State
There is no runtime control flow in this header. Its state model is hardware-backed: driver state persists in MMIO registers, PHY registers, EEPROM/VPD/SPI contents, descriptor rings referenced by DMA base-address registers, interrupt status bits, and MAC statistic counters. Some definitions encode multi-register state: the MAC address spans two station-address words, multicast filtering spans two hash table registers, RX pages have high/low base plus valid/write-offset registers, and WOL pattern state spans control and length registers.

## Dependencies and Integration Points
Includes `linux/types.h` and `linux/mii.h`, forward-declares `struct atl1e_adapter` and `struct atl1e_hw`, and is included through the ATL1E driver headers. It integrates with the PCI core through config-space offsets, with the Linux netdev stack through speed/duplex/VLAN/checksum semantics, with MDIO/MII helper definitions, and with the DMA API by defining 32-bit low/high address programming contracts.

## Risks
This file is a hardware ABI. Incorrect offsets, masks, shifts, or interrupt grouping can produce silent packet loss, broken DMA, unhandled interrupts, invalid PHY negotiation, bad WOL behavior, or register writes to reserved locations. Several definitions are shared assumptions with `atl1e_main.c`; for example `IMR_NORMAL_MASK` controls which interrupts the ISR can observe, and `REG_HOST_RXF*_PAGE*` arrays in the main file rely on these offsets matching the hardware page layout. The single high-address register model means 64-bit DMA support is deliberately constrained elsewhere; any future change to DMA masks must honor this register layout.

## Test Signals
Useful signals are compile coverage for `atl1e_main.c`, `atl1e_hw.c`, and ethtool code; probe/open on supported L1E/L2E devices; link negotiation at 10/100/1000; interrupt storms or missing RX/TX completions; register dump comparisons against known hardware; WOL suspend/resume tests; multicast/promiscuous filtering; VLAN stripping/insertion; and DMA traffic tests across ring wrap and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_main.c

## Purpose
Implements the Linux PCI/netdev driver for Atheros/Attansic ATL1E-class Ethernet controllers. It owns PCI probe/remove, netdev setup, open/close, reset recovery, DMA ring allocation, device configuration, interrupt handling, NAPI RX polling, TX mapping/offloads, PHY link management, suspend/resume/WOL, and PCI error recovery. Hardware-specific register definitions and lower-level helpers come from `atl1e.h` and `atl1e_hw.h`.

## Important APIs, Types, and Functions
Driver registration is via `atl1e_pci_tbl`, `atl1e_driver`, and `module_pci_driver`. Netdev operations are collected in `atl1e_netdev_ops`: `atl1e_open`, `atl1e_close`, `atl1e_xmit_frame`, `atl1e_get_stats`, `atl1e_set_multi`, `atl1e_set_mac_addr`, feature/MTU/ioctl handlers, TX timeout, and optional netpoll.

Lifecycle functions include `atl1e_probe`, `atl1e_init_netdev`, `atl1e_sw_init`, `atl1e_up`, `atl1e_down`, `atl1e_remove`, `atl1e_suspend`, `atl1e_resume`, `atl1e_shutdown`, and PCI AER callbacks `atl1e_io_error_detected`, `atl1e_io_slot_reset`, `atl1e_io_resume`. Ring/resource functions include `atl1e_init_ring_resources`, `atl1e_setup_ring_resources`, `atl1e_free_ring_resources`, `atl1e_init_ring_ptrs`, `atl1e_clean_tx_ring`, `atl1e_clean_rx_ring`, and `atl1e_configure_des_ring`.

Data-path functions include `atl1e_intr`, `atl1e_clean`, `atl1e_clean_rx_irq`, `atl1e_clean_tx_irq`, `atl1e_xmit_frame`, `atl1e_cal_tdp_req`, `atl1e_tso_csum`, `atl1e_tx_map`, and `atl1e_tx_queue`. Link/PHY and feature functions include `atl1e_check_link`, `atl1e_link_chg_event`, `atl1e_link_chg_task`, `atl1e_phy_config`, `atl1e_mii_ioctl`, `atl1e_vlan_mode`, `atl1e_rx_mode`, and `atl1e_set_multi`.

## Control Flow and State
Probe enables the PCI function, forces a 32-bit coherent DMA mask because the hardware has a single shared high-DMA-address register, requests BARs, allocates `net_device` plus `struct atl1e_adapter`, maps BAR0, installs MII/NAPI/timer hooks, applies module options, configures PCI command bits, initializes adapter defaults, initializes the PHY, resets hardware, reads the MAC address, creates reset/link work items, and registers the netdev.

Open initializes ring sizing, allocates one coherent ring block plus TX buffer metadata, requests a shared IRQ, and calls `atl1e_up`. `atl1e_up` initializes hardware, resets ring pointers, restores multicast/VLAN state, writes descriptor/page/register configuration, enables NAPI and interrupts, then triggers a manual interrupt to establish link state. Close and down paths set `__AT_DOWN`, stop the queue, reset MAC, disable NAPI/IRQ/timers, clear carrier, and clean TX/RX resources.

Interrupt control uses `adapter->irq_sem` to avoid nested enable/disable. The ISR reads `REG_ISR`, acknowledges status with `ISR_DIS_INT`, handles fatal PCIe/DMA conditions by scheduling `reset_task`, updates hardware stats on SMB, schedules link work for PHY/manual events, cleans TX completions, and masks RX events before scheduling NAPI. NAPI consumes RX page data until budget, then re-enables RX interrupts.

TX control flow computes descriptor demand, stops the queue if the ring lacks space, programs VLAN/802.3/offload fields, maps head and frags into TPD descriptors with 0x3000-byte segment limits, marks EOP, stores the skb on the last descriptor, writes a memory barrier, and rings `REG_MB_TPD_PROD_IDX`. RX control flow reads the current hardware write offset for the active page, validates sequence numbers, filters hardware-error frames unless `NETIF_F_RXALL`, copies packet bytes into a fresh skb, strips FCS unless requested, applies checksum/VLAN metadata, submits through GRO, advances page offsets, and toggles RX page validity when a page wraps.

Persistent state is split across `struct atl1e_adapter` flags (`__AT_DOWN`, `__AT_RESETTING`, `__AT_TESTING`), link speed/duplex, NAPI and workqueue state, the MDIO spinlock, software ring indices, coherent DMA memory, TX buffer metadata, hardware MMIO registers, PHY registers, and accumulated `hw_stats`.

## Dependencies and Integration Points
Depends on Linux PCI, DMA mapping, netdevice, NAPI, IRQ, timer, workqueue, MII ioctl, VLAN accel, checksum/TSO/GSO, ethtool setup, and optional netpoll APIs. It integrates with lower-level ATL1E hardware functions declared in `atl1e_hw.h`, option parsing from `atl1e_param.c`, ethtool ops via `atl1e_set_ethtool_ops`, and the kernel PCI error-handling framework.

## Risks
The largest risks are DMA and ring correctness. The hardware single-high-DMA-register constraint is why the driver uses 32-bit DMA; relaxing it would corrupt descriptors/pages. TX mapping unwind paths must preserve `next_to_use` and unmap only the mappings actually created. RX sequence mismatch schedules a full reset, so malformed descriptor sequencing can cause link flaps under load. Copy-based RX is simpler than page recycling but can drop packets under memory pressure. Reset work races are controlled by `__AT_RESETTING`, `__AT_DOWN`, IRQ masking, NAPI disable, and work cancellation; changes to ordering can produce use-after-free, stuck IRQs, or netdev queue hangs. Suspend/WOL paths directly program MAC/PHY while IRQs/resources may be freed, so netif-running checks must remain consistent.

## Test Signals
Exercise probe/remove, open/close, MTU changes, tx timeout reset, PCI error recovery, suspend/resume with and without WOL, netpoll if enabled, ethtool feature toggles for VLAN/RXALL/RXFCS, MII ioctl register access, multicast/promiscuous/allmulti filtering, TSO/checksum/VLAN TX, RX checksum/VLAN delivery, heavy bidirectional traffic across ring wrap, forced DMA mapping failures, link up/down events, and interrupt moderation behavior. Regression clues include queue stuck after TX_BUSY, repeated `pcie phy linkdown` or `PCIE DMA RW error`, RX sequence errors, missed carrier updates, and stats counters not moving after traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_param.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_param.c

## Purpose
Implements ATL1E module parameter parsing and validation. It converts per-board integer module options into adapter defaults for TX descriptor count, RX memory size, interrupt moderation, and media type before the main driver initializes rings and hardware configuration.

## Important APIs, Types, and Functions
The `ATL1E_PARAM` macro declares integer module-parameter arrays for up to `ATL1E_MAX_NIC` boards. Defined parameters are `tx_desc_cnt`, `rx_mem_size`, `media_type`, and `int_mod_timer`. `struct atl1e_option` describes an option as enable/range/list with default and bounds. `atl1e_validate_option` applies defaulting, range/list checks, and netdev logging. `atl1e_check_options` is the exported entry point called during probe.

## Control Flow and State
`atl1e_check_options` uses `adapter->bd_number` to select the per-board array element. Missing or unset entries fall back to defaults. Validated values are written into runtime adapter state: `adapter->tx_ring.count`, `adapter->rx_ring.page_size`, `adapter->hw.imt`, and `adapter->hw.media_type`. TX descriptor count is masked with `0xFFFC`, aligning the count down to a multiple of four. RX memory size is converted from KB to bytes. Invalid values are logged and replaced with defaults.

State persists only in static module parameter arrays and in fields of the probed adapter. There is no dynamic allocation or hardware access in this file; hardware effects occur later when `atl1e_main.c` sizes rings and writes interrupt/link configuration.

## Dependencies and Integration Points
Includes `linux/netdevice.h` and `atl1e.h`. Integrates with the module loader through `module_param_array_named` and `MODULE_PARM_DESC`, and with probe through `atl1e_check_options(adapter)`. The media type constants and flow-control defaults are consumed by hardware link setup in other ATL1E files.

## Risks
The parameter arrays are fixed-size and board-indexed. Boards beyond `ATL1E_MAX_NIC` are logged as defaulted, but the code still checks `num_* > bd`; maintaining that guard is important for array safety. Range comments do not exactly match all constants, so behavior should be based on constants rather than comments. The aligned-down TX descriptor count may surprise users near the minimum and should stay compatible with ring-size hardware requirements. Too-small RX memory or interrupt moderation settings can affect throughput/latency and expose RX page wrap behavior in `atl1e_main.c`.

## Test Signals
Load the module with default parameters, with valid per-board arrays, with out-of-range values, and with more NICs than configured. Confirm logs report validation/defaulting, ring sizes reflect expected values, interrupt moderation register programming uses `hw.imt`, and forced media settings affect link advertisement/reset behavior. Build tests should catch changes to media constants or adapter field names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/Makefile

## Purpose
Defines Kbuild objects for the Attansic/Atheros `atlx` Ethernet drivers. It conditionally builds `atl1.o` for `CONFIG_ATL1` and `atl2.o` for `CONFIG_ATL2`.

## Important APIs, Types, and Functions
There are no C APIs or runtime functions. The important declarations are `obj-$(CONFIG_ATL1) += atl1.o` and `obj-$(CONFIG_ATL2) += atl2.o`.

## Control Flow and State
Build-time only. Kconfig symbols select which object files become part of the kernel or modules. No runtime state is created here.

## Dependencies and Integration Points
Integrated with Linux Kbuild and the surrounding `drivers/net/ethernet/atheros` build. `atl1.o` compiles `atl1.c`, which directly includes `atlx.c` as a shared helper implementation. `atl2.o` is another driver in the same folder and shares common `atlx` definitions.

## Risks
The Makefile is small but controls driver inclusion. A wrong object mapping would silently drop driver support or build the wrong module. Because `atl1.c` includes `atlx.c` textually, common-helper compilation assumptions differ from normal multi-object linking; splitting the objects would require symbol/export changes rather than a Makefile-only edit.

## Test Signals
Build with `CONFIG_ATL1=m/y`, `CONFIG_ATL2=m/y`, both enabled, and both disabled. Confirm the expected modules/objects are produced and no duplicate-symbol issues appear from the textual `atlx.c` inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl1.c

## Purpose
Implements the Attansic/Atheros L1 Gigabit Ethernet PCI driver. It provides PCI probe/remove, hardware reset/initialization, EEPROM/SPI MAC-address discovery, PHY setup, link management, descriptor ring allocation, RX/TX data paths, interrupt/NAPI handling, suspend/resume/WOL, and ethtool operations. It also textually includes `atlx.c`, using common helper macros in `atl1.h` to share netdev feature, multicast, VLAN, ioctl, IRQ, and link-change helpers.

## Important APIs, Types, and Functions
Driver registration is via `atl1_pci_tbl`, `atl1_driver`, and `module_pci_driver`. Netdev operations in `atl1_netdev_ops` map to `atl1_open`, `atl1_close`, `atl1_xmit_frame`, `atlx_set_multi`, `atl1_set_mac`, `atl1_change_mtu`, `atlx_fix_features`, `atlx_set_features`, `atlx_ioctl`, `atlx_tx_timeout`, and optional poll controller.

Hardware and PHY helpers include `atl1_reset_hw`, `atl1_check_eeprom_exist`, `atl1_read_eeprom`, `atl1_spi_read`, `atl1_get_permanent_address`, `atl1_read_mac_addr`, `atl1_read_phy_reg`, `atl1_write_phy_reg`, `atl1_phy_leave_power_saving`, `atl1_phy_reset`, `atl1_phy_setup_autoneg_adv`, `atl1_setup_link`, `atl1_init_flash_opcode`, `atl1_init_hw`, `atl1_get_speed_and_duplex`, `atl1_set_mac_addr`, and `atl1_pcie_patch`.

Resource and datapath helpers include `atl1_setup_ring_resources`, `atl1_free_ring_resources`, `atl1_init_ring_ptrs`, `atl1_alloc_rx_buffers`, `atl1_intr_rx`, `atl1_intr_tx`, `atl1_tpd_avail`, `atl1_tso`, `atl1_tx_csum`, `atl1_tx_map`, `atl1_tx_queue`, `atl1_update_mailbox`, `atl1_rings_clean`, `atl1_sched_rings_clean`, and `atl1_intr`. Ettool support includes stats strings, link settings, WOL, message level, register dump, ringparam, pauseparam, nway reset, and stats callbacks.

## Control Flow and State
Probe enables PCI, sets a 32-bit DMA mask for the same shared-high-address hardware reason as ATL1E, requests regions, allocates `net_device` and `struct atl1_adapter`, maps BAR0, reads hardware revision, sets default ring counts, installs MII/NAPI/netdev/ethtool hooks, initializes adapter defaults, resets hardware, discovers or generates a MAC address, parses interrupt moderation options, initializes hardware and link advertising, applies PCIe workarounds, initializes timers/work items, registers the netdev, and applies the VIA INTx workaround.

Open allocates descriptor resources and calls `atl1_up`. `atl1_setup_ring_resources` allocates software buffer metadata for TPD/RFD rings and one coherent DMA block containing TPD, RFD, RRD, CMB, and SMB regions with 8-byte alignment. `atl1_up` restores multicast/VLAN state, initializes ring indices, allocates RX buffers, configures all descriptor base addresses, mailbox, MAC timing, flow control, TX/RX queues, DMA, CMB/SMB timers, then enables MSI if possible, requests IRQ, enables NAPI/interrupts, checks link, and starts the queue. `atl1_down` disables NAPI, queue, timer, IRQ/MSI, resets hardware, clears carrier and link state, and cleans rings.

The RX path uses hardware RFD descriptors for packet buffers and RRD descriptors for returned packets. `atl1_alloc_rx_buffers` allocates aligned skb-backed buffers, maps them for DMA, fills RFD descriptors, and advances producer state. `atl1_intr_rx` consumes valid RRDs up to budget, handles bad multi-buffer RRDs, unmaps the referenced RFD buffer, trims FCS, applies checksum/VLAN metadata, submits via `netif_receive_skb`, clears descriptor validity, refills RX buffers, and updates the mailbox. The TX path counts required TPDs, handles TSO and checksum offload fields, maps the skb head/frags in `ATL1_MAX_TX_BUF_LEN` chunks, writes descriptors, advances producer state, and updates the mailbox.

Interrupts are CMB-centered: `atl1_intr` reads `adapter->cmb.cmb->int_stats`, clears/acknowledges ISR bits, updates SMB stats, handles fatal PCIe/DMA errors by disabling IRQ and scheduling reset work, schedules link work on GPHY changes, and schedules NAPI for CMB RX/TX events while masking RX/TX interrupts. `atl1_rings_clean` drains RX/TX and reenables normal interrupts when polling completes. Link reconfiguration uses immediate carrier updates plus a timer (`phy_config_timer`) to retry autonegotiation when the resolved link does not match forced media settings.

Persistent driver state lives in `struct atl1_adapter`: ring descriptors and indices, CMB/SMB DMA blocks, soft stats, WOL flags, link speed/duplex, message level, interrupt enabled state, timers/work, lock state, and `struct atl1_hw`. Persistent hardware state lives in MMIO registers, PHY registers, VPD/SPI/BIOS MAC storage, descriptor rings, and CMB/SMB memory written by the device.

## Dependencies and Integration Points
Depends on Linux PCI, DMA mapping, netdevice, NAPI, IRQ/MSI, ethtool, MII, VLAN, checksum/GSO/TSO, timers, workqueues, and suspend/resume APIs. It includes `atl1.h`, which includes `atlx.h`; `atl1.c` also includes `atlx.c` directly, so common helpers are compiled in this translation unit and use macro aliases such as `atlx_adapter -> atl1_adapter`.

## Risks
The textual include of `atlx.c` is fragile: helper prototypes are static, macro aliases must match the L1 types, and build/link behavior differs from normal object sharing. DMA ring layout depends on one coherent block and correct 8-byte alignment; off-by-one or alignment changes can corrupt descriptor/CMB/SMB state. `atl1_free_ring_resources` assumes resources exist, so open-error paths must not call it after partial allocation unless fields are valid. The TX DMA error unwind must only unmap descriptors mapped in the current packet. The RX path has special handling for bad RRDs and hardware checksum bugs on fragmented IP packets; over-cleaning allocation flags or trusting invalid RRD fields risks buffer reuse corruption. Reset work runs from interrupt/error paths and calls down/up without an explicit reset bit comparable to ATL1E, so ordering with close/remove matters. Ettool ringparam hot changes temporarily swap old/new ring state and must preserve SMB/CMB fields correctly.

## Test Signals
Run build tests with `CONFIG_ATL1`, probe/remove, repeated open/close, MSI and INTx fallback, suspend/resume with WOL magic, link up/down and forced media settings, ethtool link/ring/pause/WOL/register/stat operations, MTU changes, VLAN TX/RX, TSO and checksum offload, RX under memory pressure, bidirectional traffic across descriptor wrap, TX timeout reset, injected DMA mapping failures, and fatal ISR conditions. Watch for lost CMB interrupts, queue stuck after `NETDEV_TX_BUSY`, RRD buffer count warnings, checksum regressions on fragmented IPv4, and stats drift between SMB and netdev counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl1.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl1.h

## Purpose
Defines the ATL1 driver-specific hardware constants, descriptor formats, statistics blocks, ring structures, hardware state, adapter state, and macro aliases that let the shared `atlx.c` helpers compile against ATL1 types. It is the primary data-model header for `atl1.c`.

## Important APIs, Types, and Functions
The macro aliases map common-helper names to ATL1 symbols, for example `atlx_adapter` to `atl1_adapter`, `atlx_hw` to `atl1_hw`, `atlx_check_link` to `atl1_check_link`, and `atlx_set_mac` to `atl1_set_mac`. Static prototypes declare common helper targets: `atl1_hash_mc_addr`, `atl1_hash_set`, `atl1_set_mac_addr`, `atl1_mii_ioctl`, and `atl1_check_link`.

Important register definitions cover idle status, MDIO timing, MAC control, WOL, SRAM partitioning, descriptor base/ring-size registers, TXQ/RXQ controls, flow-control thresholds, DMA control, CMB/SMB controls, mailbox layout, and ATL1 interrupt masks. Important descriptor and state types are `struct stats_msg_block`, `struct coals_msg_block`, `struct rx_return_desc`, `struct rx_free_desc`, `struct tx_packet_desc`, `struct atl1_ring_header`, `struct atl1_buffer`, `struct atl1_tpd_ring`, `struct atl1_rfd_ring`, `struct atl1_rrd_ring`, `struct atl1_cmb`, `struct atl1_smb`, `struct atl1_sft_stats`, `struct atl1_hw`, and `struct atl1_adapter`.

## Control Flow and State
There is no runtime control flow, but the header defines the state transitions that `atl1.c` implements. RX state moves through RFD buffers, RRD completion descriptors, `next_to_use`/`next_to_clean` indices, `alloced` flags, and mailbox producer/consumer fields. TX state moves through TPD descriptors, `buffer_info` DMA/skb ownership, and CMB-consumer indices. Statistics state is split between hardware-written `stats_msg_block`, driver-accumulated `atl1_sft_stats`, and netdev stats. Link/power state is represented by `atl1_hw` fields such as media type, advertisement registers, PHY configured flag, WOL flags, and MAC address storage.

## Dependencies and Integration Points
Includes Linux ethtool, VLAN, MII, module, skb, spinlock, timer, workqueue, and type headers plus `atlx.h`. It integrates with `atl1.c`, the textually included `atlx.c`, Kbuild through `atl1.o`, ethtool register/stat code, and the Linux netdev/PCI/DMA APIs.

## Risks
This header encodes hardware ABI and in-memory DMA layout. Incorrect descriptor field masks or structure packing can break offloads, VLAN tags, DMA addresses, or RX completion parsing. `struct rx_free_desc` is explicitly packed; removing that would change hardware-visible layout. Ring index types and masks must match hardware register widths. The macro alias layer is risky because common helpers compile as if ATL1 were the `atlx` generic type; renaming struct fields or functions can break helpers in non-obvious ways. Interrupt mask definitions separate normal RX/TX CMB events from fatal/base events; wrong masks can lose interrupts or keep NAPI from reenabling RX/TX.

## Test Signals
Compile `atl1.c` with common `atlx.c` helpers, run sparse/struct layout checks where available, verify descriptor sizes and register masks against hardware expectations, exercise checksum/TSO/VLAN descriptors, validate CMB/SMB DMA updates, run ethtool stat/register dumps, and test interrupt masking under RX/TX load and fatal-error conditions. Build coverage with `CONFIG_ATL1=m/y` is especially important because many declarations are static and only validated through the single translation unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl1.h -->
