# subset-b-004349 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/reg.h

## Purpose
`reg.h` is the register map and bitfield contract for the newer `alx` Atheros/Qualcomm Ethernet driver family. It contains no executable code; its job is to give the driver stable names for PCI device IDs, PCIe capability registers, MAC/DMA/RX/TX queue registers, interrupt bits, Wake-on-LAN controls, RSS/MSI tables, MIB counters, and PHY/MDIO debug and extension registers.

## Important APIs, types, and definitions
The file exports preprocessor constants only. Key groups are `ALX_DEV_ID_*` device IDs, revision constants, PCIe power-management fields such as `ALX_PMCTRL_*`, MAC/DMA reset fields such as `ALX_MASTER_DMA_MAC_RST`, MDIO access fields such as `ALX_MDIO_*` and `ALX_MDIO_EXTN_*`, descriptor queue address/index registers such as `ALX_RFD_ADDR_LO`, `ALX_RRD_ADDR_LO`, `ALX_TPD_PRI*_PIDX`, MAC configuration bits in `ALX_MAC_CTRL_*`, interrupt bits in `ALX_ISR_*`, and MIB offsets under `ALX_MIB_*`.

The PHY section defines standard and vendor-specific MII addresses, including `ALX_MII_GIGA_PSSR` for resolved speed/duplex, debug registers such as `ALX_MIIDBG_*`, and MMD extension register names under `ALX_MIIEXT_*`. These definitions are consumed by low-level MDIO routines, link setup code, power-saving code, stats collection, and WoL programming in the `alx` driver.

## Control flow and state behavior
There is no runtime control flow. The state modeled here is hardware state: MMIO registers, producer/consumer indices, interrupt state, MAC/PHY power modes, and MIB counters. Persistence is in hardware registers and nonvolatile EEPROM/eFuse areas addressed through the named load and MDIO registers. Driver correctness depends on using these masks consistently with read-modify-write operations, because many fields share registers with unrelated hardware controls.

## Dependencies and integration points
This header depends on kernel bit macros such as `BIT()` being available from includers. It is an integration point between the `alx` driver and the Atheros hardware specification. Important external consumers are PCI probe tables, reset sequencing, MAC start/stop, NAPI queue setup, interrupt handling, ethtool stats/register dumps, PHY tuning, WoL, RSS, and MSI/MSI-X setup.

## Risks
The main risks are semantic drift and bitfield mistakes. A wrong mask or offset can silently program link power management, DMA, interrupt, or queue registers incorrectly. Register names also encode hardware-generation quirks, for example B0/C0 WoL and heartbeat fields; using a field on the wrong revision can cause suspend/resume, wake, or link instability. Since constants are not type checked, test coverage must come from compile coverage plus hardware behavior.

## Test signals
Useful signals include successful build of the `alx` driver, probe on all listed PCI IDs, stable link negotiation at 10/100/1000 speeds, clean suspend/resume with and without WoL, ethtool register dump sanity, correct MIB counter increments, RX/TX traffic under interrupt moderation, and no MDIO timeouts during PHY access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/Makefile

## Purpose
This Makefile wires the `atl1c` Ethernet driver into Kbuild. When `CONFIG_ATL1C` is enabled, it builds a single module or built-in object named `atl1c.o`.

## Important APIs, types, and functions
The file has no C APIs. Its important Kbuild declarations are `obj-$(CONFIG_ATL1C) += atl1c.o` and `atl1c-objs := atl1c_main.o atl1c_hw.o atl1c_ethtool.o`. These three objects form the driver: PCI/netdev lifecycle and packet paths in `atl1c_main.o`, hardware/PHY helper code in `atl1c_hw.o`, and ethtool operations in `atl1c_ethtool.o`.

## Control flow and state behavior
There is no runtime control flow. At build time, Kbuild includes the object when the kernel configuration enables the driver. The object list determines link order within the composite driver object and therefore which translation units must satisfy exported symbols such as `atl1c_driver_name`, `atl1c_reset_hw`, `atl1c_reinit_locked`, and `atl1c_set_ethtool_ops`.

## Dependencies and integration points
The Makefile depends on the kernel networking and PCI build environment and on the `CONFIG_ATL1C` Kconfig symbol being defined elsewhere. It integrates the source files with the surrounding `drivers/net/ethernet/atheros` build tree and determines what code is available to modpost and module loading.

## Risks
The object list is small but critical. Omitting `atl1c_ethtool.o` would leave the driver without its ethtool registration helper. Omitting `atl1c_hw.o` would break low-level symbol resolution. Adding source files without updating this list would make new code unused. Since `atl1c-objs` uses assignment, later Makefile edits in the same scope must avoid accidentally replacing the list.

## Test signals
Primary signals are a successful kernel build with `CONFIG_ATL1C=m` and `CONFIG_ATL1C=y`, no unresolved symbols at modpost, `modinfo atl1c` availability for module builds, and runtime probe of supported PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c.h

## Purpose
`atl1c.h` is the private driver header for the Atheros L1C/L2C/L1D family. It collects Linux networking includes, descriptor layouts, ring state, adapter state, offload bit definitions, register access macros, constants for MTU/DMA/timers, and prototypes shared between `atl1c_main.c`, `atl1c_hw.c`, and `atl1c_ethtool.c`.

## Important APIs, types, and functions
The central data type is `struct atl1c_adapter`, which binds `struct net_device`, `struct pci_dev`, `struct atl1c_hw`, hardware stats, MII plumbing, WoL configuration, link state, locks, work/timers, descriptor rings, and queue counts. `struct atl1c_hw` stores MMIO base, PCI identity, NIC type, DMA ordering, link capabilities, PHY state, MAC addresses, interrupt mask, ASPM/control flags, and PHY tuning flags.

DMA state is split into `struct atl1c_ring_header`, `struct atl1c_tpd_ring`, `struct atl1c_rfd_ring`, and `struct atl1c_rrd_ring`. Per-buffer state lives in `struct atl1c_buffer`, with flags recording free/busy state, DMA mapping type, and direction. On-wire/hardware descriptors are `struct atl1c_tpd_desc`, `struct atl1c_tpd_ext_desc`, `struct atl1c_rx_free_desc`, and `struct atl1c_recv_ret_status`.

Important macros include `ATL1C_TPD_DESC`, `ATL1C_RFD_DESC`, `ATL1C_RRD_DESC`, field masks for TX checksum/TSO/VLAN offload, RRS receive status bits, VLAN byte-swap helpers, and `AT_READ_REG`/`AT_WRITE_REG` accessors. The accessors include a hibernate double-read workaround for some register reads.

## Control flow and state behavior
The header does not execute control flow, but it defines the state machine used by the driver. `adapter->flags` tracks testing, resetting, and down state; `adapter->work_event` tracks reset and link-change work; `adapter->irq_sem` gates interrupt enable/disable; ring producer/consumer indices track DMA ownership. Hardware state persists in MMIO registers and descriptors; software state persists in the adapter while the netdev is registered and is rebuilt across open/close or suspend/resume.

## Dependencies and integration points
It depends on Linux PCI, netdevice, ethtool, MII, VLAN, SKB, NAPI, workqueue, checksum, and DMA APIs. `atl1c_main.c` owns most consumers of ring and adapter fields, `atl1c_hw.c` consumes `struct atl1c_hw` and register macros for PHY and EEPROM work, and `atl1c_ethtool.c` exposes selected state to userspace.

## Risks
The descriptor structures and bit masks must match hardware layout exactly. Any mismatch can corrupt DMA, break offload, or misreport RX status. `ATL1C_SET_BUFFER_STATE` and `ATL1C_SET_PCIMAP_TYPE` are macro-based state transitions; callers must set them consistently or cleanup can unmap with the wrong direction/type. `struct atl1c_hw_stats` assumes hardware MIB order matches `atl1c_update_hw_stats()`. The hibernate read workaround makes register access semantics differ from normal readl paths.

## Test signals
Compile coverage is essential because this header is shared widely. Runtime signals include successful RX/TX with SG, checksum, TSO, VLAN acceleration, queue cleanup without DMA API warnings, correct ethtool link/register reporting, and stable reset/suspend paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_ethtool.c

## Purpose
`atl1c_ethtool.c` exposes driver diagnostics and policy controls through ethtool. It reports link capabilities, driver identity, MMIO/PHY register snapshots, EEPROM contents, message level, WoL state, and supports changing advertised speed/duplex settings.

## Important APIs, types, and functions
`atl1c_set_ethtool_ops()` installs `atl1c_ethtool_ops` on the netdev. `atl1c_get_link_ksettings()` maps `adapter->link_speed`, `adapter->link_duplex`, `hw->autoneg_advertised`, and `ATL1C_LINK_CAP_1000M` to the modern `ethtool_link_ksettings` interface. `atl1c_set_link_ksettings()` serializes on `__AT_RESETTING`, translates requested speed/duplex into legacy advertised bits, rejects invalid 1000 half-duplex, and calls `atl1c_restart_autoneg()`.

Diagnostic entry points are `atl1c_get_regs_len()`, `atl1c_get_regs()`, `atl1c_get_eeprom_len()`, `atl1c_get_eeprom()`, and `atl1c_get_drvinfo()`. WoL is handled by `atl1c_get_wol()` and `atl1c_set_wol()`, though the setter only accepts magic packet and PHY/link wake despite reporting conversion code for other `AT_WUFC_*` bits on read. `atl1c_nway_reset()` reinitializes the adapter if the netdev is running.

## Control flow and state behavior
Most functions are synchronous ethtool callbacks. Link setting changes mutate `hw->autoneg_advertised` and restart PHY negotiation without a full netdev down/up. WoL settings mutate `adapter->wol` and call `device_set_wakeup_enable()`, which later affects suspend behavior in `atl1c_main.c`. Register and EEPROM reads snapshot hardware state through MMIO and PHY/EEPROM helpers.

## Dependencies and integration points
This file depends on netdev private data, PCI identity, `atl1c_hw.c` helpers (`atl1c_restart_autoneg`, `atl1c_read_eeprom`, `atl1c_check_eeprom_exist`, `atl1c_read_phy_reg`), and register constants from `atl1c_hw.h`. It is registered by `atl1c_init_netdev()` in the probe path.

## Risks
`atl1c_get_eeprom()` computes `last_dword` inclusively but loops with `i < last_dword`, which skips the last dword for many ranges and leaves part of the allocated buffer unfilled before `memcpy()`. The function also has an unreachable second `return 0` after `return ret_val`. `atl1c_set_link_ksettings()` forces autoneg enabled in reported settings but accepts forced non-autoneg paths by converting speed and duplex into advertised bits, so userspace semantics are somewhat mixed. WoL read code recognizes unicast/multicast/broadcast flags that the setter refuses, so externally visible state can only be a subset unless other code sets those bits.

## Test signals
Use `ethtool <dev>`, `ethtool -s`, `ethtool -d`, `ethtool -e`, and `ethtool -s wol` coverage. Good signals are correct rejection of 1000 half-duplex, successful autoneg restart, register dumps with PHY BMCR/BMSR at the tail, EEPROM reads that include the requested final bytes, and suspend wake behavior matching magic/link settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.c

## Purpose
`atl1c_hw.c` implements low-level hardware services for the ATL1C family: EEPROM/OTP detection and reads, MAC address acquisition/programming, multicast hash calculation, MDIO/PHY access, PHY reset and initialization, link status/speed reporting, autonegotiation restart, low-power link selection, WoL power-save programming, and post-link PHY tuning.

## Important APIs, types, and functions
EEPROM and MAC address functions include `atl1c_check_eeprom_exist()`, `atl1c_read_eeprom()`, `atl1c_read_mac_addr()`, and `atl1c_hw_set_mac_addr()`. `atl1c_get_permanent_address()` first trusts a BIOS-programmed station address, then triggers TWSI/OTP load, with extra voltage handling for L2C_B variants, and falls back to a random address through `atl1c_read_mac_addr()` if permanent address retrieval fails.

PHY access is centered on `atl1c_read_phy_core()` and `atl1c_write_phy_core()`, wrapped by normal, extension, and debug register helpers. They stop FPGA PHY polling when necessary, choose a slow MDIO clock while hibernating on selected chips, program `REG_MDIO_EXTN` for extended access, wait with `atl1c_wait_mdio_idle()`, and restart polling.

Link and power APIs include `atl1c_phy_reset()`, `atl1c_phy_init()`, `atl1c_get_link_status()`, `atl1c_get_speed_and_duplex()`, `atl1c_restart_autoneg()`, `atl1c_phy_to_ps_link()`, `atl1c_power_saving()`, and `atl1c_post_phy_linkchg()`.

## Control flow and state behavior
Initialization flows from reset/tuning to advertisement programming and `BMCR_RESET | BMCR_ANENABLE | BMCR_ANRESTART`. `hw->phy_configured` records whether PHY setup has been done. `hw->autoneg_advertised`, `hw->media_type`, and `hw->link_cap_flags` determine MII advertisement registers. Suspend power saving narrows link advertisement where possible, stores chosen speed/duplex in `adapter`, then programs MAC, master, GPHY, and WoL registers. State persists in hardware registers and in `hw` fields such as `hibernate`, `phy_configured`, and MAC addresses.

## Dependencies and integration points
The file depends on PCI device logging, Linux MII constants, CRC helpers, register constants from `atl1c_hw.h`, and the adapter state from `atl1c.h`. It is called by probe/resume/open/link-change paths in `atl1c_main.c` and by ethtool for EEPROM, link, and autoneg operations.

## Risks
Many operations are hardware-revision-specific. Wrong `nic_type` handling can break L2C_B voltage workarounds, L1D/L2CB EEE disablement, or ASPM/hibernate behavior. MDIO functions return `-1` rather than errno values, so callers must not expose them directly without translation. `atl1c_get_permanent_address()` has early returns on TWSI timeout that can bypass voltage/clock restoration after voltage was raised. The fallback to `eth_random_addr()` keeps the device usable but changes persistence and should set `NET_ADDR_RANDOM` in the caller.

## Test signals
Signals include valid permanent MAC detection, no MDIO timeout logs, successful autoneg at all supported speeds, correct speed/duplex reporting from `MII_GIGA_PSSR`, WoL magic/link wake from suspend, clean resume after hibernation, multicast filtering behavior, and stable link after cable changes on patched platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.h

## Purpose
`atl1c_hw.h` is the hardware register and PHY definition header for `atl1c`. It names MMIO registers, bit masks, field shifts, device IDs, PCIe power controls, DMA/queue controls, interrupt masks, MIB ranges, and PHY debug/MMD registers used by `atl1c_main.c`, `atl1c_hw.c`, and `atl1c_ethtool.c`.

## Important APIs, types, and functions
The only function-like APIs are field helpers `FIELD_GETX`, `FIELD_SETX`, and `FIELDX`, plus prototypes for hardware helper functions implemented in `atl1c_hw.c`. The prototypes cover PHY disable/reset/init, MAC address programming, EEPROM reads, multicast hash programming, MDIO normal/extension/debug access, autoneg restart, power saving, and post-link tuning.

Important register groups include PCI capability and indirect access registers, TWSI/EEPROM/OTP controls, PM/ASPM controls, master reset and interrupt moderation, GPHY control, MDIO controls, MAC control and address registers, WoL controls, SRAM and descriptor base/ring-size registers, TXQ/RXQ/DMA controls, mailbox producer/consumer indices, interrupt status/mask bits, clock gating, and PHY debug/extension registers.

## Control flow and state behavior
This header has no runtime control flow. It defines the hardware state vocabulary that executable code uses for reset sequences, descriptor ring programming, interrupt masking, PHY tuning, EEPROM load, WoL, ASPM, and stats collection. Persistent state may live in EEPROM/OTP or PCI config space; volatile state lives in MMIO registers, PHY registers, and DMA descriptors.

## Dependencies and integration points
It depends on Linux `types.h` and `mii.h`, and on includers providing bit macros. It integrates the driver with Atheros L1C/L2C/L1D hardware revisions and is the authoritative local source for constants consumed by register dump ethtool code, low-level PHY code, probe/reset paths, and TX/RX configuration.

## Risks
Field helper macros are untyped and rely on a strict naming convention where `_MASK` and `_SHIFT` exist. A bad field definition propagates into every read-modify-write call. Some comments document revision-specific behavior, such as L1D v2 timers, L2CB TX FIFO settings, and EEE/AZ registers; applying these generically can cause hardware instability. `IMR_NORMAL_MASK`, `ISR_ERROR`, and `ISR_OVER` define operational interrupt policy, so omissions can hide serious events or produce interrupt storms.

## Test signals
Useful validation includes successful driver compilation, ethtool register dumps matching expected offsets, interrupt delivery and masking under RX/TX load, no DMA hangs after descriptor register programming, correct stats increments from MIB ranges, and stable suspend/resume with ASPM and WoL settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_main.c

## Purpose
`atl1c_main.c` is the main Linux PCI Ethernet driver for ATL1C/L2C/L1D devices. It owns PCI probe/remove, netdev registration, queue allocation, DMA descriptor setup, MAC reset/configuration, NAPI RX/TX handling, interrupt handling, transmit mapping/offloads, link-change work, suspend/resume/shutdown, and PCI error recovery.

## Important APIs, types, and functions
The file registers `atl1c_driver` through `module_pci_driver()` with a PCI ID table for Attansic/Atheros L1C/L2C/L2C_B/L2C_B2/L1D/L1D_2. `atl1c_probe()` enables the PCI device, sets a 32-bit DMA mask, maps BAR0, detects `nic_type`, allocates a multiqueue netdev, installs netdev and ethtool ops, sets NAPI instances, initializes software state, resets PCIe/MAC/PHY, reads/programs the MAC address, and registers the netdev.

The netdev API is `atl1c_netdev_ops`: open/close, start_xmit, set RX mode, change MTU, feature fix/set, MII ioctl, tx timeout, stats, and optional netpoll. Descriptor lifecycle is handled by `atl1c_setup_ring_resources()`, `atl1c_free_ring_resources()`, `atl1c_configure_des_ring()`, `atl1c_reset_dma_ring()`, and ring cleanup helpers. RX is handled by `atl1c_alloc_rx_buffer()` and `atl1c_clean_rx()`. TX is handled by `atl1c_xmit_frame()`, `atl1c_tso_csum()`, `atl1c_tx_map()`, `atl1c_tx_rollback()`, and `atl1c_clean_tx()`.

## Control flow and state behavior
Open allocates DMA rings, configures hardware, requests IRQ, checks link, enables NAPI, unmasks interrupts, and starts queues. Interrupts read `REG_ISR`, acknowledge status, schedule RX/TX NAPI, clear PHY interrupts, and queue reset/link-change work for error or link events. RX NAPI consumes valid RRD entries, unmaps RFD buffers, applies VLAN tags, passes SKBs to GRO, refills RFDs, and re-enables queue interrupts. TX maps SKB head/frags into TPDs, sets checksum/TSO/VLAN fields, rings the producer index, and completion NAPI unmaps/free SKBs and wakes stopped queues.

The adapter state persists while the netdev exists. Hardware state is reset and rebuilt across open/close, link down, reset work, suspend/resume, and PCI error recovery. `__AT_DOWN`, `__AT_RESETTING`, `work_event`, `irq_sem`, NAPI state, and ring indices coordinate concurrency.

## Dependencies and integration points
This file depends on Linux PCI, DMA, NAPI, netdev, MII ioctl, ethtool registration, PM, and PCI error recovery APIs. It depends on `atl1c_hw.c` for MAC/PHY/EEPROM/link helpers and on `atl1c.h`/`atl1c_hw.h` for descriptors and register constants. It integrates with userspace through the netdev, ethtool, MII ioctls, WoL, and module PCI binding.

## Risks
The 32-bit DMA mask is intentional because hardware has a shared high-address register; changing it would require auditing all ring/buffer programming. `atl1c_init_ring_ptrs()` appears to use `buffer_info[i]` inside the inner TX loop instead of `buffer_info[j]`, which can leave most TX buffer states uninitialized. `atl1c_change_mtu()` only changes MTU while running; when down, the new value path relies on core state without updating driver `max_frame_size` immediately. RX currently warns but does not support multi-RFD packets. Error paths around `atl1c_open()` call `atl1c_free_irq()` even after `atl1c_up()` may already have failed before IRQ allocation. Concurrency depends on careful ordering of NAPI disable, IRQ masking, and work cancellation.

## Test signals
Strong signals are probe/remove under module load/unload, RX/TX traffic with checksum, SG, TSO/TSO6, VLAN tag insertion/stripping, MTU changes including jumbo-capable devices, suspend/resume with and without WoL, cable link transitions, netpoll if configured, PCI AER recovery, DMA API debug with no leaks or wrong-direction unmaps, and NAPI interrupt re-enable under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/Makefile

## Purpose
This Makefile wires the `atl1e` Ethernet driver into Kbuild. When `CONFIG_ATL1E` is enabled, Kbuild builds a composite `atl1e.o`.

## Important APIs, types, and functions
The file has no runtime APIs. Its important declarations are `obj-$(CONFIG_ATL1E) += atl1e.o` and `atl1e-objs += atl1e_main.o atl1e_hw.o atl1e_ethtool.o atl1e_param.o`. Compared with `atl1c`, this driver also links `atl1e_param.o`, which likely owns module parameters or option validation referenced by `atl1e_check_options()`.

## Control flow and state behavior
There is no runtime flow. At build time, the selected configuration controls whether the composite object is compiled as a module or built-in. The object list controls which translation units satisfy driver symbols and which features are present in the final binary.

## Dependencies and integration points
It depends on the kernel Kbuild environment and `CONFIG_ATL1E`. It integrates the `atl1e` source directory with the broader Atheros Ethernet build and ensures hardware, ethtool, main driver, and parameter code are linked together.

## Risks
Removing `atl1e_param.o` would break option initialization if `atl1e_main.o` calls `atl1e_check_options()`. Replacing rather than appending to `atl1e-objs` in later Makefile edits could drop required objects. Build-only files are easy to overlook because they have no direct runtime tests, but they are the gate for all driver functionality.

## Test signals
Build with `CONFIG_ATL1E=m` and `CONFIG_ATL1E=y`, check modpost for unresolved symbols, confirm `atl1e.ko` contains main/hw/ethtool/param code, and boot/probe a supported ATL1E device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e.h

## Purpose
`atl1e.h` is the private header for the older Atheros L1E/L2E driver. It defines the driver-wide constants, descriptor formats, adapter/hardware state, RX page model, TX ring model, register access macros, and function prototypes shared by main, hardware, ethtool, and parameter code.

## Important APIs, types, and functions
The key hardware state type is `struct atl1e_hw`, containing MMIO base, memory range, PCI identity, NIC type, MAC addresses, frame thresholds, media/autoneg state, interrupt moderation timers, RSS/RRS type, DMA request sizing, and PHY flags. `struct atl1e_adapter` binds the netdev, pci_dev, NAPI object, MII info, hardware/stats, WoL/link state, locks, reset/link work, timers, DMA ring allocation, TX/RX rings, flags, PCI saved state, and config-space storage.

TX uses `struct atl1e_tpd_desc`, `struct atl1e_tx_ring`, and `struct atl1e_tx_buffer`. RX differs from ATL1C: it uses page-backed receive areas described by `struct atl1e_rx_page`, `struct atl1e_rx_page_desc`, and `struct atl1e_rx_ring`, with read/write offsets instead of a simple RFD/RRD descriptor pair per buffer. Receive status is `struct atl1e_recv_ret_status`.

Macros define TX checksum/segmentation fields, receive status flags/errors, VLAN tag transforms, DMA masks, timer constants, and MMIO accessors. Prototypes expose option checking, up/down/reinit, reset, and ethtool registration.

## Control flow and state behavior
The header has no executable flow, but its structures describe the driver lifecycle. Adapter flags track testing/reset/down state, work items perform reset/link handling, timers handle watchdog and PHY configuration, TX rings track producer/consumer indices, and RX pages track active page plus read/write offsets. Persistent hardware state includes EEPROM/VPD, PCI config, MAC address registers, PHY registers, and MMIO configuration.

## Dependencies and integration points
It depends on Linux PCI, netdevice, MII, ethtool, VLAN, SKB, workqueue, checksum, and DMA APIs, and on `atl1e_hw.h` for register constants. It integrates with `atl1e_hw.c` and `atl1e_ethtool.c`; the Makefile indicates `atl1e_main.c` and `atl1e_param.c` are additional consumers.

## Risks
The receive page model is more stateful than a descriptor-per-buffer model; offset synchronization with hardware is critical. `AT_TPD_TAG_TO_VLAN_TAG` references `_tdp` instead of `_tpd`, which would fail or miscompile if used. Several constants duplicate legacy advertisement names and must stay compatible with ethtool conversion code. Any mismatch in descriptor bit layout can corrupt TSO/checksum/VLAN behavior.

## Test signals
Compile coverage, RX under page wrap and jumbo settings, TX with SG/checksum/TSO, VLAN acceleration, ethtool link setting, suspend/resume, DMA API debug, and MII ioctl behavior are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_ethtool.c

## Purpose
`atl1e_ethtool.c` provides ethtool integration for the ATL1E driver. It reports and changes advertised link modes, dumps selected registers, reads and nominally writes EEPROM/VPD data, reports driver identity, exposes WoL options, and triggers renegotiation/reset.

## Important APIs, types, and functions
`atl1e_set_ethtool_ops()` assigns `atl1e_ethtool_ops` to the netdev. Link reporting is in `atl1e_get_link_ksettings()`, which reports 10/100 support for all devices and 1000 full only for `athr_l1e`, using `adapter->link_speed`, `adapter->link_duplex`, and `hw->autoneg_advertised`. `atl1e_set_link_ksettings()` converts userspace advertising into legacy bits, rejects unsupported gigabit on non-L1E devices and all 1000 half-duplex, updates MII advertisement shadows, sets `hw->re_autoneg`, and restarts the device if needed.

Diagnostics include `atl1e_get_regs_len()`, `atl1e_get_regs()`, `atl1e_get_eeprom_len()`, `atl1e_get_eeprom()`, `atl1e_set_eeprom()`, and `atl1e_get_drvinfo()`. WoL callbacks map only magic and PHY wake to `adapter->wol`. `atl1e_nway_reset()` calls `atl1e_reinit_locked()` when the interface is running.

## Control flow and state behavior
Link setting changes are serialized by `__AT_RESETTING`. Unlike ATL1C, the setter brings the device down/up if running or calls `atl1e_reset_hw()` if stopped, so advertisement changes are applied through a broader reset path. EEPROM set performs read/modify/write handling for unaligned first/last dwords before calling `atl1e_write_eeprom()`.

## Dependencies and integration points
The file depends on `atl1e_hw.c` for EEPROM, reset, and low-level link behavior, and on main driver functions `atl1e_up()`, `atl1e_down()`, and `atl1e_reinit_locked()`. It integrates with userspace through ethtool and with device PM through `device_set_wakeup_enable()`.

## Risks
`atl1e_get_eeprom()` has the same inclusive-range issue as ATL1C: it computes `last_dword` but loops with `i < last_dword`, skipping the final dword. `atl1e_set_eeprom()` can report success even though `atl1e_write_eeprom()` in `atl1e_hw.c` is a stub that always returns true and writes nothing. `atl1e_get_msglevel()` ignores adapter state and returns a compile-time constant based on `DBG`, so ethtool cannot tune runtime logging here. The link setter only supports autoneg-enabled requests and returns `-EINVAL` for forced settings.

## Test signals
Run `ethtool`, `ethtool -s advertise`, `ethtool -d`, `ethtool -e`, `ethtool -E`, and WoL configuration tests. Key expected signals are correct rejection of unsupported 1000 modes, real re-autoneg after advertisement change, EEPROM reads including the last requested bytes, and confirmation that EEPROM writes either truly persist or are disabled to avoid false success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.c

## Purpose
`atl1e_hw.c` implements low-level hardware services for ATL1E/L2E devices: EEPROM/VPD detection and reads, MAC address retrieval/programming, multicast hash setup, MDIO PHY register access, PCIe initialization, PHY advertisement/reset/initialization, MAC/DMA reset, base hardware initialization, link speed/duplex reporting, and autoneg restart.

## Important APIs, types, and functions
EEPROM and identity functions include `atl1e_check_eeprom_exist()`, `atl1e_read_eeprom()`, `atl1e_write_eeprom()`, `atl1e_get_permanent_address()`, `atl1e_read_mac_addr()`, and `atl1e_hw_set_mac_addr()`. `atl1e_check_eeprom_exist()` clears VPD enable in SPI flash control and interprets PCIe capability data; notably it returns `0` when EEPROM exists. `atl1e_get_permanent_address()` triggers TWSI load if EEPROM exists and validates the station address.

PHY access is implemented by `atl1e_read_phy_reg()` and `atl1e_write_phy_reg()`, which program `REG_MDIO_CTRL`, wait for `MDIO_START | MDIO_BUSY` to clear, and return `AT_ERR_PHY` on timeout. `atl1e_phy_setup_autoneg_adv()` derives MII advertisement and 1000T control shadows from `hw->media_type` and `hw->nic_type`. `atl1e_phy_commit()`, `atl1e_phy_init()`, and `atl1e_restart_autoneg()` apply PHY reset/autoneg sequences. `atl1e_reset_hw()` soft-resets MAC/DMA and waits for idle, while `atl1e_init_hw()` initializes PCIe, clears multicast hash, and initializes PHY.

## Control flow and state behavior
Initialization flows through PCIe tweak, multicast hash clear, GPHY reset, PHY debug patch writes, link-change interrupt enable, advertisement setup, and BMCR reset/autoneg restart. `hw->phy_configured` gates repeated initialization; `hw->re_autoneg` requests renegotiation on the next PHY init. Hardware state persists in VPD/EEPROM, station address registers, MDIO registers, and MMIO reset/configuration registers.

## Dependencies and integration points
The file depends on Linux PCI, delay, MII, CRC, and register definitions from `atl1e_hw.h` via `atl1e.h`. It is consumed by main lifecycle code for reset/init/link and by ethtool for EEPROM, register, link, and autoneg operations.

## Risks
`atl1e_write_eeprom()` is a stub that returns true without writing, which makes ethtool EEPROM writes appear successful while doing nothing. `atl1e_check_eeprom_exist()` uses inverted semantics compared with ATL1C, increasing caller confusion risk. MDIO timeout handling logs PCIe linkdown suspicion in `atl1e_phy_commit()` but generally returns coarse driver error constants. PHY init uses hard-coded debug magic values; hardware-revision mistakes can affect link quality or power. `atl1e_read_mac_addr()` returns `AT_ERR_EEPROM` instead of falling back to a random MAC, so caller behavior must handle failure.

## Test signals
Signals include valid MAC retrieval from EEPROM/VPD, no MDIO busy timeouts, successful PHY init and link interrupts, correct speed/duplex from `MII_AT001_PSSR`, stable reset idle detection, multicast hash behavior, ethtool EEPROM read/write truthfulness, and link recovery after advertisement changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_hw.c -->
