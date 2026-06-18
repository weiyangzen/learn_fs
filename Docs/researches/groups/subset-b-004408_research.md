# Research: subset-b-004408

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/cs89x0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/cs89x0.c

## Purpose

`cs89x0.c` is the generic Linux Ethernet driver for Crystal/Cirrus CS8900, CS8920, and CS8920M 10 Mbps NICs. It supports legacy ISA probing/module parameters and a platform-driver binding for MMIO-style devices, then exposes a conventional `net_device` using programmed I/O with optional ISA receive DMA when `CONFIG_ISA_DMA_API` is available.

## Important APIs, Types, and Functions

The main private state is `struct net_local`, which records chip type/revision, selected TX command, EEPROM-derived media/IRQ/DMA configuration, receive mode, current RX interrupt mask, media forcing flags, a spinlock, the mapped packet-page address, and optional DMA buffer state. Register access is centralized in `readwords`, `writewords`, `readreg`, and `writereg`.

Probe and setup paths include `cs89x0_probe1`, `reset_chip`, ISA-specific `cs89x0_ioport_probe`, built-in `cs89x0_probe`, module `cs89x0_isa_init_module`, and platform `cs89x0_platform_probe`. Runtime netdev operations are `net_open`, `net_close`, `net_send_packet`, `net_interrupt`, `net_rx`, `net_get_stats`, `net_timeout`, `set_multicast_list`, and `set_mac_address`. EEPROM/media helpers include `wait_eeprom_ready`, `get_eeprom_data`, `get_eeprom_cksum`, `control_dc_dc`, `send_test_pkt`, `detect_tp`, `detect_aui`, and `detect_bnc`.

## Control Flow

Probe verifies the CS89x0 signature through the packet-page address/data ports, records chip revision, selects the fastest safe TX start command, resets the chip, reads EEPROM-backed MAC/configuration when present, applies boot/module media overrides, derives IRQ and optional DMA settings, installs `net_ops`, and registers the netdev. ISA builds can scan a fixed port list or require an explicit module `io=` parameter; platform builds get IRQ and MMIO resources from `platform_device`.

`net_open` requests or auto-selects an IRQ, allocates and programs optional ISA DMA, writes the station address into `PP_IA`, performs media validation/detection, enables serial RX/TX, configures RX/TX/buffer interrupt masks, enables IRQ/memory/DMA bits, and starts the queue. TX stops the queue, writes `TX_CMD_PORT` and `TX_LEN_PORT`, waits for `READY_FOR_TX_NOW`, uploads the frame words, consumes the SKB, and relies on the TX completion interrupt to wake the queue. RX reads status/length from `RX_FRAME_PORT`, allocates an SKB, copies packet data, sets protocol, and passes it to `netif_rx`.

The interrupt handler drains the hardware ISQ until empty. Receiver events call `net_rx`; transmitter events update TX stats and wake the queue; buffer events handle TX underrun escalation and optional DMA RX frame draining; miss/collision events accumulate counters.

## State and Persistence Behavior

All state is in memory or volatile hardware registers. EEPROM is read but not written. `struct net_local` persists for the netdev lifetime, while IRQ and DMA resources are acquired on open and released on close. `send_underrun` gradually changes `send_cmd` from `TX_NOW` toward safer delayed starts after repeated underruns. Statistics are maintained in `dev->stats` and topped up from `PP_RxMiss`/`PP_TxCol` in `net_get_stats`.

## Dependencies and Integration Points

The driver depends on Linux netdev, platform device, OF match data, ISA I/O region mapping, optional ISA DMA APIs, and CS89x0 register definitions from `cs89x0.h`. It binds OF compatibles `cirrus,cs8900` and `cirrus,cs8920`, and legacy ISA support is controlled by `CONFIG_CS89x0_ISA`; platform support by `CONFIG_CS89x0_PLATFORM`.

## Risks and Edge Cases

Interrupt draining is intentionally unbounded because the chip requires all ISQ events to be read; heavy RX on slow systems can monopolize interrupt time. The open error path mixes IRQ, DMA-buffer, and DMA-channel unwind labels, so failures around DMA allocation/requesting need coverage. PIO TX depends on single-packet queue serialization; waking too early can re-enter while chip memory is unavailable. Media detection uses busy jiffy loops and test-packet loopback behavior, which can be fragile on unusual boards. Optional DMA uses ISA constraints such as low memory and a 128 KiB page boundary check.

## Test Signals

Useful signals include ISA explicit-port probe, platform probe, EEPROM-present/absent boot, forced `media=` settings, IRQ auto-selection, open/close cycles, TX underrun recovery, multicast/promiscuous mode changes, RX error accounting, `netpoll` if enabled, optional ISA DMA RX with wraparound, and cleanup after `request_irq`, DMA allocation, or `register_netdev` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/cs89x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/cs89x0.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/cs89x0.h

## Purpose

`cs89x0.h` is the CS89x0 hardware contract shared by the generic CS89x0 driver and the Macintosh variant. It defines packet-page register offsets, low I/O-port offsets, EEPROM layout, chip IDs, interrupt event encodings, media configuration bits, DMA configuration bits, and receive/transmit status masks.

## Important APIs, Types, and Definitions

The header is macro-only. Important register groups include packet-page identity/EEPROM registers (`PP_ChipID`, `PP_EECMD`, `PP_EEData`), RX/TX/buffer controls (`PP_RxCFG`, `PP_RxCTL`, `PP_TxCFG`, `PP_TxCMD`, `PP_BufCFG`), line/self/bus/test/autoneg controls, event/status counters, address filter registers, and frame windows (`PP_RxFrame`, `PP_TxFrame`). Low I/O offsets such as `RX_FRAME_PORT`, `TX_CMD_PORT`, `TX_LEN_PORT`, `ISQ_PORT`, `ADD_PORT`, and `DATA_PORT` are used by the PIO path.

Status and control masks include receive acceptance modes (`DEF_RX_ACCEPT`, `RX_ALL_ACCEPT`, multicast/promiscuous bits), TX event/error bits, buffer events (`READY_FOR_TX`, `TX_UNDERRUN`, `RX_DMA`), line status (`LINK_OK`, `CRS_OK`), EEPROM status, bus status, and auto-negotiation flags. EEPROM offsets describe ISA configuration, adapter/media configuration, MAC address data, packet-page memory base, and IRQ map. Chip constants distinguish `CS8900`, `CS8920`, and `CS8920M`.

## Control Flow

The header has no executable flow. Its values drive probe-time signature checks, EEPROM parsing, open-time media and interrupt programming, RX/TX status interpretation, and optional ISA DMA setup in `cs89x0.c` and `mac89x0.c`.

## State and Persistence Behavior

No state is stored here, but many constants describe persistent EEPROM words and volatile packet-page registers. Incorrect masks or offsets would corrupt driver interpretation of EEPROM media/IRQ/DMA choices and hardware event status.

## Dependencies and Integration Points

The definitions are consumed by both PC/embedded CS89x0 and Macintosh CS89x0 code. `CONFIG_MAC` adds Macintosh-specific slot/MMIO base constants. PnP constants remain for legacy resource interpretation.

## Risks and Edge Cases

The main risk is register-layout drift: many constants are raw hardware values and are shared by drivers with different endianness and bus access methods. EEPROM word offsets are used as array indices after 16-bit reads, so changing them affects MAC/config decoding. Event masks also gate error statistics and interrupt wakeups.

## Test Signals

Compile coverage for both `cs89x0.c` and `mac89x0.c`, successful signature probe, correct EEPROM MAC/media/IRQ parsing, RX/TX event handling, promiscuous/all-multicast mode behavior, and optional DMA configuration are the key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/cs89x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/ep93xx_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/ep93xx_eth.c

## Purpose

`ep93xx_eth.c` is the platform Ethernet driver for the Cirrus EP93xx on-chip MAC. It implements a NAPI netdev with fixed-size DMA descriptor/status rings, simple MDIO access through MAC registers, ethtool MII controls, and OF probing through `cirrus,ep9301-eth`.

## Important APIs, Types, and Functions

Hardware layout is modeled by `struct ep93xx_rdesc`, `ep93xx_rstat`, `ep93xx_tdesc`, `ep93xx_tstat`, and aggregate coherent `struct ep93xx_descs`. `struct ep93xx_priv` owns the mapped register base, IRQ, descriptor DMA block, per-entry RX/TX bounce buffers, RX/TX ring pointers, NAPI object, `mii_if_info`, and MDIO divisor.

Important functions include `ep93xx_mdio_read`, `ep93xx_mdio_write`, `ep93xx_rx`, `ep93xx_poll`, `ep93xx_xmit`, `ep93xx_tx_complete`, `ep93xx_irq`, `ep93xx_alloc_buffers`, `ep93xx_free_buffers`, `ep93xx_start_hw`, `ep93xx_stop_hw`, `ep93xx_open`, `ep93xx_close`, `ep93xx_ioctl`, ethtool link helpers, `ep93xx_eth_probe`, and `ep93xx_eth_remove`.

## Control Flow

Probe maps the MMIO resource, resolves `phy-handle` and its `reg` property, allocates a netdev, reads the hardware MAC from `REG_INDAD0..5` or generates a random one, wires NAPI/netdev/ethtool ops, requests the memory region, initializes generic MII callbacks, and registers the device.

Open allocates a coherent descriptor/status block plus per-entry kmalloc buffers mapped with streaming DMA, enables NAPI, resets and starts hardware, initializes software ring pointers and locks, requests the shared IRQ, unmasks global interrupt delivery, and starts the queue. Hardware start programs RX/TX descriptor and status queue base/current/length registers, enables bus mastering, enqueues all RX descriptors/status entries, writes the station MAC, sets max frame length, and enables RX/TX.

RX NAPI scans status entries until budget or until `RFP` bits are absent. It validates EOF/EOB/index, accounts hardware errors, strips FCS when indicated, syncs the reusable RX buffer for CPU access, copies into a fresh SKB, syncs the buffer back for device use, and calls `napi_gro_receive`. After polling, it returns consumed RX descriptors/status entries to hardware. TX copies SKB data into pre-mapped per-entry TX buffers, enqueues one descriptor, tracks `tx_pending`, stops the queue when all eight entries are outstanding, and completion reclaims status entries and wakes the queue.

## State and Persistence Behavior

State is volatile and rebuilt on each open. Descriptor memory and RX/TX buffers are allocated on open and freed on close/remove. The driver uses copy-based RX/TX rather than owning SKBs in descriptors, so persistent per-packet state is limited to ring indices and mapped buffers. Link state is exposed through generic MII helpers, not phylib.

## Dependencies and Integration Points

Dependencies include platform resources, OF `phy-handle`, DMA mapping, NAPI/GRO, generic MII/ethtool helpers, and raw MMIO accessors. The netdev advertises SG and hardware checksum features, but the implementation still copies packet data into fixed buffers.

## Risks and Edge Cases

Probe has a leak risk pattern: if `of_parse_phandle` or PHY ID parsing fails after `ioremap`, the early return does not pass through `ep93xx_eth_remove`. TX ring size is only eight entries, so queue stop/wake and `tx_pending` accounting are important. RX allocation failure drops a packet but still advances the ring. Hardware reset/start polling uses short 10 ms windows. The driver requests the memory region after ioremap, which is unusual and makes failure paths sensitive.

## Test Signals

Signals include OF probe with valid and missing `phy-handle`, open/close/remove leak checks, MDIO read/write timeout logs, RX/TX traffic, TX queue full/wake behavior, NAPI interrupt masking/unmasking, RX error bits, random MAC fallback, MTU-sized packet handling up to `MAX_PKT_SIZE`, and ethtool MII operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/ep93xx_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/mac89x0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/mac89x0.c

## Purpose

`mac89x0.c` is a Macintosh-specific CS89x0 Ethernet driver for Dayna-style CS8900 cards in classic NuBus slot space. It strips the generic driver down to TP-only, hardwired slot/IRQ behavior and shared-memory packet access suitable for these Macintosh cards.

## Important APIs, Types, and Functions

Private `struct net_local` stores message level, chip type/revision, TX command, RX mode/config, and underrun count. Register helpers are split between ISA-like access (`readreg_io`, `writereg_io`) and shared-memory packet-page access (`readreg`, `writereg`), all using NuBus word access with byte swapping.

Core functions are `mac89x0_device_probe`, `net_open`, `net_send_packet`, `net_interrupt`, `net_rx`, `net_close`, `net_get_stats`, `set_multicast_list`, `set_mac_address`, and `mac89x0_device_remove`. The driver registers as a platform driver named `mac89x0`.

## Control Flow

Probe allocates a netdev, assumes slot `0xE`, refuses to bind if a real NuBus function resource exists in that slot, probes the pseudo-ISA address at offset `DEFAULTIOBASE`, validates the CS89x0 signature, enables shared memory with `MEMORY_ON`, reads chip revision and EEPROM MAC address, computes `SLOT2IRQ(slot)`, installs netdev ops, and registers the device.

Open disables interrupts, requests the slot IRQ, writes the chip IRQ selector, programs the MAC address, enables serial RX/TX, accepts directed/broadcast/error-free frames, enables RX/TX/buffer events, re-enables interrupts, and starts the queue. TX disables local IRQs around writing command/length and copying the frame into shared memory, then waits for TX completion interrupt to wake the queue. Interrupt flow mirrors the generic CS89x0 ISQ drain: RX, TX completion/errors, buffer-ready/underrun, missed RX, and collision events.

## State and Persistence Behavior

The driver keeps only volatile netdev-private state. EEPROM is required for the MAC address and is not modified. Hardware state is reprogrammed on each open. Statistics live in `dev->stats` and are supplemented from packet-page miss/collision counters.

## Dependencies and Integration Points

The file depends on classic Macintosh/NuBus APIs (`nubus_slot_addr`, `for_each_func_rsrc`, `hwreg_present`, `SLOT2IRQ`) and shared CS89x0 constants from `cs89x0.h`. It integrates with the normal netdev layer but not phylib or NAPI.

## Risks and Edge Cases

The probe is deliberately hard-coded to slot E, so multi-slot support is absent. Lack of a real NuBus ROM requires ISA-like probing, raising false-positive/false-negative risks. TX uses `local_irq_save` instead of a device spinlock and performs MMIO memory copies directly. The RX path uses `alloc_skb(length, GFP_ATOMIC)` without the 2-byte alignment reserve used in the generic driver. Removal assumes a registered netdev exists.

## Test Signals

Validate slot-E detection with and without a real NuBus card, EEPROM-present behavior, open/close, TX completion wakeups, TX underrun fallback, RX copy path, multicast/promiscuous changes, statistics reads, and module unload cleanup on supported Macintosh hardware or emulator coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/mac89x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Kconfig

## Purpose

This Kconfig file introduces the Cisco Ethernet vendor menu. `NET_VENDOR_CISCO` is a PCI-dependent boolean that controls whether Cisco NIC driver options are shown.

## Important APIs, Types, and Functions

The only symbol defined here is `NET_VENDOR_CISCO`, defaulting to `y` and depending on `PCI`. When enabled, it sources `drivers/net/ethernet/cisco/enic/Kconfig`.

## Control Flow

There is no runtime flow. During kernel configuration, this file gates access to ENIC configuration under the Cisco vendor section.

## State and Persistence Behavior

The selected Kconfig value persists only in the kernel build configuration. It does not create runtime state and does not directly build code except by exposing child options.

## Dependencies and Integration Points

It integrates with the networking driver Kconfig hierarchy and the ENIC child Kconfig. The PCI dependency matches the ENIC driver's PCI-only probe model.

## Risks and Edge Cases

Turning this symbol off hides ENIC even if `CONFIG_ENIC` would otherwise be desired. The help text correctly notes the symbol only controls visibility of vendor-specific questions.

## Test Signals

Configuration tests should confirm the Cisco menu appears when PCI is enabled, disappears when disabled, and sources the ENIC option correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Makefile

## Purpose

This Makefile connects Cisco Ethernet driver builds to the kernel object tree.

## Important APIs, Types, and Functions

It adds the `enic/` subdirectory when `CONFIG_ENIC` is enabled: `obj-$(CONFIG_ENIC) += enic/`.

## Control Flow

There is no runtime behavior. Kbuild descends into `drivers/net/ethernet/cisco/enic` only for ENIC-enabled builds.

## State and Persistence Behavior

No runtime state exists. Build output depends on the selected `.config`.

## Dependencies and Integration Points

This file is consumed by Kbuild and depends on the child ENIC Makefile for object composition.

## Risks and Edge Cases

If `CONFIG_ENIC=m`, this arrangement builds the child directory as a module object as defined by the child Makefile. Incorrect symbol naming here would silently omit the driver.

## Test Signals

Build with `CONFIG_ENIC=y`, `m`, and unset to confirm the directory is included only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Kconfig

## Purpose

`enic/Kconfig` defines the Cisco VIC Ethernet NIC driver option.

## Important APIs, Types, and Functions

The file defines `CONFIG_ENIC` as a tristate named "Cisco VIC Ethernet NIC Support". It depends on `PCI` and selects `PAGE_POOL`, matching the RX buffer allocation strategy in `enic_main.c` and `enic_rq.c`.

## Control Flow

There is no runtime control flow. The selected value determines whether ENIC is built in, built as a module, or omitted.

## State and Persistence Behavior

State is limited to kernel build configuration.

## Dependencies and Integration Points

It integrates with the parent Cisco vendor Kconfig and Kbuild. The `PAGE_POOL` select is a direct integration requirement for ENIC RX page-pool buffers.

## Risks and Edge Cases

Removing or weakening `select PAGE_POOL` would break ENIC builds that use page pool helpers. The PCI dependency must remain aligned with the driver's PCI registration.

## Test Signals

Kconfig/build validation for built-in and module ENIC, with page-pool symbols enabled automatically, is the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Makefile

## Purpose

This Makefile defines the ENIC composite object and its source-file membership.

## Important APIs, Types, and Functions

`obj-$(CONFIG_ENIC) := enic.o` builds the ENIC driver, and `enic-y` composes it from main netdev logic, vNIC queue/intr/dev helpers, resource setup, port-profile handling, ethtool, public API, classifier, and RX/TX queue helper files.

## Control Flow

There is no runtime flow. Kbuild links the listed objects into one `enic.o`.

## State and Persistence Behavior

No runtime state exists. The source list defines which internal symbols are available in the final module/built-in object.

## Dependencies and Integration Points

The file integrates all ENIC internal modules, including helper files not in this research subset such as `vnic_dev.c`, `enic_res.c`, `enic_rq.c`, and `enic_wq.c`.

## Risks and Edge Cases

Omitting any helper breaks link-time internal dependencies. Adding files in the wrong order generally should not matter to Kbuild, but missing object membership would prevent features such as RX page-pool handling or devcmd support.

## Test Signals

Build ENIC as module and built-in, checking that all referenced internal functions link and module metadata is emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_desc.h

## Purpose

`cq_desc.h` defines the base ENIC/vNIC completion queue descriptor format and common field masks used to interpret completion entries.

## Important APIs, Types, and Definitions

`enum cq_desc_types` assigns hardware descriptor type values for Ethernet WQ, descriptor copy, exchange WQ, Ethernet RQ, and FCP RQ completions. `struct cq_desc` is the generic 16-byte layout: completed descriptor index, queue number, 11 bytes of type-specific payload, and a combined type/color byte. The masks and bit counts describe type, color, queue number, completion index, and fetch-index masks for larger CQ entry formats.

## Control Flow

No executable control flow exists. Polling code in vNIC/ENIC completion paths uses these definitions to decode completion type/color ownership and queue/completed indices.

## State and Persistence Behavior

The structures describe DMA-visible hardware memory. State is produced by the adapter in completion rings and consumed by the driver; it is not persisted.

## Dependencies and Integration Points

The header is included by `cq_enet_desc.h` and indirectly by RX/TX CQ service code. It depends on Linux bit macros and fixed-width little-endian types through included kernel headers in consumers.

## Risks and Edge Cases

Descriptor layout must remain exactly 16 bytes and match firmware/hardware. Incorrect type or color masks would cause ring ownership errors, missed completions, or queue misassociation.

## Test Signals

RX/TX completion processing, color wrap behavior, queue index decoding, and builds with 16/32/64-byte RX CQ formats are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_enet_desc.h

## Purpose

`cq_enet_desc.h` defines Ethernet-specific ENIC completion formats for TX work queues and RX receive queues, including 16-, 32-, and 64-byte RX completion variants and their bit masks.

## Important APIs, Types, and Definitions

`struct cq_enet_wq_desc` represents TX completions. RX completions are described by `struct cq_enet_rq_desc`, `cq_enet_rq_desc_32`, and `cq_enet_rq_desc_64`, which include completed index, queue/RSS flags, RSS hash, byte count, VLAN TCI, checksum/FCoE fields, packet flags, optional fetch index, timestamp, and programmable information fields. Capability macros define supported RX CQ entry sizes and `VNIC_RQ_ALL` for firmware commands.

Important masks describe SOP/EOP, ingress port, FCoE, RSS type, checksum-not-calculated, bytes written, truncation, VLAN stripped, VLAN TCI fields, FCoE SOF/EOF, TCP/UDP/IP checksum status, IPv4/IPv6/protocol flags, fragment status, and FCS status.

## Control Flow

The file has no direct control flow. ENIC RX CQ service code decodes these fields to validate packets, compute length, set checksum state, record RSS hash, restore VLAN tags, account truncation/FCS errors, and support extended CQ metadata.

## State and Persistence Behavior

These structures model hardware-written DMA completion entries. The only persistence is volatile ring memory until software consumes and clears/recycles descriptors.

## Dependencies and Integration Points

It includes `cq_desc.h` and is used by `enic_main.c` plus RX helper code. Firmware capability commands select RX CQ entry size through the constants defined here.

## Risks and Edge Cases

Bitfield interpretation differs by CQ entry size and firmware patch level for VXLAN metadata. Wrong masks would corrupt checksum offload decisions or packet length/VLAN/RSS handling. Structure padding must match hardware exactly.

## Test Signals

Validate RX with 16/32/64-byte CQ entries, VLAN stripped packets, RSS hash types, IPv4/IPv6/TCP/UDP checksum states, truncated/FCS-error packets, VXLAN offload metadata, and ring color/index wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic.h

## Purpose

`enic.h` is the central private header for the Cisco VIC Ethernet driver. It defines supported PCI subsystem IDs, queue limits, interrupt layout, ENIC-private state structures, statistics, RFS flow tables, port-profile data, VXLAN state, helpers, logging wrappers, and internal prototypes shared by ENIC source files.

## Important APIs, Types, and Definitions

`struct enic` is the device-wide state: netdev, PCI device, vNIC config, BAR mappings, `vnic_dev`, timers/work items, MSI-X metadata, devcmd/API locks, MAC/filter counts, coalescing settings, SR-IOV and VF type state, port profiles, WQ/RQ/CQ/intr arrays, NAPI array, RSS key, generic stats, extended CQ selection, VXLAN state, and optional admin-channel resources.

Queue structures `struct enic_wq` and `struct enic_rq` wrap `vnic_wq`/`vnic_rq` with spinlocks/stats and page-pool state. `struct enic_rfs_fltr_node` and `struct enic_rfs_flw_tbl` store accelerated RFS IPv4 5-tuple filters. `struct enic_port_profile` stores port-profile requests, names, UUIDs, VF MACs, and MAC addresses. Interrupt helpers map RQ/WQ queues to CQ and MSI-X interrupt indices; `enic_dma_map_check` centralizes DMA mapping error accounting.

## Control Flow

The header itself has no top-level execution. Its inline helpers guide runtime mapping of queues, CQs, and interrupts in `enic_main.c`, while structures provide the state contract for ethtool, classifier, device-command, port-profile, RX, and TX helper modules.

## State and Persistence Behavior

All structures describe in-memory driver state. Some state mirrors firmware configuration, such as vNIC config, MAC address, port MTU, RSS key, coalescing timers, VXLAN UDP port, and port profiles. None is disk-persistent; it is rebuilt at PCI probe, device init, open, reset, or provisioning events.

## Dependencies and Integration Points

The header depends on ENIC vNIC helper headers, page-pool helpers, IRQ APIs, and netdev types. It is included across ENIC implementation files and exposes prototypes for `enic_reset_addr_lists`, SR-IOV checks, ethtool setup, RSS key programming, and extended CQ configuration.

## Risks and Edge Cases

Queue/CQ/interrupt mapping helpers are foundational; off-by-one errors would route completions to the wrong NAPI or interrupt. `ENIC_DESC_MAX_SPLITS` derives from TSO and descriptor length limits and affects TX ring fullness checks. RFS hash table sizing and bitfields constrain cleanup iteration. The API busy flag coordinates with exported ENIC API calls and reset paths, so lock ordering matters.

## Test Signals

Compile coverage across all ENIC objects, probe with different interrupt modes, RSS/RFS enabled builds, SR-IOV-enabled PFs and VFs, VXLAN feature negotiation, DMA mapping error injection, queue statistics, and reset paths validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.c

## Purpose

`enic_api.c` exports a small public ENIC API for issuing firmware device commands proxied to a VF by index. It is intended for peer kernel components that need controlled access to ENIC devcmd operations.

## Important APIs, Types, and Functions

The sole exported function is `enic_api_devcmd_proxy_by_index(struct net_device *netdev, int vf, enum vnic_devcmd_cmd cmd, u64 *a0, u64 *a1, int wait)`. It obtains `struct enic` from the netdev, waits while `enic_api_busy` is set, locks `devcmd_lock`, starts proxy mode with `vnic_dev_cmd_proxy_by_index_start`, runs `vnic_dev_cmd`, ends proxy mode, and returns the firmware command result.

## Control Flow

Callers enter with a netdev and VF index. The function spin-waits with `cpu_relax()` while reset paths mark the API busy. It then serializes against other devcmd users with `devcmd_lock`, wraps the command in proxy start/end calls, and releases both locks.

## State and Persistence Behavior

It mutates only transient vNIC proxy state around the command. Persistent effects depend on the command passed by the caller and firmware behavior. `enic_api_busy` is set elsewhere during reset/hang recovery to block external activity.

## Dependencies and Integration Points

The file depends on `vnic_dev`, `vnic_devcmd`, `enic_res`, and `enic.h`. The symbol is exported with `EXPORT_SYMBOL`, so lock semantics here are part of an inter-module contract.

## Risks and Edge Cases

The busy wait is a raw spin loop, so a stuck `enic_api_busy` can burn CPU. There is no VF validation here; callers or firmware must reject invalid VF indexes. Lock ordering with reset paths is critical: API lock is taken before `devcmd_lock`, matching the reset path's busy-flag coordination.

## Test Signals

Test proxied devcmd success/failure, concurrent calls during `enic_reset`/`enic_tx_hang_reset`, invalid VF indexes, long wait command timeout behavior, and module users resolving the exported symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.h

## Purpose

`enic_api.h` declares the exported ENIC devcmd proxy API.

## Important APIs, Types, and Functions

It declares `enic_api_devcmd_proxy_by_index`, taking a netdev, VF index, devcmd enum, two command arguments, and a wait value.

## Control Flow

No executable flow exists in the header. It provides the prototype used by external or internal callers of the API implemented in `enic_api.c`.

## State and Persistence Behavior

The header stores no state. Call effects depend on the underlying devcmd issued by the implementation.

## Dependencies and Integration Points

It includes netdevice, `vnic_dev.h`, and `vnic_devcmd.h`, exposing ENIC's firmware command vocabulary to users of this API.

## Risks and Edge Cases

The prototype exposes raw devcmd arguments, so ABI users must understand firmware command semantics and locking expectations. Header/API drift would break module builds.

## Test Signals

Compile external users against this header and exercise command proxy success, failure, and reset-concurrency behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.c

## Purpose

`enic_clsf.c` implements ENIC classifier support, primarily IPv4 TCP/UDP 5-tuple filters used by accelerated RFS and exposed through ethtool RX classification reporting.

## Important APIs, Types, and Functions

`enic_addfltr_5t` converts `flow_keys` into a firmware `struct filter` and calls `vnic_dev_classifier(..., CLSF_ADD, ...)`. `enic_delfltr` deletes a firmware classifier filter. `enic_rfs_flw_tbl_init` initializes the ENIC RFS hash table, free count, and cleanup cursor; `enic_rfs_flw_tbl_free` stops the expiry timer, deletes hardware filters, removes nodes, and restores free count. `htbl_fltr_search` scans all buckets for a filter ID.

With `CONFIG_RFS_ACCEL`, `enic_flow_may_expire` periodically asks `rps_may_expire_flow` whether filters can be removed, and `enic_rx_flow_steer` adds or retargets filters for skb flows and RX queues.

## Control Flow

RX flow steering dissects the SKB, rejects non-IPv4 or non-TCP/UDP flows, hashes to a bucket, and locks `rfs_h.lock`. Existing flows on the same queue return `-EEXIST`; existing flows moving queues either add the new hardware filter before deleting the old one or, when table space is exhausted, delete first. New flows decrement the free count, allocate a node, add the hardware filter, and insert it in the hash bucket. The expiry timer processes `ENIC_CLSF_EXPIRE_COUNT` buckets per tick and reschedules itself every quarter second.

## State and Persistence Behavior

Classifier state is split between firmware hardware filters and the in-memory `enic->rfs_h` hash table. It persists while the netdev/device is active and is fully deleted during stop/free. It is not disk-persistent and is rebuilt by RFS traffic.

## Dependencies and Integration Points

The file depends on flow dissector keys, RPS/RFS APIs, ENIC vNIC classifier devcmds, `enic_res.h`, and the `devcmd_lock`. Ettool reads these nodes through helpers in `enic_ethtool.c`.

## Risks and Edge Cases

Free-count handling is delicate, especially when retargeting a flow and delete/add operations partially fail. If deleting an old filter fails after adding a new one, a minimal cleanup node is inserted so later expiry can retry, but it does not contain full key data. `htbl_fltr_search` is O(number of buckets plus entries). Timer shutdown must run before freeing nodes.

## Test Signals

Test RFS with TCP/UDP IPv4 flows, unsupported protocols, queue retargeting, table-full conditions, firmware add/delete failures, expiry via `rps_may_expire_flow`, ethtool rule listing/lookup, and stop/remove cleanup with outstanding filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.h

## Purpose

`enic_clsf.h` declares ENIC classifier/RFS helpers and provides timer wrappers that compile away when accelerated RFS is disabled.

## Important APIs, Types, and Definitions

It defines `ENIC_CLSF_EXPIRE_COUNT` as 128 buckets per expiry pass. It declares `enic_addfltr_5t`, `enic_delfltr`, RFS table init/free, and filter-ID lookup. Under `CONFIG_RFS_ACCEL`, it declares `enic_rx_flow_steer` and `enic_flow_may_expire`, plus inline `enic_rfs_timer_start` and `enic_rfs_timer_stop`. Without RFS, the timer helpers are empty.

## Control Flow

The header has no direct runtime flow except inline timer setup/deletion when RFS acceleration is enabled.

## State and Persistence Behavior

Timer helpers operate on `enic->rfs_h.rfs_may_expire`; otherwise no state is stored here.

## Dependencies and Integration Points

It includes `vnic_dev.h` and `enic.h`, and is used by `enic_main.c` and `enic_ethtool.c` to integrate RFS and ethtool RXNFC behavior.

## Risks and Edge Cases

The compile-time split must stay consistent with netdev ops: `ndo_rx_flow_steer` is only installed under `CONFIG_RFS_ACCEL`. Timer deletion uses synchronous deletion to avoid use-after-free of classifier nodes.

## Test Signals

Build with and without `CONFIG_RFS_ACCEL`, verify timer lifecycle during open/stop, and exercise ethtool RXNFC rule views for active RFS filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.c

## Purpose

`enic_dev.c` provides locked wrappers around vNIC firmware device commands and small netdev-facing VLAN callbacks. It centralizes devcmd serialization and firmware status-to-errno translation.

## Important APIs, Types, and Functions

Wrappers include `enic_dev_fw_info`, `enic_dev_stats_dump`, station address add/delete, packet filter programming, arbitrary address add/delete, notification unset, hang notification, ingress VLAN rewrite mode setup, enable/disable reference counting, interrupt coalescing timer info, VLAN add/delete callbacks, and `enic_dev_status_to_errno`.

`enic_dev_enable` and `enic_dev_disable` maintain `enic->enable_count` so nested users only trigger firmware enable on first enable and firmware disable after the last disable.

## Control Flow

Most functions take `devcmd_lock` with bottom halves disabled, call the corresponding `vnic_dev_*` helper, and unlock. VLAN callbacks run under RTNL and delegate to `enic_add_vlan`/`enic_del_vlan` under the same lock. Status conversion maps firmware `ERR_*` codes to Linux negative errno values.

## State and Persistence Behavior

The wrappers mutate firmware state such as addresses, packet filters, VLAN tables, notification buffers, device enable state, and ingress VLAN rewrite mode. Local persistent state is limited to `enable_count` and generic stats such as any error accounting done by lower layers.

## Dependencies and Integration Points

The file depends on `vnic_dev`, `vnic_vic`, `enic_res`, `enic.h`, and `enic_dev.h`. It is called by open/stop/reset/probe paths, ethtool, address filtering, VLAN operations, and port-profile code.

## Risks and Edge Cases

Correct lock coverage is important because devcmd is a shared firmware mailbox. Enable-count imbalance would leave the vNIC enabled or disabled incorrectly. Address wrappers validate the station MAC but not arbitrary multicast/unicast addresses, relying on callers. Firmware status conversion defaults unknown positive statuses to `-1`, which is less specific than standard errno.

## Test Signals

Exercise firmware info/stats retrieval, open/stop enable-count transitions, filter mode changes, station MAC add/delete, VLAN add/delete, ingress VLAN rewrite programming, firmware failure status mapping, and concurrent devcmd callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.h

## Purpose

`enic_dev.h` declares ENIC devcmd wrapper functions and provides a proxy macro for commands that may target a PF or a VF by index.

## Important APIs, Types, and Definitions

`ENIC_DEVCMD_PROXY_BY_INDEX` locks `devcmd_lock`, checks `enic_is_valid_vf`, optionally starts VF proxy mode, invokes a provided `vnicdevcmdfn`, ends proxy mode, and unlocks. The header declares all wrapper functions from `enic_dev.c`, VLAN callbacks, coalescing timer info, and status conversion.

## Control Flow

The macro implements inline control flow used by port-profile operations: valid VF indexes are proxied, otherwise the command is issued to the owning vNIC. Regular function prototypes defer control flow to `enic_dev.c`.

## State and Persistence Behavior

The header stores no state. The macro mutates transient firmware proxy mode and may cause persistent firmware changes through the invoked command.

## Dependencies and Integration Points

It includes `vnic_dev.h` and `vnic_vic.h` and is used by main, ethtool, port-profile, and resource paths.

## Risks and Edge Cases

The macro's fallback behavior means invalid/non-SR-IOV VF inputs can become PF/self commands unless callers validate separately. Lock ordering must match other devcmd users. Macro arguments must be side-effect safe enough for single evaluation in the chosen command expression.

## Test Signals

Compile all macro call sites, test PF and VF port-profile commands, invalid VF handling, and concurrent devcmd operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_ethtool.c

## Purpose

`enic_ethtool.c` implements ENIC ethtool operations: driver/link information, hardware and software statistics, ring sizing, interrupt coalescing including adaptive RX coalescing, RX classifier rule introspection, RSS key get/set, RSS hash fields, timestamp capability, and channel counts.

## Important APIs, Types, and Functions

Statistic descriptors are represented by `struct enic_stat` and macros mapping field names to `u64` offsets in firmware and per-queue stats. Public setup is `enic_set_ethtool_ops`. Key functions include `enic_get_ksettings`, `enic_get_drvinfo`, `enic_get_strings`, `enic_get_ringparam`, `enic_set_ringparam`, `enic_get_sset_count`, `enic_get_ethtool_stats`, message-level get/set, `enic_get_coalesce`, `enic_set_coalesce`, RXNFC helpers, `enic_get_rxfh`, `enic_set_rxfh`, `enic_get_rx_flow_hash`, `enic_get_ts_info`, and `enic_get_channels`.

## Control Flow

Link settings combine PCI subsystem IDs with carrier state to report supported media and current speed/duplex. Stats dumping fetches firmware counters with `enic_dev_stats_dump`, then appends driver generic, per-RQ, and per-WQ stats. Ring parameter changes validate ranges, close the interface if running, align counts down to 32, free/reallocate/reinitialize vNIC resources, and reopen if needed; on error it restores saved counts.

Coalescing validation clamps values to firmware max, rejects TX coalescing outside MSI-X mode, and validates adaptive RX low/high ranges. Setting coalescing programs TX interrupt timers for WQs, optionally programs fixed RX timers, and updates adaptive RX range state. RXNFC reads the in-memory RFS classifier table; it does not install arbitrary user rules. RSS key set rejects indirection table changes and unsupported hash functions, copies the key, and calls `__enic_set_rsskey`.

## State and Persistence Behavior

Ettool operations mutate in-memory and firmware-backed settings: ring descriptor counts, RSS key, interrupt coalescing timers, adaptive RX coalescing ranges, and message level. These settings persist for the lifetime of the device instance but are not stored across driver reload.

## Dependencies and Integration Points

The file depends on ENIC devcmd wrappers, classifier table state, vNIC RSS/stat structures, and PCI subsystem IDs from `enic.h`. It is attached to each netdev by `enic_set_ethtool_ops` during probe.

## Risks and Edge Cases

Ring resize has a notable failure mode: if reallocation fails after counts were changed, it restores counts but does not reallocate old resources before returning, leaving recovery to higher-level handling. Stats and driver-info functions silently return old/partial data on non-ENOMEM devcmd failures. RXNFC operates on RFS filters only, so user expectations for programmable ntuple rules may not match behavior. Coalescing values are clamped after warning, not rejected except for invalid relationships.

## Test Signals

Use `ethtool -i`, `-S`, `-g/-G`, `-c/-C`, `-n`, `-x/-X`, `-k`, and channel queries across interrupt modes. Validate running ring resize, resize failure injection, adaptive coalescing ranges, RSS key programming, RFS filter reporting, and media reporting for multiple VIC subsystem IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_main.c

## Purpose

`enic_main.c` is the main Cisco VIC Ethernet PCI/netdev driver. It handles PCI probe/remove, vNIC registration/open/init, resource sizing, interrupt mode selection, NAPI, TX/RX completion polling, page-pool-backed RX setup, TX offloads, RSS, VXLAN offloads, address filtering, VLAN callbacks, SR-IOV/port-profile hooks, reset/hang recovery, MTU/link notification, and netdev operation registration.

## Important APIs, Types, and Functions

The file registers `enic_driver` with PCI IDs for VIC ENET PF, dynamic vNIC, and VF devices. Interrupt handlers are `enic_isr_legacy`, `enic_isr_msi`, `enic_isr_msix`, `enic_isr_msix_err`, and `enic_isr_msix_notify`; NAPI pollers are `enic_poll`, `enic_poll_msix_rq`, and `enic_poll_msix_wq`.

TX helpers include `enic_hard_start_xmit`, `enic_queue_wq_skb`, VLAN/checksum/TSO/encap queueing variants, and checksum preload helpers. Runtime lifecycle functions include `enic_open`, `enic_stop`, `_enic_change_mtu`, `enic_change_mtu_work`, `enic_reset`, `enic_tx_hang_reset`, `enic_dev_init`, `enic_dev_deinit`, `enic_probe`, and `enic_remove`. Feature/control helpers cover VXLAN UDP tunnel configuration, features check, link/MTU/message notification, adaptive interrupt moderation, RSS key/CPU/NIC config, interrupt request/free/synchronize, resource adjustment, address filters, SR-IOV VF MAC/port operations, and queue stats.

## Control Flow

PCI probe allocates a multiqueue netdev, enables PCI memory, requests regions, sets DMA mask to 47-bit or 32-bit, maps BARs, registers the vNIC, initializes devcmd, optionally enables SR-IOV and allocates port profiles, opens the vNIC, initializes locks, configures ingress VLAN rewrite, optionally initializes firmware for non-dynamic vNICs, allocates ENIC/vNIC resources, configures RSS/NIC settings, attaches NAPI, initializes timers/work, sets MAC/coalescing/features/MTU, and registers the netdev.

Open requests interrupts and affinity hints, sets notification delivery, creates one page pool per RQ, enables and fills RQs, enables WQs, adds station address for non-dynamic PFs, programs RX mode, wakes TX queues, enables NAPI, enables the device, unmasks interrupts, and starts notification/RFS timers. Stop masks and synchronizes interrupts, deletes timers and RFS filters, disables the vNIC, disables NAPI and queues, removes station address, disables/cleans WQ/RQ/CQ/intr resources, destroys page pools, unsets notification, and frees IRQs.

TX selects WQ by skb queue mapping, linearizes overly fragmented non-TSO SKBs, checks descriptor availability, maps SKB head/frags, writes descriptors for TSO, checksum, VLAN, VXLAN encapsulation, or plain VLAN mode, timestamps, doorbells unless batching, and stops the netdev queue near low descriptor thresholds. Completion polling reclaims WQ descriptors through helper code and returns interrupt credits.

RX NAPI services CQ entries through `enic_rq_cq_service`, returns credits, refills RQs via page-pool allocation, optionally recalculates adaptive coalescing, and unmasks interrupts on completion. Error interrupts log queue errors and schedule reset work; TX timeout schedules hang reset.

## State and Persistence Behavior

Device state lives in `struct enic` for the PCI device lifetime. Queue resources, NAPI, interrupt arrays, RSS key, port-profile records, coalescing settings, VXLAN port, address counts, and work/timer state are in memory. Firmware/vNIC state is reinitialized by probe, open, reset, and hang-reset flows. Dynamic vNICs can be provisioned later through port-profile operations. There is no disk persistence.

## Dependencies and Integration Points

The driver depends on PCI, DMA mapping, vNIC firmware command/resource helpers, NAPI, page pool, ethtool, netdev queues/stat ops, VXLAN UDP tunnel APIs, RFS acceleration when enabled, SR-IOV when enabled, rtnetlink, and helper modules from the ENIC object. It integrates with firmware for device open/init/enable/reset, RSS, filters, VLAN rewrite, overlay offload, and notifications.

## Risks and Edge Cases

The highest-risk areas are reset/open/stop ordering, devcmd locking around external API users, TX DMA mapping rollback, page-pool allocation failure during open/refill, interrupt-mode resource arithmetic, and SR-IOV/port-profile state transitions. `enic_probe` enables SR-IOV before several later init steps, so later failures must disable it correctly. `enic_remove` cancels reset and MTU work but not `tx_hang_reset` explicitly, which is worth checking against unregister/stop serialization. Dynamic and VF MAC validation permits zero addresses, so address-list behavior differs by device type. VXLAN offload supports only one UDP port and feature checks must disable offloads for unsupported inner/outer protocol combinations.

## Test Signals

Validate PCI probe/remove, DMA mask fallback, BAR mapping failures, MSI-X/MSI/INTx modes, queue count/resource constraints, open/stop cycles, RX page-pool refill failures, TX SG/checksum/TSO/TSO6/VLAN/VXLAN traffic, TX timeout and queue-error reset, link/MTU notification, SR-IOV enable/disable and VF MAC/port-profile ops, RFS steering, ethtool ring/coalescing/RSS changes, kdump minimal-resource mode, and module unload with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.c

## Purpose

`enic_pp.c` implements ENIC port-profile request handling for dynamic vNICs and SR-IOV VFs. It translates netlink VF port operations into Cisco VIC provisioning TLVs and firmware devcmd sequences for preassociate, associate, disassociate, and status query.

## Important APIs, Types, and Functions

Public functions are `enic_is_valid_pp_vf`, `enic_process_set_pp_request`, and `enic_process_get_pp_request`. Internal operations include `enic_set_port_profile`, `enic_unset_port_profile`, `enic_are_pp_different`, and request handlers `enic_pp_preassociate`, `enic_pp_disassociate`, `enic_pp_preassociate_rr`, and `enic_pp_associate`.

`enic_set_port_profile` allocates `vic_provinfo`, adds TLVs for profile name, client MAC, cluster UUID string, optional instance/host UUIDs, and Linux OS type, then calls `vnic_dev_init_prov2` through the proxy macro. Association handlers call `vnic_dev_enable2`, `vnic_dev_add_addr`, `vnic_dev_del_addr`, and deinit/done commands as appropriate.

## Control Flow

VF validation accepts `PORT_SELF_VF` only for dynamic vNICs and numbered VFs only when SR-IOV is enabled. Set request dispatch indexes `enic_pp_handlers` by request type. `PREASSOCIATE` is unsupported. `PREASSOCIATE_RR` optionally disassociates first, sets provisioning data, and enables the device as standby unless it is part of a later associate. `ASSOCIATE` disassociates if the previous state was not a matching preassociate, performs preassociate-RR, enables the device active, and registers the MAC. `DISASSOCIATE` removes registered MACs and deinitializes the profile.

Get request maps firmware completion status from enable/deinit done commands into `PORT_PROFILE_RESPONSE_*` values.

## State and Persistence Behavior

State lives in `enic->pp` entries, one for self or per VF, and in firmware provisioning/device state. The file updates request status indirectly; caller code in `enic_main.c` copies/clears profile entries and marks `ENIC_PORT_REQUEST_APPLIED`. There is no disk persistence.

## Dependencies and Integration Points

The file depends on rtnetlink VF port attributes handled by `enic_main.c`, `vnic_vic` provisioning helpers, `enic_dev.h` proxy macro, firmware devcmds, and SR-IOV state from `enic.h`.

## Risks and Edge Cases

TLV construction has multiple failure exits that must free `vic_provinfo`. MAC source differs for self, VF, and explicit port-profile MACs; missing VF MAC rejects provisioning. Request transitions use `restore_pp` to tell callers whether to restore previous in-memory state, so handler return semantics are important. `PREASSOCIATE` unsupported behavior must be acceptable to userspace tooling.

## Test Signals

Exercise dynamic self port-profile associate/disassociate, SR-IOV VF profiles, missing/invalid profile name or UUID lengths, missing MAC, firmware init/enable/deinit failures, get-status responses, repeated associate with same/different profiles, and cleanup resetting address lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.h

## Purpose

`enic_pp.h` declares ENIC port-profile helpers and defines the macro that selects the self or VF port-profile entry after validation.

## Important APIs, Types, and Definitions

`ENIC_PP_BY_INDEX(enic, vf, pp, err)` calls `enic_is_valid_pp_vf`; on success it returns `enic->pp` for `PORT_SELF_VF` or `enic->pp + vf` for an SR-IOV VF. The header declares set/get request processing and VF validation functions.

## Control Flow

The macro provides inline selection flow for callers in `enic_main.c` and `enic_pp.c`. Actual provisioning state-machine flow is implemented in `enic_pp.c`.

## State and Persistence Behavior

No state is stored in the header. The macro returns pointers into `enic->pp`, whose contents persist for the device lifetime or until overwritten/cleared by port-profile operations.

## Dependencies and Integration Points

The header depends on `PORT_SELF_VF` and port-profile constants from included ENIC/vNIC headers through users. It integrates netdev VF operations with ENIC provisioning functions.

## Risks and Edge Cases

Because the macro sets `pp = NULL` on validation failure, callers must check `err` before dereferencing. Pointer arithmetic assumes `enic->pp` was allocated with enough entries for enabled VFs.

## Test Signals

Compile all macro users, test self and VF selection, invalid VF indexes, SR-IOV-disabled behavior, and dynamic-vNIC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.h -->
