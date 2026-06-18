# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_main.c

## Purpose

`r8169_main.c` is the main Linux PCI Ethernet driver for Realtek RTL8169/8168/8101-family and newer RTL8125/8126/8127 controllers. It owns PCI probing, chip revision identification, MMIO register access, descriptor-ring setup, TX/RX datapath, interrupt/NAPI service, ethtool operations, wake-on-LAN, runtime/system power management, DASH/OOB coordination, firmware dispatch, and integration with the Realtek PHY helper code in `r8169_phy_config.c`.

The file is strongly hardware-version driven. `rtl_chip_infos[]` and `rtl_chip_infos_extended[]` map PCI revision/XID fields to `enum mac_version`, user-facing chip names, and firmware filenames. Most later behavior switches on `tp->mac_version`, allowing one driver to cover legacy PCI RTL8169 variants, PCIe RTL8168/810x variants, 2.5G RTL8125 variants, RTL8126, and 10G/SFP-capable RTL8127 paths.

## Important APIs, Types, And Data

Core state lives in `struct rtl8169_private`, which binds the PCI device, `net_device`, PHY, NAPI instance, MMIO base, MAC version, DASH state, descriptor rings, DMA addresses, RX page array, TX SKB metadata, interrupt mask, optional clock, workqueue flags, OCP and LED locks, firmware handle, hardware counters, WOL options, and OCP base page. `struct TxDesc` and `struct RxDesc` model the hardware descriptors, while `struct ring_info` tracks TX SKBs and DMA lengths. `struct rtl8169_counters` mirrors the hardware tally block used by ethtool and `ndo_get_stats64`.

The exported or cross-file symbols are `rtl8168_led_mod_ctrl()`, `rtl8168_get_led_mode()`, `rtl8125_set_led_mode()`, `rtl8125_get_led_mode()`, `r8169_get_led_name()`, `rtl8168d_efuse_read()`, `r8169_apply_firmware()`, and `rtl8168h_2_get_adc_bias_ioffset()`. PHY setup calls into `r8169_hw_phy_config()` from `r8169_phy_config.c`. Firmware support is delegated to `r8169_firmware.h` helpers through a `struct rtl_fw` populated with PHY and MAC-MCU access callbacks.

The main driver API surfaces are `rtl_netdev_ops`, `rtl8169_ethtool_ops`, `rtl8169_pm_ops`, and `rtl8169_pci_driver`. They connect the driver to netdev open/stop/xmit/statistics/MTU/filtering/feature callbacks, ethtool statistics/coalescing/WOL/EEE/ring/pause/link settings, suspend/resume/runtime-PM callbacks, and PCI probe/remove/shutdown.

## Control Flow

Probe starts at `rtl_init_one()`. It allocates a managed Ethernet device, enables the PCI function, maps MMIO, reads `TxConfig` to derive the chip XID, handles extended chip version lookup when needed, decides ASPM manageability, detects SFP and DASH modes, initializes receive configuration, masks/acks interrupts, runs hardware pre-initialization, resets the MAC, allocates one interrupt vector, initializes work and NAPI, discovers or assigns the MAC address, sets feature flags, configures WOL/power-down policy, allocates DMA coherent tally counters, registers an MDIO bus, registers the netdev, optionally registers LED class devices, and logs chip identity.

`rtl_open()` is the runtime bring-up path. It resumes the PCI device, allocates coherent TX/RX descriptor rings, fills all RX descriptors with DMA-mapped pages, requests firmware if configured for the chip, requests IRQ, connects the PHY, calls `rtl8169_up()`, initializes counter offsets, and starts the netdev queue. `rtl8169_up()` starts DASH ownership if present, enables bus mastering, initializes and resumes the PHY, applies PHY configuration and firmware via `rtl8169_init_phy()`, enables NAPI/work, performs a reset/start sequence through `rtl_reset_work()`, and starts the PHY state machine.

Hardware start is layered. `rtl_hw_start()` disables ASPM/CLKREQ while programming hardware, updates the EEE TX idle timer, dispatches to legacy `rtl_hw_start_8169()`, RTL8125+ `rtl_hw_start_8125()`, or RTL8168-style `rtl_hw_start_8168()`, re-enables L1 exit and ASPM/CLKREQ when allowed, programs descriptor base addresses, applies jumbo and receive filters, enables TX/RX, initializes RX/TX configuration, applies feature bits, sets multicast/promiscuous mode, and finally enables interrupts. Hardware-family callbacks such as `rtl_hw_start_8168g_1()`, `rtl_hw_start_8125_common()`, and `rtl_hw_start_8127a()` program chip-specific EPHY, ERI, OCP, FIFO, LTR, ASPM, and errata registers.

TX starts at `rtl8169_start_xmit()`. It verifies ring space, derives VLAN/checksum/TSO descriptor options using either legacy v1 or newer v2 checksum formats, applies packet padding quirks for selected chip versions, DMA maps the linear data and fragments, marks the last and first descriptors with memory barriers, updates `cur_tx`, conditionally stops the queue using netdev queue helpers, and rings the TX doorbell. Completion is handled in `rtl_tx()` from NAPI, which walks descriptors from `dirty_tx`, unmaps DMA, consumes SKBs, updates software stats, wakes the queue, and may ring an extra doorbell for a known 8168 TX poll race.

RX is handled in `rtl_rx()`. It scans descriptors until ownership returns to the NIC or budget is exhausted, uses a DMA read barrier after seeing CPU ownership, validates error bits, rejects unsupported fragmented frames, allocates an SKB, copies from the page-backed RX buffer, syncs DMA ownership back to device, applies checksum and VLAN metadata, submits to GRO, updates stats, and returns the descriptor to the ASIC. RX buffers are preallocated in `rtl8169_rx_fill()` and fully released by `rtl8169_rx_clear()`.

Interrupt handling is minimal by design. `rtl8169_interrupt()` reads family-specific interrupt status, rejects spurious events, handles legacy PCI system errors, forwards link-change interrupts to phylib, disables interrupts, schedules NAPI, acks events, and returns. `rtl8169_poll()` performs TX completion and RX polling, then re-enables interrupts on NAPI completion.

Reset and failure recovery run through `rtl_task()`, `rtl_schedule_task()`, `rtl8169_tx_timeout()`, and `rtl_reset_work()`. TX timeout may reset the secondary PCI bus if MMIO reads fail and disables problematic ASPM states before resetting the MAC and restarting rings.

Shutdown paths are symmetrical. `rtl8169_down()` disables work, stops the PHY, resets SFP when needed, updates counters, clears PCI bus mastering, cleans up hardware/rings, disables L1 exit, prepares power-down/WOL, and stops DASH ownership when appropriate. `rtl8169_close()` stops the queue, calls `rtl8169_down()`, frees RX buffers, IRQ, PHY connection, and coherent rings. Remove unregisters the netdev, removes LEDs, stops DASH, releases firmware, and restores the permanent MAC.

## State And Persistence

Persistent driver state is in `rtl8169_private`: descriptor indices (`cur_tx`, `dirty_tx`, `cur_rx`), RX page ownership, TX SKB mappings, feature bits in `cp_cmd`, coalescing scale state, IRQ mask, saved WOL options, counter offsets, firmware pointer, and detected hardware capabilities. Hardware-visible state persists in MMIO registers, OCP/ERI/EPHY/CSI register spaces, PHY pages/MMDs, descriptor DMA memory, and firmware-programmed PHY/MAC microcode.

`saved_wolopts` survives while the device object is alive and is reapplied by runtime resume. `tc_offset` normalizes legacy tally counters that reset only on power cycle, so software statistics after driver reload/open remain coherent. Runtime PM keeps the device wake-capable with `WAKE_PHY` during idle suspend unless DASH is enabled, and system suspend preserves or disables the external clock depending on wake policy.

Concurrency state is protected by the netdev stack, NAPI serialization, `raw_spinlock_t mac_ocp_lock` for MAC OCP access, `led_lock` for LED register read-modify-write, workqueue flags for reset reasons, and memory barriers around descriptor ownership handoff. Descriptor fields and indices use `READ_ONCE()`, `WRITE_ONCE()`, `dma_wmb()`, `dma_rmb()`, and `smp_wmb()` where hardware/CPU ordering matters.

## Dependencies And Integration Points

The file depends on Linux PCI, netdevice, phylib, ethtool, NAPI, DMA mapping, runtime PM, firmware loading, page allocation, GRO, VLAN acceleration, checksum/GSO helpers, and Realtek PHY support headers. It integrates with `r8169.h` for shared declarations and `mac_version` identifiers, `r8169_firmware.h` for firmware loading/writing, the Realtek PHY driver module through the MDIO bus and `realtek_phy.h`, optional LED support through `CONFIG_R8169_LEDS`, and platform firmware/DT/ACPI for an optional `ether_clk` and MAC address.

The MDIO registration deliberately exposes only PHY address 0 and optionally Clause 45 vendor MMD access for newer chips. The code fails probe when no dedicated PHY driver has bound, warning that `realtek.ko` may be missing from initramfs. PCI integration includes managed MMIO mapping, IRQ vector allocation, wake/run-time PM behavior, ASPM tuning, and fallback CSI access for extended PCI config writes on systems without native access.

## Risks And Edge Cases

The main risks are hardware-regression risks from large switch tables of undocumented register programming. Many values are Realtek-provided "magic" sequences, so incorrect chip-version mapping can break link, power, FIFO, or DMA behavior. ASPM handling is explicitly cautious because the driver documents random stops and full-system hangs on some PCIe systems; runtime paths also disable ASPM after TX timeout.

DMA descriptor ownership is high risk: missing barriers or incorrect `cur_tx`/`dirty_tx` updates can cause data corruption, stalls, or use-after-free. TX error unwinding must unmap only descriptors already mapped. RX currently copies from page buffers into SKBs instead of page recycling into SKBs; the simplicity avoids ownership complexity but still depends on correct DMA sync ranges.

Feature interactions are restricted for known hardware limits: jumbo frames disable pause advertising on affected paths, checksum/TSO are disabled for large MTUs on newer than RTL8169, v2 checksum/TSO has header-offset limits, RTL8168evl has TSO quirks around TCP/IP options and short trailing fragments, and selected RTL8125 revisions require UDP/PTP padding. Coalescing is not exposed for RTL8125+. SFP mode only accepts forced settings and directly mutates the PHY device fields under its lock.

Power and WOL are also sensitive. DASH ownership changes use OOB/CMAC handshakes with polling; failures could leave the management engine or driver with stale ownership assumptions. Runtime suspend applies `WAKE_PHY`, detaches netdev, and tears down hardware if rings exist; resume must restore MAC address and WOL before restarting.

## Test Signals

Useful validation signals include successful `modprobe r8169` and probe logging for all target chip families, netdev registration, valid MAC selection, PHY driver binding, link up/down transitions, DHCP/iperf TX/RX traffic, NAPI interrupt moderation under load, TX timeout absence, `ethtool -S`, `ethtool -k/-K`, `ethtool -c/-C` on non-RTL8125, `ethtool --show-eee/--set-eee`, WOL suspend/resume with magic packet and link wake, runtime PM idle/resume, jumbo MTU traffic per chip limit, VLAN TX/RX acceleration, multicast/promiscuous filtering, and error injection for DMA mapping or IRQ request failures. Kernel test coverage should focus on static analysis, sparse/endian checks, lockdep for MDIO/OCP/LED paths, and hardware-in-loop regression across representative MAC versions because most behavior is hardware dependent.
