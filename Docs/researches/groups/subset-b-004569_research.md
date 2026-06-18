# Research: subset-b-004569

Grouped research for the requested Micrel and Microchip Ethernet driver files. Each section preserves the source path and is bounded by the reconciliation markers expected by the research cron.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ksz884x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ksz884x.c

## Purpose

`ksz884x.c` is the PCI network driver for Micrel KSZ8841 and KSZ8842 Ethernet devices. KSZ8841 behaves as a single-port PCI Ethernet controller; KSZ8842 adds a two-port switch fabric and can expose either one Linux netdev spanning both physical ports or two separate netdevs in `multi_dev` mode. The file owns the full hardware lifecycle: PCI probe/remove, MMIO register programming, DMA descriptor rings, TX/RX data paths, switch tables, PHY/link management, MIB statistics, ethtool operations, EEPROM access, Wake-on-LAN, suspend/resume, and module parameters.

## Important APIs, Types, And Functions

The main state containers are `struct ksz_hw`, `struct dev_info`, and `struct dev_priv`. `struct ksz_hw` caches MMIO base, switch pointer, per-port link/MIB state, DMA descriptor rings, interrupt masks, MAC/multicast lists, feature flags, and hardware overrides. `struct dev_info` is the shared adapter state behind one PCI function: PCI device, descriptor memory, locks, tasklets, timers, WOL settings, and the active RX routine. `struct dev_priv` is per-netdev state: `struct ksz_port`, MII shim, media state, message level, and multicast/promiscuous reference state.

The descriptor model is split between hardware descriptors (`struct ksz_hw_desc`), software mirrors (`struct ksz_sw_desc`), DMA buffers (`struct ksz_dma_buf`), and ring metadata (`struct ksz_desc_info`). Helpers such as `get_rx_pkt`, `get_tx_pkt`, `release_desc`, `reset_desc`, `set_rx_buf`, and `set_tx_len` encapsulate ring ownership and little-endian writes.

Hardware setup functions include `hw_init`, `hw_reset`, `hw_setup`, `hw_setup_intr`, `hw_set_desc_base`, `hw_enable`, `hw_disable`, `hw_start_rx`, `hw_stop_rx`, `hw_start_tx`, and `hw_stop_tx`. Switch-specific routines include table access (`sw_r_table`, `sw_w_table_64`, `sw_w_sta_mac_table`, `sw_r_vlan_table`), VLAN/STP/priority/mirror/broadcast-storm setup (`sw_setup`, `sw_enable`, `sw_init_stp`, `port_set_stp_state`, `bridge_change`), and per-port link control (`port_get_link_speed`, `port_set_link_speed`, `port_force_link_speed`).

The netdev entry points are collected in `netdev_ops`: `netdev_open`, `netdev_close`, `netdev_tx`, `netdev_tx_timeout`, `netdev_query_statistics`, `netdev_change_mtu`, `netdev_set_features`, `netdev_set_mac_address`, `netdev_ioctl`, and `netdev_set_rx_mode`. Ettool support includes link settings, WOL, register dump, EEPROM read/write, pause settings, ring parameters, message level, and hardware MIB stats through `netdev_ethtool_ops`.

PCI lifecycle is handled by `pcidev_init`, `pcidev_exit`, `pcidev_suspend`, and `pcidev_resume`, registered through `module_pci_driver`.

## Control Flow

Probe (`pcidev_init`) enables the PCI device, validates 32-bit DMA, requests BAR0 memory, maps MMIO, checks chip ID through `hw_init`, allocates descriptor memory, initializes locks/timers/wait queues, reads or overrides MAC addresses, configures base hardware state, optionally allocates `struct ksz_switch`, and registers one or two netdevs. Each netdev is initialized by `netdev_init`, which sets features, MII callbacks, timers, and watchdog parameters.

Open (`netdev_open`) prepares shared hardware on the first open: requests the IRQ, installs RX/TX tasklets, resets hardware, programs descriptor bases and MAC filters, configures jumbo/regular RX behavior, initializes RX buffers, initializes MIB counters, and enables DMA/interrupts. It then powers up the relevant port, configures link speed/autonegotiation, starts the per-netdev monitor timer, sets carrier state, and starts the queue.

TX starts in `netdev_tx`. The function applies a small-packet workaround on affected revisions, reserves descriptors under `hwlock`, copies or maps the skb if descriptor pressure or IPv6 checksum limitations require it, and calls `send_packet`. `send_packet` maps the skb head/fragments for DMA, sets checksum-generation bits for partial checksum skbs, records the skb on the last descriptor, calls `hw_send_pkt`, and updates TX stats. Completion is interrupt-driven: `netdev_intr` schedules `tx_proc_task`, which acknowledges TX interrupts, calls `tx_done`, and `transmit_cleanup` unmaps descriptors, frees skbs, advances ring availability, updates trans time, and wakes stopped queues.

RX is interrupt/tasklet based. `netdev_intr` disables relevant RX interrupt bits and schedules `rx_proc_task`. The tasklet calls the selected receive function (`dev_rcv_packets`, `port_rcv_packets`, or `dev_rcv_special`) until descriptors still owned by hardware are reached. `rx_proc` syncs the DMA buffer for CPU, copies data into a fresh skb with alignment padding, sets protocol, marks checksum verified when enabled, updates stats, and passes the packet via `netif_rx`. Descriptors are released back to hardware immediately after processing.

Close (`netdev_close`) stops the queue and monitor timer, adjusts switch/STP state in multi-netdev mode, decrements filter counters, and on the last close stops MIB monitoring, disables interrupts/DMA, clears multicast, kills tasklets, frees IRQ, cleans TX descriptors, resets rings, and clears static MAC entries when STP support was enabled.

Suspend detaches and closes running netdevs, optionally programs WOL and PCI PME, and enables device wakeup. Resume disables wakeup/PME and reopens/attaches running netdevs.

## State And Persistence

Persistent driver state lives in memory across opens while the PCI function is bound. `struct ksz_hw` caches hardware configuration (`tx_cfg`, `rx_cfg`, interrupt masks, features, override flags), descriptor indices, MAC filters, multicast hash bits, switch tables mirrored in `struct ksz_switch`, per-port link information, and accumulated MIB counters. Descriptor memory is coherent DMA allocated during probe and freed during remove. RX skb buffers are DMA-mapped and recycled through descriptor ownership; TX skbs are freed on descriptor cleanup.

Hardware-persistent state includes MMIO registers, switch table entries, EEPROM contents, MAC registers, PHY registers, and WOL frame CRC/mask registers. The ethtool EEPROM writer modifies the AT93C46 EEPROM using GPIO bit-banged operations, guarded only by caller context and magic validation. Wake settings are stored in `hw_priv->wol_enable` during runtime and are programmed to hardware on set/suspend.

Concurrency state is split across `hwlock` spinlock for interrupt/DMA ring operations, `lock` mutex for slower ethtool/MII feature changes, timers for monitoring, tasklets for IRQ bottom halves, and wait queues for MIB reads. Module parameters (`message`, `macaddr`, `mac1addr`, `fast_aging`, `multi_dev`, `stp`) shape initialization but are not changed dynamically by the driver.

## Dependencies And Integration Points

This is tightly integrated with Linux PCI, netdevice, DMA mapping, ethtool, MII, timer, tasklet, interrupt, and power-management APIs. It depends on MMIO accessors (`readb/readw/readl`, `writeb/writew/writel`), `dma_alloc_coherent`, `dma_map_single`, `request_irq`, `alloc_etherdev`, `register_netdev`, `mii_ethtool_*`, `netif_*` queue/carrier helpers, and `ether_crc`. It includes `linux/micrel_phy.h` for PHY definitions and supports `CONFIG_NET_POLL_CONTROLLER`.

Externally visible integration surfaces are the PCI IDs `0x8841` and `0x8842` under vendor `0x16c6`, standard netdev operations, ethtool operations, MII ioctl handling, module parameters, WOL/PME behavior, and the optional one-netdev/two-netdev switch presentation.

## Risks And Edge Cases

The highest-risk areas are DMA ring ownership and error recovery. TX maps skb fragments without obvious `dma_mapping_error` checks, and error paths rely on later cleanup. RX copies from a preallocated DMA skb into a new skb rather than handing the DMA skb upward, which is simple but costly and depends on correct sync and descriptor release ordering. `netdev_tx_timeout` performs a broad hardware reset and ring rebuild while coordinating multi-netdev users through a static `last_reset`; this deserves stress coverage.

Switch and link handling is old-style and has several behavioral constraints: multi-netdev mode cannot use independent MTUs or multicast hash tables, STP support is parameter-driven, and some bridge behavior is inferred from `netif_is_bridge_port`. WOL ARP programming uses a hard-coded `192.168.1.1` placeholder, so ARP wake is not address-accurate. EEPROM writes are permanent and expose a significant operational risk through ethtool.

Concurrency risks include the mix of spinlocks, tasklets, timers, work items, wait queues, and interrupt masking. MIB reads can block ethtool callers with timeouts, and timers directly call work routines in some paths. The small-packet workaround and IPv6 checksum copy path allocate replacement skbs inside transmit flow; memory pressure can return `NETDEV_TX_BUSY` after stopping the queue.

## Test Signals

Build coverage should include `CONFIG_KSZ884X_PCI` or the relevant Micrel Kconfig path, plus `CONFIG_NET_POLL_CONTROLLER` if that branch matters. Runtime signals include successful PCI probe with chip ID detection, netdev registration count matching KSZ8841 versus KSZ8842 and `multi_dev`, open/close cycles without IRQ/tasklet leaks, TX/RX traffic with scatter-gather and checksum offloads, forced TX timeout recovery, multicast/promiscuous toggles, MTU boundary tests around regular and huge-frame paths, ethtool link/pause/register/EEPROM/stat commands, suspend/resume with and without WOL, and MIB counter monotonicity under link up/down. Hardware-in-loop is effectively required for meaningful validation; static checks should focus on DMA mapping error handling, locking order, and lifecycle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ksz884x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Kconfig

## Purpose

This Kconfig file defines the top-level configuration menu for Microchip Ethernet drivers under `drivers/net/ethernet/microchip`. It gates the vendor menu with `NET_VENDOR_MICROCHIP` and exposes selectable driver symbols for SPI Ethernet controllers, PCI Ethernet devices, and several switch/VCAP/FDMA subdirectories.

## Important Symbols

`NET_VENDOR_MICROCHIP` is a boolean vendor selector defaulting to `y`; disabling it hides the nested Microchip questions without directly changing generated kernel code. `ENC28J60` is a tristate SPI Ethernet controller driver and selects `CRC32`. `ENC28J60_WRITEVERIFY` is a debug bool dependent on `ENC28J60` that enables transmit-buffer write verification. `ENCX24J600` is a tristate SPI driver for ENC424J600/624J600-class devices and depends on `SPI`. `LAN743X` is a PCI driver symbol that depends on `PCI` and `PTP_1588_CLOCK_OPTIONAL`, selecting `FIXED_PHY`, `CRC16`, `CRC32`, and `PHYLINK`.

The file also sources nested Kconfig files for `lan865x`, `lan966x`, `sparx5`, `vcap`, and `fdma`, making this file the aggregation point for the Microchip Ethernet driver family.

## Control Flow And Integration

Kconfig control is declarative. When `NET_VENDOR_MICROCHIP=y`, the enclosed symbols become visible and can be selected as built-in or modules when their dependencies are satisfied. The chosen symbols feed the local Makefile through `CONFIG_*` variables and decide which objects and subdirectories are compiled.

## State And Persistence

Selections persist in the kernel `.config`. No runtime state is created here, but enabling debug `ENC28J60_WRITEVERIFY` changes compiled driver behavior and SPI traffic by adding readback checks during buffer writes.

## Dependencies

The file depends on the kernel Kconfig system and downstream Kconfig files. Driver-specific dependencies include `SPI` for ENC devices, `PCI` for LAN743x, optional PTP clock support, CRC libraries, fixed PHY support, and phylink.

## Risks And Test Signals

The main risk is dependency drift between Kconfig and Makefile objects. `ENCX24J600` builds both `encx24j600.o` and `encx24j600-regmap.o`, so the symbol must cover both. Indentation in the ENCX24J600 block uses spaces rather than tabs in the prompt/help area; Kconfig accepts this, but it is stylistically inconsistent. Test signals are `make olddefconfig`, menu visibility checks, and allmodconfig/build tests for each symbol and sourced subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Makefile

## Purpose

This Makefile maps Microchip Ethernet Kconfig symbols to objects and subdirectories. It is the build-system counterpart to the local Kconfig file.

## Important Build Rules

`obj-$(CONFIG_ENC28J60) += enc28j60.o` builds the ENC28J60 SPI MAC/PHY driver. `obj-$(CONFIG_ENCX24J600) += encx24j600.o encx24j600-regmap.o` builds the main ENCX24J600 SPI driver plus its regmap bus helper. `obj-$(CONFIG_LAN743X) += lan743x.o` defines a composite object whose parts are `lan743x_main.o`, `lan743x_ethtool.o`, and `lan743x_ptp.o`. The remaining `obj-*` lines descend into `lan865x/`, `lan966x/`, `sparx5/`, `vcap/`, and `fdma/` when their symbols are enabled.

## Control Flow And Integration

Kbuild expands `obj-y` into built-in objects and `obj-m` into modules based on the corresponding `CONFIG_*` values. Composite `lan743x-objs` is linked into `lan743x.o` before module or built-in linkage. Subdirectories are delegated to their own Makefiles.

## State And Persistence

There is no runtime state. Build state is generated by Kbuild in object directories. The file persists the one-to-one relationship between symbols and compilation units.

## Dependencies

The file depends on Kbuild conventions and symbol names defined by local or sourced Kconfig files. The ENCX24J600 rule depends on both the main driver and `encx24j600-regmap.c` exporting helper symbols used by the main driver.

## Risks And Test Signals

Risks are limited to stale symbol/object names and missing composite object members. Build tests should cover `CONFIG_ENC28J60=m/y`, `CONFIG_ENCX24J600=m/y`, `CONFIG_LAN743X=m/y`, and subdirectory symbols. `make W=1` is useful for catching missing object references or changed file names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/enc28j60.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/enc28j60.c

## Purpose

`enc28j60.c` is the SPI netdev driver for the Microchip ENC28J60 10 Mbps Ethernet controller, which integrates MAC and PHY with an 8 KiB internal packet buffer. The driver implements SPI register access, FIFO setup, packet TX/RX, threaded interrupt handling, low-power mode, link configuration, multicast/promiscuous filtering, ethtool basics, device-tree matching, and SPI-driver probe/remove.

## Important APIs, Types, And Functions

`struct enc28j60_net` is the private device state. It stores the netdev, SPI device, register-access mutex, pending TX skb, work items (`tx_work`, `setrx_work`, `restart_work`), current register bank, RX FIFO next-packet pointer, debug/stat counters, duplex mode, RX filter mode, message level, and a reusable SPI transfer buffer sized for a full frame.

SPI helpers are layered from low-level operations to semantic register access. `spi_read_op`, `spi_write_op`, `spi_read_buf`, and `spi_write_buf` implement ENC28J60 opcodes. `enc28j60_set_bank` tracks register bank selection. `nolock_*` and `locked_*` helpers provide byte/word reads/writes and bit set/clear operations with explicit mutex discipline. `enc28j60_mem_read` and `enc28j60_packet_write` access internal packet memory.

Hardware setup is handled by `enc28j60_soft_reset`, `enc28j60_hw_init`, `enc28j60_hw_enable`, `enc28j60_hw_disable`, `enc28j60_lowpower`, `nolock_rxfifo_init`, and `nolock_txfifo_init`. PHY access goes through `enc28j60_phy_read`, `enc28j60_phy_write`, and `wait_phy_ready`.

Netdev operations are `enc28j60_net_open`, `enc28j60_net_close`, `enc28j60_send_packet`, `enc28j60_set_multicast_list`, `enc28j60_set_mac_address`, `enc28j60_tx_timeout`, and address validation. Ettool operations cover driver info, message level, and fixed 10baseT half/full link settings.

## Control Flow

Probe allocates an Ethernet netdev, initializes private state and work items, stores SPI driver data, probes the chip through `enc28j60_chipset_init`, assigns a firmware-provided or random MAC address, writes it to hardware, requests a threaded IRQ with `IRQF_ONESHOT`, assigns netdev operations, enters low-power mode, and registers the netdev.

Open validates the MAC address, exits low-power mode, disables and reinitializes hardware, rewrites the current MAC, enables interrupts/RX, checks link state, and starts the TX queue. Close disables interrupts/RX, enters low-power mode, and stops the queue.

TX is deferred. `enc28j60_send_packet` stops the queue, stores the skb in `priv->tx_skb`, schedules `tx_work`, and returns `NETDEV_TX_OK`. `enc28j60_hw_tx` writes a per-packet control byte and frame data to the TX FIFO, optionally verifies writes under `CONFIG_ENC28J60_WRITEVERIFY`, and sets `ECON1_TXRTS`. IRQ handling later observes `EIR_TXIF` or `EIR_TXERIF`, clears or retries based on the transmit status vector, frees the skb in `enc28j60_tx_clear`, and wakes the queue.

RX is handled inside the threaded IRQ. Because the packet interrupt flag is unreliable, `enc28j60_rx_interrupt` reads `EPKTCNT` and processes that many packets. `enc28j60_hw_rx` reads the receive status vector, validates length and `RSV_RXOK`, allocates a new skb, copies the packet from internal memory, sets protocol, updates stats, submits via `netif_rx`, advances `ERXRDPT` with the errata workaround, updates `next_pk_ptr`, and decrements the hardware packet counter.

Interrupt flow disables global interrupts, loops while actionable bits remain, handles DMA/link/TX/TX-error/RX-error/RX cases, then re-enables interrupts. TX timeouts schedule `restart_work`, which closes and reopens the netdev under RTNL if it is still running.

## State And Persistence

Runtime state is held in `struct enc28j60_net`. The driver caches the current register bank to reduce SPI bank selects, the next packet pointer for the circular RX FIFO, current duplex choice, RX filter mode, pending TX skb, and debug counters. Hardware state includes ENC28J60 control registers, MAC/PHY configuration, FIFO pointers, interrupt enable/status bits, PHY LEDs, and low-power state. No nonvolatile writes are performed.

The device is reset and reprogrammed on each open to recover from bad state without rebooting. Low-power mode is used when the interface is closed. The MAC address is stored in netdev state and rewritten when hardware is disabled.

## Dependencies And Integration Points

The driver depends on Linux SPI, netdevice, ethtool, workqueue, threaded IRQ, device property, skbuff, delay, and Ethernet helper APIs. It includes `enc28j60_hw.h` for register and bit definitions. It binds to device tree compatible `microchip,enc28j60` and module alias `spi:enc28j60`.

Integration with the networking stack is a simple single-queue Ethernet netdev. Link settings are fixed to 10 Mbps with autonegotiation disabled from the ethtool view; the driver allows duplex selection only while hardware is disabled and only for 10 Mbps.

## Risks And Edge Cases

SPI access serialization depends on consistently using locked helpers around multi-register sequences. The threaded IRQ can perform potentially heavy packet processing and SPI transactions, which is acceptable for the device class but sensitive to interrupt latency. `poll_ready` is used under the caller's locking assumptions and has a 20 ms timeout; some callers invert success into integer booleans, so regressions around `wait_phy_ready` would be subtle.

RX FIFO pointer handling has errata-specific behavior: `ERXRDPT` must be set to an odd/wrapped address, and `PKTIF` is ignored in favor of `EPKTCNT`. TX late-collision retry is bounded by `MAX_TX_RETRYCOUNT`. Probe requires an IRQ and warns that board setup must use an edge trigger; level-triggered configurations are called out as unsupported. There are no DMA concerns because all data moves through SPI.

## Test Signals

Build with `CONFIG_ENC28J60` as module and built-in, plus `CONFIG_ENC28J60_WRITEVERIFY` for debug coverage. Runtime tests need SPI hardware or an emulator: probe with valid/invalid RevID, open/close/low-power transitions, MAC address changes while down, fixed link settings through ethtool, RX under FIFO wrap and error conditions, TX success and forced late-collision/error paths, TX timeout restart, multicast/all-multicast/promiscuous filter changes, and IRQ behavior with edge-triggered wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/enc28j60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/enc28j60_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/enc28j60_hw.h

## Purpose

`enc28j60_hw.h` is the hardware definition header for the ENC28J60 SPI Ethernet controller. It provides the register encodings, bit definitions, SPI opcodes, packet status helpers, and internal memory layout constants consumed by `enc28j60.c`.

## Important Definitions

The register address encoding combines `ADDR_MASK`, `BANK_MASK`, and `SPRD_MASK`, allowing one constant to identify register address, bank, and MAC/MII dummy-read behavior. It defines all-bank control registers (`EIE`, `EIR`, `ESTAT`, `ECON2`, `ECON1`), banked Ethernet buffer registers, MAC/MII registers, station MAC address registers, built-in self-test registers, and PHY registers.

Bit definitions cover interrupt enable/status bits, status flags, ECON1/ECON2 controls, MACON options, MII command/status bits, RX filter configuration, PHY control/status bits, packet control byte bits, and PHY LED mode. TX and RX status vector helpers (`TSV_GETBIT`, `RSV_GETBIT`) convert packed status bytes/words into named bit checks used by the driver.

SPI operation constants define read/write control register, read/write buffer memory, bit set/clear, and soft reset opcodes. Buffer layout constants split the 8 KiB internal RAM into RX `[0x0000, 0x19ff]` and TX `[0x1a00, 0x1fff]`, with `MAX_FRAMELEN` set to 1518.

## Control Flow And Integration

This header has no executable control flow. Its constants directly drive SPI command generation, bank selection, hardware initialization, RX/TX FIFO pointer programming, interrupt processing, link/duplex configuration, and status-vector decoding in `enc28j60.c`.

## State And Persistence

No state is stored here. The constants describe hardware state that persists in ENC28J60 registers and internal SRAM while the chip is powered.

## Dependencies

It depends only on C preprocessor inclusion and is guarded by `_ENC28J60_HW_H`. Its consumers are expected to include Linux types elsewhere if needed; this file itself is pure macro definitions.

## Risks And Test Signals

Incorrect register constants can break all SPI access because bank and dummy-read behavior are encoded in the same value. Buffer boundary constants are central to FIFO wrap behavior and must match errata assumptions. Test signals include successful register reads across all banks, correct MAC address programming byte order, RX FIFO wrap tests, TX/RX status vector decoding, and builds with warning checks to catch stale or unused definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/enc28j60_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600-regmap.c

## Purpose

`encx24j600-regmap.c` provides regmap bus glue for Microchip ENCX24J600-family SPI Ethernet devices. It translates Linux regmap reads/writes/update-bits calls into the device's banked SFR commands, unbanked commands, single-byte SPI commands, and indirect PHY MII accesses. The main ENCX24J600 driver uses this helper to interact with registers through standard regmap APIs.

## Important APIs, Types, And Functions

The public exported functions are `regmap_encx24j600_spi_write`, `regmap_encx24j600_spi_read`, and `devm_regmap_init_encx24j600`. They operate on `struct encx24j600_context`, defined in `encx24j600_hw.h`, which supplies the SPI device, current bank cache, mutex, and output regmap pointers.

Bank and command helpers are `encx24j600_switch_bank` and `encx24j600_cmdn`. SFR access is implemented by `regmap_encx24j600_sfr_read`, `regmap_encx24j600_sfr_update`, `regmap_encx24j600_sfr_write`, `regmap_encx24j600_sfr_set_bits`, `regmap_encx24j600_sfr_clr_bits`, and `regmap_encx24j600_reg_update_bits`. The generic regmap bus callbacks are `regmap_encx24j600_write` and `regmap_encx24j600_read`.

Register policy callbacks are `encx24j600_regmap_readable`, `encx24j600_regmap_writeable`, `encx24j600_regmap_volatile`, and `encx24j600_regmap_precious`. PHY regmap access is provided by `regmap_encx24j600_phy_reg_read`, `regmap_encx24j600_phy_reg_write`, and PHY readable/writeable/volatile callbacks.

Two regmap configs are created: `regcfg` for main 8-bit-address/16-bit-value device registers with little-endian values and maple cache, and `phycfg` for indirect PHY registers. `regmap_encx24j600` and `phymap_encx24j600` provide the bus operations.

## Control Flow

`devm_regmap_init_encx24j600` initializes the context mutex, sets the regmap lock argument, creates the main regmap with custom read/write/update callbacks, then creates a second regmap for PHY accesses. Reads and writes route by register number: values above the SFR range can be direct SPI commands; banked SFRs use the cached bank and switch if needed; selected pointer registers are translated into shorter 3-byte commands; raw data registers such as `EGPDATA`, `ERXDATA`, and `EUDADATA` are rejected through the SFR regmap path.

`regmap_encx24j600_reg_update_bits` optimizes update-bits for supported low SFR ranges by issuing bit-field set and clear commands per low/high byte instead of generic read-modify-write. It rejects MAC/MII-style ranges where bit-field commands are invalid.

PHY reads write `MIREGADR`, start `MICMD.MIIRD`, sleep briefly, poll `MISTAT.BUSY`, clear `MICMD`, and read `MIRD`. PHY writes write `MIREGADR`, then `MIWR`, then poll `MISTAT.BUSY`.

## State And Persistence

The helper stores only synchronization and cached access state in `struct encx24j600_context`, especially `ctx->bank`, `ctx->mutex`, `ctx->regmap`, and `ctx->phymap`. Device register values persist in hardware and are cached by regmap except for registers marked volatile or precious. Single-byte commands are marked precious to prevent regmap from treating them as ordinary cacheable registers.

## Dependencies And Integration Points

This file depends on Linux SPI, regmap, mutex, delay, module, netdevice includes, and `encx24j600_hw.h` for opcodes, register addresses, bit definitions, masks, and context structure. Its exported symbols are GPL-only and must be linked with the ENCX24J600 main driver, as reflected by the local Makefile.

## Risks And Edge Cases

Register classification is critical. If a register is incorrectly marked readable, writeable, volatile, or precious, regmap caching or access validation can cause stale reads, invalid SPI commands, or lost side effects. The bank cache must remain synchronized with hardware; all regmap accesses use the context mutex, but direct exported SPI read/write callers must also respect expected ordering. PHY polling uses `cpu_relax` without an explicit timeout, so a stuck `MISTAT.BUSY` bit could spin indefinitely after the initial sleep. SFR read/write intentionally rejects data stream registers, so packet-buffer access must use the exported SPI helpers or main driver paths rather than generic regmap SFR access.

## Test Signals

Build tests should cover `CONFIG_ENCX24J600=m/y` and symbol linkage between `encx24j600.o` and `encx24j600-regmap.o`. Hardware tests should exercise banked register reads/writes, unbanked direct commands, update-bits on both low and high bytes, rejected invalid registers, volatile register freshness, regcache behavior across reset/suspend if applicable, and PHY register read/write completion. Fault-injection around SPI transfer errors and busy PHY polling would provide useful risk coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600-regmap.c -->
