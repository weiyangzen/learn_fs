<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.h

## Purpose
`smc91x.h` is the hardware abstraction and register-definition header for the SMSC/SMC 91C9x/91C1xx Ethernet family used by the `smc91x` driver. It does not register a netdev by itself; instead it gives the C driver portable macros for banked register selection, FIFO data movement, MMU packet allocation, MII bit access, multicast table writes, platform quirks, and private driver state.

## Important APIs, Types, and Functions
The central type is `struct smc_local`, which holds deferred TX state, tasklet/work items, optional power/reset GPIOs, chip revision, cached TX/RX/RPC/CTL modes, MII state, locks, optional PXA DMA state, MMIO bases, data-CS aliasing, bus shift/alignment quirks, and platform data. Important access macros include `SMC_inb/inw/inl`, `SMC_outb/outw/outl`, `SMC_ins*`, `SMC_outs*`, `SMC_SELECT_BANK`, `SMC_GET_*`, `SMC_SET_*`, `SMC_PUSH_DATA`, and `SMC_PULL_DATA`. Register groups cover bank 0 TX/RX/EPH/RPC, bank 1 address/config/control, bank 2 MMU/FIFO/pointer/interrupts, bank 3 multicast/MII/revision, bank 7 external registers, and SMC91C96 attribute-space ECOR/ECSR.

## Control Flow
The runtime driver selects a bank, uses the generated register offsets, and transfers packets through the device data register. TX flow allocates packet memory through `MMU_CMD`, selects packet numbers with `PN_REG`, writes packet headers and payload via `SMC_PUT_PKT_HDR` and `SMC_PUSH_DATA`, then enqueues the frame. RX flow reads the FIFO, pointer, packet header, and payload via `SMC_GET_PKT_HDR` and `SMC_PULL_DATA`, then releases packet memory through MMU commands. Interrupt handling relies on `SMC_GET_INT`, `SMC_ACK_INT`, and `SMC_SET_INT_MASK`; MII accesses are bit-level through `MII_REG`.

## State and Persistence Behavior
The header defines volatile hardware state: selected bank, interrupt masks, packet memory pages, PHY mode, MAC address registers, multicast hash table, and power/reset pins. Persistent state may be affected indirectly by EEPROM reload/store control bits, but this file only defines the bits. Cached driver state lives in `struct smc_local`, especially pending TX skb, work state, MII, cached mode registers, and platform access flags.

## Dependencies and Integration Points
It depends on `linux/smc91x.h`, DMA engine APIs, MII/netdevice types, and arch-specific I/O primitives. ARM, Atari, ColdFire, default MMIO, PXA DMA, data-CS, endian, and alignment paths are integrated by preprocessor selection. The header assumes the including C file provides names such as `lp`, `ioaddr`, `dev`, `CARDNAME`, and `SMC_DEBUG`.

## Risks
Risks are macro side effects, hidden dependencies on local variable names, bank-selection mistakes, non-atomic 8/16-bit fallback accesses, write alignment workarounds, and platform-specific DMA/cache ordering. Changing register constants or access macros can silently break old boards. `BUG()` stubs catch impossible bus-width paths but turn misconfiguration into hard failures.

## Test Signals
Useful signals are successful probe on 8/16/32-bit buses, correct bank debug checks under `SMC_DEBUG`, TX/RX with odd and aligned packet buffers, multicast/promiscuous mode updates, MII link negotiation, PXA DMA and non-DMA RX, netpoll if enabled, and EEPROM reload/store paths on hardware that supports them. Build coverage should include ARM/PXA, ColdFire big-endian 16-bit, and generic MMIO configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.c

## Purpose
`smsc911x.c` is the platform driver for SMSC LAN911x/LAN921x/LAN922x/LAN9250 Ethernet controllers. It implements MMIO register and FIFO access, MDIO/phylib integration, netdev open/stop/xmit, NAPI receive, interrupt handling, multicast filtering, ethtool register/EEPROM access, power management, and device-tree/ACPI/platform-data configuration.

## Important APIs, Types, and Functions
The main private state is `struct smsc911x_data`, containing MMIO base, chip ID/generation, copied `smsc911x_platform_config`, MAC and device spinlocks, MDIO bus, PHY state, NAPI, multicast workaround state, register ops, regulators, reset GPIO, and clock. `struct smsc911x_ops` abstracts normal versus shifted register maps. Core routines include `smsc911x_reg_read/write`, FIFO helpers, `smsc911x_mac_read/write`, `smsc911x_mii_read/write`, `smsc911x_soft_reset`, `smsc911x_open`, `smsc911x_stop`, `smsc911x_hard_start_xmit`, `smsc911x_poll`, `smsc911x_irqhandler`, `smsc911x_drv_probe/remove`, and suspend/resume callbacks.

## Control Flow
Probe acquires memory and IRQ resources, maps registers, enables regulators/clock, parses firmware or platform data, selects shifted or standard ops, initializes chip identity/byte order, resets PHY/MAC, creates an MDIO bus, registers NAPI/netdev, and resolves the MAC address from firmware, platform data, EEPROM, saved hardware state, or random fallback. Open runtime-resumes the parent, connects to the PHY if needed, soft-resets hardware, configures FIFOs/GPIO/IRQ polarity, self-tests the interrupt path with a software interrupt, starts the PHY, enables NAPI, enables RX/TX interrupts, enables MAC RX/TX, and starts the queue. TX writes two command words and skb data into the TX FIFO, updates/free statuses, and stops the queue when FIFO space is low. RX IRQ disables RX interrupt and schedules NAPI; `smsc911x_poll` drains RX statuses, discards bad packets, reads FIFO payload into skbs, and reenables RX interrupts when complete.

## State and Persistence Behavior
Runtime state includes hardware FIFOs, interrupt masks/status, MAC CSR state, PHY registers, NAPI state, netdev counters, cached duplex/carrier, multicast hash data, and regulator/clock runtime PM state. EEPROM is persistent and exposed through ethtool byte reads/writes after explicit enable/disable write commands. MAC address persistence is conditional: `smsc,save-mac-address` preserves a bootloader-programmed address across reset; otherwise EEPROM/config/random sources are used.

## Dependencies and Integration Points
The driver integrates Linux platform bus, OF/ACPI property APIs, regulator and clock frameworks, GPIO descriptor reset, phylib/MDIO, NAPI/netdev, ethtool, runtime PM, and optional architecture hooks from `smsc911x.h`. Device-tree properties include `reg-io-width`, `reg-shift`, `phy-mode`, `smsc,irq-active-high`, `smsc,irq-push-pull`, PHY forcing flags, save-MAC flag, supplies, clock, and reset GPIO.

## Risks
High-risk areas are access width/shift mismatch, byte/word swapping, ordering around MAC CSR busy polling, early-generation multicast update restrictions, PHY energy-detect reset quirks, IRQ self-test failures, EEPROM timeout handling, and cleanup ordering across probe/open failures. `pm_runtime_get_sync()` return values are not always checked. The optional PHY loopback workaround can fail probe on marginal PHY paths.

## Test Signals
Test with 16-bit and 32-bit MMIO, shifted and non-shifted register maps, internal/external PHY selection, active-high/open-drain and push-pull IRQ modes, VLAN-sized frames, multicast/promiscuous modes on old and new generations, ethtool register/EEPROM reads and guarded writes, suspend/resume with wake settings, runtime PM cycling, and fault injection for regulator/clock/IRQ/MDIO allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.h

## Purpose
`smsc911x.h` is the local register and bitfield contract for the LAN911x/LAN921x platform driver. It defines chip IDs, FIFO thresholds, EEPROM size, NAPI weight, debug macros, optional PHY loopback workaround, direct register offsets, indirect MAC CSR offsets, PHY interrupt bits, and architecture hook points.

## Important APIs, Types, and Functions
There are no exported functions or structures in this header. Its API is the macro set consumed by `smsc911x.c`: chip ID constants such as `LAN9115`, `LAN9218`, `LAN9221`, `LAN9250`, `LAN89218`; FIFO and status registers such as `RX_DATA_FIFO`, `TX_DATA_FIFO`, `RX_STATUS_FIFO`, `TX_STATUS_FIFO`, `ID_REV`, `INT_CFG`, `INT_STS`, `INT_EN`, `FIFO_INT`, `RX_CFG`, `TX_CFG`, `HW_CFG`, `PMT_CTRL`, `GPIO_CFG`, `MAC_CSR_CMD`, `E2P_CMD`; and indirect MAC registers such as `MAC_CR`, `ADDRH`, `ADDRL`, `HASHH`, `HASHL`, `MII_ACC`, `MII_DATA`, `FLOW`, `VLAN1`, `WUCSR`.

## Control Flow
The header shapes driver control flow by naming the bits that gate reset, FIFO movement, interrupt enable/ack, MAC CSR read/write, MII transactions, EEPROM commands, wake events, GPIO LEDs, and PHY status. `SMSC_WARN` and `SMSC_TRACE` compile to `netif_*` logging only when `USE_DEBUG` is raised; otherwise they compile to `no_printk`. `SMSC_ASSERT_MAC_LOCK` integrates lockdep for indirect MAC accesses when spinlock debugging is enabled. `SMSC_INITIALIZE()` and `smsc_get_mac()` are default hooks that can be overridden by `CONFIG_SMSC911X_ARCH_HOOKS`.

## State and Persistence Behavior
The defined registers represent volatile device state: FIFO occupancy, interrupt latches, MAC enable bits, GPIO/LED configuration, PHY power and wake bits, and MDIO transaction state. EEPROM command/data macros expose persistent storage operations when called by the ethtool code. The header itself stores no state.

## Dependencies and Integration Points
It includes `linux/smscphy.h` and optionally `asm/smsc911x.h`. It is tightly coupled to `smsc911x.c` and to firmware bindings that supply compatible devices, bus width, shift, IRQ polarity/type, PHY mode, supplies, reset GPIO, and MAC-address properties.

## Risks
Changing constants can corrupt MMIO or EEPROM operations. Some names represent device-specific behavior only present on selected chips, such as external PHY control on 9115/9117 and 32/16-bit mode on 9116/9118. `USE_PHY_WORK_AROUND` is enabled at header level, so build-time changes affect probe behavior. Debug macro changes can hide or expose logging in timing-sensitive paths.

## Test Signals
Build and boot-test every supported ID family, verify `BYTE_TEST`/`WORD_SWAP`, reset through `HW_CFG` and LAN9250 `RESET_CTL`, MDIO read/write through `MII_ACC`, interrupt enable/status bits, EEPROM read/write commands, WOL/PMT transitions, and multicast hash programming through `HASHH/HASHL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc9420.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc9420.c

## Purpose
`smsc9420.c` is the PCI Ethernet driver for the SMSC LAN9420 controller. It manages PCI enablement, BAR mapping, coherent DMA descriptor rings, MDIO/phylib, netdev operations, NAPI RX, interrupt handling, multicast filtering, EEPROM/register ethtool operations, and simple PCI PM suspend/resume.

## Important APIs, Types, and Functions
Private state is held in `struct smsc9420_pdata`: MMIO base, PCI/netdev pointers, coherent TX/RX descriptor rings, per-ring skb/DMA metadata, ring indices, locks, NAPI, software IRQ test flag, RX checksum flag, MDIO bus, and cached link state. `struct smsc9420_dma_desc` is the four-word hardware descriptor. Key routines include `smsc9420_probe/remove`, `smsc9420_open/stop`, `smsc9420_hard_start_xmit`, `smsc9420_rx_poll`, `smsc9420_isr`, `smsc9420_alloc/free_{tx,rx}_ring`, `smsc9420_mii_read/write`, `smsc9420_check_mac_address`, and ethtool EEPROM/register helpers.

## Control Flow
Probe enables the PCI function, requests regions, sets a 32-bit DMA mask, maps BAR 3 with big-endian offset handling, allocates one coherent block for RX and TX descriptors, validates `ID_REV`, resets DMAC, reloads EEPROM, sets or discovers the MAC address, registers NAPI and netdev, and initializes locks. Open disables and acknowledges interrupts, requests a shared IRQ, resets DMAC, configures MAC/GPIO/bus mode/DMA control, self-tests the ISR with a software interrupt, allocates descriptor rings and RX skbs, creates an MDIO bus for internal PHY address 1, starts PHY/NAPI, enables MAC and DMA RX/TX, unmasks DMA interrupts, wakes the queue, and kicks RX DMA. TX maps one skb into a TX descriptor and rings `TX_POLL_DEMAND`; RX NAPI consumes descriptors no longer owned by DMA, unmaps the buffer, builds skb state, handles optional RX checksum, updates stats, allocates replacements, kicks RX DMA, and reenables RX interrupts.

## State and Persistence Behavior
State includes coherent rings, per-descriptor skb mappings, DMAC registers, MAC address/hash registers, PHY link state, NAPI state, stats, interrupt masks, and PCI device state. EEPROM is persistent and exposed via ethtool with `SMSC9420_EEPROM_MAGIC`; writes are single-byte erase/write cycles bracketed by write-enable/write-disable commands. Suspend tears down active rings/IRQ and detaches the device; resume reopens the running device.

## Dependencies and Integration Points
The driver integrates PCI core, DMA mapping/coherent allocation, NAPI/netdev, phylib/MDIO, ethtool, VLAN frame handling, CRC multicast hashing, and generic PM. It is bound by PCI vendor/device IDs from `smsc9420.h` and uses register definitions from that header.

## Risks
High-risk areas include descriptor ownership and memory barriers, queue full detection with a small TX ring, RX replacement allocation failures, checksum trailer length adjustment, interrupt masking/reenabling, PCI write flushing, resume using full `open()`, and cleanup symmetry after open/probe failures. `smsc9420_poll_controller()` passes `dev` where the ISR expects private data, which is suspicious under netpoll builds.

## Test Signals
Validate PCI probe/remove, IRQ self-test, TX/RX under ring pressure, RX checksum enabled/disabled, multicast hash programming, ethtool EEPROM magic enforcement, MDIO PHY address 1 negotiation, suspend/resume while up and down, DMA mapping fault injection, and netpoll/controller builds if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc9420.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc9420.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc9420.h

## Purpose
`smsc9420.h` defines the LAN9420 PCI controller constants consumed by `smsc9420.c`: ring sizes, interrupt coalescing value, PCI BAR and IDs, endian register-map offset, EEPROM parameters, packet buffer size, DMAC registers, descriptor bitfields, MAC registers, interrupt registers, GPIO/EEPROM registers, and bus arbitration bits.

## Important APIs, Types, and Functions
This header has no functions or types. Important constants include `TX_RING_SIZE`, `RX_RING_SIZE`, `INT_DEAS_TIME`, `SMSC_BAR`, `LAN9420_CPSR_ENDIAN_OFFSET`, `PCI_VENDOR_ID_9420`, `PCI_DEVICE_ID_9420`, `SMSC9420_EEPROM_SIZE`, `SMSC9420_EEPROM_MAGIC`, and `PKT_BUF_SZ`. Register groups cover `BUS_MODE`, `TX_POLL_DEMAND`, `RX_POLL_DEMAND`, descriptor base registers, `DMAC_STATUS`, `DMAC_CONTROL`, `DMAC_INTR_ENA`, descriptor bits `TDES*` and `RDES*`, MAC registers `MAC_CR`, `ADDRH/L`, hash registers, `MII_ACCESS/DATA`, `FLOW`, `VLAN1/2`, `COE_CR`, system interrupt registers, `GPIO_CFG`, `BUS_CFG`, `PMT_CTRL`, `E2P_CMD`, and `E2P_DATA`.

## Control Flow
The constants drive ring allocation and ownership checks, TX/RX DMA startup and stop, interrupt acknowledgement, MDIO busy polling, MAC filter configuration, checksum offload enablement, EEPROM commands, and endian-aware MMIO mapping. TX descriptors use `TDES0_OWN_` and `TDES1_*` bits; RX descriptors use `RDES0_OWN_`, frame length, first/last, error, and multicast bits.

## State and Persistence Behavior
The header models volatile hardware state in descriptor rings and registers. EEPROM constants identify persistent byte storage and guard ethtool writes with a magic value. It does not own memory or mutate state directly.

## Dependencies and Integration Points
It relies on common kernel `BIT()` definitions through the including C file and is tightly paired with `smsc9420.c`. Integration points are PCI device matching, DMA descriptor layout, MDIO/phylib registers, ethtool EEPROM APIs, and netdev feature configuration.

## Risks
Incorrect descriptor bits or ring sizes can produce DMA memory corruption or permanent queue stalls. `PKT_BUF_SZ` includes VLAN size, alignment, and CRC/checksum slack; changing it affects RX handoff assumptions. `LAN9420_CPSR_ENDIAN_OFFSET` is critical on big-endian hosts because registers are duplicated at a different offset.

## Test Signals
Build on little- and big-endian configurations, verify BAR 3 mapping, descriptor wrap bits at the last ring entries, RX/TX DMA stop status, MDIO busy bit behavior, RX checksum trailer handling, EEPROM magic/read/write commands, and interrupt deassertion programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc9420.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Kconfig

## Purpose
`socionext/Kconfig` exposes build configuration for Socionext Ethernet drivers. It creates a vendor menu gate and two driver symbols: UniPhier AVE and SynQuacer NETSEC.

## Important APIs, Types, and Functions
The symbols are `NET_VENDOR_SOCIONEXT`, `SNI_AVE`, and `SNI_NETSEC`. `NET_VENDOR_SOCIONEXT` is a boolean vendor selector defaulting to `y`; choosing `n` hides child questions without directly changing object selection. `SNI_AVE` is a tristate depending on `(ARCH_UNIPHIER || COMPILE_TEST) && OF` and `HAS_IOMEM`, selecting `MFD_SYSCON` and `PHYLIB`. `SNI_NETSEC` is a tristate depending on `(ARCH_SYNQUACER || COMPILE_TEST) && OF`, selecting `PHYLIB`, `PAGE_POOL`, and `MII`.

## Control Flow
Kconfig evaluation first asks the vendor gate. If enabled, the AVE and NETSEC driver prompts become visible when dependency expressions are true. The selected symbols then feed the directory Makefile to compile `sni_ave.o` or `netsec.o` built-in or as modules.

## State and Persistence Behavior
The file stores build-time configuration only in `.config`; it has no runtime state. The choices persist across kernel builds through normal Kconfig configuration storage.

## Dependencies and Integration Points
This file integrates the drivers with the kernel configuration system, architecture gates, OF availability, I/O memory support, phylib, page pool, MII helpers, and the local Makefile. `SNI_NETSEC` also matches capabilities used by `netsec.c`, including page-pool backed RX and MDIO operations.

## Risks
Overly strict dependencies can hide drivers from compile-test coverage; overly loose dependencies can cause build failures on unsupported platforms. Missing `select` lines would surface as unresolved symbols for PHYLIB, PAGE_POOL, or MII functionality. The vendor gate can make a driver appear unavailable even when its direct dependencies are satisfied.

## Test Signals
Run Kconfig/build matrix coverage for `ARCH_UNIPHIER`, `ARCH_SYNQUACER`, and `COMPILE_TEST`; build `SNI_AVE` and `SNI_NETSEC` as built-in and modules; confirm `netsec.ko` naming; and check that disabling `NET_VENDOR_SOCIONEXT` hides prompts without unexpected object builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Makefile

## Purpose
`socionext/Makefile` maps Socionext Ethernet Kconfig symbols to object files. It is the build-system bridge from `.config` choices to driver compilation.

## Important APIs, Types, and Functions
The relevant build rules are `obj-$(CONFIG_SNI_AVE) += sni_ave.o` and `obj-$(CONFIG_SNI_NETSEC) += netsec.o`. There are no C APIs, runtime types, or functions.

## Control Flow
Kbuild expands the `obj-*` assignments after Kconfig resolves each symbol. `y` links the object into the built-in driver tree; `m` compiles it as a module; empty or `n` omits it. The file is included from the parent Ethernet driver Makefile during kernel build traversal.

## State and Persistence Behavior
The file has no runtime state. Build output state is limited to generated objects/modules according to Kconfig settings.

## Dependencies and Integration Points
It integrates with `drivers/net/ethernet/socionext/Kconfig` and the C sources `sni_ave.c` and `netsec.c`. The `netsec.o` target is the output for the `netsec.c` driver researched in this subset.

## Risks
Misspelled symbols or object names silently break builds or omit drivers. Adding multi-object drivers later would require composite object variables, not just a single `obj-*` line. License headers are present and should remain consistent with kernel build files.

## Test Signals
Build with `CONFIG_SNI_AVE=y/m/n` and `CONFIG_SNI_NETSEC=y/m/n`, verify generated `sni_ave.o`/`netsec.o` or modules, and run `make M=drivers/net/ethernet/socionext` for targeted build feedback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/netsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/netsec.c

## Purpose
`netsec.c` is the platform driver for the Socionext SynQuacer NETSEC Gigabit Ethernet controller. It implements MMIO register access, indirect GMAC/MDIO access, descriptor rings, page-pool RX, XDP, TX checksum/TSO offload, NAPI, ethtool coalescing, OF/ACPI probing, runtime PM, microcode loading from an EEPROM memory resource, and phylib integration.

## Important APIs, Types, and Functions
Core state is `struct netsec_priv`, containing TX/RX rings, ethtool coalescing, XDP program pointer, locks, NAPI, PHY interface/address, MDIO bus, MMIO and EEPROM mappings, clock, frequency, and checksum feature state. `struct netsec_desc_ring` tracks coherent descriptors, software descriptors, head/tail, page pool, XDP RXQ, and TX lock. `struct netsec_de` is the hardware descriptor. Key routines include `netsec_probe/remove`, `netsec_of_probe`, `netsec_acpi_probe`, `netsec_register_mdio`, `netsec_netdev_init/uninit/open/stop/start_xmit`, `netsec_napi_poll`, `netsec_process_rx`, `netsec_clean_tx_dring`, `netsec_reset_hardware`, `netsec_start_gmac/stop_gmac`, `netsec_xdp_setup/xmit`, and runtime PM callbacks.

## Control Flow
Probe maps MMIO and EEPROM resources, obtains IRQ and MAC address, parses OF or ACPI PHY information and clock frequency, validates hardware revision, adds NAPI, sets netdev features including RX checksum, GSO, IP checksum, IPv6 checksum and XDP features, registers MDIO, sets a 40-bit DMA mask if possible, and registers the netdev. `ndo_init` allocates coherent TX/RX descriptor rings, powers the PHY down while resetting hardware and loading microcode, then restores PHY state. Open runtime-resumes clocks, initializes TX descriptors, creates page-pool-backed RX descriptors, requests IRQ, connects the PHY through OF or direct phylib, starts PHY/GMAC/NAPI/queue, and unmasks TX/RX interrupts. IRQ clears TX/RX status, masks top-level interrupts, and schedules NAPI. NAPI completes TX descriptors, receives packets, runs XDP actions, builds recycled skbs for pass traffic, refills RX descriptors, and reenables interrupts when work is complete. Stop disables queue/NAPI/IRQs/GMAC, frees rings, disconnects PHY, resets hardware without reloading microcode, and runtime-suspends.

## State and Persistence Behavior
Volatile state includes hardware mode, microengine status, descriptor rings, DMA mappings, page pool pages, XDP program, IRQ masks, coalescing registers, PHY state, MAC mode, netdev stats, and runtime PM clock state. The EEPROM resource is read-only from this driver’s perspective for MAC address and microcode region addresses/sizes; the driver maps and streams those microcode regions into command buffers during reset. No persistent writes are performed.

## Dependencies and Integration Points
The driver depends on platform devices, OF/ACPI property APIs, OF MDIO, phylib, clock/runtime PM, DMA coherent and streaming APIs, page_pool, XDP/BPF, NAPI, ethtool netlink coalescing, and checksum helpers. It matches `socionext,synquacer-netsec` and ACPI `SCX0001`. DT requires `phy-mode`, `phy-handle`, clock, MMIO, EEPROM, and IRQ resources; ACPI requires `phy-channel` and `socionext,phy-clock-frequency`.

## Risks
Key risks are indefinite busy loops in reset/mode transitions, descriptor ownership/barrier mistakes, TX cleanup accounting with XDP buffers, page-pool lifetime during stop/XDP reconfiguration, unsupported jumbo frames with XDP, firmware quirks around Developerbox PHY mode, EEPROM microcode address validity, 40-bit DMA fallback behavior, and runtime PM clock access on ACPI paths where `priv->clk` may be absent. `netsec_xdp_setup()` stops and reopens a running device, so failures can disrupt live links.

## Test Signals
Validate OF and ACPI probe paths, hardware revision rejection, MDIO reads/writes and dummy-read workaround, microcode loading and code-load-end status, runtime suspend/resume clock gating, link changes across 10/100/1000 and RGMII/GMII modes, TX checksum/TSO, RX checksum feature toggles, NAPI coalescing settings, XDP PASS/DROP/TX/REDIRECT and `ndo_xdp_xmit`, jumbo MTU behavior, ring exhaustion, IRQ masking/reenabling, and stop/open cycles under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/netsec.c -->
