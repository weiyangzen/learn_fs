# Research: subset-b-004486

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.c

## Purpose
Implements AF_XDP zero-copy support for the Intel IDPF driver. It binds XSK pools to IDPF RX, split RX buffer, XDP TX, and TX completion queues, drives XSK RX polling and TX wakeup, and translates between IDPF descriptors and libeth XDP/XSK helper APIs.

## Important APIs, Types, And Functions
Key entry points are `idpf_xsk_setup_queue`, `idpf_xsk_clear_queue`, `idpf_xskfq_init`, `idpf_xskfq_rel`, `idpf_xskrq_poll`, `idpf_xsk_xmit`, `idpf_xsk_pool_setup`, and `idpf_xsk_wakeup`. Internal setup helpers attach `struct xsk_buff_pool` to queue objects and mark queue flags with `idpf_queue_set(XSK, ...)`. TX cleanup uses `idpf_xsksq_complete`, `idpf_xsksq_clean`, `xsk_tx_completed`, and `libeth_xdp_complete_tx`. RX uses `struct idpf_xskfq_refill_set` to batch buffer-queue refill accounting.

## Control Flow
Queue setup is conditional on `idpf_xdp_enabled(vport)` and on a usable XSK pool for the queue id. TX queues are initialized with a libeth XDP SQ timer and a `NOIRQ` flag when need-wakeup is active. RX polling loops over descriptors while generation bits match, extracts buffer queue and buffer ids, processes XSK buffers through the XDP program, finalizes any redirected TX work, advances queue indices, and then refills touched buffer queues. Pool setup validates frame-size alignment, optionally disables the queue pair, calls `libeth_xsk_setup_pool`, and restarts the pair.

## State And Persistence
Persistent runtime state is in queue fields: `pool`, `next_to_clean`, `next_to_use`, `pending`, `thresh`, `xsk`, buffer DMA descriptors, and queue flag bits such as `XSK`, `XDP`, `NOIRQ`, `GEN_CHK`, and `HSPLIT_EN`. There is no disk persistence. Hardware-visible state changes happen through descriptor rings and tail writes, plus queue-pair disable/enable during pool reconfiguration.

## Dependencies And Integration
Depends on Linux AF_XDP APIs, `net/libeth/xsk.h`, IDPF XDP helpers, Virtchnl2 queue types, NAPI wakeup via `libeth_xsk_init_wakeup`, and IDPF queue-pair switching. It integrates with netdev BPF `XSK_POOL_SETUP` and ndo XSK wakeup paths through functions declared in `xsk.h`.

## Risks
Queue-id mapping is sensitive for split buffer queues and XDP TX queue offsets. Incorrect `pending` accounting can starve refills or overrun rings. Need-wakeup handling must set/clear wake flags only when failures or no progress require userspace notification. Pool reconfiguration errors must leave queue-pair and pool state consistent.

## Test Signals
Useful signals include AF_XDP zero-copy bind/unbind on aligned and misaligned frame sizes, traffic through XDP_PASS/TX/REDIRECT/drop paths, need-wakeup sockets, queue restart failure injection, RX descriptor wrap/generation-bit transitions, and TX completion accounting matching userspace completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.h

## Purpose
Declares the IDPF AF_XDP integration surface used by the rest of the IDPF driver. The header keeps implementation details in `xsk.c` while exposing queue setup, teardown, polling, transmit, pool setup, and wakeup functions.

## Important APIs, Types, And Functions
The file forward-declares IDPF queue/vport types, `struct net_device`, and `struct netdev_bpf`, and includes `<linux/types.h>` for scalar types. Public prototypes cover `idpf_xsk_setup_queue`, `idpf_xsk_clear_queue`, `idpf_xsk_init_wakeup`, `idpf_xskfq_init`, `idpf_xskfq_rel`, `idpf_xsksq_clean`, `idpf_xskrq_poll`, `idpf_xsk_xmit`, `idpf_xsk_pool_setup`, and `idpf_xsk_wakeup`.

## Control Flow
This header has no executable control flow. It defines how other IDPF modules call into XSK handling: setup/clear during queue lifecycle, fill-queue init/release during buffer queue lifecycle, RX polling from NAPI, TX from wakeup/timer paths, and pool setup from netdev BPF callbacks.

## State And Persistence
No state is stored in the header. The prototypes imply mutation of queue objects, XSK pool references, queue wakeup state, and netdev BPF pool registration in implementation code.

## Dependencies And Integration
Depends on Virtchnl2 queue type declarations and IDPF internal structs. It is the integration point between generic IDPF queue management, XDP, AF_XDP, and netdev operations.

## Risks
Signature drift here can silently break callers across IDPF queue, XDP, and netdev code. The `void *q` queue setup/clear API requires callers to pass an object matching the supplied queue type.

## Test Signals
Build coverage with `CONFIG_IDPF` and AF_XDP enabled, plus queue lifecycle tests that exercise every declared entry point through normal driver paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/Makefile

## Purpose
Defines the kernel build objects for the Intel IGB PCIe Ethernet driver.

## Important APIs, Types, And Functions
The only build target is `obj-$(CONFIG_IGB) += igb.o`. The `igb-y` object list links core driver, ethtool, shared e1000 hardware modules, PTP, hwmon, mailbox, I210 support, and AF_XDP support (`igb_xsk.o`) into `igb.o`.

## Control Flow
There is no runtime control flow. Kbuild includes the object list when `CONFIG_IGB` is enabled.

## State And Persistence
No runtime state. Build state is the ordered object composition of the module.

## Dependencies And Integration
Integrates with Linux Kbuild and the driver source set in the same directory. The object list is important because shared code such as `e1000_82575.o`, `e1000_mac.o`, `e1000_mbx.o`, and `e1000_i210.o` provides function tables and exported helpers consumed by `igb_main.o`.

## Risks
Omitting a required object causes unresolved symbols; adding objects conditionally without matching config guards can break builds. Object order can matter for duplicate definitions and link diagnostics.

## Test Signals
Build `drivers/net/ethernet/intel/igb/` with `CONFIG_IGB=m` and with optional `CONFIG_IGB_HWMON`/XDP-related configs to confirm all referenced objects link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_82575.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_82575.c

## Purpose
Provides chip-family specific hardware support for 82575, 82576, 82580, I350, I354, I210, and I211 devices in the IGB driver. It detects device type, initializes MAC/PHY/NVM operation tables, handles reset and link setup, provides SR-IOV/VMDq helpers, implements NVM checksum variants, and includes EEE and optional thermal sensor support.

## Important APIs, Types, And Functions
The exported family descriptor is `e1000_82575_info`, with `igb_get_invariants_82575` as the main initializer. Important public helpers include `igb_shutdown_serdes_link_82575`, `igb_power_up_serdes_link_82575`, `igb_power_down_phy_copper_82575`, `igb_rx_fifo_flush_82575`, `igb_vmdq_set_anti_spoofing_pf`, `igb_vmdq_set_loopback_pf`, `igb_vmdq_set_replication_pf`, `igb_read_phy_reg_82580`, `igb_write_phy_reg_82580`, `igb_rxpbs_adjust_82580`, `igb_read_emi_reg`, `igb_set_eee_i350`, `igb_set_eee_i354`, and `igb_get_eee_status_i354`. Internal operations populate `e1000_mac_operations`, `e1000_phy_operations`, and `e1000_nvm_operations`.

## Control Flow
Initialization maps PCI device id to `mac->type`, derives media type from `CTRL_EXT` and SFP EEPROM when applicable, then initializes MAC, NVM, mailbox, and PHY parameters. Reset paths disable PCIe master, mask interrupts, stop RX/TX, issue function or global reset, wait for NVM auto-read, restore MDIC configuration, and apply alternate MAC addresses. Link setup selects copper or SerDes/SGMII handling, configures PCS/autoneg/forced mode, resets attached PHYs, and delegates flow-control resolution to generic MAC code.

## State And Persistence
State is stored in `struct e1000_hw`: MAC type, media type, function number, operation tables, NVM sizing, PHY id/address, device-specific flags (`sgmii_active`, `global_device_reset`, `eee_disable`, `module_plugged`, media swap state), and thermal sensor data. Persistent hardware/NVM state can be modified through NVM checksum updates, VFTA shadow updates, EEE advertisement, PHY power management, VMDq registers, and reset scripts for EEPROM-less hardware.

## Dependencies And Integration
Uses generic helpers from `e1000_mac.c`, `e1000_phy.c`, `e1000_nvm.c`, I210 routines from `e1000_i210.c`, mailbox setup from `e1000_mbx.c`, register definitions, Linux I2C/SFP access, and `struct igb_adapter` state from `igb.h`.

## Risks
Device-family branching is dense and register-sensitive. Semaphore leaks can block PHY/NVM access. Reset and EEE paths can disrupt link or management pass-through. NVM checksum updates touch multiple per-port regions and must not be interrupted. Media detection may misclassify SFP/SGMII modules if I2C/MDIO routing is wrong.

## Test Signals
Boot/probe tests across supported PCI ids, reset/reload loops, copper and SerDes link negotiation, SFP insertion cases, EEPROM-less I210/I211 paths, SR-IOV mailbox/VMDq behavior, NVM checksum validation/update, EEE enable/disable, and hwmon sensor reads when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_82575.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_82575.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_82575.h

## Purpose
Defines 82575-family public declarations, descriptor layouts, register bit masks, and feature constants used by IGB hardware code.

## Important APIs, Types, And Functions
Declares SerDes power, copper PHY power, RX FIFO flush, and I2C byte access helpers. Defines receive address entry counts for 82575/82576/82580/I350, SW/FW synchronization bits, SRRCTL/MRQC interrupt masks, advanced RX/TX descriptor unions, advanced TX context descriptors, DCA fields, ETQF/FTQF filters, VMDq/VMOLR controls, VLAN table constants, and RSS/hash related masks.

## Control Flow
No executable control flow. Constants are consumed by setup, RX/TX descriptor programming, VLAN filtering, DCA, SR-IOV, and link/power code in the C files.

## State And Persistence
Defines memory layouts for descriptor rings and hardware register fields. These structures describe DMA-visible state rather than storing state themselves.

## Dependencies And Integration
Used by `e1000_82575.c`, main IGB datapath code, and shared MAC helpers. Descriptor definitions must match hardware ABI and Linux endian annotations.

## Risks
Incorrect bit definitions can cause descriptor corruption, VLAN leakage, broken RSS/VMDq steering, or device reset/power bugs. Descriptor layout changes are high risk because hardware directly reads and writes these structures.

## Test Signals
Compile coverage plus datapath tests for RX/TX descriptors, VLAN filtering, RSS, SR-IOV/VMDq, timestamp flags, and queue enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_82575.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_defines.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_defines.h

## Purpose
Central register-bit and constant catalog for the IGB shared e1000 hardware code.

## Important APIs, Types, And Functions
Defines constants for descriptor multiples, wake-on-LAN, `CTRL`/`CTRL_EXT`, RX/TX controls, PCS/SerDes, link speeds, advertised capabilities, LEDs, DMA coalescing, interrupt causes/masks, NVM access and offsets, semaphores, PHY IDs and registers, MDIC/MDICNFG, EEE, thermal sensors, VLAN filters, Qav, and management pass-through fields.

## Control Flow
No executable control flow. The file supplies named masks and shifts used by all IGB hardware manipulation paths.

## State And Persistence
The definitions describe persistent device state in PCI config, MMIO registers, NVM words, PHY pages, and descriptor fields. They do not allocate runtime state.

## Dependencies And Integration
Included by `e1000_hw.h` and shared modules such as MAC, PHY, NVM, 82575-family, and I210 code. Many values are part of the hardware contract and must match datasheet-defined fields.

## Risks
Duplicate or wrong masks can silently program wrong hardware bits. NVM offsets and checksum constants are especially sensitive because they affect persistent flash/EEPROM contents. Interrupt and wake masks affect system power management and packet delivery.

## Test Signals
Broad compile coverage, link setup, WOL, NVM read/write/validate, PHY identification, interrupt enable/disable, VLAN filtering, EEE, PTP/time-sync, and Qav tests validate consumers of these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_hw.h

## Purpose
Defines the central IGB hardware model: supported device ids, MAC/PHY/NVM/bus/media enums, statistics, management command structures, operation tables, and `struct e1000_hw`.

## Important APIs, Types, And Functions
Important types include `enum e1000_mac_type`, `e1000_media_type`, `e1000_nvm_type`, `e1000_phy_type`, bus enums, `struct e1000_hw_stats`, host management command structs, `e1000_mac_operations`, `e1000_phy_operations`, `e1000_nvm_operations`, `e1000_mbx_operations`, `e1000_info`, `e1000_mac_info`, `e1000_phy_info`, `e1000_nvm_info`, `e1000_fc_info`, `e1000_mbx_info`, `e1000_dev_spec_82575`, and `struct e1000_hw`. It also declares PCI config helpers and `igb_get_hw_dev`.

## Control Flow
No runtime control flow, but it defines the dispatch model: probe code selects an `e1000_info`, which fills operation tables in `struct e1000_hw`; later MAC, PHY, NVM, mailbox, and reset paths call through those function pointers.

## State And Persistence
`struct e1000_hw` is the durable in-memory state for one adapter instance. It caches MMIO bases, MAC addresses, PHY/NVM metadata, flow-control settings, mailbox stats, management cookies, device-specific flags, PCI ids, and revision. Hardware/NVM persistence is accessed through function pointers stored here.

## Dependencies And Integration
Includes Linux types, delay, IO, netdevice, register and define headers, plus shared MAC/PHY/NVM/mailbox headers. It is included broadly across the IGB driver and binds the shared-code modules to `igb_main`.

## Risks
Changing structure fields or operation signatures has wide blast radius. Function pointer initialization must match the detected device family. Misstated device ids or enum mappings can select the wrong reset/link/NVM implementation.

## Test Signals
All-driver build coverage, probe on multiple PCI ids, operation-table sanity, ethtool register/EEPROM paths, SR-IOV mailbox paths, and reset/link tests exercise this hardware model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_i210.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_i210.c

## Purpose
Implements I210/I211-specific NVM, iNVM, semaphore, flash update, XMDIO, PLL workaround, and configuration-done behavior.

## Important APIs, Types, And Functions
Public functions are `igb_acquire_swfw_sync_i210`, `igb_release_swfw_sync_i210`, `igb_read_invm_version`, `igb_read_xmdio_reg`, `igb_write_xmdio_reg`, `igb_init_nvm_params_i210`, `igb_get_flash_presence_i210`, `igb_pll_workaround_i210`, and `igb_get_cfg_done_i210`. Internal helpers cover hardware semaphore acquisition, NVM acquire/release, EERD/SRWR read-write bursts, iNVM word mapping, checksum validate/update, and flash commit polling.

## Control Flow
NVM initialization chooses flash-backed NVM operations when flash is detected; otherwise it switches to read-only iNVM mappings for MAC address, init control words, LED defaults, and PCI ids. Semaphore acquisition waits for SMBI/SWESMBI and SW_FW_SYNC bits. Checksum updates read all NVM words, write the checksum through SRWR, then request a flash update. The PLL workaround temporarily changes MDICNFG, PHY page, EEPROM autoload data, and PCI power state to recover from bad clock frequency after power-up.

## State And Persistence
Mutates `hw->nvm` type and operation pointers, SW/FW synchronization bits, flash contents during checksum update, iNVM-derived runtime reads, PHY MMD registers, and PCI power-management state during the PLL workaround. `clear_semaphore_once` from the 82575 device-specific state is used to recover from a stuck semaphore once.

## Dependencies And Integration
Uses generic NVM helpers, 82580 PHY register access, PCI config accessors, register definitions, and `struct e1000_fw_version`. Called from 82575-family invariant setup for I210/I211 devices.

## Risks
Flash update and checksum writes can persist bad data if interrupted. The busy-wait release path loops until a semaphore is obtained. iNVM fallback only maps selected words, so callers must tolerate reserved values. PLL workaround touches power state and must restore registers on all paths.

## Test Signals
I210/I211 flash-present and flashless probes, NVM read/write/checksum update, iNVM MAC/LED defaults, semaphore contention tests, XMDIO read/write, PLL workaround on affected hardware, and config-done timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_i210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_i210.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_i210.h

## Purpose
Declares I210/I211-specific helpers and constants for iNVM records, LED defaults, flash/NVM behavior, XMDIO, and PLL workaround support.

## Important APIs, Types, And Functions
Declares the public functions implemented in `e1000_i210.c`. Defines iNVM record extraction macros, `enum E1000_INVM_STRUCTURE_TYPE`, record sizes, version/image fields, LED defaults, I211 NVM fallback defaults, PCI PMCSR constants, PLL retry constants, and workaround values.

## Control Flow
No executable flow. Macros and enum values are consumed by iNVM scanning and PLL workaround logic.

## State And Persistence
Constants describe OTP/iNVM records, flashless defaults, and PHY/PCI registers touched by runtime code.

## Dependencies And Integration
Included by `e1000_mac.h`, `e1000_82575.c`, and `e1000_i210.c`. It lets generic family setup switch to I210-specific NVM operations without exposing implementation internals.

## Risks
Incorrect iNVM masks or default NVM words can produce invalid MAC/LED/link initialization on flashless adapters. PLL constants are hardware-workaround sensitive.

## Test Signals
Build coverage, flashless I211 probe, iNVM version parsing, LED default validation, and PLL workaround execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_i210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mac.c

## Purpose
Provides generic MAC-layer helpers for the IGB shared hardware code: PCIe bus discovery, receive address/VLAN/multicast table programming, link and flow-control setup, hardware semaphore handling, LED control, PCIe master disable, generic control-register writes, and management pass-through checks.

## Important APIs, Types, And Functions
Public helpers include `igb_get_bus_info_pcie`, `igb_clear_vfta`, `igb_write_vfta`, `igb_init_rx_addrs`, `igb_vfta_set`, `igb_check_alt_mac_addr`, `igb_rar_set`, `igb_mta_set`, `igb_update_mc_addr_list`, `igb_clear_hw_cntrs_base`, `igb_check_for_copper_link`, `igb_setup_link`, `igb_config_collision_dist`, `igb_force_mac_fc`, `igb_config_fc_after_link_up`, `igb_get_speed_and_duplex_copper`, `igb_get_hw_semaphore`, `igb_put_hw_semaphore`, `igb_get_auto_rd_done`, LED helpers, `igb_disable_pcie_master`, `igb_validate_mdi_setting`, `igb_write_8bit_ctrl_reg`, and `igb_enable_mng_pass_thru`.

## Control Flow
Link setup optionally reads default flow-control mode from NVM, calls the media-specific physical setup function, initializes pause registers, and programs watermarks. Link-up handling resolves flow control from copper PHY autoneg registers or SerDes PCS autoneg registers before forcing MAC `CTRL` bits. VLAN update coordinates VFTA with VLVF/VLVFB pool bits so VMDq users do not lose shared VLANs. Multicast programming builds a shadow table and rewrites MTA, with an I21x double-check loop for unreliable writes.

## State And Persistence
Mutates `struct e1000_hw` bus info, flow-control current/requested modes, LED cached modes, multicast shadow table, RAR/VFTA/MTA hardware registers, adapter `shadow_vfta`, semaphore bits, and hardware counters by clear-on-read. NVM reads can affect default flow-control and alternate MAC selection.

## Dependencies And Integration
Uses operation pointers from `e1000_hw`, NVM/PHY helpers, Linux PCI capability definitions, netdevice debug, ether address helpers, and `struct igb_adapter`. Device-specific code in `e1000_82575.c` calls these helpers through operation tables.

## Risks
Flow-control resolution is branch-heavy and must match IEEE pause negotiation. VLAN/VLVF ordering is security-sensitive for VF pool isolation. Semaphore timeouts can block NVM/PHY paths. Alternate MAC handling must reject multicast addresses. Incorrect RAR/MTA writes break packet filtering.

## Test Signals
PCIe capability reads, VLAN add/remove with and without VFs, multicast list programming, copper/SerDes autoneg flow-control matrices, half-duplex behavior, LED identify tests, management pass-through checks, and reset paths waiting for auto-read completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mac.h

## Purpose
Declares generic IGB MAC helper APIs and management-mode constants used by shared hardware code.

## Important APIs, Types, And Functions
Prototypes cover LED, link, bus, semaphore, flow-control, VLAN, multicast, receive address, alternate MAC, PCIe master, MDI validation, 8-bit control register, and management pass-through helpers. It includes `e1000_hw.h`, PHY/NVM/defines/I210 headers, and defines `enum e1000_mng_mode` plus management register masks.

## Control Flow
No executable control flow. It exposes generic helpers that device-specific operation tables call directly or indirectly.

## State And Persistence
No state is stored here. Declarations imply mutation of hardware registers and `struct e1000_hw` fields in the implementation.

## Dependencies And Integration
This is a shared-code API boundary between `e1000_mac.c`, device-specific files, NVM/PHY code, and the main IGB driver.

## Risks
Header inclusion order is delicate because `e1000_hw.h` also includes MAC/PHY/NVM/mailbox headers after core type definitions. Prototype drift affects many modules.

## Test Signals
Full IGB build and sparse/prototype checking catch most integration issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mbx.c

## Purpose
Implements PF-side mailbox operations for IGB SR-IOV communication with VFs.

## Important APIs, Types, And Functions
Public wrappers are `igb_read_mbx`, `igb_write_mbx`, `igb_check_for_msg`, `igb_check_for_ack`, `igb_check_for_rst`, `igb_unlock_mbx`, and `igb_init_mbx_params_pf`. Internal routines implement posted read/write polling, PF interrupt-bit checks, mailbox lock acquire/release, and MMIO mailbox memory copy through `E1000_VMBMEM`.

## Control Flow
Wrapper functions validate size or operation availability and dispatch through `hw->mbx.ops`. Posted operations poll for message or ack until `mbx->timeout` expires; timeout zero disables future posted messages until reset. PF read/write obtains mailbox ownership with `E1000_P2VMAILBOX_PFU`, flushes pending message/ack bits when writing, copies words, then signals VF with `STS` or acknowledges with `ACK`.

## State And Persistence
Updates mailbox MMIO registers, clears interrupt cause bits, updates `hw->mbx.stats` counters for messages, acks, requests, and resets, and stores operation pointers/size/timeouts in `hw->mbx`. State is volatile device/runtime state.

## Dependencies And Integration
Depends on `e1000_hw.h` register access macros and `e1000_mbx.h` protocol constants. Initialized by 82576/I350 setup in `e1000_82575.c` when SR-IOV-capable hardware is detected.

## Risks
Mailbox locking is race-sensitive between PF and VF. Size truncation/read bounds must match the 16-word mailbox. Timeout handling can permanently disable posted operations until reset. Incorrect ACK/STS/PFU handling can deadlock VF requests.

## Test Signals
SR-IOV enablement, VF reset detection, VF request/ACK interrupt bits, PF-to-VF and VF-to-PF mailbox messages, mailbox timeout injection, and stats counter checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mbx.h

## Purpose
Defines the IGB PF/VF mailbox protocol constants and declares mailbox helper APIs.

## Important APIs, Types, And Functions
Defines `E1000_P2VMAILBOX_*` ownership/status bits, `E1000_MBVFICR_*` request/ack masks, mailbox size, VT message type flags (`ACK`, `NACK`, `CTS`), VF request opcodes, MAC filter subcommands, promiscuous-mode subcommand, and `E1000_PF_CONTROL_MSG`. Declares read/write/check/unlock/init functions.

## Control Flow
No executable flow. Constants are consumed by `e1000_mbx.c` and SR-IOV PF/VF control paths.

## State And Persistence
Describes volatile mailbox register state and message words shared between PF and VFs.

## Dependencies And Integration
Includes `e1000_hw.h` for `struct e1000_hw`. Integrated into `struct e1000_mbx_operations` and initialized for supported hardware families.

## Risks
Protocol bit mistakes can break PF/VF negotiation, MAC/VLAN programming, reset handling, or promisc requests. Message info bits share the high word with ACK/NACK/CTS flags and must be masked consistently.

## Test Signals
SR-IOV mailbox ABI tests, VF driver compatibility, reset request handling, MAC/VLAN filter requests, and mailbox size boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_mbx.h -->
