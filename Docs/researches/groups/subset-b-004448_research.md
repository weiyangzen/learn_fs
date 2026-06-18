# Research: subset-b-004448

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_main.c

## Purpose
This file is the Linux `e1000` PCI network driver core for older Intel PRO/1000 adapters. It owns PCI registration, `net_device` setup, adapter lifetime, open/close, hardware reset, DMA descriptor rings, NAPI interrupt handling, TX/RX packet paths, VLAN filtering, power management, Wake-on-LAN, PCI error recovery, and several chipset errata workarounds. It bridges the OS networking stack to the shared e1000 hardware layer through `struct e1000_adapter`, `struct e1000_hw`, register macros, and helper routines declared in `e1000.h`.

## Important APIs, Types, and Functions
The exported driver surface is the `pci_driver e1000_driver`, `e1000_pci_tbl`, `e1000_netdev_ops`, PM ops, and PCI error handlers. `e1000_probe()` allocates and initializes `net_device` and adapter state, maps BAR0, configures DMA masks, initializes `e1000_hw`, validates EEPROM, reads the MAC address, installs ethtool/NAPI/netdev ops, applies module options through `e1000_check_options()`, resets hardware, and registers the interface. `e1000_remove()` unwinds that state.

The runtime entry points are `e1000_open()`, `e1000_close()`, `e1000_up()`, `e1000_down()`, `e1000_reinit_locked()`, `e1000_reset()`, `e1000_xmit_frame()`, `e1000_intr()`, and `e1000_clean()`. Ring management is split across setup/free/clean/configure helpers for TX and RX. RX uses function pointers `adapter->clean_rx` and `adapter->alloc_rx_buf` to switch between normal and jumbo paths. The file also exposes OS shim functions used by shared code: `e1000_pci_set_mwi()`, `e1000_pci_clear_mwi()`, `e1000_pcix_get_mmrbc()`, `e1000_pcix_set_mmrbc()`, and `e1000_io_write()`.

## Control Flow
Module load calls `pci_register_driver()`. Probe enables PCI memory or memory plus I/O resources, maps registers, builds software state, validates EEPROM, configures features, and performs an initial reset before `register_netdev()`. Opening an interface allocates TX and RX descriptor memory, powers up the PHY, configures descriptors and filters, requests a shared IRQ, enables NAPI and interrupts, starts the netdev queue, and triggers a link-status software interrupt. Closing/down disables RX/TX in hardware, stops queues, disables NAPI and IRQs, cancels watchdog/PHY/FIFO work, resets hardware, cleans rings, powers down the PHY when allowed, frees IRQs, and releases descriptor resources.

The TX path pads short packets, computes descriptor needs, applies TSO/checksum/VLAN/no-FCS flags, maps skb linear and fragment data for DMA, fills descriptors, uses barriers before ringing the tail register, and stops/wakes the queue based on descriptor availability. The RX path is NAPI driven: the IRQ handler masks interrupts and schedules `e1000_clean()`, which reclaims completed TX descriptors and dispatches the selected RX cleaner. Normal RX builds or copies skbs from fragment-backed buffers; jumbo RX chains pages through GRO fragments. Both paths handle checksum status, VLAN tags, CRC trimming, TBI compatibility, stats, and buffer replenishment.

## State and Persistence
Long-lived state lives in `struct e1000_adapter` and includes rings, flags such as `__E1000_DOWN`, `__E1000_RESETTING`, `__E1000_TESTING`, and `__E1000_DISABLED`, delayed work items, NAPI, VLAN bitmap, management VLAN id, Wake-on-LAN settings, interrupt throttle state, stats snapshots, and hardware-specific workaround fields. Persistent device configuration comes from EEPROM/NVM and module parameters, while runtime state is held in kernel memory and hardware registers. Statistics accumulate in adapter and netdev counters; many hardware counters clear on read.

## Dependencies and Integration Points
The file depends on Linux PCI, DMA mapping, netdevice, NAPI, skb/GRO, VLAN, ethtool, PM, netpoll, and PCI AER/error recovery APIs. It integrates with shared Intel e1000 routines such as MAC type detection, EEPROM validation, PHY register access, autonegotiation, flow control, multicast hashing, VLAN table programming, adaptive IFS, and reset/init helpers. Register access depends on `e1000_osdep.h` macros and on `hw->hw_addr` being mapped.

## Risks
The highest risk areas are descriptor ownership and DMA lifetime, especially on error exits and when TX mapping partially fails. Reset/down races are mitigated with flags, NAPI ordering, IRQ masking, RTNL in reset work, and work cancellation, but changes must preserve those orderings. Hardware errata workarounds for 82542 reset mode, 82544 PCI-X descriptor alignment, 82545/82546 64 KiB boundaries, 82547 FIFO stalls, TBI receive acceptance, and RX IPv4/IPv6/checksum behavior are easy to break. VLAN management and manageability pass-through share hardware filters with the OS and must not drop management VLANs. Power management and error recovery reuse open/down/reset logic and can expose leaks or double-free errors.

## Test Signals
Useful signals include successful module load/unload and PCI probe/remove, `ip link set up/down`, MTU changes including jumbo frames, TX/RX traffic with scatter-gather, TSO, checksum offload, VLAN add/remove, RXALL/RXFCS modes, suspend/resume with and without WoL, PCI error recovery if injectable, ethtool register/stats checks, netpoll/netconsole when configured, and stress loops over reset, link flap, and heavy traffic. Kernel logs should be monitored for EEPROM checksum warnings, DMA map failures, TX hangs, queue stop/wake churn, and allocation failure counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_osdep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_osdep.h

## Purpose
This header is the OS-dependent glue for the legacy `e1000` shared hardware code. It maps generic e1000 register operations onto Linux I/O primitives and hides register layout differences between 82542-era parts and later devices.

## Important APIs, Types, and Functions
It defines MMIO helpers `er32(reg)` and `ew32(reg, value)` for read/write of scalar registers using a local `struct e1000_hw *hw`. It also defines array register helpers for dword, word, and byte widths, `E1000_WRITE_FLUSH()` as a status read flush, ICH flash access helpers, and CE4100-style configuration RAM/flash helpers based on `CONFIG_RAM_BASE`, `GBE_CONFIG_OFFSET`, and `phys_to_virt()`.

## Control Flow
There is no executable control flow beyond macro expansion. Callers pass either the implicit local `hw` variable or an explicit `struct e1000_hw *a`. Each access selects the register offset by checking `mac_type >= e1000_82543`; older 82542 devices use alternate register constants. Writes go through `writel`, `writew`, or `writeb`; reads go through `readl`, `readw`, or `readb`. `E1000_WRITE_FLUSH()` forces posted MMIO writes to reach the device by reading STATUS.

## State and Persistence
The header stores no state. It mutates hardware MMIO registers and flash/config spaces through the caller's mapped base pointers: `hw->hw_addr`, `hw->flash_address`, or CE4100 config address macros. Correct behavior depends on those mappings being valid and on the caller selecting the correct access width and offset.

## Dependencies and Integration Points
It includes `<asm/io.h>` and depends on Linux I/O accessors plus register constants from the e1000 headers. It is used by `e1000_main.c` and shared hardware files to keep register accesses compact and consistent. The implicit `hw` dependency in `er32`/`ew32` is a notable integration convention: functions using those macros must have a local variable named `hw`.

## Risks
Risks are mostly low-level and severe: wrong register selection for 82542 versus later devices, missing flushes after control writes, invalid MMIO pointers after remove/suspend/error recovery, and incorrect word/byte array offset shifts. The CE4100 config macros use physical-to-virtual mapping assumptions and replicated I/O helpers, so misuse can hit the wrong memory-mapped area. Because these are macros, type checking and side-effect protection are limited.

## Test Signals
Build coverage is important because macro users must compile in context. Runtime signals include successful probe/reset/link operations across both older 82542 and newer devices, register dump sanity, EEPROM/flash access where supported, and absence of MMIO faults during suspend/resume, remove, and PCI error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_osdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_param.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_param.c

## Purpose
This file defines and validates legacy `e1000` module parameters. Its job is to translate per-adapter integer arrays supplied at module load into adapter settings for descriptor counts, speed/duplex/autonegotiation, flow control, checksum offload, interrupt moderation, and PHY smart power down.

## Important APIs, Types, and Functions
The `E1000_PARAM()` macro declares parameter arrays and `module_param_array_named()` metadata for up to `E1000_MAX_NIC` boards. `struct e1000_option` describes an enable, range, or list option. `e1000_validate_option()` applies defaults, validates ranges or enumerated values, and logs selected or invalid values. `e1000_check_options()` is the public entry point called during probe after queues and hardware type are known. Link-specific validation is delegated to `e1000_check_fiber_options()` and `e1000_check_copper_options()`.

## Control Flow
Probe assigns `adapter->bd_number`, allocates queues, then calls `e1000_check_options()`. The function checks whether a module parameter was provided for that board index. If present, it validates and stores it; otherwise it uses the option default. Descriptor counts are range-limited by MAC generation and aligned to required descriptor multiples, then copied to all rings. Flow control is stored in both `hw.fc` and `hw.original_fc`. InterruptThrottleRate has special modes: `0` disables, `1` dynamic, `3` dynamic conservative, `4` simplified 2000-8000 interrupts/sec, and other valid values become fixed rates with control bits masked out.

For fiber and internal serdes, Speed and Duplex are ignored, and AutoNeg values other than 1000/full are rejected. For copper, Speed, Duplex, and AutoNeg are validated together. Explicit speed/duplex combinations either force `hw.forced_speed_duplex` or set autonegotiation advertisement masks; incomplete inputs narrow autonegotiation to the requested speed or duplex. The function finally validates MDI/MDI-X compatibility through `e1000_validate_mdi_setting()`.

## State and Persistence
The declared module arrays are global module state populated by the kernel module parameter parser. Adapter-specific results are persisted for the lifetime of the device in `adapter->tx_ring[].count`, `adapter->rx_ring[].count`, `adapter->rx_csum`, interrupt delay fields, `adapter->itr`, `adapter->itr_setting`, `adapter->smart_power_down`, `adapter->fc_autoneg`, and `adapter->hw` link/flow-control fields. No files or NVM are written.

## Dependencies and Integration Points
This file depends on `e1000.h` for adapter, ring, MAC, PHY, descriptor, speed, duplex, and flow-control definitions. Its output feeds `e1000_main.c` ring allocation, RX checksum configuration, interrupt moderation register programming, link setup, and power behavior. It relies on kernel module parameter infrastructure and device logging helpers.

## Risks
Parameter handling is order-sensitive: it requires `adapter->hw.mac_type`, media type, and queue allocation to be initialized before validation. Bad descriptor ranges can waste memory or fail DMA allocation if bounds or alignment rules are changed incorrectly. Speed, Duplex, and AutoNeg interactions can silently force unexpected link modes if validation logic regresses. InterruptThrottleRate mode values overlap with fixed numeric values, so changes must preserve the special-case handling. Board index overflow falls back to defaults, which is safe but can surprise multi-port users.

## Test Signals
Useful tests are module-load permutations for each parameter, including invalid values, sparse per-board arrays, more than 32 adapters, old MAC types with 256-descriptor caps, newer MACs with 4096 descriptors, fiber versus copper link options, forced 10/100 modes, 1000/full autonegotiation, dynamic and fixed ITR settings, checksum offload toggles, and SmartPowerDownEnable. Runtime validation should confirm resulting ring sizes, link mode, ethtool advertised modes, and interrupt throttle register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/80003es2lan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/80003es2lan.c

## Purpose
This file is the `e1000e` hardware-specific implementation for Intel 80003ES2LAN controllers, covering copper and internal serdes variants. It supplies MAC, PHY, and NVM operation tables and implements ESB2-specific reset, initialization, link setup, Kumeran interface access, GG82563 PHY access, semaphores, cable length, power-down, and counter clearing behavior.

## Important APIs, Types, and Functions
The main exported object is `const struct e1000_info e1000_es2_info`, which identifies the MAC type, feature flags, packet buffer allocation, max frame size, variant initializer, and operation tables. `e1000_get_variants_80003es2lan()` initializes MAC, NVM, and PHY parameters. `es2_mac_ops`, `es2_phy_ops`, and `es2_nvm_ops` bind generic e1000e code to this file's callbacks.

Key routines include `e1000_init_mac_params_80003es2lan()`, `e1000_init_nvm_params_80003es2lan()`, `e1000_init_phy_params_80003es2lan()`, `e1000_reset_hw_80003es2lan()`, `e1000_init_hw_80003es2lan()`, `e1000_setup_copper_link_80003es2lan()`, `e1000_copper_link_setup_gg82563_80003es2lan()`, `e1000_cfg_on_link_up_80003es2lan()`, `e1000_read_phy_reg_gg82563_80003es2lan()`, `e1000_write_phy_reg_gg82563_80003es2lan()`, and `e1000_read_kmrn_reg_80003es2lan()`/`e1000_write_kmrn_reg_80003es2lan()`.

## Control Flow
The adapter selects `e1000_es2_info`, then calls `get_variants`, which chooses copper versus serdes behavior, sets register counts, checks firmware/manageability capabilities, derives NVM geometry from EECD, and verifies the GG82563 PHY ID for copper. PHY/NVM/Kumeran access paths acquire software/firmware semaphores through `SW_FW_SYNC`; PHY access additionally selects a GG82563 page before MDIC reads or writes and may apply the MDIC ready-bit workaround with delays and verification.

Reset disables PCIe master, masks interrupts, disables RX/TX, acquires PHY ownership, issues global reset, disables far-end loopback through Kumeran, waits for NVM auto-read, clears pending interrupts, and checks alternate MAC address. Initialization sets ESB2 hardware bits, initializes LED state, clears VLAN and multicast tables, programs receive addresses, sets up link, applies Kumeran/PHY errata, programs TX descriptor write-back policy, enables late-collision retransmit, sets carry-extend padding and TIPG, determines whether the MDIC workaround is needed, and clears hardware counters.

Copper link setup programs SLU and clears forced speed/duplex bits, adjusts Kumeran polling and padding behavior, configures GG82563 MAC/PHY control registers, commits PHY reset, bypasses Kumeran FIFOs, enables electrical idle when manageability is not active, disables padding in MAC and PHY, and then invokes generic copper link setup. On link-up, speed-specific Kumeran/TIPG settings are applied: 1000 Mbps uses gigabit defaults, while 10/100 can enable false-carrier passing for half duplex.

## State and Persistence
Runtime state is stored in `hw->mac`, `hw->phy`, `hw->nvm`, `hw->dev_spec.e80003es2lan.mdic_wa_enable`, operation tables, and hardware registers. EEPROM/NVM is read and written through generic SPI helpers protected by the ESB2 semaphore. Hardware counters are cleared by reads. The file does not persist data outside device NVM, and its writes mainly configure volatile MAC/PHY/Kumeran registers.

## Dependencies and Integration Points
It depends on e1000e core definitions and generic helpers for PCIe master disable, hardware semaphores, NVM SPI/EERD operations, PHY MDIC access, copper/serdes link setup, M88 PHY helpers, MAC address handling, VLAN table clearing, receive address setup, multicast table writes, LED operations, wake/manageability checks, and counter clearing. Constants in `80003es2lan.h` define the ESB2/GG82563 register bits used here.

## Risks
Semaphore handling is critical: missed releases can block firmware, PHY, NVM, or Kumeran access, while missing acquisition can race firmware. The release path spins until the hardware semaphore is acquired, so hardware failure can hang. The MDIC workaround deliberately sleeps and verifies page select; removing it can cause wrong PHY page accesses. Reset and init order is hardware-sensitive, especially PCIe master disable, auto-read completion, interrupt masking, and Kumeran loopback/padding workarounds. Copper versus serdes media selection changes operation pointers, so device-id handling must remain exact.

## Test Signals
Signals include successful probe of copper and serdes ESB2 devices, valid GG82563 PHY ID detection, NVM read/write/checksum operations, reset and init without SW_FW_SYNC timeouts, link-up at 10/100/1000 and half/full combinations where supported, correct TIPG/Kumeran settings after link changes, cable length reporting, suspend or driver unload PHY power-down respecting manageability/reset blocks, VLAN/multicast table initialization, counter clearing, and absence of MDIC page verification failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/80003es2lan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/80003es2lan.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/80003es2lan.h

## Purpose
This header contains ESB2/80003ES2LAN-specific register offsets, bit masks, defaults, and GG82563 PHY constants used by `80003es2lan.c`. It is a hardware-definition companion rather than an executable module.

## Important APIs, Types, and Functions
There are no functions or types. Important constants include Kumeran control/status offsets for FIFO, in-band, half-duplex, and MAC-to-PHY operation mode; FIFO bypass and in-band padding-disable bits; default Kumeran half-duplex control values; operation-mode masks; transmit carry-extend padding masks and defaults; TIPG defaults for 1000 and 10/100 operation; GG82563 crossover, polarity, TX clock, cable-length, false-carrier, electrical-idle, and padding-disable bits; and `GG82563_MAX_KMRN_RETRY`.

## Control Flow
Control flow is entirely in consumers. `80003es2lan.c` uses these constants while configuring copper link, Kumeran workarounds, speed-dependent link-up tuning, forced speed/duplex, init-time descriptor/IPG defaults, and cable length interpretation.

## State and Persistence
The header stores no state. Its constants control writes to volatile MAC, PHY, and Kumeran registers. Some values influence persistent behavior only indirectly when NVM or link configuration routines choose hardware modes, but this header itself performs no reads or writes.

## Dependencies and Integration Points
It is guarded by `_E1000E_80003ES2LAN_H_` and is included through the e1000e driver headers used by `80003es2lan.c`. It aligns with generic e1000e register access macros and GG82563 PHY page/register definitions from the broader driver. The constants are tightly coupled to ESB2 errata and link setup code.

## Risks
Because these constants directly encode hardware bits, incorrect edits can cause link failures, CRC errors, hangs, or broken half-duplex/10/100/1000 behavior. The padding-disable and FIFO-bypass values are used as workarounds; changing them can reintroduce data corruption. The retry count balances stability and delay when validating repeated Kumeran reads.

## Test Signals
Build coverage confirms include compatibility. Runtime signals are indirect: ESB2 link setup succeeds, no CRC/padding anomalies appear under traffic, forced speed/duplex programs the expected TX clock, cable length values are plausible, and Kumeran read validation is stable across link transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/80003es2lan.h -->
