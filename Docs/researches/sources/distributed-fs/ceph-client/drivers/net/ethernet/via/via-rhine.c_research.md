# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-rhine.c

## Purpose
This is the Linux Ethernet driver for VIA Rhine Fast Ethernet controllers, including VT86C100A/Rhine-I, Rhine-II, Rhine-III, integrated southbridge variants, a management adapter path, and a platform/OF VT8500-compatible path. It implements PCI/platform probe, MII link management, DMA descriptor rings, NAPI interrupt handling, VLAN/multicast filtering, Wake-on-LAN, suspend/resume, and legacy hardware workarounds.

## Important APIs, types, and functions
`struct rhine_private` is the core state object. It stores active VLANs, coherent RX/TX descriptor rings, skb arrays and DMA addresses, Rhine-I TX bounce buffers, IRQ and MMIO/PIO addresses, NAPI, locks, work items, quirk flags, ring indexes, RX/TX u64 stats, WOL options, thresholds, MII state, and register base.

Important entry points are `rhine_init`/`rhine_cleanup`, `rhine_init_one_pci`, `rhine_init_one_platform`, `rhine_init_one_common`, `rhine_open`, `rhine_close`, `rhine_start_tx`, `rhine_interrupt`, `rhine_napipoll`, `rhine_rx`, `rhine_tx`, `rhine_tx_timeout`, `rhine_reset_task`, `rhine_slow_event_task`, `rhine_suspend`, `rhine_resume`, and `rhine_shutdown_pci`. Netdev ops include open/stop/start_xmit/stats/set_rx_mode/MII ioctl/VLAN add-kill/tx_timeout. Ettool ops expose driver info, MII link settings, link state, message level, and WOL.

The hardware model is described by register offset enums, interrupt bit enums, descriptor structures, and quirk bits such as `rqWOL`, `rqForceReset`, `rqStatusWBRace`, `rqRhineI`, `rqIntPHY`, `rqMgmt`, and `rqNeedEnMMIO`.

## Control flow
Module init checks a DMI table for BIOSes that need `avoid_D3`, then registers both PCI and platform drivers. PCI probe enables the device, derives quirks from revision, requests regions, maps PIO or MMIO depending on `CONFIG_VIA_RHINE_MMIO`, enables/verifies MMIO when needed, then calls common initialization. Platform probe maps the memory resource, parses IRQ, reads OF match quirks, and enters the same common path.

Common initialization sets a 32-bit DMA mask, allocates netdev state, initializes locks/work/NAPI/MII callbacks, resets and powers the chip, reads or randomizes the MAC, registers the netdev, discovers the PHY, and seeds carrier state. Open requests the shared IRQ, allocates coherent descriptor rings and buffers, re-enables MMIO/power, resets the chip, enables work tasks, initializes registers under netdev lock, then starts the queue. Register initialization writes station address, FIFO thresholds, ring base addresses, RX mode, optional CAM filters, enables NAPI, unmasks interrupts, starts TX/RX, and checks media.

Interrupt handling reads combined status including `IntrStatus2` for writeback-race chips. Fast RX/TX/stat work is moved into NAPI after masking interrupts. NAPI acknowledges non-slow events, calls `rhine_rx` up to budget, reaps TX completions with `rhine_tx`, handles TX errors via threshold bumps and `rhine_restart_tx`, updates hardware error counters, schedules slow work for link/PCI events, and re-enables interrupts when complete. Slow work acknowledges link/PCI events and updates media.

TX maps or bounce-copies the skb, writes descriptor address and length, handles hardware VLAN tagging for management adapters, uses memory barriers before setting `DescOwn`, advances `cur_tx`, wakes the TX engine, and applies queue stop/wake backpressure. TX completion scans from `dirty_tx` to `cur_tx`, handles error bits, unmaps DMA, consumes skbs, updates u64 stats and BQL, and wakes the queue when space returns. RX scans descriptors until owned by hardware or budget is reached, copies small packets when `rx_copybreak` applies, otherwise swaps in a newly allocated DMA buffer, extracts VLAN tags, submits skbs with `netif_receive_skb`, updates u64 stats, and returns descriptors to hardware.

Close disables tasks, NAPI, queue, interrupts, and the chip, then frees IRQ, RX/TX buffers, and coherent rings. Suspend disables tasks/interrupts/NAPI and may program WOL through the PCI shutdown path. Resume restores MMIO/power, resets rings, re-enables tasks, and reinitializes registers.

## State and persistence behavior
Most state is per-netdev and recreated on open. Descriptor rings and RX/TX buffers are allocated when the interface opens and freed on close. MAC address is read from hardware/EEPROM at probe and can be changed through `eth_mac_addr`. WOL options persist in `rp->wolopts` for the device lifetime and are programmed during shutdown/suspend. Hardware MIB-style CRC/missed counters are read and cleared into software stats. D3 avoidance can persist as a module parameter or DMI-derived runtime setting.

## Dependencies and integration points
The driver integrates with PCI, platform/OF, DMA mapping, netdev/NAPI/BQL, MII helpers, ethtool, VLAN acceleration, CRC32 multicast hashing, DMI, PM sleep, and optional netpoll. It relies on Kconfig-selected `MII`, `CRC32`, `HAS_DMA`, `HAS_IOPORT`, and optional MMIO behavior. Hardware integration includes EEPROM reload, PHY MDIO, CAM/VCAM filters, WOL registers, and chip-specific reset paths.

## Risks and edge cases
The driver carries many revision-specific workarounds: Rhine-I alignment/bounce buffers, MMIO enable differences, Tx status writeback race, forced reset, integrated PHY handling, and management adapter VLAN CAM behavior. Correct memory ordering around descriptor ownership and `cur_tx`/`dirty_tx` is critical. RX error counter clearing uses both write and read because chips differ. `rhine_disable_linkmon` can delay in contexts near interrupt handling. Platform remove manually `iounmap`s a devm-mapped resource, which is a point to inspect if ownership changes. WOL and D3 behavior is BIOS-sensitive.

## Test signals
Build with PCI, platform, and `VIA_RHINE_MMIO` variants. Runtime testing should cover open/close, sustained RX/TX, small packet copy path, VLAN filter add/remove on management adapters, multicast/promiscuous/allmulti changes, MII ethtool speed/duplex changes, TX timeout reset recovery, NAPI budget behavior, WOL shutdown/suspend, DMI `avoid_D3`, and netpoll when configured. Counters to watch include tx/rx packets and bytes, CRC/missed errors, TX FIFO/collision errors, and carrier transitions.
