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
